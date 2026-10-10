"""Brightline's own GTFS-Realtime: vehicle positions and trip updates -> one
Snapshot. No Home Assistant imports.

Fetching is the coordinator's; this module reads two decoded FeedMessages, so
every rule here is tested offline against recorded polls (tests/fixtures).
Everything below is MEASURED on two captures of this feed, round 3 (Saturday
2026-10-03) and round 4 (Friday 2026-10-09); `RECORD.md` 5.

IDENTITY IS THE TRIP (Lee 2026-10-10 14:14: "The trip is the identity"):
"<trip number>-<day of month of its service date>", Amtraker's shape for
Amtrak, so the two railroads read alike. NOT `vehicle.id`: it is a
locomotive, two per trainset, the reporting one can change mid-run, and in
round 4 one id sat on two trips at two live positions 45 km apart for an
hour. The entity id is the trip id on every fix, and no trip ever carried two
vehicles. The marker label is the trip number (Lee 2026-10-03).

What the feed sets on a position: trip, start date, lat/lon, bearing,
timestamp. Never set: label, status, stop, sequence, SPEED. So no speed is
published (D2); the along-route estimate derives one from two fixes
(geometry.Projector.fix_speed).

A trip with no vehicle in the feed gets no marker (Lee 2026-10-03, 209 = A).
"""

from __future__ import annotations

from typing import Any

from saw_livetrack.gtfs.realtime import Obs, position_of, vehicle_time

from .base import Snapshot

# A fix older than this is not used (Lee 2026-10-10, rule 2). MEASURED: the
# feed refreshes every 60 s and a fix arrives p50 58 s, p90 71 s old; over 300 s
# happened only on fixes frozen on parked equipment (5342 for 91 minutes, 5740,
# 5741, 5318). Replayed, dropping them removed the jumps they caused.
MAX_AGE_S = 300.0
# A trip whose fix went stale keeps its last usable fix this long, then has
# no marker until a usable fix comes (Fleet's REFUSED_HOLD_S, the same idea).
HOLD_S = 600.0
# The line every Brightline train runs on. The GTFS route is "Mainline"; the
# hover box says what a rider calls it.
LINE_NAME = "Brightline"


def _number(trip_id: str) -> str | None:
    """'5740_BL_63_1' -> '5740'."""
    head = trip_id.split("_", 1)[0].strip()
    return head if head.isdigit() else None


def identity(trip_id: str, start_date: str | None) -> str | None:
    """'<number>-<day>' ('5740-3' on 2026-10-03), or the bare number when the
    feed gives no usable start date. None for a trip id with no number."""
    number = _number(trip_id)
    if number is None:
        return None
    sd = (start_date or "").strip()
    if len(sd) == 8 and sd.isdigit():
        return f"{number}-{int(sd[6:8])}"
    return number


def _has(m: Any, name: str) -> bool:
    try:
        return m.HasField(name)
    except ValueError:
        return False


def _stop_rows(tu: Any) -> list[tuple[str, float | None, float | None, int | None]]:
    """(stop_id, arrival, departure, delay s) per stop of one TripUpdate, in
    the feed's order. The feed keeps a trip's PASSED stops (measured: the first
    stop never changed in 52 trips), so order, not presence, says what is next."""
    out = []
    for s in tu.stop_time_update:
        arr = float(s.arrival.time) if _has(s, "arrival") and s.arrival.time else None
        dep = float(s.departure.time) if _has(s, "departure") and s.departure.time else None
        delay = None
        if _has(s, "arrival") and _has(s.arrival, "delay"):
            delay = int(s.arrival.delay)
        elif _has(s, "departure") and _has(s.departure, "delay"):
            delay = int(s.departure.delay)
        out.append((s.stop_id, arr, dep, delay))
    return out


def next_stop_row(rows: list, now: float):
    """The trip's next stop: the first after its origin that it has not left
    yet (its departure, else its arrival, still ahead of now). The origin is
    never the next stop, as for Amtrak: a train standing there has not left,
    and the stop it is going to is the second. None when none is left."""
    for row in rows[1:]:
        leave = row[2] if row[2] is not None else row[1]
        if leave is None or leave > now:
            return row
    return None


class BrightlineRealtime:
    """Per config entry: remembers each trip's last usable fix (HOLD_S)."""

    def __init__(self) -> None:
        self._good: dict[str, tuple[Obs, float]] = {}

    def parse(self, positions: Any, trips: Any, now: float,
              stop_names: dict[str, str] | None = None) -> Snapshot | None:
        """Two decoded FeedMessages -> Snapshot, or None when the positions
        feed did not arrive or would not decode (an outage: the coordinator
        rides it out). An EMPTY positions feed is not an outage: Brightline
        runs no trains at night (round 4: none from 01:55 to 04:40 EDT).
        `trips` may be None: positions are published without next stops."""
        if positions is None:
            return None
        names = stop_names or {}
        snap = Snapshot()

        def skip(reason: str) -> None:
            snap.skipped[reason] = snap.skipped.get(reason, 0) + 1

        stops_by_trip: dict[str, list] = {}
        for ent in getattr(trips, "entity", ()) or ():
            if not ent.HasField("trip_update"):
                continue
            tu = ent.trip_update
            key = identity(tu.trip.trip_id, tu.trip.start_date)
            if key is not None and key not in stops_by_trip:
                stops_by_trip[key] = _stop_rows(tu)

        seen: set[str] = set()
        for ent in positions.entity:
            if not ent.HasField("vehicle"):
                continue
            v = ent.vehicle
            if not _has(v, "trip") or not v.trip.trip_id:
                skip("no_trip")
                continue
            key = identity(v.trip.trip_id, v.trip.start_date)
            if key is None:
                skip("no_trip_number")
                continue
            if key in seen:
                # Never measured (no trip carried two vehicles in either
                # round); first wins, as in Fleet.
                skip("duplicate")
                continue
            pos = position_of(v)
            if pos is None:
                skip("no_position")
                continue
            seen.add(key)
            when = vehicle_time(v)
            number = _number(v.trip.trip_id)
            obs = Obs(vehicle_id=key, lat=pos[0], lon=pos[1], observed_at=when,
                      in_service=True, train=number, line=None,
                      # The feed's bearing is set while standing too (0, 45,
                      # 315 at a platform): the line's bearing is used instead
                      # (projection.py), Fleet's chord where there is no line.
                      reported_course=None, trip_id=key)
            age = None if when is None else now - when.timestamp()
            if age is not None and age <= MAX_AGE_S:
                self._good[key] = (obs, now)
            else:
                good = self._good.get(key)
                if good is None or now - good[1] > HOLD_S:
                    skip("stale")
                    continue
                skip("stale_held")
                obs = good[0]
            snap.observations.append(obs)

            rows = stops_by_trip.get(key) or []
            extra: dict[str, Any] = {"line_name": LINE_NAME}
            if rows:
                # Where the train is going: the colour key (operators/brightline.py).
                extra["destination"] = rows[-1][0]
            nxt = next_stop_row(rows, now)
            if nxt is not None:
                stop_id, arr, dep, delay = nxt
                snap.stop_codes[key] = stop_id
                name = names.get(stop_id)
                if name:
                    # Absent until the GTFS names have loaded (D0: never a code
                    # dressed up as a name).
                    snap.next_stops[key] = (name, arr if arr is not None else dep)
                if delay is not None:
                    snap.trip_delays[key] = delay
            snap.extras[key] = extra
        for key in stops_by_trip.keys() - seen:
            skip("no_vehicle")
        # Forget trips that left the feed long ago.
        for key in [k for k, (_, at) in self._good.items() if now - at > HOLD_S and k not in seen]:
            self._good.pop(key, None)
        return snap
