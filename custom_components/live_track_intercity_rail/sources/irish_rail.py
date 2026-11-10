"""Irish Rail's mainline trains (Ireland) -> one Snapshot, every train FROM ITS TIMETABLE, Irish Rail's positions as
updates. No Home Assistant imports.

Lee 2026-11-09 02:00 CST (Intercity SSOT 8.10, decisions 3-8): "Draw them from the timetable with their last known
delay, marked as estimated. Push them along the track and use positions as updates." The API's positions are SIGNALLING
points, a new one every ~3.5 min (InterCity p90 16 min), and the branch lines and the Enterprise past Dundalk are never
tracked at all (probe note 3), so the TIMETABLE carries every train and the API corrects it.

WHAT RUNS. Every A or B coded trip of the NTA's timetable whose calendar runs it today or yesterday (a run passes
midnight: times to 25:47 measured), from PRE_DEPARTURE_S before its first departure to FINISHED_S after its last arrival
plus its delay. A trip serving Belfast is the Enterprise (A100-A131, A141-A166 and B182 in the 2026-11-08 timetable).

ITS TIMES. Each call's aimed time from the timetable; its expected time aimed + the run's delay: the API's `Difference`
for this run when it lists it running, else the last one it gave (kept in memory), else none (a run never seen is drawn
on its timetable and publishes no delay: D0, only the railroad's word is a delay). Where it is, by those times, is
sources/entur_et.place (SJ Nord's rule): standing at a call between its arrival and departure, else timed from the call it
left to the next one's arrival, along its trip's own shape.

A REPORT IS AN UPDATE ONLY WHEN IT IS THIS RUN: status R, the same code, its origin time the trip's first departure
(within MATCH_S), and not a ghost (now within the run's scheduled span plus its delay plus GHOST_S). MEASURED 2026-11-10
04:3x Irish time: all 13 trains the API listed were the previous evening's, still "running" at Clondalkin and
Hazelhatch. A report of the documented call (no origin time) matches by date and is still bound by the span. Status T
(terminated) ends the run. A report's LAST LOCATION, joined to the trip's stops, is a FLOOR: the train is drawn at that
call or past it, never before it.

IDENTITY "<code>-<day of the service date>" (A700-9): the letter keeps A700 and B700 apart. LABEL the number without its
letter (Lee: "Label 700"). LOOK, LATE: operators/irish_rail.py.
"""

from __future__ import annotations

import csv
import datetime as dt
import io
import re
import zipfile
from typing import Any, Mapping

from saw_livetrack.gtfs.realtime import Obs
from saw_livetrack.irish_rail import INTERCITY, consumer_of, number_of

from .. import geometry
from .base import AIM_ETA_KEY, HELD_SPEED_KEY, NO_FIX_KEY, TIMED_AFTER_KEY, Snapshot
from .entur import HOLD
from .entur_et import call_times, place

TIME_ZONE = "Europe/Dublin"
PRE_DEPARTURE_S = 300.0
FINISHED_S = 300.0
# A report's origin time and the trip's first departure agree to this (both are the timetable's minute).
MATCH_S = 120.0
# A run listed after its scheduled end plus its delay plus this is a ghost.
GHOST_S = 1800.0
# A report more than this EARLY is not an update (no delay, no floor). MEASURED on the capture (bin\ie_b_early.txt):
# before a train leaves its origin Hacon may list it running at a station on its route with the stock's own position
# and a Difference of about minus an hour (A104 at Rush and Lusk -3,258 s, A713 at Oranmore -3,708 s); believed, the
# whole run was drawn an hour ahead, up to 60 km from the next fix.
EARLY_S = 600.0
# The longest delay a run is looked for under (A222 stood 205 min late on 2026-11-09).
MAX_LATE_S = 4 * 3600.0
FORGET_S = 36 * 3600.0
DUBLIN = ("Connolly", "Dublin Heuston", "Dublin Connolly", "Heuston")
BELFAST = "Belfast"
# CSO Census 2022 F1015, Built Up Areas (probe note 8; bin\ie_b_cso.txt for Nenagh, Thurles, Tullamore, Gorey, Wexford):
# the end towns of the trips that do not touch Dublin. A junction is not a town (0). Keyed by the timetable's stop name
# up to its first space or bracket, lower case.
TOWNS = {"athenry": 4603, "athlone": 22869, "ballina": 10556, "ballybrophy": 0, "carlow": 27351, "cork": 222526,
         "ennis": 27923, "galway": 85910, "gorey": 11517, "limerick": 102287, "limerick junction": 0, "mallow": 13456,
         "manulla junction": 0, "nenagh": 9895, "rosslare": 2247, "sligo": 20608, "thurles": 8185, "tralee": 26079,
         "tullamore": 15598, "waterford": 60079, "westport": 6872, "wexford": 21524, "belfast": 291386}
GEO_V = 1
_WORD = re.compile(r"[^a-z]+")


def _zone():
    from zoneinfo import ZoneInfo
    return ZoneInfo(TIME_ZONE)


def service_base(day: dt.date) -> float:
    """The GTFS service day's zero: noon less 12 h, local (GTFS's own definition; right across a clock change)."""
    return dt.datetime(day.year, day.month, day.day, 12, tzinfo=_zone()).timestamp() - 12 * 3600


def local_day(now: float) -> dt.date:
    return dt.datetime.fromtimestamp(now, _zone()).date()


def town_of(name: str) -> int | None:
    n = (name or "").strip().lower()
    for k in sorted(TOWNS, key=len, reverse=True):
        if n.startswith(k):
            return TOWNS[k]
    return None


def toward_dublin(first: str, last: str) -> bool | None:
    """Lee 2026-11-09 ~00:58: forward (the green fill) LEAVING Dublin, reversed toward it; a train not touching Dublin
    leaves the larger end town (CSO 2022). None: not known (the leaving look)."""
    if last in DUBLIN:
        return True
    if first in DUBLIN:
        return False
    a, b = town_of(first), town_of(last)
    if a is None or b is None or a == b:
        return None
    return b > a


def _norm(name: str) -> str:
    n = re.sub(r"\(.*?\)", "", (name or "").lower())
    n = _WORD.sub("", n)
    return n[6:] if n.startswith("dublin") and len(n) > 6 else n


def join_stations(api: list, stops: Mapping[str, Any], names: Mapping[str, str], max_km: float = 1.5) -> dict:
    """API station code -> timetable stop_id: the same name (brackets, punctuation and a leading "Dublin" dropped;
    either a prefix of the other), else the nearest stop within max_km. MEASURED 2026-11-10: 150 of 171 within 0.4 km
    and the same first word; Belfast is 2.43 km off (still Lanyon Place), Portadown 0.66; four at 0,0."""
    by_name: dict[str, list[str]] = {}
    for sid, n in names.items():
        if sid in stops:
            by_name.setdefault(_norm(n), []).append(sid)
    out = {}
    for s in api:
        code, nm = s.get("code"), _norm(s.get("name") or "")
        if not code:
            continue
        hit = by_name.get(nm) or [sid for k, v in by_name.items() if nm and len(nm) >= 4
                                  and (k.startswith(nm) or nm.startswith(k)) for sid in v]
        if len(set(hit)) == 1:
            out[code] = hit[0]
            continue
        if s.get("lat") is None:
            continue
        best, bd = None, max_km
        for sid, (la, lo) in stops.items():
            d = _km(s["lat"], s["lon"], la, lo)
            if d < bd:
                best, bd = sid, d
        if best:
            out[code] = best
    return out


def _km(a, b, c, d):
    import math
    p = math.pi / 180
    h = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def read(client: Any, consumer: str, view: Any) -> tuple[Any, str | None]:
    """(this consumer's trains, the view's version). Blocking: run in the executor. Raises the client's errors."""
    trains = client.for_consumer(consumer)
    return trains, view.static_version()


class StaticView:
    """The shared client's timetable, distilled by trip for the A and B codes, with what the timetable-driven estimate
    needs beside the lines: per trip its code, service, direction and span; the services' dates for a week from
    yesterday (Dublin); the API stations joined to the stops. The version carries the Dublin date, so the dates are
    distilled again every day even when the NTA's file has not changed (MEASURED: not rebuilt on 2026-11-09)."""

    def __init__(self, client: Any, consumer: str = INTERCITY, clock: Any = None) -> None:
        self._client, self._consumer = client, consumer
        import time as _t
        self._clock = clock or _t.time

    def static_version(self) -> str | None:
        v = self._client.static_version()
        return None if v is None else f"{v}|{local_day(self._clock()).isoformat()}|g{GEO_V}"

    def static_path(self) -> str | None:
        return self._client.static_path()

    def distill_geometry(self) -> dict[str, Any] | None:
        path = self._client.static_path()
        if path is None:
            return None
        with open(path, "rb") as fh:
            raw = fh.read()
        return distill(raw, self._client.stations(), self._consumer, local_day(self._clock()))


def distill(raw: bytes, api_stations: list, consumer: str, today: dt.date) -> dict[str, Any]:
    """The NTA zip -> geometry.distill by trip, cut to `consumer`'s codes, with `ir_trips` (trip_id -> [code, service,
    toward Dublin, first departure s, last arrival s, Enterprise]), `ir_dates` (service -> ISO dates, yesterday to six
    days on), `ir_stations` (API code -> stop_id)."""
    d = geometry.distill(raw, trip_keys=True)
    z = zipfile.ZipFile(io.BytesIO(raw))

    def rows(name):
        with z.open(name) as f:
            yield from csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))

    keep: dict[str, tuple[str, str]] = {}
    for r in rows("trips.txt"):
        code = (r.get("trip_short_name") or "").strip().upper()
        if consumer_of(code) == consumer:
            keep[(r.get("trip_id") or "").strip()] = (code, (r.get("service_id") or "").strip())
    names = d.get("stop_names") or {}
    trips: dict[str, list] = {}
    for tid, rws in (d.get("trip_stops") or {}).items():
        if tid not in keep or len(rws) < 2:
            continue
        code, sid = keep[tid]
        first, last = names.get(rws[0][1], ""), names.get(rws[-1][1], "")
        dep0 = rws[0][3] if rws[0][3] is not None else rws[0][2]
        arr1 = rws[-1][2] if rws[-1][2] is not None else rws[-1][3]
        if dep0 is None or arr1 is None:
            continue
        ent = any(BELFAST in names.get(r[1], "") for r in rws)
        trips[tid] = [code, sid, toward_dublin(first, last), dep0, arr1, ent]
    for k in ("trains", "train_routes", "trip_stops", "trip_numbers"):
        d[k] = {t: v for t, v in (d.get(k) or {}).items() if t in trips}
    used = {s for sh in d["trains"].values() for s in sh}
    d["shapes"] = {k: v for k, v in (d.get("shapes") or {}).items() if k in used}
    dates = [today + dt.timedelta(days=i) for i in range(-1, 7)]
    days = geometry.service_days(rows, z.namelist(), dates)
    services = {v[1] for v in trips.values()}
    d["ir_dates"] = {s: sorted(days.get(s, ())) for s in services}
    d["ir_trips"] = trips
    d["ir_stations"] = join_stations(api_stations or [], d.get("stops") or {}, names)
    d["ir_v"] = GEO_V
    return d


def line_name(code: str, enterprise: bool, first: str, last: str) -> str:
    """The hover's line: "Irish Rail A700 · Dublin Heuston–Galway (Ceannt)"; the Enterprise by its own name."""
    brand = "Enterprise" if enterprise else "Irish Rail"
    ends = "–".join(("Dublin Connolly" if x == "Connolly" else x) for x in (first, last) if x)
    return f"{brand} {code} · {ends}" if ends else f"{brand} {code}"


def _show(name: str) -> str:
    return "Dublin Connolly" if name == "Connolly" else name


class IrishRailRealtime:
    """Per config entry: each run's last delay from Irish Rail, and the runs it said had terminated."""

    def __init__(self) -> None:
        self._delay: dict[str, tuple[int, float]] = {}
        self._done: dict[str, float] = {}
        self.ghosts = 0
        self.early = 0

    @staticmethod
    def genuine(rep: Mapping[str, Any], day: dt.date, start: float, end: float, now: float) -> bool:
        """Whether a report is THIS run's (module docstring)."""
        if rep.get("status") not in ("R", "T"):
            return False
        ot = rep.get("origin_time")
        if ot is not None:
            if abs(ot - start) > MATCH_S:
                return False
        elif rep.get("date") != day.isoformat():
            return False
        late = rep.get("delay_s") or 0
        return start - PRE_DEPARTURE_S - MATCH_S <= now <= end + max(late, 0) + GHOST_S

    def parse(self, trains: Any, now: float, geometry_: Mapping[str, Any] | None = None) -> Snapshot | None:
        """This consumer's trains (the client's dicts) -> Snapshot. None when they did not arrive (the client raises
        when the feed fails; an EMPTY list is a quiet hour, and the timetable still runs)."""
        if trains is None:
            return None
        geo = geometry_ or {}
        trips = geo.get("ir_trips") or {}
        dates = geo.get("ir_dates") or {}
        rows_of = geo.get("trip_stops") or {}
        stops = geo.get("stops") or {}
        names = geo.get("stop_names") or {}
        stations = geo.get("ir_stations") or {}
        snap = Snapshot()

        def skip(reason: str) -> None:
            snap.skipped[reason] = snap.skipped.get(reason, 0) + 1

        reports: dict[str, list] = {}
        for t in trains:
            reports.setdefault(t.get("code") or "", []).append(t)
        if not trips:
            skip("no_timetable")
            return snap
        today = local_day(now)
        matched: set[int] = set()
        seen: set[str] = set()
        for day in (today - dt.timedelta(days=1), today):
            iso, base = day.isoformat(), service_base(day)
            for tid, (code, sid, toward, first, last, ent) in trips.items():
                if iso not in dates.get(sid, ()):
                    continue
                start, end = base + first, base + last
                if now < start - PRE_DEPARTURE_S or now > end + MAX_LATE_S:
                    continue
                key = f"{code}-{day.day}"
                if key in seen:
                    skip("duplicate")
                    continue
                seen.add(key)
                rep = next((r for r in reports.get(code, ()) if self.genuine(r, day, start, end, now)), None)
                if rep is not None:
                    matched.add(id(rep))
                    if rep.get("status") == "R" and (rep.get("delay_s") or 0) < -EARLY_S:
                        # Not believed: no delay, no floor (EARLY_S).
                        self.early += 1
                        rep = None
                if rep is not None:
                    if rep.get("status") == "T":
                        self._done[key] = now
                    elif rep.get("delay_s") is not None:
                        self._delay[key] = (int(rep["delay_s"]), now)
                if key in self._done:
                    skip("terminated")
                    continue
                delay = self._delay[key][0] if key in self._delay else None
                if now > end + max(delay or 0, 0) + FINISHED_S:
                    skip("finished")
                    continue
                self._one(snap, key, tid, code, toward, ent, base, delay, rep if rep and rep.get("status") == "R"
                          else None, rows_of.get(tid) or [], stops, names, stations, now, skip)
        self.ghosts = sum(1 for rs in reports.values() for r in rs if r.get("status") == "R" and id(r) not in matched)
        if self.ghosts:
            snap.skipped["ghost_or_unmatched"] = self.ghosts
        for store in (self._delay, self._done):
            for k in [k for k, v in store.items() if now - (v[1] if isinstance(v, tuple) else v) > FORGET_S]:
                store.pop(k, None)
        return snap

    def _one(self, snap, key, tid, code, toward, ent, base, delay, rep, rows, stops, names, stations, now, skip):
        calls = []
        for _, stop, a, d in rows:
            aa = base + a if a is not None else None
            ad = base + d if d is not None else None
            c = {"stop": stop, "aimed_arrival": aa, "aimed_departure": ad}
            if delay is not None:
                c["expected_arrival"] = aa + delay if aa is not None else None
                c["expected_departure"] = ad + delay if ad is not None else None
            calls.append(c)
        floor = None
        if rep is not None and rep.get("last_location"):
            sid = stations.get(rep["last_location"])
            idx = [i for i, c in enumerate(calls) if c["stop"] == sid]
            if idx:
                floor = idx[0]
                c, kind = calls[floor], rep.get("last_location_type")
                late = delay or 0
                if kind == "A" and (c["aimed_arrival"] or c["aimed_departure"]) is not None:
                    c["actual_arrival"] = (c["aimed_arrival"] or c["aimed_departure"]) + late
                elif kind == "D" and (c["aimed_departure"] or c["aimed_arrival"]) is not None:
                    c["actual_departure"] = (c["aimed_departure"] or c["aimed_arrival"]) + late
        times = call_times(calls)
        if len(times) < 2:
            skip("no_times")
            return
        where = place(times, now)
        if floor is not None:
            j = next((k for k, t in enumerate(times) if t[0] is calls[floor]), None)
            if j is not None and (where is None or where[1] < j):
                kind = rep.get("last_location_type")
                where = ("running", j) if kind == "D" and j < len(times) - 1 else ("standing", j)
        if where is None:
            skip("not_running")
            return
        state, i = where
        call, arr_i, dep_i, _ = times[i]
        pos = stops.get(call["stop"])
        if not pos:
            skip("no_stop_position")
            return
        when = arr_i if state == "standing" and now >= arr_i else (dep_i if state == "running" else now)
        number = number_of(code) or code
        snap.observations.append(Obs(
            vehicle_id=key, lat=float(pos[0]), lon=float(pos[1]),
            observed_at=dt.datetime.fromtimestamp(min(when, now), dt.timezone.utc), in_service=True,
            train=number, line=None, reported_course=None, trip_id=key))
        first, last = names.get(rows[0][1], ""), names.get(rows[-1][1], "")
        extra: dict[str, Any] = {"line_name": line_name(code, ent, first, last), NO_FIX_KEY: True,
                                 "route_code": code, "service_family": "Enterprise" if ent else "InterCity",
                                 "destination": rows[-1][1]}
        if toward is not None:
            extra["toward_hub"] = toward
        snap.route_keys[key] = tid
        snap.extras[key] = extra
        nxt = times[i + 1] if i + 1 < len(times) else None
        if state == "standing" or nxt is None:
            extra.update(HOLD)
        else:
            extra[HELD_SPEED_KEY] = None
            extra[TIMED_AFTER_KEY] = 0.0
            extra[AIM_ETA_KEY] = nxt[1]
        if nxt is None:
            return
        ncall, narr, _, known = nxt
        snap.stop_codes[key] = ncall["stop"]
        name = names.get(ncall["stop"])
        if name:
            snap.next_stops[key] = (_show(name), narr)
        aimed = ncall.get("aimed_arrival")
        if aimed is None:
            aimed = ncall.get("aimed_departure")
        if known and aimed is not None:
            snap.trip_delays[key] = int(round(narr - aimed))
