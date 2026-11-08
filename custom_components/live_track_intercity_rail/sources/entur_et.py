"""Entur's SIRI Estimated Timetable (Norway) -> one Snapshot, for a railroad that publishes NO position. No Home
Assistant imports.

SJ NORD (Lee 2026-11-08 10:59 CST: "Build SJ Nord from its expected times, actuals as a correction"; Intercity SSOT
8.8, "SJ NORD"). It publishes no position anywhere on Entur, only every call's aimed, expected and actual times through
Bane NOR's SIRI ET; the shared client reads it once a minute for every consumer and hands over plain journeys
(saw_livetrack.entur.et_journeys). Every train here is an ESTIMATE, never a fix: `position_source` "estimated" and no
`fix_latitude` (projection.py, NO_FIX_KEY).

MEASURED on the capture of 2026-11-07 21:34Z to 2026-11-08 11:04Z (811 polls; bin\\no_sjn_analyse2.txt), daytime:
* an expected arrival 5-15 minutes ahead is off by p50 35 s, p90 112 s;
* an actual DEPARTURE is published p50 88 s, p90 131 s after the event; an actual ARRIVAL p50 203 s, p90 340 s after;
* a third of calls never get an actual at all, sometimes for the rest of a run (R71 1303's last five calls).
So the EXPECTED times carry the train and an actual corrects them: a missing actual is the normal case, and the train
never waits for one.

WHERE A TRAIN IS (call_times, place). Each call gets one arrival and one departure: its actual, else its expected, else
its aimed plus the delay last KNOWN before it (a passed call carries only aimed and actual times: measured, a
RecordedCall has no expected time); a call with no time at all, or cancelled, is left out. Then, at `now`:
* before its first departure, from PRE_DEPARTURE_S: standing at its origin;
* between a call's arrival and its departure: standing there (HOLD);
* after a call's departure: from that call, along its line toward the next, arriving at the next call's arrival (the
  timed rule: AIM_ETA_KEY), and held there if it has not arrived by then, until that call's own departure passes, by
  the same rule (so never waiting for an actual);
* at its last call until FINISHED_S after its arrival; then gone.
An actual that comes later than the expected time it replaces moves the anchor's TIME, never the train back: the
estimate goes on from where the train was last drawn (geometry.Projector._timed, and its never-backwards clamp).

THE LINE: the timetable's trip with this train's number whose stops share the most with the journey's (ET names quays,
NSR:Quay:...; Entur's GTFS stop_id is the quay), so the shape the estimate runs on is this run's own. IDENTITY
"<number>-<day>", as Vy's (sources/entur.py). LABEL, LOOK and LATE: operators/norway.py.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Iterable, Mapping

from saw_livetrack.gtfs.realtime import Obs

from .base import AIM_ETA_KEY, HELD_SPEED_KEY, NO_FIX_KEY, TIMED_AFTER_KEY, Snapshot
from .entur import HOLD, identity, number_of, train_line_name

# Drawn at its origin from this long before its first departure.
PRE_DEPARTURE_S = 300.0
# Kept at its last call this long after arriving.
FINISHED_S = 300.0
# A failed read keeps the last answer this long (const.SOURCE_GAP_S); the coordinator holds the snapshot itself.
FORGET_S = 3600.0
TIMES = ("aimed_arrival", "aimed_departure", "expected_arrival", "expected_departure", "actual_arrival",
         "actual_departure")
# No stretch is run in less than this share of its scheduled time: an arrival that says so is not believed, and the
# call takes its aimed time plus the delay known before it. MEASURED on the capture (bin\\sjn_ratio.txt): actual over
# scheduled running time, 193 stretches, min 0.33 (Trondheim lufthavn-Hell, 50 s against 150), p5 0.62, p50 0.89;
# expected arrivals under 0.7 in 629 of 882,680 reads, the worst 0.0: F7 478's expected arrival at Bjerka was its
# expected departure from Mo i Rana, 22 km and 25 minutes back (bin\\sjn_dbg.txt), and the train was drawn there at once.
RUN_FLOOR = 0.3


def read(client: Any, consumer: str, codespace: str, view: Any = None) -> tuple[Any, str | None]:
    """(journeys, timetable version) from the shared client. Blocking: run in the executor. Raises the client's
    errors."""
    journeys = client.et_for_consumer(consumer, codespace)
    return journeys, view.static_version() if view is not None else client.static_version(codespace)


def call_times(calls: Iterable[Mapping[str, Any]]) -> list[tuple[Mapping[str, Any], float, float, bool]]:
    """[(call, arrival, departure, known)] for the calls with a time, in order (module docstring). `known`: its
    arrival is the railroad's own word (actual or expected), not the aimed time plus a carried delay. A call with no
    arrival takes its departure, and the reverse; a departure is never before its arrival."""
    out = []
    delay = 0.0
    prev_dep = prev_ad = None
    for c in calls:
        if c.get("cancelled"):
            continue
        aa, ad = c.get("aimed_arrival"), c.get("aimed_departure")
        word_a = c.get("actual_arrival") if c.get("actual_arrival") is not None else c.get("expected_arrival")
        word_d = c.get("actual_departure") if c.get("actual_departure") is not None else c.get("expected_departure")
        if (word_a is not None and aa is not None and prev_dep is not None and prev_ad is not None
                and aa > prev_ad and word_a - prev_dep < RUN_FLOOR * (aa - prev_ad)):
            word_a = None     # faster than any train runs it (RUN_FLOOR)
        arr = word_a if word_a is not None else (aa + delay if aa is not None else None)
        dep = word_d if word_d is not None else (ad + delay if ad is not None else None)
        # What this call says about the delay, for the calls after it that say nothing.
        if word_d is not None and ad is not None:
            delay = word_d - ad
        elif word_a is not None and aa is not None:
            delay = word_a - aa
        if arr is None and dep is None:
            continue
        arr = dep if arr is None else arr
        dep = arr if dep is None else max(dep, arr)
        out.append((c, arr, dep, word_a is not None))
        prev_dep, prev_ad = dep, (ad if ad is not None else aa)
    return out


def place(times: list, now: float) -> tuple[str, int] | None:
    """Where the train is: ("standing", i) at times[i], ("running", i) from times[i] toward times[i + 1]; None when
    it is not out (before PRE_DEPARTURE_S of its first departure, or FINISHED_S after its last arrival)."""
    if not times:
        return None
    if now < times[0][2] - PRE_DEPARTURE_S or now > times[-1][1] + FINISHED_S:
        return None
    # The last call it has reached by its times (the origin counts from before it leaves).
    i = 0
    for k in range(1, len(times)):
        if times[k][1] <= now:
            i = k
    if i == len(times) - 1 or now < times[i][2]:
        return ("standing", i)
    return ("running", i)


class EnturEtRealtime:
    """Per config entry: the line each journey was matched to."""

    def __init__(self) -> None:
        self._trip: dict[str, str | None] = {}
        self._seen: dict[str, float] = {}
        self._index_of: int | None = None
        self._by_number: dict[str, list[str]] = {}

    def _numbers(self, geo: Mapping[str, Any]) -> dict[str, list[str]]:
        trips = geo.get("trip_stops") or {}
        if self._index_of != id(trips):
            self._index_of = id(trips)
            self._trip.clear()
            self._by_number = {}
            for tid in trips:
                n = number_of(tid)
                if n:
                    self._by_number.setdefault(n, []).append(tid)
        return self._by_number

    def trip_for(self, journey: Mapping[str, Any], geo: Mapping[str, Any]) -> str | None:
        """The timetable trip with this train's number whose stops share the most with the journey's; None with no
        trip of that number, or none sharing a stop."""
        key = journey.get("id") or ""
        by_number = self._numbers(geo)
        if key in self._trip:
            return self._trip[key]
        quays = {c.get("stop") for c in journey.get("calls") or ()}
        trips = geo.get("trip_stops") or {}
        best, score = None, 0
        for tid in sorted(by_number.get(journey.get("number") or "", ())):
            n = len(quays & {row[1] for row in trips.get(tid) or ()})
            if n > score:
                best, score = tid, n
        self._trip[key] = best
        return best

    @staticmethod
    def stop_of(c: Mapping[str, Any], calls_n: int, rows: list, stops: Mapping[str, Any],
                names: Mapping[str, str]) -> str | None:
        """The timetable stop a call is at: its own quay when the timetable has it; else, on the matched trip, the
        stop whose station name begins with the call's name, else the trip's stop at the call's Order when the trip
        has as many stops as the journey has calls; None with none. MEASURED on the capture (bin\\sjn_quays.txt):
        Melhus' NSR:Quay:111911, on every R60 and R70, is not in SJ Nord's timetable at all; Hamar's NSR:Quay:355 is,
        but no trip kept uses it."""
        quay = c.get("stop")
        if quay in stops:
            return quay
        ids = [row[1] for row in rows]
        name = (c.get("name") or "").strip().lower()
        if name:
            hit = [s for s in ids if (names.get(s) or "").strip().lower().startswith(name) and s in stops]
            if len(set(hit)) == 1:
                return hit[0]
        order = c.get("order")
        if isinstance(order, int) and len(ids) == calls_n and 1 <= order <= len(ids) and ids[order - 1] in stops:
            return ids[order - 1]
        return None

    def parse(self, journeys: Any, now: float, geometry_: Mapping[str, Any] | None = None) -> Snapshot | None:
        """The consumer's journeys -> Snapshot. None when the journeys did not arrive (the client raises when the
        feed fails; an EMPTY list is a quiet hour)."""
        if journeys is None:
            return None
        geo = geometry_ or {}
        stops = geo.get("stops") or {}
        names = geo.get("stop_names") or {}
        routes = geo.get("train_routes") or {}
        colors = geo.get("trip_colors") or {}
        hubs = geo.get("trip_hub") or {}
        trips = geo.get("trip_stops") or {}
        snap = Snapshot()

        def skip(reason: str) -> None:
            snap.skipped[reason] = snap.skipped.get(reason, 0) + 1

        seen: set[str] = set()
        for j in journeys:
            if j.get("cancelled"):
                skip("cancelled")
                continue
            number = j.get("number")
            if not number:
                skip("no_number")
                continue
            key = identity(number, j.get("date"))
            if key in seen:
                skip("duplicate")
                continue
            times = call_times(j.get("calls") or ())
            where = place(times, now)
            if where is None:
                skip("not_running")
                continue
            state, i = where
            call, arr_i, dep_i, _ = times[i]
            trip_id = self.trip_for(j, geo)
            rows = (trips.get(trip_id) or []) if trip_id else []
            calls_n = len(j.get("calls") or ())
            pos = stops.get(self.stop_of(call, calls_n, rows, stops, names))
            if not pos:
                skip("no_stop_position")
                continue
            seen.add(key)
            self._seen[key] = now
            # Placed AT the call it last reached, at the time it reached (standing) or left (running) it.
            when = arr_i if state == "standing" and now >= arr_i else (dep_i if state == "running" else now)
            snap.observations.append(Obs(
                vehicle_id=key, lat=float(pos[0]), lon=float(pos[1]),
                observed_at=dt.datetime.fromtimestamp(min(when, now), dt.timezone.utc), in_service=True,
                train=number, line=None, reported_course=None, trip_id=key))
            extra: dict[str, Any] = {"line_name": train_line_name(number, routes.get(trip_id) if trip_id else None),
                                     NO_FIX_KEY: True}
            if j.get("line"):
                extra["route_code"] = j["line"]
            if trip_id:
                snap.route_keys[key] = trip_id
                if colors.get(trip_id):
                    extra["route_color"] = colors[trip_id]
            snap.extras[key] = extra
            nxt = times[i + 1] if i + 1 < len(times) else None
            if state == "standing" or nxt is None:
                extra.update(HOLD)
            else:
                extra[HELD_SPEED_KEY] = None
                extra[TIMED_AFTER_KEY] = 0.0
                extra[AIM_ETA_KEY] = nxt[1]
            if nxt is None:
                continue
            ncall, narr, _, known = nxt
            nstop = self.stop_of(ncall, calls_n, rows, stops, names) or ncall.get("stop")
            snap.stop_codes[key] = nstop
            name = names.get(nstop) or ncall.get("name")
            if name:
                snap.next_stops[key] = (name, narr)
            aimed = ncall.get("aimed_arrival")
            if aimed is None:
                aimed = ncall.get("aimed_departure")
            if known and aimed is not None:
                # Only the railroad's own word is a delay (D0): a carried one is not said.
                snap.trip_delays[key] = int(round(narr - aimed))
            hub = hubs.get(trip_id) if trip_id else None
            if hub is not None:
                ids = [row[1] for row in rows]
                idx = ids.index(nstop) if nstop in ids else None
                if idx is not None:
                    extra["toward_hub"] = hub >= idx
        for k in [k for k, t in self._seen.items() if now - t > FORGET_S]:
            self._seen.pop(k, None)
        return snap
