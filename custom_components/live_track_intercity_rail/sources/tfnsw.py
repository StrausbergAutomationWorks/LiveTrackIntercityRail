"""Transport for NSW's `nswtrains` feed (NSW TrainLink's regional trains) -> one
Snapshot. No Home Assistant imports.

The shared client saw_livetrack.tfnsw fetches, routes each vehicle to ONE
consumer (06_MAP_CONTRACT.md D1) and cleans the feed once for every consumer: a
trip with a position holds only that run's update, and the position's stop_id,
current_stop_sequence, current_status and speed are gone. This module reads one
consumer's two feeds, so every rule here is tested offline against recorded
bodies.

Every rule MEASURED on capture round 1, 2026-10-18 to 10-21, or DECIDED by Lee
2026-11-01 (20_Research/_shared/australia/AU_CAPTURE1_ANALYSIS_20261101.md,
section 13; Intercity SSOT 8.5 and 8.6):

IDENTITY "<number>-<day of start date>": 72 runs, no collisions, and no number
twice on one date in 3 weeks of the 2026-11-01 timetable. NOT the vehicle (4
trips had two), NOT the entity id (221 to 337 per trip).

LABEL the number as GTFS route_short_name writes it (31, 243): decision 10. It
is read from `vehicle.label` ("05:45am (032)  Brisbane - Sydney"), so it needs no
timetable, and from the timetable where the label has none. The route_id will
not do: 4T.T.NT31 is 31 and 4T.T.SP31 is 631.

NEXT STOP (decision 11): the timetable plus the update's delay, first stop still
ahead. Never the position feed's stop, which is the one last left, and never an
update's `time`, which is often 0 or absent. A skipped stop is never next;
REPLACEMENT reads as scheduled, by not being looked at. As for the other railroads
the origin is not a next stop: a train standing there is going to the second. The
border stops (pickup_type and drop_off_type both 1, "Wodonga - Victoria Border
Stop Station") are no stops for a rider; geometry.distill leaves them out. The name
is the parent station's ("Grafton Station", not "..., Platform 1").

NO AGE REFUSAL (decision 3): 9 of 10 fixes reaching 300 s came back. A fix over
300 s old at FIRST sight gets no marker. A train is finished, and gets none,
once its terminal's forecast has passed and its fix is over 300 s old.

STALLED (decision 7, rule C): the scheduled dwell + 366 s within 300 m of one of
the trip's stops, 366 s elsewhere. Timetabled waits are real here (Grafton 840
s), so a flat wait pulses a late train during its own scheduled stop. Rule C was
the only one tested with no pulse inside a scheduled dwell at 366 s.

UPDATES outlive a train by a median 469 minutes, so an update never makes a marker.
"""

from __future__ import annotations

import datetime as dt
import re
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from saw_livetrack.gtfs.fleet import metres
from saw_livetrack.gtfs.realtime import Obs, position_of, vehicle_time
from saw_livetrack.gtfs.schedule import next_by_timetable, update_delays
from saw_livetrack.tfnsw import TIME_ZONE, KeyedError, KeyRefused, TfnswClient

from .base import Snapshot

MAX_FIRST_AGE_S = 300.0
FINISHED_AGE_S = 300.0
# Standing: Fleet's JITTER_M, PLATFORM_HOLD_S and STALL_M, with the dwell added.
MOVED_M = 50.0
STALL_S = 366.0
AT_STOP_M = 300.0
# A failed update poll keeps the last answer this long (const.SOURCE_GAP_S): 6 of
# 8,096 update polls failed in the capture, and the hover should not blink.
UPDATES_HOLD_S = 600.0
# How long a run's state outlives its last row.
FORGET_S = 3600.0

_LABEL_NUMBER = re.compile(r"\((\d{1,4})\)")


def number_of(label: Any) -> str | None:
    """'05:45am (032)  Brisbane - Sydney' -> '32'; None without one."""
    m = _LABEL_NUMBER.search(label) if isinstance(label, str) else None
    return str(int(m.group(1))) if m else None


def identity(number: str, start_date: str | None) -> str:
    """'31', '20261020' -> '31-20'; the bare number with no usable start date."""
    sd = (start_date or "").strip()
    if len(sd) == 8 and sd.isdigit():
        return f"{number}-{int(sd[6:8])}"
    return number


def read(client: Any, consumer: str) -> tuple[Any, Any, str | None]:
    """(positions, trip updates, timetable version) from the shared client.
    Blocking: run in the executor. Raises the client's errors."""
    positions, updates = client.for_consumer(consumer)
    return positions, updates, client.static_version()


def check_key(consumer: str, key: str) -> str | None:
    """One read with a user's key, for the setup form: None when it works,
    else the form's error ("invalid_key", "cannot_connect"). Blocking."""
    client = TfnswClient({consumer: key})
    try:
        client.for_consumer(consumer)
    except KeyRefused:
        return "invalid_key"
    except KeyedError:
        return "cannot_connect"
    return None


def _terminal_forecast(rows: list, delays: Mapping[int, int]) -> float | None:
    """When the last stop's forecast falls: its scheduled arrival plus the last
    delay known. None without a timetable."""
    if not rows:
        return None
    last = 0
    for seq, *_ in rows:
        if seq in delays:
            last = delays[seq]
    seq, stop, arrival, departure = rows[-1]
    when = arrival if arrival is not None else departure
    return None if when is None else when + last


class TfnswRealtime:
    """Per config entry: which runs have had a fresh fix, where each last moved,
    and the last answer of the updates."""

    # The zone a service day's times are in (sources/vline.py has its own).
    time_zone = TIME_ZONE

    def __init__(self) -> None:
        self._fresh: dict[str, float] = {}
        self._still: dict[str, tuple[float, float, float]] = {}
        self._updates: Any = None
        self._updates_t = 0.0
        self._zone = None
        self._origins: dict[str, float | None] = {}

    def _origin(self, start_date: str) -> float | None:
        """The GTFS service day's origin as an epoch: local noon less 12 hours,
        the only reading that holds across a daylight-saving change."""
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

    def _stalled(self, key: str, lat: float, lon: float, when: float | None, rows: list,
                 geo: Mapping[str, Any]) -> bool:
        """Rule C (module docstring), from the fixes' own times."""
        if when is None:
            return False
        held = self._still.get(key)
        if held is None or metres(held[0], held[1], lat, lon) > MOVED_M or when < held[2]:
            self._still[key] = (lat, lon, when)
            return False
        still = when - held[2]
        if still < STALL_S:
            return False
        stops = geo.get("stops") or {}
        best, dwell = AT_STOP_M, 0.0
        for _, stop, arrival, departure in rows:
            at = stops.get(stop)
            if not at:
                continue
            m = metres(lat, lon, at[0], at[1])
            if m <= best:
                best = m
                dwell = departure - arrival if arrival is not None and departure is not None else 0.0
        return still >= dwell + STALL_S

    def parse(self, positions: Any, updates: Any, now: float,
              geometry: Mapping[str, Any] | None = None) -> Snapshot | None:
        """The consumer's two FeedMessages -> Snapshot. None when the positions did
        not arrive. An EMPTY positions feed is a quiet hour, not an outage: the
        client raises when the feed fails. `updates` may be None: the last answer
        is used for UPDATES_HOLD_S. Blocking on the first run of a date (the zone
        file): run in the executor."""
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

        by_run: dict[tuple[str, str], Any] = {}
        for ent in getattr(updates, "entity", ()) or ():
            if ent.HasField("trip_update"):
                trip = ent.trip_update.trip
                by_run.setdefault((trip.trip_id.strip(), trip.start_date.strip()), ent.trip_update)

        numbers = geo.get("trip_numbers") or {}
        names = geo.get("stop_names") or {}
        routes = geo.get("train_routes") or {}
        seen: set[str] = set()
        for ent in positions.entity:
            if not ent.HasField("vehicle"):
                continue
            v = ent.vehicle
            trip_id = v.trip.trip_id.strip()
            start = v.trip.start_date.strip()
            number = number_of(v.vehicle.label) or numbers.get(trip_id)
            if not number:
                skip("no_number")
                continue
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
            rows = self._rows(trip_id, start, geo)
            forecast = _terminal_forecast(rows, delays)
            if forecast is not None and forecast < now and age is not None and age > FINISHED_AGE_S:
                skip("finished")
                continue
            self._fresh[key] = now
            seen.add(key)
            snap.observations.append(Obs(
                vehicle_id=key, lat=pos[0], lon=pos[1], observed_at=when, in_service=True,
                train=number, line=None,
                # The line's bearing is used (projection.py), Fleet's chord where
                # there is no line.
                reported_course=None, trip_id=key))
            snap.route_keys[key] = trip_id
            extra: dict[str, Any] = {}
            name = routes.get(trip_id)
            if name:
                extra["line_name"] = name
            if self._stalled(key, pos[0], pos[1], stamp, rows, geo):
                extra["stalled"] = True
            if extra:
                snap.extras[key] = extra
            if rows:
                # The origin's delay still counts for the stop after it.
                ahead = rows[1:] if len(rows) > 1 else rows
                known = dict(delays)
                if rows[0][0] in known and ahead[0][0] not in known:
                    known[ahead[0][0]] = known[rows[0][0]]
                nxt = next_by_timetable(ahead, known, skipped, now)
                if nxt is not None:
                    _, stop, delay, eta = nxt
                    snap.stop_codes[key] = stop
                    stop_name = names.get(stop)
                    if stop_name:
                        snap.next_stops[key] = (stop_name, eta)
                    if delays:
                        # With no delay in the update nothing is said (D0).
                        snap.trip_delays[key] = delay
        for k in [k for k, t in self._fresh.items() if now - t > FORGET_S]:
            self._fresh.pop(k, None)
        for k in [k for k in self._still if k not in self._fresh]:
            self._still.pop(k, None)
        return snap
