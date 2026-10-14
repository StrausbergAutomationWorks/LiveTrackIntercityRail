"""VIA Rail: its own train-status feed (sources/via_rail.py), its look and
lateness (operators/via_rail.py), stops by stop_code (geometry.distill) and
the timed estimate for a train with no usable fix (geometry, projection).
No Home Assistant.

Fixture: tests/fixtures/via_allData_20261010T201422Z.json, nine trains of
VIA's answer at 2026-10-10 20:14:22Z (bin\\ltir_via_fixture.py; alerts
dropped): the Canadian (1), a corridor train (64), 185 running without a
position, both runs of 692, the Maple Leaf's 97 and 98, an arrived and a
not-departed train.
"""

import copy
import csv
import datetime as dt
import io
import json
import math
import pathlib
import unittest
import zipfile

from _load import load

from saw_livetrack.gtfs.realtime import Obs

via_src = load("sources.via_rail")
sources_base = load("sources.base")
operators = load("operators")
via_op = load("operators.via_rail")
geometry = load("geometry")
projection = load("projection")
attributes = load("attributes")

FIX = pathlib.Path(__file__).parent / "fixtures"
DATA = json.loads((FIX / "via_allData_20261010T201422Z.json").read_text(encoding="utf-8"))
UTC = dt.timezone.utc
NOW = dt.datetime(2026, 10, 10, 20, 14, 22, tzinfo=UTC).timestamp()
KX = geometry.R * math.pi / 180
T0 = 1_791_504_000.0


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


class SourceTests(unittest.TestCase):

    def parse(self, data=None, now=NOW, routes=None, via=None):
        via = via or via_src.ViaRail()
        return via.parse(copy.deepcopy(data if data is not None else DATA), now, routes), via

    def test_only_running_positioned_trains_are_published(self):
        snap, _ = self.parse()
        self.assertEqual(sorted(o.vehicle_id for o in snap.observations), ["1-7", "64-10", "692-8"])
        self.assertEqual(snap.skipped.get("no_position"), 1)          # 185, never positioned
        self.assertEqual(snap.skipped.get("drawn_by_amtrak"), 2)      # 97 and 98
        self.assertEqual(snap.skipped.get("arrived"), 1)              # 15
        self.assertEqual(snap.skipped.get("predeparture"), 2)         # 69, 692 (10-10)

    def test_identity_is_number_and_instance_never_the_key(self):
        snap, _ = self.parse()
        o = {o.vehicle_id: o for o in snap.observations}
        self.assertEqual(o["692-8"].train, "692")
        self.assertEqual(o["1-7"].train, "1")
        # The same run under a bare key is the same identity.
        d = {"692": DATA["692 (10-08)"]}
        snap2, _ = self.parse(d)
        self.assertEqual([x.vehicle_id for x in snap2.observations], ["692-8"])
        self.assertEqual(via_src.identity("5", "nonsense"), "5")

    def test_a_new_position_is_timed_by_its_poll(self):
        snap, _ = self.parse()
        o = {o.vehicle_id: o for o in snap.observations}["1-7"]
        self.assertEqual(o.observed_at.timestamp(), ts(DATA["1 (10-07)"]["poll"]))
        self.assertEqual((o.lat, o.lon), (DATA["1 (10-07)"]["lat"], DATA["1 (10-07)"]["lng"]))

    def test_the_same_position_keeps_the_time_it_first_appeared(self):
        # VIA re-sends a frozen position with a newer poll (8,801 pairs).
        snap, via = self.parse()
        first = {o.vehicle_id: o for o in snap.observations}["1-7"].observed_at
        d = copy.deepcopy(DATA)
        d["1 (10-07)"]["poll"] = "2026-10-10T20:20:00Z"
        snap2, _ = self.parse(d, NOW + 400, via=via)
        self.assertEqual({o.vehicle_id: o for o in snap2.observations}["1-7"].observed_at, first)
        d["1 (10-07)"]["lat"] += 0.01
        snap3, _ = self.parse(d, NOW + 430, via=via)
        self.assertEqual({o.vehicle_id: o for o in snap3.observations}["1-7"].observed_at.timestamp(),
                         ts("2026-10-10T20:20:00Z"))

    def test_a_train_that_loses_its_position_keeps_its_last_fix_held(self):
        snap, via = self.parse()
        d = copy.deepcopy(DATA)
        for k in ("lat", "lng", "speed", "poll"):
            d["692 (10-08)"].pop(k, None)
        snap2, _ = self.parse(d, NOW + 600, via=via)
        o = {o.vehicle_id: o for o in snap2.observations}["692-8"]
        self.assertEqual((o.lat, o.lon), (DATA["692 (10-08)"]["lat"], DATA["692 (10-08)"]["lng"]))
        self.assertEqual(o.observed_at.timestamp(), ts(DATA["692 (10-08)"]["poll"]))
        extra = snap2.extras["692-8"]
        self.assertNotIn("speed_kmh", extra)                         # D2: not reported now
        self.assertEqual(extra[sources_base.HELD_SPEED_KEY], DATA["692 (10-08)"]["speed"])
        self.assertEqual(snap2.skipped.get("no_position_held"), 1)
        self.assertNotIn(sources_base.HELD_SPEED_KEY, sources_base.EXTRA_KEYS)

    def test_a_train_that_stops_running_forgets_its_fix(self):
        snap, via = self.parse()
        d = copy.deepcopy(DATA)
        d["692 (10-08)"]["arrived"] = True
        self.parse(d, NOW + 60, via=via)
        d["692 (10-08)"]["arrived"] = False
        for k in ("lat", "lng"):
            d["692 (10-08)"].pop(k)
        snap3, _ = self.parse(d, NOW + 120, via=via)
        self.assertNotIn("692-8", [o.vehicle_id for o in snap3.observations])

    def test_the_next_stop_is_the_first_not_marked_arrived(self):
        snap, _ = self.parse()
        times = DATA["1 (10-07)"]["times"]
        nxt = next(s for s in times if s.get("eta") != "ARR")
        self.assertEqual(snap.stop_codes["1-7"], nxt["code"])
        name, eta = snap.next_stops["1-7"]
        self.assertEqual(name, nxt["station"])
        want = (nxt.get("arrival") or {}).get("estimated") or nxt["estimated"]
        self.assertEqual(eta, ts(want))
        self.assertEqual(snap.trip_delays["1-7"], nxt["diffMin"] * 60)

    def test_unknown_times_are_none_not_text(self):
        times = [{"code": "AAAA", "station": "A", "eta": "ARR"},
                 {"code": "BBBB", "station": "B", "eta": "&mdash;", "estimated": "&mdash;",
                  "arrival": {"estimated": "&mdash;"}, "diffMin": "&mdash;"}]
        self.assertEqual(via_src.next_stop(times), ("BBBB", "B", None, None))
        self.assertIsNone(via_src.next_stop([{"code": "A", "station": "A", "eta": "ARR"}]))

    def test_an_answer_that_is_not_the_feed_is_an_outage(self):
        for bad in (None, {}, [], "x"):
            self.assertIsNone(via_src.ViaRail().parse(bad, NOW))

    def test_a_poll_in_the_future_is_not_a_time(self):
        d = {"1 (10-07)": copy.deepcopy(DATA["1 (10-07)"])}
        d["1 (10-07)"]["poll"] = "2026-10-10T23:00:00Z"
        snap, _ = self.parse(d)
        self.assertIsNone(snap.observations[0].observed_at)

    def test_the_line_name_is_the_gtfs_route_without_the_railroads_name(self):
        snap, _ = self.parse(routes={"1": "VIA Rail Vancouver - Toronto", "64": "Montréal - Toronto"})
        self.assertEqual(snap.extras["1-7"]["line_name"], "Vancouver - Toronto")
        self.assertEqual(snap.extras["64-10"]["line_name"], "Montréal - Toronto")
        self.assertNotIn("line_name", snap.extras["692-8"])
        self.assertEqual(snap.extras["1-7"]["speed_kmh"], DATA["1 (10-07)"]["speed"])

    def test_a_run_long_past_its_last_stop_is_finished(self):
        # Live 2026-10-14: the Ocean of 11 Oct at Halifax, one stop listed,
        # estimated 49 h before, still "departed, not arrived".
        ghost = copy.deepcopy(DATA["64"])
        ghost["times"] = [{"code": "LPOC", "station": "La Pocatiere", "eta": "ARR",
                           "arrival": {"estimated": "2026-10-08T15:00:00-04:00"}}]
        late = copy.deepcopy(DATA["64"])
        late["times"] = [{"code": "TRTO", "station": "Toronto", "eta": "ARR",
                          "arrival": {"estimated": "2026-10-10T14:00:00-04:00"}}]   # 2 h 14 min before NOW
        snap, _ = self.parse({"64": ghost, "65": late})
        self.assertEqual([o.vehicle_id for o in snap.observations], ["65-10"])
        self.assertEqual(snap.skipped.get("finished"), 1)
        self.assertFalse(via_src.finished([], NOW))
        self.assertFalse(via_src.finished([{"eta": "ARR"}], NOW))                  # no time: not finished

    def test_a_key_without_a_number_is_skipped(self):
        snap, _ = self.parse({"Bus 3": copy.deepcopy(DATA["1 (10-07)"])})
        self.assertEqual(snap.observations, [])
        self.assertEqual(snap.skipped, {"no_number": 1})


class OperatorTests(unittest.TestCase):

    def test_registered_on_its_own_feed(self):
        op = operators.OPERATORS["via_rail"]
        self.assertEqual((op.source, op.regions, op.gtfs_stop_key), (operators.SOURCE_VIA, ("CA",), "stop_code"))
        self.assertTrue(op.timed_without_fix)
        self.assertEqual(op.source_options, {"url": "https://tsimobile.viarail.ca/data/allData.json"})
        self.assertIn("Open Government Licence", op.attribution)
        self.assertIn("VIA Rail", op.attribution)

    def test_odd_trains_are_yellow_in_the_groups_band(self):
        s = via_op.via_styling("65", "Montréal - Toronto")
        self.assertEqual(s, {"marker_shape": "maple", "marker_color": "#FFCC00", "marker_ring_color": "#323198",
                             "marker_symbol_color": "#FF0000", "marker_symbol_outline_color": "#000000",
                             "marker_label_placement": "heading", "marker_label_outline_color": "none"})
        self.assertNotIn("marker_label_color", s)          # the card picks by contrast

    def test_even_trains_swap_and_outline_the_leaf_white(self):
        s = via_op.via_styling("2", "Vancouver - Toronto")
        self.assertEqual((s["marker_color"], s["marker_ring_color"], s["marker_symbol_outline_color"]),
                         ("#FF0000", "#FFCC00", "#FFFFFF"))

    def test_every_group_and_its_band(self):
        cases = {"Montréal - Halifax": "#417689", "Vancouver - Toronto": "#FF0000",
                 "Jasper - Prince Rupert": "#EA63A4", "Winnipeg - Churchill": "#01B5FF",
                 "The Pas - Churchill": "#01B5FF", "Sudbury - White River": "#2AAC82",
                 "Montréal - Jonquière": "#FF6D00", "Montréal - Senneterre": "#FF6D00",
                 "Ottawa - Toronto": "#323198", "Toronto - Windsor": "#323198",
                 "Québec - Fallowfield": "#323198", "Toronto - Sarnia": "#323198"}
        for line, band in cases.items():
            self.assertEqual(via_op.via_styling("1", line)["marker_ring_color"], band, line)
            self.assertEqual(via_op.via_styling("2", line)["marker_color"], band, line)

    def test_accents_and_case_do_not_decide_the_route(self):
        self.assertEqual(via_op.route_group("MONTREAL - HALIFAX"), via_op.route_group("Montréal - Halifax"))
        self.assertEqual(via_src.route_key("Montréal - Québec"), "montreal quebec")

    def test_a_route_not_known_takes_the_corridors_band(self):
        self.assertEqual(via_op.via_styling("3", None)["marker_ring_color"], "#323198")
        self.assertEqual(via_op.via_styling("3", "Nowhere - Elsewhere")["marker_ring_color"], "#323198")
        for n in (None, "", "v28", "5A"):
            self.assertEqual(via_op.via_styling(n, "Ottawa - Toronto"), {})

    def test_late_on_the_corridor_at_10_and_off_it_at_60(self):
        self.assertEqual(via_op.via_lateness("45", "Ottawa - Toronto"),
                         {"late_threshold_min": 10, "very_late_threshold_min": 20})
        self.assertEqual(via_op.via_lateness("1", "Vancouver - Toronto"),
                         {"late_threshold_min": 60, "very_late_threshold_min": 120})
        self.assertEqual(via_op.via_lateness("1", None), {})
        op = operators.OPERATORS["via_rail"]
        self.assertEqual(op.lateness_for({"train": "45", "line_name": "Ottawa - Toronto"})["late_threshold_min"], 10)
        amtrak = operators.OPERATORS["amtrak"]
        self.assertEqual(amtrak.lateness_for({"train": "5"}), amtrak.lateness_keys())

    def test_the_maple_keys_reach_the_map(self):
        rec = {"vehicle_id": "65-10", "marker_label": "65", "in_service": True,
               **via_op.via_styling("65", "Montréal - Toronto")}
        a = attributes.to_attributes(rec, "via_rail")
        for k in ("marker_shape", "marker_symbol_color", "marker_symbol_outline_color", "marker_label_placement"):
            self.assertEqual(a[k], rec[k], k)


def _zip(stops, routes, trips, shapes):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, rows in (("stops.txt", stops), ("routes.txt", routes), ("trips.txt", trips), ("shapes.txt", shapes)):
            s = io.StringIO()
            w = csv.DictWriter(s, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
            z.writestr(name, s.getvalue())
    return buf.getvalue()


GTFS = _zip(
    [{"stop_id": "346", "stop_code": "NIAG", "stop_name": "Niagara Falls", "stop_lat": "0.0", "stop_lon": "0.1"},
     {"stop_id": "199", "stop_code": "TRTO", "stop_name": "Toronto", "stop_lat": "0.0", "stop_lon": "0.5"}],
    [{"route_id": "119-618", "route_long_name": "VIA Rail Toronto - Windsor", "route_type": "2"}],
    [{"route_id": "119-618", "trip_short_name": "71", "shape_id": "S1"}],
    [{"shape_id": "S1", "shape_pt_sequence": str(i), "shape_pt_lat": "0.0", "shape_pt_lon": str(i / 10)}
     for i in range(11)])


class DistillTests(unittest.TestCase):

    def test_stops_by_stop_code_for_via(self):
        d = geometry.distill(GTFS, stop_key="stop_code")
        self.assertEqual(sorted(d["stops"]), ["NIAG", "TRTO"])
        self.assertEqual(d["stop_names"]["TRTO"], "Toronto")
        self.assertEqual(d["train_routes"], {"71": "VIA Rail Toronto - Windsor"})

    def test_stops_by_stop_id_otherwise(self):
        d = geometry.distill(GTFS)
        self.assertEqual(sorted(d["stops"]), ["199", "346"])


def geo():
    return {"v": 1, "stops": {"D": [0.0, 0.3], "B": [0.0, 0.05]}, "trains": {"7": ["S1"]},
            "shapes": {"S1": [[0.0, i / 100] for i in range(101)]}}


class TimedTests(unittest.TestCase):
    """Past the horizon, toward the next stop arriving at the estimate."""

    def est(self, p, now, eta=T0 + 3600, timed=True, stop="D", speed=0.0, fix=0.1):
        return p.estimate("7-9", "7", (0.0, fix), T0, stop, speed, now, eta=eta, timed=timed)

    def test_from_the_fix_the_first_time(self):
        p = geometry.Projector(geo())
        lat, lon = self.est(p, T0 + 2000)
        self.assertAlmostEqual(lon, 0.1 + 0.2 * 2000 / 3600, places=5)

    def test_from_where_it_was_last_drawn(self):
        p = geometry.Projector(geo())
        self.assertEqual(self.est(p, T0 + 60), (0.0, 0.1))         # speed rule, standing
        lat, lon = self.est(p, T0 + 2000)
        self.assertAlmostEqual(lon, 0.1 + 0.2 * 1940 / 3540, places=5)
        lat2, lon2 = self.est(p, T0 + 3000)
        self.assertAlmostEqual(lon2, lon + (0.3 - lon) * 1000 / 1600, places=5)

    def test_at_the_stop_once_its_estimate_has_passed(self):
        p = geometry.Projector(geo())
        self.assertEqual(self.est(p, T0 + 4000), (0.0, 0.3))

    def test_waits_without_an_estimate_or_a_stop_ahead(self):
        p = geometry.Projector(geo())
        self.assertEqual(self.est(p, T0 + 2000, eta=None), (0.0, 0.1))
        p2 = geometry.Projector(geo())
        self.assertEqual(self.est(p2, T0 + 2000, stop="B"), (0.0, 0.1))  # behind
        p3 = geometry.Projector(geo())
        self.assertEqual(self.est(p3, T0 + 2000, stop=None), (0.0, 0.1))

    def test_not_timed_it_waits_at_the_horizon(self):
        p = geometry.Projector(geo())
        self.assertEqual(self.est(p, T0 + 2000, timed=False), (0.0, 0.1))

    def test_inside_the_horizon_the_speed_rule_stands(self):
        p = geometry.Projector(geo())
        lat, lon = self.est(p, T0 + 600, speed=10.0)
        self.assertAlmostEqual(lon, 0.1 + 6000 / KX, places=5)


def _obs(lon, t, vid="7-9"):
    return Obs(vehicle_id=vid, lat=0.0, lon=lon, observed_at=dt.datetime.fromtimestamp(t, UTC),
               in_service=True, train="7", line=None, reported_course=None, trip_id=vid)


class ProjectionTimedTests(unittest.TestCase):

    def run_once(self, extra, now=T0 + 2000):
        p = geometry.Projector(geo())
        s = sources_base.Snapshot(observations=[_obs(0.1, T0)])
        s.next_stops["7-9"] = ("D", T0 + 3600)
        s.stop_codes["7-9"] = "D"
        s.extras["7-9"] = extra
        res = {"vehicles": {"7-9": {"vehicle_id": "7-9", "latitude": 0.0, "longitude": 0.1,
                                    "in_service": True}}, "departed": []}
        projection.apply(p, s, res, now, timed=True)
        return res["vehicles"]["7-9"]["longitude"]

    def test_a_held_fix_moves_toward_its_stop(self):
        self.assertAlmostEqual(self.run_once({sources_base.HELD_SPEED_KEY: None}), 0.1 + 0.2 * 2000 / 3600, places=5)

    def test_a_train_reported_moving_moves(self):
        self.assertGreater(self.run_once({"speed_kmh": 60.0}), 0.1)

    def test_a_held_fix_inside_the_horizon_moves_at_its_last_speed(self):
        # 36 km/h is 10 m/s: 6 km in 600 s, never published as speed_kmh.
        lon = self.run_once({sources_base.HELD_SPEED_KEY: 36.0}, now=T0 + 600)
        self.assertAlmostEqual(lon, 0.1 + 6000 / KX, places=5)

    def test_a_train_standing_at_its_fix_does_not_creep(self):
        self.assertEqual(self.run_once({"speed_kmh": 0.0}), 0.1)
        self.assertEqual(self.run_once({}), 0.1)


if __name__ == "__main__":
    unittest.main()
