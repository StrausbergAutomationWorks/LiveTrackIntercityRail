"""SJ Nord on Entur's SIRI ET (Intercity SSOT 8.8, "SJ NORD"; Lee 2026-11-08 10:59 CST: "Build SJ Nord from its
expected times, actuals as a correction"): sources/entur_et.py, its operator, and the estimate it feeds.
Run from the repo root: python -m unittest tests.test_entur_et_source
"""

import datetime as dt
import io
import pathlib
import sys
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _load import load  # noqa: E402

from saw_livetrack import entur as lib  # noqa: E402

ent = load("sources.entur")
et = load("sources.entur_et")
base = load("sources.base")
operators = load("operators")

OSLO = dt.timezone(dt.timedelta(hours=1))       # CET on 2026-11-08
DAY = dt.date(2026, 11, 8)
A, B, C = (63.30, 10.30), (63.40, 10.40), (63.50, 10.50)


def epoch(h, m=0, s=0):
    return dt.datetime(DAY.year, DAY.month, DAY.day, h, m, s, tzinfo=OSLO).timestamp()


def sjn_zip():
    """A small SJ Nord-like timetable: R70 train 453 A - B - C (two variants of the number: one by A, B, C; one by
    other quays), F7 train 475."""
    files = {
        "agency.txt": "agency_id,agency_name,agency_url,agency_timezone\nSJN,SJ Nord,https://www.sj.no,Europe/Oslo\n",
        "routes.txt": ("route_id,agency_id,route_short_name,route_long_name,route_type,route_color\n"
                       "SJN:Line:R70,SJN,R70,Lundamo-Trondheim S-Steinkjer,100,E13E2E\n"
                       "SJN:Line:F7,SJN,F7,Trondheim S-Bodo,100,285DA9\n"),
        "calendar_dates.txt": "service_id,date,exception_type\nS8,20261108,1\n",
        "trips.txt": ("route_id,trip_id,service_id,trip_headsign,shape_id\n"
                      "SJN:Line:R70,SJN:ServiceJourney:453-X_1,S8,Elsewhere,SH9\n"
                      "SJN:Line:R70,SJN:ServiceJourney:453-ABC_2,S8,C,SH1\n"
                      "SJN:Line:F7,SJN:ServiceJourney:475-ABC_3,S8,C,SH1\n"),
        "stops.txt": ("stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station\n"
                      "NSR:StopPlace:1,A stasjon,63.30,10.30,1,\n"
                      "NSR:Quay:1,A stasjon,63.30,10.30,0,NSR:StopPlace:1\n"
                      "NSR:StopPlace:2,B stasjon,63.40,10.40,1,\n"
                      "NSR:Quay:2,B stasjon,63.40,10.40,0,NSR:StopPlace:2\n"
                      "NSR:StopPlace:3,C stasjon,63.50,10.50,1,\n"
                      "NSR:Quay:3,C stasjon,63.50,10.50,0,NSR:StopPlace:3\n"
                      "NSR:Quay:8,X stasjon,62.00,9.00,0,\n"
                      "NSR:Quay:9,Y stasjon,62.10,9.10,0,\n"),
        "stop_times.txt": ("trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type\n"
                           "SJN:ServiceJourney:453-X_1,10:00:00,10:00:00,NSR:Quay:8,1,0,0\n"
                           "SJN:ServiceJourney:453-X_1,10:30:00,10:30:00,NSR:Quay:9,2,0,0\n"
                           "SJN:ServiceJourney:453-ABC_2,10:00:00,10:00:00,NSR:Quay:1,1,0,0\n"
                           "SJN:ServiceJourney:453-ABC_2,10:20:00,10:22:00,NSR:Quay:2,2,0,0\n"
                           "SJN:ServiceJourney:453-ABC_2,10:42:00,10:42:00,NSR:Quay:3,3,0,0\n"
                           "SJN:ServiceJourney:475-ABC_3,12:00:00,12:00:00,NSR:Quay:1,1,0,0\n"
                           "SJN:ServiceJourney:475-ABC_3,12:30:00,12:30:00,NSR:Quay:3,2,0,0\n"),
        "shapes.txt": ("shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n"
                       "SH1,63.30,10.30,1\nSH1,63.40,10.40,2\nSH1,63.50,10.50,3\n"
                       "SH9,62.00,9.00,1\nSH9,62.10,9.10,2\n"),
        "feed_info.txt": "feed_publisher_name,feed_publisher_url,feed_lang\nEntur,https://www.entur.org,no\n",
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for k, v in files.items():
            z.writestr(k, v)
    return buf.getvalue()


GEO = None


def geo():
    global GEO
    if GEO is None:
        GEO = ent.distill(sjn_zip(), lib.INTERCITY_LETTERS, {}, DAY)
    return GEO


def call(order, stop, name, aa=None, ad=None, ea=None, ed=None, xa=None, xd=None, recorded=False, cancelled=False):
    return {"order": order, "stop": stop, "name": name, "recorded": recorded, "cancelled": cancelled,
            "aimed_arrival": aa, "aimed_departure": ad, "expected_arrival": ea, "expected_departure": ed,
            "actual_arrival": xa, "actual_departure": xd}


def journey(calls, number="453", date="20261108", line="R70", cancelled=False):
    return {"id": f"{number}:{date[:4]}-{date[4:6]}-{date[6:]}", "number": number, "date": date, "line": line,
            "cancelled": cancelled, "calls": calls}


def r70(xd_a=None, ea_b=None, ed_b=None, xa_b=None, xd_b=None, ea_c=None, ed_a=None):
    """Train 453 A 10:00 - B 10:20/10:22 - C 10:42, with what the feed says."""
    return journey([
        call(1, "NSR:Quay:1", "A", ad=epoch(10), ed=ed_a, xd=xd_a, recorded=xd_a is not None),
        call(2, "NSR:Quay:2", "B", aa=epoch(10, 20), ad=epoch(10, 22), ea=ea_b, ed=ed_b, xa=xa_b, xd=xd_b,
             recorded=xa_b is not None),
        call(3, "NSR:Quay:3", "C", aa=epoch(10, 42), ea=ea_c),
    ])


class TestCallTimes(unittest.TestCase):
    def test_actual_over_expected_over_aimed(self):
        c = call(1, "q", "n", aa=100.0, ad=110.0, ea=200.0, ed=210.0, xa=300.0)
        (_, arr, dep, known), = et.call_times([c])
        self.assertEqual((arr, dep, known), (300.0, 300.0, True))   # actual arr; expected dep 210, never before it
        (_, arr, dep, _), = et.call_times([call(1, "q", "n", aa=100.0, ad=110.0, ea=200.0, ed=210.0)])
        self.assertEqual((arr, dep), (200.0, 210.0))
        (_, arr, dep, known), = et.call_times([call(1, "q", "n", aa=100.0, ad=110.0)])
        self.assertEqual((arr, dep, known), (100.0, 110.0, False))

    def test_a_passed_call_with_no_actual_carries_the_delay_known_before_it(self):
        # A RecordedCall has aimed and actual times only (measured): with no actual, the delay before it.
        t = et.call_times([call(1, "a", "A", ad=1000.0, xd=1120.0, recorded=True),
                           call(2, "b", "B", aa=2000.0, ad=2060.0, recorded=True)])
        self.assertEqual((t[1][1], t[1][2], t[1][3]), (2120.0, 2180.0, False))

    def test_an_arrival_alone_carries_its_delay(self):
        # An actual arrival with no departure word (a third of calls get no actual departure): its delay goes on.
        t = et.call_times([call(1, "a", "A", ad=1000.0),
                           call(2, "b", "B", aa=2000.0, xa=2300.0),
                           call(3, "c", "C", aa=3000.0, ad=3060.0)])
        self.assertEqual((t[2][1], t[2][2]), (3300.0, 3360.0))

    def test_expected_resets_the_carried_delay(self):
        t = et.call_times([call(1, "a", "A", ad=1000.0, xd=1300.0),
                           call(2, "b", "B", aa=2000.0, ad=2060.0, ea=2030.0, ed=2090.0),
                           call(3, "c", "C", aa=3000.0)])
        self.assertEqual(t[2][1], 3030.0)

    def test_cancelled_and_timeless_calls_are_left_out(self):
        t = et.call_times([call(1, "a", "A", ad=1000.0), call(2, "b", "B", aa=2000.0, cancelled=True),
                           call(3, "c", "C"), call(4, "d", "D", aa=4000.0)])
        self.assertEqual([x[0]["stop"] for x in t], ["a", "d"])

    def test_an_arrival_faster_than_any_train_is_not_believed(self):
        # F7 478 (measured): expected at Bjerka at its expected departure from Mo i Rana, 25 minutes scheduled.
        t = et.call_times([call(1, "a", "A", ad=1000.0, ed=1006.0),
                           call(2, "b", "B", aa=2530.0, ad=2560.0, ea=1006.0, ed=2560.0)])
        self.assertEqual((t[1][1], t[1][3]), (2536.0, False))      # aimed plus the delay known before it
        # At the floor it is believed (RUN_FLOOR of 1530 s is 459 s).
        t = et.call_times([call(1, "a", "A", ad=1000.0, ed=1006.0),
                           call(2, "b", "B", aa=2530.0, ad=2560.0, ea=1006.0 + 0.3 * 1530.0 + 1, ed=2560.0)])
        self.assertEqual(t[1][3], True)

    def test_departure_never_before_arrival(self):
        (_, arr, dep, _), = et.call_times([call(1, "a", "A", aa=100.0, ad=120.0, xa=200.0)])
        self.assertEqual((arr, dep), (200.0, 200.0))


class TestPlace(unittest.TestCase):
    T = None

    def setUp(self):
        self.t = et.call_times(r70()["calls"])

    def test_not_out_before_its_origin(self):
        self.assertIsNone(et.place(self.t, epoch(10) - et.PRE_DEPARTURE_S - 1))
        self.assertEqual(et.place(self.t, epoch(10) - et.PRE_DEPARTURE_S + 1), ("standing", 0))

    def test_running_after_a_departure(self):
        self.assertEqual(et.place(self.t, epoch(10, 5)), ("running", 0))

    def test_standing_between_arrival_and_departure(self):
        self.assertEqual(et.place(self.t, epoch(10, 21)), ("standing", 1))

    def test_moves_on_by_its_times_without_an_actual(self):
        self.assertEqual(et.place(self.t, epoch(10, 23)), ("running", 1))

    def test_at_its_last_call_then_gone(self):
        self.assertEqual(et.place(self.t, epoch(10, 44)), ("standing", 2))
        self.assertIsNone(et.place(self.t, epoch(10, 42) + et.FINISHED_S + 1))

    def test_nothing_without_times(self):
        self.assertIsNone(et.place([], epoch(10)))


class TestParse(unittest.TestCase):
    def parse(self, journeys, now):
        return et.EnturEtRealtime().parse(journeys, now, geo())

    def test_running_is_timed_from_the_stop_it_left_to_the_next(self):
        snap = self.parse([r70(xd_a=epoch(10, 1), ea_b=epoch(10, 21))], epoch(10, 10))
        o, = snap.observations
        self.assertEqual((o.vehicle_id, o.train, (o.lat, o.lon)), ("453-8", "453", A))
        self.assertEqual(o.observed_at.timestamp(), epoch(10, 1))
        ex = snap.extras["453-8"]
        self.assertIs(ex[base.NO_FIX_KEY], True)
        self.assertEqual((ex[base.HELD_SPEED_KEY], ex[base.TIMED_AFTER_KEY], ex[base.AIM_ETA_KEY]),
                         (None, 0.0, epoch(10, 21)))
        self.assertEqual(snap.stop_codes["453-8"], "NSR:Quay:2")
        self.assertEqual(snap.next_stops["453-8"], ("B stasjon", epoch(10, 21)))
        self.assertEqual(snap.trip_delays["453-8"], 60)
        self.assertEqual(snap.route_keys["453-8"], "SJN:ServiceJourney:453-ABC_2")     # the variant by its stops
        self.assertEqual((ex["route_code"], ex["route_color"]), ("R70", "E13E2E"))
        self.assertTrue(ex["line_name"].startswith("Train 453"))

    def test_standing_is_held(self):
        snap = self.parse([r70(xd_a=epoch(10, 1), xa_b=epoch(10, 20, 30))], epoch(10, 21))
        o, = snap.observations
        self.assertEqual((o.lat, o.lon), B)
        self.assertEqual(o.observed_at.timestamp(), epoch(10, 20, 30))     # placed there when it arrived
        ex = snap.extras["453-8"]
        for k, v in ent.HOLD.items():
            self.assertEqual(ex[k], v)
        self.assertEqual(snap.stop_codes["453-8"], "NSR:Quay:3")

    def test_a_carried_delay_is_not_said(self):
        snap = self.parse([r70(xd_a=epoch(10, 3))], epoch(10, 10))
        self.assertNotIn("453-8", snap.trip_delays)
        self.assertEqual(snap.next_stops["453-8"][1], epoch(10, 23))    # but the train is timed by it

    def test_cancelled_unknown_stop_and_off_hours_are_skipped(self):
        far = journey([call(1, "NSR:Quay:404", "Nowhere", ad=epoch(10)), call(2, "NSR:Quay:3", "C", aa=epoch(11))],
                      number="999")
        cancelled = journey(r70()["calls"], cancelled=True)
        snap = self.parse([cancelled, far, r70()], epoch(9))
        # 453 at 09:00 is an hour before it leaves; 999 too.
        self.assertEqual(snap.skipped, {"cancelled": 1, "not_running": 2})
        snap = self.parse([far], epoch(10, 5))
        self.assertEqual(snap.skipped, {"no_stop_position": 1})

    def test_none_and_quiet(self):
        self.assertIsNone(self.parse(None, epoch(10)))
        self.assertEqual(self.parse([], epoch(10)).observations, [])

    def test_one_run_once(self):
        snap = self.parse([r70(), r70()], epoch(10, 5))
        self.assertEqual((len(snap.observations), snap.skipped), (1, {"duplicate": 1}))

    def test_a_quay_the_timetable_lacks_is_found_on_the_trip(self):
        # Melhus' NSR:Quay:111911 is in no SJ Nord timetable (measured): by its name on the matched trip ...
        calls = r70(xd_a=epoch(10, 1))["calls"]
        calls[1] = dict(calls[1], stop="NSR:Quay:111911", name="B")
        snap = self.parse([journey(calls)], epoch(10, 10))
        self.assertEqual(snap.stop_codes["453-8"], "NSR:Quay:2")
        self.assertEqual(snap.next_stops["453-8"][0], "B stasjon")
        snap = self.parse([journey(calls)], epoch(10, 21))
        self.assertEqual((snap.observations[0].lat, snap.observations[0].lon), B)
        # ... else by its Order, when the trip has as many stops as the journey has calls ...
        calls[1] = dict(calls[1], name="Melhus")
        snap = self.parse([journey(calls)], epoch(10, 21))
        self.assertEqual((snap.observations[0].lat, snap.observations[0].lon), B)
        # ... and not when it has not.
        snap = self.parse([journey(calls + [call(4, "NSR:Quay:3", "C", aa=epoch(11))])], epoch(10, 21))
        self.assertEqual(snap.skipped, {"no_stop_position": 1})

    def test_stop_of_name_must_be_unique(self):
        rows = [(1, "NSR:Quay:1", 0, 0), (2, "NSR:Quay:2", 0, 0)]
        names = {"NSR:Quay:1": "Bø stasjon", "NSR:Quay:2": "Bø sentrum"}
        stops = {"NSR:Quay:1": [0, 0], "NSR:Quay:2": [1, 1]}
        self.assertIsNone(et.EnturEtRealtime.stop_of({"stop": "q", "name": "Bø", "order": 9}, 2, rows, stops, names))
        self.assertEqual(et.EnturEtRealtime.stop_of({"stop": "q", "name": "Bø", "order": 2}, 2, rows, stops, names),
                         "NSR:Quay:2")

    def test_toward_the_hub(self):
        # The hub is the larger end city (no Oslo S here): C, then A.
        for ends, toward in (({"C stasjon": {"population": 9000}, "A stasjon": {"population": 10}}, True),
                             ({"C stasjon": {"population": 10}, "A stasjon": {"population": 9000}}, False)):
            g = ent.distill(sjn_zip(), lib.INTERCITY_LETTERS, ends, DAY)
            # Running B -> C: the next stop is C itself.
            snap = et.EnturEtRealtime().parse([r70(xd_a=epoch(10), xd_b=epoch(10, 22))], epoch(10, 30), g)
            self.assertIs(snap.extras["453-8"]["toward_hub"], toward)

    def test_no_trip_of_that_number(self):
        snap = self.parse([journey(r70()["calls"], number="9999")], epoch(10, 5))
        self.assertEqual(len(snap.observations), 1)
        self.assertNotIn("9999-8", snap.route_keys)


class TestOnTheMap(unittest.TestCase):
    """Through the estimate, as drawn (projection.apply, geometry.Projector)."""

    def setUp(self):
        self.geometry = load("geometry")
        self.projection = load("projection")
        self.proj, self.rt = self.geometry.Projector(geo()), et.EnturEtRealtime()

    def draw(self, j, now):
        snap = self.rt.parse([j], now, geo())
        o, = snap.observations
        rec = {"latitude": o.lat, "longitude": o.lon, "in_service": True, "previous_latitude": 1.0}
        self.projection.apply(self.proj, snap, {"vehicles": {o.vehicle_id: rec}}, now, False, True, None)
        return rec

    def test_halfway_in_time_is_halfway_along_and_never_a_fix(self):
        rec = self.draw(r70(xd_a=epoch(10), ea_b=epoch(10, 20)), epoch(10, 10))
        mid = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
        self.assertLess(ent.metres((rec["latitude"], rec["longitude"]), mid), 300)
        self.assertEqual(rec["position_source"], "estimated")
        self.assertNotIn("fix_latitude", rec)
        self.assertNotIn("previous_latitude", rec)
        self.assertEqual(rec["icon_rotation_basis"], "course")
        self.assertIn("course_deg", rec)

    def test_standing_is_at_the_stop_and_estimated(self):
        rec = self.draw(r70(xd_a=epoch(10), xa_b=epoch(10, 20)), epoch(10, 21))
        self.assertLess(ent.metres((rec["latitude"], rec["longitude"]), B), 50)
        self.assertEqual(rec["position_source"], "estimated")
        self.assertNotIn("fix_latitude", rec)

    def test_waits_at_the_next_stop_if_late_then_moves_on_by_its_times(self):
        # Expected at B at 10:20 and never an actual: at B from 10:20, on toward C after 10:22.
        j = r70(xd_a=epoch(10))
        self.draw(j, epoch(10, 10))
        at_b = self.draw(j, epoch(10, 21))
        self.assertLess(ent.metres((at_b["latitude"], at_b["longitude"]), B), 50)
        on = self.draw(j, epoch(10, 32))
        self.assertGreater(ent.metres((on["latitude"], on["longitude"]), B), 3000)

    def test_a_later_actual_never_moves_the_train_back(self):
        # Timed from the EXPECTED departure 10:00; at 10:05 the actual says 10:02. The train is not sent back.
        first = self.draw(r70(ed_a=epoch(10), ea_b=epoch(10, 20)), epoch(10, 5))
        then = self.draw(r70(xd_a=epoch(10, 2), ea_b=epoch(10, 20)), epoch(10, 5, 30))
        self.assertGreaterEqual(ent.metres((then["latitude"], then["longitude"]), A) + 1,
                                ent.metres((first["latitude"], first["longitude"]), A))


    def test_an_actual_far_behind_corrects_the_train_and_it_goes_on(self):
        # Train 433 (measured): timed off at its aimed 10:00, 9 km along by 10:15; then the actual says it left A
        # only at 10:14:30. Over 5 km back: taken, as a real fix would be ("actuals as a correction"), and the train
        # goes on forward: its way is not learned from the stop it is timed from going back. (Under 5 km it is held:
        # test_a_later_actual_never_moves_the_train_back.)
        first = self.draw(r70(), epoch(10, 15))
        self.assertGreater(ent.metres((first["latitude"], first["longitude"]), A), 8500)
        then = self.draw(r70(xd_a=epoch(10, 14, 30)), epoch(10, 15))
        self.assertLess(ent.metres((then["latitude"], then["longitude"]), A), 1500)
        on = self.draw(r70(xd_a=epoch(10, 14, 30)), epoch(10, 18))
        self.assertGreater(ent.metres((on["latitude"], on["longitude"]), A),
                           ent.metres((then["latitude"], then["longitude"]), A) + 1000)
        self.assertEqual(self.proj._state["453-8"].motion, 0.0)

    def test_a_stop_moved_back_by_a_revision_does_not_turn_the_train(self):
        # Timed on to B (its time at A revised early), then a revision puts it back at A: it still faces B.
        self.draw(r70(xd_a=epoch(10)), epoch(10, 21))                      # standing at B
        self.draw(r70(xd_a=epoch(10, 19)), epoch(10, 21, 30))              # the stop it is timed from is A again
        self.assertGreaterEqual(self.proj._state["453-8"].direction, 0.0)


class TestOperator(unittest.TestCase):
    def test_registered(self):
        op = operators.OPERATORS["sj_nord"]
        self.assertEqual((op.source, op.source_options["codespace"], op.source_options["consumer"]),
                         ("entur_et", "SJN", "intercity"))
        self.assertEqual((op.regions, op.scan_interval_s, op.timed_without_fix, op.gtfs_from_source),
                         (("NO",), 60, True, True))
        self.assertEqual(op.attribution, lib.ATTRIBUTION)
        self.assertIn(op, operators.operators_in("NO"))

    def test_look_and_late(self):
        op = operators.OPERATORS["sj_nord"]
        self.assertEqual(op.marker_keys({"route_code": "R70"})["marker_color"], "#E13E2E")
        self.assertEqual(op.marker_keys({"route_code": "F7", "route_color": "285DA9"})["marker_color"], "#285DA9")
        self.assertEqual(op.lateness_for({"route_code": "F7"})["late_threshold_min"], 6)
        self.assertEqual(op.lateness_for({"route_code": "R70"})["late_threshold_min"], 4)


if __name__ == "__main__":
    unittest.main()
