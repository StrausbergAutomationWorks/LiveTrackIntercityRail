"""VR (Finland) on Fintraffic Digitraffic: the adapter, the operator, the dated
route lines, the shared-client registration. Offline.

Fixtures (bin\\vr_fixture.py): digitraffic_vr_20261013T0800Z.json.gz is capture
round 1's position snapshot of 2026-10-13 08:00:01Z with every train it
references, each timetable masked to that moment; vr_geometry_20261014.json.gz
is the dated geometry of VR's passenger GTFS of 14 Oct for those trains.
"""

import datetime as dt
import gzip
import io
import json
import pathlib
import unittest
import zipfile

import saw_livetrack.digitraffic_rail as dr
from saw_livetrack.gtfs import Fleet

from _load import load

geometry = load("geometry")
projection = load("projection")
src = load("sources.digitraffic_rail")
operators = load("operators")
vr_mod = load("operators.vr")
shared = load("shared_digitraffic_rail")

FIX = pathlib.Path(__file__).parent / "fixtures"
NOW = dt.datetime(2026, 10, 14, 12, 0, tzinfo=dt.timezone.utc).timestamp()


def _fixture():
    fx = json.loads(gzip.decompress((FIX / "digitraffic_vr_20261013T0800Z.json.gz").read_bytes()))
    geo = json.loads(gzip.decompress((FIX / "vr_geometry_20261014.json.gz").read_bytes()))
    return fx, geo


def iso(minutes):
    return dt.datetime.fromtimestamp(NOW + minutes * 60, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def row(code, kind, minutes, actual=None, diff=None, stopping=True, commercial=True):
    r = {"stationShortCode": code, "type": kind, "trainStopping": stopping,
         "commercialStop": commercial, "scheduledTime": iso(minutes)}
    if actual is not None:
        r["actualTime"] = iso(actual)
    if diff is not None:
        r["differenceInMinutes"] = diff
    return r


def train(number="22", ttype="IC", date="2026-10-14", rows=None, cancelled=False):
    return {"trainNumber": int(number), "departureDate": date, "trainType": ttype,
            "trainCategory": "Long-distance", "cancelled": cancelled, "version": 1,
            "timeTableRows": rows if rows is not None else [
                row("HKI", "DEPARTURE", -30, actual=-29, diff=1),
                row("PSL", "ARRIVAL", -25, actual=-23, diff=2),
                row("PSL", "DEPARTURE", -24, actual=-22, diff=2),
                row("TKL", "ARRIVAL", 10, diff=3),
                row("TKL", "DEPARTURE", 11),
                row("TPE", "ARRIVAL", 90)]}


def rec(number="22", ttype="IC", date="2026-10-14", lat=60.3, lon=24.9, speed=120,
        observed=-5, cancelled=False):
    return {"key": (number, date), "number": number, "departure_date": date,
            "lat": lat, "lon": lon, "speed_kmh": speed,
            "observed_at": None if observed is None else
            dt.datetime.fromtimestamp(NOW + observed, dt.timezone.utc),
            "train_type": ttype, "category": "Long-distance", "cancelled": cancelled}


def parse(records, trains, names=None, routes=None):
    return src.DigitrafficRail().parse(records, trains, NOW, names or {}, routes or {})


class AdapterTests(unittest.TestCase):

    def test_identity_is_number_and_day_of_departure_date(self):
        self.assertEqual(src.identity("22", "2026-10-14"), "22-14")
        self.assertEqual(src.identity("265", "2026-10-09"), "265-9")
        self.assertEqual(src.identity("22", "not a date"), "22")
        self.assertEqual(src.identity("22", None), "22")

    def test_label_is_the_gtfs_short_name(self):
        self.assertEqual(src.label("IC", "23"), "IC 23")
        self.assertEqual(src.label(" PYO ", "265"), "PYO 265")
        self.assertEqual(src.label(None, "23"), "23")
        self.assertEqual(src.label("", "23"), "23")

    def test_a_running_train_is_published_with_its_stop_delay_and_line(self):
        snap = parse([rec()], {("22", "2026-10-14"): train()},
                     names={"TKL": "Tikkurila"},
                     routes={"IC 22|2026-10-14": "Helsinki - Tampere"})
        self.assertEqual(len(snap.observations), 1)
        o = snap.observations[0]
        self.assertEqual((o.vehicle_id, o.train, o.trip_id), ("22-14", "IC 22", "22-14"))
        self.assertTrue(o.in_service)
        self.assertIsNone(o.reported_course)
        self.assertEqual(snap.route_keys["22-14"], "IC 22|2026-10-14")
        self.assertEqual(snap.next_stops["22-14"], ("Tikkurila", NOW + 600))
        self.assertEqual(snap.stop_codes["22-14"], "TKL")
        self.assertEqual(snap.trip_delays["22-14"], 180)
        self.assertEqual(snap.extras["22-14"], {"speed_kmh": 120.0, "line_name": "Helsinki - Tampere",
                                                "departure_date": "2026-10-14"})
        self.assertEqual(snap.skipped, {})

    def test_the_stop_name_falls_back_to_the_code(self):
        snap = parse([rec()], {("22", "2026-10-14"): train()})
        self.assertEqual(snap.next_stops["22-14"][0], "TKL")
        self.assertNotIn("line_name", snap.extras["22-14"])

    def test_no_delay_is_no_delay_not_zero(self):
        rows = [row("HKI", "DEPARTURE", -30, actual=-30), row("TPE", "ARRIVAL", 90)]
        snap = parse([rec()], {("22", "2026-10-14"): train(rows=rows)})
        self.assertNotIn("22-14", snap.trip_delays)

    def test_a_zero_delay_is_published(self):
        rows = [row("HKI", "DEPARTURE", -30, actual=-30, diff=0), row("TPE", "ARRIVAL", 90, diff=0)]
        snap = parse([rec()], {("22", "2026-10-14"): train(rows=rows)})
        self.assertEqual(snap.trip_delays["22-14"], 0)

    def test_depot_and_empty_stock_trains_are_left_out(self):
        for ttype in ("V", "MV"):
            snap = parse([rec(ttype=ttype)], {("22", "2026-10-14"): train(ttype=ttype)})
            self.assertEqual(snap.observations, [], ttype)
            self.assertEqual(snap.skipped, {"not_passenger": 1}, ttype)

    def test_a_cancelled_train_is_left_out(self):
        snap = parse([rec(cancelled=True)], {("22", "2026-10-14"): train(cancelled=True)})
        self.assertEqual(snap.skipped, {"cancelled": 1})

    def test_before_its_first_departure_it_is_not_published(self):
        rows = [row("HKI", "DEPARTURE", 5), row("TPE", "ARRIVAL", 90)]
        snap = parse([rec()], {("22", "2026-10-14"): train(rows=rows)})
        self.assertEqual(snap.skipped, {"predeparture": 1})

    def test_after_its_last_commercial_stop_it_is_not_published(self):
        rows = [row("HKI", "DEPARTURE", -90, actual=-90),
                row("TPE", "ARRIVAL", -2, actual=-1),
                row("TPE_DEPOT", "ARRIVAL", 20, commercial=False)]
        snap = parse([rec()], {("22", "2026-10-14"): train(rows=rows)})
        self.assertEqual(snap.skipped, {"arrived": 1})

    def test_passing_points_and_non_commercial_stops_are_not_the_next_stop(self):
        rows = [row("HKI", "DEPARTURE", -30, actual=-30),
                row("ILA", "ARRIVAL", 2, stopping=False),
                row("KE", "ARRIVAL", 5, commercial=False),
                row("TPE", "ARRIVAL", 90)]
        snap = parse([rec()], {("22", "2026-10-14"): train(rows=rows)})
        self.assertEqual(snap.stop_codes["22-14"], "TPE")

    def test_a_train_missing_from_the_table_is_left_out(self):
        snap = parse([rec()], {})
        self.assertEqual(snap.skipped, {"not_in_table": 1})

    def test_one_identity_once(self):
        snap = parse([rec(), rec(lat=61.0)], {("22", "2026-10-14"): train()})
        self.assertEqual(len(snap.observations), 1)
        self.assertEqual(snap.observations[0].lat, 60.3)
        self.assertEqual(snap.skipped, {"duplicate": 1})

    def test_no_position_or_zero_zero_is_left_out(self):
        for lat, lon in ((None, 24.9), (0, 0), ("60", 24.9)):
            snap = parse([rec(lat=lat, lon=lon)], {("22", "2026-10-14"): train()})
            self.assertEqual(snap.skipped, {"no_position": 1}, (lat, lon))

    def test_a_fix_stamped_in_the_future_has_no_time(self):
        snap = parse([rec(observed=61)], {("22", "2026-10-14"): train()})
        self.assertIsNone(snap.observations[0].observed_at)
        snap = parse([rec(observed=59)], {("22", "2026-10-14"): train()})
        self.assertIsNotNone(snap.observations[0].observed_at)

    def test_no_speed_is_no_speed(self):
        snap = parse([rec(speed=None)], {("22", "2026-10-14"): train()})
        self.assertNotIn("speed_kmh", snap.extras["22-14"])
        snap = parse([rec(speed=0)], {("22", "2026-10-14"): train()})
        self.assertEqual(snap.extras["22-14"]["speed_kmh"], 0.0)

    def test_read_takes_one_consumer_and_its_trains(self):
        class Client:
            # No `table`: read() must take each train from its record.
            def __init__(self):
                self.asked = None

            def for_consumer(self, consumer):
                self.asked = consumer
                return [dict(rec(), train=train())]
        c = Client()
        records, trains = src.read(c)
        self.assertEqual(c.asked, "intercity")
        self.assertEqual(len(records), 1)
        self.assertEqual(trains[("22", "2026-10-14")]["trainNumber"], 22)


class FixtureTests(unittest.TestCase):
    """The real snapshot of 2026-10-13 08:00:01Z through the shared client's own
    parser and router and this adapter."""

    @classmethod
    def setUpClass(cls):
        cls.fx, cls.geo = _fixture()
        cls.now = dt.datetime.fromisoformat(cls.fx["now"]).timestamp()
        table = dr.TrainTable()
        table.update(cls.fx["trains"])
        cls.split = dr.split(dr.join(dr.parse_locations(cls.fx["locations"]), table))
        recs = cls.split[dr.INTERCITY]
        cls.snap = src.DigitrafficRail().parse(
            recs, {r["key"]: table.get(r["key"]) for r in recs}, cls.now,
            cls.geo["stop_names"], cls.geo["train_routes"])

    def test_the_client_routes_the_snapshot_as_measured(self):
        self.assertEqual({k: len(v) for k, v in self.split.items()},
                         {"intercity": 38, "commuter": 62, "freight": 49})

    def test_what_is_published(self):
        # 31 and 5 arrived since saw-livetrack 0.2.25 (backlog 289): S 44 reached Helsinki at
        # 07:58:44 and was still published, its "next stop" Tikkurila, passed about 04:04.
        self.assertEqual(len(self.snap.observations), 31)
        self.assertEqual(self.snap.skipped, {"arrived": 5, "predeparture": 2})

    def test_289_the_next_stop_is_after_the_last_actual_row(self):
        # Each of these named a stop BEHIND the train before saw-livetrack 0.2.25: IC 41 TK
        # (passed LAI 07:51), HDM 424 KLO (passed KAS 07:57), HDM 482 TUU (at PH 07:52).
        ids = {o.train: o.vehicle_id for o in self.snap.observations}
        self.assertNotIn("S 44", ids)
        self.assertEqual(self.snap.stop_codes[ids["IC 41"]], "VS")
        self.assertEqual(self.snap.stop_codes[ids["HDM 424"]], "JJ")
        self.assertEqual(self.snap.stop_codes[ids["HDM 482"]], "PH")

    def test_every_label_is_type_and_number_and_every_identity_number_and_day(self):
        dates = {(str(t["trainNumber"])): t["departureDate"] for t in self.fx["trains"]}
        for o in self.snap.observations:
            ttype, number = o.train.split(" ")
            self.assertIn(ttype, {"IC", "S", "HDM", "PYO"})
            self.assertEqual(o.vehicle_id, f"{number}-{int(dates[number][8:])}")
        # The night train PYO 273 left Helsinki on the 12th: its identity keeps
        # its departure date into the morning of the 13th.
        self.assertIn("273-12", {o.vehicle_id for o in self.snap.observations})
        self.assertEqual(self.snap.route_keys["273-12"], "PYO 273|2026-10-12")

    def test_names_come_from_the_gtfs(self):
        self.assertEqual(self.snap.next_stops["1-13"][0], "Kitee")
        self.assertEqual(self.snap.extras["1-13"]["line_name"], "Helsinki - Joensuu")
        self.assertEqual(self.snap.trip_delays["1-13"], 360)

    def test_the_estimate_puts_trains_with_a_line_on_it(self):
        snap, now = self.snap, self.now
        result = Fleet().update(snap.observations, now, next_stops=snap.next_stops,
                                trip_delays=snap.trip_delays)
        counts = projection.apply(geometry.Projector(self.geo), snap, result, now)
        with_line = sum(1 for o in snap.observations if snap.route_keys[o.vehicle_id] in self.geo["trains"])
        self.assertEqual(with_line, 13)
        self.assertEqual(counts["estimated"], 13)
        self.assertEqual(counts["observed"], 18)   # 19 before 0.2.25: S 44, arrived
        for vid, r in result["vehicles"].items():
            if r.get("position_source") == "estimated":
                self.assertIn("fix_latitude", r)


class OperatorTests(unittest.TestCase):

    def test_vr_is_registered_in_finland(self):
        vr = operators.OPERATORS["vr"]
        self.assertEqual((vr.id, vr.short, vr.regions), ("vr", "VR", ("FI",)))
        self.assertEqual(operators.regions_in_use().get("FI"), "Finland")
        self.assertEqual([op.id for op in operators.operators_in("FI")], ["vr"])
        self.assertEqual(vr.source, operators.SOURCE_DIGITRAFFIC)
        self.assertEqual(vr.source_options, {"consumer": "intercity"})

    def test_credit_and_header_are_the_clients_own(self):
        vr = operators.OPERATORS["vr"]
        self.assertEqual(vr.attribution, "Data: Fintraffic / digitraffic.fi, CC BY 4.0")
        self.assertEqual(vr.attribution, dr.ATTRIBUTION)
        self.assertEqual(dict(vr.request_headers), {"Digitraffic-User": dr.DEFAULT_USER})

    def test_late_from_six_very_late_from_twelve(self):
        vr = operators.OPERATORS["vr"]
        self.assertEqual(vr.lateness_for({"train": "IC 22"}),
                         {"late_threshold_min": 6, "very_late_threshold_min": 12})

    def test_the_gtfs_is_dated_daily_long_distance_only(self):
        vr = operators.OPERATORS["vr"]
        self.assertTrue(vr.gtfs_dated)
        self.assertEqual(vr.gtfs_refresh_s, 86400)
        self.assertEqual(tuple(vr.gtfs_route_types), ("102",))
        self.assertEqual(vr.gtfs_stop_key, "stop_id")
        self.assertFalse(vr.derive_speed)
        self.assertFalse(vr.timed_without_fix)

    def test_other_railroads_keep_a_weekly_undated_gtfs(self):
        for oid in ("amtrak", "brightline", "via_rail"):
            op = operators.OPERATORS[oid]
            self.assertEqual(op.gtfs_refresh_s, 7 * 86400, oid)
            self.assertFalse(op.gtfs_dated, oid)
            self.assertEqual(tuple(op.gtfs_route_types), (), oid)
            self.assertEqual(dict(op.request_headers), {}, oid)

    def test_odd_green_fill_dark_ring_even_swapped(self):
        odd = vr_mod.vr_styling("IC 23")
        self.assertEqual(odd, {
            "marker_color": "#00B451", "marker_ring_color": "#070708", "marker_ring_width": 4,
            "marker_label_color": "#FFFFFF", "marker_label_outline_color": "none",
            "marker_arrow_color": "#00B451", "marker_arrow_outline_color": "#070708"})
        even = vr_mod.vr_styling("PYO 266")
        self.assertEqual((even["marker_color"], even["marker_ring_color"]), ("#070708", "#00B451"))
        self.assertEqual({k: v for k, v in even.items() if k not in ("marker_color", "marker_ring_color")},
                         {k: v for k, v in odd.items() if k not in ("marker_color", "marker_ring_color")})

    def test_no_number_no_styling(self):
        for label in (None, "", "IC", "IC 2a", 23):
            self.assertEqual(vr_mod.vr_styling(label), {}, label)
        self.assertEqual(vr_mod.number_of("265"), 265)
        self.assertEqual(vr_mod.number_of("S 45"), 45)

    def test_marker_keys_style_the_published_record(self):
        vr = operators.OPERATORS["vr"]
        self.assertEqual(vr.marker_keys({"train": "S 45"})["marker_color"], "#00B451")


def _zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return buf.getvalue()


SHAPE_A = "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n" + "".join(
    f"A,{60 + i * 0.01:.2f},24.90,{i}\n" for i in range(5))
SHAPE_B = "".join(f"B,{60 + i * 0.01:.2f},25.10,{i}\n" for i in range(5))
SHAPE_C = "".join(f"C,{61 + i * 0.01:.2f},25.50,{i}\n" for i in range(5))


def gtfs():
    """IC 22 in two timetable periods with different lines (A to 15 Oct, B from
    16 Oct), a 17 Oct exception removing B and an 18 Oct one adding A; a
    commuter route (109) with its own line C."""
    return _zip({
        "routes.txt": "route_id,route_short_name,route_long_name,route_type\n"
                      "R1,IC 22,Helsinki - Tampere,102\nR2,R,Helsinki - Riihimaki,109\n",
        "trips.txt": "route_id,service_id,trip_id,trip_short_name,shape_id\n"
                     "R1,P1,22_20261015,IC 22,A\nR1,P2,22_20261231,IC 22,B\nR2,P3,9001_x,R (HL 9001),C\n",
        "calendar.txt": "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n"
                        "P1,1,1,1,1,1,1,1,20261007,20261015\n"
                        "P2,1,1,1,1,1,1,1,20261016,20261231\n"
                        "P3,1,1,1,1,1,1,1,20261007,20261231\n",
        "calendar_dates.txt": "service_id,date,exception_type\nP2,20261017,2\nP1,20261018,1\n",
        "stops.txt": "stop_id,stop_name,stop_lat,stop_lon\nHKI,Helsinki,60.00,24.90\n",
        "shapes.txt": SHAPE_A + SHAPE_B + SHAPE_C,
        "feed_info.txt": "feed_version,feed_start_date,feed_end_date\nv1,20261007,20271231\n",
    })


class DatedGeometryTests(unittest.TestCase):

    def test_each_date_holds_the_trip_its_calendar_runs(self):
        geo = geometry.distill(gtfs(), dated_from=dt.date(2026, 10, 14), dated_days=5,
                               route_types=("102",))
        self.assertEqual(geo["trains"], {
            "IC 22|2026-10-14": ["A"], "IC 22|2026-10-15": ["A"],
            "IC 22|2026-10-16": ["B"], "IC 22|2026-10-18": ["A", "B"]})
        self.assertEqual(geo["dated_until"], "2026-10-18")
        self.assertEqual(geo["train_routes"]["IC 22|2026-10-16"], "Helsinki - Tampere")
        self.assertNotIn("IC 22", geo["trains"])

    def test_only_the_wanted_route_types_and_their_lines(self):
        geo = geometry.distill(gtfs(), dated_from=dt.date(2026, 10, 14), dated_days=2,
                               route_types=("102",))
        self.assertEqual(sorted(geo["shapes"]), ["A"])
        self.assertFalse(any(k.startswith("R ") for k in geo["trains"]))
        geo = geometry.distill(gtfs(), dated_from=dt.date(2026, 10, 14), dated_days=2)
        self.assertIn("R (HL 9001)|2026-10-14", geo["trains"])
        self.assertEqual(sorted(geo["shapes"]), ["A", "C"])

    def test_undated_is_unchanged(self):
        geo = geometry.distill(gtfs())
        self.assertEqual(geo["trains"]["IC 22"], ["A", "B"])
        self.assertNotIn("dated_until", geo)
        self.assertEqual(sorted(geo["shapes"]), ["A", "B", "C"])

    def test_the_four_days_cover_utc_yesterday_to_the_day_after_tomorrow(self):
        geo = geometry.distill(gtfs(), dated_from=geometry.first_dated_day(dt.date(2026, 10, 15)),
                               route_types=("102",))
        # 14 to 17 Oct; IC 22 runs on 14-16 (17 is removed by its exception).
        self.assertEqual(sorted(k.split("|")[1] for k in geo["trains"]),
                         ["2026-10-14", "2026-10-15", "2026-10-16"])
        self.assertEqual(geo["dated_until"], "2026-10-17")

    def test_covers_utc_tomorrow(self):
        today = dt.date(2026, 10, 15)
        self.assertTrue(geometry.covers({"dated_until": "2026-10-16"}, today))
        self.assertTrue(geometry.covers({"dated_until": "2026-10-17"}, today))
        self.assertFalse(geometry.covers({"dated_until": "2026-10-15"}, today))
        self.assertFalse(geometry.covers({}, today))
        self.assertEqual(geometry.first_dated_day(today), dt.date(2026, 10, 14))

    def test_service_days_rule(self):
        z = zipfile.ZipFile(io.BytesIO(gtfs()))
        import csv

        def rows(name):
            with z.open(name) as f:
                yield from csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))
        dates = [dt.date(2026, 10, 15) + dt.timedelta(days=i) for i in range(4)]
        days = geometry.service_days(rows, z.namelist(), dates)
        self.assertEqual(days["P1"], {"2026-10-15", "2026-10-18"})
        self.assertEqual(days["P2"], {"2026-10-16", "2026-10-18"})

    def test_a_weekday_service_does_not_run_at_the_weekend(self):
        z = zipfile.ZipFile(io.BytesIO(_zip({
            "calendar.txt": "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n"
                            "W,1,1,1,1,1,0,0,20261001,20261231\nE,0,0,0,0,0,1,1,20261001,20261231\n"})))
        import csv

        def rows(name):
            with z.open(name) as f:
                yield from csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))
        # 2026-10-15 is a Thursday; 17 and 18 Oct are Saturday and Sunday.
        dates = [dt.date(2026, 10, 15) + dt.timedelta(days=i) for i in range(4)]
        days = geometry.service_days(rows, z.namelist(), dates)
        self.assertEqual(days["W"], {"2026-10-15", "2026-10-16"})
        self.assertEqual(days["E"], {"2026-10-17", "2026-10-18"})

    def test_dated_key(self):
        self.assertEqual(geometry.dated_key("IC 22", "2026-10-14"), "IC 22|2026-10-14")


class ProjectionKeyTests(unittest.TestCase):
    """projection.apply looks a train's line up by the source's route key."""

    def _run(self, keys):
        geo = geometry.distill(gtfs(), dated_from=dt.date(2026, 10, 14), dated_days=1,
                               route_types=("102",))
        snap = parse([rec(lat=60.02, lon=24.9001)], {("22", "2026-10-14"): train()})
        snap.route_keys.clear()
        snap.route_keys.update(keys)
        result = Fleet().update(snap.observations, NOW, next_stops=snap.next_stops,
                                trip_delays=snap.trip_delays)
        projection.apply(geometry.Projector(geo), snap, result, NOW)
        return result["vehicles"]["22-14"]

    def test_the_dated_key_finds_the_line(self):
        r = self._run({"22-14": "IC 22|2026-10-14"})
        self.assertEqual(r["position_source"], "estimated")
        self.assertEqual(r["longitude"], 24.9)

    def test_without_a_route_key_the_number_is_used(self):
        r = self._run({})
        self.assertEqual(r["position_source"], "observed")

    def test_a_date_with_no_trip_has_no_line(self):
        r = self._run({"22-14": "IC 22|2026-10-20"})
        self.assertEqual(r["position_source"], "observed")


class SharedClientTests(unittest.TestCase):
    """shared_digitraffic_rail.py, byte-copied from LiveTrackCore's reference
    (saw-livetrack 0.2.7: each integration registers its consumer)."""

    class Hass:
        def __init__(self):
            self.data = {}

    def test_one_client_whoever_comes_first_and_the_last_removes_it(self):
        hass = self.Hass()
        a = shared.get_shared_rail_client(hass, "intercity")
        b = shared.get_shared_rail_client(hass, "commuter")
        self.assertIs(a, b)
        self.assertEqual(a.user, "StrausbergAutomationWorks/saw-livetrack")
        self.assertEqual(a.consumers, frozenset({"intercity", "commuter"}))
        self.assertEqual(hass.data[dr.SHARED_KEY]["refcount"], 2)
        shared.release_shared_rail_client(hass, "commuter")
        self.assertEqual(a.consumers, frozenset({"intercity"}))
        shared.release_shared_rail_client(hass, "intercity")
        self.assertNotIn(dr.SHARED_KEY, hass.data)

    def test_a_single_integration_alone_keeps_only_its_own_trains(self):
        hass = self.Hass()
        c = shared.get_shared_rail_client(hass, "intercity")
        self.assertIsInstance(c, dr.DigitrafficRailClient)
        self.assertEqual(c.consumers, frozenset({"intercity"}))
        shared.release_shared_rail_client(hass, "intercity")
        self.assertEqual(hass.data, {})

    def test_the_client_routes_v_and_mv_to_freight(self):
        self.assertEqual(dr.consumer_of("Long-distance", "V"), dr.FREIGHT)
        self.assertEqual(dr.consumer_of("Long-distance", "MV"), dr.FREIGHT)

    def test_vr_registers_intercity(self):
        self.assertEqual(operators.OPERATORS["vr"].source_options["consumer"], dr.INTERCITY)

    def test_a_foreign_entry_is_left_alone(self):
        hass = self.Hass()
        hass.data[dr.SHARED_KEY] = "something else"
        c = shared.get_shared_rail_client(hass, "intercity")
        self.assertIsInstance(c, dr.DigitrafficRailClient)
        self.assertEqual(hass.data[dr.SHARED_KEY], "something else")


if __name__ == "__main__":
    unittest.main()
