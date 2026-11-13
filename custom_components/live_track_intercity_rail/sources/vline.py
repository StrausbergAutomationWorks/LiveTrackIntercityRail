"""Transport Victoria's V/Line feeds -> one Snapshot. No Home Assistant imports.

The shared client saw_livetrack.transport_vic fetches the feeds and keeps the timetable. Since saw-livetrack 0.2.38
(backlog 337; Lee 2026-11-13 01:45 CST, "Build and deploy") it hands this consumer ("intercity") only V/Line's
long-distance routes: GEL, BAT, TRN, BGO and SER, V/Line's own commuter class, went to Live Track Commuter Rail, revising
Lee's 2026-10-17 decision that all V/Line trains were this integration's (Intercity SSOT 8.5). The same day V/Line's
feed rules moved from this file into the library, saw_livetrack.vline, for both consumers ("Build and deploy covers PyPI
and moving the feed rules into the library", 01:48): the position feed running on the timetable, a missing row as a very
stale fix, the frozen feed (now read from the WHOLE feed: whole()), flips with CONFIRM_S, older fixes refused, the
trip-id fallback, the terminal's forecast as the end, the next stop. Their measurements and decisions are quoted there.
The constants and helpers are re-exported here unchanged.

LEFT HERE, this consumer's own:
* The timetable view: the lines file (geometry.distill_stream) behind saw_livetrack.vline.Timetable's four names
  (GeoTimetable): trip_tables, trip_services, services (geometry.service_runs) and stop_tables.
* The Snapshot: one Obs per run at its last accepted fix, the line the timetable trip's, `route_code` and `line_name`.
* THE TIMED RULE (decision 2): a stale row goes on at its last speed until the fix is TIMED_AFTER_S old, then is timed
  to its next stop; with no row (Report.held: the row gone, or the feed frozen), timed once the fix is ROW_GONE_TIMED_S
  old (HELD_SPEED_KEY, TIMED_AFTER_KEY; projection.py).
* STALLED (decision 7, rule C): sources/tfnsw.py's. Not while timed: nothing says where it is.
* IDENTITY "<service number>-<day of start date>" and LABEL the service number (decision 10), the library's identity.
"""

from __future__ import annotations

from typing import Any, Mapping

from saw_livetrack.gtfs.realtime import Obs
from saw_livetrack.transport_vic import TIME_ZONE, KeyedError, KeyRefused, TransportVicClient
from saw_livetrack.vline import (  # noqa: F401  (re-exported: operators/vline.py, the tests)
    CANCELED,
    CONFIRM_S,
    FINISHED_AGE_S,
    FROZEN_FEED_ROWS,
    FROZEN_FEED_S,
    MAX_FIRST_AGE_S,
    MAX_FIX_MS,
    ROW_GONE_TIMED_S,
    TIMED_AFTER_S,
    UPDATES_GONE_S,
    VLineRuns,
    feed_frozen,
    line_prefix,
    next_stop,
    route_code,
    service_number,
)

from ..geometry import service_runs
from .base import HELD_SPEED_KEY, TIMED_AFTER_KEY, Snapshot
from .tfnsw import TfnswRealtime


def read(client: Any, consumer: str) -> tuple[Any, Any, str | None]:
    """(positions, trip updates, timetable version) from the shared client.
    Blocking: run in the executor. Raises the client's errors."""
    positions, updates = client.for_consumer(consumer)
    return positions, updates, client.static_version(consumer)


def whole(client: Any, consumer: str) -> tuple[float | None, int] | None:
    """The WHOLE V/Line feed's (newest fix, dated fixes) from the shared client (saw-livetrack 0.2.38), for the frozen
    rule: this consumer is handed only its routes, and at midnight they may be one train. None from a client without it
    (the tests' stand-ins): the rule then reads this consumer's share, as before 0.2.38. Never waits for a fetch."""
    newest = getattr(client, "feed_newest", None)
    return newest(consumer) if newest is not None else None


def check_key(consumer: str, key: str) -> str | None:
    """One read with a user's key, for the setup form: None when it works, else the form's
    error ("invalid_key", "cannot_connect"). Blocking."""
    client = TransportVicClient({consumer: key})
    try:
        client.for_consumer(consumer)
    except KeyRefused:
        return "invalid_key"
    except KeyedError:
        return "cannot_connect"
    return None


class StaticView:
    """One consumer's folder of the client's timetable, as route_store asks for it."""

    def __init__(self, client: Any, consumer: str) -> None:
        self.client, self.consumer = client, consumer

    def static_version(self) -> str | None:
        return self.client.static_version(self.consumer)

    def static_path(self) -> str | None:
        return self.client.static_path(self.consumer)


class GeoTimetable:
    """This integration's lines file (geometry.distill_stream) behind saw_livetrack.vline.Timetable's names."""

    def __init__(self, geo: Mapping[str, Any]) -> None:
        self.tables = geo.get("trip_tables") or {}
        self.services = geo.get("trip_services") or {}
        self.calendars = geo.get("services") or {}
        self.stops = geo.get("stop_tables") or {}
        # The twin index is rebuilt when the lines file is another object.
        self.token = self.services

    def __contains__(self, trip_id: object) -> bool:
        return trip_id in self.tables

    def twin_candidates(self):
        return iter(self.services)

    def runs_on(self, trip_id: str, start_date: str) -> bool:
        return service_runs(self.calendars, self.services.get(trip_id), start_date)

    def stop_rows(self, trip_id: str) -> list:
        return self.stops.get(self.tables.get(trip_id)) or []


class VLineRealtime(TfnswRealtime):
    """Per config entry: the library's runs (saw_livetrack.vline.VLineRuns) and this consumer's Snapshot.
    The service day, the stalled rule and the forecast's zone are NSW's (sources/tfnsw.py)."""

    time_zone = TIME_ZONE

    def __init__(self) -> None:
        super().__init__()
        self._tracker = VLineRuns(origin=self._origin)

    @property
    def _runs(self) -> dict:
        return self._tracker.runs

    def _table_id(self, trip_id: str, start_date: str, geo: Mapping[str, Any]) -> str | None:
        return self._tracker.table_id(trip_id, start_date, GeoTimetable(geo))

    def _rows(self, trip_id: str, start_date: str, geo: Mapping[str, Any]) -> list:
        return self._tracker.rows(trip_id, start_date, GeoTimetable(geo))

    _feed_frozen = staticmethod(feed_frozen)

    def _report(self, snap: Snapshot, key: str, run: Any, now: float, geo: Mapping[str, Any],
                held: bool) -> None:
        snap.observations.append(Obs(
            vehicle_id=key, lat=run.lat, lon=run.lon, observed_at=run.observed, in_service=True,
            train=run.number, line=None,
            # The line's bearing is used (projection.py), Fleet's chord where there is no line.
            reported_course=None, trip_id=key))
        # The line is the timetable trip's: a live id the timetable lacks has none of its own.
        snap.route_keys[key] = run.table_id or run.trip_id
        extra: dict[str, Any] = {"route_code": route_code(run.route_id)}
        name = (geo.get("route_names") or {}).get(run.route_id)
        if name:
            extra["line_name"] = name
        age = None if run.when is None else now - run.when
        if held or (age is not None and age > TIMED_AFTER_S):
            # No speed to give: the estimate derives one, then times the train (projection.py).
            extra[HELD_SPEED_KEY] = None
            if held:
                extra[TIMED_AFTER_KEY] = ROW_GONE_TIMED_S
        elif self._stalled(key, run.lat, run.lon, run.when, run.rows, geo):
            extra["stalled"] = True
        snap.extras[key] = extra
        nxt = next_stop(run.rows, run.delays, run.skipped, now)
        if nxt is None:
            return
        _, stop, delay, eta = nxt
        snap.stop_codes[key] = stop
        stop_name = (geo.get("stop_names") or {}).get(stop)
        if stop_name:
            snap.next_stops[key] = (stop_name, eta)
        if run.delays:
            # With no delay in the update nothing is said (D0).
            snap.trip_delays[key] = delay

    def parse(self, positions: Any, updates: Any, now: float,
              geometry: Mapping[str, Any] | None = None,
              whole: tuple[float | None, int] | None = None) -> Snapshot | None:
        """The two FeedMessages -> Snapshot. None when the positions did not arrive. An EMPTY
        positions feed is not an outage: the client raises when the feed fails, and the runs are
        reported on. `updates` is None when that file failed: each run keeps its last delays.
        `whole`: the whole feed's newest fix (whole()). Blocking on the first run of a date (the
        zone file): run in the executor."""
        if positions is None:
            return None
        geo = geometry or {}
        snap = Snapshot()
        reports, skipped = self._tracker.update(positions, updates, now, GeoTimetable(geo), whole)
        snap.skipped.update(skipped)
        for rep in reports:
            self._report(snap, rep.key, rep.run, now, geo, held=rep.held)
        for k in [k for k in self._still if k not in self._runs]:
            self._still.pop(k, None)
        return snap
