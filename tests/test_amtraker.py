"""The Amtraker adapter on hand-built rows shaped like the feed. No HA.

Each row below copies the shape of a real Amtrak record captured 2026-10-09
(bin\\ltir_amtk\\); the replay of the real capture is test_amtraker_replay.py.
"""

import datetime as dt
import unittest

from _load import load

amtraker = load("sources.amtraker")

NOW = dt.datetime(2026, 10, 9, 7, 4, 42, tzinfo=dt.timezone.utc).timestamp()


def station(code, status, sch_arr=None, arr=None, name=None):
    return {"name": name or code, "code": code, "status": status,
            "schArr": sch_arr, "schDep": sch_arr, "arr": arr, "dep": arr}


def row(tid="5-8", num="5", state="Active", lat=40.1, lon=-104.9,
        last="2026-10-09T01:00:39-06:00", **kw):
    r = {"trainID": tid, "trainNum": num, "trainNumRaw": num,
         "routeName": "California Zephyr", "trainState": state,
         "lat": lat, "lon": lon, "lastValTS": last, "velocity": 50.0,
         "heading": "W", "provider": "Amtrak", "onlyOfTrainNum": False,
         "stations": [
             station("CHI", "Departed", "2026-10-08T14:00:00-05:00",
                     "2026-10-08T14:00:00-05:00", "Chicago Union Station"),
             station("OMA", "Departed", "2026-10-08T23:00:00-05:00",
                     "2026-10-08T23:20:00-05:00", "Omaha"),
             station("DEN", "Enroute", "2026-10-09T07:15:00-06:00",
                     "2026-10-09T07:27:00-06:00", "Denver"),
             station("EMY", "Enroute", "2026-10-10T08:10:00-07:00",
                     "2026-10-10T08:10:00-07:00", "Emeryville"),
         ]}
    r.update(kw)
    return r


class IdentityTests(unittest.TestCase):

    def test_identity_is_train_id_and_label_is_the_number(self):
        snap = amtraker.parse([row()], NOW)
        (obs,) = snap.observations
        self.assertEqual(obs.vehicle_id, "5-8")
        self.assertEqual(obs.trip_id, "5-8")
        self.assertEqual(obs.train, "5")
        self.assertTrue(obs.in_service)

    def test_two_runs_of_one_number_are_two_trains(self):
        snap = amtraker.parse([row(tid="5-7", lat=39.0), row(tid="5-8")], NOW)
        self.assertEqual([o.vehicle_id for o in snap.observations], ["5-7", "5-8"])
        self.assertEqual({o.train for o in snap.observations}, {"5"})

    def test_duplicate_train_id_first_wins(self):
        snap = amtraker.parse([row(lat=40.1), row(lat=41.0)], NOW)
        self.assertEqual(len(snap.observations), 1)
        self.assertEqual(snap.observations[0].lat, 40.1)
        self.assertEqual(snap.skipped, {"duplicate": 1})

    def test_label_falls_back_to_train_num_then_id(self):
        snap = amtraker.parse([row(trainNumRaw=None),
                               row(tid="7-8", trainNumRaw="", trainNum=None)], NOW)
        self.assertEqual([o.train for o in snap.observations], ["5", "7-8"])

    def test_an_empty_provider_is_an_outage(self):
        # Measured 2026-10-09 08:54:42Z: a 200 with no Amtrak row at all.
        self.assertIsNone(amtraker.parse([], NOW))
        self.assertIsNone(amtraker.parse(iter(()), NOW))

    def test_rows_none_published_are_not_an_outage(self):
        snap = amtraker.parse([row(state="Predeparture")], NOW)
        self.assertIsNotNone(snap)
        self.assertEqual(snap.observations, [])

    def test_no_train_id_is_skipped(self):
        snap = amtraker.parse([row(tid=""), row(tid=None), "junk"], NOW)
        self.assertEqual(snap.observations, [])
        self.assertEqual(snap.skipped, {"no_train_id": 2, "not_a_record": 1})


class StateTests(unittest.TestCase):

    def test_only_active_is_published(self):
        snap = amtraker.parse([row(tid="1-9", state="Predeparture"),
                               row(tid="2-8", state="Completed"),
                               row(tid="3-8", state=None),
                               row(tid="5-8")], NOW)
        self.assertEqual([o.vehicle_id for o in snap.observations], ["5-8"])
        self.assertEqual(snap.skipped,
                         {"predeparture": 1, "completed": 1, "no_state": 1})
        self.assertNotIn("1-9", snap.next_stops)

    def test_no_position(self):
        for bad in ({"lat": None}, {"lon": "40"}, {"lat": 0.0, "lon": 0.0},
                    {"lat": float("nan")}, {"lat": 95.0}, {"lat": True}):
            snap = amtraker.parse([row(**bad)], NOW)
            self.assertEqual(snap.observations, [], bad)
            self.assertEqual(snap.skipped, {"no_position": 1}, bad)

    def test_position_rounded_to_six_places(self):
        snap = amtraker.parse([row(lat=32.74250902626264, lon=-114.35183329991705)], NOW)
        self.assertEqual((snap.observations[0].lat, snap.observations[0].lon),
                         (32.742509, -114.351833))


class ClockTests(unittest.TestCase):

    def test_observed_at_is_last_val_ts(self):
        snap = amtraker.parse([row(last="2026-10-09T00:00:39-07:00")], NOW)
        self.assertEqual(snap.observations[0].observed_at,
                         dt.datetime(2026, 10, 9, 7, 0, 39, tzinfo=dt.timezone.utc))

    def test_a_future_stamp_is_omitted(self):
        # Live Track Amtrak SSOT 3.4: a stamp three hours in the future.
        snap = amtraker.parse([row(last="2026-10-09T06:04:42-04:00")], NOW)
        self.assertIsNone(snap.observations[0].observed_at)

    def test_within_the_slack_is_kept(self):
        snap = amtraker.parse([row(last="2026-10-09T07:05:30+00:00")], NOW)
        self.assertIsNotNone(snap.observations[0].observed_at)

    def test_unparseable_stamp_is_omitted(self):
        snap = amtraker.parse([row(last="not a time")], NOW)
        self.assertIsNone(snap.observations[0].observed_at)


class NextStopTests(unittest.TestCase):

    def test_after_the_last_departed(self):
        snap = amtraker.parse([row()], NOW)
        name, eta = snap.next_stops["5-8"]
        self.assertEqual(name, "Denver")
        self.assertEqual(eta, dt.datetime(2026, 10, 9, 13, 27,
                                          tzinfo=dt.timezone.utc).timestamp())
        self.assertEqual(snap.trip_delays["5-8"], 12 * 60)

    def test_a_stale_station_status_behind_the_train_is_ignored(self):
        # Measured: train 1-7 at Yuma listed San Antonio, a day back, as
        # "Station" with no times, ahead of later Departed stops.
        r = row()
        r["stations"][0]["status"] = "Station"
        r["stations"][0]["arr"] = None
        self.assertEqual(amtraker.parse([r], NOW).next_stops["5-8"][0], "Denver")

    def test_at_a_station_it_is_that_station(self):
        r = row()
        r["stations"][2]["status"] = "Station"
        self.assertEqual(amtraker.parse([r], NOW).next_stops["5-8"][0], "Denver")

    def test_early_is_negative(self):
        r = row()
        r["stations"][2]["arr"] = "2026-10-09T07:07:00-06:00"
        self.assertEqual(amtraker.parse([r], NOW).trip_delays["5-8"], -8 * 60)

    def test_no_estimate_keeps_the_station_without_time_or_delay(self):
        r = row()
        r["stations"][2]["arr"] = None
        snap = amtraker.parse([r], NOW)
        self.assertEqual(snap.next_stops["5-8"], ("Denver", None))
        self.assertNotIn("5-8", snap.trip_delays)

    def test_at_the_origin_the_next_stop_is_the_second(self):
        r = row()
        for s in r["stations"]:
            s["status"] = "Enroute"
        r["stations"][0]["status"] = "Station"
        self.assertEqual(amtraker.parse([r], NOW).next_stops["5-8"][0], "Omaha")

    def test_past_the_last_stop_there_is_none(self):
        r = row()
        for s in r["stations"]:
            s["status"] = "Departed"
        snap = amtraker.parse([r], NOW)
        self.assertNotIn("5-8", snap.next_stops)
        self.assertNotIn("5-8", snap.trip_delays)
        self.assertEqual(len(snap.observations), 1)

    def test_no_stations(self):
        snap = amtraker.parse([row(stations=None)], NOW)
        self.assertEqual(snap.next_stops, {})

    def test_name_falls_back_to_code(self):
        r = row()
        r["stations"][2]["name"] = " "
        self.assertEqual(amtraker.parse([r], NOW).next_stops["5-8"][0], "DEN")


class ExtrasTests(unittest.TestCase):

    def test_line_name_speed_and_octant(self):
        snap = amtraker.parse([row(routeName="  California   Zephyr ")], NOW)
        self.assertEqual(snap.extras["5-8"], {
            "line_name": "California Zephyr",
            "speed_kmh": round(50.0 * 1.609344, 1),
            "heading_octant": "W"})

    def test_zero_speed_is_a_value(self):
        snap = amtraker.parse([row(velocity=0)], NOW)
        self.assertEqual(snap.extras["5-8"]["speed_kmh"], 0.0)

    def test_absent_fields_are_absent(self):
        snap = amtraker.parse([row(routeName=None, velocity=None, heading="")], NOW)
        self.assertNotIn("5-8", snap.extras)


if __name__ == "__main__":
    unittest.main()
