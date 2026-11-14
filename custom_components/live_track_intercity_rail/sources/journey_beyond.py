"""Journey Beyond's trains (Australia) -> one Snapshot, every train FROM ITS TIMETABLE. No Home Assistant imports.

Lee 2026-11-14 01:44 CST: The Ghan, Indian Pacific, Great Southern and The Overland "have no source for live positions
so they will be built by timetables"; 11:05 CST, the eight decisions (Intercity SSOT 8.13). No live position exists
anywhere, so every train is drawn from its timetable, as WA Trains (sources/transperth.py). Measured:
`20_Research/journey_beyond/JB_TIMETABLES_20261114.md`.

THE DATA ships with the integration and nothing is fetched, ever (decision 2: the booking site and its API are never
called by this code): data/journey_beyond_timetable.json (stations with their IANA zones, stop patterns, weekly runs)
and data/journey_beyond_lines.json.gz (each pattern's line on OpenStreetMap's track, ODbL), both written by
tools/journey_beyond.py from the hand transcription tools/journey_beyond_source.json. After the file's last departure
nothing is drawn (`last_departure`); the data needs a new transcription before then.

TIMES are local wall-clock at each station (MEASURED, decision 6): a call's minutes count from the run's first local
midnight at that station's own clock, so a run crossing zones (Sydney, Broken Hill, Adelaide, Cook, Rawlinna, Perth) and
a daylight-saving change land right. A run's departure and arrival replace its pattern's ends (the calendar wins for the
ends). A call with no time (Marla, Katherine northbound, Port Augusta, Canberra, Coffs Harbour) is REACHED AT THE
SERVICE'S AVERAGE SPEED (`avg_kmh`, 85 km/h from Journey Beyond's "in numbers" pages) from the last timed call, and the
train HOLDS there for the time left over before the next timed call (Lee 2026-11-14 13:19 CST); untimed calls in one
stretch share it by the pattern's `weights` (default 1: the 2027 Ghan's Port Augusta, a full day, 3 to Marla's
morning; Lee 13:51, "Weight the split"). A stretch the schedule leaves no time over for, or a service with no average speed, is paced
evenly along the line instead (decision 3, as first built).

WHERE A TRAIN IS: saw_livetrack.timetable (call_times, place): at its origin from 5 minutes before it leaves, standing
at a call between its arrival and departure, running between calls along its pattern's line, kept at its last call 5
minutes after arriving. No delay exists, so none is published (D0) and no lateness either.

SECTIONS: a pattern whose train reverses at a call (the Indian Pacific at Adelaide, the Great Southern at Canberra)
ships one line per section, "<pattern>#<n>", and lists the call each starts at (tools/journey_beyond.py), so no line
runs over the same track twice. A train's line is the section it is on: the last one starting at or before the call
it is at, or has just left.

IDENTITY "<service>-<day of the departure date>" (`the_ghan-22`): no train number is published. The marker is the
service's picture (operators/journey_beyond.py); `train` carries the service's name, which projection needs to place a
train on its line. HOVER "The Ghan · Adelaide–Darwin".
"""

from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import os
import time as _time
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo

from saw_livetrack.gtfs.realtime import Obs
from saw_livetrack.timetable import call_times, place

from .base import AIM_ETA_KEY, HELD_SPEED_KEY, NO_FIX_KEY, TIMED_AFTER_KEY, Snapshot
from .entur import HOLD

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
TIMETABLE_FILE = os.path.join(DATA_DIR, "journey_beyond_timetable.json")
LINES_FILE = os.path.join(DATA_DIR, "journey_beyond_lines.json.gz")
# The data's own format; a file of another version is not read.
DATA_VERSION = 1
GEO_V = 1
# The longest run is five calendar days (Indian Pacific, Perth to Sydney): a departure older than this is not out.
LOOKBACK_DAYS = 6


def decode(enc: Sequence[int]) -> list[list[float]]:
    """1e-5 degree deltas (tools/journey_beyond.py encode) -> [[lat, lon], ...]."""
    out, la, lo = [], 0, 0
    for i in range(0, len(enc) - 1, 2):
        la += enc[i]
        lo += enc[i + 1]
        out.append([round(la / 1e5, 5), round(lo / 1e5, 5)])
    return out


def load(timetable_path: str = TIMETABLE_FILE, lines_path: str = LINES_FILE) -> dict[str, Any]:
    """Both shipped files, checked: {"tt", "lines", "digest"}. Blocking (about 100 KB of gzip). Raises ValueError for a
    file of another version."""
    with open(timetable_path, "rb") as fh:
        tt_raw = fh.read()
    with open(lines_path, "rb") as fh:
        lines_raw = fh.read()
    tt = json.loads(tt_raw)
    lines = json.loads(gzip.decompress(lines_raw))
    for name, d in (("timetable", tt), ("lines", lines)):
        if d.get("v") != DATA_VERSION:
            raise ValueError(f"Journey Beyond {name} of version {d.get('v')!r}, not {DATA_VERSION}")
    digest = hashlib.sha256(tt_raw + lines_raw).hexdigest()
    return {"tt": tt, "lines": lines, "digest": digest}


def local_epoch(day: dt.date, minute: int, zone: str) -> float:
    """Epoch seconds of `minute` minutes after local midnight of `day` (whole days carried) at `zone`'s wall clock."""
    d = day + dt.timedelta(days=minute // 1440)
    hh, mm = divmod(minute % 1440, 60)
    return dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=ZoneInfo(zone)).timestamp()


def run_calls(tt: Mapping[str, Any], pid: str, day: dt.date, dep: int, arr: int) -> list[dict[str, Any]] | None:
    """One run's calls with epoch `aimed_arrival` / `aimed_departure` (THE module's TIMES), the run's departure and
    arrival in place of the pattern's ends, a call with no time reached at the average speed and held for the time left
    over, else paced along the line (`paced` True). None when the pattern or a zone is unknown, or the times do not run
    forward."""
    pat = (tt.get("patterns") or {}).get(pid)
    stations = tt.get("stations") or {}
    if not pat or len(pat.get("calls") or ()) < 2:
        return None
    rows = [list(c) for c in pat["calls"]]
    rows[0][1], rows[0][2] = None, dep
    rows[-1][1], rows[-1][2] = arr, None
    out: list[dict[str, Any]] = []
    for sid, a, d, m in rows:
        st = stations.get(sid)
        if not st:
            return None
        zone = st[3]
        out.append({"stop": sid, "m": float(m),
                    "aimed_arrival": None if a is None else local_epoch(day, a, zone),
                    "aimed_departure": None if d is None else local_epoch(day, d, zone)})
    speed = ((tt.get("services") or {}).get(pat.get("service")) or {}).get("avg_kmh")
    mps = float(speed) / 3.6 if speed else None
    timed = [i for i, c in enumerate(out) if c["aimed_arrival"] is not None or c["aimed_departure"] is not None]
    for before, after in zip(timed, timed[1:]):
        gap = range(before + 1, after)
        if not gap:
            continue
        t0 = out[before]["aimed_departure"] if out[before]["aimed_departure"] is not None else out[before]["aimed_arrival"]
        t1 = out[after]["aimed_arrival"] if out[after]["aimed_arrival"] is not None else out[after]["aimed_departure"]
        m0, m1 = out[before]["m"], out[after]["m"]
        left = (t1 - t0) - (m1 - m0) / mps if mps else 0.0
        weights = [float((pat.get("weights") or {}).get(out[k]["stop"], 1)) for k in gap]
        holds = [left * w / sum(weights) for w in weights] if left > 0 else None
        held = 0.0
        for n, k in enumerate(gap):
            c = out[k]
            if holds is None:
                share = (c["m"] - m0) / (m1 - m0) if m1 > m0 else 0.5
                c["aimed_arrival"] = c["aimed_departure"] = t0 + share * (t1 - t0)
            else:
                c["aimed_arrival"] = t0 + (c["m"] - m0) / mps + held
                held += holds[n]
                c["aimed_departure"] = c["aimed_arrival"] + holds[n]
            c["paced"] = True
    last = None
    for c in out:
        for k in ("aimed_arrival", "aimed_departure"):
            t = c[k]
            if t is None:
                continue
            if last is not None and t < last:
                return None
            last = t
    return out


def departures(tt: Mapping[str, Any], now: float):
    """(pattern, date, departure, arrival) of every run that left within LOOKBACK_DAYS of `now` or leaves within a day."""
    today = dt.datetime.fromtimestamp(now, dt.timezone.utc).date()
    lo, hi = today - dt.timedelta(days=LOOKBACK_DAYS), today + dt.timedelta(days=1)
    for pid, first, weeks, dep, arr in tt.get("runs") or ():
        start = dt.date.fromisoformat(first)
        for k in range(int(weeks)):
            day = start + dt.timedelta(weeks=k)
            if day > hi:
                break
            if day >= lo:
                yield pid, day, int(dep), int(arr)


def section_of(pattern: Mapping[str, Any], i: int) -> int:
    """The section a train at (or just leaving) call i is on: the last whose first call is at or before i."""
    return max((n for n, s in enumerate(pattern.get("sections") or [0]) if s <= i), default=0)


def hover(service: str, names: Sequence[str]) -> str:
    """"The Ghan · Adelaide–Darwin" (HOVER)."""
    ends = "–".join(n for n in (names[0], names[-1]) if n) if names else ""
    return f"{service} · {ends}" if service and ends else (service or ends)


class StaticView:
    """The shipped data as the route store's timetable: lines and stations distilled once, the timetable beside them
    (`jb`). Its version is the files' digest, so a new release distills again and nothing else does."""

    def __init__(self, loader=load) -> None:
        self._loader = loader
        self._data: dict[str, Any] | None = None

    def _get(self) -> dict[str, Any]:
        if self._data is None:
            self._data = self._loader()
        return self._data

    def static_version(self) -> str | None:
        return f"jb{self._get()['digest'][:12]}|g{GEO_V}"

    def static_path(self) -> str | None:
        return None

    def distill_geometry(self) -> dict[str, Any] | None:
        return distill(self._get())


def read(view: StaticView) -> str | None:
    """The view's version; the first call reads the shipped files. Blocking: run in the executor."""
    return view.static_version()


def distill(data: Mapping[str, Any]) -> dict[str, Any]:
    """The shipped data -> the geometry the route store keeps and the Projector reads: each section of a pattern is a
    "train" whose one shape is its own line ("<pattern>#<n>"); stops and their names; the timetable as `jb`."""
    from .. import geometry
    tt, lines = data["tt"], data["lines"]
    services = tt.get("services") or {}
    shapes = {pid: decode(v[1]) for pid, v in (lines.get("lines") or {}).items()}
    pats = tt.get("patterns") or {}
    return {"v": geometry.GEOMETRY_VERSION,
            "stops": {sid: [s[1], s[2]] for sid, s in (tt.get("stations") or {}).items()},
            "stop_names": {sid: s[0] for sid, s in (tt.get("stations") or {}).items()},
            "trains": {sid: [sid] for sid in shapes if sid.split("#")[0] in pats},
            "train_routes": {sid: (services.get(pats[sid.split("#")[0]]["service"]) or {}).get("name", "")
                             for sid in shapes if sid.split("#")[0] in pats},
            "shapes": shapes, "jb": tt, "jb_v": GEO_V}


class JourneyBeyondTimetable:
    """Per config entry: the runs out now, drawn as estimates. Holds no state between polls."""

    def parse(self, now: float, geometry_: Mapping[str, Any] | None) -> Snapshot:
        """Snapshot at epoch `now`. An empty timetable (not yet distilled) publishes nothing and says so (skipped
        "no_timetable"); a run whose times do not run forward is skipped "bad_times"."""
        snap = Snapshot()
        tt = (geometry_ or {}).get("jb") or {}
        if not tt:
            snap.skipped["no_timetable"] = 1
            return snap
        for pid, day, dep, arr in departures(tt, now):
            calls = run_calls(tt, pid, day, dep, arr)
            if calls is None:
                snap.skipped["bad_times"] = snap.skipped.get("bad_times", 0) + 1
                continue
            times = call_times(calls)
            where = place(times, now)
            if where is None:
                continue
            self._one(snap, tt, pid, day, calls, times, where, now)
        return snap

    @staticmethod
    def _one(snap: Snapshot, tt, pid: str, day: dt.date, calls, times, where, now: float) -> None:
        state, i = where
        pat = tt["patterns"][pid]
        service_id = pat["service"]
        service = ((tt.get("services") or {}).get(service_id) or {}).get("name", service_id)
        stations = tt.get("stations") or {}
        call, arr_i, dep_i, _ = times[i]
        st = stations[call["stop"]]
        key = f"{service_id}-{day.day}"
        when = arr_i if state == "standing" and now >= arr_i else (dep_i if state == "running" else now)
        snap.observations.append(Obs(
            vehicle_id=key, lat=float(st[1]), lon=float(st[2]),
            observed_at=dt.datetime.fromtimestamp(min(when, now), dt.timezone.utc), in_service=True,
            train=service, line=None, reported_course=None, trip_id=key))
        names = [stations[c["stop"]][0] for c in calls]
        extra: dict[str, Any] = {"line_name": hover(service, names), NO_FIX_KEY: True, "route_code": pid,
                                 "service_family": service_id, "service_direction": pat["dir"],
                                 "destination": calls[-1]["stop"]}
        snap.route_keys[key] = f"{pid}#{section_of(pat, i)}"
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
        snap.stop_codes[key] = nxt[0]["stop"]
        snap.next_stops[key] = (stations[nxt[0]["stop"]][0], nxt[1])


def last_departure(tt: Mapping[str, Any]) -> dt.date | None:
    """The file's last departure date (the data's horizon), or None."""
    v = tt.get("last_departure")
    try:
        return dt.date.fromisoformat(v) if v else None
    except ValueError:
        return None


__all__ = ["DATA_VERSION", "JourneyBeyondTimetable", "StaticView", "decode", "departures", "distill", "load",
           "local_epoch", "read", "run_calls", "section_of"]
_ = _time  # (the module keeps no clock of its own; parse is given `now`)
