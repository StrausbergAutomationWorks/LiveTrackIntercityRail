"""Renfe's long-distance GTFS-Realtime (AV, LD and MD trains, Spain) -> one Snapshot. No Home Assistant imports.

Backlog 324; every rule here was MEASURED on the capld capture (2026-11-05 23:53 to 11-06 05:53 CST, 1,428
position reads 15 s apart, bin\\es_renfe\\capld; bin\\es_ld_analyse.txt, es324_dups.txt) or DECIDED by Lee
(Intercity SSOT 8.7). Data: Renfe (data.renfe.com), CC BY 4.0, keyless:
    vehicle_positions_LD.pb   positions, stated every 15 s
    trip_updates_LD.pb        one stop and a delay per trip, stated every 30 s
    google_transit.zip        the AV/LD/MD timetable, about 0.8 MB, NO shapes.txt (renfe_ld_lines.py)

THE CLIENT is this integration's own (RenfeLdClient): saw_livetrack.renfe polls only the commuter feed. It has
no Home Assistant import so it can be hoisted into saw-livetrack later; one per config entry until then.

THE HEADER is stamped about 3,604 s behind the clock (p50; INFERRED: local time written as UTC) and rows carry
no vehicle timestamp, so no age is read from the feed: a fix keeps the time THIS client first saw it there.

THE TRIP ID is <5-digit number><digit><YYYY-MM-DD> (0306212026-11-05). The date opens the trip's TIMETABLE
PERIOD (service 2026-11-052026-12-12...), not the day it runs, so the run date comes from the calendar: of the
days the trip runs (yesterday, today, tomorrow in Spain), the one whose scheduled span holds now, or is nearest
it. The digit is a LEG: the train's whole trip and pieces of it, each its own trip (03062: 1 Barcelona-Madrid,
2 Lleida-Zaragoza, 3 Calatayud-Madrid, 4 Barcelona-Zaragoza). SPECIAL_<number><YYYYMMDD> trips are in no
timetable. IDENTITY "<number>-<day of the run date>", as the regionals'; LABEL the number.

ONE NUMBER ON SEVERAL ROWS (35,107 reads all at one point, 1,707 at different points): every leg of a train
carries the train's position, so at one point the train is the leg with the most timetabled stops (digit 1 in
every case read). At different points the rows are two vehicles of one number: 00752 Logrono-Madrid and a unit
coming down from Pamplona (INFERRED: they couple at Castejon), 03062 at Lleida on time and another west of
Barcelona. The train is the point nearest its last trusted fix (within CONTINUITY_M), else the point nearest
where its timetable puts it now (the stop it last left or the one it goes to next); the others are skipped.

R11-R17 (Rodalies' regionals) are in this feed too; Renfe Regionals (Catalunya) owns them (Lee 2026-11-06,
"Live hand-off", then "12 h + timetable"): every number that entry has seen live in the last HANDOFF_S, and every
train number of its own timetable, is dropped here (Handoff). MEASURED on the capture (bin\\es324_handoff2.txt):
the commuter feed lists each R train only now and then, so holding a number 30 min let 5,501 of 24,615 LD reads
of R trains through (22%); 12 h and the timetable, 336 (1.4%: two trains whose live number is not their trip's,
15030 for 30530, until first seen). With no such entry they are drawn here.

POSITIONS ARE CONTINUOUS (a fix moved on 48% of 15-s reads, p50 1,638 m from a station; INFERRED GPS-like), so
the speed comes from the last two fixes (Operator.derive_speed), and a fix unchanged for STILL_S is a train
STANDING (held speed 0). NOT the regionals' timed rule (sources/renfe.py, written for station snaps): MEASURED on
every 2nd read of the capture (bin\\es324_still.txt), the marker drawn the poll before a fix moved, against that
fix, and drawn jumps over 5 km the fix did not make:
    timed (the regionals')   p50 852 m, p90 2,632, p99 7,518; 304 jumps (a standing train timed on, then back)
    speed only               p50 835, p90 2,632, p99 9,123;    94 jumps
    standing after 45 s      p50 822, p90 2,650, p99 9,754;     4 jumps   <- built
    standing after 90 s      p50 823, p90 2,630, p99 9,604;    59 jumps

DIRECTION, for the look (Lee 10:55): a trip that stops in Madrid has Madrid as its hub, toward it until its
last Madrid stop is behind it; any other the larger of its two end cities (data/renfe_spain_ends.json); none
known, no answer, and the leaving look.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import math
import re
import threading
import time
import urllib.error
import urllib.request
import zipfile
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo

from saw_livetrack.gtfs.fleet import metres
from saw_livetrack.gtfs.realtime import Obs, decode, position_of
from saw_livetrack.gtfs.schedule import next_by_timetable
from saw_livetrack.renfe import ATTRIBUTION, FeedUnavailable, RateLimited, RenfeError, TERMS_URL  # noqa: F401

from .. import geometry
from . import renfe_ld_lines
from .base import HELD_SPEED_KEY, Snapshot
from .renfe import update_of
from .tfnsw import MOVED_M

POSITIONS_URL = "https://gtfsrt.renfe.com/vehicle_positions_LD.pb"
TRIP_UPDATES_URL = "https://gtfsrt.renfe.com/trip_updates_LD.pb"
STATIC_URL = "https://ssl.renfe.com/gtransit/Fichero_AV_LD/google_transit.zip"
USER_AGENT = "StrausbergAutomationWorks/live_track_intercity_rail"
TIME_ZONE = "Europe/Madrid"
FEED_TTL_S = 15.0
STATIC_TTL_S = 24 * 3600.0
STATIC_RETRY_S = 3600.0
STATIC_MAX_BYTES = 16 * 1024 * 1024
FEED_MAX_BYTES = 4 * 1024 * 1024
# The distilled geometry's own format: a change here distills again.
DISTILL_V = 1
# How long a run's state outlives its last row.
FORGET_S = 3600.0
# A second position of one number within this of the train's last trusted fix is the same train (my call:
# 15 s at 300 km/h is 1.25 km; a read can be missed).
CONTINUITY_M = 10000.0
# A run date is taken when now lies within this of its scheduled span (my call: trains stand at their
# origin before departure, and run late).
BEFORE_S = 2 * 3600.0
AFTER_S = 6 * 3600.0
# A number Renfe Regionals has seen stays its own this long after (Lee 2026-11-06: "12 h + timetable"; a number
# runs once a day, so the same number within 12 h is the same train).
HANDOFF_S = 12 * 3600.0
HANDOFF_KEY = "saw_live_track_intercity_rail_renfe_handoff"
# A fix unchanged this long is a train standing (bin\es324_still.txt: 30 and 45 s 4 drawn jumps, 60 s 10, 90 s 59; a
# fix stood p50 15 s, p90 39 s on the capture, es_ld_analyse.txt).
STILL_S = 45.0

_TRIP = re.compile(r"^(\d{5})(\d)(\d{4}-\d\d-\d\d)$")
_SPECIAL = re.compile(r"^SPECIAL_(\d+)(\d{8})$")
_WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
# route_short_name -> what the hover box says (Renfe's product names; my call).
FAMILY_NAMES = {
    "AVE": "AVE", "AVE INT": "AVE Internacional", "AVLO": "Avlo", "ALVIA": "Alvia", "AVANT": "Avant",
    "AVANT EXP": "Avant Exprés", "EUROMED": "Euromed", "INTERCITY": "Intercity", "MD": "MD",
    "REGIONAL": "Regional", "REG.EXP.": "Regional Exprés", "PROXIMDAD": "Proximidad", "TRENCELTA": "Trencelta",
}


def parse_trip_id(trip_id: Any) -> tuple[str | None, int | None, str | None]:
    """(number, leg digit, date): '0306212026-11-05' -> ('03062', 1, '2026-11-05') (the date opens a timetable
    period); 'SPECIAL_9505220261106' -> ('95052', None, '20261106') (the day it runs); else (None, None, None)."""
    t = trip_id.strip() if isinstance(trip_id, str) else ""
    m = _TRIP.match(t)
    if m:
        return m.group(1), int(m.group(2)), m.group(3)
    m = _SPECIAL.match(t)
    if m:
        return m.group(1), None, m.group(2)
    return None, None, None


def identity(number: str, date: str | None) -> str:
    """'03062', '20261106' -> '03062-6'; the bare number with no usable date."""
    d = (date or "").strip()
    if len(d) == 8 and d.isdigit():
        return f"{number}-{int(d[6:8])}"
    return number


def spain_today() -> str:
    return dt.datetime.now(ZoneInfo(TIME_ZONE)).date().isoformat()


# --------------------------------------------------------------------------
# The hand-off: which numbers Renfe Regionals (Catalunya) owns
# --------------------------------------------------------------------------

class Handoff:
    """Numbers one entry owns, for another to leave alone (Lee 2026-11-06): those it has seen live in the last
    hold_s, and those of its own timetable. One per Home Assistant."""

    def __init__(self, hold_s: float = HANDOFF_S) -> None:
        self.hold_s = hold_s
        self._seen: dict[str, float] = {}
        self._timetable: frozenset[str] = frozenset()
        self._lock = threading.Lock()

    def set_timetable(self, numbers: Iterable[str]) -> None:
        """The owner's timetable numbers, replacing the last."""
        with self._lock:
            self._timetable = frozenset(n for n in numbers if n)

    def clear(self) -> None:
        """The owner has gone: nothing is owned."""
        with self._lock:
            self._seen.clear()
            self._timetable = frozenset()

    def note(self, numbers: Iterable[str], now: float) -> None:
        with self._lock:
            for n in numbers:
                if n:
                    self._seen[n] = now
            for n in [n for n, t in self._seen.items() if now - t > self.hold_s]:
                del self._seen[n]

    def owned(self, now: float) -> frozenset[str]:
        with self._lock:
            return frozenset(n for n, t in self._seen.items() if now - t <= self.hold_s) | self._timetable


def handoff_for(data: dict) -> Handoff:
    """The one Handoff in `data` (hass.data), made the first time."""
    h = data.get(HANDOFF_KEY)
    if not isinstance(h, Handoff):
        h = data[HANDOFF_KEY] = Handoff()
    return h


# --------------------------------------------------------------------------
# The client
# --------------------------------------------------------------------------

def _get(url: str, user: str, timeout: float, opener=None, max_bytes: int | None = None) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": user})
    try:
        with (opener or urllib.request.urlopen)(req, timeout=timeout) as response:
            raw = response.read() if max_bytes is None else response.read(max_bytes + 1)
    except urllib.error.HTTPError as err:
        if err.code == 429:
            raise RateLimited(f"HTTP 429 from {url}") from err
        raise FeedUnavailable(f"HTTP {err.code} from {url}") from err
    except Exception as err:  # noqa: BLE001 - transport of any kind
        raise FeedUnavailable(f"{type(err).__name__} from {url}") from err
    if max_bytes is not None and len(raw) > max_bytes:
        raise FeedUnavailable(f"more than {max_bytes} bytes from {url}")
    return raw


class RenfeLdClient:
    """Renfe's AV/LD/MD feed: the two realtime files, cached FEED_TTL_S, and the timetable zip, fetched
    when asked and at most daily. Synchronous (urllib): run it in the executor. One lock covers a fetch."""

    def __init__(self, user: str = USER_AGENT, timeout: float = 30, opener=None, clock=None,
                 feed_ttl_s: float = FEED_TTL_S, static_timeout: float = 120) -> None:
        self.user, self.timeout, self.static_timeout = user, timeout, static_timeout
        self._opener = opener
        self._clock = clock or time.time
        self.feed_ttl_s = float(feed_ttl_s)
        self._lock = threading.Lock()
        self._static_lock = threading.Lock()
        self._feeds: tuple[Any, Any] | None = None
        self._fetched_at: float | None = None
        self._zip: bytes | None = None
        self._zip_at: float | None = None
        self._zip_retry = 0.0
        self.fetch_count = 0

    def snapshot(self, force: bool = False) -> tuple[Any, Any]:
        """(positions, trip updates) FeedMessages; trip updates None when that file failed. Raises
        RenfeError when the positions fail."""
        with self._lock:
            now = self._clock()
            if (not force and self._feeds is not None and self._fetched_at is not None
                    and now - self._fetched_at < self.feed_ttl_s):
                return self._feeds
            self.fetch_count += 1
            vp = decode(_get(POSITIONS_URL, self.user, self.timeout, self._opener, FEED_MAX_BYTES))
            if vp is None:
                raise FeedUnavailable(f"undecodable body from {POSITIONS_URL}")
            try:
                self.fetch_count += 1
                tu = decode(_get(TRIP_UPDATES_URL, self.user, self.timeout, self._opener, FEED_MAX_BYTES))
            except RenfeError:
                tu = None
            self._feeds, self._fetched_at = (vp, tu), now
            return self._feeds

    def static_zip(self, fetch: bool = False) -> bytes | None:
        """The timetable zip; with fetch=True, downloaded first when the copy held is a day old (or there is
        none) and no attempt failed in the last STATIC_RETRY_S. Never raises."""
        if fetch:
            with self._static_lock:
                now = self._clock()
                due = self._zip_at is None or now - self._zip_at >= STATIC_TTL_S
                if due and now >= self._zip_retry:
                    self._zip_retry = now + STATIC_RETRY_S
                    try:
                        self.fetch_count += 1
                        raw = _get(STATIC_URL, self.user, self.static_timeout, self._opener, STATIC_MAX_BYTES)
                        zipfile.ZipFile(io.BytesIO(raw)).testzip()
                        self._zip, self._zip_at = raw, now
                    except Exception:  # noqa: BLE001 - keep the last copy
                        pass
        return self._zip


def read(client: RenfeLdClient, view: "StaticView | None" = None) -> tuple[Any, Any, str | None]:
    """(positions, trip updates, timetable version). Blocking: run in the executor."""
    positions, updates = client.snapshot()
    return positions, updates, view.static_version() if view is not None else None


# --------------------------------------------------------------------------
# The timetable
# --------------------------------------------------------------------------

def _rows(z: zipfile.ZipFile, name: str):
    if name not in z.namelist():
        return
    with z.open(name) as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")):
            # Renfe pads every field (05_SHARED_LESSONS.md B5).
            yield {(k or "").strip(): (v or "").strip() for k, v in r.items() if k}


def running_days(z: zipfile.ZipFile, days: list[dt.date]) -> dict[str, list[str]]:
    """{service_id: [YYYYMMDD, ...]}: the `days` each service runs, DAY BY DAY (calendar.txt, then that
    day's calendar_dates.txt: 1 adds, 2 removes). Measured 2026-11-06 (bin\\es324_reg3.txt): applying a
    removal once over the whole window dropped trains that ran on its other days (15001 and others)."""
    cal = list(_rows(z, "calendar.txt"))
    by_date: dict[str, list] = {}
    for r in _rows(z, "calendar_dates.txt"):
        by_date.setdefault(r.get("date", ""), []).append(r)
    out: dict[str, list[str]] = {}
    for day in days:
        ymd, wd = day.strftime("%Y%m%d"), _WEEKDAYS[day.weekday()]
        on = {r["service_id"] for r in cal if r.get("service_id") and r.get(wd) == "1"
              and r.get("start_date", "") <= ymd <= r.get("end_date", "")}
        for r in by_date.get(ymd, ()):
            if r.get("exception_type") == "1":
                on.add(r["service_id"])
            elif r.get("exception_type") == "2":
                on.discard(r["service_id"])
        for s in on:
            out.setdefault(s, []).append(ymd)
    return out


def _seconds(text: str | None) -> int | None:
    try:
        h, m, s = (text or "").strip().split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)
    except ValueError:
        return None


def is_madrid(name: str | None) -> bool:
    return (name or "").strip().lower().startswith("madrid")


def hub_index(stop_ids: list[str], names: Mapping[str, str], ends: Mapping[str, Mapping[str, Any]]) -> int | None:
    """The index of the trip's hub among its stops: its LAST Madrid stop; else its larger end city by
    population (data/renfe_spain_ends.json); None when neither end is known, or both are as large."""
    if not stop_ids:
        return None
    mad = [i for i, s in enumerate(stop_ids) if is_madrid(names.get(s))]
    if mad:
        return mad[-1]

    def pop(s):
        v = (ends.get(s) or {}).get("population")
        return v if isinstance(v, (int, float)) else None
    a, b = pop(stop_ids[0]), pop(stop_ids[-1])
    if a is None and b is None or a == b:
        return None
    if b is None or (a is not None and a > b):
        return 0
    return len(stop_ids) - 1


def distill(raw: bytes, lines: renfe_ld_lines.ShippedLines, ends: Mapping[str, Mapping[str, Any]],
            today: dt.date) -> dict[str, Any]:
    """The timetable's trips running yesterday, today or tomorrow (Spain) -> the geometry the estimate needs,
    JSON-ready, keyed by trip id (geometry.distill's trip_keys shape): stops, stop_names, trip_stops, trains
    and shapes (each trip's line assembled from the shipped lines, shared by every trip of one stop pattern
    and choice), plus trip_dates (the days each runs), trip_families, trip_km (its line's length) and
    trip_hub (hub_index). Blocking, about a second."""
    z = zipfile.ZipFile(io.BytesIO(raw))
    days = [today + dt.timedelta(days=d) for d in (-1, 0, 1)]
    runs = running_days(z, days)
    stops: dict[str, list[float]] = {}
    names: dict[str, str] = {}
    for r in _rows(z, "stops.txt"):
        sid = r.get("stop_id")
        try:
            stops[sid] = [round(float(r["stop_lat"]), 6), round(float(r["stop_lon"]), 6)]
        except (KeyError, TypeError, ValueError):
            continue
        if r.get("stop_name"):
            names[sid] = r["stop_name"]
    family = {r["route_id"]: (r.get("route_short_name") or "").upper() for r in _rows(z, "routes.txt")
              if r.get("route_id")}
    trip_dates, trip_families = {}, {}
    for t in _rows(z, "trips.txt"):
        tid, sid = t.get("trip_id"), t.get("service_id")
        if tid and sid in runs:
            trip_dates[tid] = runs[sid]
            trip_families[tid] = family.get(t.get("route_id", ""), "")
    seq: dict[str, list] = {}
    for r in _rows(z, "stop_times.txt"):
        tid = r.get("trip_id")
        if tid not in trip_dates:
            continue
        try:
            n = int(r["stop_sequence"])
        except (KeyError, ValueError):
            continue
        seq.setdefault(tid, []).append((n, r.get("stop_id", ""), _seconds(r.get("arrival_time")),
                                        _seconds(r.get("departure_time")),
                                        r.get("pickup_type") == "1" and r.get("drop_off_type") == "1"))
    # Each trip's line as LEGS of the shipped pair lines, every line stored once (geometry.line_from_legs).
    shape_legs: dict[str, list] = {}
    pair_lines: dict[str, Any] = {}
    trains, trip_stops, trip_km, trip_hub = {}, {}, {}, {}
    made: dict[tuple, tuple[str, float]] = {}
    straight = 0
    for tid, rows_ in seq.items():
        rows_.sort()
        ids = [s for _, s, _, _, _ in rows_]
        fam = trip_families.get(tid, "")
        key = (tuple(ids), renfe_ld_lines.preferred_gauge(fam))
        if key not in made:
            legs, length = lines.plan(ids, stops, fam)
            straight += sum(1 for leg in legs if leg[2] is None)
            shape = "p" + hashlib.sha1(json.dumps(legs).encode()).hexdigest()[:12]
            if legs:
                shape_legs.setdefault(shape, legs)
                for _, _, k in legs:
                    if k is not None and k not in pair_lines:
                        pair_lines[k] = list(lines.encoded(k))
            made[key] = (shape, length)
        shape, length = made[key]
        if shape in shape_legs:
            trains[tid] = [shape]
        trip_km[tid] = round(length / 1000.0, 1)
        # A row nobody boards or leaves is no stop (geometry.distill).
        kept = [[n, s, a, d] for n, s, a, d, skip in rows_ if not skip]
        trip_stops[tid] = kept
        h = hub_index([s for _, s, _, _ in kept], names, ends)
        if h is not None:
            trip_hub[tid] = h
    info = dict(lines.meta)
    return {"v": geometry.GEOMETRY_VERSION, "distill_v": DISTILL_V, "stops": stops, "stop_names": names,
            "trains": trains, "shapes": {}, "shape_legs": shape_legs, "pair_lines": pair_lines,
            "trip_stops": trip_stops, "trip_dates": trip_dates,
            "trip_families": {k: v for k, v in trip_families.items() if k in seq}, "trip_km": trip_km,
            "trip_hub": trip_hub, "window": [d.isoformat() for d in days], "straight_legs": straight,
            "lines_built": info.get("built"), "osm_base": info.get("osm_base")}


class StaticView:
    """The timetable as route_store asks for it: a version, and the distilled geometry. The shipped lines
    and the end-city table are read once, on the first distill (blocking)."""

    def __init__(self, client: RenfeLdClient, today=spain_today, lines_path: str = renfe_ld_lines.LINES_FILE,
                 ends_path: str = renfe_ld_lines.ENDS_FILE) -> None:
        self.client = client
        self._today = today
        self._lines_path, self._ends_path = lines_path, ends_path
        self._lines: renfe_ld_lines.ShippedLines | None = None
        self._ends: dict | None = None
        self._tag: str | None = None

    def static_version(self) -> str:
        """The shipped lines' and end-city table's digests, the distill's format and Spain's date: a new day, a new
        release of the lines or of the ends, or a new distill distills again. The ends' digest since 2026-11-09: the
        hubs are distilled into the cached geometry, which otherwise kept the old ones until Spain's next day (as
        Norway's did, Intercity SSOT 8.8). Blocking the first time (the two digests)."""
        if self._tag is None:
            with open(self._lines_path, "rb") as fh:
                lines = hashlib.sha1(fh.read()).hexdigest()[:12]
            try:
                with open(self._ends_path, "rb") as fh:
                    ends = hashlib.sha1(fh.read()).hexdigest()[:12]
            except OSError:
                ends = "none"
            self._tag = f"{lines}+{ends}"
        return f"ld{DISTILL_V}:{self._tag}:{self._today()}"

    def static_path(self) -> str | None:
        return None

    def distill_geometry(self) -> dict[str, Any] | None:
        raw = self.client.static_zip(fetch=True)
        if raw is None:
            return None
        if self._lines is None:
            self._lines = renfe_ld_lines.ShippedLines.load(self._lines_path)
            self._ends = renfe_ld_lines.load_ends(self._ends_path)
        return distill(raw, self._lines, self._ends or {}, dt.date.fromisoformat(self._today()))


# --------------------------------------------------------------------------
# The feed
# --------------------------------------------------------------------------

class RenfeLdRealtime:
    """Per config entry: each run's last trusted fix (with the time it was first seen there), and the last
    answer of the updates."""

    time_zone = TIME_ZONE

    def __init__(self) -> None:
        self._trusted: dict[str, tuple[float, float, dt.datetime, float]] = {}  # key -> lat, lon, observed, seen
        self._updates: Any = None
        self._updates_t = 0.0
        self._zone = None
        self._origins: dict[str, float | None] = {}
        self.dropped: dict[str, int] = {}

    def _origin(self, date: str) -> float | None:
        """The GTFS service day's origin as an epoch: local noon less 12 hours."""
        if date not in self._origins:
            if len(self._origins) > 32:
                self._origins.clear()
            if self._zone is None:
                self._zone = ZoneInfo(self.time_zone)
            try:
                day = dt.datetime.strptime(date, "%Y%m%d")
                noon = dt.datetime(day.year, day.month, day.day, 12, tzinfo=self._zone)
                self._origins[date] = noon.timestamp() - 43200.0
            except ValueError:
                self._origins[date] = None
        return self._origins[date]

    def _rows(self, trip_id: str, date: str | None, geo: Mapping[str, Any]) -> list:
        table = (geo.get("trip_stops") or {}).get(trip_id)
        origin = self._origin(date) if table and date else None
        if origin is None:
            return []
        return [(seq, stop, None if a is None else origin + a, None if d is None else origin + d)
                for seq, stop, a, d in table]

    def run_date(self, trip_id: str, geo: Mapping[str, Any], now: float) -> str | None:
        """The day this trip is running now: of the days it runs in the window, the one whose scheduled span
        holds now, else the nearest within BEFORE_S / AFTER_S of it; None when none is."""
        table = (geo.get("trip_stops") or {}).get(trip_id)
        dates = (geo.get("trip_dates") or {}).get(trip_id) or ()
        if not table or not dates:
            return None
        times = [t for row in table for t in (row[2], row[3]) if t is not None]
        if not times:
            return None
        best = None
        for d in dates:
            origin = self._origin(d)
            if origin is None:
                continue
            start, end = origin + min(times), origin + max(times)
            if start - BEFORE_S <= now <= end + AFTER_S:
                gap = start - now if now < start else now - end if now > end else 0.0
                if best is None or gap < best[0]:
                    best = (gap, d)
        return best[1] if best else None

    def _where(self, rows: list, delay: int, now: float, geo: Mapping[str, Any]) -> list:
        """[(lat, lon)]: the stop the timetable says the train last left and the one it goes to next."""
        stops = geo.get("stops") or {}
        last, nxt = None, None
        for _, stop, arrival, departure in rows:
            t = departure if departure is not None else arrival
            if t is None:
                continue
            if t + delay <= now:
                last = stop
            elif nxt is None:
                nxt = stop
        return [stops[s] for s in (last, nxt) if s in stops]

    def parse(self, positions: Any, updates: Any, now: float, geometry: Mapping[str, Any] | None = None,
              drop: frozenset[str] = frozenset()) -> Snapshot | None:
        """The two FeedMessages -> Snapshot. None when the positions did not arrive; an EMPTY feed is a quiet
        hour (the client raises on a failure). `updates` may be None: the last answer is used for
        UPDATES_HOLD_S. `drop`: train numbers another entry owns (Handoff)."""
        if positions is None:
            return None
        geo = geometry or {}
        if updates is not None:
            self._updates, self._updates_t = updates, now
        elif self._updates is not None and now - self._updates_t <= UPDATES_HOLD_S:
            updates = self._updates
        snap = Snapshot()

        def skip(reason: str) -> None:
            snap.skipped[reason] = snap.skipped.get(reason, 0) + 1

        by_trip: dict[str, Any] = {}
        by_number: dict[str, list] = {}
        for ent in getattr(updates, "entity", ()) or ():
            if ent.HasField("trip_update"):
                tid = ent.trip_update.trip.trip_id.strip()
                by_trip.setdefault(tid, ent.trip_update)
                n = parse_trip_id(tid)[0]
                if n:
                    by_number.setdefault(n, []).append(ent.trip_update)
        trip_stops = geo.get("trip_stops") or {}
        # number -> [(trip id, leg, date from the id, (lat, lon))], in feed order.
        groups: dict[str, list] = {}
        for ent in positions.entity:
            if not ent.HasField("vehicle"):
                continue
            v = ent.vehicle
            tid = v.trip.trip_id.strip()
            number, leg, date = parse_trip_id(tid)
            if not number:
                skip("no_number")
                continue
            pos = position_of(v)
            if pos is None:
                skip("no_position")
                continue
            groups.setdefault(number, []).append((tid, leg, date, pos))
        names = geo.get("stop_names") or {}
        families = geo.get("trip_families") or {}
        hubs = geo.get("trip_hub") or {}
        kms = geo.get("trip_km") or {}
        spain = dt.datetime.fromtimestamp(now, ZoneInfo(self.time_zone)).strftime("%Y%m%d")
        for number, rows_ in groups.items():
            if number in drop:
                skip("regional")
                continue
            # The train's own trip: the leg with the most timetabled stops, then the lowest digit.
            def rank(r):
                return (-len(trip_stops.get(r[0]) or ()), r[1] if r[1] is not None else 99)
            main = min(rows_, key=rank)
            timed = False
            if main[0] in trip_stops:
                date = self.run_date(main[0], geo, now)
                timed = date is not None
                if not timed:
                    # Running on no day of the window the timetable was cut for (a copy days old): drawn at
                    # its fix, under Spain's date, with no timetable.
                    skip("no_run_date")
                    date = spain
            else:
                # Not in the timetable (SPECIAL_ trips carry their day; any other, Spain's today).
                date = main[2] if main[2] and len(main[2]) == 8 and main[2].isdigit() else spain
            key = identity(number, date)
            update = by_trip.get(main[0]) or next(iter(by_number.get(number) or ()), None)
            stop, delay = update_of(update) if update is not None else (None, None)
            rows = self._rows(main[0], date, geo) if timed else []
            held = self._trusted.get(key)
            points = list(dict.fromkeys(r[3] for r in rows_))
            if len(points) > 1:
                near = None
                if held is not None:
                    d, p = min((metres(held[0], held[1], *p), p) for p in points)
                    if d <= CONTINUITY_M:
                        near = p
                if near is None:
                    where = self._where(rows, delay or 0, now, geo)
                    if where:
                        near = min(points, key=lambda p: min(metres(p[0], p[1], w[0], w[1]) for w in where))
                    else:
                        near = points[0]
                skip("second_position")
                pos = near
                at = [r for r in rows_ if r[3] == pos]
                main = min(at, key=rank)
                if timed and main[0] in trip_stops:
                    rows = self._rows(main[0], date, geo)
            else:
                pos = points[0]
            if held is not None and metres(held[0], held[1], pos[0], pos[1]) <= MOVED_M:
                # Still where it was: the fix keeps the time it was first seen there.
                lat, lon, when = held[0], held[1], held[2]
            else:
                lat, lon = pos
                # Whole seconds, never after now: a datetime rounds to the microsecond, and a fix time a
                # microsecond past now is refused by the estimate (geometry.Projector.estimate; seen on the live
                # read of 2026-11-06, bin\\es324_look2.txt: 152 of 152 trains drawn at their raw fix).
                when = dt.datetime.fromtimestamp(math.floor(now), dt.timezone.utc)
            self._trusted[key] = (lat, lon, when, now)
            trip_id = main[0]
            snap.observations.append(Obs(
                vehicle_id=key, lat=lat, lon=lon, observed_at=when, in_service=True, train=number, line=None,
                # The line's bearing (projection.py); the feed has none.
                reported_course=None, trip_id=key))
            snap.route_keys[key] = trip_id
            fam = families.get(trip_id, "")
            # A fix unchanged for STILL_S is a train standing: no speed. Else the speed of its last two fixes.
            extra: dict[str, Any] = {HELD_SPEED_KEY: 0.0 if now - when.timestamp() > STILL_S else None}
            if fam:
                extra["line_name"] = FAMILY_NAMES.get(fam, fam.title())
                extra["service_family"] = fam
            if trip_id in kms:
                extra["trip_km"] = kms[trip_id]
            snap.extras[key] = extra
            hub = hubs.get(trip_id)
            if len(rows) < 2:
                continue
            start = 1
            for i, row in enumerate(rows):
                if i >= 1 and row[1] == stop:
                    start = i
                    break
            ahead = rows[start:]
            known = {row[0]: delay or 0 for row in ahead}
            nxt = next_by_timetable(ahead, known, set(), now)
            if hub is not None:
                if nxt is None:
                    extra["toward_hub"] = hub == len(rows) - 1
                else:
                    index = next((i for i, row in enumerate(rows) if row[0] == nxt[0]), len(rows) - 1)
                    extra["toward_hub"] = hub >= index
            if nxt is None:
                continue
            _, stop_id, _, eta = nxt
            snap.stop_codes[key] = stop_id
            stop_name = names.get(stop_id)
            if stop_name:
                snap.next_stops[key] = (stop_name, eta)
            if delay is not None:
                # With no delay in the update nothing is said (D0).
                snap.trip_delays[key] = delay
        for k in [k for k, t in self._trusted.items() if now - t[3] > FORGET_S]:
            self._trusted.pop(k, None)
        return snap


# A failed trip-update file keeps the last answer this long (const.SOURCE_GAP_S).
UPDATES_HOLD_S = 600.0
