"""Renfe's regional trains in Catalonia (R11-R17): the adapter, the timetable cut, the look, the
lateness, the route store's own-distill hook and the coordinator. Every case is a measured finding
or a decision of Lee's: sources/renfe.py, operators/renfe_regionals.py (Intercity SSOT 8.7,
backlog 294). Run from the repo root: python -m unittest tests.test_renfe_regionals
"""

import asyncio
import datetime as dt
import gzip
import io
import json
import pathlib
import shutil
import sys
import tempfile
import types
import unittest
import zipfile
from zoneinfo import ZoneInfo

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _ha_stub  # noqa: E402
_ha_stub.install()
from _load import load  # noqa: E402

from google.transit import gtfs_realtime_pb2 as pb  # noqa: E402

src = load("sources.renfe")
base = load("sources.base")
operators = load("operators")
rr = load("operators.renfe_regionals")
attributes = load("attributes")
route_store = load("route_store")
coordinator = load("coordinator")
const = load("const")
flow = load("config_flow")

run = asyncio.run
MAD = ZoneInfo("Europe/Madrid")
DATE = "20261106"
ORIGIN = dt.datetime(2026, 11, 6, 12, tzinfo=MAD).timestamp() - 43200.0
T = lambda h, m=0, s=0: ORIGIN + h * 3600 + m * 60 + s
TRIP = "5109V15772R11"
GEO = {
    # On the line S1, a third and two thirds along it.
    "stops": {"F": [42.0, 3.0], "G": [41.8, 2.7], "S": [41.6, 2.4], "B": [41.4, 2.1]},
    "stop_names": {"F": "Figueres", "G": "Girona", "S": "Sant Celoni", "B": "Barcelona-Sants"},
    "trip_numbers": {TRIP: "R11"},
    "trip_dates": {TRIP: DATE},
    "line_colours": {"R11": "#0069AA"},
    # 05:52, 06:25-06:27, 06:42, 07:55
    "trip_stops": {TRIP: [[1, "F", T(5, 52), T(5, 52)], [2, "G", T(6, 25), T(6, 27)],
                          [3, "S", T(6, 42), T(6, 43)], [4, "B", T(7, 55), T(7, 55)]]},
    "trains": {TRIP: ["S1"]},
    "shapes": {"S1": [[42.0, 3.0], [41.4, 2.1]]},
}
for _k, _rows in GEO["trip_stops"].items():
    GEO["trip_stops"][_k] = [[s, i, a - ORIGIN, d - ORIGIN] for s, i, a, d in _rows]


def positions(*vehicles):
    """(trip, label, lat, lon, ts, status or None)."""
    f = pb.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    for i, (trip, label, lat, lon, ts, status) in enumerate(vehicles):
        e = f.entity.add()
        e.id = f"VP_{i}"
        e.vehicle.trip.trip_id = trip
        if label is not None:
            e.vehicle.vehicle.label = label
        if lat is not None:
            e.vehicle.position.latitude = lat
            e.vehicle.position.longitude = lon
        if ts is not None:
            e.vehicle.timestamp = int(ts)
        if status is not None:
            e.vehicle.current_status = status
    return f


def updates(*rows):
    """(trip, stop id or None, arrival delay or None, departure delay or None, trip delay or None)."""
    f = pb.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    for i, (trip, stop, arr, dep, whole) in enumerate(rows):
        e = f.entity.add()
        e.id = f"TU_{i}"
        u = e.trip_update
        u.trip.trip_id = trip
        if whole is not None:
            u.delay = whole
        if stop is not None or arr is not None or dep is not None:
            s = u.stop_time_update.add()
            if stop is not None:
                s.stop_id = stop
            if arr is not None:
                s.arrival.delay = arr
            if dep is not None:
                s.departure.delay = dep
    return f


STOPPED, INCOMING, IN_TRANSIT = 1, 0, 2


class Identity(unittest.TestCase):
    def test_label_number(self):
        self.assertEqual(src.number_of("R16-18120"), "18120")
        self.assertEqual(src.number_of("R15-15031 "), "15031")
        # Seen 2026-11-06 05:49 Spain time leaving Barcelona Estacio de Franca.
        self.assertEqual(src.number_of("R16-18121-PLATF.(11)"), "18121")
        self.assertIsNone(src.number_of("R16"))
        self.assertIsNone(src.number_of("R16-1812345"))
        self.assertIsNone(src.number_of("18120"))
        self.assertIsNone(src.number_of(None))

    def test_identity_is_the_number_and_the_day(self):
        self.assertEqual(src.identity("15772", "20261106"), "15772-6")
        self.assertEqual(src.identity("15772", "20261130"), "15772-30")
        self.assertEqual(src.identity("15772", None), "15772")
        self.assertEqual(src.identity("15772", "2026116"), "15772")


class UpdateOf(unittest.TestCase):
    def one(self, *row):
        return src.update_of(updates((TRIP,) + row).entity[0].trip_update)

    def test_arrival_delay_first(self):
        self.assertEqual(self.one("G", 120, 60, 30), ("G", 120))

    def test_departure_when_no_arrival(self):
        self.assertEqual(self.one("G", None, 60, 30), ("G", 60))

    def test_the_trips_own_when_the_stop_has_none(self):
        self.assertEqual(self.one("G", None, None, 30), ("G", 30))

    def test_nothing(self):
        self.assertEqual(self.one(None, None, None, None), (None, None))

    def test_only_the_trips_delay(self):
        self.assertEqual(self.one(None, None, None, 300), (None, 300))


class Toward(unittest.TestCase):
    names = {"F": "Figueres", "B": "Barcelona-Sants", "L": "Lleida-Pirineus", "P": "La Plana-Picamoixons"}

    def test_ending_in_barcelona_goes_to_it(self):
        self.assertIs(src.toward([(1, "F"), (2, "B")], self.names, "Barcelona"), True)

    def test_starting_there_leaves_it(self):
        self.assertIs(src.toward([(1, "B"), (2, "F")], self.names, "Barcelona"), False)

    def test_neither(self):
        self.assertIsNone(src.toward([(1, "L"), (2, "P")], self.names, "Barcelona"))

    def test_no_rows_or_hub(self):
        self.assertIsNone(src.toward([], self.names, "Barcelona"))
        self.assertIsNone(src.toward([(1, "F"), (2, "B")], self.names, ""))

    def test_case_does_not_matter(self):
        self.assertIs(src.toward([(1, "F"), (2, "B")], {"B": "Barcelona-Sants"}, "BARCELONA"), True)


class Parse(unittest.TestCase):
    def setUp(self):
        self.rt = src.RenfeRealtime("Barcelona")

    def one(self, vp, tu=None, now=None, geo=GEO):
        return self.rt.parse(vp, tu, T(6, 0) if now is None else now, geo)

    def test_no_positions_is_no_answer(self):
        self.assertIsNone(self.rt.parse(None, None, T(6, 0), GEO))

    def test_an_empty_feed_is_a_quiet_hour(self):
        snap = self.one(positions())
        self.assertEqual(snap.observations, [])

    def test_identity_label_and_line(self):
        snap = self.one(positions((TRIP, "R11-15772", 42.0, 3.0, T(5, 59), STOPPED)))
        o = snap.observations[0]
        self.assertEqual((o.vehicle_id, o.trip_id, o.train), ("15772-6", "15772-6", "15772"))
        self.assertIsNone(o.reported_course)
        self.assertEqual(snap.route_keys, {"15772-6": TRIP})
        # At Figueres, which it leaves at 05:52: timed from 420 s BEFORE this fix.
        self.assertEqual(snap.extras["15772-6"], {"line_name": "R11", "route_color": "#0069AA",
                                                  "toward_hub": True, base.HELD_SPEED_KEY: None,
                                                  base.TIMED_AFTER_KEY: -420.0})

    def test_the_label_is_the_number_riders_see_and_the_identity_the_trips(self):
        # 5109V30531R15 carried vehicle 15031 (2026-11-05 22:26 CST).
        trip = "5109V30531R15"
        geo = dict(GEO, trip_dates={trip: DATE})
        snap = self.one(positions((trip, "R15-15031", 41.4, 2.1, T(5, 59), STOPPED)), geo=geo)
        o = snap.observations[0]
        self.assertEqual((o.vehicle_id, o.train), ("30531-6", "15031"))
        self.assertEqual(snap.extras[o.vehicle_id]["line_name"], "R15")

    def test_the_timetables_line_wins(self):
        geo = dict(GEO, trip_numbers={TRIP: "R12"})
        snap = self.one(positions((TRIP, "R11-15772", 42.0, 3.0, T(5, 59), STOPPED)), geo=geo)
        self.assertEqual(snap.extras["15772-6"]["line_name"], "R12")

    def test_no_label_takes_the_trips_number(self):
        snap = self.one(positions((TRIP, None, 42.0, 3.0, T(5, 59), STOPPED)))
        self.assertEqual(snap.observations[0].train, "15772")

    def test_no_number_at_all(self):
        snap = self.one(positions(("garbage", None, 42.0, 3.0, T(5, 59), STOPPED)))
        self.assertEqual(snap.skipped, {"no_number": 1})

    def test_a_trip_id_without_a_number_is_skipped_whatever_the_label(self):
        snap = self.one(positions(("garbage", "R11-15772", 42.0, 3.0, T(5, 59), STOPPED)))
        self.assertEqual((snap.observations, snap.skipped), ([], {"no_number": 1}))

    def test_a_trip_with_stops_but_no_date_has_no_timetable(self):
        geo = dict(GEO, trip_dates={})
        snap = self.one(positions((TRIP, "R11-15772", 41.9, 2.9, T(6, 0), IN_TRANSIT)), geo=geo)
        self.assertEqual(snap.observations[0].vehicle_id, "15772")
        self.assertEqual((snap.next_stops, snap.stop_codes), ({}, {}))
        self.assertNotIn("toward_hub", snap.extras["15772"])

    def test_no_position(self):
        snap = self.one(positions((TRIP, "R11-15772", None, None, T(5, 59), STOPPED)))
        self.assertEqual(snap.skipped, {"no_position": 1})

    def test_without_a_timetable_the_bare_number_and_the_trips_line(self):
        snap = self.one(positions((TRIP, "R11-15772", 42.0, 3.0, T(5, 59), STOPPED)), geo={})
        self.assertEqual(snap.observations[0].vehicle_id, "15772")
        self.assertEqual(snap.extras["15772"], {"line_name": "R11", base.HELD_SPEED_KEY: None,
                                                base.TIMED_AFTER_KEY: src.FREE_HORIZON_S})
        self.assertEqual((snap.next_stops, snap.trip_delays, snap.stop_codes), ({}, {}, {}))

    def test_incoming_at_first_sight_gets_no_marker(self):
        snap = self.one(positions((TRIP, "R11-15772", 42.0, 3.0, T(5, 20), INCOMING)), now=T(5, 20))
        self.assertEqual((snap.observations, snap.skipped), ([], {"incoming": 1}))

    def test_incoming_at_repeats_the_last_trusted_fix_and_its_time(self):
        self.one(positions((TRIP, "R11-15772", 42.0, 3.0, T(5, 59), IN_TRANSIT)), now=T(5, 59))
        snap = self.one(positions((TRIP, "R11-15772", 41.9, 2.9, T(6, 0), INCOMING)), now=T(6, 0))
        o = snap.observations[0]
        self.assertEqual((o.lat, o.lon), (42.0, 3.0))
        self.assertEqual(o.observed_at.timestamp(), T(5, 59))

    def test_unset_status_is_trusted(self):
        snap = self.one(positions((TRIP, "R11-15772", 42.0, 3.0, T(5, 59), None)))
        self.assertEqual(len(snap.observations), 1)

    def test_next_stop_is_the_updates_and_its_delay_is_said(self):
        # At 06:00 Girona (06:27) is ahead by the timetable; Renfe says Sant Celoni.
        snap = self.one(positions((TRIP, "R11-15772", 41.7, 2.6, T(6, 0), IN_TRANSIT)),
                        updates((TRIP, "S", 180, None, None)))
        self.assertEqual(snap.stop_codes, {"15772-6": "S"})
        self.assertEqual(snap.next_stops, {"15772-6": ("Sant Celoni", T(6, 45))})
        self.assertEqual(snap.trip_delays, {"15772-6": 180})

    def test_the_update_stop_passed_moves_on_by_time(self):
        snap = self.one(positions((TRIP, "R11-15772", 41.5, 2.2, T(6, 50), IN_TRANSIT)),
                        updates((TRIP, "S", 0, None, None)), now=T(6, 50))
        self.assertEqual(snap.stop_codes, {"15772-6": "B"})

    def test_the_origin_is_never_next(self):
        snap = self.one(positions((TRIP, "R11-15772", 42.0, 3.0, T(5, 40), STOPPED)),
                        updates((TRIP, "F", 0, None, None)), now=T(5, 40))
        self.assertEqual(snap.stop_codes, {"15772-6": "G"})

    def test_without_an_update_the_timetable_and_no_delay(self):
        snap = self.one(positions((TRIP, "R11-15772", 41.9, 2.9, T(6, 0), IN_TRANSIT)))
        self.assertEqual(snap.next_stops, {"15772-6": ("Girona", T(6, 25))})
        self.assertEqual(snap.trip_delays, {})

    def test_an_update_with_no_delay_says_none(self):
        snap = self.one(positions((TRIP, "R11-15772", 41.9, 2.9, T(6, 0), IN_TRANSIT)),
                        updates((TRIP, "G", None, None, None)))
        self.assertEqual(snap.stop_codes, {"15772-6": "G"})
        self.assertEqual(snap.trip_delays, {})

    def test_an_update_stop_not_in_the_trip_is_ignored(self):
        snap = self.one(positions((TRIP, "R11-15772", 41.9, 2.9, T(6, 0), IN_TRANSIT)),
                        updates((TRIP, "X", 60, None, None)))
        self.assertEqual(snap.stop_codes, {"15772-6": "G"})
        self.assertEqual(snap.trip_delays, {"15772-6": 60})

    def test_after_the_last_stop_nothing_is_next(self):
        snap = self.one(positions((TRIP, "R11-15772", 41.4, 2.1, T(8, 30), STOPPED)), now=T(8, 30))
        self.assertEqual((snap.next_stops, snap.stop_codes), ({}, {}))

    def test_a_lost_update_file_keeps_the_last_for_ten_minutes(self):
        vp = positions((TRIP, "R11-15772", 41.9, 2.9, T(6, 0), IN_TRANSIT))
        self.one(vp, updates((TRIP, "G", 240, None, None)), now=T(6, 0))
        self.assertEqual(self.one(vp, None, now=T(6, 10)).trip_delays, {"15772-6": 240})
        self.assertEqual(self.one(vp, None, now=T(6, 10, 1)).trip_delays, {})

    def test_never_stalled(self):
        at = (41.8, 2.8)
        for m in range(0, 40, 1):
            snap = self.one(positions((TRIP, "R11-15772", *at, T(6, 25 + m), STOPPED)), now=T(6, 25 + m))
        self.assertNotIn("stalled", snap.extras["15772-6"])

    def test_a_fix_keeps_the_time_it_was_first_reported_there(self):
        # Renfe repeats a station's coordinates with each batch's time (Reus, 05:20-05:58).
        self.one(positions((TRIP, "R11-15772", 42.0, 3.0, T(5, 20), STOPPED)), now=T(5, 20))
        snap = self.one(positions((TRIP, "R11-15772", 42.0002, 3.0002, T(5, 40), STOPPED)), now=T(5, 40))
        o = snap.observations[0]
        self.assertEqual((o.lat, o.lon, o.observed_at.timestamp()), (42.0, 3.0, T(5, 20)))
        # Leaves Figueres 05:52, 32 minutes after that fix.
        self.assertEqual(snap.extras["15772-6"][base.TIMED_AFTER_KEY], 32 * 60)

    def test_a_move_over_50_m_is_a_new_fix(self):
        self.one(positions((TRIP, "R11-15772", 41.40, 2.10, T(6, 0), IN_TRANSIT)), now=T(6, 0))
        snap = self.one(positions((TRIP, "R11-15772", 41.4005, 2.10, T(6, 0, 30), IN_TRANSIT)), now=T(6, 0, 30))
        o = snap.observations[0]
        self.assertAlmostEqual(o.lat, 41.4005, places=5)
        self.assertEqual(o.observed_at.timestamp(), T(6, 0, 30))

    def test_a_late_train_leaves_its_station_late(self):
        snap = self.one(positions((TRIP, "R11-15772", 41.8, 2.7, T(6, 25), STOPPED)),
                        updates((TRIP, "S", 300, None, None)), now=T(6, 25))
        # Girona departs 06:27, +5 min: 06:32 less the fix's 06:25.
        self.assertEqual(snap.extras["15772-6"][base.TIMED_AFTER_KEY], 7 * 60)

    def test_between_stations_the_free_horizon(self):
        snap = self.one(positions((TRIP, "R11-15772", 41.7, 2.6, T(6, 30), IN_TRANSIT)), now=T(6, 30))
        self.assertEqual(snap.extras["15772-6"][base.TIMED_AFTER_KEY], src.FREE_HORIZON_S)

    def test_a_station_snap_is_within_300_m(self):
        # 0.0027 degrees of latitude is about 300 m.
        near = self.one(positions((TRIP, "R11-15772", 41.8026, 2.7, T(6, 20), STOPPED)), now=T(6, 20))
        self.assertEqual(near.extras["15772-6"][base.TIMED_AFTER_KEY], 420)
        self.rt = src.RenfeRealtime("Barcelona")
        far = self.one(positions((TRIP, "R11-15772", 41.8030, 2.7, T(6, 20), STOPPED)), now=T(6, 20))
        self.assertEqual(far.extras["15772-6"][base.TIMED_AFTER_KEY], src.FREE_HORIZON_S)

    def test_no_fix_time_the_free_horizon(self):
        self.assertEqual(self.rt._horizon(41.8, 2.7, None, [], 0, GEO), src.FREE_HORIZON_S)

    def test_a_stop_with_no_departure_leaves_at_its_arrival(self):
        rows = [(1, "G", T(6, 25), None)]
        self.assertEqual(self.rt._horizon(41.8, 2.7, T(6, 0), rows, 60, GEO), 26 * 60)

    def test_a_stop_with_neither_time_the_free_horizon(self):
        rows = [(1, "G", None, None)]
        self.assertEqual(self.rt._horizon(41.8, 2.7, T(6, 0), rows, 60, GEO), src.FREE_HORIZON_S)

    def test_a_run_is_forgotten_after_an_hour(self):
        self.one(positions((TRIP, "R11-15772", 42.0, 3.0, T(5, 59), IN_TRANSIT)), now=T(5, 59))
        self.one(positions(), now=T(7, 0))
        snap = self.one(positions((TRIP, "R11-15772", 41.9, 2.9, T(7, 1), INCOMING)), now=T(7, 1))
        self.assertEqual(snap.skipped, {"incoming": 1})


class TimedThroughTheEstimate(unittest.TestCase):
    """The adapter, Fleet and projection.apply together, as the coordinator runs them: a train whose
    fix stays on Figueres's coordinates moves on from 05:52 by the timetable."""

    def setUp(self):
        from saw_livetrack.gtfs import Fleet
        geometry = load("geometry")
        self.projection = load("projection")
        self.op = operators.OPERATORS["renfe_regionals_catalunya"]
        self.rt, self.fleet, self.proj = src.RenfeRealtime("Barcelona"), Fleet(**dict(self.op.fleet)), geometry.Projector(GEO)

    def at(self, now, lat=42.0, lon=3.0, tu=None, status=STOPPED):
        snap = self.rt.parse(positions((TRIP, "R11-15772", lat, lon, now - 5, status)), tu, now, GEO)
        res = self.fleet.update(snap.observations, now, next_stops=snap.next_stops, trip_delays=snap.trip_delays)
        self.projection.apply(self.proj, snap, res, now, self.op.derive_speed, self.op.timed_without_fix,
                              self.op.timed_after_s)
        return res["vehicles"]["15772-6"]

    def test_before_its_departure_at_the_station(self):
        self.at(T(5, 40))
        rec = self.at(T(5, 51))
        self.assertAlmostEqual(rec["latitude"], 42.0, places=4)

    def test_after_it_on_toward_girona_and_there_at_its_time(self):
        self.at(T(5, 40))
        self.at(T(5, 51))
        a = self.at(T(6, 5))["latitude"]
        b = self.at(T(6, 15))["latitude"]
        self.assertLess(a, 42.0 - 0.01)
        self.assertLess(b, a)
        self.assertGreater(b, 41.8)
        self.assertAlmostEqual(self.at(T(6, 25))["latitude"], 41.8, places=3)
        self.assertEqual(self.at(T(6, 26))["position_source"], "estimated")

    def test_late_it_leaves_late(self):
        tu = updates((TRIP, "G", 600, None, None))
        self.at(T(5, 40), tu=tu)
        rec = self.at(T(6, 1), tu=tu)
        self.assertAlmostEqual(rec["latitude"], 42.0, places=4)
        self.assertLess(self.at(T(6, 10), tu=tu)["latitude"], 42.0 - 0.01)


class Keys(unittest.TestCase):
    def test_records_only_keys_never_reach_the_map(self):
        for key in ("route_color", "toward_hub"):
            self.assertIn(key, base.EXTRA_KEYS)
            self.assertIn(key, base.RECORD_ONLY_KEYS)


def renfe_zip(*subs):
    """A Renfe-shaped timetable: padded fields (05 B5), an R11 trip on 2026-11-06 and one on 11-20,
    an R13 bus route, Barcelona's commuter R1, Madrid's C5. `subs`: (old, new) text replacements."""
    pad = lambda *cells: ",".join(f" {c} " for c in cells) + "\n"
    files = {
        "agency.txt": pad("agency_id", "agency_name", "agency_url", "agency_timezone")
                      + pad("1071", "Renfe", "https://renfe.com", "Europe/Madrid"),
        "routes.txt": pad("route_id", "agency_id", "route_short_name", "route_long_name", "route_type",
                          "route_color", "route_text_color")
                      + pad("51T0093R11", "1071", "R11", "Figueres -Barcelona-Sants", "2", "0069AA", "FFFFFF")
                      + pad("51T0185R13", "1071", "R13", "La Plana -Lleida", "3", "146520", "FFFFFF")
                      + pad("51T0001R1", "1071", "R1", "Molins -Macanet", "2", "73B0DF", "FFFFFF")
                      + pad("10T0001C5", "1071", "C5", "Mostoles -Humanes", "2", "F2C100", "FFFFFF"),
        "calendar.txt": pad("service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
                            "sunday", "start_date", "end_date")
                        + pad("5109V", 0, 0, 0, 0, 1, 0, 0, "20261106", "20261106")
                        + pad("5123V", 0, 0, 0, 0, 1, 0, 0, "20261120", "20261120")
                        + pad("1009V", 0, 0, 0, 0, 1, 0, 0, "20261106", "20261106"),
        "trips.txt": pad("route_id", "service_id", "trip_id", "trip_headsign", "shape_id")
                     + pad("51T0093R11", "5109V", "5109V15772R11", "Barcelona-Sants", "SH11")
                     + pad("51T0093R11", "5123V", "5123V15772R11", "Barcelona-Sants", "SH11")
                     + pad("51T0185R13", "5109V", "5109V99999R13", "Lleida", "SH13")
                     + pad("51T0001R1", "5109V", "5109V25000R1", "Macanet", "SH1")
                     + pad("10T0001C5", "1009V", "1009V23743C5", "Humanes", "SH5"),
        "stop_times.txt": pad("trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence")
                          + pad("5109V15772R11", "05:52:00", "05:52:00", "79309", 1)
                          + pad("5109V15772R11", "07:55:00", "07:55:00", "71801", 2)
                          + pad("5123V15772R11", "05:52:00", "05:52:00", "79309", 1)
                          + pad("5123V15772R11", "07:55:00", "07:55:00", "71801", 2)
                          + pad("5109V99999R13", "05:00:00", "05:00:00", "B1", 1)
                          + pad("5109V99999R13", "06:00:00", "06:00:00", "B2", 2)
                          + pad("5109V25000R1", "05:00:00", "05:00:00", "R1A", 1)
                          + pad("5109V25000R1", "06:00:00", "06:00:00", "R1B", 2)
                          + pad("1009V23743C5", "05:00:00", "05:00:00", "C5A", 1)
                          + pad("1009V23743C5", "06:00:00", "06:00:00", "C5B", 2),
        "stops.txt": pad("stop_id", "stop_name", "stop_lat", "stop_lon")
                     + pad("79309", "Figueres", "42.265", "2.969") + pad("71801", "Barcelona-Sants", "41.379", "2.141")
                     + pad("B1", "La Plana", "41.3", "1.2") + pad("B2", "Lleida", "41.6", "0.6")
                     + pad("R1A", "Molins", "41.4", "2.0") + pad("R1B", "Macanet", "41.7", "2.7")
                     + pad("C5A", "Mostoles", "40.3", "-3.8") + pad("C5B", "Humanes", "40.2", "-3.8"),
        "shapes.txt": pad("shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence")
                      + pad("SH11", "42.265", "2.969", 1) + pad("SH11", "41.379", "2.141", 2)
                      + pad("SH13", "41.3", "1.2", 1) + pad("SH13", "41.6", "0.6", 2)
                      + pad("SH1", "41.4", "2.0", 1) + pad("SH1", "41.7", "2.7", 2)
                      + pad("SH5", "40.3", "-3.8", 1) + pad("SH5", "40.2", "-3.8", 2),
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            for old, new in subs:
                text = text.replace(old, new)
            z.writestr(name, text)
    return buf.getvalue()


class Client:
    def __init__(self, raw):
        self.raw = raw

    def static_zip(self):
        return self.raw


class Timetable(unittest.TestCase):
    def view(self, raw=None, today="2026-11-06"):
        self.day = today
        return src.StaticView(Client(renfe_zip() if raw is None else raw), today=lambda: self.day)

    def test_no_version_before_the_client_has_a_zip(self):
        v = src.StaticView(Client(None), today=lambda: "2026-11-06")
        self.assertIsNone(v.static_version())
        self.assertIsNone(v.distill_geometry())
        self.assertIsNone(v.static_path())

    def test_the_version_is_the_zips_digest_and_spains_date(self):
        v = self.view()
        a = v.static_version()
        self.assertTrue(a.endswith(":2026-11-06"))
        self.assertEqual(v.static_version(), a)
        self.day = "2026-11-07"
        self.assertNotEqual(v.static_version(), a)
        same = bytes(bytearray(v.client.raw))
        self.assertIsNot(same, v.client.raw)
        v.client.raw = same   # equal bytes, a new object: the same digest
        self.assertEqual(v.static_version().split(":")[0], a.split(":")[0])
        v.client.raw = same.replace(b"Figueres ", b"Figueras ")
        self.assertNotEqual(v.static_version().split(":")[0], a.split(":")[0])

    def test_only_the_regional_rail_trips_of_the_window(self):
        d = self.view().distill_geometry()
        self.assertEqual(sorted(d["trains"]), ["5109V15772R11"])
        self.assertEqual(d["trip_numbers"], {"5109V15772R11": "R11"})
        self.assertEqual(d["trip_dates"], {"5109V15772R11": "20261106"})
        self.assertEqual(d["line_colours"], {"R11": "#0069AA"})
        self.assertEqual(d["trip_stops"]["5109V15772R11"],
                         [[1, "79309", 21120, 21120], [2, "71801", 28500, 28500]])
        self.assertEqual(d["stop_names"], {"79309": "Figueres", "71801": "Barcelona-Sants"})
        self.assertEqual(sorted(d["shapes"]), ["SH11"])

    def test_the_window_moves_with_the_date(self):
        d = self.view(today="2026-11-20").distill_geometry()
        self.assertEqual(sorted(d["trains"]), ["5123V15772R11"])

    def test_a_service_over_many_dates_has_no_date(self):
        raw = renfe_zip((" 5109V , 0 , 0 , 0 , 0 , 1 , 0 , 0 , 20261106 , 20261106 ",
                         " 5109V , 1 , 1 , 1 , 1 , 1 , 1 , 1 , 20261101 , 20261130 "))
        d = self.view(raw).distill_geometry()
        self.assertIn("5109V15772R11", d["trains"])
        self.assertEqual(d["trip_dates"], {})

    def test_regional_zip_strips_the_padding(self):
        from saw_livetrack.gtfs.filter import keep_service_window
        cut = src.regional_zip(keep_service_window(renfe_zip(), route_types=("2",),
                                                   today=dt.date(2026, 11, 6), route_prefixes=("51",)))
        z = zipfile.ZipFile(io.BytesIO(cut))
        self.assertTrue(z.read("trips.txt").decode().startswith("route_id,service_id,trip_id,"))
        self.assertNotIn(b" ,", z.read("stop_times.txt"))
        self.assertEqual(z.read("routes.txt").decode().count("\n"), 2)

    def test_regional_zip_alone_keeps_rail_on_the_regional_lines_of_network_51(self):
        z = zipfile.ZipFile(io.BytesIO(src.regional_zip(renfe_zip())))
        trips = z.read("trips.txt").decode().splitlines()[1:]
        self.assertEqual(sorted(t.split(",")[2] for t in trips), ["5109V15772R11", "5123V15772R11"])
        self.assertEqual(sorted(r.split(",")[0] for r in z.read("stops.txt").decode().splitlines()[1:]),
                         ["71801", "79309"])
        self.assertEqual(sorted(r.split(",")[0] for r in z.read("calendar.txt").decode().splitlines()[1:]),
                         ["5109V", "5123V"])

    def test_a_trip_against_its_shape_gets_it_reversed(self):
        d = {"stops": {"A": [42.0, 3.0], "M": [41.7, 2.55], "B": [41.4, 2.1]},
             "shapes": {"S": [[42.0, 3.0], [41.7, 2.55], [41.4, 2.1]]},
             "trains": {"down": ["S"], "up": ["S"], "bare": ["S"], "lost": ["X"], "mid": ["S"]},
             "trip_stops": {"down": [[1, "A", 0, 0], [2, "B", 60, 60]], "up": [[1, "B", 0, 0], [2, "A", 60, 60]],
                            "lost": [[1, "B", 0, 0], [2, "A", 60, 60]], "mid": [[1, "M", 0, 0], [2, "B", 60, 60]]}}
        self.assertEqual(src.orient(d), 1)
        self.assertEqual(d["trains"], {"down": ["S"], "up": ["S~r"], "bare": ["S"], "lost": ["X"], "mid": ["S"]})
        self.assertEqual(d["shapes"]["S~r"], [[41.4, 2.1], [41.7, 2.55], [42.0, 3.0]])
        self.assertEqual(d["shapes"]["S"], [[42.0, 3.0], [41.7, 2.55], [41.4, 2.1]])

    def test_a_stop_not_in_the_stops_is_left_alone(self):
        d = {"stops": {"A": [42.0, 3.0]}, "shapes": {"S": [[42.0, 3.0], [41.4, 2.1]]}, "trains": {"up": ["S"]},
             "trip_stops": {"up": [[1, "B", 0, 0], [2, "A", 60, 60]]}}
        self.assertEqual(src.orient(d), 0)

    def test_the_distill_orients(self):
        raw = renfe_zip((" SH11 , 42.265 , 2.969 , 1 ", " SH11 , 42.265 , 2.969 , 3 "))
        d = self.view(raw).distill_geometry()
        self.assertEqual(d["trains"]["5109V15772R11"], ["SH11~r"])
        self.assertEqual(d["shapes"]["SH11~r"][0], [42.265, 2.969])

    def test_a_line_colour_must_be_six_hex_digits(self):
        raw = renfe_zip((" 0069AA ", " blue "))
        self.assertEqual(self.view(raw).distill_geometry()["line_colours"], {})


class Operator(unittest.TestCase):
    op = operators.OPERATORS["renfe_regionals_catalunya"]

    def test_the_entry(self):
        op = self.op
        self.assertEqual((op.name, op.short, op.regions, op.source),
                         ("Renfe Regionals (Catalunya)", "Renfe Regionals", ("ES",), "renfe"))
        self.assertEqual(dict(op.source_options), {"consumer": "intercity", "hub": "Barcelona"})
        self.assertEqual(op.attribution, "Data: Renfe (data.renfe.com), CC BY 4.0")
        self.assertEqual(op.terms_url, "https://data.renfe.com/")
        self.assertTrue(op.gtfs_from_source)
        self.assertFalse(op.needs_key or op.gtfs_stream)
        # Outside Barcelona a position is a station: timed between them (sources/renfe.py).
        self.assertTrue(op.derive_speed and op.timed_without_fix)
        self.assertEqual(op.timed_after_s, 120.0)
        self.assertIsNone(op.gtfs_url)
        self.assertEqual(op.scan_interval_s, 30)

    def test_spain_is_offered(self):
        self.assertEqual(operators.regions_in_use()["ES"], "Spain")
        self.assertEqual([o.id for o in operators.operators_in("ES")], ["renfe_regionals_catalunya"])

    def test_late_from_10_very_late_from_20(self):
        self.assertEqual(self.op.lateness_for({"train": "15772", "line_name": "R16"}),
                         {"late_threshold_min": 10, "very_late_threshold_min": 20})

    def look(self, **rec):
        return self.op.marker_keys(rec)

    def test_leaving_barcelona_the_line_colour(self):
        k = self.look(train="15772", line_name="R11", route_color="#0069AA", toward_hub=False)
        self.assertEqual(k, {"marker_color": "#0069AA", "marker_ring_color": "#FFFFFF", "marker_ring_width": 3,
                             "marker_label_color": "#FFFFFF", "marker_label_outline_color": "none",
                             "marker_arrow_color": "#0069AA", "marker_arrow_outline_color": "#FFFFFF"})

    def test_going_to_it_white(self):
        k = self.look(train="15772", line_name="R11", route_color="#0069AA", toward_hub=True)
        self.assertEqual((k["marker_color"], k["marker_ring_color"], k["marker_label_color"],
                          k["marker_arrow_color"], k["marker_arrow_outline_color"]),
                         ("#FFFFFF", "#0069AA", "#0069AA", "#FFFFFF", "#0069AA"))

    def test_the_sources_answer_wins_over_the_number(self):
        k = self.look(train="18121", line_name="R16", route_color="#B52B46", toward_hub=True)
        self.assertEqual(k["marker_color"], "#FFFFFF")

    def test_neither_end_in_barcelona_the_number_says(self):
        self.assertEqual(self.look(train="18120", line_name="R16", route_color="#B52B46")["marker_color"], "#FFFFFF")
        self.assertEqual(self.look(train="18121", line_name="R16", route_color="#B52B46")["marker_color"], "#B52B46")
        for line in ("R13", "R14", "R15", "R17"):
            self.assertEqual(self.look(train="2", line_name=line, route_color="#000001")["marker_color"], "#FFFFFF")

    def test_r11s_number_says_nothing(self):
        self.assertEqual(self.look(train="15772", line_name="R11", route_color="#0069AA")["marker_color"], "#0069AA")
        self.assertEqual(self.look(train="15772", line_name="R12", route_color="#0069AA")["marker_color"], "#0069AA")

    def test_no_number_or_no_line(self):
        self.assertEqual(self.look(train=None, line_name="R16", route_color="#B52B46")["marker_color"], "#B52B46")
        self.assertEqual(self.look(train="18120", route_color="#B52B46")["marker_color"], "#B52B46")

    def test_no_colour_renfes_purple(self):
        self.assertEqual(self.look(train="15773", line_name="R12")["marker_color"], "#8A0072")

    def test_the_looks_keys_reach_the_map_and_its_inputs_do_not(self):
        rec = {"vehicle_id": "15772-6", "marker_label": "15772", "in_service": True, "train": "15772",
               "line_name": "R11", "route_color": "#0069AA", "toward_hub": True}
        rec.update(self.look(**rec))
        out = attributes.to_attributes(rec, "renfe_regionals_catalunya")
        self.assertEqual(out["line_name"], "R11")
        self.assertNotIn("route_color", out)
        self.assertNotIn("toward_hub", out)
        self.assertEqual(out["marker_color"], "#FFFFFF")


class FakeRenfe:
    def __init__(self, raw):
        self.raw, self.calls = raw, 0

    def static_zip(self):
        return self.raw


class RouteStoreOwnDistill(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.hass = _ha_stub.Hass(self.dir)
        self.op = operators.OPERATORS["renfe_regionals_catalunya"]

    def store(self, raw):
        s = route_store.RouteStore(self.hass, None, self.op)
        view = src.StaticView(FakeRenfe(raw), today=lambda: "2026-11-06")
        s.static_client = view
        s.note_static(view.static_version())
        return s, view

    def test_the_view_distills_and_the_version_is_kept(self):
        s, view = self.store(renfe_zip())
        run(s.async_refresh())
        g = s.projector.geometry
        self.assertEqual(g["source_version"], view.static_version())
        self.assertEqual(g["trip_dates"], {"5109V15772R11": "20261106"})
        self.assertEqual(g["source"], "shared client")

    def test_nothing_before_the_client_has_a_zip(self):
        s, _ = self.store(None)
        self.assertFalse(s._stale(0.0))
        run(s.async_refresh())
        self.assertIsNone(s.projector)

    def test_a_restart_reads_the_copy_and_a_new_day_cuts_again(self):
        s, view = self.store(renfe_zip())
        run(s.async_refresh())
        s2, view2 = self.store(renfe_zip())
        s2.note_static(view.static_version())
        run(s2.async_load_cached())
        self.assertFalse(s2._stale(0.0))
        s2.note_static(view.static_version().split(":")[0] + ":2026-11-07")
        self.assertTrue(s2._stale(0.0))


class Coordinator(unittest.TestCase):
    def make(self, read=None):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        hass = _ha_stub.Hass(self.dir)
        entry = types.SimpleNamespace(data={"operator": "renfe_regionals_catalunya"}, options={},
                                      domain=const.DOMAIN)
        if read is not None:
            self.addCleanup(setattr, src, "read", src.read)
            src.read = read
        op = operators.OPERATORS["renfe_regionals_catalunya"]
        return coordinator.IntercityRailCoordinator(hass, entry, op), hass

    def test_registers_intercity_with_the_shared_client(self):
        c, hass = self.make()
        self.assertEqual(c._renfe_client.consumers, {"intercity"})
        self.assertEqual(hass.data["saw_renfe_v1"]["consumers"], {"intercity": 1})
        self.assertIs(c.routes.static_client, c._renfe_view)
        self.assertIs(c._renfe_view.client, c._renfe_client)
        self.assertEqual(c._renfe.hub, "Barcelona")

    def test_finds_commuter_rails_client(self):
        from saw_livetrack import renfe as lib
        hass = _ha_stub.Hass(tempfile.gettempdir())
        theirs = lib.RenfeClient(consumers=("commuter",))
        hass.data["saw_renfe_v1"] = {"contract_version": lib.CONTRACT_VERSION, "entry_shape": 1,
                                     "client": theirs, "refcount": 1, "consumers": {"commuter": 1}}
        entry = types.SimpleNamespace(data={"operator": "renfe_regionals_catalunya"}, options={},
                                      domain=const.DOMAIN)
        c = coordinator.IntercityRailCoordinator(hass, entry, operators.OPERATORS["renfe_regionals_catalunya"])
        self.assertIs(c._renfe_client, theirs)
        self.assertEqual(theirs.consumers, {"commuter", "intercity"})
        c.async_release()
        self.assertEqual(theirs.consumers, {"commuter"})
        self.assertEqual(hass.data["saw_renfe_v1"]["consumers"], {"commuter": 1})

    def test_release_unregisters(self):
        c, hass = self.make()
        c.async_release()
        self.assertNotIn("saw_renfe_v1", hass.data)
        self.assertIsNone(c.routes.static_client)
        c.async_release()   # idempotent

    def test_a_failure_is_ridden_out(self):
        from saw_livetrack import renfe as lib

        def read(client, consumer, view):
            raise lib.FeedUnavailable("HTTP 503 from x")
        c, _ = self.make(read)
        self.assertIsNone(run(c._fetch()))
        self.assertIn("HTTP 503", c._last_reason)

    def test_a_429_too(self):
        from saw_livetrack import renfe as lib

        def read(client, consumer, view):
            raise lib.RateLimited("HTTP 429 from x")
        c, _ = self.make(read)
        self.assertIsNone(run(c._fetch()))
        self.assertIn("RateLimited", c._last_reason)

    def test_a_good_read_notes_the_version_and_parses(self):
        seen = []

        def read(client, consumer, view):
            seen.append((client, consumer, view))
            return positions(), None, "v7"
        c, _ = self.make(read)
        snap = run(c._fetch())
        self.assertEqual(snap.observations, [])
        self.assertEqual(c.routes._static_version, "v7")
        self.assertEqual(seen, [(c._renfe_client, "intercity", c._renfe_view)])

    def test_read_asks_the_client_and_the_view(self):
        class C:
            def for_consumer(self, consumer):
                return ("vp", "tu") if consumer == "intercity" else None

        class V:
            def static_version(self):
                return "v9"
        self.assertEqual(src.read(C(), "intercity", V()), ("vp", "tu", "v9"))
        self.assertEqual(src.read(C(), "intercity"), ("vp", "tu", None))

    def test_other_railroads_are_not_sent_here(self):
        hass = _ha_stub.Hass(tempfile.gettempdir())
        entry = types.SimpleNamespace(data={"operator": "vr"}, options={}, domain=const.DOMAIN)
        c = coordinator.IntercityRailCoordinator(hass, entry, operators.OPERATORS["vr"])
        self.assertIsNone(c._renfe)
        self.assertIsNone(c._renfe_client)
        c.async_release()


class Setup(unittest.TestCase):
    def test_spain_needs_no_key(self):
        f = flow.IntercityRailConfigFlow()
        f._ids = ()
        f.hass = _ha_stub.Hass(tempfile.gettempdir())
        run(f.async_step_user({"region": "ES"}))
        s = run(f.async_step_operator({"operator": "renfe_regionals_catalunya"}))
        self.assertEqual(s["type"], "create_entry")
        self.assertEqual(s["data"], {"operator": "renfe_regionals_catalunya"})
        self.assertEqual(s["title"], "Renfe Regionals (Catalunya)")
