"""Renfe's GTFS-Realtime, Rodalies de Catalunya's regional lines (R11-R17) -> one Snapshot.
No Home Assistant imports.

The shared client saw_livetrack.renfe fetches once for every Live Track integration, sends
each vehicle to ONE consumer (06_MAP_CONTRACT.md D1; this one is "intercity") and cleans the
feed once: 0,0 dropped, one row per trip, a return to where the train was two fixes back
held, a network missing from one batch served from the last. Every rule below was MEASURED
on 2026-11-05/06 (bin\\es294_measure.txt, es294_measure2.txt, the cap294 capture) or on
Commuter Rail's capture round 1 (its 20_Research/ES_RENFE_CERCANIAS_FEED_20261016.md), or
DECIDED by Lee 2026-11-05 (Intercity SSOT 8.7, backlog 294).

THE TRIP ID IS DATED. 5109V15772R11 is network 51, service 09V, train 15772, line R11; the
service (5109V) is one calendar date (20261106), so a trip id runs once. IDENTITY
"<trip's number>-<day of its date>" (15772-6), as NSW TrainLink's: the trip id's number,
which is unique per date, not the label's (5109V30531R15 carries vehicle 15031).

LABEL (Lee 2026-11-05): the train number riders see, from vehicle.label ("R15-15031" ->
15031), the trip id's number where the label has none. The line (R15) goes in the hover box.

THE TIMETABLE is Renfe's whole zip (16 MB, every network), which the client already holds
for its bus check (static_zip()): StaticView cuts it to network 51's R11-R17 rail trips of
yesterday, today and tomorrow (about 140 trips a day), strips Renfe's padding (05_SHARED_
LESSONS.md B5) and distills it by trip (geometry.distill, trip_keys). Its version is the
zip's digest and Spain's date, so a new day re-cuts the window even when the zip is the same.

NEXT STOP. A trip update holds ONE stop, with no stop_sequence: the stop the train is going
to (index 1 of the trip at the origin, 8 of 8 measured), its arrival time and delay. The
next stop is the first timetabled stop from that one whose time plus the delay is ahead;
the origin is never next. Without an update the timetable alone says it, and no delay is
said (D0).

INCOMING_AT ROWS ARE NOT WHERE THE TRAIN IS: Commuter Rail measured them p50 1.6 km ahead of
the trip's next row, and tonight every train before its departure stood INCOMING_AT its own
origin, up to 50 minutes early. Such a row repeats the run's last trusted fix, with that
fix's time; a run with none yet gets no marker.

OUTSIDE BARCELONA A POSITION IS A STATION (cap294, 2026-11-06 05:2x-06:1x Spain time): R15
15000 stood on Reus's coordinates from 05:20 to 05:58, its departure 05:36, then appeared on
Tarragona's, Vila-seca never shown; trains at Figueres, Girona and Tortosa did the same. In
Barcelona's core a leaving train's fix moved at every poll (R16 18121, 150-300 m per 30 s). So:
* a fix keeps the time it was FIRST reported there (observed_at), not the batch's;
* from the moment the train leaves the station its fix is on (scheduled departure plus the
  delay), the estimate is TIMED to its next stop, arriving at the timetable plus the delay
  (Operator.timed_without_fix, per train by TIMED_AFTER_KEY; HELD_SPEED_KEY None says there is
  no speed); a fix between stations, after FREE_HORIZON_S unchanged;
* speed, where two fixes allow it, from the last two (Operator.derive_speed), as V/Line.
NO STALLED: a train running between two stations stands on the first in the feed, so the feed
cannot say one is stalled (my call).

DIRECTION, for the look (operators/renfe_regionals.py): toward the hub when the trip's last
stop is in Barcelona, away when its first is; neither (Lleida - La Plana, Reus - Mora),
unknown here, and the operator reads the number's parity.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import re
import zipfile
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from saw_livetrack.gtfs.filter import keep_service_window
from saw_livetrack.gtfs.fleet import metres
from saw_livetrack.gtfs.realtime import Obs, position_of, vehicle_time
from saw_livetrack.gtfs.schedule import next_by_timetable
from saw_livetrack.renfe import (REGIONAL_LINES, REGIONAL_NETWORKS, TIME_ZONE, parse_trip_id)

from .. import geometry
from .base import HELD_SPEED_KEY, TIMED_AFTER_KEY, Snapshot
from .tfnsw import AT_STOP_M, MOVED_M

# How long a run's state outlives its last row.
FORGET_S = 3600.0
# A fix between stations unchanged this long is timed to the next stop (my call: four polls;
# in Barcelona a moving train's fix changed at every poll, 2026-11-06).
FREE_HORIZON_S = 120.0
# A failed trip-update file keeps the last answer this long (const.SOURCE_GAP_S).
UPDATES_HOLD_S = 600.0
# GTFS-RT VehicleStopStatus INCOMING_AT. Unset reads IN_TRANSIT_TO, the proto's default.
INCOMING_AT = 0
RAIL = "2"

# The line, a dash, the number; anything after it is Renfe's ("R16-18121-PLATF.(11)", the
# platform, seen 2026-11-06 at Barcelona Estacio de Franca).
_LABEL_NUMBER = re.compile(r"^\s*[A-Za-z]+\d*-(\d{3,6})(?!\d)")


def number_of(label: Any) -> str | None:
    """'R16-18120' -> '18120', 'R16-18121-PLATF.(11)' -> '18121'; None without one."""
    m = _LABEL_NUMBER.search(label) if isinstance(label, str) else None
    return m.group(1) if m else None


def identity(number: str, date: str | None) -> str:
    """'15772', '20261106' -> '15772-6'; the bare number with no usable date."""
    d = (date or "").strip()
    if len(d) == 8 and d.isdigit():
        return f"{number}-{int(d[6:8])}"
    return number


# --------------------------------------------------------------------------
# The timetable
# --------------------------------------------------------------------------

def _table(z: zipfile.ZipFile, name: str) -> tuple[list[str], list[list[str]]]:
    """(stripped header, stripped rows) of one file; empty when absent."""
    if name not in z.namelist():
        return [], []
    with z.open(name) as fh:
        rd = csv.reader(io.TextIOWrapper(fh, encoding="utf-8-sig", newline=""))
        header = [h.strip() for h in next(rd, [])]
        rows = [[(c or "").strip() for c in r] for r in rd if r]
    return header, rows


def regional_zip(cut: bytes, lines: frozenset[str] = REGIONAL_LINES,
                 networks: frozenset[str] = REGIONAL_NETWORKS) -> bytes:
    """A GTFS zip (already cut to a service window) -> one with only the rail routes of
    `networks` whose short name is in `lines`, their trips, stop times, stops, shapes and
    calendars, every field stripped of Renfe's padding. Blocking."""
    z = zipfile.ZipFile(io.BytesIO(cut))
    out_buf = io.BytesIO()

    def col(header, name):
        return header.index(name) if name in header else None

    rh, routes = _table(z, "routes.txt")
    ir, it, isn = col(rh, "route_id"), col(rh, "route_type"), col(rh, "route_short_name")
    keep_routes = {r[ir] for r in routes if None not in (ir, it, isn) and len(r) > max(ir, it, isn)
                   and r[ir][:2] in networks and r[isn] in lines and r[it] == RAIL}
    th, trips = _table(z, "trips.txt")
    tr, tt, ts, tsh = col(th, "route_id"), col(th, "trip_id"), col(th, "service_id"), col(th, "shape_id")
    trips = [r for r in trips if tr is not None and len(r) > tr and r[tr] in keep_routes]
    keep_trips = {r[tt] for r in trips if tt is not None and len(r) > tt}
    keep_services = {r[ts] for r in trips if ts is not None and len(r) > ts}
    keep_shapes = {r[tsh] for r in trips if tsh is not None and len(r) > tsh}
    sth, stop_times = _table(z, "stop_times.txt")
    st_t, st_s = col(sth, "trip_id"), col(sth, "stop_id")
    stop_times = [r for r in stop_times if st_t is not None and len(r) > st_t and r[st_t] in keep_trips]
    keep_stops = {r[st_s] for r in stop_times if st_s is not None and len(r) > st_s}

    def keep(name, column, allowed):
        header, rows = _table(z, name)
        i = col(header, column)
        return header, [r for r in rows if i is not None and len(r) > i and r[i] in allowed]

    files = {
        "agency.txt": _table(z, "agency.txt"),
        "routes.txt": (rh, [r for r in routes if ir is not None and len(r) > ir and r[ir] in keep_routes]),
        "trips.txt": (th, trips),
        "stop_times.txt": (sth, stop_times),
        "stops.txt": keep("stops.txt", "stop_id", keep_stops),
        "shapes.txt": keep("shapes.txt", "shape_id", keep_shapes),
        "calendar.txt": keep("calendar.txt", "service_id", keep_services),
        "calendar_dates.txt": keep("calendar_dates.txt", "service_id", keep_services),
    }
    with zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as out:
        for name, (header, rows) in files.items():
            if not header:
                continue
            text = io.StringIO()
            w = csv.writer(text, lineterminator="\n")
            w.writerow(header)
            w.writerows(rows)
            out.writestr(name, text.getvalue())
    return out_buf.getvalue()


def trip_dates(zip_bytes: bytes) -> dict[str, str]:
    """{trip_id: YYYYMMDD} for every trip whose service runs on ONE date (Renfe's: 25 of 25
    services measured 2026-11-05, start_date == end_date)."""
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    ch, cal = _table(z, "calendar.txt")
    one = {}
    if {"service_id", "start_date", "end_date"} <= set(ch):
        i, s, e = ch.index("service_id"), ch.index("start_date"), ch.index("end_date")
        one = {r[i]: r[s] for r in cal if len(r) > max(i, s, e) and r[s] and r[s] == r[e]}
    th, trips = _table(z, "trips.txt")
    if not {"trip_id", "service_id"} <= set(th):
        return {}
    it, isv = th.index("trip_id"), th.index("service_id")
    return {r[it]: one[r[isv]] for r in trips if len(r) > max(it, isv) and r[isv] in one}


def line_colours(zip_bytes: bytes) -> dict[str, str]:
    """{route_short_name: '#RRGGBB'} from routes.txt, the first route of each line."""
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    rh, routes = _table(z, "routes.txt")
    if not {"route_short_name", "route_color"} <= set(rh):
        return {}
    isn, ic = rh.index("route_short_name"), rh.index("route_color")
    out: dict[str, str] = {}
    for r in routes:
        if len(r) > max(isn, ic) and r[isn] and re.fullmatch(r"[0-9A-Fa-f]{6}", r[ic]):
            out.setdefault(r[isn], "#" + r[ic].upper())
    return out


def orient(d: dict[str, Any]) -> int:
    """Each trip on a line drawn the way it runs, in place: Renfe's shapes are not (on the
    2026-11-06 copy 239 of 398 trips ran against their own shape's order, both `51_R15` and
    `51_R15_INV` used both ways; bin\\es294_shapes.txt), and the estimate goes along a line in its own order until two
    fixes have shown the way (geometry.Projector). A trip whose first stop lies past its last on
    its shape gets the shape reversed, as `<shape_id>~r`. Returns how many were turned."""
    shapes, stops, turned = d.get("shapes") or {}, d.get("stops") or {}, 0
    routes: dict[str, Any] = {}
    for trip, sids in (d.get("trains") or {}).items():
        rows = (d.get("trip_stops") or {}).get(trip)
        if not rows or not sids or sids[0] not in shapes:
            continue
        a, b = stops.get(rows[0][1]), stops.get(rows[-1][1])
        if not a or not b:
            continue
        sid = sids[0]
        if sid not in routes:
            routes[sid] = geometry.Route([tuple(p) for p in shapes[sid]])
        if routes[sid].project(*a)[0] > routes[sid].project(*b)[0]:
            rid = sid + "~r"
            if rid not in shapes:
                shapes[rid] = shapes[sid][::-1]
            d["trains"][trip] = [rid]
            turned += 1
    return turned


def spain_today() -> str:
    return dt.datetime.now(ZoneInfo(TIME_ZONE)).date().isoformat()


class StaticView:
    """The client's timetable as route_store asks for it: a version, and the distilled
    geometry (route_store calls distill_geometry() when a view has one)."""

    def __init__(self, client: Any, today=spain_today) -> None:
        self.client = client
        self._today = today
        self._raw: Any = None
        self._digest: str | None = None

    def static_version(self) -> str | None:
        """The zip's digest and Spain's date; None before the client has a zip. Blocking
        the first time a zip is seen (a 16 MB digest)."""
        raw = self.client.static_zip()
        if raw is None:
            return None
        if raw is not self._raw:
            self._raw, self._digest = raw, hashlib.sha1(raw).hexdigest()[:16]
        return f"{self._digest}:{self._today()}"

    def static_path(self) -> str | None:
        return None

    def distill_geometry(self) -> dict[str, Any] | None:
        """The window's regional trips, distilled by trip, with each trip's date and each
        line's colour. None before the client has a zip. Blocking (a few seconds)."""
        raw = self.client.static_zip()
        if raw is None:
            return None
        today = dt.date.fromisoformat(self._today())
        cut = regional_zip(keep_service_window(raw, route_types=(RAIL,), today=today,
                                               route_prefixes=tuple(REGIONAL_NETWORKS)))
        d = geometry.distill(cut, trip_keys=True)
        orient(d)
        d["trip_dates"] = {k: v for k, v in trip_dates(cut).items() if k in d["trains"]}
        d["line_colours"] = line_colours(cut)
        return d


# --------------------------------------------------------------------------
# The feed
# --------------------------------------------------------------------------

def read(client: Any, consumer: str, view: StaticView | None = None) -> tuple[Any, Any, str | None]:
    """(positions, trip updates, timetable version) from the shared client. Blocking: run
    in the executor. Raises the client's errors (saw_livetrack.renfe.RenfeError)."""
    positions, updates = client.for_consumer(consumer)
    return positions, updates, view.static_version() if view is not None else None


def update_of(tu: Any) -> tuple[str | None, int | None]:
    """(the update's stop id, its delay in seconds) from one TripUpdate: the stop's arrival
    delay, else its departure delay, else the trip's own."""
    for stu in tu.stop_time_update:
        stop = (stu.stop_id or "").strip() or None
        for event in ("arrival", "departure"):
            if stu.HasField(event) and getattr(stu, event).HasField("delay"):
                return stop, int(getattr(stu, event).delay)
        return stop, int(tu.delay) if tu.HasField("delay") else None
    return None, int(tu.delay) if tu.HasField("delay") else None


def toward(rows: list, names: Mapping[str, str], hub: str) -> bool | None:
    """True when the last stop's name holds `hub`, False when the first's does, else None."""
    if not rows or not hub:
        return None
    h = hub.lower()
    if h in (names.get(rows[-1][1]) or "").lower():
        return True
    if h in (names.get(rows[0][1]) or "").lower():
        return False
    return None


class RenfeRealtime:
    """Per config entry: each run's last trusted fix (with the time it was first reported
    there), and the last answer of the updates."""

    time_zone = TIME_ZONE

    def __init__(self, hub: str = "") -> None:
        self.hub = hub
        self._trusted: dict[str, tuple[float, float, Any, float]] = {}  # key -> lat, lon, observed, seen
        self._updates: Any = None
        self._updates_t = 0.0
        self._zone = None
        self._origins: dict[str, float | None] = {}

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
        if not table or not date:
            return []
        origin = self._origin(date)
        if origin is None:
            return []
        return [(seq, stop, None if a is None else origin + a, None if d is None else origin + d)
                for seq, stop, a, d in table]

    def _horizon(self, lat: float, lon: float, observed: float | None, rows: list, delay: int,
                 geo: Mapping[str, Any]) -> float:
        """Seconds after its fix when this train's estimate turns to the timed rule: at the
        moment it leaves the station its fix is snapped to (scheduled departure plus the
        delay), or FREE_HORIZON_S for a fix between stations."""
        if observed is None:
            return FREE_HORIZON_S
        stops = geo.get("stops") or {}
        best, leave = AT_STOP_M, None
        for _, stop, arrival, departure in rows:
            at = stops.get(stop)
            if not at:
                continue
            m = metres(lat, lon, at[0], at[1])
            if m <= best:
                best, leave = m, departure if departure is not None else arrival
        if leave is None:
            return FREE_HORIZON_S
        return leave + delay - observed

    def parse(self, positions: Any, updates: Any, now: float,
              geometry: Mapping[str, Any] | None = None) -> Snapshot | None:
        """The consumer's two FeedMessages -> Snapshot. None when the positions did not
        arrive; an EMPTY feed is a quiet hour (the client raises on a failure). `updates`
        may be None: the last answer is used for UPDATES_HOLD_S."""
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
        for ent in getattr(updates, "entity", ()) or ():
            if ent.HasField("trip_update"):
                by_trip.setdefault(ent.trip_update.trip.trip_id.strip(), ent.trip_update)
        dates = geo.get("trip_dates") or {}
        names = geo.get("stop_names") or {}
        lines = geo.get("trip_numbers") or {}
        colours = geo.get("line_colours") or {}
        for ent in positions.entity:
            if not ent.HasField("vehicle"):
                continue
            v = ent.vehicle
            trip_id = v.trip.trip_id.strip()
            _, trip_number, line = parse_trip_id(trip_id)
            label = number_of(v.vehicle.label) or trip_number
            if not trip_number or not label:
                skip("no_number")
                continue
            date = dates.get(trip_id)
            key = identity(trip_number, date)
            pos = position_of(v)
            if pos is None:
                skip("no_position")
                continue
            held = self._trusted.get(key)
            if v.current_status == INCOMING_AT:
                if held is None:
                    skip("incoming")
                    continue
                lat, lon, when = held[0], held[1], held[2]
            elif held is not None and metres(held[0], held[1], pos[0], pos[1]) <= MOVED_M:
                # Still where it was: the fix keeps the time it was first reported there.
                lat, lon, when = held[0], held[1], held[2]
            else:
                lat, lon = pos
                when = vehicle_time(v)
            self._trusted[key] = (lat, lon, when, now)
            observed = when.timestamp() if when is not None else None
            rows = self._rows(trip_id, date, geo)
            snap.observations.append(Obs(
                vehicle_id=key, lat=lat, lon=lon, observed_at=when, in_service=True,
                train=label, line=None,
                # The line's bearing (projection.py); the feed has none.
                reported_course=None, trip_id=key))
            snap.route_keys[key] = trip_id
            update = by_trip.get(trip_id)
            stop, delay = update_of(update) if update is not None else (None, None)
            # No speed to give (HELD_SPEED_KEY), which lets the timed rule run.
            extra: dict[str, Any] = {HELD_SPEED_KEY: None,
                                     TIMED_AFTER_KEY: self._horizon(lat, lon, observed, rows, delay or 0, geo)}
            line = lines.get(trip_id) or line
            if line:
                extra["line_name"] = line
                if line in colours:
                    extra["route_color"] = colours[line]
            way = toward(rows, names, self.hub)
            if way is not None:
                extra["toward_hub"] = way
            snap.extras[key] = extra
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
