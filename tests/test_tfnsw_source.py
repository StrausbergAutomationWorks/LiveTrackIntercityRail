"""NSW TrainLink on Transport for NSW's feed: the adapter, the look, the timetable by
trip. Every case is a measured finding or a decision of Lee's: sources/tfnsw.py,
operators/nsw_trainlink.py. Run from the repo root: python -m unittest tests.test_tfnsw_source
"""

import datetime as dt
import io
import json
import pathlib
import sys
import unittest
import zipfile
from zoneinfo import ZoneInfo

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _load import load  # noqa: E402

from google.transit import gtfs_realtime_pb2 as pb  # noqa: E402

src = load("sources.tfnsw")
geometry = load("geometry")
operators = load("operators")
nsw = load("operators.nsw_trainlink")
attributes = load("attributes")
base = load("sources.base")
projection = load("projection")

SYD = ZoneInfo("Australia/Sydney")
START = "20261020"
# 2026-10-20 12:00 Sydney, the service day's origin + 12 h.
ORIGIN = dt.datetime(2026, 10, 20, 12, tzinfo=SYD).timestamp() - 43200.0
TRIP = "NT31.1419.201026.108.P.6.1"
LABEL = "07:30am (031)  Sydney - Brisbane"
GEO = {
    "stops": {"A": [-33.0, 151.0], "B": [-32.0, 151.0], "C": [-31.0, 151.0], "D": [-30.0, 151.0]},
    "stop_names": {"A": "Central Station", "B": "Gosford Station", "C": "Grafton Station", "D": "Roma Street"},
    "train_routes": {TRIP: "North Coast NSW"},
    "trip_numbers": {TRIP: "31"},
    # at 10:00, 11:00-11:14, 12:00, 13:00, seconds from the origin
    "trip_stops": {TRIP: [[1, "A", 36000, 36000], [2, "B", 39600, 40440], [3, "C", 43200, 43200], [4, "D", 46800, 46800]]},
    "trains": {TRIP: ["S"]},
    "shapes": {"S": [[-33.0, 151.0], [-30.0, 151.0]]},
}
T = lambda h, m=0, s=0: ORIGIN + h * 3600 + m * 60 + s


def positions(*vehicles):
    f = pb.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    for i, (trip, start, label, lat, lon, ts) in enumerate(vehicles):
        e = f.entity.add()
        e.id = str(i)
        e.vehicle.trip.trip_id = trip
        e.vehicle.trip.start_date = start
        if label is not None:
            e.vehicle.vehicle.label = label
        if lat is not None:
            e.vehicle.position.latitude = lat
            e.vehicle.position.longitude = lon
        if ts is not None:
            e.vehicle.timestamp = int(ts)
    return f


def update(*stops, trip=TRIP, start=START, f=None):
    """Each stop: (sequence, relationship, arrival delay)."""
    f = f or pb.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    e = f.entity.add()
    e.id = "u" + trip + start
    u = e.trip_update
    u.trip.trip_id = trip
    u.trip.start_date = start
    for seq, rel, delay in stops:
        s = u.stop_time_update.add()
        s.stop_sequence = seq
        s.schedule_relationship = rel
        if delay is not None:
            s.arrival.delay = delay
    return f


def one(lat=-32.5, lon=151.0, ts=None, now=None):
    now = T(10, 30) if now is None else now
    return positions((TRIP, START, LABEL, lat, lon, now - 60 if ts is None else ts)), now


class Identity(unittest.TestCase):
    def test_number_from_the_label(self):
        self.assertEqual(src.number_of("05:45am (032)  Brisbane - Sydney"), "32")
        self.assertEqual(src.number_of(LABEL), "31")
        self.assertEqual(src.number_of("10:00am (243)  Werris Creek - Moree"), "243")

    def test_no_number(self):
        for bad in ("Sydney - Brisbane", "", None, 31, "(abc)"):
            self.assertIsNone(src.number_of(bad))

    def test_identity(self):
        self.assertEqual(src.identity("31", "20261020"), "31-20")
        self.assertEqual(src.identity("31", "20261101"), "31-1")
        for bad in ("", None, "2026102", "2026-10-20"):
            self.assertEqual(src.identity("31", bad), "31")

    def test_trip_is_one_marker_whoever_the_vehicle_is(self):
        f, now = one()
        snap = src.TfnswRealtime().parse(f, None, now, GEO)
        o = snap.observations[0]
        self.assertEqual((o.vehicle_id, o.train, o.trip_id, o.in_service, o.line, o.reported_course),
                         ("31-20", "31", "31-20", True, None, None))
        self.assertEqual(snap.route_keys["31-20"], TRIP)

    def test_number_from_the_timetable_without_a_label(self):
        f = positions((TRIP, START, None, -32.5, 151.0, T(10, 29)))
        snap = src.TfnswRealtime().parse(f, None, T(10, 30), GEO)
        self.assertEqual(snap.observations[0].train, "31")

    def test_no_number_anywhere(self):
        f = positions(("X", START, None, -32.5, 151.0, T(10, 29)))
        snap = src.TfnswRealtime().parse(f, None, T(10, 30), GEO)
        self.assertEqual((snap.observations, snap.skipped), ([], {"no_number": 1}))

    def test_two_rows_one_run_first_wins(self):
        f = positions((TRIP, START, LABEL, -32.5, 151.0, T(10, 29)), (TRIP, START, LABEL, -32.4, 151.0, T(10, 29)))
        snap = src.TfnswRealtime().parse(f, None, T(10, 30), GEO)
        self.assertEqual(len(snap.observations), 1)
        self.assertEqual(snap.skipped, {"duplicate": 1})

    def test_same_number_on_two_dates_two_markers(self):
        f = positions((TRIP, START, LABEL, -32.5, 151.0, T(10, 29)), (TRIP, "20261019", LABEL, -31.5, 151.0, T(10, 29)))
        snap = src.TfnswRealtime().parse(f, None, T(10, 30), GEO)
        self.assertEqual(sorted(o.vehicle_id for o in snap.observations), ["31-19", "31-20"])

    def test_no_position(self):
        f = positions((TRIP, START, LABEL, None, None, T(10, 29)))
        snap = src.TfnswRealtime().parse(f, None, T(10, 30), GEO)
        self.assertEqual(snap.skipped, {"no_position": 1})

    def test_none_is_an_outage_and_empty_is_not(self):
        self.assertIsNone(src.TfnswRealtime().parse(None, None, 0.0, GEO))
        snap = src.TfnswRealtime().parse(positions(), None, 0.0, GEO)
        self.assertEqual(snap.observations, [])

    def test_an_update_alone_makes_no_marker(self):
        snap = src.TfnswRealtime().parse(positions(), update((1, 0, 60)), T(10, 30), GEO)
        self.assertEqual(snap.observations, [])

    def test_without_a_timetable_a_marker_with_no_next_stop(self):
        f, now = one()
        snap = src.TfnswRealtime().parse(f, update((2, 0, 60)), now, {})
        self.assertEqual(snap.observations[0].train, "31")
        self.assertEqual((snap.next_stops, snap.trip_delays, snap.stop_codes), ({}, {}, {}))

    def test_line_name(self):
        f, now = one()
        snap = src.TfnswRealtime().parse(f, None, now, GEO)
        self.assertEqual(snap.extras["31-20"], {"line_name": "North Coast NSW"})


class NextStop(unittest.TestCase):
    def parse(self, now, *stops, ts=None):
        f, now = one(now=now, ts=ts)
        return src.TfnswRealtime().parse(f, update(*stops) if stops else None, now, GEO)

    def test_by_timetable_plus_delay(self):
        snap = self.parse(T(10, 30), (2, 0, 120), (3, 0, 120))
        self.assertEqual(snap.next_stops["31-20"], ("Gosford Station", T(11, 2)))
        self.assertEqual(snap.stop_codes["31-20"], "B")
        self.assertEqual(snap.trip_delays["31-20"], 120)

    def test_held_at_a_stop_until_its_delayed_departure(self):
        # Leaves B at 11:14 + 10 min.
        self.assertEqual(self.parse(T(11, 20), (2, 0, 600), (3, 0, 600)).stop_codes["31-20"], "B")
        self.assertEqual(self.parse(T(11, 25), (2, 0, 600), (3, 0, 600)).stop_codes["31-20"], "C")

    def test_the_origin_is_never_next(self):
        snap = self.parse(T(9, 50), (1, 0, 0))
        self.assertEqual(snap.stop_codes["31-20"], "B")

    def test_the_origins_delay_counts_for_the_stop_after_it(self):
        snap = self.parse(T(10, 10), (1, 0, 900))
        self.assertEqual(snap.trip_delays["31-20"], 900)
        self.assertEqual(snap.next_stops["31-20"][1], T(11, 15))

    def test_a_skipped_stop_is_never_next(self):
        snap = self.parse(T(10, 30), (2, 1, 0), (3, 0, 60))
        self.assertEqual(snap.stop_codes["31-20"], "C")

    def test_past_the_last_stop(self):
        snap = self.parse(T(14, 0), (4, 0, 0))
        self.assertEqual((snap.stop_codes, snap.next_stops), ({}, {}))

    def test_no_update_no_delay_said(self):
        snap = self.parse(T(10, 30))
        self.assertEqual(snap.stop_codes["31-20"], "B")
        self.assertNotIn("31-20", snap.trip_delays)

    def test_update_with_no_delay_says_none(self):
        snap = self.parse(T(10, 30), (2, 0, None))
        self.assertNotIn("31-20", snap.trip_delays)

    def test_time_in_the_update_is_not_read(self):
        f, now = one()
        u = update((2, 0, 60))
        u.entity[0].trip_update.stop_time_update[0].arrival.time = 1
        snap = src.TfnswRealtime().parse(f, u, now, GEO)
        self.assertEqual(snap.next_stops["31-20"], ("Gosford Station", T(11, 1)))

    def test_a_replacement_reads_as_scheduled(self):
        f, now = one()
        u = update((2, 0, 60))
        u.entity[0].trip_update.trip.schedule_relationship = 5
        snap = src.TfnswRealtime().parse(f, u, now, GEO)
        self.assertEqual(snap.stop_codes["31-20"], "B")

    def test_another_runs_update_is_not_read(self):
        f, now = one()
        u = update((2, 0, 999), start="20261021")
        snap = src.TfnswRealtime().parse(f, u, now, GEO)
        self.assertNotIn("31-20", snap.trip_delays)

    def test_first_update_of_a_run_wins(self):
        f, now = one()
        u = update((2, 0, 60))
        update((2, 0, 999), f=u)
        snap = src.TfnswRealtime().parse(f, u, now, GEO)
        self.assertEqual(snap.trip_delays["31-20"], 60)

    def test_a_trip_with_one_stop(self):
        geo = dict(GEO, trip_stops={TRIP: [[1, "A", 39600, 39600]]})
        f, now = one()
        snap = src.TfnswRealtime().parse(f, None, now, geo)
        self.assertEqual(snap.stop_codes["31-20"], "A")

    def test_no_name_no_next_stop_but_the_aim_stays(self):
        geo = dict(GEO, stop_names={})
        f, now = one()
        snap = src.TfnswRealtime().parse(f, None, now, geo)
        self.assertEqual(snap.next_stops, {})
        self.assertEqual(snap.stop_codes["31-20"], "B")

    def test_a_bad_start_date_no_rows(self):
        f = positions((TRIP, "2026xx20", LABEL, -32.5, 151.0, T(10, 29)))
        snap = src.TfnswRealtime().parse(f, None, T(10, 30), GEO)
        self.assertEqual(len(snap.observations), 1)
        self.assertEqual(snap.stop_codes, {})
        self.assertEqual(src.TfnswRealtime()._rows(TRIP, "2026xx20", GEO), [])

    def test_past_midnight(self):
        geo = dict(GEO, trip_stops={TRIP: [[1, "A", 3600, 3600], [2, "B", 90000, 90060]]})
        now = ORIGIN + 86400 + 1800      # 00:30 the next morning
        f = positions((TRIP, START, LABEL, -32.5, 151.0, now - 60))
        snap = src.TfnswRealtime().parse(f, None, now, geo)
        self.assertEqual(snap.next_stops["31-20"][1], ORIGIN + 90000)

    def test_daylight_saving_day(self):
        # 2026-10-04: clocks forward in Sydney. Noon less 12 h is the GTFS origin.
        r = src.TfnswRealtime()
        self.assertEqual(r._origin("20261004"), dt.datetime(2026, 10, 4, 12, tzinfo=SYD).timestamp() - 43200.0)

    def test_held_updates(self):
        r = src.TfnswRealtime()
        f, now = one()
        r.parse(f, update((2, 0, 120)), now, GEO)
        snap = r.parse(f, None, now + 599, GEO)
        self.assertEqual(snap.trip_delays["31-20"], 120)
        snap = r.parse(f, None, now + 601, GEO)
        self.assertNotIn("31-20", snap.trip_delays)


class Age(unittest.TestCase):
    def test_a_stale_first_sight_gets_no_marker(self):
        now = T(10, 30)
        f = positions((TRIP, START, LABEL, -32.5, 151.0, now - 301))
        snap = src.TfnswRealtime().parse(f, None, now, GEO)
        self.assertEqual((snap.observations, snap.skipped), ([], {"stale_first_sight": 1}))

    def test_at_the_limit_it_does(self):
        now = T(10, 30)
        f = positions((TRIP, START, LABEL, -32.5, 151.0, now - 300))
        self.assertEqual(len(src.TfnswRealtime().parse(f, None, now, GEO).observations), 1)

    def test_a_stale_first_sight_comes_back_when_fresh(self):
        r, now = src.TfnswRealtime(), T(10, 30)
        r.parse(positions((TRIP, START, LABEL, -32.5, 151.0, now - 400)), None, now, GEO)
        snap = r.parse(positions((TRIP, START, LABEL, -32.5, 151.0, now + 50)), None, now + 60, GEO)
        self.assertEqual(len(snap.observations), 1)

    def test_no_age_refusal_once_seen(self):
        r, now = src.TfnswRealtime(), T(10, 30)
        f = positions((TRIP, START, LABEL, -32.5, 151.0, now - 60))
        r.parse(f, None, now, GEO)
        snap = r.parse(f, None, now + 1500, GEO)
        self.assertEqual(len(snap.observations), 1)

    def test_finished(self):
        r, now = src.TfnswRealtime(), T(12, 50)
        f = positions((TRIP, START, LABEL, -30.0, 151.0, now - 60))
        r.parse(f, update((4, 0, 0)), now, GEO)
        # Terminal 13:00 passed and the fix over 300 s old.
        later = T(13, 10)
        snap = r.parse(f, update((4, 0, 0)), later, GEO)
        self.assertEqual((snap.observations, snap.skipped), ([], {"finished": 1}))

    def test_not_finished_while_the_fix_is_fresh(self):
        later = T(13, 10)
        f = positions((TRIP, START, LABEL, -30.0, 151.0, later - 60))
        self.assertEqual(len(src.TfnswRealtime().parse(f, update((4, 0, 0)), later, GEO).observations), 1)

    def test_not_finished_while_the_forecast_is_ahead(self):
        r, now = src.TfnswRealtime(), T(12, 50)
        f = positions((TRIP, START, LABEL, -30.5, 151.0, now - 60))
        r.parse(f, update((4, 0, 1800)), now, GEO)
        later = T(13, 20)
        self.assertEqual(len(r.parse(f, update((4, 0, 1800)), later, GEO).observations), 1)

    def test_forecast_uses_the_last_delay_known(self):
        rows = [(1, "A", 10.0, 10.0), (2, "B", 100.0, 100.0)]
        self.assertEqual(src._terminal_forecast(rows, {1: 5}), 105.0)
        self.assertEqual(src._terminal_forecast(rows, {1: 5, 2: 7}), 107.0)
        self.assertEqual(src._terminal_forecast(rows, {}), 100.0)
        self.assertIsNone(src._terminal_forecast([], {}))
        self.assertEqual(src._terminal_forecast([(1, "A", None, 9.0)], {}), 9.0)
        self.assertEqual(src._terminal_forecast([(1, "A", 100.0, 160.0)], {}), 100.0)
        self.assertIsNone(src._terminal_forecast([(1, "A", None, None)], {}))

    def test_state_forgotten(self):
        r, now = src.TfnswRealtime(), T(10, 30)
        f = positions((TRIP, START, LABEL, -32.5, 151.0, now - 60))
        r.parse(f, None, now, GEO)
        self.assertIn("31-20", r._fresh)
        self.assertIn("31-20", r._still)
        r.parse(positions(), None, now + src.FORGET_S + 1, GEO)
        self.assertNotIn("31-20", r._fresh)
        self.assertNotIn("31-20", r._still)


class Stalled(unittest.TestCase):
    def run_at(self, lat, lon, seconds, start=None, geo=GEO):
        """A train standing `seconds`: one fix at the start, one at the end."""
        r = src.TfnswRealtime()
        t0 = T(10, 30) if start is None else start
        r.parse(positions((TRIP, START, LABEL, lat, lon, t0)), None, t0 + 1, geo)
        snap = r.parse(positions((TRIP, START, LABEL, lat, lon, t0 + seconds)), None, t0 + seconds + 1, geo)
        return (snap.extras.get("31-20") or {}).get("stalled")

    def test_away_from_stops(self):
        self.assertIsNone(self.run_at(-32.5, 151.0, 365))
        self.assertTrue(self.run_at(-32.5, 151.0, 366))

    def test_at_a_stop_with_a_dwell(self):
        # B dwells 840 s.
        self.assertIsNone(self.run_at(-32.0, 151.0, 840 + 365))
        self.assertTrue(self.run_at(-32.0, 151.0, 840 + 366))

    def test_within_300_m_of_it(self):
        lat = -32.0 + 290 / 111195.0
        self.assertIsNone(self.run_at(lat, 151.0, 840 + 365))

    def test_beyond_300_m_of_it(self):
        lat = -32.0 + 310 / 111195.0
        self.assertTrue(self.run_at(lat, 151.0, 366))

    def test_just_beyond_300_m_of_it(self):
        self.assertTrue(self.run_at(-32.0 + 303 / 111195.0, 151.0, 366))

    def test_a_fix_with_no_time_starts_nothing(self):
        r, t0 = src.TfnswRealtime(), T(10, 30)
        r.parse(positions((TRIP, START, LABEL, -32.5, 151.0, None)), None, t0, GEO)
        self.assertNotIn("31-20", r._still)
        snap = r.parse(positions((TRIP, START, LABEL, -32.5, 151.0, t0 + 1)), None, t0 + 2, GEO)
        self.assertNotIn("stalled", snap.extras["31-20"])

    def test_at_a_stop_with_no_dwell(self):
        self.assertIsNone(self.run_at(-31.0, 151.0, 365))
        self.assertTrue(self.run_at(-31.0, 151.0, 366))

    def test_nearest_stop_wins(self):
        geo = dict(GEO, stops=dict(GEO["stops"], C=[-32.0 + 200 / 111195.0, 151.0]))
        # At B's coordinates: C is 200 m away with no dwell, B 0 m with 840 s.
        self.assertIsNone(self.run_at(-32.0, 151.0, 840 + 365, geo=geo))

    def test_a_stop_of_another_trip_is_not_one(self):
        geo = dict(GEO, stops=dict(GEO["stops"], Z=[-32.5, 151.0]))
        self.assertTrue(self.run_at(-32.5, 151.0, 366, geo=geo))

    def test_no_timetable(self):
        self.assertTrue(self.run_at(-32.5, 151.0, 366, geo={"trip_numbers": {}}))

    def test_moving_restarts_it(self):
        r, t0 = src.TfnswRealtime(), T(10, 30)
        r.parse(positions((TRIP, START, LABEL, -32.5, 151.0, t0)), None, t0 + 1, GEO)
        # 60 m on.
        r.parse(positions((TRIP, START, LABEL, -32.5 + 60 / 111195.0, 151.0, t0 + 300)), None, t0 + 301, GEO)
        snap = r.parse(positions((TRIP, START, LABEL, -32.5 + 60 / 111195.0, 151.0, t0 + 400)), None, t0 + 401, GEO)
        self.assertNotIn("stalled", snap.extras["31-20"])

    def test_wander_is_not_moving(self):
        r, t0 = src.TfnswRealtime(), T(10, 30)
        r.parse(positions((TRIP, START, LABEL, -32.5, 151.0, t0)), None, t0 + 1, GEO)
        snap = r.parse(positions((TRIP, START, LABEL, -32.5 + 40 / 111195.0, 151.0, t0 + 400)), None, t0 + 401, GEO)
        self.assertTrue(snap.extras["31-20"]["stalled"])

    def test_by_the_fixes_time_not_the_clock(self):
        r, t0 = src.TfnswRealtime(), T(10, 30)
        f = positions((TRIP, START, LABEL, -32.5, 151.0, t0))
        r.parse(f, None, t0 + 1, GEO)
        snap = r.parse(f, None, t0 + 1000, GEO)
        self.assertNotIn("stalled", snap.extras["31-20"])

    def test_an_older_fix_restarts_it(self):
        r, t0 = src.TfnswRealtime(), T(10, 30)
        r.parse(positions((TRIP, START, LABEL, -32.5, 151.0, t0)), None, t0 + 1, GEO)
        r.parse(positions((TRIP, START, LABEL, -32.5, 151.0, t0 - 500)), None, t0 + 2, GEO)
        self.assertEqual(r._still["31-20"][2], t0 - 500)

    def test_reaches_the_map(self):
        self.assertIn("stalled", base.EXTRA_KEYS)
        self.assertNotIn("stalled", base.RECORD_ONLY_KEYS)
        self.assertTrue(attributes.to_attributes(
            {"vehicle_id": "31-20", "marker_label": "31", "in_service": True, "stalled": True}, "nsw_trainlink")["stalled"])


class Look(unittest.TestCase):
    def test_leaving_sydney(self):
        k = nsw.nsw_styling("31")
        self.assertEqual((k["marker_color"], k["marker_ring_color"], k["marker_label_color"]), ("#F6891F", "#FFFFFF", "#FFFFFF"))
        self.assertEqual((k["marker_arrow_color"], k["marker_arrow_outline_color"]), ("#F6891F", "#FFFFFF"))

    def test_going_to_sydney(self):
        k = nsw.nsw_styling("32")
        self.assertEqual((k["marker_color"], k["marker_ring_color"], k["marker_label_color"]), ("#FFFFFF", "#F6891F", "#F6891F"))
        self.assertEqual((k["marker_arrow_color"], k["marker_arrow_outline_color"]), ("#FFFFFF", "#F6891F"))

    def test_unknown_is_primary(self):
        for number in (None, "", "X1"):
            self.assertEqual(nsw.nsw_styling(number)["marker_color"], "#F6891F")

    def test_ring_and_no_label_outline(self):
        k = nsw.nsw_styling("31")
        self.assertEqual(k["marker_ring_width"], nsw.RING_WIDTH)
        self.assertEqual(k["marker_label_outline_color"], "none")

    def test_through_the_operator(self):
        op = operators.OPERATORS["nsw_trainlink"]
        self.assertEqual(op.marker_keys({"train": "243"})["marker_color"], "#F6891F")
        self.assertEqual(op.lateness_for({"train": "31"}), {"late_threshold_min": 11, "very_late_threshold_min": 30})


class Operator(unittest.TestCase):
    def test_settings(self):
        op = operators.OPERATORS["nsw_trainlink"]
        self.assertEqual((op.id, op.name, op.regions, op.source, op.scan_interval_s),
                         ("nsw_trainlink", "NSW TrainLink", ("AU",), operators.SOURCE_TFNSW, 60))
        self.assertEqual(op.source_options, {"consumer": "intercity"})
        self.assertEqual(op.gtfs_route_types, ("106",))
        self.assertTrue(op.derive_speed and op.needs_key and op.gtfs_from_source)
        self.assertFalse(op.timed_without_fix)
        self.assertIsNone(op.gtfs_url)
        self.assertEqual(op.attribution, "Data: Transport for NSW (opendata.transport.nsw.gov.au), CC BY 4.0")
        self.assertTrue(op.terms_url and op.key_url)

    def test_region_offered(self):
        self.assertEqual(operators.regions_in_use()["AU"], "Australia")
        # WA Trains (Transwa) since 2026-11-14 (Intercity SSOT 8.12) and Journey Beyond (8.13), sorted by name.
        self.assertEqual([o.id for o in operators.operators_in("AU")],
                         ["journey_beyond", "nsw_trainlink", "vline", "wa_trains"])

    def test_other_railroads_need_no_key(self):
        for op in operators.OPERATORS.values():
            # Sweden's fifteen take each user's Trafikverket key (SSOT 8.9; tests/test_trafikverket_source.py).
            # The Netherlands' three take each user's NS key (SSOT 8.11; tests/test_ns_source.py).
            if op.source in (operators.SOURCE_TRAFIKVERKET, operators.SOURCE_NS):
                continue
            if op.id not in ("nsw_trainlink", "vline"):
                self.assertFalse(op.needs_key, op.id)
                # Renfe's regionals take the timetable from the shared client too (SSOT 8.7), and Norway's railroads
                # from Entur's (SSOT 8.8), Irish Rail from its client's (SSOT 8.10); Journey Beyond's ships with the
                # integration and reaches the route store the same way (SSOT 8.13).
                self.assertEqual(op.gtfs_from_source,
                                 op.id in ("renfe_regionals_catalunya", "renfe_spain", "vy", "go_ahead_norge",
                                           "sj_nord", "irish_rail", "wa_trains", "journey_beyond"), op.id)


class Manifest(unittest.TestCase):
    """Backlog 286: Home Assistant ignores an extra, so its packages are named."""

    def test_extras_named(self):
        import importlib.metadata as md
        import re
        here = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_intercity_rail"
        req = json.loads((here / "manifest.json").read_text(encoding="utf-8"))["requirements"]
        # 0.2.40 since 2026-11-14: saw_livetrack.transperth, Transwa (Intercity SSOT 8.12). 0.2.38 from 2026-11-13: V/Line's long routes only and saw_livetrack.vline (backlog 337). 0.2.35 from 2026-11-11: saw_livetrack.ns, the Netherlands (Intercity SSOT 8.11). 0.2.33 from 2026-11-10: the Irish Rail client builds its TLS opener at first use. 0.2.32 from 2026-11-10: saw_livetrack.irish_rail, Ireland (Intercity SSOT 8.10). 0.2.31 from 2026-11-08: saw_livetrack.trafikverket, Sweden (Intercity SSOT 8.9). 0.2.29 from 2026-11-08: SIRI ET for SJ Nord (Intercity SSOT 8.8, "SJ NORD: BUILT"). 0.2.27 from
        # 2026-11-07: saw_livetrack.entur, Norway. 0.2.25 from 2026-11-05: digitraffic_rail.next_stop after the
        # last actual row (backlog 289).
        self.assertTrue(req[0].startswith("saw-livetrack[gtfs]>=0.2.40,"), req)
        names = {re.split(r"[=<>\[]", r)[0].lower() for r in req}
        extra = [r.split(";")[0].strip() for r in md.requires("saw-livetrack") if 'extra == "gtfs"' in r]
        self.assertTrue(extra)
        for pkg in extra:
            self.assertIn(re.split(r"[=<>\[]", pkg)[0].lower(), names, pkg)

    def test_reference_copy_is_byte_exact_when_the_library_clone_is_here(self):
        here = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_intercity_rail" / "shared_tfnsw.py"
        # The library's reference copy, in a LiveTrackCore clone (AmtrakerClient) beside this one; skipped without it.
        clone = pathlib.Path(__file__).resolve().parents[2] / "AmtrakerClient" / "reference" / "shared_tfnsw.py"
        if clone.exists():
            self.assertEqual(here.read_bytes(), clone.read_bytes())


def gtfs_zip():
    files = {
        "routes.txt": "route_id,route_short_name,route_long_name,route_type\n4T.T.NT31,31,North Coast NSW,106\n",
        "trips.txt": "route_id,service_id,trip_id,trip_short_name,shape_id\n4T.T.NT31,S,T1,NT31,X\n4T.T.NT31,S,T2,NT31,Y\n",
        "stops.txt": ("stop_id,stop_name,stop_lat,stop_lon,parent_station\n"
                      "P,Grafton Station,-29.7,152.9,\n"
                      "1,\"Grafton Station, Platform 1\",-29.7,152.9,P\n"
                      "2,Wodonga  -  Victoria Border Stop Station,-36.1,146.9,\n"),
        "stop_times.txt": ("trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type\n"
                           "T1,25:10:00,25:24:00,1,2,0,0\n"
                           "T1,08:00:00,08:00:00,1,1,0,1\n"
                           "T1,26:00:00,26:00:00,2,3,1,1\n"
                           "T1,27:00:00,27:00:00,1,4,1,3\n"
                           "T2,,,1,1,3,3\n"),
        "shapes.txt": ("shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n"
                       "X,-29.0,152.0,1\nX,-30.0,152.0,2\nY,-31.0,152.0,1\nY,-32.0,152.0,2\n"),
    }
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        for n, t in files.items():
            z.writestr(n, t)
    return out.getvalue()


class TripKeys(unittest.TestCase):
    def setUp(self):
        self.d = geometry.distill(gtfs_zip(), trip_keys=True)

    def test_trains_by_trip(self):
        self.assertEqual(self.d["trains"], {"T1": ["X"], "T2": ["Y"]})
        self.assertEqual(self.d["train_routes"], {"T1": "North Coast NSW", "T2": "North Coast NSW"})
        self.assertEqual(self.d["trip_numbers"], {"T1": "31", "T2": "31"})

    def test_stops_in_order_seconds_past_midnight(self):
        self.assertEqual(self.d["trip_stops"]["T1"][:2], [[1, "1", 28800, 28800], [2, "1", 90600, 91440]])

    def test_a_stop_no_rider_uses_is_left_out(self):
        self.assertEqual([r[0] for r in self.d["trip_stops"]["T1"]], [1, 2, 4])

    def test_pickup_or_drop_alone_stays(self):
        self.assertEqual(self.d["trip_stops"]["T1"][2][0], 4)

    def test_no_times_are_none(self):
        self.assertEqual(self.d["trip_stops"]["T2"], [[1, "1", None, None]])

    def test_parent_name(self):
        self.assertEqual(self.d["stop_names"]["1"], "Grafton Station")
        self.assertEqual(self.d["stop_names"]["2"], "Wodonga  -  Victoria Border Stop Station")

    def test_seconds(self):
        self.assertEqual(geometry._seconds("25:10:05"), 90605)
        for bad in ("", None, "x", "1:2"):
            self.assertIsNone(geometry._seconds(bad))

    def test_the_default_is_unchanged(self):
        d = geometry.distill(gtfs_zip())
        self.assertEqual(d["trains"], {"NT31": ["X", "Y"]})
        self.assertNotIn("trip_stops", d)
        self.assertNotIn("trip_numbers", d)
        self.assertEqual(d["stop_names"]["1"], "Grafton Station, Platform 1")

    def test_a_trips_own_line_is_chosen(self):
        p = geometry.Projector(self.d)
        # On Y's line, with the key T1: T1 has only X.
        self.assertIsNone(p.estimate("31-20", "T1", (-31.5, 152.0), 100.0, None, None, 110.0))
        self.assertIsNotNone(p.estimate("31-20", "T2", (-31.5, 152.0), 100.0, None, None, 110.0))


if __name__ == "__main__":
    unittest.main()
