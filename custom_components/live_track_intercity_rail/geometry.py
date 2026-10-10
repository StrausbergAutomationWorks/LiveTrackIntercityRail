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
import io
import math
import zipfile
from dataclasses import dataclass, field
from typing import Any

R = 6371008.8
GEOMETRY_VERSION = 1

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


def distill(zip_bytes: bytes, simplify_m: float = SIMPLIFY_M) -> dict[str, Any]:
    """A GTFS zip -> the geometry the estimate needs, JSON-ready:
    stops (code -> [lat, lon]), trains (trip_short_name -> [shape_id]),
    shapes (shape_id -> [[lat, lon], ...], simplified), feed_info dates."""
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))

    def rows(name):
        with z.open(name) as f:
            yield from csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))

    stops = {r["stop_id"].strip(): [round(float(r["stop_lat"]), 6), round(float(r["stop_lon"]), 6)]
             for r in rows("stops.txt") if r.get("stop_lat") and r.get("stop_lon")}
    trains: dict[str, set] = {}
    for r in rows("trips.txt"):
        num, sid = (r.get("trip_short_name") or "").strip(), (r.get("shape_id") or "").strip()
        if num and sid:
            trains.setdefault(num, set()).add(sid)
    raw: dict[str, list] = {}
    for r in rows("shapes.txt"):
        raw.setdefault(r["shape_id"].strip(), []).append(
            (int(r["shape_pt_sequence"]), float(r["shape_pt_lat"]), float(r["shape_pt_lon"])))
    shapes = {}
    for sid, pts in raw.items():
        line = [(a, b) for _, a, b in sorted(pts)]
        if len(line) >= 2:
            shapes[sid] = [[round(a, 6), round(b, 6)] for a, b in simplify(line, simplify_m)]
    info = {}
    if "feed_info.txt" in z.namelist():
        for r in rows("feed_info.txt"):
            info = {k: (r.get(k) or "").strip() or None for k in ("feed_version", "feed_start_date", "feed_end_date")}
            break
    return {"v": GEOMETRY_VERSION, **info, "stops": stops,
            "trains": {k: sorted(v & shapes.keys()) for k, v in trains.items() if v & shapes.keys()},
            "shapes": shapes}


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


@dataclass
class Projector:
    """Per railroad. Feed it the distilled geometry once; ask it each poll."""

    geometry: dict[str, Any]
    _routes: dict[str, Route] = field(default_factory=dict)
    _state: dict[str, _State] = field(default_factory=dict)
    _stop_d: dict[tuple, tuple] = field(default_factory=dict)

    def _route(self, sid: str) -> Route | None:
        if sid not in self._routes:
            pts = (self.geometry.get("shapes") or {}).get(sid)
            if not pts or len(pts) < 2:
                return None
            self._routes[sid] = Route([tuple(p) for p in pts])
        return self._routes[sid]

    def forget(self, train_id: str) -> None:
        self._state.pop(train_id, None)

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

    def estimate(self, train_id: str, number: str, fix: tuple[float, float], fix_t: float | None,
                 stop_code: str | None, speed_ms: float | None,
                 now: float) -> tuple[float, float] | None:
        """(lat, lon) on the route at `now`, or None for "publish the fix"."""
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
            elif abs(d_fix - st.d_fix) > MOTION_M:
                # The way the train actually went, from two fixes on its route.
                st.motion = math.copysign(1.0, d_fix - st.d_fix)
            st.fix_key, st.d_fix = key, d_fix
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
        dt = min(now - fix_t, MAX_HORIZON_S)
        speed = max(0.0, speed_ms or 0.0)
        # Which way along the line: the way two fixes showed it going, else
        # the LINE'S OWN ORDER. A GTFS shape is drawn in the direction its
        # trips run, and the line was chosen from this train number's own
        # trips. It read: the side the next stop is on, which pointed a train
        # whose passed stop the source had not yet marked Departed BACKWARDS
        # (27 of 38 backward arrows in bin\ltir_heading_trial2.txt).
        st.direction = st.motion or 1.0
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
        st.last_d, st.last_point = d, p
        return p

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
