"""Renfe (Spain): AV, LD and MD trains on Renfe's long-distance feed. The client, the timetable and its run dates,
the shipped lines and their gauge choice, the end cities, the adapter's rules (legs, two vehicles of one number,
the hand-off of R11-R17), the look, the lateness by scheduled distance and the coordinator. Every case is a
measured finding or a decision of Lee's: sources/renfe_ld.py, sources/renfe_ld_lines.py, operators/renfe_spain.py
(Intercity SSOT 8.7, backlog 324). Run from the repo root: python -m unittest tests.test_renfe_spain
"""

import asyncio
import datetime as dt
import io
import json
import os
import pathlib
import shutil
import sys
import tempfile
import time
import types
import unittest
import urllib.error
import zipfile
from zoneinfo import ZoneInfo

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _ha_stub  # noqa: E402
_ha_stub.install()
from _load import load  # noqa: E402

from google.transit import gtfs_realtime_pb2 as pb  # noqa: E402

ld = load("sources.renfe_ld")
lines = load("sources.renfe_ld_lines")
renfe = load("sources.renfe")
base = load("sources.base")
operators = load("operators")
rs = load("operators.renfe_spain")
attributes = load("attributes")
route_store = load("route_store")
coordinator = load("coordinator")
const = load("const")
flow = load("config_flow")

run = asyncio.run
MAD = ZoneInfo("Europe/Madrid")


def origin(ymd):
    d = dt.datetime.strptime(ymd, "%Y%m%d")
    return dt.datetime(d.year, d.month, d.day, 12, tzinfo=MAD).timestamp() - 43200.0


O6 = origin("20261106")
T = lambda h, m=0, s=0, o=O6: o + h * 3600 + m * 60 + s
S = lambda h, m=0: h * 3600 + m * 60

AVE, AVE_LLE, AVE_ZAR = "0306212026-11-05", "0306222026-11-05", "0306242026-11-05"
MD = "1412312026-11-05"
THRU = "0062112026-11-05"
NIGHT = "0080012026-11-05"
LONG = "0090012026-11-05"
STOPS = {"BCN": [41.379, 2.140], "LLE": [41.620, 0.633], "ZAR": [41.658, -0.911], "MAD": [40.472, -3.683],
         "VAL": [39.466, -0.377], "MUR": [37.975, -1.130]}
GEO = {
    "stops": STOPS,
    "stop_names": {"BCN": "Barcelona-Sants", "LLE": "Lleida-Pirineus", "ZAR": "Zaragoza Delicias",
                   "MAD": "Madrid-Puerta de Atocha", "VAL": "Valencia-Nord", "MUR": "Murcia del Carmen"},
    "trip_stops": {
        AVE: [[1, "BCN", S(5, 50), S(5, 50)], [2, "LLE", S(6, 52), S(6, 53)], [3, "ZAR", S(7, 36), S(7, 38)],
              [4, "MAD", S(9, 40), S(9, 40)]],
        AVE_LLE: [[1, "LLE", S(6, 52), S(6, 53)], [2, "ZAR", S(7, 36), S(7, 36)]],
        AVE_ZAR: [[1, "BCN", S(5, 50), S(5, 50)], [2, "LLE", S(6, 52), S(6, 53)], [3, "ZAR", S(7, 36), S(7, 36)]],
        MD: [[1, "VAL", S(6, 45), S(6, 45)], [2, "MUR", S(10, 58), S(10, 58)]],
        THRU: [[1, "ZAR", S(6), S(6)], [2, "MAD", S(8), S(8, 20)], [3, "VAL", S(10), S(10)]],
        NIGHT: [[1, "BCN", S(23), S(23)], [2, "MAD", S(26), S(26)]],
        LONG: [[1, "BCN", S(4), S(4)], [2, "MAD", S(24), S(24)]],
    },
    "trip_dates": {AVE: ["20261105", "20261106"], AVE_LLE: ["20261106"], AVE_ZAR: ["20261106"], MD: ["20261106"],
                   THRU: ["20261106"], NIGHT: ["20261105", "20261106"],
                   LONG: ["20261105", "20261106"]},
    "trip_families": {AVE: "AVE", AVE_LLE: "AVE", AVE_ZAR: "AVE", MD: "MD", THRU: "ALVIA", NIGHT: "INTERCITY"},
    "trip_km": {AVE: 621.0, MD: 400.0, THRU: 650.0},
    "trip_hub": {AVE: 3, AVE_LLE: 1, AVE_ZAR: 2, MD: 0, THRU: 1, NIGHT: 1},
    "trains": {AVE: ["L1"]},
    "shapes": {"L1": [STOPS["BCN"], STOPS["LLE"], STOPS["ZAR"], STOPS["MAD"]]},
}


def positions(*vehicles):
    """(trip, lat, lon) or (trip, lat, lon, status)."""
    f = pb.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    for i, v in enumerate(vehicles):
        trip, lat, lon = v[:3]
        e = f.entity.add()
        e.id = f"VP_{i}"
        e.vehicle.trip.trip_id = trip
        e.vehicle.vehicle.label = trip[:5]
        if lat is not None:
            e.vehicle.position.latitude = lat
            e.vehicle.position.longitude = lon
        if len(v) > 3:
            e.vehicle.current_status = v[3]
    return f


def updates(*rows):
    """(trip, stop id, delay s)."""
    f = pb.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    for i, (trip, stop, delay) in enumerate(rows):
        e = f.entity.add()
        e.id = f"TU_{i}"
        e.trip_update.trip.trip_id = trip
        u = e.trip_update.stop_time_update.add()
        u.stop_id = stop
        u.arrival.delay = delay
    return f


class TripIds(unittest.TestCase):
    def test_number_leg_and_period(self):
        self.assertEqual(ld.parse_trip_id("0306212026-11-05"), ("03062", 1, "2026-11-05"))
        self.assertEqual(ld.parse_trip_id(" 0306242026-11-05 "), ("03062", 4, "2026-11-05"))

    def test_special_carries_its_day(self):
        self.assertEqual(ld.parse_trip_id("SPECIAL_9505220261106"), ("95052", None, "20261106"))

    def test_anything_else(self):
        for t in ("", None, 7, "5109V15772R11", "030621202611-05", "SPECIAL_x"):
            self.assertEqual(ld.parse_trip_id(t), (None, None, None))

    def test_identity(self):
        self.assertEqual(ld.identity("03062", "20261106"), "03062-6")
        self.assertEqual(ld.identity("03062", "20261130"), "03062-30")
        self.assertEqual(ld.identity("03062", None), "03062")
        self.assertEqual(ld.identity("03062", "2026-11-06"), "03062")


class Choose(unittest.TestCase):
    def test_one_leg_the_cheapest(self):
        self.assertEqual(lines.choose([{"1435": 100.0, "1668": 90.0}], None), ["1668"])

    def test_the_prior(self):
        # 1668 is 10% shorter, but AVE prefers 1435 and every other gauge costs 1.3x.
        self.assertEqual(lines.choose([{"1435": 100.0, "1668": 90.0}], "1435"), ["1435"])
        self.assertEqual(lines.choose([{"1435": 100.0, "1668": 125.0}], "1668"), ["1668"])
        # 100 x 1.3 = 130 against 130: a tie keeps 1435.
        self.assertEqual(lines.choose([{"1435": 100.0, "1668": 130.0}], "1668"), ["1435"])

    def test_a_change_costs_30_km(self):
        legs = [{"1435": 1000.0, "1668": 1100.0}, {"1435": 21000.0, "1668": 1000.0}, {"1435": 1000.0, "1668": 1100.0}]
        # Changing twice costs 60 km to save 20: stay on 1668 is 1100+1000+1100 against 1000+21000+1000.
        self.assertEqual(lines.choose(legs, None), ["1668", "1668", "1668"])
        legs[1]["1435"] = 100000.0
        self.assertEqual(lines.choose(legs, None), ["1668", "1668", "1668"])
        legs = [{"1435": 1000.0}, {"1435": 90000.0, "1668": 1000.0}]
        self.assertEqual(lines.choose(legs, None), ["1435", "1668"])

    def test_a_tie_keeps_the_earlier_gauge(self):
        self.assertEqual(lines.choose([{"1435": 100.0, "1668": 100.0}], None), ["1435"])

    def test_nothing(self):
        self.assertEqual(lines.choose([], "1435"), [])

    def test_preferred_gauge(self):
        for fam in ("AVE", "avlo", "AVE INT", "AVANT", "AVANT EXP"):
            self.assertEqual(lines.preferred_gauge(fam), "1435", fam)
        for fam in ("MD", "REGIONAL", "REG.EXP.", "PROXIMDAD", "TRENCELTA"):
            self.assertEqual(lines.preferred_gauge(fam), "1668", fam)
        for fam in ("ALVIA", "INTERCITY", "EUROMED", "", None):
            self.assertIsNone(lines.preferred_gauge(fam), fam)

    def test_constants(self):
        self.assertEqual((lines.PRIOR_X, lines.SWITCH_M, lines.STRAIGHT_X, lines.GAUGES),
                         (1.3, 30000.0, 10.0, ("1435", "1668", "1000")))


# A shipped file of two lines: BCN-LLE on 1435 through a point, and on 1668 straight; LLE-ZAR on 1668 only.
MID = [41.55, 1.40]
SHIPPED = {"v": 1, "meta": {"built": "x", "osm_base": "y"}, "lines": {
    "BCN|LLE|1435": [160000.0, 160000.0, lines.encode([STOPS["BCN"], MID, STOPS["LLE"]])],
    "BCN|LLE|1668": [150000.0, 150000.0, lines.encode([STOPS["BCN"], STOPS["LLE"]])],
    "LLE|ZAR|1668": [130000.0, 130000.0, lines.encode([STOPS["LLE"], STOPS["ZAR"]])],
}}


class Shipped(unittest.TestCase):
    def setUp(self):
        self.s = lines.ShippedLines(SHIPPED)

    def test_encode_decode(self):
        pts = [[41.37912, 2.14011], [40.0, -3.5], [40.00001, -3.49999]]
        self.assertEqual(lines.decode(lines.encode(pts)), pts)
        self.assertEqual(lines.encode([[1.0, 2.0], [1.00002, 1.99999]]), [100000, 200000, 2, -1])

    def test_pair_key_is_unordered(self):
        self.assertEqual(lines.pair_key("LLE", "BCN", "1668"), "BCN|LLE|1668")

    def test_options_in_gauge_order(self):
        self.assertEqual(list(self.s.options("LLE", "BCN")), ["1435", "1668"])
        self.assertEqual(self.s.options("ZAR", "LLE"), {"1668": 130000.0})
        self.assertEqual(self.s.options("BCN", "MAD"), {})

    def test_points_each_way(self):
        self.assertEqual(self.s.points("BCN", "LLE", "1435"), [STOPS["BCN"], MID, STOPS["LLE"]])
        self.assertEqual(self.s.points("LLE", "BCN", "1435"), [STOPS["LLE"], MID, STOPS["BCN"]])

    def test_an_ave_takes_standard_gauge_an_md_iberian(self):
        _, length, gauges = self.s.assemble(["BCN", "LLE"], STOPS, "AVE")
        self.assertEqual((gauges, length), (["1435"], 160000.0))
        self.assertEqual(self.s.assemble(["BCN", "LLE"], STOPS, "MD")[2], ["1668"])
        # No prior: the cheaper.
        self.assertEqual(self.s.assemble(["BCN", "LLE"], STOPS, "ALVIA")[2], ["1668"])

    def test_a_change_of_gauge_costs_30_km(self):
        # An AVE on to Zaragoza: 1435 then 1668 costs 160 + 30 + 130x1.3 = 359 km; staying on 1668,
        # 150x1.3 + 130x1.3 = 364: the change is worth it. An Alvia (no prior): 1668 both ways, 280.
        self.assertEqual(self.s.assemble(["BCN", "LLE", "ZAR"], STOPS, "AVE")[2], ["1435", "1668"])
        self.assertEqual(self.s.assemble(["BCN", "LLE", "ZAR"], STOPS, "ALVIA")[2], ["1668", "1668"])

    def test_a_leg_with_no_line_is_straight_and_measured(self):
        pts, length, gauges = self.s.assemble(["ZAR", "MAD"], STOPS, "AVE")
        self.assertEqual(gauges, [None])
        self.assertEqual(pts, [STOPS["ZAR"], STOPS["MAD"]])
        self.assertAlmostEqual(length, lines.metres(STOPS["ZAR"], STOPS["MAD"]), places=3)

    def test_a_straight_leg_still_charges_a_change_across_it(self):
        legs = [("BCN", "LLE"), ("LLE", "MAD"), ("MAD", "ZAR")]
        opts = lines.leg_options([{"1435": 100000.0}, {}, {"1668": 100000.0, "1435": 120000.0}], legs, STOPS)
        self.assertEqual(set(opts[1]), {"1435", "1668", "1000"})
        self.assertEqual(len(set(opts[1].values())), 1)
        # Through the straight leg on 1435 the last leg costs 120; changing to 1668 saves 20 and costs 30.
        self.assertEqual(lines.choose(opts, None), ["1435", "1435", "1435"])
        legs_, _ = self.s.plan(["BCN", "LLE", "MAD", "LLE", "ZAR"], STOPS, None)
        self.assertEqual([k for _, _, k in legs_], ["BCN|LLE|1668", None, None, "LLE|ZAR|1668"])

    def test_the_trip_is_one_line_a_shared_point_once(self):
        pts, length, _ = self.s.assemble(["BCN", "LLE", "ZAR"], STOPS, "MD")
        self.assertEqual(pts, [STOPS["BCN"], STOPS["LLE"], STOPS["ZAR"]])
        self.assertEqual(length, 280000.0)

    def test_a_repeated_stop_and_a_stop_with_no_place(self):
        self.assertEqual(self.s.plan(["BCN", "BCN", "LLE"], STOPS, "MD")[0], [["BCN", "LLE", "BCN|LLE|1668"]])
        self.assertEqual(self.s.plan(["BCN", "NOWHERE", "LLE"], STOPS, "MD")[0], [["BCN", "LLE", "BCN|LLE|1668"]])
        self.assertEqual(self.s.plan(["BCN"], STOPS, "MD"), ([], 0.0))

    def test_another_version_is_not_read(self):
        with self.assertRaises(ValueError):
            lines.ShippedLines({"v": 2, "lines": {}})

    def test_legs_to_line_reverses_and_skips_unknown(self):
        pts = lines.legs_to_line([["LLE", "BCN", "BCN|LLE|1435"], ["BCN", "X", None]], STOPS,
                                 lambda k: lines.decode(SHIPPED["lines"][k][2]))
        self.assertEqual(pts, [STOPS["LLE"], MID, STOPS["BCN"]])


class ShippedData(unittest.TestCase):
    """The files committed in data/, built by tools/renfe_spain_lines.py on 2026-11-06."""

    @classmethod
    def setUpClass(cls):
        cls.lines = lines.ShippedLines.load()
        cls.ends = lines.load_ends()

    def test_the_lines(self):
        self.assertGreater(len(self.lines), 1400)
        self.assertTrue(self.lines.meta["licence"].startswith("ODbL 1.0"))
        self.assertEqual(self.lines.meta["osm_base"], "2026-11-06T14:01:31Z")
        for key, (m, c, flat) in list(self.lines._lines.items())[:200]:
            a, b, g = key.split("|")
            self.assertLess(a, b)
            self.assertIn(g, lines.GAUGES)
            self.assertGreaterEqual(c, m - 0.2)
            self.assertGreaterEqual(len(flat), 4)

    def test_madrid_to_barcelona_on_the_high_speed_line(self):
        # Puerta de Atocha 60000, Barcelona-Sants 71801: an AVE leg between them is on 1435.
        legs = [k for k in self.lines._lines if k.startswith("60000|71801|")]
        self.assertEqual(legs, ["60000|71801|1435"], legs)

    def test_the_end_cities(self):
        self.assertEqual(len(self.ends), 127)
        for sid, e in self.ends.items():
            self.assertIsInstance(e["population"], int, sid)
            # Baides (Guadalajara), an MD terminus, has 46.
            self.assertGreater(e["population"], 10, sid)

    def test_its_three_faults_are_handled(self):
        by_name = {e["stop"]: e for e in self.ends.values()}
        porto = next(e for n, e in by_name.items() if n.startswith("Porto Campanh"))
        self.assertEqual((porto["municipality"], porto["admin_level"]), ("Porto", "7"))
        self.assertEqual(by_name["Valencia de Alcántara"]["population"], 5140)
        self.assertEqual(by_name["Valencia de Alcántara"]["population_source"], "osm")
        self.assertEqual(by_name["Figueres-Vilafant"]["municipality"], "Figueres")


def ld_zip(*subs):
    """A Renfe AV/LD/MD-shaped timetable: padded fields (05 B5), dated trip ids, a period calendar, a day's
    removal in calendar_dates, legs of one train, an MD with no Madrid stop. `subs`: text replacements."""
    pad = lambda *cells: ",".join(f" {c} " for c in cells) + "\n"
    files = {
        "agency.txt": pad("agency_id", "agency_name", "agency_url", "agency_timezone")
                      + pad("1071", "RENFE OPERADORA", "http://www.renfe.com", "Europe/Madrid"),
        "routes.txt": pad("route_id", "agency_id", "route_short_name", "route_type", "route_color")
                      + pad("7180160000AV006", "1071", "AVE", "2", "F2F5F5")
                      + pad("6510061200VRX", "1071", "MD", "2", "F2F5F5"),
        "calendar.txt": pad("service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
                            "sunday", "start_date", "end_date")
                        + pad("P1", 1, 1, 1, 1, 1, 1, 1, "20261105", "20261212")
                        + pad("P2", 1, 1, 1, 1, 1, 1, 1, "20261105", "20261108")
                        + pad("P3", 1, 1, 1, 1, 1, 1, 1, "20261201", "20261231"),
        # The measured fault: removed on the 5th, it still runs the 6th and 7th.
        "calendar_dates.txt": pad("service_id", "date", "exception_type") + pad("P2", "20261105", "2")
                              + pad("P4", "20261107", "1"),
        "trips.txt": pad("route_id", "service_id", "trip_id", "trip_short_name", "shape_id")
                     + pad("7180160000AV006", "P1", AVE, "03062", "")
                     + pad("7180160000AV006", "P1", AVE_LLE, "03062", "")
                     + pad("7180160000AV006", "P1", "0306312026-11-05", "03063", "")
                     + pad("6510061200VRX", "P2", MD, "14123", "")
                     + pad("6510061200VRX", "P3", "1412312026-12-01", "14123", ""),
        "stop_times.txt": pad("trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence", "pickup_type",
                              "drop_off_type")
                          + pad(AVE, "5:50:00", "5:50:00", "71801", "01", 0, 1)
                          + pad(AVE, "6:52:00", "6:53:00", "78400", "02", 0, 0)
                          + pad(AVE, "7:36:00", "7:38:00", "04040", "03", 0, 0)
                          + pad(AVE, "9:40:00", "9:40:00", "60000", "04", 1, 0)
                          + pad(AVE_LLE, "6:52:00", "6:53:00", "78400", "01", 0, 1)
                          + pad(AVE_LLE, "7:36:00", "7:36:00", "04040", "02", 1, 0)
                          + pad("0306312026-11-05", "6:00:00", "6:00:00", "60000", "01", 0, 1)
                          + pad("0306312026-11-05", "7:00:00", "7:00:00", "99999", "02", 1, 1)
                          + pad("0306312026-11-05", "9:50:00", "9:50:00", "71801", "03", 1, 0)
                          + pad(MD, "6:45:00", "6:45:00", "65000", "01", 0, 1)
                          + pad(MD, "10:58:00", "10:58:00", "61200", "02", 1, 0)
                          + pad("1412312026-12-01", "6:45:00", "6:45:00", "65000", "01", 0, 1)
                          + pad("1412312026-12-01", "10:58:00", "10:58:00", "61200", "02", 1, 0),
        "stops.txt": pad("stop_id", "stop_name", "stop_lat", "stop_lon")
                     + pad("71801", "Barcelona-Sants", "41.379", "2.140") + pad("78400", "Lleida-Pirineus", "41.620", "0.633")
                     + pad("04040", "Zaragoza Delicias", "41.658", "-0.911")
                     + pad("60000", "Madrid-Puerta de Atocha-Almudena Grandes", "40.406", "-3.690")
                     + pad("99999", "Guadalajara-Yebes", "40.590", "-3.120")
                     + pad("65000", "Valencia-Estacio del Nord", "39.466", "-0.377")
                     + pad("61200", "Murcia del Carmen", "37.975", "-1.130"),
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            for old, new in subs:
                text = text.replace(old, new)
            z.writestr(name, text)
    return buf.getvalue()


LD_LINES = lines.ShippedLines({"v": 1, "meta": {"built": "b", "osm_base": "o"}, "lines": {
    "71801|78400|1435": [160000.0, 160000.0, lines.encode([[41.379, 2.140], [41.55, 1.40], [41.620, 0.633]])],
}})
ENDS = {"65000": {"population": 840792}, "61200": {"population": 470000}}


class Timetable(unittest.TestCase):
    def setUp(self):
        self.d = ld.distill(ld_zip(), LD_LINES, ENDS, dt.date(2026, 11, 6))

    def test_running_days_day_by_day(self):
        z = zipfile.ZipFile(io.BytesIO(ld_zip()))
        days = [dt.date(2026, 11, 5), dt.date(2026, 11, 6), dt.date(2026, 11, 7)]
        self.assertEqual(ld.running_days(z, days), {"P1": ["20261105", "20261106", "20261107"],
                                                    "P2": ["20261106", "20261107"], "P4": ["20261107"]})

    def test_only_the_trips_of_the_window_with_their_days(self):
        self.assertEqual(self.d["trip_dates"], {AVE: ["20261105", "20261106", "20261107"],
                                                AVE_LLE: ["20261105", "20261106", "20261107"],
                                                "0306312026-11-05": ["20261105", "20261106", "20261107"],
                                                MD: ["20261106", "20261107"]})
        self.assertEqual(self.d["window"], ["2026-11-05", "2026-11-06", "2026-11-07"])

    def test_stops_names_and_padding(self):
        self.assertEqual(self.d["stops"]["78400"], [41.62, 0.633])
        self.assertEqual(self.d["stop_names"]["04040"], "Zaragoza Delicias")
        self.assertEqual(self.d["trip_families"][AVE], "AVE")
        self.assertEqual(self.d["trip_stops"][AVE][1], [2, "78400", S(6, 52), S(6, 53)])

    def test_a_row_nobody_boards_or_leaves_is_no_stop(self):
        self.assertEqual([r[1] for r in self.d["trip_stops"]["0306312026-11-05"]], ["60000", "71801"])

    def test_each_trip_its_line_as_legs_of_the_shipped_lines(self):
        legs = self.d["shape_legs"][self.d["trains"][AVE][0]]
        self.assertEqual(legs, [["71801", "78400", "71801|78400|1435"], ["78400", "04040", None],
                                ["04040", "60000", None]])
        self.assertEqual(list(self.d["pair_lines"]), ["71801|78400|1435"])
        self.assertEqual(self.d["shapes"], {})
        # AVE 2, its Lleida leg 1, 03063 2 (through Guadalajara, where nobody boards), the MD 1.
        self.assertEqual(self.d["straight_legs"], 6)

    def test_the_trips_length(self):
        straight = lines.metres([41.620, 0.633], [41.658, -0.911]) + lines.metres([41.658, -0.911], [40.406, -3.690])
        self.assertAlmostEqual(self.d["trip_km"][AVE], round((160000.0 + straight) / 1000, 1))

    def test_the_projector_draws_a_line_of_legs(self):
        p = load("geometry").Projector(self.d)
        r = p._route(self.d["trains"][AVE][0])
        self.assertEqual((r.lat[0], r.lon[0]), (41.379, 2.14))
        self.assertEqual((r.lat[1], r.lon[1]), (41.55, 1.4))
        self.assertEqual((r.lat[-1], r.lon[-1]), (40.406, -3.69))
        self.assertIsNone(p._route("nope"))
        pts = load("geometry").line_from_legs(self.d, self.d["trains"][AVE][0], {})
        self.assertEqual(pts, [[41.379, 2.14], [41.55, 1.4], [41.62, 0.633], [41.658, -0.911], [40.406, -3.69]])

    def test_the_hub(self):
        # Madrid at the end (the kept rows); the MD's larger end is Valencia, its first stop.
        self.assertEqual(self.d["trip_hub"], {AVE: 3, "0306312026-11-05": 0, MD: 0})

    def test_hub_index(self):
        names = {"M": "Madrid-Chamartin", "M2": "Madrid-Atocha", "A": "a", "B": "b"}
        self.assertEqual(ld.hub_index(["A", "M", "M2", "B"], names, {}), 2)
        self.assertEqual(ld.hub_index(["A", "B"], names, {"A": {"population": 5}, "B": {"population": 9}}), 1)
        self.assertEqual(ld.hub_index(["A", "B"], names, {"A": {"population": 9}, "B": {"population": 5}}), 0)
        self.assertEqual(ld.hub_index(["A", "B"], names, {"B": {"population": 5}}), 1)
        self.assertEqual(ld.hub_index(["A", "B"], names, {"A": {"population": 5}}), 0)
        self.assertIsNone(ld.hub_index(["A", "B"], names, {}))
        self.assertIsNone(ld.hub_index(["A", "B"], names, {"A": {"population": 5}, "B": {"population": 5}}))
        self.assertIsNone(ld.hub_index([], names, {}))

    def test_the_window_moves_with_the_date(self):
        d = ld.distill(ld_zip(), LD_LINES, ENDS, dt.date(2026, 12, 2))
        self.assertEqual(sorted(d["trip_dates"]), [AVE, AVE_LLE, "0306312026-11-05", "1412312026-12-01"])


class Response:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self, n=-1):
        return self.body if n is None or n < 0 else self.body[:n]


class Opener:
    """urlopen stand-in: url -> bytes, or an exception to raise. Counts calls per url."""

    def __init__(self, answers):
        self.answers, self.calls = dict(answers), {}

    def __call__(self, req, timeout=None):
        url = req.full_url
        self.calls[url] = self.calls.get(url, 0) + 1
        a = self.answers[url]
        if isinstance(a, Exception):
            raise a
        return Response(a)


def http(code):
    return urllib.error.HTTPError("u", code, "x", {}, None)


class Client(unittest.TestCase):
    def make(self, **answers):
        self.t = 1000.0
        o = Opener({ld.POSITIONS_URL: positions((AVE, 41.4, 2.0)).SerializeToString(),
                    ld.TRIP_UPDATES_URL: updates((AVE, "78400", 60)).SerializeToString(),
                    ld.STATIC_URL: ld_zip(), **answers})
        return ld.RenfeLdClient(opener=o, clock=lambda: self.t), o

    def test_the_two_files_cached_15_s(self):
        c, o = self.make()
        vp, tu = c.snapshot()
        self.assertEqual(vp.entity[0].vehicle.trip.trip_id, AVE)
        self.assertEqual(tu.entity[0].trip_update.trip.trip_id, AVE)
        self.t += 14.9
        c.snapshot()
        self.assertEqual(o.calls[ld.POSITIONS_URL], 1)
        self.t += 0.2
        c.snapshot()
        self.assertEqual(o.calls[ld.POSITIONS_URL], 2)
        c.snapshot(force=True)
        self.assertEqual(o.calls[ld.POSITIONS_URL], 3)

    def test_a_failed_update_file_is_none(self):
        c, _ = self.make(**{ld.TRIP_UPDATES_URL: http(503)})
        vp, tu = c.snapshot()
        self.assertIsNotNone(vp)
        self.assertIsNone(tu)

    def test_failed_positions_raise(self):
        c, _ = self.make(**{ld.POSITIONS_URL: http(503)})
        with self.assertRaises(ld.FeedUnavailable):
            c.snapshot()
        c, _ = self.make(**{ld.POSITIONS_URL: http(429)})
        with self.assertRaises(ld.RateLimited):
            c.snapshot()
        c, _ = self.make(**{ld.POSITIONS_URL: OSError("reset")})
        with self.assertRaises(ld.RenfeError):
            c.snapshot()

    def test_undecodable_positions_raise(self):
        c, _ = self.make(**{ld.POSITIONS_URL: b"\xff\xfe not a feed"})
        with self.assertRaises(ld.FeedUnavailable):
            c.snapshot()

    def test_too_large_raises(self):
        self.addCleanup(setattr, ld, "FEED_MAX_BYTES", ld.FEED_MAX_BYTES)
        ld.FEED_MAX_BYTES = 10
        c, _ = self.make()
        with self.assertRaisesRegex(ld.FeedUnavailable, "more than 10 bytes"):
            c.snapshot()

    def test_the_timetable_once_a_day(self):
        c, o = self.make()
        self.assertIsNone(c.static_zip())
        self.assertEqual(c.static_zip(fetch=True), ld_zip())
        self.t += 3600
        c.static_zip(fetch=True)
        self.assertEqual(o.calls[ld.STATIC_URL], 1)
        self.t += 24 * 3600
        c.static_zip(fetch=True)
        self.assertEqual(o.calls[ld.STATIC_URL], 2)

    def test_a_failed_timetable_keeps_the_last_and_waits_an_hour(self):
        c, o = self.make()
        good = c.static_zip(fetch=True)
        o.answers[ld.STATIC_URL] = http(500)
        self.t += 25 * 3600
        self.assertEqual(c.static_zip(fetch=True), good)
        self.t += 1800
        c.static_zip(fetch=True)
        self.assertEqual(o.calls[ld.STATIC_URL], 2)
        o.answers[ld.STATIC_URL] = b"not a zip"
        self.t += 1801
        self.assertEqual(c.static_zip(fetch=True), good)
        self.assertEqual(o.calls[ld.STATIC_URL], 3)

    def test_read(self):
        c, _ = self.make()
        view = types.SimpleNamespace(static_version=lambda: "v1")
        vp, tu, v = ld.read(c, view)
        self.assertEqual(v, "v1")
        self.assertIsNone(ld.read(c)[2])

    def test_constants(self):
        self.assertEqual((ld.FEED_TTL_S, ld.STATIC_TTL_S, ld.STATIC_RETRY_S),
                         (15.0, 24 * 3600.0, 3600.0))
        self.assertEqual(ld.POSITIONS_URL, "https://gtfsrt.renfe.com/vehicle_positions_LD.pb")
        self.assertEqual(ld.TRIP_UPDATES_URL, "https://gtfsrt.renfe.com/trip_updates_LD.pb")
        self.assertEqual(ld.STATIC_URL, "https://ssl.renfe.com/gtransit/Fichero_AV_LD/google_transit.zip")


class StaticViewCase(unittest.TestCase):
    def view(self, raw):
        self.day = "2026-11-06"
        c = types.SimpleNamespace(static_zip=lambda fetch=False: raw)
        return ld.StaticView(c, today=lambda: self.day)

    def test_the_version_is_the_lines_digest_and_spains_date(self):
        v = self.view(ld_zip())
        a = v.static_version()
        self.assertRegex(a, r"^ld1:[0-9a-f]{12}\+[0-9a-f]{12}:2026-11-06$")
        self.day = "2026-11-07"
        self.assertEqual(v.static_version(), a[:-2] + "07")
        self.assertIsNone(v.static_path())

    def test_a_new_ends_file_is_a_new_version(self):
        # 2026-11-09 (Lee: "make future end-station changes take effect at the restart"): the hubs are distilled into
        # the cached geometry, so the ends file's digest is part of its version.
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        c = types.SimpleNamespace(static_zip=lambda fetch=False: None)
        p = os.path.join(tmp, "ends.json")

        def version(body):
            if body is None:
                os.remove(p)
            else:
                open(p, "w", encoding="utf-8").write(body)
            return ld.StaticView(c, today=lambda: "2026-11-09", ends_path=p).static_version()
        a, b = version('{"ends": {}}'), version('{"ends": {"Madrid": {}}}')
        self.assertNotEqual(a, b)
        self.assertEqual(a.split("+")[0], b.split("+")[0])         # the lines' digest unchanged
        self.assertEqual(version('{"ends": {}}'), a)
        self.assertTrue(version(None).endswith("+none:2026-11-09"))

    def test_nothing_before_a_zip(self):
        self.assertIsNone(self.view(None).distill_geometry())

    def test_the_distill_on_the_shipped_lines(self):
        d = self.view(ld_zip()).distill_geometry()
        self.assertEqual(d["v"], load("geometry").GEOMETRY_VERSION)
        self.assertEqual(d["osm_base"], "2026-11-06T14:01:31Z")
        # Barcelona-Sants - Lleida is shipped on 1435.
        self.assertIn("71801|78400|1435", d["pair_lines"])


class RouteStoreCase(unittest.TestCase):
    def test_a_copy_of_legs_is_kept_and_read_back(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        hass = _ha_stub.Hass(tmp)
        op = operators.OPERATORS["renfe_spain"]
        s = route_store.RouteStore(hass, None, op)
        c = types.SimpleNamespace(static_zip=lambda fetch=False: ld_zip())
        view = ld.StaticView(c, today=lambda: "2026-11-06")
        s.static_client = view
        s.note_static(view.static_version())
        run(s.async_refresh())
        self.assertIsNotNone(s.projector)
        self.assertEqual(s.info["shapes"], len(s.projector.geometry["shape_legs"]))
        s2 = route_store.RouteStore(hass, None, op)
        s2.static_client = view
        s2.note_static(view.static_version())
        run(s2.async_load_cached())
        self.assertFalse(s2._stale(0.0))
        self.assertIsNotNone(s2.projector._route(s2.projector.geometry["trains"][AVE][0]))


class HandoffCase(unittest.TestCase):
    def test_seen_numbers_are_held_12_h(self):
        h = ld.Handoff()
        h.note(["15000", "", "18120"], 0.0)
        self.assertEqual(h.owned(12 * 3600.0), {"15000", "18120"})
        self.assertEqual(h.owned(12 * 3600.0 + 1), set())

    def test_the_timetable_is_owned_from_the_start(self):
        h = ld.Handoff()
        h.set_timetable(["17050", ""])
        self.assertEqual(h.owned(0.0), {"17050"})
        h.set_timetable(["15040"])
        self.assertEqual(h.owned(0.0), {"15040"})

    def test_clear(self):
        h = ld.Handoff()
        h.note(["15000"], 0.0)
        h.set_timetable(["17050"])
        h.clear()
        self.assertEqual(h.owned(1.0), set())

    def test_one_per_home_assistant(self):
        data = {}
        self.assertIs(ld.handoff_for(data), ld.handoff_for(data))
        self.assertEqual(ld.HANDOFF_S, 12 * 3600.0)


class RegionalsNumbers(unittest.TestCase):
    def test_the_regionals_note_every_label_and_their_timetable(self):
        rt = renfe.RenfeRealtime("Barcelona")
        f = pb.FeedMessage()
        for i, (trip, label, status) in enumerate((("5109V30530R15", "R15-15030", None),
                                                   ("5109V15000R15", "R15-15000", 0))):
            e = f.entity.add()
            e.id = str(i)
            e.vehicle.trip.trip_id = trip
            e.vehicle.vehicle.label = label
            e.vehicle.position.latitude, e.vehicle.position.longitude = 41.0, 1.0
            if status is not None:
                e.vehicle.current_status = status
        geo = {"trip_stops": {"5109V17050R15": [], "5109V15772R11": []}}
        rt.parse(f, None, 0.0, geo)
        # 15000 was INCOMING_AT with no trusted fix and got no marker: its number is still the regionals'.
        self.assertEqual(rt.last_numbers, {"15030", "15000"})
        self.assertEqual(rt.timetable_numbers, {"17050", "15772"})


AT_LLE = STOPS["LLE"]
WEST_OF_BCN = [41.483, 1.922]


def at(o):
    """An Obs's position to 5 decimals (the feed's floats are float32)."""
    return (round(o.lat, 5), round(o.lon, 5))


class Parse(unittest.TestCase):
    def setUp(self):
        self.rt = ld.RenfeLdRealtime()

    def parse(self, vp, tu=None, now=T(6, 53), drop=frozenset(), geo=GEO):
        return self.rt.parse(vp, tu, now, geo, drop)

    def test_no_positions_is_no_answer(self):
        self.assertIsNone(self.parse(None))

    def test_an_empty_feed_is_a_quiet_hour(self):
        s = self.parse(positions())
        self.assertEqual((s.observations, s.skipped), ([], {}))

    def test_every_leg_at_one_point_is_one_train_on_its_whole_trip(self):
        s = self.parse(positions((AVE_LLE, *AT_LLE), (AVE, *AT_LLE), (AVE_ZAR, *AT_LLE)))
        self.assertEqual(len(s.observations), 1)
        o = s.observations[0]
        self.assertEqual((o.vehicle_id, o.train, at(o)), ("03062-6", "03062", tuple(AT_LLE)))
        self.assertEqual(s.route_keys["03062-6"], AVE)
        ex = s.extras["03062-6"]
        self.assertEqual((ex["line_name"], ex["service_family"], ex["trip_km"]), ("AVE", "AVE", 621.0))
        self.assertNotIn("second_position", s.skipped)

    def test_two_vehicles_of_one_number_the_one_where_the_timetable_puts_it(self):
        # 06:53: 03062 leaves Lleida. The unit west of Barcelona is not the train (capld, 2026-11-06).
        s = self.parse(positions((AVE, *WEST_OF_BCN), (AVE_LLE, *WEST_OF_BCN), (AVE, *AT_LLE), (AVE_LLE, *AT_LLE)))
        o = s.observations[0]
        self.assertEqual((at(o), s.route_keys[o.vehicle_id]), (tuple(AT_LLE), AVE))
        self.assertEqual(s.skipped["second_position"], 1)

    def test_then_the_one_nearest_its_last_fix(self):
        self.parse(positions((AVE, *WEST_OF_BCN)))
        s = self.parse(positions((AVE, *AT_LLE), (AVE, 41.47, 1.90)), now=T(6, 53, 15))
        self.assertEqual(at(s.observations[0]), (41.47, 1.90))

    def test_a_last_fix_too_far_away_does_not_decide(self):
        # 33 km from the vehicle west of Barcelona, 140 from Lleida: too far to say, the timetable decides.
        self.parse(positions((AVE, 41.40, 2.30)))
        s = self.parse(positions((AVE, *WEST_OF_BCN), (AVE, *AT_LLE)), now=T(6, 53, 15))
        self.assertEqual(at(s.observations[0]), tuple(AT_LLE))

    def test_the_trip_is_chosen_again_at_the_point(self):
        # The longest leg is west of Barcelona; the timetable's point carries only the Lleida leg.
        s = self.parse(positions((AVE, *WEST_OF_BCN), (AVE_LLE, *AT_LLE)))
        self.assertEqual((at(s.observations[0]), s.route_keys["03062-6"]), (tuple(AT_LLE), AVE_LLE))

    def test_the_stop_it_last_left_counts(self):
        # 07:00: left Lleida, Zaragoza next. One vehicle just past Lleida, one 60 km past Zaragoza.
        past_zar = [41.40, -1.50]
        s = self.parse(positions((AVE, *past_zar), (AVE, *AT_LLE)), now=T(7))
        self.assertEqual(at(s.observations[0]), tuple(AT_LLE))

    def test_where_counts_the_delay(self):
        # 06:30 an hour late: not yet left Barcelona. On time it would be between Barcelona and Lleida.
        s = self.parse(positions((AVE, *AT_LLE), (AVE, *STOPS["BCN"])), updates((AVE, "LLE", 3600)), now=T(6, 30))
        self.assertEqual(at(s.observations[0]), tuple(STOPS["BCN"]))

    def test_equal_legs_the_lowest_digit(self):
        geo = dict(GEO, trip_stops=dict(GEO["trip_stops"], **{AVE_ZAR: GEO["trip_stops"][AVE]}))
        s = self.parse(positions((AVE_ZAR, *AT_LLE), (AVE, *AT_LLE)), geo=geo)
        self.assertEqual(s.route_keys["03062-6"], AVE)

    def test_with_no_timetable_the_first(self):
        s = self.parse(positions((AVE, *WEST_OF_BCN), (AVE, *AT_LLE)), geo={})
        self.assertEqual(at(s.observations[0]), tuple(WEST_OF_BCN))

    def test_a_number_renfe_regionals_owns_is_left_to_it(self):
        s = self.parse(positions((AVE, *AT_LLE), (MD, 39.47, -0.38)), drop=frozenset({"03062"}))
        self.assertEqual([o.train for o in s.observations], ["14123"])
        self.assertEqual(s.skipped["regional"], 1)

    def test_no_number_or_no_position(self):
        s = self.parse(positions(("5109V15772R11", 41.0, 1.0), (AVE, None, None)))
        self.assertEqual(s.skipped, {"no_number": 1, "no_position": 1})

    def test_the_run_date_is_the_calendars_not_the_ids(self):
        # 0306212026-11-05 runs every day of its period: at 06:53 on the 6th it is the 6th's run.
        self.assertEqual(self.parse(positions((AVE, *AT_LLE))).observations[0].vehicle_id, "03062-6")

    def test_a_train_past_midnight_is_yesterdays(self):
        # 23:00 Barcelona - 02:00 Madrid: at 01:00 on the 6th it is the 5th's run.
        s = self.parse(positions((NIGHT, 41.0, -1.0)), now=T(1))
        self.assertEqual(s.observations[0].vehicle_id, "00800-5")
        s = self.parse(positions((NIGHT, 41.0, -1.0)), now=T(22, 30))
        self.assertEqual(s.observations[0].vehicle_id, "00800-6")

    def test_of_two_runs_that_fit_the_nearest(self):
        # 04:00-24:00 on the 5th and the 6th: at 04:30 on the 6th both fit; the 6th's has begun.
        self.assertEqual(self.rt.run_date(LONG, GEO, T(4, 30)), "20261106")
        self.assertEqual(self.rt.run_date(LONG, GEO, T(1)), "20261105")

    def test_a_special_of_yesterday(self):
        s = self.parse(positions(("SPECIAL_9505220261105", 40.0, -3.0)), now=T(1))
        self.assertEqual(s.observations[0].vehicle_id, "95052-5")

    def test_no_run_date_no_timetable(self):
        # 12:00: the 5th's night train ended by 08:00, the 6th's leaves at 23:00 (from 21:00 it would fit).
        s = self.parse(positions((NIGHT, 41.0, 1.0)), now=T(12))
        self.assertEqual(s.skipped["no_run_date"], 1)
        self.assertNotIn("00800-6", s.next_stops)

    def test_run_date(self):
        self.assertEqual(self.rt.run_date(MD, GEO, T(6)), "20261106")
        self.assertEqual(self.rt.run_date(MD, GEO, T(4, 44)), None)
        self.assertEqual(self.rt.run_date(MD, GEO, T(4, 46)), "20261106")
        self.assertEqual(self.rt.run_date(MD, GEO, T(16, 57)), "20261106")
        self.assertIsNone(self.rt.run_date(MD, GEO, T(17, 0)))
        self.assertIsNone(self.rt.run_date("nope", GEO, T(6)))

    def test_running_on_no_day_of_the_window_drawn_at_its_fix(self):
        s = self.parse(positions((MD, 39.47, -0.38)), now=T(20))
        self.assertEqual(s.observations[0].vehicle_id, "14123-6")
        self.assertEqual(s.skipped["no_run_date"], 1)
        self.assertNotIn("14123-6", s.next_stops)

    def test_a_special_carries_its_day_and_no_timetable(self):
        s = self.parse(positions(("SPECIAL_9505220261106", 40.0, -3.0)))
        o = s.observations[0]
        self.assertEqual((o.vehicle_id, o.train), ("95052-6", "95052"))
        self.assertNotIn("95052-6", s.next_stops)
        self.assertNotIn("line_name", s.extras["95052-6"])

    def test_a_trip_not_in_the_timetable_takes_spains_day(self):
        s = self.parse(positions(("0999912026-12-01", 40.0, -3.0)))
        self.assertEqual(s.observations[0].vehicle_id, "09999-6")

    def test_next_stop_and_delay_from_the_update(self):
        s = self.parse(positions((AVE, 41.63, 0.0)), updates((AVE, "ZAR", 120)), now=T(7, 10))
        self.assertEqual(s.next_stops["03062-6"], ("Zaragoza Delicias", T(7, 36) + 120))
        self.assertEqual((s.stop_codes["03062-6"], s.trip_delays["03062-6"]), ("ZAR", 120))

    def test_the_updates_stop_is_next(self):
        # 06:45, Lleida by the timetable at 06:52; the update says Zaragoza.
        s = self.parse(positions((AVE, 41.6, 0.8)), updates((AVE, "ZAR", 0)), now=T(6, 45))
        self.assertEqual(s.stop_codes["03062-6"], "ZAR")

    def test_a_legs_update_serves_the_train(self):
        s = self.parse(positions((AVE, 41.63, 0.0)), updates((AVE_LLE, "ZAR", 300)), now=T(7, 10))
        self.assertEqual(s.trip_delays["03062-6"], 300)

    def test_without_an_update_the_timetable_and_no_delay(self):
        s = self.parse(positions((AVE, 41.63, 0.0)), now=T(7, 10))
        self.assertEqual(s.next_stops["03062-6"][0], "Zaragoza Delicias")
        self.assertNotIn("03062-6", s.trip_delays)

    def test_a_lost_update_file_keeps_the_last_for_ten_minutes(self):
        self.parse(positions((AVE, 41.63, 0.0)), updates((AVE, "ZAR", 120)), now=T(7, 10))
        self.assertEqual(self.parse(positions((AVE, 41.63, 0.0)), now=T(7, 19)).trip_delays["03062-6"], 120)
        self.assertNotIn("03062-6", self.parse(positions((AVE, 41.63, 0.0)), now=T(7, 21)).trip_delays)

    def test_toward_madrid_until_its_last_madrid_stop_is_behind(self):
        before = self.parse(positions((THRU, 41.0, -2.0)), now=T(7))
        self.assertIs(before.extras["00621-6"]["toward_hub"], True)
        after = self.parse(positions((THRU, 40.0, -2.0)), now=T(9))
        self.assertIs(after.extras["00621-6"]["toward_hub"], False)

    def test_the_hover_says_the_services_name(self):
        s = self.parse(positions((THRU, 41.0, -2.0)), now=T(7))
        self.assertEqual((s.extras["00621-6"]["line_name"], s.extras["00621-6"]["service_family"]), ("Alvia", "ALVIA"))

    def test_ending_in_madrid_toward_starting_in_valencia_away(self):
        self.assertIs(self.parse(positions((AVE, *AT_LLE))).extras["03062-6"]["toward_hub"], True)
        self.assertIs(self.parse(positions((MD, 39.0, -0.6)), now=T(8)).extras["14123-6"]["toward_hub"], False)

    def test_after_the_last_stop_toward_if_the_hub_is_last(self):
        s = self.parse(positions((AVE, *STOPS["MAD"])), now=T(11))
        self.assertIs(s.extras["03062-6"]["toward_hub"], True)
        self.assertNotIn("03062-6", s.next_stops)

    def test_no_hub_no_answer(self):
        geo = dict(GEO, trip_hub={})
        self.assertNotIn("toward_hub", self.parse(positions((AVE, *AT_LLE)), geo=geo).extras["03062-6"])

    def test_a_fix_keeps_the_time_it_was_first_seen_there(self):
        a = self.parse(positions((AVE, *AT_LLE)), now=T(6, 52)).observations[0]
        b = self.parse(positions((AVE, AT_LLE[0] + 0.0003, AT_LLE[1])), now=T(6, 52, 15)).observations[0]
        self.assertEqual(a.observed_at, b.observed_at)
        self.assertEqual(a.observed_at, dt.datetime.fromtimestamp(T(6, 52), dt.timezone.utc))
        self.assertEqual(at(b), tuple(AT_LLE))
        c = self.parse(positions((AVE, AT_LLE[0] + 0.001, AT_LLE[1])), now=T(6, 52, 30)).observations[0]
        self.assertEqual(c.observed_at, dt.datetime.fromtimestamp(T(6, 52, 30), dt.timezone.utc))

    def test_a_fix_time_is_never_after_now(self):
        now = T(6, 52) + 0.9999996
        o = self.parse(positions((AVE, *AT_LLE)), now=now).observations[0]
        self.assertLessEqual(o.observed_at.timestamp(), now)
        self.assertEqual(o.observed_at.timestamp(), T(6, 52))

    def test_the_header_is_never_the_fixes_time(self):
        f = positions((AVE, *AT_LLE))
        f.header.timestamp = int(T(6, 53) - 3604)
        self.assertEqual(self.parse(f).observations[0].observed_at,
                         dt.datetime.fromtimestamp(T(6, 53), dt.timezone.utc))

    def test_a_fresh_fix_moves_at_the_speed_of_two_fixes(self):
        s = self.parse(positions((AVE, *AT_LLE)), now=T(6, 50))
        self.assertIsNone(s.extras["03062-6"][base.HELD_SPEED_KEY])
        self.assertNotIn(base.TIMED_AFTER_KEY, s.extras["03062-6"])
        s = self.parse(positions((AVE, *AT_LLE)), now=T(6, 50, 45))
        self.assertIsNone(s.extras["03062-6"][base.HELD_SPEED_KEY])

    def test_a_fix_unchanged_over_45_s_is_a_train_standing(self):
        self.parse(positions((AVE, *AT_LLE)), now=T(6, 50))
        s = self.parse(positions((AVE, *AT_LLE)), now=T(6, 50, 46))
        self.assertEqual(s.extras["03062-6"][base.HELD_SPEED_KEY], 0.0)
        s = self.parse(positions((AVE, AT_LLE[0] + 0.01, AT_LLE[1])), now=T(6, 51))
        self.assertIsNone(s.extras["03062-6"][base.HELD_SPEED_KEY])
        self.assertEqual(ld.STILL_S, 45.0)

    def test_a_run_is_forgotten_after_an_hour(self):
        self.parse(positions((AVE, *AT_LLE)), now=T(6, 50))
        self.parse(positions(), now=T(7, 51))
        self.assertNotIn("03062-6", self.rt._trusted)

    def test_never_stalled(self):
        s = self.parse(positions((AVE, *AT_LLE)))
        self.assertNotIn("stalled", s.extras["03062-6"])


class OperatorCase(unittest.TestCase):
    op = operators.OPERATORS["renfe_spain"]

    def test_the_entry(self):
        op = self.op
        self.assertEqual((op.id, op.name, op.short, op.regions, op.source),
                         ("renfe_spain", "Renfe (Spain)", "Renfe", ("ES",), "renfe_ld"))
        self.assertEqual((op.scan_interval_s, op.derive_speed, op.timed_without_fix, op.timed_after_s,
                          op.gtfs_from_source, op.needs_key), (15, True, False, None, True, False))
        self.assertEqual(op.attribution, "Data: Renfe (data.renfe.com), CC BY 4.0")
        self.assertEqual(op.terms_url, "https://data.renfe.com/")

    def test_spain_offers_both(self):
        self.assertEqual([o.id for o in operators.operators_in("ES")], ["renfe_spain", "renfe_regionals_catalunya"])

    def test_late_by_scheduled_distance(self):
        mi = rs.MILE_KM
        for km, t in ((None, 10), ("x", 10), (True, 10), (-1, 10), (0, 10), (250 * mi, 10), (250 * mi + 0.1, 15),
                      (350 * mi, 15), (350 * mi + 0.1, 20), (450 * mi, 20), (450 * mi + 0.1, 25), (550 * mi, 25),
                      (550 * mi + 0.1, 30), (2000, 30)):
            self.assertEqual(rs.threshold_min(km), t, km)
        # 621 km is 385.9 miles.
        self.assertEqual(self.op.lateness_for({"trip_km": 621.0}),
                         {"late_threshold_min": 20, "very_late_threshold_min": 40})
        self.assertEqual(self.op.lateness_for({}), {"late_threshold_min": 10, "very_late_threshold_min": 20})

    def look(self, **rec):
        return self.op.marker_keys(rec)

    def test_ave_navy_and_white(self):
        for fam in ("AVE", "AVE INT"):
            k = self.look(service_family=fam, toward_hub=False)
            self.assertEqual((k["marker_color"], k["marker_ring_color"], k["marker_label_color"],
                              k["marker_arrow_color"], k["marker_arrow_outline_color"]),
                             ("#001F4C", "#FFFFFF", "#FFFFFF", "#001F4C", "#FFFFFF"))
            k = self.look(service_family=fam, toward_hub=True)
            self.assertEqual((k["marker_color"], k["marker_ring_color"], k["marker_label_color"]),
                             ("#FFFFFF", "#001F4C", "#001F4C"))

    def test_avlo_turquoise_and_navy(self):
        k = self.look(service_family="AVLO", toward_hub=False)
        self.assertEqual((k["marker_color"], k["marker_ring_color"]), ("#5FCBC6", "#001F4C"))
        k = self.look(service_family="AVLO", toward_hub=True)
        self.assertEqual((k["marker_color"], k["marker_ring_color"]), ("#001F4C", "#5FCBC6"))

    def test_every_other_service_renfe_purple(self):
        for fam in ("ALVIA", "AVANT", "INTERCITY", "EUROMED", "MD", "REGIONAL", "REG.EXP.", None):
            k = self.look(service_family=fam)
            self.assertEqual((k["marker_color"], k["marker_ring_color"]), ("#8A0072", "#FFFFFF"), fam)

    def test_no_answer_the_leaving_look(self):
        self.assertEqual(self.look(service_family="AVE")["marker_color"], "#001F4C")
        self.assertEqual(self.look(service_family="AVE", toward_hub="yes")["marker_color"], "#001F4C")

    def test_the_rest_of_the_look(self):
        k = self.look(service_family="MD")
        self.assertEqual((k["marker_ring_width"], k["marker_label_outline_color"]), (3, "none"))


class Keys(unittest.TestCase):
    def test_the_looks_inputs_never_reach_the_map(self):
        for key in ("service_family", "trip_km", "toward_hub"):
            self.assertIn(key, base.EXTRA_KEYS)
            self.assertIn(key, base.RECORD_ONLY_KEYS)
            self.assertNotIn(key, attributes.PASSTHROUGH)
        rec = {"vehicle_id": "03062-6", "marker_label": "03062", "in_service": True, "train": "03062",
               "line_name": "AVE", "service_family": "AVE", "trip_km": 621.0, "toward_hub": True}
        rec.update(operators.OPERATORS["renfe_spain"].marker_keys(rec))
        a = attributes.to_attributes(rec, "renfe_spain")
        self.assertEqual((a["line_name"], a["marker_color"]), ("AVE", "#FFFFFF"))
        for key in ("service_family", "trip_km", "toward_hub"):
            self.assertNotIn(key, a)

    def test_family_names(self):
        self.assertEqual(ld.FAMILY_NAMES["AVLO"], "Avlo")
        self.assertEqual(ld.FAMILY_NAMES["REG.EXP."], "Regional Exprés")
        self.assertEqual(ld.FAMILY_NAMES["PROXIMDAD"], "Proximidad")


class CoordinatorCase(unittest.TestCase):
    def make(self, op_id, hass=None):
        if hass is None:
            self.dir = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, self.dir)
            hass = _ha_stub.Hass(self.dir)
        entry = types.SimpleNamespace(data={"operator": op_id}, options={}, domain=const.DOMAIN)
        return coordinator.IntercityRailCoordinator(hass, entry, operators.OPERATORS[op_id]), hass

    def patch_read(self, fn):
        self.addCleanup(setattr, ld, "read", ld.read)
        ld.read = fn

    def test_its_own_client_view_and_the_shared_handoff(self):
        c, hass = self.make("renfe_spain")
        self.assertIsInstance(c._ld_client, ld.RenfeLdClient)
        self.assertIsInstance(c.routes.static_client, ld.StaticView)
        self.assertIs(c.routes.static_client.client, c._ld_client)
        self.assertIs(c._handoff, ld.handoff_for(hass.data))
        self.assertIsNone(c._renfe_client)
        self.assertNotIn("saw_renfe_v1", hass.data)
        r, _ = self.make("renfe_regionals_catalunya", hass)
        self.assertIs(r._handoff, c._handoff)
        r.async_release()
        c.async_release()
        self.assertIsNone(c.routes.static_client)

    def test_a_failure_is_ridden_out(self):
        def read(client, view):
            raise ld.FeedUnavailable("HTTP 503 from x")
        self.patch_read(read)
        c, _ = self.make("renfe_spain")
        self.assertIsNone(run(c._fetch()))
        self.assertIn("HTTP 503", c._last_reason)

    def test_a_good_read_drops_what_the_regionals_own(self):
        seen = []

        def read(client, view):
            seen.append((client, view))
            return positions((AVE, *AT_LLE), (MD, 39.0, -0.6)), None, "v3"
        self.patch_read(read)
        c, hass = self.make("renfe_spain")
        ld.handoff_for(hass.data).set_timetable(["14123"])
        snap = run(c._fetch())
        self.assertEqual([o.train for o in snap.observations], ["03062"])
        self.assertEqual(snap.skipped, {"regional": 1})
        self.assertEqual(c.routes._static_version, "v3")
        self.assertEqual(seen, [(c._ld_client, c.routes.static_client)])

    def test_the_regionals_entry_notes_its_numbers_and_clears_them_when_it_goes(self):
        def read(client, consumer, view):
            f = pb.FeedMessage()
            e = f.entity.add()
            e.id = "1"
            e.vehicle.trip.trip_id = "5109V30530R15"
            e.vehicle.vehicle.label = "R15-15030"
            e.vehicle.position.latitude, e.vehicle.position.longitude = 41.1, 1.1
            return f, None, "v1"
        self.addCleanup(setattr, renfe, "read", renfe.read)
        renfe.read = read
        r, hass = self.make("renfe_regionals_catalunya")
        r.routes.projector = load("geometry").Projector({"trip_stops": {"5109V17050R15": []}})
        run(r._fetch())
        h = ld.handoff_for(hass.data)
        self.assertEqual(h.owned(time.time()), {"15030", "17050"})
        r.async_release()
        self.assertEqual(h.owned(time.time()), set())


class Setup(unittest.TestCase):
    def test_renfe_spain_needs_no_key(self):
        f = flow.IntercityRailConfigFlow()
        f._ids = ()
        f.hass = _ha_stub.Hass(tempfile.gettempdir())
        run(f.async_step_user({"region": "ES"}))
        s = run(f.async_step_operator({"operator": "renfe_spain"}))
        self.assertEqual(s["type"], "create_entry")
        self.assertEqual(s["data"], {"operator": "renfe_spain"})
        self.assertEqual(s["title"], "Renfe (Spain)")


if __name__ == "__main__":
    unittest.main()
