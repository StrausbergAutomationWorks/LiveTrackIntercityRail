"""Where a train is BETWEEN its source's fixes: along its route, toward its
next stop. No Home Assistant imports, no third-party packages.

Lee, 2026-10-09: "Project the train along the rail line toward its next
stop". MEASURED first, on the 2026-10-09 capture against each train's next
real fix (SSOT section 9; bin\\ltir_proj_trial.py), 1,398 fix pairs:

    holding the last fix (the map until now)   p50 4.83 km  p90 9.77  max 26.3
    timed to Amtrak's arrival estimate          p50 0.96 km  p90 3.78  max 101.9
    at the reported velocity (SHIPPED)          p50 0.40 km  p90 2.45  max 20.2
    the slower of the two                       p50 0.76 km  p90 2.86  max 11.3

The arrival estimate fails in its tail: a stale or near-due estimate for a
stop far away implies impossible speeds (to 3,418 km/h). The slower of the
two shipped first (4a2e469); Lee, 15:47: "Let's use reported speed". The
train moves at the speed it reported, and stops at its next stop. Every
estimate moves the fix ALONG the
route, so a straight line can no longer cross the landscape (D3b condition 3,
the reason straight-line extrapolation was refused).

Every estimate is ON the line. Lee, 2026-10-09 20:38: "Let's snap so train
stays on the tracks." Until then the fix was moved along the line keeping
its own offset from it (p50 3 m, but 655 in the Hudson at 523 m); now the
train is drawn at the nearest point of its line, and the fix it came from is
published beside it (fix_latitude, fix_longitude).

The route is the railroad's own GTFS shape for the train's number; the stop
is the GTFS stop with the source's station code. No route, or a fix more
than MAX_FIX_OFF_M from every route of its number, and no estimate is made:
the fix is published as it is. No next stop, or one off the route, and the
train is put on its line where its fix is, and held there.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import math
import zipfile
from dataclasses import dataclass, field
from typing import Any

R = 6371008.8
GEOMETRY_VERSION = 1
# distill_stream's own version (V/Line). A copy distilled under another is distilled again
# (route_store), without touching any other railroad's copy. 2: trip_services and services,
# for the trip-id fallback (2026-11-05; Intercity SSOT 8.5).
STREAM_VERSION = 2

# A fix farther than this from every route of its train number is not on a
# route we know: no estimate. MEASURED: first fix to its route p50 3 m, p90
# 114 m, max 586 m across 51 trains (bin\ltir_proj_trial.txt).
MAX_FIX_OFF_M = 1000.0
# A next stop this far from the route is not on it (a bus stop, a wrong code).
MAX_STOP_OFF_M = 2000.0
# Never estimate further than this past the fix. The source's fixes come
# every 3-5 minutes (p95 gap 330 s); half an hour without one is an outage,
# and the marker waits where it is.
MAX_HORIZON_S = 1800.0
# Route simplification when distilling. A choice: 15 m keeps the route on the
# track at any zoom the map shows trains at, and shrinks the file. Measured
# effect on the trial: SSOT section 9.
SIMPLIFY_M = 15.0
# Two fixes this far apart along the route say which way the train is going.
# Saw_livetrack's JITTER_M: a parked train's reported position wanders less.
MOVED_M = 50.0
# ...but it takes this far to REVERSE a train against its line's own order.
# MEASURED (bin\ltir_heading_trial2.py, the 2026-10-09 capture): at 50 m,
# station jitter flipped 7 drawn arrows backwards; at 150, 300 and 500 m none.
MOTION_M = 150.0
# The course is the line's bearing over this far either side of the train:
# a 100 m chord, short enough to follow a curve, long enough that the
# simplified line's 15 m vertices do not twitch it.
COURSE_SPAN_M = 50.0
# The longest stretch of line published as a train's track_path. Thirty
# seconds at 300 km/h is 2.5 km; a longer move is a new fix far from the
# last estimate, drawn as the card's straight slide or a jump.
MAX_PATH_M = 10000.0
# Two fixes farther apart than this give no derived speed (fix_speed): a gap
# that long is an outage or a stop, not a run. Brightline's fixes come every
# 60 s (measured, RECORD 5); 300 s is its stale-fix limit.
MAX_FIX_GAP_S = 300.0
# Two fixes that imply more than this give no derived speed: the feed handed
# the trip to another locomotive and the "move" is the gap between the two
# (measured 2026-10-10 on the round-4 test fixture: 5339 read 152 m/s at its
# departure handover and was drawn 15 km ahead). 70 m/s is the replay's jump
# bound (RECORD 5); Brightline's top speed, 125 mph, is 56 m/s, and the
# fastest pair measured on the fixture was 56.1 m/s.
MAX_FIX_SPEED_MS = 70.0
# A line within this of where it was at least FOLD_MIN_M earlier along it has folded back
# (unfold, V/Line). 60 m: parallel tracks; checked every FOLD_STEP_M. A stop this far from what
# is left means the loop was real.
FOLD_TOL_M = 60.0
FOLD_MIN_M = 1000.0
FOLD_STEP_M = 100.0
FOLD_STOP_M = 300.0


def bearing(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Initial great-circle bearing from a to b, degrees true, 0-360."""
    la1, la2 = math.radians(a[0]), math.radians(b[0])
    dl = math.radians(b[1] - a[1])
    y = math.sin(dl) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(dl)
    return math.degrees(math.atan2(y, x)) % 360.0


def _xy(lat, lon, kx):
    return lon * kx, lat * (R * math.pi / 180)


class Route:
    """One polyline, with distance along it."""

    def __init__(self, points: list[tuple[float, float]]) -> None:
        if len(points) < 2:
            raise ValueError("a route needs two points")
        self.lat = [p[0] for p in points]
        self.lon = [p[1] for p in points]
        lat0 = math.radians(sum(self.lat) / len(self.lat))
        self.kx = R * math.cos(lat0) * math.pi / 180
        self.x = [lo * self.kx for lo in self.lon]
        self.y = [la * R * math.pi / 180 for la in self.lat]
        self.cum = [0.0]
        for i in range(1, len(points)):
            self.cum.append(self.cum[-1] + math.hypot(self.x[i] - self.x[i - 1], self.y[i] - self.y[i - 1]))
        self.length = self.cum[-1]

    def project(self, lat: float, lon: float) -> tuple[float, float]:
        """(metres along the route, metres off it) of the nearest point."""
        px, py = lon * self.kx, lat * R * math.pi / 180
        best = (float("inf"), 0.0)
        x, y, cum = self.x, self.y, self.cum
        for i in range(len(x) - 1):
            dx, dy = x[i + 1] - x[i], y[i + 1] - y[i]
            l2 = dx * dx + dy * dy
            t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - x[i]) * dx + (py - y[i]) * dy) / l2))
            qx, qy = x[i] + t * dx, y[i] + t * dy
            d2 = (px - qx) ** 2 + (py - qy) ** 2
            if d2 < best[0]:
                best = (d2, cum[i] + t * math.sqrt(l2))
        return best[1], math.sqrt(best[0])

    def point(self, d: float) -> tuple[float, float]:
        """(lat, lon) at d metres along the route, clamped to its ends."""
        d = min(max(d, 0.0), self.length)
        lo, hi = 0, len(self.cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.cum[mid] <= d:
                lo = mid
            else:
                hi = mid
        seg = self.cum[hi] - self.cum[lo]
        f = 0.0 if seg <= 0 else (d - self.cum[lo]) / seg
        return (round(self.lat[lo] + f * (self.lat[hi] - self.lat[lo]), 6),
                round(self.lon[lo] + f * (self.lon[hi] - self.lon[lo]), 6))


def simplify(points: list[tuple[float, float]], tol_m: float) -> list[tuple[float, float]]:
    """Douglas-Peucker, iterative, in a local metric projection."""
    if len(points) < 3 or tol_m <= 0:
        return list(points)
    lat0 = math.radians(sum(p[0] for p in points) / len(points))
    kx = R * math.cos(lat0) * math.pi / 180
    xy = [_xy(p[0], p[1], kx) for p in points]
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        (ax, ay), (bx, by) = xy[a], xy[b]
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        best, idx = -1.0, -1
        for i in range(a + 1, b):
            px, py = xy[i]
            if l2 == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
                d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
            if d > best:
                best, idx = d, i
        if best > tol_m and idx > 0:
            keep[idx] = True
            stack.append((a, idx))
            stack.append((idx, b))
    return [p for p, k in zip(points, keep) if k]


def dated_key(number: str, departure_date: str) -> str:
    """The key of a train number's line ON a date ('IC 22', '2026-10-14' ->
    'IC 22|2026-10-14'), for a railroad whose line is picked by the GTFS
    calendar (Operator.gtfs_dated)."""
    return f"{number}|{departure_date}"


def first_dated_day(today: dt.date) -> dt.date:
    """The first date a dated copy covers: UTC yesterday. A departure date is
    the railroad's local date (Finland's runs up to three hours ahead of UTC)
    and a night train runs into the next day, so a train in service has a
    departure date of UTC yesterday, today or tomorrow (the shared client
    loads exactly those three)."""
    return today - dt.timedelta(days=1)


def covers(d: dict[str, Any], today: dt.date) -> bool:
    """A dated copy still covers UTC tomorrow's departures."""
    until = d.get("dated_until")
    return isinstance(until, str) and until >= (today + dt.timedelta(days=1)).isoformat()


_WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def service_days(rows, names, dates: list[dt.date]) -> dict[str, set[str]]:
    """service_id -> the ISO dates among `dates` it runs on: calendar.txt's
    weekdays and date range, then calendar_dates.txt (1 adds the date, 2
    removes it). The GTFS rule, as measured for VR on 2026-10-14
    (35_Dependencies/third_party/digitraffic/SSOT.md section 3)."""
    days: dict[str, set[str]] = {}
    if "calendar.txt" in names:
        for r in rows("calendar.txt"):
            sid = (r.get("service_id") or "").strip()
            try:
                start = dt.datetime.strptime((r.get("start_date") or "").strip(), "%Y%m%d").date()
                end = dt.datetime.strptime((r.get("end_date") or "").strip(), "%Y%m%d").date()
            except ValueError:
                continue
            days[sid] = {d.isoformat() for d in dates if start <= d <= end
                         and (r.get(_WEEKDAYS[d.weekday()]) or "").strip() == "1"}
    if "calendar_dates.txt" in names:
        wanted = {d.strftime("%Y%m%d"): d.isoformat() for d in dates}
        for r in rows("calendar_dates.txt"):
            iso = wanted.get((r.get("date") or "").strip())
            if iso is None:
                continue
            sid = (r.get("service_id") or "").strip()
            kind = (r.get("exception_type") or "").strip()
            if kind == "1":
                days.setdefault(sid, set()).add(iso)
            elif kind == "2" and sid in days:
                days[sid].discard(iso)
    return days


def calendars(rows, names) -> dict[str, list]:
    """service_id -> [weekdays as seven 0/1 characters from Monday, start YYYYMMDD, end YYYYMMDD,
    [dates added], [dates removed]], JSON-ready, read by service_runs. A service only in
    calendar_dates.txt has weekdays "0000000" and no range."""
    out: dict[str, list] = {}
    if "calendar.txt" in names:
        for r in rows("calendar.txt"):
            sid = (r.get("service_id") or "").strip()
            if sid:
                out[sid] = ["".join("1" if (r.get(w) or "").strip() == "1" else "0" for w in _WEEKDAYS),
                            (r.get("start_date") or "").strip(), (r.get("end_date") or "").strip(), [], []]
    if "calendar_dates.txt" in names:
        for r in rows("calendar_dates.txt"):
            sid = (r.get("service_id") or "").strip()
            day = (r.get("date") or "").strip()
            kind = (r.get("exception_type") or "").strip()
            if not sid or not day or kind not in ("1", "2"):
                continue
            entry = out.setdefault(sid, ["0000000", "", "", [], []])
            entry[3 if kind == "1" else 4].append(day)
    for entry in out.values():
        entry[3].sort()
        entry[4].sort()
    return out


def service_runs(services: Any, sid: str | None, day: str) -> bool:
    """Whether service `sid` runs on `day` (YYYYMMDD), by the GTFS rule service_days uses:
    calendar_dates.txt first (1 adds the date, 2 removes it), then calendar.txt's range and
    weekday. False for an unknown service or a date that is not one."""
    entry = (services or {}).get(sid) if sid else None
    if not entry:
        return False
    weekdays, start, end, added, removed = entry
    if day in added:
        return True
    if day in removed:
        return False
    try:
        weekday = dt.datetime.strptime(day, "%Y%m%d").weekday()
    except ValueError:
        return False
    return bool(start) and start <= day <= end and weekdays[weekday:weekday + 1] == "1"


def _seconds(text: str | None) -> int | None:
    """'25:10:00' -> 90600; None when empty or not a time."""
    try:
        h, m, s = (text or "").strip().split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)
    except ValueError:
        return None


def distill(zip_bytes: bytes, simplify_m: float = SIMPLIFY_M,
            stop_key: str = "stop_id", dated_from: dt.date | None = None,
            dated_days: int = 4, route_types: tuple[str, ...] = (),
            trip_keys: bool = False) -> dict[str, Any]:
    """A GTFS zip -> the geometry the estimate needs, JSON-ready:
    stops (code -> [lat, lon]), trains (trip_short_name -> [shape_id]),
    shapes (shape_id -> [[lat, lon], ...], simplified), feed_info dates,
    train_routes (trip_short_name -> its route's long name).

    stop_key: the GTFS column the source's station codes are, "stop_id"
    (Amtrak, Brightline) or "stop_code" (VIA, measured 249 of 249).

    dated_from: keys `trains` and `train_routes` by dated_key(number, date)
    for `dated_days` dates from it, each number holding only the trips its
    calendar runs that date (VR), and records the last date as
    `dated_until`; only the shapes those trips use are kept. route_types:
    only routes of these GTFS route_types (strings); empty, every route.

    trip_keys: keys `trains` and `train_routes` by trip_id, a trip's own shape being
    its line, with no choosing among a number's lines (NSW TrainLink: no fix over
    1 km from its own trip's line, 35,028 measured). It adds `trip_stops` (trip_id ->
    [[sequence, stop_id, arrival s, departure s], ...], seconds from the GTFS service
    day, with no row where pickup_type and drop_off_type are both 1: no rider stops
    there, as at NSW's border stops) and `trip_numbers` (trip_id -> route_short_name),
    and `stop_names` become the parent station's where there is one."""
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))

    def rows(name):
        with z.open(name) as f:
            yield from csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))

    stops = {(r.get(stop_key) or "").strip(): [round(float(r["stop_lat"]), 6), round(float(r["stop_lon"]), 6)]
             for r in rows("stops.txt")
             if r.get("stop_lat") and r.get("stop_lon") and (r.get(stop_key) or "").strip()}
    # Station names for the hover box, by stop_id (2026-10-10, Brightline:
    # its realtime feed names stops by id only). Added without bumping
    # GEOMETRY_VERSION: an older cached copy simply has none until its next
    # weekly refresh, and only a source that needs names reads them.
    stop_names = {(r.get(stop_key) or "").strip(): (r.get("stop_name") or "").strip()
                  for r in rows("stops.txt")
                  if (r.get("stop_name") or "").strip() and (r.get(stop_key) or "").strip()}
    if trip_keys:
        parent = {(r.get(stop_key) or "").strip(): (r.get("parent_station") or "").strip()
                  for r in rows("stops.txt")}
        stop_names = {s: stop_names.get(parent.get(s) or "") or n for s, n in stop_names.items()}
    # A train number's route, for its line name and its look (VIA: the
    # route decides the band and the corridor's lateness; 2026-10-14). Added
    # without bumping GEOMETRY_VERSION, as stop_names was.
    route_names = {}
    if "routes.txt" in z.namelist():
        route_names = {(r.get("route_id") or "").strip():
                       (r.get("route_long_name") or r.get("route_short_name") or "").strip()
                       for r in rows("routes.txt")}
    trains: dict[str, set] = {}
    train_routes: dict[str, str] = {}
    trip_numbers: dict[str, str] = {}
    route_short = {}
    if trip_keys and "routes.txt" in z.namelist():
        route_short = {(r.get("route_id") or "").strip(): (r.get("route_short_name") or "").strip()
                       for r in rows("routes.txt")}
    route_type = {}
    if route_types and "routes.txt" in z.namelist():
        route_type = {(r.get("route_id") or "").strip(): (r.get("route_type") or "").strip()
                      for r in rows("routes.txt")}
    dated_until = None
    days: dict[str, set[str]] = {}
    if dated_from is not None:
        dates = [dated_from + dt.timedelta(days=i) for i in range(max(1, dated_days))]
        dated_until = dates[-1].isoformat()
        days = service_days(rows, z.namelist(), dates)
    for r in rows("trips.txt"):
        if route_types and route_type.get((r.get("route_id") or "").strip()) not in route_types:
            continue
        if dated_from is not None:
            num, sid = (r.get("trip_short_name") or "").strip(), (r.get("shape_id") or "").strip()
            route = route_names.get((r.get("route_id") or "").strip())
            for iso in days.get((r.get("service_id") or "").strip(), ()):
                if num and sid:
                    trains.setdefault(dated_key(num, iso), set()).add(sid)
                if num and route:
                    train_routes.setdefault(dated_key(num, iso), route)
            continue
        if trip_keys:
            num = (r.get("trip_id") or "").strip()
            short = route_short.get((r.get("route_id") or "").strip())
            if num and short:
                trip_numbers[num] = short
        else:
            num = (r.get("trip_short_name") or "").strip()
        sid = (r.get("shape_id") or "").strip()
        if num and sid:
            trains.setdefault(num, set()).add(sid)
        route = route_names.get((r.get("route_id") or "").strip())
        if num and route:
            train_routes.setdefault(num, route)
    raw: dict[str, list] = {}
    for r in rows("shapes.txt"):
        raw.setdefault(r["shape_id"].strip(), []).append(
            (int(r["shape_pt_sequence"]), float(r["shape_pt_lat"]), float(r["shape_pt_lon"])))
    shapes = {}
    for sid, pts in raw.items():
        line = [(a, b) for _, a, b in sorted(pts)]
        if len(line) >= 2:
            shapes[sid] = [[round(a, 6), round(b, 6)] for a, b in simplify(line, simplify_m)]
    if dated_from is not None:
        # Only the lines the dated trips use: the rest is another period's.
        used = set().union(*trains.values()) if trains else set()
        shapes = {k: v for k, v in shapes.items() if k in used}
    info = {}
    if "feed_info.txt" in z.namelist():
        for r in rows("feed_info.txt"):
            info = {k: (r.get(k) or "").strip() or None for k in ("feed_version", "feed_start_date", "feed_end_date")}
            break
    out = {"v": GEOMETRY_VERSION, **info, "stops": stops, "stop_names": stop_names,
           "trains": {k: sorted(v & shapes.keys()) for k, v in trains.items() if v & shapes.keys()},
           "train_routes": train_routes, "shapes": shapes}
    if dated_until is not None:
        out["dated_until"] = dated_until
    if trip_keys:
        trip_rows: dict[str, list] = {}
        for r in rows("stop_times.txt"):
            trip = (r.get("trip_id") or "").strip()
            if trip not in out["trains"]:
                continue
            if (r.get("pickup_type") or "").strip() == "1" and (r.get("drop_off_type") or "").strip() == "1":
                continue
            trip_rows.setdefault(trip, []).append(
                [int(r["stop_sequence"]), (r.get("stop_id") or "").strip(),
                 _seconds(r.get("arrival_time")), _seconds(r.get("departure_time"))])
        out["trip_stops"] = {k: sorted(v, key=lambda x: x[0]) for k, v in trip_rows.items()}
        out["trip_numbers"] = {k: v for k, v in trip_numbers.items() if k in out["trains"]}
    return out


def _fold(points: list[tuple[float, float]]) -> tuple[list[tuple[float, float]], float] | None:
    """The first place a line comes back to where it has been: (the line without that loop, km
    cut), or None. Sampled every FOLD_STEP_M. The earliest point any later part of the line comes
    back to, then the LAST time it does: a Z-fold has passes over the same track three times, and
    the middle one and the first are what go."""
    lat0 = math.radians(sum(p[0] for p in points) / len(points))
    kx = R * math.cos(lat0) * math.pi / 180
    ky = R * math.pi / 180
    xy = [(p[1] * kx, p[0] * ky) for p in points]
    cum = [0.0]
    for a, b in zip(xy, xy[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    samples: list[tuple[float, float, float]] = []
    k = 0
    d = 0.0
    while d < cum[-1]:
        while k + 2 < len(cum) and cum[k + 1] < d:
            k += 1
        seg = cum[k + 1] - cum[k]
        f = 0.0 if seg <= 0 else (d - cum[k]) / seg
        samples.append((xy[k][0] + (xy[k + 1][0] - xy[k][0]) * f, xy[k][1] + (xy[k + 1][1] - xy[k][1]) * f, d))
        d += FOLD_STEP_M
    grid: dict[tuple[int, int], list[tuple[float, float, float]]] = {}
    first = None
    for x, y, d in samples:
        cx, cy = int(x // FOLD_TOL_M), int(y // FOLD_TOL_M)
        for gx in (cx - 1, cx, cx + 1):
            for gy in (cy - 1, cy, cy + 1):
                for x2, y2, d2 in grid.get((gx, gy), ()):
                    if d - d2 > FOLD_MIN_M and math.hypot(x - x2, y - y2) < FOLD_TOL_M and (first is None or d2 < first[2]):
                        first = (x2, y2, d2)
        grid.setdefault((cx, cy), []).append((x, y, d))
    if first is None:
        return None
    last = max(d for x, y, d in samples
               if d - first[2] > FOLD_MIN_M and math.hypot(x - first[0], y - first[1]) < FOLD_TOL_M)
    kept = [p for p, c in zip(points, cum) if c < first[2]]
    i = next(n for n, c in enumerate(cum) if c >= last)
    return kept + list(points[i:]), (cum[i] - first[2]) / 1000.0


def unfold(points: list[tuple[float, float]], stops: Any = ()) -> tuple[list[tuple[float, float]], float]:
    """(the line with its folds taken out, km cut). A loop that has a stop nowhere else on the line
    is a real out-and-back and stays, with anything after it.

    MEASURED 2026-11-02 (bin\\ltir_vl_folds.txt, ltir_vl_fold_aby.png): every Albury line runs from
    km 141 to 154, back to 167 and on to 180 over the same track, 26 km that no train travels. On
    that stretch the nearest point of the line jumps between passes (684 moves of over 5 km in one
    poll on the replay) and a train timed along the line would be drawn running back and forth."""
    total = 0.0
    line = list(points)
    while True:
        cut = _fold(line) if len(line) >= 2 else None
        if cut is None:
            return line, total
        new, km = cut
        if len(new) < 2 or len(new) >= len(line):
            return line, total
        before, after = Route(line), Route(new)
        if any(after.project(*s)[1] > FOLD_STOP_M >= before.project(*s)[1] for s in stops):
            return line, total
        line, total = new, total + km


def _digest(value: Any) -> str:
    return hashlib.sha1(json.dumps(value, separators=(",", ":")).encode()).hexdigest()[:12]


def distill_stream(path: str, simplify_m: float = SIMPLIFY_M) -> dict[str, Any]:
    """A GTFS zip ON DISK -> the geometry the estimate needs, for a whole publication, one shape
    and one trip at a time (V/Line; Intercity SSOT 8.5).

    distill() holds every shape before simplifying: 458 MB of heap on V/Line's 2,868,931 points.
    Here each shape is simplified and dropped as it ends, and identical lines and stop tables are
    kept once. MEASURED on the 2 November 2026 publication (bin\\ltir_vl0_stream3.txt): 6,988 trips,
    1,416 shapes, 60 distinct lines, 696 distinct stop tables; 946 KB of JSON, 5.4 MB loaded. A
    four-day window of the same copy was 711 KB, so a dated cut would save 235 KB and cost a daily
    distill (Lee 2026-11-02 03:14: whole publication).

    `shapes` and `stop_tables` are keyed by a hash of their contents, so a line keeps its id across
    publications (`stable_lines`; Projector.adopt). `trains` and `trip_tables` are keyed by trip_id.
    Stop names are as published (D5); `route_names` is by route_id, which the feed carries.

    A shape's folds are taken out (unfold), the trips' own stops deciding what is a fold.

    A shape that comes back after another has started raises ValueError: shapes.txt is contiguous
    in both publications measured, and a shape met twice would silently lose a part."""
    with zipfile.ZipFile(path) as z:
        def rows(name):
            with z.open(name) as f:
                yield from csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))

        tables: dict[str, list] = {}
        trip_tables: dict[str, str] = {}
        used_stops: set[str] = set()
        current: str | None = None
        buffer: list = []

        def close_trip() -> None:
            if current is None or not buffer:
                return
            table = sorted(buffer, key=lambda x: x[0])
            digest = _digest(table)
            tables.setdefault(digest, table)
            trip_tables[current] = digest

        for r in rows("stop_times.txt"):
            trip = (r.get("trip_id") or "").strip()
            if trip != current:
                close_trip()
                current = trip
                # A trip met again goes on from what it had, so nothing is lost.
                buffer = list(tables[trip_tables[trip]]) if trip in trip_tables else []
            if (r.get("pickup_type") or "").strip() == "1" and (r.get("drop_off_type") or "").strip() == "1":
                continue
            stop = (r.get("stop_id") or "").strip()
            used_stops.add(stop)
            buffer.append([int(r["stop_sequence"]), stop, _seconds(r.get("arrival_time")),
                           _seconds(r.get("departure_time"))])
        close_trip()

        trip_shape: dict[str, str] = {}
        trip_services: dict[str, str] = {}
        for r in rows("trips.txt"):
            trip = (r.get("trip_id") or "").strip()
            trip_shape[trip] = (r.get("shape_id") or "").strip()
            sid = (r.get("service_id") or "").strip()
            if trip and sid:
                trip_services[trip] = sid
        services = calendars(rows, z.namelist())
        wanted = {s for s in trip_shape.values() if s}

        stops: dict[str, list] = {}
        stop_names: dict[str, str] = {}
        for r in rows("stops.txt"):
            stop = (r.get("stop_id") or "").strip()
            if stop not in used_stops:
                continue
            if r.get("stop_lat") and r.get("stop_lon"):
                stops[stop] = [round(float(r["stop_lat"]), 6), round(float(r["stop_lon"]), 6)]
            name = (r.get("stop_name") or "").strip()
            if name:
                stop_names[stop] = name
        shape_stops: dict[str, set] = {}
        for trip, digest in trip_tables.items():
            sid = trip_shape.get(trip)
            if sid:
                shape_stops.setdefault(sid, set()).update(x[1] for x in tables[digest])

        lines: dict[str, list] = {}
        line_of: dict[str, str] = {}
        finished: set[str] = set()
        shape: str | None = None
        points: list = []
        # 1,416 shapes are 60 lines before anything is done to them.
        memo: dict[tuple, tuple[str, float]] = {}
        cut_km: dict[str, float] = {}

        def close_shape() -> None:
            if len(points) < 2:
                return
            raw = [(a, b) for _, a, b in sorted(points)]
            own = frozenset(shape_stops.get(shape, ()))
            key = (_digest(raw), own)
            if key not in memo:
                flat, km = unfold(raw, [stops[s] for s in sorted(own) if s in stops])
                line = [[round(a, 6), round(b, 6)] for a, b in simplify(flat, simplify_m)]
                digest = _digest(line)
                lines.setdefault(digest, line)
                memo[key] = (digest, km)
                if km:
                    cut_km[digest] = round(km, 1)
            line_of[shape] = memo[key][0]

        for r in rows("shapes.txt"):
            sid = (r.get("shape_id") or "").strip()
            if sid != shape:
                close_shape()
                if sid in finished:
                    raise ValueError(f"shapes.txt is not contiguous at shape {sid}")
                finished.add(sid)
                shape, points = sid, []
            if sid in wanted:
                points.append((int(r["shape_pt_sequence"]), float(r["shape_pt_lat"]), float(r["shape_pt_lon"])))
        close_shape()
        route_names = {(r.get("route_id") or "").strip():
                       " ".join((r.get("route_long_name") or r.get("route_short_name") or "").split())
                       for r in rows("routes.txt")}
    return {"v": GEOMETRY_VERSION, "stream_v": STREAM_VERSION, "stable_lines": True, "stops": stops,
            "stop_names": stop_names, "route_names": route_names,
            "trains": {t: [line_of[s]] for t, s in trip_shape.items() if s in line_of},
            "shapes": lines, "stop_tables": tables, "trip_tables": trip_tables, "folds_cut_km": cut_km,
            "trip_services": trip_services, "services": services}


@dataclass
class _State:
    shape_id: str
    fix_key: tuple = ()
    d_fix: float = 0.0
    last_d: float | None = None     # along-route position last published
    direction: float = 0.0          # +1 / -1 along the route, once known
    motion: float = 0.0             # +1 / -1: the way the FIXES moved along it
    last_point: tuple | None = None  # the position last published
    prev_d: float | None = None     # the one before it, for track_path
    prev_point: tuple | None = None
    fix_t: float | None = None      # the current fix's time
    prev_fix: tuple | None = None   # (d, time) of the fix before it, for a derived speed
    last_t: float | None = None     # when last_d was published


def line_from_legs(geo: dict[str, Any], sid: str, decoded: dict[str, list]) -> list[list[float]] | None:
    """A line stored as LEGS of shared lines: geometry["shape_legs"][sid] is [[from stop, to stop, line key or
    None], ...], each key's points in geometry["pair_lines"] as 1e-5 degree integers (the first absolute, the
    rest differences) from the lower stop id to the higher; None is the straight line between the two stops.
    Renfe (Spain) assembles its trips' lines from lines shipped per stop pair (sources/renfe_ld_lines.py):
    stored whole, 2026-11-06's window was 8,371,586 bytes of JSON and 382,534 points, every pattern repeating
    its legs (bin\\es324_replay.txt). `decoded` caches each key's points. None: no such line."""
    legs = (geo.get("shape_legs") or {}).get(sid)
    if not legs:
        return None
    stops, lines = geo.get("stops") or {}, geo.get("pair_lines") or {}
    pts: list[list[float]] = []
    for a, b, key in legs:
        if key is None or key not in lines:
            if a not in stops or b not in stops:
                continue
            seg = [list(stops[a]), list(stops[b])]
        else:
            if key not in decoded:
                flat, out, la, lo = lines[key], [], 0, 0
                for i in range(0, len(flat) - 1, 2):
                    la += flat[i]
                    lo += flat[i + 1]
                    out.append([la / 1e5, lo / 1e5])
                decoded[key] = out
            seg = decoded[key][::-1] if a > b else list(decoded[key])
        if pts and seg and pts[-1] == seg[0]:
            seg = seg[1:]
        pts.extend(seg)
    return pts if len(pts) >= 2 else None


@dataclass
class Projector:
    """Per railroad. Feed it the distilled geometry once; ask it each poll."""

    geometry: dict[str, Any]
    _routes: dict[str, Route] = field(default_factory=dict)
    _state: dict[str, _State] = field(default_factory=dict)
    _stop_d: dict[tuple, tuple] = field(default_factory=dict)
    _decoded: dict[str, list] = field(default_factory=dict)

    def _route(self, sid: str) -> Route | None:
        if sid not in self._routes:
            pts = (self.geometry.get("shapes") or {}).get(sid)
            if not pts and self.geometry.get("shape_legs"):
                pts = line_from_legs(self.geometry, sid, self._decoded)
            if not pts or len(pts) < 2:
                return None
            self._routes[sid] = Route([tuple(p) for p in pts])
        return self._routes[sid]

    def forget(self, train_id: str) -> None:
        self._state.pop(train_id, None)

    def adopt(self, old: "Projector") -> None:
        """Running trains go on from the copy before, when both copies name their lines by a
        hash of their points, so a line id means the same line (distill_stream). A train whose
        line has gone starts again from its next fix. V/Line's trip ids change between
        publications (3,031 of 6,988 shared over 17 days), so a train running across a new copy
        may no longer have a trip there: its state is what keeps it on its line."""
        if not (self.geometry.get("stable_lines") and old.geometry.get("stable_lines")):
            return
        shapes = self.geometry.get("shapes") or {}
        self._state = {k: s for k, s in old._state.items() if s.shape_id in shapes}

    def course(self, train_id: str) -> float | None:
        """The train's course where estimate() last placed it: its route
        line's bearing there, the way it is going, degrees true to 0.1. None
        until its direction is known, or at the very end of a line.

        Lee 2026-10-09 16:05: "Amtrak headings are very bad". MEASURED live
        16:10 (bin\\ltir_live_heading.txt): Fleet's course, from the chord
        between two fixes 3-5 minutes apart, was p50 20 deg off the line the
        estimate moves along, p90 60, 5 of 101 trains over 90."""
        st = self._state.get(train_id)
        if st is None or not st.direction or st.last_d is None:
            return None
        route = self._route(st.shape_id)
        # Kept a span inside the line's ends: a train run past its terminus
        # (replay: 794-8 at the end of its line) faces the line's last 100 m.
        d = min(max(st.last_d, COURSE_SPAN_M), max(route.length - COURSE_SPAN_M, COURSE_SPAN_M))
        a = route.point(d - st.direction * COURSE_SPAN_M)
        b = route.point(d + st.direction * COURSE_SPAN_M)
        if a == b:
            return None
        return round(bearing(a, b), 1)

    def _choose(self, number: str, lat: float, lon: float):
        best = None
        for sid in (self.geometry.get("trains") or {}).get(number, ()):
            route = self._route(sid)
            if route is None:
                continue
            d, off = route.project(lat, lon)
            if best is None or off < best[2]:
                best = (sid, d, off)
        return best

    def fix_speed(self, train_id: str) -> float | None:
        """m/s along the line between the train's last two fixes, or None
        (no earlier fix, the two more than MAX_FIX_GAP_S apart, or a speed
        over MAX_FIX_SPEED_MS, which is a handover, not a run).

        Lee 2026-10-10 (Brightline, whose feed sets no speed): "Use the Amtrak
        positioning for Brightline too". MEASURED on Brightline's rounds 3 and
        4 (bin\\ltir_bl_replay2.py, 6,136 fix pairs 60 s apart): moved along
        the line at this speed, a train lands p50 0.2 km, p90 0.7 km from its
        next fix; held, p50 2.1 km, p90 2.9 km."""
        st = self._state.get(train_id)
        if st is None or st.prev_fix is None or st.fix_t is None:
            return None
        d0, t0 = st.prev_fix
        gap = st.fix_t - t0
        if gap <= 0 or gap > MAX_FIX_GAP_S:
            return None
        moved = abs(st.d_fix - d0)
        # A standing train's reported position wanders (MOVED_M): not a speed.
        if moved < MOVED_M:
            return 0.0
        speed = moved / gap
        return speed if speed <= MAX_FIX_SPEED_MS else None

    def estimate(self, train_id: str, number: str, fix: tuple[float, float], fix_t: float | None,
                 stop_code: str | None, speed_ms: float | None,
                 now: float, derive_speed: bool = False,
                 eta: float | None = None, timed: bool = False,
                 horizon: float = MAX_HORIZON_S) -> tuple[float, float] | None:
        """(lat, lon) on the route at `now`, or None for "publish the fix".
        With derive_speed and no speed_ms, the speed of the last two fixes.

        timed: once the fix is older than MAX_HORIZON_S (the source has no
        newer one; VIA holds its last fix, then drops it), the train moves
        from where it was last drawn toward its next stop, arriving there at
        `eta`, the source's estimate (Lee 2026-10-11 15:28: "keep the train
        moving using the speed and/or estimate to the next station so it
        arrives at the estimated time"). MEASURED on VIA's capture, 30
        positionless stretches over 10 min replayed against the next real fix
        (bin\\ltir_via_final.txt): held p50 23.3 km, p90 118.3; timed p50
        10.7 km, p90 42.2.

        horizon: when the last speed gives way to the timed rule, per railroad
        (Operator.timed_after_s; V/Line 600 s, Lee 2026-11-01, decision 2)."""
        if fix_t is None or now < fix_t:
            return None
        stop = (self.geometry.get("stops") or {}).get(stop_code) if stop_code else None
        st = self._state.get(train_id)
        key = (fix[0], fix[1], fix_t)
        if st is None or st.fix_key != key:
            route = self._route(st.shape_id) if st else None
            d_fix, off = route.project(*fix) if route else (0.0, float("inf"))
            if off > MAX_FIX_OFF_M:          # first sight, or it left its route: choose again
                best = self._choose(number, *fix)
                if best is None or best[2] > MAX_FIX_OFF_M:
                    self._state.pop(train_id, None)
                    return None
                st = _State(shape_id=best[0])
                d_fix = best[1]
            else:
                if abs(d_fix - st.d_fix) > MOTION_M:
                    # The way the train actually went, from two fixes on its route.
                    st.motion = math.copysign(1.0, d_fix - st.d_fix)
                if st.fix_t is not None:
                    st.prev_fix = (st.d_fix, st.fix_t)
            st.fix_key, st.d_fix, st.fix_t = key, d_fix, fix_t
            self._state[train_id] = st
        route = self._route(st.shape_id)
        d_stop = None
        if stop is not None:
            skey = (st.shape_id, stop_code)
            if skey not in self._stop_d:
                self._stop_d[skey] = route.project(*stop)
            d_stop, stop_off = self._stop_d[skey]
            if stop_off > MAX_STOP_OFF_M:
                d_stop = None
        dt = min(now - fix_t, horizon)
        if speed_ms is None and derive_speed:
            # A source with no speed (Brightline): the speed of its last two
            # fixes along the line (fix_speed).
            speed_ms = self.fix_speed(train_id)
        speed = max(0.0, speed_ms or 0.0)
        # Which way along the line: the way two fixes showed it going, else
        # the LINE'S OWN ORDER. A GTFS shape is drawn in the direction its
        # trips run, and the line was chosen from this train number's own
        # trips. It read: the side the next stop is on, which pointed a train
        # whose passed stop the source had not yet marked Departed BACKWARDS
        # (27 of 38 backward arrows in bin\ltir_heading_trial2.txt).
        st.direction = st.motion or 1.0
        if timed and now - fix_t > horizon:
            d = self._timed(st, d_stop, eta, fix_t, now)
        else:
            if d_stop is None:
                # No stop to aim at: on the line where the fix is, held there.
                step = 0.0
            elif d_stop != st.d_fix and math.copysign(1.0, d_stop - st.d_fix) != st.direction:
                # The "next" stop is BEHIND the way the train is going: it has
                # passed it and the source has not marked it Departed yet
                # (measured: 22 of 22 backward moves in the first replay came from
                # this or from a stop overrun; bin\ltir_proj_back.txt). Move on at
                # the reported speed, no stop to stop at.
                step = speed * dt
            else:
                # At the reported speed, and never past the next stop.
                step = min(abs(d_stop - st.d_fix), speed * dt)
            d = st.d_fix + st.direction * step
        # Never backwards along the direction of travel: a fix that arrives
        # behind the last estimate holds the marker until the train passes it.
        if st.last_d is not None and st.direction and (d - st.last_d) * st.direction < 0 \
                and abs(d - st.last_d) < 5000:
            d = st.last_d
        # ON the line, even at the moment of a fix (Lee 2026-10-09 20:38,
        # "snap so train stays on the tracks"; 06_MAP_CONTRACT.md D3d).
        p = route.point(d)
        st.prev_d, st.prev_point = st.last_d, st.last_point
        st.last_d, st.last_point, st.last_t = d, p, now
        return p

    def _timed(self, st: _State, d_stop: float | None, eta: float | None,
               fix_t: float, now: float) -> float:
        """Where a train with no usable fix is along its line at `now`: from
        where it was last drawn (or its fix, the first time), toward its next
        stop, arriving at `eta`. A stop not ahead, or no estimate: it waits
        where it is. A stop whose estimate has passed: at the stop."""
        if st.last_d is not None and st.last_t is not None and st.last_t >= fix_t:
            a_d, a_t = st.last_d, st.last_t
        else:
            a_d, a_t = st.d_fix, fix_t
        if d_stop is None or (d_stop - a_d) * st.direction <= 0 or eta is None:
            return a_d
        if eta <= a_t:
            return d_stop
        # At the stop once its estimate has passed (the clamp).
        return a_d + (d_stop - a_d) * min(1.0, (now - a_t) / (eta - a_t))

    def path(self, train_id: str) -> list[list[float]] | None:
        """The train's line from where estimate() placed it the time before
        to where it placed it last: [[lat, lon], ...], first and last exactly
        those two positions, between them the line's own vertices (all of it
        on the line since 2026-10-09 20:38). None when it did not move forward along its
        line, moved more than MAX_PATH_M, or has no earlier position.

        Lee 2026-10-09 17:44: "Trains are off the track by a long way".
        MEASURED 17:45 (bin\\ltir_live_offline.txt): the PUBLISHED positions
        are on the line (p50 3 m, p90 13 m); the card slid each marker in a
        straight line between them for up to 30 s, and 2 km of Acela across a
        curve strays hundreds of metres. This is the route hint of
        06_MAP_CONTRACT.md D3c-v, for the card to slide along."""
        st = self._state.get(train_id)
        if st is None or st.prev_point is None or st.prev_d is None or st.last_d is None \
                or st.last_point is None or not st.direction:
            return None
        moved = (st.last_d - st.prev_d) * st.direction
        if moved <= 0 or moved > MAX_PATH_M:
            return None
        route = self._route(st.shape_id)
        if route is None:
            return None
        lo, hi = sorted((st.prev_d, st.last_d))
        inner = [i for i in range(len(route.cum)) if lo < route.cum[i] < hi]
        if st.direction < 0:
            inner.reverse()
        pts = [list(st.prev_point)]
        pts += [[route.lat[i], route.lon[i]] for i in inner]
        pts.append(list(st.last_point))
        return pts
