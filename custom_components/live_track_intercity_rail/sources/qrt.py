"""Queensland Rail Travel (Australia) -> one Snapshot, every train FROM ITS TIMES. No Home Assistant imports.

DECIDED 2026-11-14 (Lee; Intercity SSOT 8.14): the source is QRT's Service Updates page's own JSON, read by each install
for its own user, under 10_SEED/05_SHARED_LESSONS_DATA.md B18 (the website-API exception); 2026-11-14 20:44 CST "Times
only": the train is placed by its calls' times alone, TrainPosition is not used. Measured:
`20_Research/queensland_rail_travel/QRT_RECORDING_ANALYSIS_20261114.md`.

THE ENDPOINTS (what queenslandrailtravel.com.au/serviceupdates calls): `AllServices` (today's services by line and
direction, a train still running from yesterday included) and `GetService?serviceId=<id>&serivceDate=<date>` (their
spelling): each call's PlaceCode, PlannedArrival/Departure and ActualArrival/Departure, `0001-01-01T00:00:00` when empty.
Times are Brisbane wall clock (no daylight saving), with no zone.

TIMES (MEASURED, the note 2.3-2.4): `Planned*` is the running estimate while a call is on time and is rewritten live;
`Actual*` is the actual time for calls behind and a live FORECAST for calls ahead, filled only on calls not on time. So
each call's aimed time is Planned and its word is Actual (saw_livetrack.timetable.call_times: actual, else expected,
else aimed plus the delay last known before it), re-read every poll.

B18, AS BUILT. (6) Polite: the requests the page makes, an honest User-Agent naming the integration (const.USER_AGENT);
`AllServices` at most every ALL_TTL_S, a service's `GetService` at most every SVC_TTL_S and only for a train out or
leaving within LEAD_S, and none for a train past its last call; ADDED_GAP_S between requests; after a failure, backoff
doubling from BACKOFF_S to BACKOFF_MAX_S. (7) Fails closed: the last good answers are kept STALE_S; past that `read`
raises QrtUnavailable, the coordinator holds the last snapshot SOURCE_GAP_S (const, 600 s) more, then the markers go,
with one warning in the log. (5) Nothing of QRT's ships: the shipped data (data/qrt_lines.json.gz, tools/qrt_lines.py)
is SAW's own pairing and stop patterns and OpenStreetMap's track.

WHERE A TRAIN IS (saw_livetrack.timetable.place): at its origin from 5 minutes before it leaves, standing at a call
between its arrival and departure, running between calls along its line, kept at its last call 5 minutes after
arriving. Its line is its pattern's, in the direction it runs ("<pattern>_out#<n>" / "_back#<n>"), the section it is
on where the train reverses (the Spirit of the Outback at Rockhampton, the Westlander at Toowoomba).

IDENTITY "<train number>-<day of the service date>" (`V980-15`). The train number (decision 5) is the ServiceId without
its trailing T after the line's first character (`980T` -> V980, `W57T` -> PW57; MEASURED from the disruption titles,
the note 2.8). HOVER "Spirit of Queensland V980 · Cairns–Brisbane - Roma Street".
"""

from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import os
import time as _time
import urllib.parse
import urllib.request
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo

from saw_livetrack.gtfs.realtime import Obs
from saw_livetrack.timetable import call_times, place

from .base import AIM_ETA_KEY, HELD_SPEED_KEY, NO_FIX_KEY, TIMED_AFTER_KEY, Snapshot
from .entur import HOLD

BASE = "https://www.queenslandrailtravel.com.au/SPWebApp/api/ServiceUpdates"
PAGE = "https://www.queenslandrailtravel.com.au/serviceupdates"
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "qrt_lines.json.gz")
DATA_VERSION = 1
GEO_V = 1
TZ = ZoneInfo("Australia/Brisbane")
SENTINEL = "0001-01-01T00:00:00"
ALL_TTL_S = 300.0        # the list, at most every 5 minutes (B18 6: "every few minutes")
SVC_TTL_S = 300.0        # a running train's times, at most every 5 minutes
LEAD_S = 1800.0          # a train's times are first read 30 minutes before it leaves
DONE_S = 900.0           # and not read again from 15 minutes after its last arrival
ADDED_GAP_S = 1.0        # between two requests in one poll
BACKOFF_S = 60.0
BACKOFF_MAX_S = 900.0
STALE_S = 900.0          # the last good list is drawn from for 15 minutes, then the source is down
TIMEOUT_S = 20.0
MAX_BYTES = 1024 * 1024


class QrtUnavailable(Exception):
    """No good answer within STALE_S."""


def t_epoch(s: str | None) -> float | None:
    """A QRT time (Brisbane wall clock, no zone) -> epoch seconds; None for the sentinel or nothing."""
    if not s or s.startswith("0001"):
        return None
    try:
        return dt.datetime.fromisoformat(s[:19]).replace(tzinfo=TZ).timestamp()
    except ValueError:
        return None


def train_number(service_id: str, prefix: str) -> str:
    """`980T` with the Spirit of Queensland's "V" -> "V980"; an id not ending in T is kept, prefixed."""
    core = service_id[:-1] if service_id.endswith("T") else service_id
    return f"{prefix}{core}"


class QrtClient:
    """The two endpoints, cached and paced (B18 6, 7). Synchronous: run in the executor. One per config entry."""

    def __init__(self, user_agent: str, opener=None, clock=_time.time, sleep=_time.sleep) -> None:
        self._ua = user_agent
        self._open = opener or self._urlopen
        self._clock, self._sleep = clock, sleep
        self._all: dict[str, Any] | None = None
        self._all_t: float | None = None
        self._svc: dict[tuple[str, str], tuple[float, dict[str, Any]]] = {}
        self._next_try = 0.0
        self._fail_n = 0
        self.last_error: str | None = None
        self.requests = 0

    def _urlopen(self, url: str) -> bytes:
        req = urllib.request.Request(url, headers={"User-Agent": self._ua, "Accept": "application/json",
                                                   "Referer": PAGE})
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            if resp.status != 200:
                raise OSError(f"HTTP {resp.status}")
            raw = resp.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise OSError("answer too large")
        return raw

    def _get(self, url: str) -> dict[str, Any]:
        if self.requests:
            self._sleep(ADDED_GAP_S)
        self.requests += 1
        body = json.loads(self._open(url))
        if not isinstance(body, dict) or body.get("Success") is False:
            raise ValueError(f"not a good answer: {str(body)[:80]}")
        return body

    def _failed(self, err: Exception) -> None:
        self._fail_n += 1
        self.last_error = f"{type(err).__name__}: {err}"[:200]
        self._next_try = self._clock() + min(BACKOFF_MAX_S, BACKOFF_S * 2 ** (self._fail_n - 1))

    def poll(self) -> list[dict[str, Any]]:
        """[{service, line, direction, body}] for the trains out or near, from the cache where it is fresh enough.
        Raises QrtUnavailable when the last good list is older than STALE_S."""
        now = self._clock()
        self.requests = 0
        if now >= self._next_try and (self._all_t is None or now - self._all_t >= ALL_TTL_S):
            try:
                self._all = self._get(f"{BASE}/AllServices")
                self._all_t = self._clock()
                self._fail_n = 0
            except Exception as err:  # noqa: BLE001 - any failure is a failed read (B18 7)
                self._failed(err)
        if self._all is None or self._all_t is None or now - self._all_t > STALE_S:
            raise QrtUnavailable(self.last_error or "no answer yet")
        out, keep = [], set()
        for line, direction, svc in listed(self._all):
            sid, sdate = svc.get("ServiceId") or "", (svc.get("ServiceDate") or "")[:10]
            if not sid or not sdate:
                continue
            key = (sid, sdate)
            keep.add(key)
            dep = t_epoch(svc.get("DepartureDate"))
            cached = self._svc.get(key)
            done = cached is not None and finished(cached[1], now)
            near = dep is None or dep - now <= LEAD_S
            if near and not done and now >= self._next_try and (cached is None or now - cached[0] >= SVC_TTL_S):
                q = urllib.parse.urlencode({"serviceId": sid, "serivceDate": f"{sdate}T00:00:00.000Z"})
                try:
                    self._svc[key] = cached = (self._clock(), self._get(f"{BASE}/GetService?{q}"))
                except Exception as err:  # noqa: BLE001
                    self._failed(err)
            if cached is not None and now - cached[0] <= STALE_S + SVC_TTL_S:
                out.append({"service": svc, "line": line, "direction": direction, "body": cached[1]})
        for key in [k for k in self._svc if k not in keep]:
            del self._svc[key]       # gone from the list: not drawn, not read
        return out


def listed(all_body: Mapping[str, Any]):
    """(line name, direction name, service) for every service AllServices lists."""
    for ln in all_body.get("ServiceLines") or ():
        for d in ln.get("Directions") or ():
            for s in d.get("Services") or ():
                yield ln.get("ServiceLineName") or "", d.get("DirectionName") or "", s


def finished(body: Mapping[str, Any], now: float) -> bool:
    """Past DONE_S after its last call's arrival, by its own times."""
    mv = body.get("TrainMovements") or []
    if not mv:
        return False
    last = mv[-1]
    t = t_epoch(last.get("ActualArrival")) or t_epoch(last.get("PlannedArrival"))
    return t is not None and now > t + DONE_S


def read(client: QrtClient) -> list[dict[str, Any]]:
    """One paced poll (QrtClient.poll). Blocking: run in the executor."""
    return client.poll()


# ---------- the shipped data ----------

def decode(enc: Sequence[int]) -> list[list[float]]:
    """1e-5 degree deltas (tools/journey_beyond.py encode) -> [[lat, lon], ...]."""
    out, la, lo = [], 0, 0
    for i in range(0, len(enc) - 1, 2):
        la += enc[i]
        lo += enc[i + 1]
        out.append([round(la / 1e5, 5), round(lo / 1e5, 5)])
    return out


def load(path: str = DATA_FILE) -> dict[str, Any]:
    """The shipped lines, checked: {"data", "digest"}. Blocking. Raises ValueError for a file of another version."""
    with open(path, "rb") as fh:
        raw = fh.read()
    data = json.loads(gzip.decompress(raw))
    if data.get("v") != DATA_VERSION:
        raise ValueError(f"QRT lines of version {data.get('v')!r}, not {DATA_VERSION}")
    return {"data": data, "digest": hashlib.sha256(raw).hexdigest()}


def pattern_of(line_key: str) -> str:
    """"tilt_rok_back#0" -> "tilt_rok"."""
    return line_key.split("#")[0].rsplit("_", 1)[0]


def distill(loaded: Mapping[str, Any]) -> dict[str, Any]:
    """The shipped data -> the geometry the route store keeps and the Projector reads: each line section is a "train"
    whose one shape is itself; stops and their names; the patterns as `qrt`."""
    from .. import geometry
    data = loaded["data"]
    shapes = {k: decode(v[1]) for k, v in (data.get("lines") or {}).items()}
    pats = data.get("patterns") or {}
    return {"v": geometry.GEOMETRY_VERSION,
            "stops": {c: [s[1], s[2]] for c, s in (data.get("stations") or {}).items()},
            "stop_names": {c: s[0] for c, s in (data.get("stations") or {}).items()},
            "trains": {k: [k] for k in shapes},
            "train_routes": {k: (pats.get(pattern_of(k)) or {}).get("line", "") for k in shapes},
            "shapes": shapes, "qrt": {"patterns": pats, "stations": data.get("stations") or {}}, "qrt_v": GEO_V}


class StaticView:
    """The shipped lines as the route store's timetable; its version is the file's digest."""

    def __init__(self, loader=load) -> None:
        self._loader = loader
        self._loaded: dict[str, Any] | None = None

    def _get(self) -> dict[str, Any]:
        if self._loaded is None:
            self._loaded = self._loader()
        return self._loaded

    def static_version(self) -> str | None:
        return f"qrt{self._get()['digest'][:12]}|g{GEO_V}"

    def static_path(self) -> str | None:
        return None

    def distill_geometry(self) -> dict[str, Any] | None:
        return distill(self._get())


def version(view: StaticView) -> str | None:
    """The view's version; the first call reads the shipped file. Blocking: run in the executor."""
    return view.static_version()


# ---------- trains ----------

def pattern_for(pats: Mapping[str, Any], line: str) -> tuple[str, Mapping[str, Any]] | None:
    for pid, p in pats.items():
        if p.get("line") == line:
            return pid, p
    return None


def section_of(sections: Sequence[int], i: int) -> int:
    """The section a train at (or just leaving) call i of its direction is on."""
    return max((n for n, s in enumerate(sections or [0]) if s <= i), default=0)


class QrtService:
    """Per config entry: the trains out now, drawn from their times. Holds no state between polls."""

    def parse(self, services: Sequence[Mapping[str, Any]], now: float,
              geometry_: Mapping[str, Any] | None) -> Snapshot:
        snap = Snapshot()
        q = (geometry_ or {}).get("qrt") or {}
        pats, stations = q.get("patterns") or {}, q.get("stations") or {}
        if not pats:
            snap.skipped["no_lines"] = 1
            return snap
        for item in services:
            self._train(snap, item, pats, stations, now)
        return snap

    @staticmethod
    def _count(snap: Snapshot, why: str) -> None:
        snap.skipped[why] = snap.skipped.get(why, 0) + 1

    def _train(self, snap, item, pats, stations, now) -> None:
        svc, body = item["service"], item["body"]
        found = pattern_for(pats, item.get("line") or "")
        if found is None:
            self._count(snap, "unknown_line")
            return
        pid, pat = found
        mv = [m for m in body.get("TrainMovements") or () if m.get("PlaceCode") in stations]
        if len(mv) < 2:
            self._count(snap, "too_few_known_calls")
            return
        order = [c for c, _ in pat["out"]["calls"]]
        try:
            way = "out" if order.index(mv[0]["PlaceCode"]) < order.index(mv[-1]["PlaceCode"]) else "back"
        except ValueError:
            way = "out"
        index = {c: i for i, (c, _) in enumerate(pat[way]["calls"])}
        calls = [{"stop": m["PlaceCode"],
                  "aimed_arrival": t_epoch(m.get("PlannedArrival")),
                  "aimed_departure": t_epoch(m.get("PlannedDeparture")),
                  "expected_arrival": t_epoch(m.get("ActualArrival")),
                  "expected_departure": t_epoch(m.get("ActualDeparture"))} for m in mv]
        times = call_times(calls)
        where = place(times, now)
        if where is None:
            return
        state, i = where
        call, arr_i, dep_i, _ = times[i]
        st = stations[call["stop"]]
        number = train_number(svc.get("ServiceId") or "", pat.get("prefix") or "")
        key = f"{number}-{int((svc.get('ServiceDate') or '0000-00-00')[8:10])}"
        when = arr_i if state == "standing" and now >= arr_i else (dep_i if state == "running" else now)
        snap.observations.append(Obs(
            vehicle_id=key, lat=float(st[1]), lon=float(st[2]),
            observed_at=dt.datetime.fromtimestamp(min(when, now), dt.timezone.utc), in_service=True,
            train=number, line=None, reported_course=None, trip_id=key))
        first, last = stations[mv[0]["PlaceCode"]][0], stations[mv[-1]["PlaceCode"]][0]
        snap.extras[key] = extra = {
            "line_name": f"{pat.get('line')} {number} · {first}–{last}", NO_FIX_KEY: True,
            "route_code": pid, "service_family": pat.get("picture"), "service_direction": way,
            "destination": mv[-1]["PlaceCode"]}
        snap.route_keys[key] = f"{pid}_{way}#{section_of(pat[way]['sections'], index.get(call['stop'], 0))}"
        nxt = times[i + 1] if i + 1 < len(times) else None
        if state == "standing" or nxt is None:
            extra.update(HOLD)
        else:
            extra[HELD_SPEED_KEY] = None
            extra[TIMED_AFTER_KEY] = 0.0
            extra[AIM_ETA_KEY] = nxt[1]
        if nxt is None:
            return
        snap.stop_codes[key] = nxt[0]["stop"]
        snap.next_stops[key] = (stations[nxt[0]["stop"]][0], nxt[1])


__all__ = ["DATA_VERSION", "QrtClient", "QrtService", "QrtUnavailable", "StaticView", "decode", "distill", "finished",
           "listed", "load", "read", "section_of", "t_epoch", "train_number", "version"]
