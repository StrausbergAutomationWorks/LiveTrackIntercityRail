"""Transport Victoria's V/Line feeds -> one Snapshot. No Home Assistant imports.

The shared client saw_livetrack.transport_vic fetches and keeps the timetable. No V/Line rule is
in the library: they are this consumer's. Every rule MEASURED on capture round 1, 2026-10-18 to
10-21, or DECIDED by Lee 2026-11-01 and 11-02
(20_Research/_shared/australia/AU_CAPTURE1_ANALYSIS_20261101.md, section 13; Intercity SSOT 8.5):

THE POSITION FEED RUNS ON THE TIMETABLE, NOT THE TRAIN. A trip leaves it about a minute after its
scheduled arrival wherever the train is: 45.5% of 1,137 trips were last seen over 1 km short of
the terminal, every run forecast 10 minutes or more late among them. Fixes freeze at about 23:58
and running trips leave at 00:15, the same nine trains losing up to 130 minutes each night.
Their trip updates go on.

SO A MISSING ROW IS A VERY STALE FIX (decision 1). A run keeps its last accepted fix and goes on
being reported with it, at that fix's time, so Fleet and the estimate treat the freeze, the 00:15
cut and the timetable's exit alike. A stale row goes on at its last speed until the fix is 10
minutes old (decision 2), then is timed to its next stop. With no row, timed once the fix is 120 s
old. Scored on 223 to 252 late runs with their rows hidden (bin\\ltir_vl_holdout_variants.txt), metres from
the fixes hidden, 5 to 10 minutes on, p50 / p90: timed from 120 s 987 / 4,491, from 600 s 2,469 /
8,282. It ends when the terminal's forecast has passed, when the trip is cancelled, or when
good answers have not carried it for UPDATES_GONE_S; a failed answer never counts. Nothing can
report on the train once its row has ended, only on these hidden stretches (INFERRED that it is
running, strongly: section 4). The state is in memory: after a restart these trains are gone until
their next run.

A FROZEN FEED COUNTS AS NO ROW (Lee 2026-11-02 14:03). The first midnight on the box: a frozen row
stood at its next stop, then raced at 10 minutes (8817, 176 km/h for five minutes). Timing every
stale row sooner is wrong: at 300 s a real stale fix, 300-600 s old, went from p50 1,324 m to 2,406
(bin\\ltir_vl_t_show.txt). A freeze can be told without a clock, every train stopping at once: when
the newest fix in the whole feed is over FROZEN_FEED_S old with FROZEN_FEED_ROWS or more rows. In 67.6
hours, both midnights and two single polls by day (bin\\ltir_vl_t_feedwide.txt); every other spell
had one row, a lone train or the frozen last Geelong run.

IDENTITY "<service number>-<day of start date>": 1,151 runs, no collisions; the trip id repeats
across dates (377). NOT the vehicle: 46 trips had two, 50 an empty one, and 3 sat on two trips at
once. LABEL the service number (decision 10): the last four digits of trip_id on 6,988 of 6,988,
even toward Melbourne.

NO AGE REFUSAL (decision 3): 89% of fixes reaching 300 s came back. A fix over 300 s old at FIRST
sight gets no marker. A train is finished, and gets none, once its terminal's forecast has passed
and its fix is over 300 s old: the last Geelong run stands frozen in the feed until 04:22.

FLIPS (decision 5): a fix over 70 m/s from the last accepted one is refused, and the train goes
on from that one: 14 pairs on 4 trips of 1,151, out and back 33 to 254 km with no change of
vehicle id, INFERRED to be two units reporting under one id; the longest such stretch ran 19
minutes (bin\\ltir_vl_flips.txt). Commuter Rail's plausible.py was read first and is not shared: its
150 m own-shape refusal goes against decision 6 and it reads that integration's timetable. Its one
idea taken: refused fixes that agree with each other for CONFIRM_S are the truth, or a wrong first
fix would hold the right ones off for as long as 70 m/s takes to cover the distance.

A FIX CAN COME OLDER THAN ONE ALREADY READ (bin\\ltir_vl_older.txt; the analysis sorted by fix time
and did not see it): 1,192 of 111,262, on 633 of 1,151 runs, nearly always one fix alone, p50 23 s
behind, p90 514, max 1,703, with the next fix current again. It says nothing new: refused, no vote.

NEXT STOP (D5): the timetable plus the update's delay, first stop still ahead, since the updates
name no stop ahead on 20.8% of cases. The name as published. The origin is never next.

A LIVE TRIP ID MAY NOT BE IN THE TIMETABLE (Lee 2026-11-05 21:34, "Build the V/Line fallback").
Found 2026-11-05 with no new publication since 11-02 (same ETag): the realtime feed named Friday's
trips `01-GEL--1-T0-8751` on six lines where the timetable has `01-GEL--5-T0-8751`; 20 of 33 running
trains had no stops, no delay and no estimate (bin\\ltir_vl_tripids.txt). Such a trip takes the ONE
timetable trip with the same line prefix (`01-GEL`) and service number whose service runs on its
start date: 34 of 34 had exactly one, 33 of 34 matching every stop its update names by stop_id and
sequence (bin\\ltir_vl_unknown_trips.txt), and across the publication's first 63 days every line and
number running on a date ran ONE trip (21,835 of 21,835, bin\\ltir_vl_fb_census.txt). None or several:
nothing, as before. The trip update is still matched by the live id; only the stops and the line
come from the timetable trip.

STALLED (decision 7, rule C): sources/tfnsw.py's. Not while timed: nothing says where it is.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from saw_livetrack.gtfs.fleet import metres
from saw_livetrack.gtfs.realtime import Obs, position_of, vehicle_time
from saw_livetrack.gtfs.schedule import next_by_timetable, update_delays
from saw_livetrack.transport_vic import TIME_ZONE, KeyedError, KeyRefused, TransportVicClient

from ..geometry import service_runs
from .base import HELD_SPEED_KEY, TIMED_AFTER_KEY, Snapshot
from .tfnsw import TfnswRealtime, _terminal_forecast, identity

MAX_FIRST_AGE_S = 300.0
FINISHED_AGE_S = 300.0
# Fix age at which the last speed gives way to the timed rule (Lee 2026-11-01, decision 2):
# on 25 gaps of 10-30 minutes that came back, p50 2,033 m timed against 9,285 m at the last speed.
TIMED_AFTER_S = 600.0
MAX_FIX_MS = 70.0
CONFIRM_S = 1800.0
# Replay: 341 times an answer missed a running trip and it was back within 2 minutes; never longer.
# The answers in the capture are about 60 s apart.
UPDATES_GONE_S = 180.0
ROW_GONE_TIMED_S = 120.0
FROZEN_FEED_S = 180.0
FROZEN_FEED_ROWS = 2
CANCELED = 3


def service_number(trip_id: str) -> str | None:
    """'01-ABY--10-T0-8605' -> '8605'; None when the id does not end in a number."""
    tail = trip_id.rsplit("-", 1)[-1] if trip_id else ""
    return tail if tail.isdigit() else None


def line_prefix(trip_id: str) -> str | None:
    """'01-GEL--1-T0-8751' -> '01-GEL'; None without the '--'."""
    head, sep, _ = (trip_id or "").partition("--")
    return head if sep and head else None


def route_code(route_id: str) -> str:
    """'aus:vic:vic-01-GEL:' -> 'GEL'."""
    return route_id.strip().rstrip(":").rsplit("-", 1)[-1]


def read(client: Any, consumer: str) -> tuple[Any, Any, str | None]:
    """(positions, trip updates, timetable version) from the shared client.
    Blocking: run in the executor. Raises the client's errors."""
    positions, updates = client.for_consumer(consumer)
    return positions, updates, client.static_version(consumer)


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


@dataclass
class _Run:
    trip_id: str
    start: str
    number: str
    route_id: str
    lat: float | None = None        # the last accepted fix
    lon: float | None = None
    when: float | None = None
    observed: Any = None
    rows: list = field(default_factory=list)
    delays: dict = field(default_factory=dict)
    skipped: set = field(default_factory=set)
    gone_since: float | None = None  # since when good answers have not carried it
    cand: list = field(default_factory=list)  # [(lat, lon, time)] refused in a row
    table_id: str | None = None      # the timetable's trip: trip_id, or its twin (_table_id)


class VLineRealtime(TfnswRealtime):
    """Per config entry: each running trip's last accepted fix, its timetable and last delays.
    The service day, the stalled rule and the forecast are NSW's (sources/tfnsw.py)."""

    time_zone = TIME_ZONE

    def __init__(self) -> None:
        super().__init__()
        self._runs: dict[str, _Run] = {}
        self._twin_src: Any = None
        self._twin_idx: dict[tuple[str, str], list[str]] = {}

    def _twins(self, geo: Mapping[str, Any]) -> dict[tuple[str, str], list[str]]:
        """(line prefix, service number) -> the timetable's trip ids, built once per copy."""
        services = geo.get("trip_services") or {}
        if services is not self._twin_src:
            idx: dict[tuple[str, str], list[str]] = {}
            for trip in services:
                prefix, number = line_prefix(trip), service_number(trip)
                if prefix and number:
                    idx.setdefault((prefix, number), []).append(trip)
            self._twin_src, self._twin_idx = services, idx
        return self._twin_idx

    def _table_id(self, trip_id: str, start_date: str, geo: Mapping[str, Any]) -> str | None:
        """The timetable trip for a live trip: itself when the timetable has it, else the ONE
        trip with its line prefix and service number whose service runs on start_date (the
        module docstring); None when there is none or more than one."""
        tables = geo.get("trip_tables") or {}
        if trip_id in tables:
            return trip_id
        prefix, number = line_prefix(trip_id), service_number(trip_id)
        if not prefix or not number:
            return None
        services, calendars = geo.get("trip_services") or {}, geo.get("services") or {}
        hits = [t for t in self._twins(geo).get((prefix, number), ())
                if t in tables and service_runs(calendars, services.get(t), start_date)]
        return hits[0] if len(hits) == 1 else None

    def _run_rows(self, run: _Run, geo: Mapping[str, Any]) -> None:
        """Fill a run's timetable rows (and its timetable trip) while it has none."""
        if run.rows:
            return
        run.table_id = self._table_id(run.trip_id, run.start, geo)
        run.rows = self._rows(run.table_id, run.start, geo) if run.table_id else []

    def _rows(self, trip_id: str, start_date: str, geo: Mapping[str, Any]) -> list:
        """[(sequence, stop_id, arrival epoch, departure epoch)] for this run."""
        table = (geo.get("stop_tables") or {}).get((geo.get("trip_tables") or {}).get(trip_id))
        if not table:
            return []
        origin = self._origin(start_date)
        if origin is None:
            return []
        return [(seq, stop, None if a is None else origin + a, None if d is None else origin + d)
                for seq, stop, a, d in table]

    @staticmethod
    def _note_update(run: _Run, update: Any, answered: bool, now: float) -> None:
        if update is not None:
            run.gone_since = None
            delays, skipped = update_delays(update)
            # An update with no stops says nothing about the delay.
            if delays or skipped:
                run.delays, run.skipped = delays, skipped
        elif answered and run.gone_since is None:
            run.gone_since = now

    @staticmethod
    def _accept(run: _Run, lat: float, lon: float, stamp: float | None, observed: Any) -> bool:
        """Decision 5. True when the run's fix is now this one or stands unchanged by choice:
        False only when this row was refused."""
        if run.lat is None or run.when is None or stamp is None:
            run.lat, run.lon, run.when, run.observed, run.cand = lat, lon, stamp, observed, []
            return True
        if (lat, lon) == (run.lat, run.lon):
            if stamp > run.when:
                run.when, run.observed = stamp, observed
            run.cand = []
            return True
        gap = stamp - run.when
        if gap <= 0:
            return False
        if metres(run.lat, run.lon, lat, lon) / gap <= MAX_FIX_MS:
            run.lat, run.lon, run.when, run.observed, run.cand = lat, lon, stamp, observed, []
            return True
        cand = run.cand
        if not cand or stamp > cand[-1][2]:
            last = cand[-1] if cand else None
            if last is not None and metres(last[0], last[1], lat, lon) / (stamp - last[2]) <= MAX_FIX_MS:
                cand.append((lat, lon, stamp))
            else:
                run.cand = cand = [(lat, lon, stamp)]
            if stamp - cand[0][2] >= CONFIRM_S:
                run.lat, run.lon, run.when, run.observed, run.cand = lat, lon, stamp, observed, []
                return True
        return False

    @staticmethod
    def _feed_frozen(positions: Any, now: float) -> bool:
        """Every dated fix in the feed old at once, with at least FROZEN_FEED_ROWS of them."""
        stamps = []
        for ent in positions.entity:
            if ent.HasField("vehicle") and position_of(ent.vehicle) is not None:
                when = vehicle_time(ent.vehicle)
                if when is not None:
                    stamps.append(when.timestamp())
        return len(stamps) >= FROZEN_FEED_ROWS and now - max(stamps) > FROZEN_FEED_S

    def _ended(self, run: _Run, update: Any, now: float) -> bool:
        """A run with no row: whether it stops being reported."""
        if run.when is None:
            return True
        if run.gone_since is not None and now - run.gone_since >= UPDATES_GONE_S:
            return True
        if update is not None and update.trip.schedule_relationship == CANCELED:
            return True
        forecast = _terminal_forecast(run.rows, run.delays)
        return forecast is None or forecast < now

    def _report(self, snap: Snapshot, key: str, run: _Run, now: float, geo: Mapping[str, Any],
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
        rows = run.rows
        if not rows:
            return
        # The origin's delay still counts for the stop after it.
        ahead = rows[1:] if len(rows) > 1 else rows
        known = dict(run.delays)
        if rows[0][0] in known and ahead[0][0] not in known:
            known[ahead[0][0]] = known[rows[0][0]]
        nxt = next_by_timetable(ahead, known, run.skipped, now)
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
              geometry: Mapping[str, Any] | None = None) -> Snapshot | None:
        """The two FeedMessages -> Snapshot. None when the positions did not arrive. An EMPTY
        positions feed is not an outage: the client raises when the feed fails, and the runs are
        reported on. `updates` is None when that file failed: each run keeps its last delays.
        Blocking on the first run of a date (the zone file): run in the executor."""
        if positions is None:
            return None
        geo = geometry or {}
        answered = updates is not None
        snap = Snapshot()

        def skip(reason: str) -> None:
            snap.skipped[reason] = snap.skipped.get(reason, 0) + 1

        by_run: dict[tuple[str, str], Any] = {}
        for ent in getattr(updates, "entity", ()) or ():
            if ent.HasField("trip_update"):
                trip = ent.trip_update.trip
                by_run.setdefault((trip.trip_id.strip(), trip.start_date.strip()), ent.trip_update)

        frozen = self._feed_frozen(positions, now)
        if frozen:
            skip("feed_frozen")
        seen: set[str] = set()
        for ent in positions.entity:
            if not ent.HasField("vehicle"):
                continue
            v = ent.vehicle
            trip_id = v.trip.trip_id.strip()
            start = v.trip.start_date.strip()
            number = service_number(trip_id)
            if not number:
                skip("no_number")
                continue
            key = identity(number, start)
            if key in seen:
                skip("duplicate")
                continue
            pos = position_of(v)
            if pos is None:
                # Not `seen`: a run already known goes on below.
                skip("no_position")
                continue
            when = vehicle_time(v)
            stamp = when.timestamp() if when is not None else None
            age = None if stamp is None else now - stamp
            run = self._runs.get(key)
            if run is None and age is not None and age > MAX_FIRST_AGE_S:
                skip("stale_first_sight")
                continue
            if run is None:
                run = _Run(trip_id, start, number, v.trip.route_id.strip())
            self._run_rows(run, geo)
            self._note_update(run, by_run.get((trip_id, start)), answered, now)
            forecast = _terminal_forecast(run.rows, run.delays)
            if forecast is not None and forecast < now and age is not None and age > FINISHED_AGE_S:
                self._runs.pop(key, None)
                skip("finished")
                continue
            if not self._accept(run, pos[0], pos[1], stamp, when):
                skip("fix_refused")
            self._runs[key] = run
            seen.add(key)
            self._report(snap, key, run, now, geo, held=frozen)

        for key, run in list(self._runs.items()):
            if key in seen:
                continue
            update = by_run.get((run.trip_id, run.start))
            self._note_update(run, update, answered, now)
            self._run_rows(run, geo)
            if self._ended(run, update, now):
                del self._runs[key]
                skip("ended")
                continue
            skip("held")
            self._report(snap, key, run, now, geo, held=True)
        for k in [k for k in self._still if k not in self._runs]:
            self._still.pop(k, None)
        return snap
