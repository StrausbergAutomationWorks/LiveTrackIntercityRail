"""Entur (Norway) -> one Snapshot, for one railroad's codespace. No Home Assistant imports.

The shared client saw_livetrack.entur polls Entur once for every Live Track integration, per codespace (VYG Vy, GOA
Go-Ahead Norge), and routes each vehicle to ONE consumer by its line's letter (06_MAP_CONTRACT.md D1): F, RE, RX and R
lines here ("intercity"), L lines and Flytoget to Live Track Commuter Rail, rail-replacement buses to nobody yet (Lee
2026-11-07; Intercity SSOT 8.8, backlog 326). This module reads one consumer's two feeds in one codespace, so every
rule here is tested offline against recorded bodies.

MEASURED 2026-11-07 (20_Research/_shared/norway/): the positions are GraphQL's (the client's docstring: fresher, more
complete), with no speed, and no bearing passed on (GraphQL's is the chord of its own last two fixes), so the estimate
takes the line's bearing and derives a speed from two fixes (Operator.derive_speed); every live trip id is in its
railroad's timetable.

IDENTITY "<train number>-<day of start date>". The number is Vy's vehicle.id's (1672-2026-11-07), else the trip id's
leading digits (Go-Ahead's vehicle.id is the unit, 72-04; GOA:ServiceJourney:715-LOD_68400-R is train 715). MEASURED on
the capture (bin\\no_cap_analyse.txt, no_cap_check2.txt): the two agree on 2,199 of 2,245 Vy rows; the 46 that differ
are one train, RE20 Göteborg-Oslo S, trip VYG:ServiceJourney:398-138_690446-R, whose vehicle.id is 138-2026-11-07: 398
in Sweden, 138 in Norway, and Vy's own id says 138. The shared client gives the date (from GraphQL's
datedServiceJourney, else a Vy vehicle.id).

LABEL the line code (R13, F4; Lee 2026-11-07), set as marker_label by the operator's styling from the record-only
`route_code`; the number goes in the hover box's one line, `line_name` "Train 1672 · Drammen-Oslo S-Dal" (the card
shows `line_name` and never `train` there, 06_MAP_CONTRACT.md D4b).

NEXT STOP: the timetable plus the update's delays, first stop still ahead (saw_livetrack.gtfs.schedule.
next_by_timetable), never the origin. The name is the parent station's.

TUNNELS (Lee 2026-11-07 18:10: "the long tunnels around Oslo should be handled like the tunnel in Helsinki"; the
capture, bin\\no_tunnels.txt): a train's fix FREEZES where a tunnel takes its signal, for minutes, and the next comes
from the far end: Oslotunnelen (Oslo S-Skøyen, where the fix freezes AT Oslo S), Lysaker-Sandvika, Sandvika-Asker,
Romeriksporten, Lieråsen and Follobanen, each way (TUNNELS). As Live Track Commuter Rail's push through the airport
tunnel: a fix frozen over FROZEN_S near a way in, with the next stop beyond it, is moved from the train's leaving the
stop before it, along its line to where its fixes come back, in the quickest time measured, and held there until a
fresh fix takes over; before that stop's departure it is held where it stands (a STANDING train's fix freezes too:
1,199 reads at one position kept their fix time, 137 advanced; bin\\no_frozen.txt). The comeback points are stops of
the distilled geometry, the timed rule's aim (TUNNEL_STOP, AIM_ETA_KEY).

HELD (Lee 2026-11-07 18:10): a frozen train whose next stop's estimate has passed (or with no stop left) stays where it
was last drawn; it is never moved on to the stop. Not in a tunnel: a push runs on to where the fixes come back, and
once begun on a fix it runs on whatever the timetable says meanwhile, until a fresh fix.

SERVICE DAY: Entur's run date is not always the GTFS service day (a train timetabled 23:5x-24:xx on the 7th carries
the 8th); the rows are read on the run date, else the day before or after, whichever spans now
(EnturRealtime._run_rows).

DIRECTION (Lee 2026-11-07, his Renfe rule): toward the hub, Oslo S, while it is still ahead; a trip that does not stop
at Oslo S takes the larger of its two end cities (data/norway_ends.json).

THE TIMETABLE is the client's, on disk (Vy's 66 MB), cut here to this railroad's lines, rail trips only, running the
day before, on or after today in Oslo, then distilled by trip (geometry.distill, trip_keys). Its version carries
Oslo's date, so a new day cuts again.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
import re
import zipfile
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo

from saw_livetrack.entur import TIME_ZONE, is_bus, letters, line_from_route_id, local_id
from saw_livetrack.entur import TUNNEL_ALONG_X, TUNNEL_ENTRY_M
from saw_livetrack.entur import TUNNELS as SHARED_TUNNELS
from saw_livetrack.gtfs.filter import services_on
from saw_livetrack.gtfs.realtime import Obs, position_of, vehicle_time
from saw_livetrack.gtfs.schedule import next_by_timetable, update_delays

from .. import geometry
from .base import AIM_ETA_KEY, HELD_SPEED_KEY, TIMED_AFTER_KEY, Snapshot

HUB_NAME = "Oslo S"
ENDS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "norway_ends.json")
# 2: the tunnels' comeback points are stops in the distilled geometry (TUNNEL_STOP).
DISTILL_V = 2
MAX_FIRST_AGE_S = 300.0
FINISHED_AGE_S = 300.0
# A fix older than this is FROZEN: Entur keeps a fix's time while it has no newer one, in a tunnel and while a train
# stands (the module docstring). 60 s keeps a margin over GraphQL's 30 s refresh (bin\\no_frozen.txt).
FROZEN_S: float | None = 60.0
# The extras that HOLD a train where it was last drawn: the timed rule at once, with no time to aim at
# (geometry.Projector._timed waits where it is), at rest.
HOLD = {HELD_SPEED_KEY: 0.0, TIMED_AFTER_KEY: 0.0, AIM_ETA_KEY: None}
# THE TUNNELS, each way: (id, where its fixes freeze going in, where they come back, the quickest dark time in s,
# passages measured). Since 2026-11-09 (Lee 17:10: "Switch") the shared list, saw_livetrack.entur.TUNNELS: Oslo's
# fourteen, measured here 2026-11-07 and hoisted in 0.2.28 for Live Track Commuter Rail, equal row for row, and
# Ulriken (0.2.30), which Intercity's F4 and R40 now get too; its entry and along limits with it. It read: Intercity's
# own copy of Oslo's fourteen (bin\\no_tunnels.txt, no_tunnels2.txt), Ulriken "left out".
# Then this railroad's own, PROVISIONAL: the Bergen Line (Lee 2026-11-09 17:10: "more capture to finalize, but keep
# them running until then"). MEASURED on the WHOLE capture of 2026-11-07/08 (21:34Z-11:04Z, bin\\bl_tunnels_full.txt;
# the first analysis saw its first 2.6 h): the same rule, a fix still 60 s or more, then back 3 km or more away;
# quickest among the clean passages to the main comeback. Arna to Voss each way 3-5 passages; Myrdal one each way;
# toward Finse one, eastbound only. Here, not in the library: Intercity alone runs the Bergen Line (one consumer).
# They are FINALIZED from a longer capture; the passage counts say how firm each is.
BERGEN_LINE_TUNNELS = (
    ("bergensbanen_1e", (60.43035, 5.62607), (60.45849, 5.73735), 240.0, 5),     # east of Arna, eastbound
    ("bergensbanen_1w", (60.45530, 5.73220), (60.42933, 5.62471), 359.0, 3),
    ("bergensbanen_2e", (60.59936, 5.82380), (60.63772, 5.95648), 270.0, 5),
    ("bergensbanen_2w", (60.63729, 5.95183), (60.59331, 5.81875), 271.0, 3),
    ("bergensbanen_3e", (60.64638, 6.01522), (60.64684, 6.11043), 210.0, 1),     # and 2 frozen inside it: 150 s left
    ("bergensbanen_3w", (60.64634, 6.10078), (60.64669, 6.01461), 179.0, 3),
    ("bergensbanen_4e", (60.62937, 6.29156), (60.62391, 6.38804), 180.0, 4),
    ("bergensbanen_4w", (60.62324, 6.38543), (60.62996, 6.28784), 209.0, 4),     # toward Voss
    ("bergensbanen_5e", (60.72593, 7.01607), (60.73448, 7.12289), 240.0, 1),     # up to Myrdal
    ("bergensbanen_5w", (60.73325, 7.12118), (60.72531, 7.01183), 301.0, 1),
    ("bergensbanen_6e", (60.73937, 7.12501), (60.67015, 7.24363), 690.0, 1),     # Myrdal toward Finse
    ("bergensbanen_7e", (60.65884, 7.26879), (60.60255, 7.50223), 510.0, 1),
)
TUNNELS = SHARED_TUNNELS + BERGEN_LINE_TUNNELS
# The rows' digest, a part of the cached geometry's version: their comeback points are stops in it (TUNNEL_STOP), so
# a tunnel added here or in the library is distilled in at the restart, not at Oslo's next day.
TUNNELS_TAG = hashlib.sha1(repr(TUNNELS).encode("utf-8")).hexdigest()[:8]
# A frozen fix this near a tunnel's way in is taken as going in (the freeze fixes spread up to 534 m), or one already
# inside it: its distances to the way in and to the comeback point add up to at most ALONG_X times theirs (measured:
# train 1673's fix froze 1.6 km into Romeriksporten, its two distances 1.017 times; bin\\no_replay_tunnels_dbg.txt).
ENTRY_M = TUNNEL_ENTRY_M
ALONG_X = TUNNEL_ALONG_X
# A tunnel's comeback point as a stop of the distilled geometry, the timed rule's aim.
TUNNEL_STOP = "saw:tunnel:"
# A failed update poll keeps the last answer this long (const.SOURCE_GAP_S).
UPDATES_HOLD_S = 600.0
# How long a run's state outlives its last row.
FORGET_S = 3600.0
# A service day is this run's when now lies from this long before its first time to this long after its last (the
# run date Entur gives is not always the GTFS service day: EnturRealtime._run_rows). Renfe (Spain)'s window.
RUN_BEFORE_S = 2 * 3600.0
RUN_AFTER_S = 6 * 3600.0

_NUMBER = re.compile(r"^(\d{1,5})(?=[-_]|$)")
_VEHICLE_DATE = re.compile(r"-(\d{4})-(\d{2})-(\d{2})$")
_VEHICLE_NUMBER = re.compile(r"^(\d{1,5})-\d{4}-\d{2}-\d{2}$")


def number_of(trip_id: Any, vehicle_id: Any = None) -> str | None:
    """The train number: a Vy vehicle.id's ('138-2026-11-07' -> '138'), else the trip id's leading digits
    ('VYG:ServiceJourney:1672_443368-R' -> '1672', '...:715-LOD_68400-R' -> '715'); None with neither."""
    m = _VEHICLE_NUMBER.match(vehicle_id.strip()) if isinstance(vehicle_id, str) else None
    if m:
        return str(int(m.group(1)))
    m = _NUMBER.match(local_id(trip_id))
    return str(int(m.group(1))) if m else None


def identity(number: str, start_date: str | None) -> str:
    """'1672', '20261107' -> '1672-7'; the bare number with no usable start date."""
    sd = (start_date or "").strip()
    if len(sd) == 8 and sd.isdigit():
        return f"{number}-{int(sd[6:8])}"
    return number


def date_from_vehicle(vehicle_id: Any) -> str | None:
    """'1672-2026-11-07' -> '20261107'; None for any other shape (Go-Ahead's units, '72-04')."""
    m = _VEHICLE_DATE.search(vehicle_id.strip()) if isinstance(vehicle_id, str) else None
    return "".join(m.groups()) if m else None


def oslo_today() -> str:
    return dt.datetime.now(ZoneInfo(TIME_ZONE)).date().isoformat()


def train_line_name(number: str, line: str | None) -> str:
    """The hover box's line: 'Train 1672 · Drammen-Oslo S-Dal', or 'Train 1672' with no line name."""
    return f"Train {number} · {line}" if line else f"Train {number}"


def read(client: Any, consumer: str, codespace: str, view: "StaticView | None" = None) -> tuple[Any, Any, str | None]:
    """(positions, trip updates, timetable version) from the shared client. Blocking: run in the executor. Raises the
    client's errors."""
    positions, updates = client.for_consumer(consumer, codespace)
    return positions, updates, view.static_version() if view is not None else client.static_version(codespace)


# --------------------------------------------------------------------------
# The timetable
# --------------------------------------------------------------------------

def _reader(z: zipfile.ZipFile, name: str):
    fh = z.open(name)
    rd = csv.reader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline=""))
    header = next(rd, None) or []
    return header, [h.strip() for h in header], rd, fh


def _copy_rows(z: zipfile.ZipFile, out: zipfile.ZipFile, name: str, col: str, allowed: set[str],
               collect: str | None = None) -> set[str]:
    """Copy `name` keeping the rows whose `col` is in `allowed`, reading it once; the values of `collect` kept."""
    header, keys, rd, fh = _reader(z, name)
    got: set[str] = set()
    with fh:
        i = keys.index(col)
        j = keys.index(collect) if collect in keys else None
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(header)
        for row in rd:
            if len(row) > i and row[i].strip() in allowed:
                w.writerow(row)
                if j is not None and len(row) > j and row[j].strip():
                    got.add(row[j].strip())
    out.writestr(name, buf.getvalue())
    return got


def _dicts(z: zipfile.ZipFile, name: str):
    with z.open(name) as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig")):
            yield {(k or "").strip(): (v or "").strip() for k, v in r.items() if k}


def cut(raw: bytes, keep_letters: Iterable[str], days: Iterable[dt.date]) -> tuple[bytes, dict[str, tuple[str, str]]]:
    """(the zip with only the routes whose line letters are in `keep_letters`, their rail trips (no rail-replacement
    bus) running on one of `days`, and those trips' stop times, stops with their parents, and shapes; {trip_id:
    (line code, route_color)}). Blocking."""
    keep = frozenset(keep_letters)
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = z.namelist()
    routes = {}
    for r in _dicts(z, "routes.txt"):
        if letters(r.get("route_short_name")) in keep and r.get("route_id"):
            routes[r["route_id"]] = (r["route_short_name"], (r.get("route_color") or "").upper())
    running = services_on(z, list(days))
    trips: dict[str, tuple[str, str]] = {}
    shapes: set[str] = set()
    for t in _dicts(z, "trips.txt"):
        tid, rid = t.get("trip_id"), t.get("route_id")
        if not tid or rid not in routes or is_bus(tid):
            continue
        if running is not None and t.get("service_id") not in running:
            continue
        trips[tid] = routes[rid]
        if t.get("shape_id"):
            shapes.add(t["shape_id"])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as out:
        used = _copy_rows(z, out, "stop_times.txt", "trip_id", set(trips), collect="stop_id")
        parents = set()
        for s in _dicts(z, "stops.txt"):
            if s.get("stop_id") in used and s.get("parent_station"):
                parents.add(s["parent_station"])
        for name in names:
            if name == "stop_times.txt":
                continue
            if name == "routes.txt":
                _copy_rows(z, out, name, "route_id", set(routes))
            elif name == "trips.txt":
                _copy_rows(z, out, name, "trip_id", set(trips))
            elif name == "stops.txt":
                _copy_rows(z, out, name, "stop_id", used | parents)
            elif name == "shapes.txt":
                _copy_rows(z, out, name, "shape_id", shapes)
            elif name == "transfers.txt":
                continue
            else:
                out.writestr(name, z.read(name))
    return buf.getvalue(), trips


def load_ends(path: str = ENDS_FILE) -> dict[str, Any]:
    """{station name: {"population": int, ...}}; {} when the file is missing or unreadable."""
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return {}
    return d.get("ends", {}) if isinstance(d, dict) else {}


def file_tag(path: str) -> str:
    """The first 12 hex of a file's SHA-1, "none" when it cannot be read: a cache version's part for a shipped data
    file the distill reads (the end-city table). Blocking."""
    try:
        with open(path, "rb") as fh:
            return hashlib.sha1(fh.read()).hexdigest()[:12]
    except OSError:
        return "none"


def hub_index(stop_ids: list[str], names: Mapping[str, str], ends: Mapping[str, Any]) -> int | None:
    """The index of a trip's hub among its stops: its LAST Oslo S stop; else its larger end city by population
    (data/norway_ends.json, by station name); None when neither end is known, or both are as large."""
    if not stop_ids:
        return None
    oslo = [i for i, s in enumerate(stop_ids) if names.get(s) == HUB_NAME]
    if oslo:
        return oslo[-1]

    def pop(s: str) -> Any:
        v = (ends.get(names.get(s, "")) or {}).get("population")
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    a, b = pop(stop_ids[0]), pop(stop_ids[-1])
    if (a is None and b is None) or a == b:
        return None
    if b is None or (a is not None and a > b):
        return 0
    return len(stop_ids) - 1


def distill(raw: bytes, keep_letters: Iterable[str], ends: Mapping[str, Any], today: dt.date) -> dict[str, Any]:
    """A codespace's whole timetable -> the geometry the estimate needs, keyed by trip id (geometry.distill with
    trip_keys), cut to `keep_letters`' lines, rail trips running yesterday, today or tomorrow (Oslo), plus
    trip_colors (the route's colour), trip_hub (hub_index) and the window. Blocking."""
    days = [today + dt.timedelta(days=d) for d in (-1, 0, 1)]
    small, info = cut(raw, keep_letters, days)
    d = geometry.distill(small, trip_keys=True)
    names = d.get("stop_names") or {}
    hubs, colors = {}, {}
    for tid, rows in (d.get("trip_stops") or {}).items():
        h = hub_index([r[1] for r in rows], names, ends)
        if h is not None:
            hubs[tid] = h
    for tid, (_, color) in info.items():
        if color and tid in d.get("trains", {}):
            colors[tid] = color
    stops = d.setdefault("stops", {})
    for t in TUNNELS:
        stops[TUNNEL_STOP + t[0]] = list(t[2])
    d.update({"distill_v": DISTILL_V, "trip_colors": colors, "trip_hub": hubs,
              "window": [x.isoformat() for x in days], "cut_trips": len(info), "cut_bytes": len(small)})
    return d


class StaticView:
    """One codespace's timetable as route_store asks for it: a version (the client's, plus the end-city table's digest
    and Oslo's date), and the distilled geometry. The end-city table is read once, on the first distill (blocking)."""

    def __init__(self, client: Any, codespace: str, keep_letters: Iterable[str], today=oslo_today,
                 ends_path: str = ENDS_FILE) -> None:
        self.client = client
        self.codespace = codespace
        self.keep_letters = tuple(sorted(keep_letters))
        self._today = today
        self._ends_path = ends_path
        self._ends: dict[str, Any] | None = None
        self._ends_tag: str | None = None

    def static_version(self) -> str | None:
        """The distill's format, the end-city table's and the tunnels' digests, the client's version and Oslo's
        date. The digests make a new norway_ends.json or tunnel distil again at the restart; without it the cached geometry kept the old hubs
        until Oslo's next day (2026-11-08, SJ Nord's ends: Intercity SSOT 8.8). Blocking the first time (the
        digest); read() runs it in the executor."""
        v = self.client.static_version(self.codespace)
        if v is None:
            return None
        if self._ends_tag is None:
            self._ends_tag = file_tag(self._ends_path)
        return f"entur{DISTILL_V}:{self._ends_tag}:{TUNNELS_TAG}:{v}:{self._today()}"

    def static_path(self) -> str | None:
        return self.client.static_path(self.codespace)

    def distill_geometry(self) -> dict[str, Any] | None:
        path = self.static_path()
        if path is None:
            return None
        if self._ends is None:
            self._ends = load_ends(self._ends_path)
        with open(path, "rb") as fh:
            raw = fh.read()
        return distill(raw, self.keep_letters, self._ends, dt.date.fromisoformat(self._today()))


# --------------------------------------------------------------------------
# The realtime
# --------------------------------------------------------------------------

def left_at(row: tuple, delays: Mapping[int, int]) -> float | None:
    """When the train leaves this stop: its scheduled departure (else arrival) plus the delay known there, else the
    last delay known before it; None without a time."""
    seq, _, arrival, departure = row
    when = departure if departure is not None else arrival
    if when is None:
        return None
    earlier = [delays[s] for s in sorted(delays) if s <= seq]
    delay = delays.get(seq, earlier[-1] if earlier else 0)
    return when + delay


def metres(a: Any, b: Any) -> float:
    """Ground distance in m between two (lat, lon), equirectangular (good to a fraction of a percent at these
    distances)."""
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    return 6371000.0 * math.hypot((lo2 - lo1) * math.cos((la1 + la2) / 2.0), la2 - la1)


def ahead(a: Any, b: Any, e: Any, c: Any) -> bool:
    """Whether going from stop `a` to stop `b` is going the tunnel's way, from its way in `e` to its comeback `c`: the
    two directions on the ground agree (a positive dot product, longitude scaled by the cosine of latitude). It read:
    the next stop nearer the comeback than the stop left, which a train from Drammen to Oslo S passed for the
    WESTBOUND Lysaker-Sandvika (Drammen is farther west than its comeback; found by a test)."""
    k = math.cos(math.radians((a[0] + b[0]) / 2.0))
    return (b[0] - a[0]) * (c[0] - e[0]) + (b[1] - a[1]) * k * k * (c[1] - e[1]) > 0


def tunnel_at(pos: Any, prev_stop: str, next_stop: str, geo: Mapping[str, Any]) -> tuple | None:
    """The TUNNELS row a frozen fix at `pos` is going into, between the stop the train left and its next: its way in
    within ENTRY_M or the fix already inside, going the tunnel's way (`ahead`, so a train come OUT at that point is not
    sent back in), and the comeback point in this geometry. The nearest way in; None with none."""
    stops = geo.get("stops") or {}
    a, b = stops.get(prev_stop), stops.get(next_stop)
    if not a or not b:
        return None
    best = None
    for t in TUNNELS:
        d, left = metres(pos, t[1]), metres(pos, t[2])
        # Inside, and not already at the comeback point (a train standing there has come OUT).
        inside = d + left <= ALONG_X * metres(t[1], t[2]) and left > ENTRY_M
        if (d > ENTRY_M and not inside) or not ahead(a, b, t[1], t[2]) or TUNNEL_STOP + t[0] not in stops:
            continue
        if best is None or d < best[0]:
            best = (d, t)
    return best[1] if best else None


def tunnel_time(pos: Any, tunnel: tuple) -> float:
    """The quickest time from `pos` to the tunnel's comeback point: its quickest from the way in, in proportion to
    the distance left (a fix that froze inside has less to go)."""
    whole = metres(tunnel[1], tunnel[2])
    return tunnel[3] * min(1.0, metres(pos, tunnel[2]) / whole) if whole > 0 else tunnel[3]


def _terminal_forecast(rows: list, delays: Mapping[int, int]) -> float | None:
    """When the last stop's forecast falls: its scheduled arrival plus the last delay known. None without one."""
    if not rows:
        return None
    last = 0
    for seq, *_ in rows:
        if seq in delays:
            last = delays[seq]
    _, _, arrival, departure = rows[-1]
    when = arrival if arrival is not None else departure
    return None if when is None else when + last


class EnturRealtime:
    """Per config entry: which runs have had a fresh fix, and the last answer of the updates."""

    time_zone = TIME_ZONE

    def __init__(self) -> None:
        self._fresh: dict[str, float] = {}
        self._updates: Any = None
        self._updates_t = 0.0
        self._zone = None
        self._origins: dict[str, float | None] = {}
        # identity -> (fix time, TUNNELS row, start) of a push under way on that fix.
        self._push: dict[str, tuple] = {}

    def _origin(self, start_date: str) -> float | None:
        """The GTFS service day's origin as an epoch: local noon less 12 hours, the only reading that holds across a
        daylight-saving change."""
        if start_date not in self._origins:
            if len(self._origins) > 32:
                self._origins.clear()
            if self._zone is None:
                self._zone = ZoneInfo(self.time_zone)
            try:
                day = dt.datetime.strptime(start_date, "%Y%m%d")
                noon = dt.datetime(day.year, day.month, day.day, 12, tzinfo=self._zone)
                self._origins[start_date] = noon.timestamp() - 43200.0
            except ValueError:
                self._origins[start_date] = None
        return self._origins[start_date]

    def _rows(self, trip_id: str, start_date: str, geo: Mapping[str, Any]) -> list:
        """[(sequence, stop_id, arrival epoch, departure epoch)] for this run."""
        table = (geo.get("trip_stops") or {}).get(trip_id)
        if not table:
            return []
        origin = self._origin(start_date)
        if origin is None:
            return []
        return [(seq, stop, None if a is None else origin + a, None if d is None else origin + d)
                for seq, stop, a, d in table]

    def _run_rows(self, trip_id: str, start_date: str, geo: Mapping[str, Any], now: float) -> list:
        """This run's rows on the GTFS service day whose span holds `now` (from RUN_BEFORE_S before its first time
        to RUN_AFTER_S after its last): the run date Entur gives, else the day before, else the day after; with none,
        the run date's. MEASURED 2026-11-08 (bin\\no_replay_tunnels_dbg.txt): train 1179 Stabekk-Moss, run date
        2026-11-08 in both its vehicle id and its datedServiceJourney, is timetabled on the 7th's service day at
        23:5x-24:xx; read on the 8th it was a day early, its next stop a day ahead."""
        rows = self._rows(trip_id, start_date, geo)
        if not rows or self._spans(rows, now):
            return rows
        try:
            day = dt.datetime.strptime(start_date, "%Y%m%d").date()
        except ValueError:
            return rows
        for shift in (-1, 1):
            other = self._rows(trip_id, (day + dt.timedelta(days=shift)).strftime("%Y%m%d"), geo)
            if other and self._spans(other, now):
                return other
        return rows

    @staticmethod
    def _spans(rows: list, now: float) -> bool:
        times = [t for _, _, a, d in rows for t in (a, d) if t is not None]
        return bool(times) and min(times) - RUN_BEFORE_S <= now <= max(times) + RUN_AFTER_S

    def parse(self, positions: Any, updates: Any, now: float,
              geometry_: Mapping[str, Any] | None = None) -> Snapshot | None:
        """The consumer's two FeedMessages -> Snapshot. None when the positions did not arrive. An EMPTY positions
        feed is a quiet hour, not an outage: the client raises when the feed fails. `updates` may be None: the last
        answer is used for UPDATES_HOLD_S. Blocking on the first run of a date (the zone file): run in the executor."""
        if positions is None:
            return None
        geo = geometry_ or {}
        if updates is not None:
            self._updates, self._updates_t = updates, now
        elif self._updates is not None and now - self._updates_t <= UPDATES_HOLD_S:
            updates = self._updates
        snap = Snapshot()

        def skip(reason: str) -> None:
            snap.skipped[reason] = snap.skipped.get(reason, 0) + 1

        by_run: dict[tuple[str, str], Any] = {}
        for ent in getattr(updates, "entity", ()) or ():
            if ent.HasField("trip_update"):
                trip = ent.trip_update.trip
                by_run.setdefault((trip.trip_id.strip(), trip.start_date.strip()), ent.trip_update)

        names = geo.get("stop_names") or {}
        routes = geo.get("train_routes") or {}
        codes = geo.get("trip_numbers") or {}
        colors = geo.get("trip_colors") or {}
        hubs = geo.get("trip_hub") or {}
        seen: set[str] = set()
        for ent in positions.entity:
            if not ent.HasField("vehicle"):
                continue
            v = ent.vehicle
            trip_id = v.trip.trip_id.strip()
            number = number_of(trip_id, v.vehicle.id)
            if not number:
                skip("no_number")
                continue
            start = v.trip.start_date.strip() or date_from_vehicle(v.vehicle.id) or ""
            key = identity(number, start)
            if key in seen:
                skip("duplicate")
                continue
            pos = position_of(v)
            if pos is None:
                skip("no_position")
                continue
            when = vehicle_time(v)
            stamp = when.timestamp() if when is not None else None
            age = None if stamp is None else now - stamp
            if key not in self._fresh and age is not None and age > MAX_FIRST_AGE_S:
                skip("stale_first_sight")
                continue
            update = by_run.get((trip_id, start))
            delays, skipped = update_delays(update) if update is not None else ({}, set())
            rows = self._run_rows(trip_id, start, geo, now)
            forecast = _terminal_forecast(rows, delays)
            if forecast is not None and forecast < now and age is not None and age > FINISHED_AGE_S:
                skip("finished")
                continue
            self._fresh[key] = now
            seen.add(key)
            snap.observations.append(Obs(
                vehicle_id=key, lat=pos[0], lon=pos[1], observed_at=when, in_service=True,
                train=number, line=None,
                # No bearing in the feed: the line's bearing (projection.py), Fleet's chord where there is no line.
                reported_course=None, trip_id=key))
            snap.route_keys[key] = trip_id
            # Vy's route ids carry the line (VYG:Line:R13), Go-Ahead's do not (GOA:Line:50): those wait for the timetable.
            code = codes.get(trip_id) or line_from_route_id(v.trip.route_id)
            extra: dict[str, Any] = {"line_name": train_line_name(number, routes.get(trip_id))}
            if code:
                extra["route_code"] = code
            if colors.get(trip_id):
                extra["route_color"] = colors[trip_id]
            snap.extras[key] = extra
            if not rows:
                continue
            # The origin is no next stop; its delay still counts for the stop after it.
            ahead = rows[1:] if len(rows) > 1 else rows
            known = dict(delays)
            if rows[0][0] in known and ahead[0][0] not in known:
                known[ahead[0][0]] = known[rows[0][0]]
            nxt = next_by_timetable(ahead, known, skipped, now)
            index = (next((i for i, row in enumerate(rows) if row[0] == nxt[0]), len(rows) - 1)
                     if nxt is not None else None)
            hub = hubs.get(trip_id)
            if hub is not None:
                extra["toward_hub"] = hub == len(rows) - 1 if index is None else hub >= index
            frozen = FROZEN_S is not None and stamp is not None and age is not None and age > FROZEN_S
            # A push already under way on this very fix goes on to the comeback point, whatever the timetable says
            # meanwhile (measured: train 1678's next stop moved on mid-Lieråsen, the push stopped, and the marker
            # went 14 km back the way two wandering fixes had pointed; bin\\no_replay_tunnels_dbg.txt).
            pushing = self._push.get(key) if frozen else None
            if pushing is None or pushing[0] != stamp:
                self._push.pop(key, None)
                pushing = None

            def push(tunnel: tuple, start: float) -> None:
                extra[HELD_SPEED_KEY] = None
                extra[TIMED_AFTER_KEY] = start - stamp
                extra[AIM_ETA_KEY] = start + tunnel_time(pos, tunnel)
                snap.stop_codes[key] = TUNNEL_STOP + tunnel[0]
                self._push[key] = (stamp, tunnel, start)

            if nxt is None:
                if pushing is not None:
                    push(pushing[1], pushing[2])
                elif frozen:
                    extra.update(HOLD)
                continue
            _, stop, delay, eta = nxt
            snap.stop_codes[key] = stop
            if pushing is not None:
                push(pushing[1], pushing[2])
            elif frozen:
                tunnel = tunnel_at(pos, rows[index - 1][1], stop, geo) if index else None
                if tunnel is None and eta is not None and eta <= now:
                    # Frozen, and its next stop's estimate has passed (Lee 2026-11-07 18:10): HELD where it was last
                    # drawn, never moved on to the stop. Not in a tunnel: there the push below runs to where the
                    # fixes come back whatever the estimate says, as in Helsinki (measured: holding there too kept
                    # late trains at the way in until their fixes came back; bin\\no_replay_tunnels.txt).
                    extra.update(HOLD)
                if tunnel is not None:
                    # In a tunnel (TUNNELS), as Live Track Commuter Rail's airport tunnel in Helsinki: from the
                    # train's leaving the stop before it (never before its fix), along its line to where its fixes
                    # come back, in the quickest time measured, and held there until a fresh fix takes over. Before
                    # it leaves that stop by the timetable: held where it stands.
                    left = left_at(rows[index - 1], known)
                    start = max(stamp, left) if left is not None else stamp
                    if now <= start:
                        extra.update(HOLD)
                    else:
                        push(tunnel, start)
            stop_name = names.get(stop)
            if stop_name:
                snap.next_stops[key] = (stop_name, eta)
            if delays:
                # With no delay in the update nothing is said (D0).
                snap.trip_delays[key] = delay
        for k in [k for k, t in self._fresh.items() if now - t > FORGET_S]:
            self._fresh.pop(k, None)
            self._push.pop(k, None)
        return snap
