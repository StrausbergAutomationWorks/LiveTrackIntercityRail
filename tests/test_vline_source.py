"""V/Line on Transport Victoria's feeds: the adapter, the look, the timetable read one shape at a
time. Every case is a measured finding or a decision of Lee's: sources/vline.py, operators/vline.py,
geometry.distill_stream. Run from the repo root: python -m unittest tests.test_vline_source
"""

import datetime as dt
import json
import os
import pathlib
import shutil
import sys
import tempfile
import unittest
import zipfile
from zoneinfo import ZoneInfo

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _load import load  # noqa: E402

from google.transit import gtfs_realtime_pb2 as pb  # noqa: E402
from saw_livetrack.gtfs import Fleet  # noqa: E402

src = load("sources.vline")
geometry = load("geometry")
operators = load("operators")
vl = load("operators.vline")
attributes = load("attributes")
base = load("sources.base")
projection = load("projection")

MEL = ZoneInfo("Australia/Melbourne")
START = "20261020"
ORIGIN = dt.datetime(2026, 10, 20, 12, tzinfo=MEL).timestamp() - 43200.0
TRIP = "01-ABY--10-T0-8605"
ROUTE = "aus:vic:vic-01-ABY:"
GEO = {
    "stops": {"A": [-37.8, 145.0], "B": [-37.0, 145.0], "C": [-36.0, 145.0], "D": [-35.0, 145.0]},
    "stop_names": {"A": "Southern Cross Station", "B": "Seymour Station", "C": "Benalla Station", "D": "Albury Station"},
    "route_names": {ROUTE: "Albury - Melbourne via Seymour"},
    # at 10:00, 11:00-11:14, 12:00, 13:00, seconds from the origin
    "stop_tables": {"t": [[1, "A", 36000, 36000], [2, "B", 39600, 40440], [3, "C", 43200, 43200], [4, "D", 46800, 46800]]},
    "trip_tables": {TRIP: "t"},
    "trains": {TRIP: ["L"]},
    "shapes": {"L": [[-37.8, 145.0], [-35.0, 145.0]]},
}
T = lambda h, m=0, s=0: ORIGIN + h * 3600 + m * 60 + s
HELD = base.HELD_SPEED_KEY


def positions(*vehicles):
    """Each: (trip, start, lat, lon, time[, route])."""
    f = pb.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    for i, row in enumerate(vehicles):
        trip, start, lat, lon, ts = row[:5]
        e = f.entity.add()
        e.id = str(i)
        e.vehicle.trip.trip_id = trip
        e.vehicle.trip.start_date = start
        e.vehicle.trip.route_id = row[5] if len(row) > 5 else ROUTE
        if lat is not None:
            e.vehicle.position.latitude = lat
            e.vehicle.position.longitude = lon
        if ts is not None:
            e.vehicle.timestamp = int(ts)
    return f


def update(*stops, trip=TRIP, start=START, relationship=None):
    """Each stop: (sequence, relationship, arrival delay)."""
    f = pb.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    e = f.entity.add()
    e.id = "u"
    u = e.trip_update
    u.trip.trip_id = trip
    u.trip.start_date = start
    if relationship is not None:
        u.trip.schedule_relationship = relationship
    for seq, rel, delay in stops:
        s = u.stop_time_update.add()
        s.stop_sequence = seq
        s.schedule_relationship = rel
        if delay is not None:
            s.arrival.delay = delay
    return f


def empty():
    f = pb.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    return f


# Along the line, -37.8 to -35.0: about 111 km a degree.
def row(lat=-37.4, ts=None, now=None, trip=TRIP, start=START):
    now = T(10, 30) if now is None else now
    return positions((trip, start, lat, 145.0, now - 60 if ts is None else ts))


def rt():
    return src.VLineRealtime()


class Identity(unittest.TestCase):
    def test_service_number(self):
        self.assertEqual(src.service_number(TRIP), "8605")
        self.assertEqual(src.service_number("01-GEL--3-T0-8786"), "8786")

    def test_no_number(self):
        for bad in ("", "01-ABY", "8605-x"):
            self.assertIsNone(src.service_number(bad), bad)

    def test_route_code(self):
        self.assertEqual(src.route_code(ROUTE), "ABY")
        self.assertEqual(src.route_code("aus:vic:vic-01-vPK:"), "vPK")

    def test_one_marker_a_run(self):
        snap = rt().parse(row(), None, T(10, 30), GEO)
        o = snap.observations[0]
        self.assertEqual((o.vehicle_id, o.train, o.trip_id, o.in_service, o.line, o.reported_course),
                         ("8605-20", "8605", "8605-20", True, None, None))
        self.assertEqual(snap.route_keys["8605-20"], TRIP)

    def test_same_trip_on_two_dates(self):
        f = positions((TRIP, START, -37.4, 145.0, T(10, 29)), (TRIP, "20261019", -36.0, 145.0, T(10, 29)))
        snap = rt().parse(f, None, T(10, 30), GEO)
        self.assertEqual(sorted(o.vehicle_id for o in snap.observations), ["8605-19", "8605-20"])

    def test_two_rows_one_run(self):
        f = positions((TRIP, START, -37.4, 145.0, T(10, 29)), (TRIP, START, -37.3, 145.0, T(10, 29)))
        snap = rt().parse(f, None, T(10, 30), GEO)
        self.assertEqual(len(snap.observations), 1)
        self.assertEqual(snap.skipped, {"duplicate": 1})

    def test_no_number_skipped(self):
        snap = rt().parse(positions(("X-Y", START, -37.4, 145.0, T(10, 29))), None, T(10, 30), GEO)
        self.assertEqual((snap.observations, snap.skipped), ([], {"no_number": 1}))

    def test_no_position_new_run(self):
        snap = rt().parse(positions((TRIP, START, None, None, T(10, 29))), None, T(10, 30), GEO)
        self.assertEqual((snap.observations, snap.skipped), ([], {"no_position": 1}))

    def test_none_is_an_outage_and_empty_is_not(self):
        self.assertIsNone(rt().parse(None, None, 0.0, GEO))
        snap = rt().parse(empty(), None, 0.0, GEO)
        self.assertEqual(snap.observations, [])

    def test_line_and_code(self):
        snap = rt().parse(row(), None, T(10, 30), GEO)
        self.assertEqual(snap.extras["8605-20"]["line_name"], "Albury - Melbourne via Seymour")
        self.assertEqual(snap.extras["8605-20"]["route_code"], "ABY")

    def test_no_timetable_yet_still_a_marker(self):
        snap = rt().parse(row(), None, T(10, 30), {})
        self.assertEqual(len(snap.observations), 1)
        self.assertNotIn("line_name", snap.extras["8605-20"])
        self.assertEqual(snap.stop_codes, {})

    def test_timetable_arriving_later_is_picked_up(self):
        r = rt()
        r.parse(row(), None, T(10, 30), {})
        snap = r.parse(row(now=T(10, 31)), None, T(10, 31), GEO)
        self.assertEqual(snap.stop_codes["8605-20"], "B")


class FirstSightAndFinished(unittest.TestCase):
    def test_old_at_first_sight_no_marker(self):
        snap = rt().parse(row(ts=T(10, 24, 59)), None, T(10, 30), GEO)
        self.assertEqual((snap.observations, snap.skipped), ([], {"stale_first_sight": 1}))

    def test_300_s_at_first_sight_is_a_marker(self):
        snap = rt().parse(row(ts=T(10, 25)), None, T(10, 30), GEO)
        self.assertEqual(len(snap.observations), 1)

    def test_old_after_first_sight_stays(self):
        r = rt()
        t = T(10, 30)
        r.parse(row(ts=t - 10), None, t, GEO)
        snap = r.parse(row(ts=t - 10), None, t + 900, GEO)
        self.assertEqual(len(snap.observations), 1)

    def test_finished_forecast_passed_and_fix_old(self):
        r = rt()
        t = T(12, 55)
        r.parse(row(lat=-35.1, ts=t - 10), None, t, GEO)
        snap = r.parse(row(lat=-35.1, ts=t - 10), None, T(13, 1), GEO)
        self.assertEqual((snap.observations, snap.skipped), ([], {"finished": 1}))
        self.assertEqual(r._runs, {})

    def test_the_ghost_stays_gone(self):
        r = rt()
        t = T(12, 55)
        r.parse(row(lat=-35.1, ts=t - 10), None, t, GEO)
        r.parse(row(lat=-35.1, ts=t - 10), None, T(13, 1), GEO)
        snap = r.parse(row(lat=-35.1, ts=t - 10), None, T(13, 2), GEO)
        self.assertEqual(snap.skipped, {"stale_first_sight": 1})

    def test_forecast_passed_with_a_fresh_fix_stays(self):
        snap = rt().parse(row(lat=-35.1, ts=T(13, 0, 30)), None, T(13, 1), GEO)
        self.assertEqual(len(snap.observations), 1)

    def test_forecast_passed_fix_exactly_300_s_stays(self):
        r = rt()
        r.parse(row(lat=-35.1, ts=T(12, 56)), None, T(12, 56, 10), GEO)
        snap = r.parse(row(lat=-35.1, ts=T(12, 56)), None, T(13, 1), GEO)
        self.assertEqual(len(snap.observations), 1)

    def test_old_fix_forecast_ahead_stays(self):
        r = rt()
        r.parse(row(lat=-36.0, ts=T(11, 0)), None, T(11, 0, 5), GEO)
        snap = r.parse(row(lat=-36.0, ts=T(11, 0)), None, T(11, 20), GEO)
        self.assertEqual(len(snap.observations), 1)

    def test_delay_moves_the_forecast(self):
        r = rt()
        r.parse(row(lat=-35.1, ts=T(12, 55)), None, T(12, 55, 5), GEO)
        late = update((4, 0, 3600))
        snap = r.parse(row(lat=-35.1, ts=T(12, 55)), late, T(13, 10), GEO)
        self.assertEqual(len(snap.observations), 1)


class Flips(unittest.TestCase):
    """Decision 5: 14 pairs on 4 trips, 33 to 254 km out and back."""

    def start(self):
        r = rt()
        r.parse(row(lat=-37.4, ts=T(10, 30)), None, T(10, 30, 5), GEO)
        return r

    def at(self, snap):
        o = snap.observations[0]
        return o.lat, o.observed_at.timestamp()

    def test_a_flip_is_refused_and_the_train_stays_on_its_fix(self):
        r = self.start()
        snap = r.parse(row(lat=-36.0, ts=T(10, 31)), None, T(10, 31, 5), GEO)
        self.assertEqual(snap.skipped, {"fix_refused": 1})
        self.assertAlmostEqual(self.at(snap)[0], -37.4, places=4)
        self.assertEqual(self.at(snap)[1], T(10, 30))

    def test_a_train_speed_is_accepted(self):
        r = self.start()
        # 0.03 degrees in 60 s: 55 m/s
        snap = r.parse(row(lat=-37.37, ts=T(10, 31)), None, T(10, 31, 5), GEO)
        self.assertEqual(snap.skipped, {})
        self.assertAlmostEqual(self.at(snap)[0], -37.37, places=4)

    def test_just_over_70_is_refused(self):
        r = self.start()
        # 0.04 degrees in 60 s: 74 m/s
        snap = r.parse(row(lat=-37.36, ts=T(10, 31)), None, T(10, 31, 5), GEO)
        self.assertEqual(snap.skipped, {"fix_refused": 1})

    def test_a_long_gap_lets_a_far_fix_through(self):
        r = self.start()
        # 1.4 degrees in 2 hours
        snap = r.parse(row(lat=-36.0, ts=T(12, 30)), None, T(12, 30, 5), GEO)
        self.assertEqual(snap.skipped, {})

    def test_same_place_later_moves_the_time(self):
        r = self.start()
        snap = r.parse(row(lat=-37.4, ts=T(10, 40)), None, T(10, 40, 5), GEO)
        self.assertEqual(self.at(snap)[1], T(10, 40))

    def test_same_place_older_keeps_the_time(self):
        r = self.start()
        snap = r.parse(row(lat=-37.4, ts=T(10, 20)), None, T(10, 30, 9), GEO)
        self.assertEqual(self.at(snap)[1], T(10, 30))

    def test_an_older_fix_elsewhere_is_refused(self):
        r = self.start()
        snap = r.parse(row(lat=-37.39, ts=T(10, 29)), None, T(10, 30, 9), GEO)
        self.assertEqual(snap.skipped, {"fix_refused": 1})
        self.assertEqual(self.at(snap)[1], T(10, 30))

    def test_the_same_clock_elsewhere_is_refused(self):
        r = self.start()
        snap = r.parse(row(lat=-37.39, ts=T(10, 30)), None, T(10, 30, 9), GEO)
        self.assertEqual(snap.skipped, {"fix_refused": 1})

    def far(self, r, first_min, last_min):
        """A wrong unit standing near Melbourne's far end, a fix a minute; the refused speed test
        passes only from about 30 minutes for this distance's limit, so the place is far enough."""
        snap = None
        for m in range(first_min, last_min + 1):
            snap = r.parse(positions((TRIP, START, -35.0, 145.0, T(10, m))), None, T(10, m, 5), GEO)
        return snap

    def test_thirty_minutes_agreeing_are_the_truth(self):
        r = self.start()
        snap = self.far(r, 31, 61)
        self.assertEqual(snap.skipped, {})
        self.assertAlmostEqual(self.at(snap)[0], -35.0, places=4)
        self.assertEqual(r._runs["8605-20"].cand, [])

    def test_a_minute_less_is_not_enough(self):
        r = self.start()
        snap = self.far(r, 31, 60)
        self.assertEqual(snap.skipped, {"fix_refused": 1})
        self.assertAlmostEqual(self.at(snap)[0], -37.4, places=4)

    def test_older_fixes_cast_no_vote(self):
        r = self.start()
        for m in range(0, 5):
            r.parse(row(lat=-37.5 + m * 0.01, ts=T(10, 20 + m)), None, T(10, 31, m), GEO)
        self.assertEqual(r._runs["8605-20"].cand, [])

    def test_after_an_older_fix_the_next_current_one_goes_on(self):
        r = self.start()
        r.parse(row(lat=-37.5, ts=T(10, 20)), None, T(10, 31), GEO)
        snap = r.parse(row(lat=-37.38, ts=T(10, 32)), None, T(10, 32, 5), GEO)
        self.assertEqual(snap.skipped, {})
        self.assertAlmostEqual(self.at(snap)[0], -37.38, places=4)

    def test_the_same_read_again_is_not_another_vote(self):
        r = self.start()
        for s in (5, 35, 55):
            snap = r.parse(row(lat=-36.0, ts=T(10, 31)), None, T(10, 31, s), GEO)
        self.assertEqual(snap.skipped, {"fix_refused": 1})
        self.assertEqual(len(r._runs["8605-20"].cand), 1)

    def test_disagreeing_starts_again(self):
        r = self.start()
        r.parse(row(lat=-36.0, ts=T(10, 31)), None, T(10, 31, 5), GEO)
        r.parse(row(lat=-35.0, ts=T(10, 32)), None, T(10, 32, 5), GEO)
        self.assertEqual(r._runs["8605-20"].cand, [(-35.0, 145.0, T(10, 32))])

    def test_the_same_place_clears_the_votes(self):
        r = self.start()
        r.parse(row(lat=-36.0, ts=T(10, 31)), None, T(10, 31, 5), GEO)
        r.parse(row(lat=-37.4, ts=T(10, 32)), None, T(10, 32, 5), GEO)
        self.assertEqual(r._runs["8605-20"].cand, [])

    def test_a_good_fix_clears_the_votes(self):
        r = self.start()
        r.parse(row(lat=-36.0, ts=T(10, 31)), None, T(10, 31, 5), GEO)
        r.parse(row(lat=-37.39, ts=T(10, 32)), None, T(10, 32, 5), GEO)
        self.assertEqual(r._runs["8605-20"].cand, [])

    def test_no_time_is_taken_as_it_comes(self):
        r = self.start()
        snap = r.parse(positions((TRIP, START, -36.0, 145.0, None)), None, T(10, 31), GEO)
        self.assertEqual(snap.skipped, {})


class Held(unittest.TestCase):
    """Decision 1: a missing row is a very stale fix."""

    def start(self, updates=None):
        r = rt()
        self.t0 = T(10, 30)
        r.parse(row(lat=-37.4, ts=self.t0), updates, self.t0 + 5, GEO)
        return r

    def test_a_trip_leaving_the_feed_is_still_reported(self):
        r = self.start()
        snap = r.parse(empty(), None, self.t0 + 60, GEO)
        o = snap.observations[0]
        self.assertEqual(o.vehicle_id, "8605-20")
        self.assertAlmostEqual(o.lat, -37.4, places=4)
        self.assertEqual(o.observed_at.timestamp(), self.t0)
        self.assertEqual(snap.route_keys["8605-20"], TRIP)
        self.assertEqual(snap.skipped, {"held": 1})

    def test_held_may_be_timed_and_a_fresh_row_may_not(self):
        r = self.start()
        fresh = r.parse(row(lat=-37.39, ts=self.t0 + 50), None, self.t0 + 55, GEO)
        self.assertNotIn(HELD, fresh.extras["8605-20"])
        snap = r.parse(empty(), None, self.t0 + 60, GEO)
        self.assertIn(HELD, snap.extras["8605-20"])
        self.assertIsNone(snap.extras["8605-20"][HELD])
        self.assertEqual(snap.extras["8605-20"][base.TIMED_AFTER_KEY], 120.0)
        self.assertNotIn(base.TIMED_AFTER_KEY, fresh.extras["8605-20"])

    def test_a_stale_row_is_timed_from_ten_minutes(self):
        r = self.start()
        at = r.parse(row(lat=-37.4, ts=self.t0), None, self.t0 + 600, GEO)
        self.assertNotIn(HELD, at.extras["8605-20"])
        past = r.parse(row(lat=-37.4, ts=self.t0), None, self.t0 + 601, GEO)
        self.assertIn(HELD, past.extras["8605-20"])
        self.assertNotIn(base.TIMED_AFTER_KEY, past.extras["8605-20"])

    def test_a_row_with_no_position_is_held(self):
        r = self.start()
        snap = r.parse(positions((TRIP, START, None, None, self.t0 + 60)), None, self.t0 + 60, GEO)
        self.assertEqual(snap.skipped, {"no_position": 1, "held": 1})
        self.assertEqual(len(snap.observations), 1)

    def test_the_row_coming_back_goes_on(self):
        r = self.start()
        r.parse(empty(), None, self.t0 + 60, GEO)
        snap = r.parse(row(lat=-37.3, ts=self.t0 + 900), None, self.t0 + 905, GEO)
        self.assertEqual(snap.skipped, {})
        self.assertAlmostEqual(snap.observations[0].lat, -37.3, places=4)

    def test_ends_when_the_terminal_forecast_has_passed(self):
        r = self.start()
        self.assertEqual(len(r.parse(empty(), None, T(12, 59), GEO).observations), 1)
        snap = r.parse(empty(), None, T(13, 0, 1), GEO)
        self.assertEqual((snap.observations, snap.skipped), ([], {"ended": 1}))
        self.assertEqual(r._runs, {})

    def test_the_delay_keeps_it_going(self):
        r = self.start()
        late = update((4, 0, 1800))
        self.assertEqual(len(r.parse(empty(), late, T(13, 20), GEO).observations), 1)
        self.assertEqual(r.parse(empty(), late, T(13, 31), GEO).observations, [])

    def test_ends_when_cancelled(self):
        r = self.start()
        snap = r.parse(empty(), update((4, 0, 0), relationship=pb.TripDescriptor.CANCELED), self.t0 + 60, GEO)
        self.assertEqual(snap.skipped, {"ended": 1})

    def test_a_cancelled_trip_with_a_row_is_drawn(self):
        r = self.start()
        snap = r.parse(row(lat=-37.39, ts=self.t0 + 50), update((4, 0, 0), relationship=src.CANCELED), self.t0 + 55, GEO)
        self.assertEqual(len(snap.observations), 1)

    def test_ends_after_three_minutes_of_good_answers_without_it(self):
        r = self.start()
        for s in (30, 60, 120, 209):
            self.assertEqual(len(r.parse(empty(), empty(), self.t0 + s, GEO).observations), 1, s)
        snap = r.parse(empty(), empty(), self.t0 + 210, GEO)
        self.assertEqual(snap.skipped, {"ended": 1})

    def test_an_answer_without_it_then_back(self):
        r = self.start()
        r.parse(empty(), empty(), self.t0 + 30, GEO)
        r.parse(empty(), update((4, 0, 0)), self.t0 + 200, GEO)
        self.assertIsNone(r._runs["8605-20"].gone_since)
        self.assertEqual(len(r.parse(empty(), empty(), self.t0 + 230, GEO).observations), 1)

    def test_the_clock_starts_at_the_first_answer_without_it(self):
        r = self.start()
        r.parse(empty(), empty(), self.t0 + 30, GEO)
        r.parse(empty(), empty(), self.t0 + 60, GEO)
        self.assertEqual(r._runs["8605-20"].gone_since, self.t0 + 30)

    def test_a_row_is_not_ended_by_it(self):
        r = self.start()
        r.parse(row(lat=-37.39, ts=self.t0 + 50), empty(), self.t0 + 55, GEO)
        snap = r.parse(row(lat=-37.38, ts=self.t0 + 500), empty(), self.t0 + 505, GEO)
        self.assertEqual(len(snap.observations), 1)

    def test_a_failed_answer_does_not_count(self):
        r = self.start()
        for s in (30, 60, 90, 120):
            self.assertEqual(len(r.parse(empty(), None, self.t0 + s, GEO).observations), 1)
        self.assertIsNone(r._runs["8605-20"].gone_since)

    def test_a_failed_answer_keeps_the_delay(self):
        r = self.start()
        r.parse(row(lat=-37.39, ts=self.t0 + 50), update((2, 0, 120)), self.t0 + 55, GEO)
        snap = r.parse(empty(), None, self.t0 + 500, GEO)
        self.assertEqual(snap.trip_delays["8605-20"], 120)

    def test_an_empty_update_keeps_the_delays(self):
        r = self.start(updates=update((4, 0, 1800)))
        r.parse(empty(), update(), self.t0 + 30, GEO)
        self.assertEqual(r._runs["8605-20"].delays, {4: 1800})

    def test_no_timetable_nothing_to_hold(self):
        r = rt()
        r.parse(row(ts=T(10, 29)), None, T(10, 30), {})
        snap = r.parse(empty(), None, T(10, 31), {})
        self.assertEqual((snap.observations, snap.skipped), ([], {"ended": 1}))

    def test_no_fix_time_nothing_to_time(self):
        r = rt()
        r.parse(positions((TRIP, START, -37.4, 145.0, None)), None, T(10, 30), GEO)
        snap = r.parse(empty(), None, T(10, 31), GEO)
        self.assertEqual(snap.skipped, {"ended": 1})

    def test_another_dates_update_is_not_this_runs(self):
        r = self.start()
        snap = r.parse(empty(), update((4, 0, 0), start="20261021", relationship=pb.TripDescriptor.CANCELED), self.t0 + 60, GEO)
        self.assertEqual(snap.skipped, {"held": 1})

    def test_a_row_keeps_its_timetable_when_the_new_copy_lacks_the_trip(self):
        r = self.start()
        geo = {**GEO, "trip_tables": {}, "stop_tables": {}}
        snap = r.parse(row(lat=-37.39, ts=self.t0 + 50), None, self.t0 + 55, geo)
        self.assertEqual(snap.stop_codes["8605-20"], "B")

    def test_a_table_with_no_times_ends(self):
        geo = {**GEO, "stop_tables": {"t": [[1, "A", None, None], [2, "B", None, None]]}}
        r = rt()
        r.parse(row(ts=T(10, 29)), None, T(10, 30), geo)
        self.assertEqual(r.parse(empty(), None, T(10, 31), geo).skipped, {"ended": 1})

    def test_holds_its_timetable_when_the_new_copy_lacks_the_trip(self):
        r = self.start()
        geo = {**GEO, "trip_tables": {}, "stop_tables": {}}
        snap = r.parse(empty(), None, self.t0 + 60, geo)
        self.assertEqual(snap.stop_codes["8605-20"], "B")

    def test_timetable_read_while_held(self):
        r = rt()
        r.parse(row(ts=T(10, 29)), None, T(10, 30), {})
        r._runs["8605-20"].rows = []
        snap = r.parse(empty(), None, T(10, 31), GEO)
        self.assertEqual(snap.stop_codes["8605-20"], "B")


OTHER = "01-GEL--1-T0-8701"


class FrozenFeed(unittest.TestCase):
    """Every train stopping at once: the rows count as no row, by the feed and not by a clock."""

    def two(self, a, b):
        return positions((TRIP, START, -37.4, 145.0, a), (OTHER, START, -38.0, 144.5, b))

    def start(self):
        r = rt()
        self.t0 = T(10, 30)
        r.parse(self.two(self.t0, self.t0), None, self.t0 + 5, GEO)
        return r

    def test_every_fix_old_is_frozen(self):
        snap = self.start().parse(self.two(self.t0, self.t0), None, self.t0 + 181, GEO)
        self.assertEqual(snap.skipped, {"feed_frozen": 1})
        e = snap.extras["8605-20"]
        self.assertIn(HELD, e)
        self.assertEqual(e[base.TIMED_AFTER_KEY], 120.0)
        self.assertEqual(len(snap.observations), 2)

    def test_at_180_s_not_yet(self):
        snap = self.start().parse(self.two(self.t0, self.t0), None, self.t0 + 180, GEO)
        self.assertEqual(snap.skipped, {})
        self.assertNotIn(HELD, snap.extras["8605-20"])

    def test_the_newest_fix_decides(self):
        snap = self.start().parse(self.two(self.t0, self.t0 + 100), None, self.t0 + 200, GEO)
        self.assertEqual(snap.skipped, {})
        self.assertNotIn(HELD, snap.extras["8605-20"])

    def test_one_row_is_not_a_feed(self):
        r = rt()
        t0 = T(10, 30)
        r.parse(row(ts=t0), None, t0 + 5, GEO)
        snap = r.parse(row(ts=t0), None, t0 + 300, GEO)
        self.assertEqual(snap.skipped, {})
        self.assertNotIn(HELD, snap.extras["8605-20"])

    def test_a_row_with_no_time_does_not_vote(self):
        f = positions((TRIP, START, -37.4, 145.0, T(10, 30)), (OTHER, START, -38.0, 144.5, None))
        self.assertFalse(src.VLineRealtime._feed_frozen(f, T(10, 40)))

    def test_a_row_with_no_position_does_not_vote(self):
        f = positions((TRIP, START, -37.4, 145.0, T(10, 30)), (OTHER, START, None, None, T(10, 40)))
        self.assertFalse(src.VLineRealtime._feed_frozen(f, T(10, 40)))
        g = positions((TRIP, START, -37.4, 145.0, T(10, 30)), (OTHER, START, -38.0, 144.5, T(10, 30)), ("01-ABY--1-T0-8607", START, None, None, T(10, 40)))
        self.assertTrue(src.VLineRealtime._feed_frozen(g, T(10, 40)))

    def test_empty_is_not_frozen(self):
        self.assertFalse(src.VLineRealtime._feed_frozen(empty(), T(10, 40)))

    def test_no_stall_is_said_of_a_frozen_train(self):
        r = rt()
        t0 = T(10, 0)
        r.parse(self.two(t0, t0), None, t0 + 5, GEO)
        r.parse(self.two(t0 + 500, t0 + 500), None, t0 + 505, GEO)
        snap = r.parse(self.two(t0 + 500, t0 + 500), None, t0 + 700, GEO)
        self.assertNotIn("stalled", snap.extras["8605-20"])

    def test_it_lifts_when_a_new_fix_comes(self):
        r = self.start()
        r.parse(self.two(self.t0, self.t0), None, self.t0 + 200, GEO)
        snap = r.parse(self.two(self.t0, self.t0 + 205), None, self.t0 + 210, GEO)
        self.assertEqual(snap.skipped, {})
        self.assertNotIn(base.TIMED_AFTER_KEY, snap.extras["8605-20"])

    def test_first_sight_and_finished_are_as_before(self):
        snap = rt().parse(self.two(T(10, 30), T(10, 30)), None, T(10, 40), GEO)
        self.assertEqual(snap.skipped, {"feed_frozen": 1, "stale_first_sight": 2})

    def test_a_frozen_row_is_timed_through_the_estimate(self):
        op = operators.OPERATORS["vline"]
        r, f, p = rt(), Fleet(**dict(op.fleet)), geometry.Projector(GEO)
        t0 = T(10, 30)
        path_through(r, f, p, op, self.two(t0 - 60, t0 - 60), None, t0 - 55)
        rec, _ = path_through(r, f, p, op, self.two(t0, t0), None, t0 + 5)
        before = rec["latitude"]
        path_through(r, f, p, op, self.two(t0, t0), None, t0 + 170)
        rec, snap = path_through(r, f, p, op, self.two(t0, t0), None, T(11, 0))
        self.assertAlmostEqual(rec["latitude"], -37.0, places=3)
        self.assertGreater(rec["latitude"], before)


class Stalled(unittest.TestCase):
    """Decision 7's rule, tfnsw's code; here, that it is not said of a train nobody can see."""

    def standing(self):
        r = rt()
        lat = -36.5
        r.parse(row(lat=lat, ts=T(10, 0)), None, T(10, 0, 5), GEO)
        return r, lat

    def test_standing_past_366_s_away_from_a_stop(self):
        r, lat = self.standing()
        snap = r.parse(row(lat=lat, ts=T(10, 6, 6)), None, T(10, 6, 10), GEO)
        self.assertTrue(snap.extras["8605-20"].get("stalled"))

    def test_not_yet(self):
        r, lat = self.standing()
        snap = r.parse(row(lat=lat, ts=T(10, 6, 5)), None, T(10, 6, 10), GEO)
        self.assertNotIn("stalled", snap.extras["8605-20"])

    def test_not_when_held(self):
        r, lat = self.standing()
        r.parse(row(lat=lat, ts=T(10, 7)), None, T(10, 7, 5), GEO)
        snap = r.parse(empty(), None, T(10, 8), GEO)
        self.assertNotIn("stalled", snap.extras["8605-20"])

    def test_not_when_stale(self):
        r, lat = self.standing()
        r.parse(row(lat=lat, ts=T(10, 7)), None, T(10, 7, 5), GEO)
        snap = r.parse(row(lat=lat, ts=T(10, 7)), None, T(10, 17, 1), GEO)
        self.assertNotIn("stalled", snap.extras["8605-20"])

    def test_state_goes_with_the_run(self):
        r = rt()
        r.parse(row(lat=-35.1, ts=T(12, 59)), None, T(12, 59, 5), GEO)
        r.parse(empty(), None, T(13, 1), GEO)
        self.assertEqual(r._still, {})


class NextStop(unittest.TestCase):
    """D5: the timetable plus the update's delay; the name as published."""

    def test_by_the_timetable(self):
        snap = rt().parse(row(), None, T(10, 30), GEO)
        self.assertEqual(snap.stop_codes["8605-20"], "B")
        self.assertEqual(snap.next_stops["8605-20"], ("Seymour Station", T(11, 0)))

    def test_no_update_says_no_delay(self):
        snap = rt().parse(row(), None, T(10, 30), GEO)
        self.assertEqual(snap.trip_delays, {})

    def test_the_update_moves_the_time(self):
        snap = rt().parse(row(), update((2, 0, 600)), T(10, 30), GEO)
        self.assertEqual(snap.next_stops["8605-20"], ("Seymour Station", T(11, 10)))
        self.assertEqual(snap.trip_delays["8605-20"], 600)

    def test_a_late_train_still_goes_to_the_stop_its_timetable_has_passed(self):
        snap = rt().parse(row(lat=-37.1, now=T(11, 20)), update((2, 0, 1800)), T(11, 20), GEO)
        self.assertEqual(snap.stop_codes["8605-20"], "B")

    def test_a_dwell_holds_the_stop(self):
        snap = rt().parse(row(lat=-37.0, now=T(11, 10)), None, T(11, 10), GEO)
        self.assertEqual(snap.stop_codes["8605-20"], "B")

    def test_then_the_next(self):
        snap = rt().parse(row(lat=-37.0, now=T(11, 15)), None, T(11, 15), GEO)
        self.assertEqual(snap.stop_codes["8605-20"], "C")

    def test_the_origin_is_never_next(self):
        snap = rt().parse(row(lat=-37.8, ts=T(9, 59)), None, T(9, 59, 30), GEO)
        self.assertEqual(snap.stop_codes["8605-20"], "B")

    def test_the_origins_delay_counts_for_the_next(self):
        snap = rt().parse(row(lat=-37.8, ts=T(9, 59)), update((1, 0, 300)), T(9, 59, 30), GEO)
        self.assertEqual(snap.next_stops["8605-20"][1], T(11, 5))

    def test_a_skipped_stop_is_never_next(self):
        snap = rt().parse(row(), update((2, 1, None), (3, 0, 0)), T(10, 30), GEO)
        self.assertEqual(snap.stop_codes["8605-20"], "C")

    def test_a_one_stop_trip_has_its_stop(self):
        geo = {**GEO, "stop_tables": {"t": [[1, "A", 39600, 39600]]}}
        snap = rt().parse(row(), None, T(10, 30), geo)
        self.assertEqual(snap.stop_codes["8605-20"], "A")

    def test_past_every_stop_no_next(self):
        snap = rt().parse(row(lat=-35.0, ts=T(13, 30)), None, T(13, 31), GEO)
        self.assertEqual(snap.stop_codes, {})

    def test_a_stop_with_no_name_aims_and_says_nothing(self):
        geo = {**GEO, "stop_names": {}}
        snap = rt().parse(row(), None, T(10, 30), geo)
        self.assertEqual(snap.stop_codes["8605-20"], "B")
        self.assertEqual(snap.next_stops, {})

    def test_seconds_from_a_service_day_past_midnight(self):
        geo = {**GEO, "stop_tables": {"t": [[1, "A", 90000, 90000], [2, "B", 93600, 93600]]}}
        when = ORIGIN + 90000
        snap = rt().parse(row(ts=when + 60), None, when + 90, geo)
        self.assertEqual(snap.next_stops["8605-20"], ("Seymour Station", ORIGIN + 93600))

    def test_a_bad_start_date_no_table(self):
        snap = rt().parse(row(start="bad"), None, T(10, 30), GEO)
        self.assertEqual(snap.stop_codes, {})

    def test_melbourne_time(self):
        self.assertEqual(rt().time_zone, "Australia/Melbourne")
        self.assertEqual(rt()._origin(START), ORIGIN)

    def test_the_zone_is_the_adapters(self):
        class Perth(src.VLineRealtime):
            time_zone = "Australia/Perth"
        self.assertEqual(Perth()._origin(START) - ORIGIN, 3 * 3600)
        # The library's runs read the adapter's zone too (saw-livetrack 0.2.38).
        self.assertEqual(Perth()._rows(TRIP, START, GEO)[0][2] - rt()._rows(TRIP, START, GEO)[0][2], 3 * 3600)

    def test_no_table_for_a_bad_date(self):
        self.assertEqual(rt()._rows(TRIP, "bad", GEO), [])


def path_through(r, fleet, projector, op, positions_, updates, now):
    snap = r.parse(positions_, updates, now, GEO)
    res = fleet.update(snap.observations, now, next_stops=snap.next_stops, trip_delays=snap.trip_delays)
    for vid, rec in res["vehicles"].items():
        rec.update({k: v for k, v in (snap.extras.get(vid) or {}).items() if k in base.EXTRA_KEYS})
    projection.apply(projector, snap, res, now, op.derive_speed, op.timed_without_fix, op.timed_after_s)
    return res["vehicles"].get("8605-20"), snap


class ThroughTheEstimate(unittest.TestCase):
    """The adapter, Fleet and projection.apply together, as the coordinator runs them."""

    def setUp(self):
        self.op = operators.OPERATORS["vline"]
        self.r, self.f, self.p = rt(), Fleet(**dict(self.op.fleet)), geometry.Projector(GEO)
        self.t0 = T(10, 30)
        path_through(self.r, self.f, self.p, self.op, row(lat=-37.50, ts=self.t0 - 60), None, self.t0 - 55)
        self.rec, _ = path_through(self.r, self.f, self.p, self.op, row(lat=-37.47, ts=self.t0), None, self.t0 + 5)

    def go(self, now, updates=None):
        return path_through(self.r, self.f, self.p, self.op, empty(), updates, now)

    def test_a_held_train_moves_on_at_its_speed(self):
        rec, _ = self.go(self.t0 + 120)
        self.assertEqual(rec["position_source"], "estimated")
        self.assertGreater(rec["latitude"], -37.47)
        self.assertAlmostEqual(rec["fix_latitude"], -37.47, places=4)

    def test_then_timed_to_the_stop(self):
        self.go(self.t0 + 590)
        rec, _ = self.go(self.t0 + 610)
        self.assertAlmostEqual(rec["latitude"], -37.0, delta=0.46)
        at = self.go(T(11, 0))[0]
        self.assertAlmostEqual(at["latitude"], -37.0, places=3)

    def test_on_to_the_next_stop(self):
        self.go(self.t0 + 610)
        self.go(T(11, 0))
        self.go(T(11, 14, 30))
        rec, _ = self.go(T(11, 40))
        self.assertGreater(rec["latitude"], -37.0)
        self.assertLess(rec["latitude"], -36.0)

    def test_gone_with_the_forecast(self):
        self.go(T(12, 59))
        rec, snap = self.go(T(13, 0, 1))
        self.assertIsNone(rec)
        self.assertEqual(snap.skipped, {"ended": 1})

    def test_a_frozen_row_does_the_same(self):
        self.go(self.t0 + 590)
        rec, _ = path_through(self.r, self.f, self.p, self.op, row(lat=-37.47, ts=self.t0), None, self.t0 + 650)
        self.assertEqual(rec["position_source"], "estimated")
        self.assertGreater(rec["latitude"], -37.47)

    def test_the_fix_time_stays_the_fixes(self):
        rec, _ = self.go(self.t0 + 120)
        self.assertEqual(dt.datetime.fromisoformat(rec["observed_at"]).timestamp(), self.t0)

    def test_no_key_for_the_map(self):
        rec, _ = self.go(self.t0 + 120)
        self.assertNotIn(HELD, rec)
        self.assertEqual(rec["route_code"], "ABY")
        self.assertNotIn("route_code", attributes.to_attributes({**rec, "marker_label": "8605"}, "vline"))


class ThePerRailroadHorizon(unittest.TestCase):
    """projection.apply: the horizon reaches the estimate, and None is the old 30 minutes."""

    def go(self, horizon, own=None):
        p = geometry.Projector(GEO)
        t0 = T(10, 30)
        snap = base.Snapshot(observations=[], route_keys={"x": TRIP}, stop_codes={"x": "B"},
                             next_stops={"x": ("Seymour Station", T(11, 0))}, extras={"x": {HELD: None}})
        o = base.Obs(vehicle_id="x", lat=-37.5, lon=145.0, observed_at=dt.datetime.fromtimestamp(t0, dt.timezone.utc),
                     in_service=True, train="8605", line=None, reported_course=None, trip_id="x")
        snap.observations.append(o)
        if own is not None:
            snap.extras["x"][base.TIMED_AFTER_KEY] = own
        out = []
        for age in (5, 700):
            rec = {"latitude": -37.5, "longitude": 145.0, "in_service": True}
            projection.apply(p, snap, {"vehicles": {"x": rec}}, t0 + age, True, True, horizon)
            out.append(rec["latitude"])
        return out

    def test_a_railroads_own(self):
        self.assertGreater(self.go(600.0)[1], -37.45)

    def test_none_is_the_default(self):
        self.assertAlmostEqual(self.go(None)[1], -37.5, places=3)

    def test_a_trains_own_wins(self):
        self.assertGreater(self.go(None, own=120.0)[1], -37.45)
        self.assertAlmostEqual(self.go(600.0, own=900.0)[1], -37.5, places=3)


def _along(km, lat0=-37.0, lon=145.0):
    return (lat0 + km / 111.195, lon)


class Unfold(unittest.TestCase):
    """The Albury line's fold: 0-10 forward, back to 5, forward to 20 over the same track."""

    def fold(self):
        out = [_along(k / 2) for k in range(0, 21)]        # 0 to 10
        out += [_along(k / 2) for k in range(19, 9, -1)]   # back to 5
        out += [_along(k / 2) for k in range(11, 41)]      # on to 20
        return out

    def length(self, line):
        return geometry.Route(line).length

    def test_a_fold_comes_out(self):
        line, km = geometry.unfold(self.fold())
        self.assertAlmostEqual(self.length(line), 20000, delta=400)
        self.assertAlmostEqual(km, 10.0, delta=0.4)

    def test_it_is_one_way_now(self):
        line, _ = geometry.unfold(self.fold())
        lats = [p[0] for p in line]
        self.assertEqual(lats, sorted(lats))

    def test_the_ends_stay(self):
        f = self.fold()
        line, _ = geometry.unfold(f)
        self.assertEqual((line[0], line[-1]), (f[0], f[-1]))

    def test_a_line_ending_where_it_folded_keeps_its_end(self):
        p = [_along(k / 2) for k in range(0, 21)] + [_along(k / 2) for k in range(19, 9, -1)]
        line, _ = geometry.unfold(p)
        self.assertEqual(line[-1], p[-1])

    def test_a_plain_line_is_left_alone(self):
        p = [_along(k) for k in range(30)]
        self.assertEqual(geometry.unfold(p), (p, 0.0))

    def test_under_a_kilometre_is_left_alone(self):
        p = [_along(k * 0.2) for k in range(5)] + [_along(0.6), _along(0.4)] + [_along(k * 0.2 + 0.6) for k in range(10)]
        self.assertEqual(geometry.unfold(p)[1], 0.0)

    def test_two_parallel_tracks_are_not_a_fold(self):
        p = [_along(k / 2) for k in range(21)] + [(_along(10)[0], 145.002)] + [(_along(k / 2)[0], 145.002) for k in range(19, -1, -1)]
        self.assertEqual(geometry.unfold(p)[1], 0.0)

    def test_a_stop_only_on_the_loop_keeps_it(self):
        # An out-and-back to a station: 0-10, a spur off sideways and back, on to 20.
        spur = [(_along(5)[0], 145.0 + k * 0.01) for k in range(0, 8)]
        p = [_along(k / 2) for k in range(0, 11)] + spur + spur[-2::-1] + [_along(k / 2) for k in range(11, 41)]
        self.assertEqual(geometry.unfold(p, [spur[-1]])[0], p)
        self.assertGreater(geometry.unfold(p)[1], 1.0)

    def test_stops_on_the_line_let_it_go(self):
        self.assertGreater(geometry.unfold(self.fold(), [_along(3), _along(7), _along(15)])[1], 9)

    def test_two_folds(self):
        one = self.fold()
        two = [(a, b + 0.5) for a, b in self.fold()]
        link = [(one[-1][0], 145.0 + k * 0.05) for k in range(1, 10)]
        line, km = geometry.unfold(one + link + two)
        self.assertAlmostEqual(km, 20.0, delta=0.8)

    def test_in_the_distill(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        path = os.path.join(d, "z.zip")
        rows = "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n" + "".join(f"X,{a},{b},{i}\n" for i, (a, b) in enumerate(self.fold()))
        write_zip(path, **{"shapes.txt": rows, "trips.txt": "route_id,service_id,trip_id,shape_id\nR1,S,T1,X\n"})
        out = geometry.distill_stream(path)
        line = out["shapes"][out["trains"]["T1"][0]]
        self.assertAlmostEqual(geometry.Route([tuple(p) for p in line]).length, 20000, delta=400)
        self.assertAlmostEqual(out["folds_cut_km"][out["trains"]["T1"][0]], 10.0, delta=0.4)

    def test_the_trips_own_stop_decides_in_the_distill(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        path = os.path.join(d, "z.zip")
        spur = [(_along(5)[0], 145.0 + k * 0.01) for k in range(0, 8)]
        p = [_along(k / 2) for k in range(0, 11)] + spur + spur[-2::-1] + [_along(k / 2) for k in range(11, 41)]
        rows = "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n" + "".join(f"X,{a},{b},{i}\n" for i, (a, b) in enumerate(p))
        stops = f"stop_id,stop_name,stop_lat,stop_lon,parent_station\nA,End,{spur[-1][0]},{spur[-1][1]},\n"
        times = "trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type\nT1,08:00:00,08:00:00,A,1,0,0\n"
        write_zip(path, **{"shapes.txt": rows, "trips.txt": "route_id,service_id,trip_id,shape_id\nR1,S,T1,X\n", "stops.txt": stops, "stop_times.txt": times})
        out = geometry.distill_stream(path)
        self.assertEqual(out["folds_cut_km"], {})


class Horizon(unittest.TestCase):
    def geo(self):
        return {"stops": {"B": [-37.0, 145.0]}, "trains": {"T": ["L"]}, "shapes": {"L": [[-37.8, 145.0], [-35.0, 145.0]]}}

    def est(self, age, **kw):
        p = geometry.Projector(self.geo())
        p.estimate("x", "T", (-37.5, 145.0), 1000.0, "B", 0.0, 1001.0)
        return p.estimate("x", "T", (-37.5, 145.0), 1000.0, "B", 0.0, 1000.0 + age, eta=1000.0 + age + 1000, timed=True, **kw)

    def test_by_default_30_minutes(self):
        self.assertAlmostEqual(self.est(1800)[0], -37.5, places=4)
        self.assertGreater(self.est(1801)[0], -37.5)

    def test_a_railroads_own(self):
        self.assertAlmostEqual(self.est(600, horizon=600.0)[0], -37.5, places=4)
        self.assertGreater(self.est(601, horizon=600.0)[0], -37.5)

    def test_it_caps_the_speed_rule_too(self):
        p = geometry.Projector(self.geo())
        a = p.estimate("x", "T", (-37.5, 145.0), 1000.0, "B", 10.0, 1000.0 + 700, horizon=600.0)
        self.assertAlmostEqual((a[0] + 37.5) * 111195, 6000, delta=20)


class Look(unittest.TestCase):
    def test_leaving_melbourne(self):
        k = vl.vline_styling("8605")
        self.assertEqual((k["marker_color"], k["marker_ring_color"], k["marker_label_color"]), ("#8F1A95", "#FBC627", "#FBC627"))
        self.assertEqual((k["marker_arrow_color"], k["marker_arrow_outline_color"]), ("#8F1A95", "#FBC627"))

    def test_going_to_melbourne(self):
        k = vl.vline_styling("8610")
        self.assertEqual((k["marker_color"], k["marker_ring_color"], k["marker_label_color"]), ("#FBC627", "#8F1A95", "#8F1A95"))
        self.assertEqual((k["marker_arrow_color"], k["marker_arrow_outline_color"]), ("#FBC627", "#8F1A95"))

    def test_unknown_is_purple(self):
        for number in (None, "", "X1"):
            self.assertEqual(vl.vline_styling(number)["marker_color"], "#8F1A95")

    def test_ring_and_no_label_outline(self):
        k = vl.vline_styling("8605")
        self.assertEqual(k["marker_ring_width"], vl.RING_WIDTH)
        self.assertEqual(k["marker_label_outline_color"], "none")

    def test_through_the_operator(self):
        self.assertEqual(operators.OPERATORS["vline"].marker_keys({"train": "8610"})["marker_color"], "#FBC627")


class Lateness(unittest.TestCase):
    def test_short(self):
        for code in ("GEL", "BAT", "BGO", "SER", "TRN", "vPK"):
            self.assertEqual(operators.OPERATORS["vline"].lateness_for({"route_code": code}),
                             {"late_threshold_min": 6, "very_late_threshold_min": 30}, code)

    def test_long(self):
        for code in ("WBL", "ART", "MBY", "SWL", "ECH", "ABY", "SNH", "BDE"):
            self.assertEqual(operators.OPERATORS["vline"].lateness_for({"route_code": code}),
                             {"late_threshold_min": 11, "very_late_threshold_min": 30}, code)

    def test_a_new_line_is_short(self):
        self.assertEqual(vl.vline_lateness({"route_code": "NEW"})["late_threshold_min"], 6)
        self.assertEqual(vl.vline_lateness({})["late_threshold_min"], 6)

    def test_other_railroads_are_as_before(self):
        self.assertEqual(operators.OPERATORS["nsw_trainlink"].lateness_for({"train": "31"})["late_threshold_min"], 11)


class OperatorSettings(unittest.TestCase):
    def test_settings(self):
        op = operators.OPERATORS["vline"]
        self.assertEqual((op.id, op.name, op.short, op.regions, op.source, op.scan_interval_s),
                         ("vline", "V/Line", "V/Line", ("AU",), operators.SOURCE_TRANSPORT_VIC, 30))
        self.assertEqual(op.source_options, {"consumer": "intercity"})
        self.assertTrue(op.derive_speed and op.needs_key and op.gtfs_from_source and op.gtfs_stream and op.timed_without_fix)
        self.assertEqual(op.timed_after_s, 600.0)
        self.assertIsNone(op.gtfs_url)
        self.assertEqual(op.attribution, "Data: Transport Victoria (opendata.transport.vic.gov.au), CC BY 4.0")
        self.assertTrue(op.terms_url and op.key_url)

    def test_the_others_keep_their_horizon_and_their_distill(self):
        for op in operators.OPERATORS.values():
            if op.id != "vline":
                # Renfe's regionals have their own: a station's departure, else 120 s (Intercity SSOT 8.7).
                if op.id not in ("renfe_regionals_catalunya", "renfe_spain"):
                    self.assertIsNone(op.timed_after_s, op.id)
                self.assertFalse(op.gtfs_stream, op.id)

    def test_constants(self):
        self.assertEqual((src.MAX_FIRST_AGE_S, src.FINISHED_AGE_S, src.TIMED_AFTER_S, src.MAX_FIX_MS, src.CONFIRM_S, src.UPDATES_GONE_S, src.ROW_GONE_TIMED_S, src.FROZEN_FEED_S, src.FROZEN_FEED_ROWS),
                         (300.0, 300.0, 600.0, 70.0, 1800.0, 180.0, 120.0, 180.0, 2))

    def test_entity_key_goes_to_the_map_only_as_allowed(self):
        self.assertIn("route_code", base.EXTRA_KEYS)
        self.assertIn("route_code", base.RECORD_ONLY_KEYS)


ROUTES = ("route_id,route_short_name,route_long_name,route_type\n"
          "R1,Seymour,Albury - Melbourne   via  Seymour,2\nR2,,,2\n")
TRIPS = ("route_id,service_id,trip_id,shape_id\n"
         "R1,S,T1,X\nR1,S,T2,X2\nR1,S,T3,Y\nR1,S,T4,NOPE\nR1,S,T5,\n")
STOP_TIMES = ("trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type\n"
              "T1,25:10:00,25:24:00,B,2,0,0\n"       # out of order
              "T1,08:00:00,08:00:00,A,1,0,1\n"
              "T1,26:00:00,26:00:00,U,3,1,1\n"       # no rider stops here
              "T2,08:00:00,08:00:00,A,1,0,1\n"       # T1's table
              "T2,25:10:00,25:24:00,B,2,0,0\n"
              "T3,09:00:00,09:00:00,A,1,0,0\n")
STOPS = ("stop_id,stop_name,stop_lat,stop_lon,parent_station\n"
         "A,Southern Cross Station,-37.8,145.0,P\n"
         "B,Seymour Station,-37.0,145.0,\n"
         "U,Unused Station,-36.0,145.0,\n"
         "P,Parent Name,-37.8,145.0,\n")
SHAPES = ("shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n"
          "X,-37.8,145.0,1\nX,-37.0,145.0,2\n"
          "X2,-37.8,145.0,1\nX2,-37.0,145.0,2\n"     # the same line
          "Y,-37.0,145.0,1\nY,-37.8,145.0,2\n"       # the same line the other way
          "UNUSED,-30.0,145.0,1\nUNUSED,-31.0,145.0,2\n"
          "ONE,-30.0,145.0,1\n")


def write_zip(path, **over):
    files = {"routes.txt": ROUTES, "trips.txt": TRIPS, "stop_times.txt": STOP_TIMES, "stops.txt": STOPS, "shapes.txt": SHAPES}
    files.update(over)
    with zipfile.ZipFile(path, "w") as z:
        for n, t in files.items():
            # A fixed time: a fixture's bytes must not hold when it was made.
            z.writestr(zipfile.ZipInfo(n, date_time=(2026, 1, 1, 0, 0, 0)), t)


class DistillStream(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.path = os.path.join(self.dir, "z.zip")
        write_zip(self.path)
        self.d = geometry.distill_stream(self.path)

    def again(self, **over):
        write_zip(self.path, **over)
        return geometry.distill_stream(self.path)

    def test_marks_itself(self):
        self.assertEqual(self.d["v"], geometry.GEOMETRY_VERSION)
        self.assertTrue(self.d["stable_lines"])

    def test_identical_lines_merge(self):
        self.assertEqual(self.d["trains"]["T1"], self.d["trains"]["T2"])

    def test_lines_the_same_once_simplified_merge(self):
        rows = ("shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n"
                "X,-37.8,145.0,1\nX,-37.4,145.00001,2\nX,-37.0,145.0,3\n"
                "X2,-37.8,145.0,1\nX2,-37.4,145.00002,2\nX2,-37.0,145.0,3\n")
        d = self.again(**{"shapes.txt": rows, "trips.txt": "route_id,service_id,trip_id,shape_id\nR1,S,T1,X\nR1,S,T2,X2\n"})
        self.assertEqual(d["trains"]["T1"], d["trains"]["T2"])
        self.assertEqual(len(d["shapes"]), 1)

    def test_the_other_way_is_another_line(self):
        self.assertNotEqual(self.d["trains"]["T1"], self.d["trains"]["T3"])
        self.assertEqual(len(self.d["shapes"]), 2)

    def test_points_in_order(self):
        self.assertEqual(self.d["shapes"][self.d["trains"]["T1"][0]], [[-37.8, 145.0], [-37.0, 145.0]])
        self.assertEqual(self.d["shapes"][self.d["trains"]["T3"][0]], [[-37.0, 145.0], [-37.8, 145.0]])

    def test_unused_shape_and_one_point_are_no_line(self):
        self.assertNotIn([[-30.0, 145.0], [-31.0, 145.0]], list(self.d["shapes"].values()))

    def test_a_wanted_shape_of_one_point_is_no_line(self):
        rows = "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\nX,-37.8,145.0,1\nY,-37.0,145.0,1\nY,-37.8,145.0,2\n"
        d = self.again(**{"shapes.txt": rows})
        self.assertNotIn("T1", d["trains"])
        self.assertIn("T3", d["trains"])

    def test_trip_without_a_line_has_no_entry(self):
        for t in ("T4", "T5"):
            self.assertNotIn(t, self.d["trains"])

    def test_simplified(self):
        rows = "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\nX,-37.8,145.0,1\nX,-37.4,145.00001,2\nX,-37.0,145.0,3\n"
        d = self.again(**{"shapes.txt": rows, "trips.txt": "route_id,service_id,trip_id,shape_id\nR1,S,T1,X\n"})
        self.assertEqual(len(d["shapes"][d["trains"]["T1"][0]]), 2)

    def test_a_points_sequence_decides_not_its_place(self):
        rows = "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\nX,-37.0,145.0,2\nX,-37.8,145.0,1\n"
        d = self.again(**{"shapes.txt": rows, "trips.txt": "route_id,service_id,trip_id,shape_id\nR1,S,T1,X\n"})
        self.assertEqual(d["shapes"][d["trains"]["T1"][0]][0], [-37.8, 145.0])

    def test_a_shape_met_twice_raises(self):
        rows = ("shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n"
                "X,-37.8,145.0,1\nX,-37.0,145.0,2\nY,-37.0,145.0,1\nY,-37.8,145.0,2\nX,-36.0,145.0,3\n")
        with self.assertRaises(ValueError):
            self.again(**{"shapes.txt": rows})

    def test_the_last_shape_is_kept(self):
        rows = "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\nUNUSED,-30.0,145.0,1\nUNUSED,-31.0,145.0,2\nX,-37.8,145.0,1\nX,-37.0,145.0,2\n"
        d = self.again(**{"shapes.txt": rows})
        self.assertIn("T1", d["trains"])

    def test_a_line_keeps_its_id_across_copies(self):
        d = self.again(**{"trips.txt": "route_id,service_id,trip_id,shape_id\nR1,S,OTHER,X\n",
                          "shapes.txt": "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\nX,-37.8,145.0,1\nX,-37.0,145.0,2\n"})
        self.assertEqual(d["trains"]["OTHER"], self.d["trains"]["T1"])

    def test_stop_table_in_order_seconds_past_midnight(self):
        table = self.d["stop_tables"][self.d["trip_tables"]["T1"]]
        self.assertEqual(table, [[1, "A", 28800, 28800], [2, "B", 90600, 91440]])

    def test_a_stop_no_rider_uses_is_left_out(self):
        self.assertNotIn("U", self.d["stops"])
        self.assertNotIn("U", self.d["stop_names"])

    def test_identical_tables_merge(self):
        self.assertEqual(self.d["trip_tables"]["T1"], self.d["trip_tables"]["T2"])
        self.assertEqual(len(self.d["stop_tables"]), 2)

    def test_a_trip_met_twice_goes_on(self):
        rows = ("trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type\n"
                "T1,08:00:00,08:00:00,A,1,0,0\nT3,09:00:00,09:00:00,A,1,0,0\nT1,09:00:00,09:00:00,B,2,0,0\n")
        d = self.again(**{"stop_times.txt": rows})
        self.assertEqual([r[0] for r in d["stop_tables"][d["trip_tables"]["T1"]]], [1, 2])

    def test_the_last_trip_is_kept(self):
        self.assertIn("T3", self.d["trip_tables"])

    def test_no_times_are_none(self):
        rows = "trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type\nT1,,,A,1,0,0\n"
        d = self.again(**{"stop_times.txt": rows})
        self.assertEqual(d["stop_tables"][d["trip_tables"]["T1"]], [[1, "A", None, None]])

    def test_stop_names_as_published(self):
        self.assertEqual(self.d["stop_names"]["A"], "Southern Cross Station")

    def test_stop_with_no_place_or_name(self):
        rows = "stop_id,stop_name,stop_lat,stop_lon,parent_station\nA,,,,\nB,Seymour Station,-37.0,145.0,\n"
        d = self.again(**{"stops.txt": rows})
        self.assertNotIn("A", d["stops"])
        self.assertNotIn("A", d["stop_names"])

    def test_route_names_tidied(self):
        self.assertEqual(self.d["route_names"]["R1"], "Albury - Melbourne via Seymour")

    def test_route_name_falls_back(self):
        d = self.again(**{"routes.txt": "route_id,route_short_name,route_long_name,route_type\nR1,Seymour,,2\n"})
        self.assertEqual(d["route_names"]["R1"], "Seymour")

    def test_json_and_a_projector_can_read_it(self):
        d = json.loads(json.dumps(self.d))
        p = geometry.Projector(d)
        self.assertIsNotNone(p.estimate("x", "T1", (-37.5, 145.0), 100.0, "B", 0.0, 110.0))

    def test_a_file_on_disk_is_all_it_wants(self):
        with self.assertRaises(FileNotFoundError):
            geometry.distill_stream(os.path.join(self.dir, "nope.zip"))


class Adopt(unittest.TestCase):
    def pair(self, stable=True, shapes=None):
        old = {"stable_lines": stable, "trains": {"T": ["L"]}, "shapes": {"L": [[-37.8, 145.0], [-35.0, 145.0]]}, "stops": {}}
        new = {"stable_lines": stable, "trains": {}, "shapes": {"L": [[-37.8, 145.0], [-35.0, 145.0]]} if shapes is None else shapes, "stops": {}}
        a = geometry.Projector(old)
        a.estimate("x", "T", (-37.5, 145.0), 100.0, None, 0.0, 110.0)
        b = geometry.Projector(new)
        b.adopt(a)
        return a, b

    def test_goes_on_with_a_trip_the_new_copy_lacks(self):
        _, b = self.pair()
        self.assertIn("x", b._state)
        self.assertIsNotNone(b.estimate("x", "T", (-37.4, 145.0), 200.0, None, 0.0, 210.0))

    def test_a_line_that_has_gone_starts_again(self):
        _, b = self.pair(shapes={"M": [[-37.8, 145.0], [-35.0, 145.0]]})
        self.assertEqual(b._state, {})

    def test_only_with_hashed_lines(self):
        _, b = self.pair(stable=False)
        self.assertEqual(b._state, {})

    def test_both_copies_must_be(self):
        a, _ = self.pair()
        c = geometry.Projector({"trains": {}, "shapes": {"L": [[-37.8, 145.0], [-35.0, 145.0]]}, "stops": {}})
        c.adopt(a)
        self.assertEqual(c._state, {})
        old = geometry.Projector({"trains": {"T": ["L"]}, "shapes": {"L": [[-37.8, 145.0], [-35.0, 145.0]]}, "stops": {}})
        old.estimate("x", "T", (-37.5, 145.0), 100.0, None, 0.0, 110.0)
        d = geometry.Projector({"stable_lines": True, "trains": {}, "shapes": {"L": [[-37.8, 145.0], [-35.0, 145.0]]}, "stops": {}})
        d.adopt(old)
        self.assertEqual(d._state, {})


class ClientAdapters(unittest.TestCase):
    def test_read_asks_for_this_consumers_version(self):
        class Client:
            def for_consumer(self, consumer):
                return consumer, "U"

            def static_version(self, consumer):
                return "V" + consumer
        self.assertEqual(src.read(Client(), "intercity"), ("intercity", "U", "Vintercity"))

    def test_static_view(self):
        class Client:
            def static_version(self, consumer):
                return "V" + consumer

            def static_path(self, consumer):
                return "P" + consumer
        view = src.StaticView(Client(), "intercity")
        self.assertEqual((view.static_version(), view.static_path()), ("Vintercity", "Pintercity"))


class CheckKey(unittest.TestCase):
    def setUp(self):
        self.client = src.TransportVicClient
        self.addCleanup(setattr, src, "TransportVicClient", self.client)

    def answer(self, exc):
        seen = {}

        class Fake:
            def __init__(self, consumers):
                seen.update(consumers)

            def for_consumer(self, consumer):
                if exc:
                    raise exc("x")
                return None, None
        src.TransportVicClient = Fake
        return seen

    def test_ok(self):
        seen = self.answer(None)
        self.assertIsNone(src.check_key("intercity", "k"))
        self.assertEqual(seen, {"intercity": "k"})

    def test_refused(self):
        self.answer(src.KeyRefused)
        self.assertEqual(src.check_key("intercity", "k"), "invalid_key")

    def test_no_answer(self):
        self.answer(src.KeyedError)
        self.assertEqual(src.check_key("intercity", "k"), "cannot_connect")


# The trip-id fallback (2026-11-05, Lee 21:34): the live feed named Friday's trips `--1-` where the
# timetable has `--5-` (bin\ltir_vl_tripids.txt). START, 2026-10-20, is a Tuesday.
LIVE = "01-ABY--1-T0-8605"
TWIN = "01-ABY--5-T0-8605"
SAT = "01-ABY--6-T0-8605"
WEEKDAYS = ["1111100", "20261001", "20261231", [], []]
SATURDAYS = ["0000010", "20261001", "20261231", [], []]


def geo_fb(services=None, **over):
    g = dict(GEO)
    g["trip_tables"] = {TWIN: "t", SAT: "t"}
    g["trains"] = {TWIN: ["L"], SAT: ["L"]}
    g["trip_services"] = {TWIN: "WK", SAT: "SA"}
    g["services"] = services or {"WK": WEEKDAYS, "SA": SATURDAYS}
    g.update(over)
    return g


class TripIdFallback(unittest.TestCase):
    def test_a_live_id_the_timetable_lacks_takes_the_one_running_twin(self):
        snap = rt().parse(row(trip=LIVE), None, T(10, 30), geo_fb())
        self.assertEqual(snap.stop_codes["8605-20"], "B")
        self.assertEqual(snap.route_keys["8605-20"], TWIN)
        self.assertEqual(snap.next_stops["8605-20"][0], "Seymour Station")

    def test_the_update_is_still_matched_by_the_live_id(self):
        snap = rt().parse(row(trip=LIVE), update((2, 0, 300), trip=LIVE), T(10, 30), geo_fb())
        self.assertEqual(snap.trip_delays["8605-20"], 300)

    def test_an_update_under_the_twins_id_is_not_this_run(self):
        snap = rt().parse(row(trip=LIVE), update((2, 0, 300), trip=TWIN), T(10, 30), geo_fb())
        self.assertNotIn("8605-20", snap.trip_delays)

    def test_two_running_that_day_is_none(self):
        snap = rt().parse(row(trip=LIVE), None, T(10, 30), geo_fb({"WK": WEEKDAYS, "SA": WEEKDAYS}))
        self.assertEqual(snap.stop_codes, {})
        self.assertEqual(snap.route_keys["8605-20"], LIVE)

    def test_none_running_that_day_is_none(self):
        snap = rt().parse(row(trip=LIVE), None, T(10, 30), geo_fb({"WK": SATURDAYS, "SA": SATURDAYS[:1] + ["20261101", "20261231", [], []]}))
        self.assertEqual(snap.stop_codes, {})

    def test_another_line_is_never_a_twin(self):
        snap = rt().parse(row(trip="01-GEL--1-T0-8605"), None, T(10, 30), geo_fb())
        self.assertEqual(snap.stop_codes, {})

    def test_another_number_is_never_a_twin(self):
        snap = rt().parse(row(trip="01-ABY--1-T0-8607"), None, T(10, 30), geo_fb())
        self.assertEqual(snap.stop_codes, {})

    def test_the_exact_id_wins_whatever_its_calendar(self):
        snap = rt().parse(row(trip=SAT), None, T(10, 30), geo_fb())
        self.assertEqual(snap.route_keys["8605-20"], SAT)
        self.assertEqual(snap.stop_codes["8605-20"], "B")

    def test_a_removed_date_is_not_run(self):
        wk = ["1111100", "20261001", "20261231", [], ["20261020"]]
        snap = rt().parse(row(trip=LIVE), None, T(10, 30), geo_fb({"WK": wk, "SA": SATURDAYS}))
        self.assertEqual(snap.stop_codes, {})

    def test_an_added_date_is_run(self):
        wk = ["1111100", "20261001", "20261231", [], ["20261020"]]
        sa = ["0000010", "20261001", "20261231", ["20261020"], []]
        snap = rt().parse(row(trip=LIVE), None, T(10, 30), geo_fb({"WK": wk, "SA": sa}))
        self.assertEqual(snap.route_keys["8605-20"], SAT)

    def test_a_twin_without_a_stop_table_is_not_one(self):
        # Both run on the day; only SAT has a table, so SAT is the one (mutation, 2026-11-05).
        g = geo_fb({"WK": WEEKDAYS, "SA": WEEKDAYS})
        g["trip_tables"] = {SAT: "t"}
        snap = rt().parse(row(trip=LIVE), None, T(10, 30), g)
        self.assertEqual(snap.route_keys["8605-20"], SAT)
        self.assertEqual(snap.stop_codes["8605-20"], "B")

    def test_an_old_copy_without_calendars_finds_none(self):
        g = geo_fb()
        del g["trip_services"], g["services"]
        snap = rt().parse(row(trip=LIVE), None, T(10, 30), g)
        self.assertEqual(snap.stop_codes, {})
        self.assertEqual(snap.route_keys["8605-20"], LIVE)

    def test_a_timetable_arriving_later_is_used_for_a_held_run(self):
        r = rt()
        r.parse(row(trip=LIVE), None, T(10, 30), {})
        snap = r.parse(empty(), update((2, 0, 60), trip=LIVE), T(10, 31), geo_fb())
        self.assertEqual(snap.skipped.get("held"), 1)
        self.assertEqual(snap.stop_codes["8605-20"], "B")
        self.assertEqual(snap.route_keys["8605-20"], TWIN)

    def test_a_new_copy_rebuilds_the_index(self):
        r = rt()
        self.assertEqual(r._table_id(LIVE, START, geo_fb()), TWIN)
        g = geo_fb()
        g["trip_tables"] = {"01-ABY--7-T0-8605": "t"}
        g["trip_services"] = {"01-ABY--7-T0-8605": "WK"}
        self.assertEqual(r._table_id(LIVE, START, g), "01-ABY--7-T0-8605")

    def test_line_prefix(self):
        self.assertEqual(src.line_prefix(LIVE), "01-ABY")
        for bad in ("", "8605", "--1-T0-8605"):
            self.assertIsNone(src.line_prefix(bad), bad)


class ServiceRuns(unittest.TestCase):
    S = {"WK": ["1111100", "20261001", "20261231", ["20261025"], ["20261021"]],
         "ONLY": ["0000000", "", "", ["20261101"], []]}

    def test_a_weekday_in_range(self):
        self.assertTrue(geometry.service_runs(self.S, "WK", "20261020"))

    def test_a_weekend_day(self):
        self.assertFalse(geometry.service_runs(self.S, "WK", "20261024"))

    def test_each_weekday_reads_its_own_bit(self):
        # 2026-10-19 is a Monday. One service a day: each runs on its own day only (mutation, 2026-11-05).
        days = ["2026101%d" % d for d in range(9, 10)] + ["202610%d" % d for d in range(20, 26)]
        for i in range(7):
            s = {"D": ["".join("1" if j == i else "0" for j in range(7)), "20261001", "20261231", [], []]}
            self.assertEqual([geometry.service_runs(s, "D", d) for d in days], [j == i for j in range(7)], i)

    def test_out_of_range(self):
        self.assertFalse(geometry.service_runs(self.S, "WK", "20260930"))
        self.assertFalse(geometry.service_runs(self.S, "WK", "20270101"))

    def test_the_range_is_inclusive(self):
        self.assertTrue(geometry.service_runs(self.S, "WK", "20261001"))
        self.assertTrue(geometry.service_runs(self.S, "WK", "20261231"))

    def test_added_beats_the_weekday(self):
        self.assertTrue(geometry.service_runs(self.S, "WK", "20261025"))

    def test_removed_beats_the_weekday(self):
        self.assertFalse(geometry.service_runs(self.S, "WK", "20261021"))

    def test_a_service_only_in_calendar_dates(self):
        self.assertTrue(geometry.service_runs(self.S, "ONLY", "20261101"))
        self.assertFalse(geometry.service_runs(self.S, "ONLY", "20261102"))

    def test_unknown_or_bad(self):
        self.assertFalse(geometry.service_runs(self.S, "NOPE", "20261020"))
        self.assertFalse(geometry.service_runs(self.S, None, "20261020"))
        self.assertFalse(geometry.service_runs(None, "WK", "20261020"))
        self.assertFalse(geometry.service_runs(self.S, "WK", "2026-10-20"))


CALENDAR = ("service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n"
            "S,1,1,1,1,1,0,0,20261001,20261231\n")
CALENDAR_DATES = ("service_id,date,exception_type\n"
                  "S,20261025,1\nS,20261021,2\nX,20261101,1\nS,20261102,9\n")


class DistillCalendars(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.path = os.path.join(self.dir, "z.zip")

    def distill(self, **over):
        write_zip(self.path, **over)
        return geometry.distill_stream(self.path)

    def test_stream_version_and_each_trips_service(self):
        d = self.distill(**{"calendar.txt": CALENDAR, "calendar_dates.txt": CALENDAR_DATES})
        self.assertEqual(d["stream_v"], geometry.STREAM_VERSION)
        self.assertEqual(d["trip_services"], {"T1": "S", "T2": "S", "T3": "S", "T4": "S", "T5": "S"})

    def test_calendars(self):
        d = self.distill(**{"calendar.txt": CALENDAR, "calendar_dates.txt": CALENDAR_DATES})
        self.assertEqual(d["services"], {"S": ["1111100", "20261001", "20261231", ["20261025"], ["20261021"]],
                                         "X": ["0000000", "", "", ["20261101"], []]})

    def test_no_calendar_files(self):
        d = self.distill()
        self.assertEqual(d["services"], {})
        self.assertEqual(d["trip_services"]["T1"], "S")

    def test_the_distilled_copy_answers_the_fallback(self):
        trips = ("route_id,service_id,trip_id,shape_id\n"
                 "R1,S,01-ABY--5-T0-8605,X\nR1,W,01-ABY--6-T0-8605,X\n")
        times = ("trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type\n"
                 "01-ABY--5-T0-8605,08:00:00,08:00:00,A,1,0,0\n01-ABY--5-T0-8605,09:00:00,09:00:00,B,2,0,0\n"
                 "01-ABY--6-T0-8605,08:00:00,08:00:00,A,1,0,0\n01-ABY--6-T0-8605,09:00:00,09:00:00,B,2,0,0\n")
        cal = CALENDAR + "W,0,0,0,0,0,1,1,20261001,20261231\n"
        d = self.distill(**{"trips.txt": trips, "stop_times.txt": times, "calendar.txt": cal})
        d = json.loads(json.dumps(d))   # as route_store writes and reads it
        r = rt()
        self.assertEqual(r._table_id(LIVE, "20261020", d), "01-ABY--5-T0-8605")
        self.assertEqual(r._table_id(LIVE, "20261024", d), "01-ABY--6-T0-8605")


class TheLibrarysRules(unittest.TestCase):
    """saw-livetrack 0.2.38 (backlog 337): the rules are saw_livetrack.vline's, this file the adapter."""

    def test_the_rules_are_the_librarys(self):
        import saw_livetrack.vline as lib
        self.assertIs(src.VLineRealtime._feed_frozen, lib.feed_frozen)
        self.assertIsInstance(rt()._tracker, lib.VLineRuns)
        self.assertIs(src.service_number, lib.service_number)
        self.assertIs(src.next_stop, lib.next_stop)

    def test_whole_feed_from_the_client(self):
        class C:
            def feed_newest(self, consumer):
                return (123.0, 9) if consumer == "intercity" else None
        self.assertEqual(src.whole(C(), "intercity"), (123.0, 9))
        self.assertIsNone(src.whole(object(), "intercity"))

    def test_a_frozen_whole_feed_holds_a_lone_long_distance_train(self):
        # At midnight the long routes may be one train: alone it is no freeze, the whole feed says it is.
        r = rt()
        t0 = T(10, 30)
        lone = positions((TRIP, START, -37.39, 145.0, t0))
        snap = r.parse(lone, None, t0 + 5, GEO)
        self.assertNotIn(HELD, snap.extras["8605-20"])
        snap = r.parse(lone, None, t0 + 200, GEO)
        self.assertNotIn("feed_frozen", snap.skipped)
        snap = r.parse(lone, None, t0 + 200, GEO, whole=(t0, 12))
        self.assertEqual(snap.skipped.get("feed_frozen"), 1)
        self.assertIsNone(snap.extras["8605-20"][HELD])
        self.assertEqual(snap.extras["8605-20"][base.TIMED_AFTER_KEY], src.ROW_GONE_TIMED_S)

    def test_the_geometry_view(self):
        v = src.GeoTimetable(GEO)
        self.assertIn(TRIP, v)
        self.assertNotIn("nope", v)
        self.assertEqual(v.stop_rows(TRIP)[0], [1, "A", 36000, 36000])
        self.assertEqual(v.stop_rows("nope"), [])
        services = {TRIP: "S"}
        g = dict(GEO, trip_services=services)
        self.assertIs(src.GeoTimetable(g).token, services)
        self.assertEqual(list(src.GeoTimetable(g).twin_candidates()), [TRIP])
        self.assertEqual(list(src.GeoTimetable({}).twin_candidates()), [])


class Reference(unittest.TestCase):
    def test_copy_is_byte_exact_when_the_library_clone_is_here(self):
        here = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_intercity_rail" / "shared_transport_vic.py"
        # The library's reference copy, in a LiveTrackCore clone (AmtrakerClient) beside this one; skipped without it.
        clone = pathlib.Path(__file__).resolve().parents[2] / "AmtrakerClient" / "reference" / "shared_transport_vic.py"
        if clone.exists():
            self.assertEqual(here.read_bytes(), clone.read_bytes())


if __name__ == "__main__":
    unittest.main()
