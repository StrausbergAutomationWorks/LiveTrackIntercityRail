"""sources/entur.py and the Norway operators (Intercity SSOT 8.8): offline, on small built timetables and recorded
bodies (tests/fixtures/entur_*_20261107)."""

import base64
import datetime as dt
import gzip
import io
import json
import pathlib
import sys
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _load import load  # noqa: E402

from google.transit import gtfs_realtime_pb2 as rt
from saw_livetrack import entur as lib

ent = load("sources.entur")
operators = load("operators")
norway = load("operators.norway")

FIX = pathlib.Path(__file__).resolve().parent / "fixtures"
OSLO = dt.timezone(dt.timedelta(hours=1))       # CET on 2026-11-07
DAY = dt.date(2026, 11, 7)


def epoch(h, m=0, day=DAY):
    return dt.datetime(day.year, day.month, day.day, h, m, tzinfo=OSLO).timestamp()


def gtfs_zip(extra_trips=()):
    """A small Vy-like timetable: R13 Drammen - Oslo S - Dal, L1 local, F4 Oslo S - Bergen, R40 Voss - Bergen, and a
    rail-replacement bus on R13; one service on 2026-11-07, one on 2026-11-20."""
    files = {
        "agency.txt": "agency_id,agency_name,agency_url,agency_timezone\nVY,Vy,https://www.vy.no,Europe/Oslo\n",
        "routes.txt": ("route_id,agency_id,route_short_name,route_long_name,route_type,route_color\n"
                       "VYG:Line:R13,VY,R13,Drammen-Oslo S-Dal,100,DF2027\n"
                       "VYG:Line:L1,VY,L1,Spikkestad-Oslo S-Lillestrom,100,8DC63F\n"
                       "VYG:Line:F4,VY,F4,Oslo S-Bergen,100,FF0000\n"
                       "VYG:Line:R40,VY,R40,Bergen-Voss-Myrdal-Al,100,FF0000\n"),
        "calendar_dates.txt": ("service_id,date,exception_type\nS7,20261107,1\nS20,20261120,1\n"),
        "trips.txt": ("route_id,trip_id,service_id,trip_headsign,shape_id\n"
                      "VYG:Line:R13,VYG:ServiceJourney:1672_1-R,S7,Dal,SH1\n"
                      "VYG:Line:R13,VYG:ServiceJourney:1674_1-R,S20,Dal,SH1\n"
                      "VYG:Line:L1,VYG:ServiceJourney:2150_1-R,S7,Lillestrom,SH2\n"
                      "VYG:Line:F4,VYG:ServiceJourney:64_1-R,S7,Bergen,SH3\n"
                      "VYG:Line:R40,VYG:ServiceJourney:1808_1-R,S7,Bergen,SH4\n"
                      "VYG:Line:R13,VYG:ServiceJourney:BUS-1672_1-R,S7,Dal,SH5\n" + "".join(extra_trips)),
        "stops.txt": ("stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station\n"
                      "NSR:StopPlace:1,Drammen stasjon,59.74,10.20,1,\n"
                      "NSR:Quay:11,Drammen stasjon,59.74,10.20,0,NSR:StopPlace:1\n"
                      "NSR:StopPlace:2,Oslo S,59.911,10.752,1,\n"
                      "NSR:Quay:21,Oslo S,59.911,10.752,0,NSR:StopPlace:2\n"
                      "NSR:StopPlace:3,Dal stasjon,60.25,11.20,1,\n"
                      "NSR:Quay:31,Dal stasjon,60.25,11.20,0,NSR:StopPlace:3\n"
                      "NSR:Quay:41,Bergen stasjon,60.39,5.33,0,\n"
                      "NSR:Quay:51,Voss stasjon,60.63,6.41,0,\n"
                      "NSR:Quay:61,Lillestrom stasjon,59.95,11.05,0,\n"
                      "NSR:Quay:71,Bus stop,60.0,11.0,0,\n"),
        "stop_times.txt": ("trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type\n"
                           "VYG:ServiceJourney:1672_1-R,20:00:00,20:00:00,NSR:Quay:11,1,0,0\n"
                           "VYG:ServiceJourney:1672_1-R,20:30:00,20:32:00,NSR:Quay:21,2,0,0\n"
                           "VYG:ServiceJourney:1672_1-R,21:10:00,21:10:00,NSR:Quay:31,3,0,0\n"
                           "VYG:ServiceJourney:1674_1-R,20:00:00,20:00:00,NSR:Quay:11,1,0,0\n"
                           "VYG:ServiceJourney:1674_1-R,21:10:00,21:10:00,NSR:Quay:31,2,0,0\n"
                           "VYG:ServiceJourney:2150_1-R,20:00:00,20:00:00,NSR:Quay:21,1,0,0\n"
                           "VYG:ServiceJourney:2150_1-R,20:20:00,20:20:00,NSR:Quay:61,2,0,0\n"
                           "VYG:ServiceJourney:64_1-R,08:00:00,08:00:00,NSR:Quay:21,1,0,0\n"
                           "VYG:ServiceJourney:64_1-R,14:40:00,14:40:00,NSR:Quay:41,2,0,0\n"
                           "VYG:ServiceJourney:1808_1-R,20:00:00,20:00:00,NSR:Quay:51,1,0,0\n"
                           "VYG:ServiceJourney:1808_1-R,21:15:00,21:15:00,NSR:Quay:41,2,0,0\n"
                           "VYG:ServiceJourney:BUS-1672_1-R,20:00:00,20:00:00,NSR:Quay:71,1,0,0\n"),
        "shapes.txt": ("shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n"
                       "SH1,59.74,10.20,1\nSH1,59.911,10.752,2\nSH1,60.25,11.20,3\n"
                       "SH2,59.911,10.752,1\nSH2,59.95,11.05,2\n"
                       "SH3,59.911,10.752,1\nSH3,60.39,5.33,2\n"
                       "SH4,60.63,6.41,1\nSH4,60.39,5.33,2\n"
                       "SH5,60.0,11.0,1\nSH5,60.1,11.1,2\n"),
        "transfers.txt": "from_stop_id,to_stop_id,transfer_type\nNSR:Quay:11,NSR:Quay:21,0\n",
        "feed_info.txt": "feed_publisher_name,feed_publisher_url,feed_lang\nEntur,https://www.entur.org,no\n",
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for k, v in files.items():
            z.writestr(k, v)
    return buf.getvalue()


ENDS = {"Bergen stasjon": {"population": 274589}, "Voss stasjon": {"population": 7130},
        "Myrdal stasjon": {"population": None}}


class TestIds(unittest.TestCase):
    def test_number(self):
        self.assertEqual(ent.number_of("VYG:ServiceJourney:1672_443368-R"), "1672")
        self.assertEqual(ent.number_of("GOA:ServiceJourney:715-LOD_68400-R", "73-02"), "715")
        self.assertEqual(ent.number_of("VYG:ServiceJourney:398-138_690446-R", "138-2026-11-07"), "138")
        self.assertEqual(ent.number_of("VYG:ServiceJourney:0064-BRG_1-R"), "64")
        self.assertIsNone(ent.number_of("VYG:ServiceJourney:BUS-336_855501-R"))
        self.assertIsNone(ent.number_of("VYG:ServiceJourney:33d5b4ad-6caa-4b6d-ac56-fc523e6b96ae-336-2026-11-07-0"))
        self.assertIsNone(ent.number_of(None))

    def test_identity_and_date(self):
        self.assertEqual(ent.identity("1672", "20261107"), "1672-7")
        self.assertEqual(ent.identity("1672", ""), "1672")
        self.assertEqual(ent.identity("1672", "2026-11-07"), "1672")
        self.assertEqual(ent.date_from_vehicle("1672-2026-11-07"), "20261107")
        self.assertIsNone(ent.date_from_vehicle("72-04"))
        self.assertIsNone(ent.date_from_vehicle(None))

    def test_line_name(self):
        self.assertEqual(ent.train_line_name("1672", "Drammen-Oslo S-Dal"), "Train 1672 · Drammen-Oslo S-Dal")
        self.assertEqual(ent.train_line_name("1672", None), "Train 1672")


class TestHub(unittest.TestCase):
    names = {"a": "Drammen stasjon", "b": "Oslo S", "c": "Dal stasjon", "d": "Oslo S", "v": "Voss stasjon",
             "g": "Bergen stasjon", "m": "Myrdal stasjon"}

    def test_oslo_last(self):
        self.assertEqual(ent.hub_index(["a", "b", "c"], self.names, ENDS), 1)
        self.assertEqual(ent.hub_index(["b", "c", "d", "a"], self.names, ENDS), 2)

    def test_larger_end(self):
        self.assertEqual(ent.hub_index(["v", "g"], self.names, ENDS), 1)
        self.assertEqual(ent.hub_index(["g", "c", "v"], self.names, ENDS), 0)
        self.assertEqual(ent.hub_index(["m", "g"], self.names, ENDS), 1)       # Myrdal is in no settlement
        self.assertEqual(ent.hub_index(["g", "m"], self.names, ENDS), 0)

    def test_unknown_or_equal(self):
        self.assertIsNone(ent.hub_index(["a", "c"], self.names, ENDS))
        self.assertIsNone(ent.hub_index(["m", "m"], self.names, ENDS))
        same = {"Bergen stasjon": {"population": 5}, "Voss stasjon": {"population": 5}}
        self.assertIsNone(ent.hub_index(["v", "g"], self.names, same))
        self.assertIsNone(ent.hub_index([], self.names, ENDS))
        self.assertIsNone(ent.hub_index(["v", "g"], self.names, {"Bergen stasjon": {"population": True}}))

    def test_shipped_ends(self):
        ends = ent.load_ends()
        self.assertEqual(ends["Bergen stasjon"]["population"], 274589)
        self.assertIsNone(ends["Myrdal stasjon"]["population"])
        self.assertEqual(ends["Skien stasjon"]["population"], ends["Porsgrunn stasjon"]["population"])
        self.assertEqual(ent.load_ends(str(FIX / "nothing_here.json")), {})

    def test_sj_nord_ends(self):
        # SJ Nord's ends (2026-11-08), names as its timetable spells them: 193 of its 242 trips without Oslo S had no
        # hub before. Heimdal and Lerkendal are Trondheim's; Storlien is in Sweden, so the other end decides.
        ends = ent.load_ends()
        trd = ends["Trondheim S"]["population"]
        self.assertEqual(trd, 202397)
        self.assertEqual(ends["Heimdal stasjon"]["population"], trd)
        self.assertEqual(ends["Lerkendal stasjon"]["population"], trd)
        self.assertEqual(ends["Bodø stasjon"]["population"], 43446)
        self.assertIsNone(ends["Storlien station"]["population"])
        names = {"t": "Trondheim S", "s": "Storlien station", "b": "Bodø stasjon", "r": "Rognan stasjon",
                 "k": "Steinkjer stasjon", "l": "Lerkendal stasjon", "x": "Mid"}
        self.assertEqual(ent.hub_index(["s", "x", "t"], names, ends), 2)    # R71 to Trondheim
        self.assertEqual(ent.hub_index(["t", "x", "s"], names, ends), 0)
        self.assertEqual(ent.hub_index(["t", "x", "b"], names, ends), 0)    # F7: Trondheim over Bodo
        self.assertEqual(ent.hub_index(["r", "b"], names, ends), 1)         # R75 to Bodo
        self.assertEqual(ent.hub_index(["k", "x", "l"], names, ends), 2)    # R70 to Lerkendal = Trondheim


class TestCutAndDistill(unittest.TestCase):
    def test_cut(self):
        small, info = ent.cut(gtfs_zip(), lib.INTERCITY_LETTERS, [DAY - dt.timedelta(days=1), DAY])
        self.assertEqual(sorted(info), ["VYG:ServiceJourney:1672_1-R", "VYG:ServiceJourney:1808_1-R",
                                        "VYG:ServiceJourney:64_1-R"])
        self.assertEqual(info["VYG:ServiceJourney:1672_1-R"], ("R13", "DF2027"))
        z = zipfile.ZipFile(io.BytesIO(small))
        self.assertNotIn("transfers.txt", z.namelist())
        stops = z.read("stops.txt").decode()
        ids = {line.split(",")[0] for line in stops.splitlines()[1:]}
        self.assertIn("NSR:StopPlace:2", ids)                   # a parent of a used quay, as a row of its own
        self.assertNotIn("NSR:Quay:61", stops)                  # the L1's only
        self.assertNotIn("NSR:Quay:71", stops)                  # the bus's
        self.assertNotIn("SH5", z.read("shapes.txt").decode())
        self.assertNotIn("1674_1-R", z.read("stop_times.txt").decode())    # runs on the 20th only
        self.assertIn("calendar_dates.txt", z.namelist())

    def test_cut_colour_upper(self):
        src = zipfile.ZipFile(io.BytesIO(gtfs_zip()))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as out:
            for n in src.namelist():
                b = src.read(n)
                out.writestr(n, b.replace(b"DF2027", b"df2027") if n == "routes.txt" else b)
        _, info = ent.cut(buf.getvalue(), lib.INTERCITY_LETTERS, [DAY])
        self.assertEqual(info["VYG:ServiceJourney:1672_1-R"], ("R13", "DF2027"))

    def test_distill(self):
        d = ent.distill(gtfs_zip(), lib.INTERCITY_LETTERS, ENDS, DAY)
        self.assertEqual(sorted(d["trains"]), ["VYG:ServiceJourney:1672_1-R", "VYG:ServiceJourney:1808_1-R",
                                               "VYG:ServiceJourney:64_1-R"])
        self.assertEqual(d["trip_numbers"]["VYG:ServiceJourney:1672_1-R"], "R13")
        self.assertEqual(d["train_routes"]["VYG:ServiceJourney:64_1-R"], "Oslo S-Bergen")
        self.assertEqual(d["trip_colors"]["VYG:ServiceJourney:64_1-R"], "FF0000")
        self.assertEqual(d["trip_hub"], {"VYG:ServiceJourney:1672_1-R": 1, "VYG:ServiceJourney:64_1-R": 0,
                                         "VYG:ServiceJourney:1808_1-R": 1})
        self.assertEqual(d["stop_names"]["NSR:Quay:21"], "Oslo S")
        self.assertEqual(d["window"], ["2026-11-06", "2026-11-07", "2026-11-08"])
        self.assertEqual(d["cut_trips"], 3)
        self.assertEqual(d["v"], load("geometry").GEOMETRY_VERSION)


class FakeClient:
    def __init__(self, version="v1", path=None):
        self.version, self.path = version, path

    def static_version(self, codespace):
        return self.version

    def static_path(self, codespace):
        return self.path


class TestStaticView(unittest.TestCase):
    def test_version_and_distill(self):
        import os
        import tempfile
        tmp = os.path.join(tempfile.mkdtemp(), "saw_entur_vyg.zip")
        with open(tmp, "wb") as fh:
            fh.write(gtfs_zip())
        v = ent.StaticView(FakeClient("Fri, 06 Nov", tmp), "VYG", lib.INTERCITY_LETTERS, today=lambda: "2026-11-07")
        self.assertEqual(v.static_version(),
                         f"entur{ent.DISTILL_V}:{ent.file_tag(ent.ENDS_FILE)}:Fri, 06 Nov:2026-11-07")
        d = v.distill_geometry()
        self.assertEqual(len(d["trains"]), 3)
        self.assertIn("VYG:ServiceJourney:1808_1-R", d["trip_hub"])     # the shipped ends: Bergen beats Voss
        self.assertIsNone(ent.StaticView(FakeClient(None), "VYG", ()).static_version())
        self.assertIsNone(ent.StaticView(FakeClient("v", None), "VYG", ()).distill_geometry())

    def test_a_new_ends_file_is_a_new_version(self):
        # 2026-11-09 (Lee: "make future end-station changes take effect at the restart"): SJ Nord's ends of 2026-11-08
        # waited for Oslo's next day, because the cached geometry's version had no part of the ends file.
        import os
        import tempfile
        p = os.path.join(tempfile.mkdtemp(), "ends.json")

        def version(body):
            if body is None:
                os.remove(p)
            else:
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(body)
            return ent.StaticView(FakeClient("v1"), "SJN", (), today=lambda: "2026-11-09", ends_path=p).static_version()
        a, b = version('{"ends": {}}'), version('{"ends": {"Trondheim S": {"population": 1}}}')
        self.assertNotEqual(a, b)
        self.assertRegex(a, r"^entur\d+:[0-9a-f]{12}:v1:2026-11-09$")
        self.assertEqual(version('{"ends": {}}'), a)
        self.assertEqual(version(None), f"entur{ent.DISTILL_V}:none:v1:2026-11-09")
        self.assertEqual(ent.file_tag(p), "none")


def positions(rows, now):
    """A GTFS-Realtime positions feed as the shared client hands it on: rows (trip_id, route_id, start_date, lat, lon,
    fix epoch or None[, vehicle id])."""
    fm = rt.FeedMessage()
    fm.header.gtfs_realtime_version = "2.0"
    fm.header.timestamp = int(now)
    for r in rows:
        tid, rid, sd, lat, lon, ts = r[:6]
        e = fm.entity.add()
        e.id = tid
        e.vehicle.trip.trip_id = tid
        e.vehicle.trip.route_id = rid
        if sd:
            e.vehicle.trip.start_date = sd
        if len(r) > 6:
            e.vehicle.vehicle.id = r[6]
        e.vehicle.position.latitude = lat
        e.vehicle.position.longitude = lon
        if ts is not None:
            e.vehicle.timestamp = int(ts)
    return fm


def updates(rows):
    """rows: (trip_id, start_date, [(stop_sequence, delay s)])"""
    fm = rt.FeedMessage()
    fm.header.gtfs_realtime_version = "2.0"
    for tid, sd, stus in rows:
        e = fm.entity.add()
        e.id = tid + sd
        e.trip_update.trip.trip_id = tid
        e.trip_update.trip.start_date = sd
        for seq, delay in stus:
            s = e.trip_update.stop_time_update.add()
            s.stop_sequence = seq
            s.arrival.delay = delay
            s.departure.delay = delay
    return fm


R13 = "VYG:ServiceJourney:1672_1-R"
F4 = "VYG:ServiceJourney:64_1-R"
R40 = "VYG:ServiceJourney:1808_1-R"


class TestParse(unittest.TestCase):
    def setUp(self):
        self.geo = ent.distill(gtfs_zip(), lib.INTERCITY_LETTERS, ENDS, DAY)

    def test_a_train_between_drammen_and_oslo(self):
        now = epoch(20, 10)
        snap = ent.EnturRealtime().parse(
            positions([(R13, "VYG:Line:R13", "20261107", 59.80, 10.40, now - 20, "1672-2026-11-07")], now),
            updates([(R13, "20261107", [(2, 180)])]), now, self.geo)
        self.assertEqual([o.vehicle_id for o in snap.observations], ["1672-7"])
        o = snap.observations[0]
        self.assertEqual((o.train, o.trip_id), ("1672", "1672-7"))
        self.assertIsNone(o.reported_course)
        self.assertEqual(snap.route_keys["1672-7"], R13)
        ex = snap.extras["1672-7"]
        self.assertEqual(ex["line_name"], "Train 1672 · Drammen-Oslo S-Dal")
        self.assertEqual(ex["route_code"], "R13")
        self.assertEqual(ex["route_color"], "DF2027")
        self.assertIs(ex["toward_hub"], True)              # Oslo S still ahead
        self.assertEqual(snap.next_stops["1672-7"], ("Oslo S", epoch(20, 33)))
        self.assertEqual(snap.trip_delays["1672-7"], 180)
        self.assertEqual(snap.stop_codes["1672-7"], "NSR:Quay:21")

    def test_past_oslo_leaves_the_hub(self):
        now = epoch(20, 45)
        snap = ent.EnturRealtime().parse(
            positions([(R13, "VYG:Line:R13", "20261107", 60.05, 11.0, now - 20)], now),
            updates([(R13, "20261107", [(3, 0)])]), now, self.geo)
        self.assertIs(snap.extras["1672-7"]["toward_hub"], False)
        self.assertEqual(snap.next_stops["1672-7"][0], "Dal stasjon")

    def test_no_update_no_delay_said(self):
        now = epoch(20, 10)
        snap = ent.EnturRealtime().parse(
            positions([(R13, "VYG:Line:R13", "20261107", 59.80, 10.40, now - 20)], now), None, now, self.geo)
        self.assertEqual(snap.next_stops["1672-7"][0], "Oslo S")
        self.assertNotIn("1672-7", snap.trip_delays)

    def test_larger_end_city(self):
        now = epoch(20, 30)
        snap = ent.EnturRealtime().parse(
            positions([(R40, "VYG:Line:R40", "20261107", 60.5, 6.0, now - 10)], now), None, now, self.geo)
        self.assertIs(snap.extras["1808-7"]["toward_hub"], True)       # Voss to Bergen

    def test_skips(self):
        now = epoch(20, 10)
        rows = [("VYG:ServiceJourney:BUS-1672_1-R", "VYG:Line:R13", "20261107", 60.0, 11.0, now),
                (R13, "VYG:Line:R13", "20261107", 59.8, 10.4, now - 10),
                (R13, "VYG:Line:R13", "20261107", 59.8, 10.41, now - 10),
                ("VYG:ServiceJourney:1700_9-R", "VYG:Line:R13", "20261107", 59.8, 10.4, now - 400)]
        snap = ent.EnturRealtime().parse(positions(rows, now), None, now, self.geo)
        self.assertEqual([o.vehicle_id for o in snap.observations], ["1672-7"])
        self.assertEqual(snap.skipped, {"no_number": 1, "duplicate": 1, "stale_first_sight": 1})

    def test_stale_after_first_sight_kept_then_finished(self):
        rt_ = ent.EnturRealtime()
        now = epoch(21, 0)
        rt_.parse(positions([(R13, "VYG:Line:R13", "20261107", 60.2, 11.1, now - 10)], now), None, now, self.geo)
        later = now + 400
        snap = rt_.parse(positions([(R13, "VYG:Line:R13", "20261107", 60.2, 11.1, now - 10)], later), None, later,
                         self.geo)
        self.assertEqual(len(snap.observations), 1)          # seen fresh before: kept
        after = epoch(21, 30)
        snap = rt_.parse(positions([(R13, "VYG:Line:R13", "20261107", 60.25, 11.2, now - 10)], after), None, after,
                         self.geo)
        self.assertEqual(snap.skipped, {"finished": 1})

    def test_date_from_vehicle_when_none(self):
        now = epoch(20, 10)
        snap = ent.EnturRealtime().parse(
            positions([(R13, "VYG:Line:R13", None, 59.8, 10.4, now - 10, "1672-2026-11-07")], now), None, now,
            self.geo)
        self.assertEqual(snap.observations[0].vehicle_id, "1672-7")
        self.assertIn("1672-7", snap.next_stops)

    def test_no_timetable_yet(self):
        now = epoch(20, 10)
        snap = ent.EnturRealtime().parse(
            positions([(R13, "VYG:Line:R13", "20261107", 59.8, 10.4, now - 10),
                       ("GOA:ServiceJourney:715-LOD_1-R", "GOA:Line:50", "20261107", 58.5, 5.8, now - 10)], now),
            None, now, {})
        self.assertEqual(snap.extras["1672-7"], {"line_name": "Train 1672", "route_code": "R13"})
        self.assertEqual(snap.extras["715-7"], {"line_name": "Train 715"})
        self.assertEqual(snap.next_stops, {})

    def test_updates_held_then_dropped(self):
        rt_ = ent.EnturRealtime()
        now = epoch(20, 10)
        vp = positions([(R13, "VYG:Line:R13", "20261107", 59.8, 10.4, now - 10)], now)
        rt_.parse(vp, updates([(R13, "20261107", [(2, 240)])]), now, self.geo)
        snap = rt_.parse(vp, None, now + ent.UPDATES_HOLD_S - 1, self.geo)
        self.assertEqual(snap.trip_delays["1672-7"], 240)
        snap = rt_.parse(vp, None, now + ent.UPDATES_HOLD_S + 1, self.geo)
        self.assertNotIn("1672-7", snap.trip_delays)

    def test_no_positions(self):
        self.assertIsNone(ent.EnturRealtime().parse(None, None, epoch(20), self.geo))

    def test_at_its_origin_the_next_stop_is_the_one_after(self):
        now = epoch(19, 55)
        snap = ent.EnturRealtime().parse(
            positions([(R13, "VYG:Line:R13", "20261107", 59.74, 10.20, now - 10)], now), None, now, self.geo)
        self.assertEqual(snap.next_stops["1672-7"][0], "Oslo S")

    def test_the_origin_delay_carries_to_the_next_stop(self):
        now = epoch(20, 10)
        snap = ent.EnturRealtime().parse(
            positions([(R13, "VYG:Line:R13", "20261107", 59.80, 10.40, now - 20)], now),
            updates([(R13, "20261107", [(1, 300)])]), now, self.geo)
        self.assertEqual(snap.next_stops["1672-7"], ("Oslo S", epoch(20, 35)))
        self.assertEqual(snap.trip_delays["1672-7"], 300)

    def test_the_timetable_names_the_line_before_the_route_id(self):
        now = epoch(20, 10)
        snap = ent.EnturRealtime().parse(
            positions([(R13, "VYG:Line:R12", "20261107", 59.80, 10.40, now - 20)], now), None, now, self.geo)
        self.assertEqual(snap.extras["1672-7"]["route_code"], "R13")

    def test_past_its_last_stop_with_a_fresh_fix(self):
        # Kept (a fresh fix is no finished train); no next stop, so toward the hub only when the hub is the end.
        now = epoch(21, 20)
        snap = ent.EnturRealtime().parse(
            positions([(R40, "VYG:Line:R40", "20261107", 60.39, 5.34, now - 10),
                       (R13, "VYG:Line:R13", "20261107", 60.25, 11.2, now - 10)], now), None, now, self.geo)
        self.assertEqual(sorted(o.vehicle_id for o in snap.observations), ["1672-7", "1808-7"])
        self.assertIs(snap.extras["1808-7"]["toward_hub"], True)       # Bergen, its last stop
        self.assertIs(snap.extras["1672-7"]["toward_hub"], False)      # Oslo S behind it
        self.assertNotIn("1808-7", snap.next_stops)

    def test_finished_by_the_last_delay_known(self):
        rt_ = ent.EnturRealtime()
        first = epoch(21, 0)
        rt_.parse(positions([(R13, "VYG:Line:R13", "20261107", 60.2, 11.1, first - 10)], first), None, first,
                  self.geo)
        now = epoch(21, 20)
        snap = rt_.parse(positions([(R13, "VYG:Line:R13", "20261107", 60.2, 11.1, now - 400)], now),
                         updates([(R13, "20261107", [(2, 900), (3, 0)])]), now, self.geo)
        self.assertEqual(snap.skipped, {"finished": 1})                # Dal at 21:10, on time

    def test_a_run_is_forgotten(self):
        rt_ = ent.EnturRealtime()
        now = epoch(20, 10)
        rt_.parse(positions([(R13, "VYG:Line:R13", "20261107", 59.8, 10.4, now - 10)], now), None, now, self.geo)
        self.assertIn("1672-7", rt_._fresh)
        later = now + ent.FORGET_S + 1
        rt_.parse(positions([], later), None, later, self.geo)
        self.assertNotIn("1672-7", rt_._fresh)

    def frozen(self, now, fix_age, delays=(), at=(59.78, 10.60)):     # (59.8, 10.4) is inside Lieråsen
        """The train seen fresh when its fix was taken, then again at `now` with the same fix: (extras, snapshot)."""
        rt_ = ent.EnturRealtime()
        fix_t = now - fix_age
        tu = updates([(R13, "20261107", list(delays))]) if delays else None
        vp = positions([(R13, "VYG:Line:R13", "20261107", at[0], at[1], fix_t)], now)
        rt_.parse(vp, tu, fix_t + 5, self.geo)
        snap = rt_.parse(vp, tu, now, self.geo)
        return snap.extras["1672-7"], snap

    def test_pushed_through_a_tunnel(self):
        # Drammen to Oslo S: frozen at Lysaker-Sandvika's way in toward Oslo S, 2 minutes after leaving Drammen.
        base_ = load("sources.base")
        tunnel = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_e")
        now = epoch(20, 15)
        ex, snap = self.frozen(now, 120, at=tunnel[1])
        self.assertIsNone(ex[base_.HELD_SPEED_KEY])
        self.assertEqual(ex[base_.TIMED_AFTER_KEY], 0.0)                 # it left Drammen before its fix
        self.assertEqual(ex[base_.AIM_ETA_KEY], now - 120 + tunnel[3])
        self.assertEqual(snap.stop_codes["1672-7"], ent.TUNNEL_STOP + "lysaker_sandvika_e")
        self.assertEqual(snap.next_stops["1672-7"][0], "Oslo S")         # the hover keeps the real next stop
        for k in (base_.HELD_SPEED_KEY, base_.TIMED_AFTER_KEY, base_.AIM_ETA_KEY):
            self.assertNotIn(k, base_.EXTRA_KEYS)

    def test_the_push_starts_when_it_leaves_the_stop_before(self):
        base_ = load("sources.base")
        tunnel = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_e")
        # Late from Drammen by 10 minutes: due out 20:10, fix frozen since 20:02, read at 20:12.
        ex, _ = self.frozen(epoch(20, 12), 600, [(1, 600)], at=tunnel[1])
        self.assertEqual(ex[base_.TIMED_AFTER_KEY], epoch(20, 10) - epoch(20, 2))
        self.assertEqual(ex[base_.AIM_ETA_KEY], epoch(20, 10) + tunnel[3])
        # Still before it: held where it stands.
        ex, snap = self.frozen(epoch(20, 8), 360, [(1, 600)], at=tunnel[1])
        self.assertEqual({k: ex[k] for k in ent.HOLD}, ent.HOLD)
        self.assertEqual(snap.stop_codes["1672-7"], "NSR:Quay:21")

    def test_not_pushed_the_wrong_way_or_far_from_a_way_in(self):
        base_ = load("sources.base")
        # At Oslo S, the way in to Oslotunnelen westbound, but bound for Dal: not into that tunnel.
        ex, snap = self.frozen(epoch(20, 45), 120, at=(59.91168, 10.75219))
        self.assertNotIn(base_.AIM_ETA_KEY, ex)
        self.assertEqual(snap.stop_codes["1672-7"], "NSR:Quay:31")
        # Toward Oslo S, but 800 m from the way in.
        tunnel = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_e")
        ex, _ = self.frozen(epoch(20, 15), 120, at=(tunnel[1][0] + 0.0072, tunnel[1][1]))
        self.assertNotIn(base_.AIM_ETA_KEY, ex)
        # A fresh fix at the way in: not frozen, not pushed.
        ex, _ = self.frozen(epoch(20, 15), ent.FROZEN_S - 1, at=tunnel[1])
        self.assertNotIn(base_.AIM_ETA_KEY, ex)

    def test_held_once_the_next_stops_estimate_has_passed(self):
        base_ = load("sources.base")
        # Ten minutes late into Oslo S (due 20:30, estimate 20:40), fix frozen since 20:20, read at 20:41.
        ex, snap = self.frozen(epoch(20, 41), 1260, [(2, 600)])
        self.assertEqual(snap.next_stops["1672-7"], ("Oslo S", epoch(20, 40)))
        self.assertEqual({k: ex[k] for k in ent.HOLD}, ent.HOLD)
        self.assertEqual(ent.HOLD, {base_.HELD_SPEED_KEY: 0.0, base_.TIMED_AFTER_KEY: 0.0, base_.AIM_ETA_KEY: None})
        # Not at a tunnel's way in: there the push runs on to where its fixes come back, as in Helsinki.
        tunnel = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_e")
        ex, snap = self.frozen(epoch(20, 41), 1260, [(2, 600)], at=tunnel[1])
        self.assertIsNotNone(ex[base_.AIM_ETA_KEY])
        self.assertEqual(snap.stop_codes["1672-7"], ent.TUNNEL_STOP + "lysaker_sandvika_e")
        # Not frozen: not held.
        ex, _ = self.frozen(epoch(20, 41), ent.FROZEN_S - 1, [(2, 600)])
        self.assertNotIn(base_.AIM_ETA_KEY, ex)
        # Frozen, estimate still ahead, no tunnel: nothing said.
        ex, _ = self.frozen(epoch(20, 15), 600)
        self.assertNotIn(base_.AIM_ETA_KEY, ex)
        self.assertNotIn(base_.HELD_SPEED_KEY, ex)

    def test_rule_off(self):
        old = ent.FROZEN_S
        try:
            ent.FROZEN_S = None
            tunnel = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_e")
            ex, _ = self.frozen(epoch(20, 15), 600, at=tunnel[1])
            self.assertNotIn(load("sources.base").TIMED_AFTER_KEY, ex)
            ex, _ = self.frozen(epoch(20, 41), 1260, [(2, 600)])
            self.assertNotIn(load("sources.base").TIMED_AFTER_KEY, ex)
        finally:
            ent.FROZEN_S = old

    def test_tunnel_at(self):
        geo = {"stops": {"A": [59.889, 10.525], "L": [59.913, 10.640],
                         ent.TUNNEL_STOP + "lysaker_sandvika_e": [59.9147, 10.62993],
                         ent.TUNNEL_STOP + "lysaker_sandvika_w": [59.89459, 10.53044]}}
        e = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_e")
        w = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_w")
        self.assertIs(ent.tunnel_at(e[1], "A", "L", geo), e)
        self.assertIs(ent.tunnel_at(w[1], "L", "A", geo), w)
        # Westbound at the eastbound way in: not into e (the other way), nor w (600 m from w's comeback: come out).
        self.assertIsNone(ent.tunnel_at(e[1], "L", "A", geo))
        self.assertFalse(ent.ahead([59.74, 10.20], [59.911, 10.752], w[1], w[2]))      # Drammen to Oslo S: not w
        self.assertTrue(ent.ahead([59.74, 10.20], [59.911, 10.752], e[1], e[2]))
        self.assertIsNone(ent.tunnel_at(e[1], "A", "X", geo))            # a stop with no place
        self.assertIsNone(ent.tunnel_at((e[1][0] + 0.0072, e[1][1]), "A", "L", geo))    # 800 m off
        self.assertIs(ent.tunnel_at((e[1][0] + 0.0054, e[1][1]), "A", "L", geo), e)    # 600 m: in
        old = {"stops": {"A": [59.889, 10.525], "L": [59.913, 10.640]}}
        self.assertIsNone(ent.tunnel_at(e[1], "A", "L", old))            # geometry from before the tunnels
        self.assertAlmostEqual(ent.metres((59.9, 10.6), (59.91, 10.6)), 1111.9, delta=1.0)
        self.assertAlmostEqual(ent.metres((59.9, 10.6), (59.9, 10.62)), 1115.0, delta=2.0)

    def test_the_nearest_way_in_wins(self):
        # Between Oslotunnelen's westbound way in (281 m) and Follobanen's southbound (693 m), going south-west,
        # which is either tunnel's way: the nearer.
        ow = next(t for t in ent.TUNNELS if t[0] == "oslotunnelen_w")
        fs = next(t for t in ent.TUNNELS if t[0] == "follobanen_s")
        geo = {"stops": {"A": [59.92, 10.77], "B": [59.90, 10.74], ent.TUNNEL_STOP + ow[0]: list(ow[2]),
                         ent.TUNNEL_STOP + fs[0]: list(fs[2])}}
        at = (59.9100, 10.7560)
        self.assertLess(ent.metres(at, ow[1]), ent.metres(at, fs[1]))
        self.assertLess(ent.metres(at, fs[1]), ent.ENTRY_M)
        self.assertIs(ent.tunnel_at(at, "A", "B", geo), ow)
        self.assertIs(ent.tunnel_at(at, "A", "B", {"stops": {k: v for k, v in geo["stops"].items() if "oslo" not in k}}),
                      fs)

    def test_inside_a_tunnel_and_the_time_left(self):
        geo = {"stops": {"A": [59.889, 10.525], "L": [59.913, 10.640],
                         ent.TUNNEL_STOP + "lysaker_sandvika_e": [59.9147, 10.62993]}}
        e = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_e")
        mid = ((e[1][0] + e[2][0]) / 2, (e[1][1] + e[2][1]) / 2)               # 2.7 km in, on its way
        self.assertIs(ent.tunnel_at(mid, "A", "L", geo), e)
        self.assertAlmostEqual(ent.tunnel_time(mid, e), e[3] / 2, delta=1.0)
        self.assertEqual(ent.tunnel_time(e[1], e), e[3])
        self.assertEqual(ent.tunnel_time((e[1][0] - 0.002, e[1][1] - 0.004), e), e[3])   # outside: never more
        off = (mid[0] + 0.012, mid[1])                                          # 1.3 km off its way
        self.assertIsNone(ent.tunnel_at(off, "A", "L", geo))
        self.assertEqual(ent.ALONG_X, 1.05)
        # Through the parse: a fix frozen halfway in is aimed at the comeback in half the quickest time.
        base_ = load("sources.base")
        ex, _ = self.frozen(epoch(20, 15), 120, at=mid)
        self.assertAlmostEqual(ex[base_.AIM_ETA_KEY], epoch(20, 13) + e[3] / 2, delta=1.0)

    def test_a_new_frozen_fix_does_not_inherit_a_push(self):
        base_ = load("sources.base")
        e = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_e")
        rt_ = ent.EnturRealtime()
        fix_t = epoch(20, 13)
        rt_.parse(positions([(R13, "VYG:Line:R13", "20261107", e[1][0], e[1][1], fix_t)], fix_t), None, fix_t + 5,
                  self.geo)
        rt_.parse(positions([(R13, "VYG:Line:R13", "20261107", e[1][0], e[1][1], fix_t)], fix_t), None, fix_t + 90,
                  self.geo)
        self.assertIn("1672-7", rt_._push)
        # Its next fix, far from any tunnel, is itself already 2 minutes old when read: no push.
        f2, now = epoch(20, 16), epoch(20, 18)
        snap = rt_.parse(positions([(R13, "VYG:Line:R13", "20261107", 59.85, 10.60, f2)], now), None, now, self.geo)
        self.assertNotIn(base_.AIM_ETA_KEY, snap.extras["1672-7"])
        self.assertEqual(snap.stop_codes["1672-7"], "NSR:Quay:21")
        self.assertNotIn("1672-7", rt_._push)

    def test_a_push_runs_on_while_its_fix_stands(self):
        base_ = load("sources.base")
        e = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_e")
        rt_ = ent.EnturRealtime()
        fix_t = epoch(20, 13)
        vp = positions([(R13, "VYG:Line:R13", "20261107", e[1][0], e[1][1], fix_t)], fix_t)
        rt_.parse(vp, None, fix_t + 5, self.geo)
        rt_.parse(vp, None, fix_t + 90, self.geo)
        self.assertIn("1672-7", rt_._push)
        # The timetable has it past Oslo S meanwhile (next stop Dal, which is no reason to push): the push runs on.
        snap = rt_.parse(vp, None, epoch(20, 34), self.geo)
        self.assertEqual(snap.next_stops["1672-7"][0], "Dal stasjon")
        self.assertEqual(snap.stop_codes["1672-7"], ent.TUNNEL_STOP + "lysaker_sandvika_e")
        self.assertEqual(snap.extras["1672-7"][base_.AIM_ETA_KEY], fix_t + e[3])
        # A fresh fix ends it.
        later = epoch(21, 13)
        snap = rt_.parse(positions([(R13, "VYG:Line:R13", "20261107", 60.2, 11.1, later - 5)], later), None, later,
                         self.geo)
        self.assertNotIn("1672-7", rt_._push)
        self.assertNotIn(base_.AIM_ETA_KEY, snap.extras["1672-7"])
        # And a run forgotten takes its push with it.
        rt_._push["x"] = (1, e, 1)
        rt_._fresh["x"] = later - ent.FORGET_S - 1
        rt_.parse(positions([], later), None, later, self.geo)
        self.assertNotIn("x", rt_._push)

    def test_a_push_runs_on_past_its_last_stop(self):
        base_ = load("sources.base")
        e = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_e")
        rt_ = ent.EnturRealtime()
        fix_t = epoch(21, 9)
        vp = positions([(R13, "VYG:Line:R13", "20261107", e[1][0], e[1][1], fix_t)], fix_t)
        rt_.parse(vp, None, fix_t + 5, self.geo)
        rt_._push["1672-7"] = (fix_t, e, fix_t)
        snap = rt_.parse(vp, None, epoch(21, 11), self.geo)              # Dal due 21:10: no stop left
        self.assertNotIn("1672-7", snap.next_stops)
        self.assertEqual(snap.stop_codes["1672-7"], ent.TUNNEL_STOP + "lysaker_sandvika_e")
        self.assertEqual(snap.extras["1672-7"][base_.AIM_ETA_KEY], fix_t + e[3])

    def test_held_with_no_stop_left(self):
        base_ = load("sources.base")
        rt_ = ent.EnturRealtime()
        fix_t = epoch(21, 12)
        vp = positions([(R13, "VYG:Line:R13", "20261107", 60.25, 11.2, fix_t)], fix_t)
        rt_.parse(vp, None, fix_t + 5, self.geo)
        snap = rt_.parse(vp, None, fix_t + 120, self.geo)
        self.assertNotIn("1672-7", snap.next_stops)
        self.assertEqual({k: snap.extras["1672-7"][k] for k in ent.HOLD}, ent.HOLD)
        snap = ent.EnturRealtime().parse(positions([(R13, "VYG:Line:R13", "20261107", 60.25, 11.2, fix_t)], fix_t + 5),
                                         None, fix_t + 5, self.geo)
        self.assertNotIn(base_.AIM_ETA_KEY, snap.extras["1672-7"])        # fresh: nothing

    def test_the_service_day_that_spans_now(self):
        # The run date says the 8th, the timetable has it on the 7th (20:00-21:10): read at 20:10 on the 7th, the
        # 7th's rows; the 8th's would put Oslo S a day ahead.
        rt_ = ent.EnturRealtime()
        now = epoch(20, 10)
        rows = rt_._run_rows(R13, "20261108", self.geo, now)
        self.assertEqual(rows[1][2], epoch(20, 30))
        snap = rt_.parse(positions([(R13, "VYG:Line:R13", "20261108", 59.8, 10.4, now - 10)], now), None, now,
                         self.geo)
        self.assertEqual(snap.next_stops["1672-8"], ("Oslo S", epoch(20, 30)))
        # The day after, likewise; the run date's own when it spans now; none spanning: the run date's.
        self.assertEqual(rt_._run_rows(R13, "20261106", self.geo, now)[1][2], epoch(20, 30))
        self.assertEqual(rt_._run_rows(R13, "20261107", self.geo, now)[1][2], epoch(20, 30))
        far = epoch(20, 10) + 3 * 86400
        self.assertEqual(rt_._run_rows(R13, "20261107", self.geo, far)[1][2], epoch(20, 30))
        self.assertEqual(rt_._run_rows(R13, "bad", self.geo, now), [])
        # The window's edges: 2 h before the first time, 6 h after the last.
        self.assertTrue(rt_._spans(rows, epoch(18, 0)))
        self.assertFalse(rt_._spans(rows, epoch(17, 59)))
        self.assertTrue(rt_._spans(rows, epoch(21, 10) + 6 * 3600))
        self.assertFalse(rt_._spans(rows, epoch(21, 10) + 6 * 3600 + 60))
        self.assertFalse(rt_._spans([], now))

    def test_tunnels_table(self):
        ids = [t[0] for t in ent.TUNNELS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 14)
        for t in ent.TUNNELS:
            self.assertEqual(self.geo["stops"][ent.TUNNEL_STOP + t[0]], list(t[2]))
            self.assertGreater(t[3], ent.FROZEN_S)
            self.assertLess(ent.metres(t[1], t[2]) / t[3], 200 / 3.6)  # never faster than 200 km/h
        self.assertEqual(self.geo["distill_v"], 2)

    def test_left_at(self):
        row = (2, "NSR:Quay:21", 1000.0, 1120.0)
        self.assertEqual(ent.left_at(row, {}), 1120.0)
        self.assertEqual(ent.left_at(row, {2: 60}), 1180.0)
        self.assertEqual(ent.left_at(row, {3: 600, 1: 30}), 1150.0)      # the last delay at or before it
        self.assertEqual(ent.left_at(row, {1: 30, 0: 10}), 1150.0)       # the last, not the first
        self.assertEqual(ent.left_at((2, "x", 1000.0, None), {}), 1000.0)
        self.assertIsNone(ent.left_at((2, "x", None, None), {1: 5}))


def tunnel_zip(arrive="20:06:00"):
    """Sandvika to Lysaker through Lysaker-Sandvika eastbound: the shape runs through its way in and its comeback."""
    files = {
        "agency.txt": "agency_id,agency_name,agency_url,agency_timezone\nVY,Vy,https://www.vy.no,Europe/Oslo\n",
        "routes.txt": "route_id,agency_id,route_short_name,route_long_name,route_type,route_color\n"
                      "VYG:Line:R13,VY,R13,Drammen-Oslo S-Dal,100,DF2027\n",
        "calendar_dates.txt": "service_id,date,exception_type\nS7,20261107,1\n",
        "trips.txt": "route_id,trip_id,service_id,trip_headsign,shape_id\nVYG:Line:R13,VYG:ServiceJourney:1672_1-R,S7,Dal,SH1\n",
        "stops.txt": "stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station\n"
                     "NSR:Quay:1,Sandvika stasjon,59.8890,10.5250,0,\nNSR:Quay:2,Lysaker stasjon,59.9130,10.6400,0,\n",
        "stop_times.txt": "trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type\n"
                          "VYG:ServiceJourney:1672_1-R,20:00:00,20:00:00,NSR:Quay:1,1,0,0\n"
                          f"VYG:ServiceJourney:1672_1-R,{arrive},{arrive},NSR:Quay:2,2,0,0\n",
        "shapes.txt": "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n"
                      "SH1,59.8890,10.5250,1\nSH1,59.89673,10.53845,2\nSH1,59.91470,10.62993,3\nSH1,59.9130,10.6400,4\n",
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for k, v in files.items():
            z.writestr(k, v)
    return buf.getvalue()


class TestTunnelOnTheMap(unittest.TestCase):
    """The rule through the estimate (projection.apply, geometry.Projector), as drawn."""

    def run_polls(self, polls, arrive="20:06:00"):
        geometry = load("geometry")
        projection = load("projection")
        geo = ent.distill(tunnel_zip(arrive), lib.INTERCITY_LETTERS, {}, DAY)
        proj, rt_ = geometry.Projector(geo), ent.EnturRealtime()
        out = []
        for now, (lat, lon, fix_t) in polls:
            snap = rt_.parse(positions([(R13, "VYG:Line:R13", "20261107", lat, lon, fix_t)], now), None, now, geo)
            o = snap.observations[0]
            rec = {"latitude": o.lat, "longitude": o.lon, "in_service": True}      # as Fleet publishes the fix
            projection.apply(proj, snap, {"vehicles": {"1672-7": rec}}, now, True, True, None)
            out.append((rec["latitude"], rec["longitude"], snap))
        return out

    def test_pushed_to_the_comeback_and_held_there(self):
        e = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_e")
        f0, f1 = epoch(20, 0, ) + 30, epoch(20, 1)
        polls = [(f0 + 5, (59.8920, 10.5300, f0)), (f1 + 5, (e[1][0], e[1][1], f1))]
        polls += [(f1 + s, (e[1][0], e[1][1], f1)) for s in (65, 90, 120, e[3] + 1, e[3] + 60, e[3] + 150)]
        out = self.run_polls(polls)
        d = [ent.metres(o[:2], e[2]) for o in out]
        self.assertTrue(all(d[i + 1] <= d[i] + 1 for i in range(1, len(d) - 1)), d)     # never backwards
        self.assertGreater(d[3], 500)                       # on its way, not there yet
        for x in d[5:]:
            self.assertLess(x, 60)                          # at the comeback point, and held there
        self.assertLess(ent.metres(out[-1][:2], e[2]), ent.metres(out[-1][:2], (59.9130, 10.6400)))   # not at Lysaker

    def test_pushed_the_right_way_after_a_fix_wandered_back(self):
        # Its last two fixes went BACK 300 m along the line (as at Oslo S's platforms): the push still goes on to
        # the comeback point, not back the way the fixes pointed.
        e = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_e")
        f0, f1 = epoch(20, 0) + 30, epoch(20, 1)
        ahead = (e[1][0] + 0.0009, e[1][1] + 0.0046)                     # 300 m on toward the comeback
        polls = [(f0 + 5, (ahead[0], ahead[1], f0)), (f1 + 5, (e[1][0], e[1][1], f1))]
        polls += [(f1 + s, (e[1][0], e[1][1], f1)) for s in (65, 120, e[3] + 30)]
        out = self.run_polls(polls)
        self.assertLess(ent.metres(out[-1][:2], e[2]), 60)

    def test_held_not_moved_on_when_the_estimate_has_passed(self):
        # Due at Lysaker at 20:02: by 20:02:31 its estimate has passed and the frozen train stays where it is drawn,
        # though two fixes give it a speed.
        e = next(t for t in ent.TUNNELS if t[0] == "lysaker_sandvika_e")
        f0, f1 = epoch(20, 0) + 30, epoch(20, 1)
        out = self.run_polls([(f0 + 5, (59.8920, 10.5300, f0)), (f1 + 5, (e[1][0], e[1][1], f1)),
                              (f1 + 91, (e[1][0], e[1][1], f1)), (f1 + 300, (e[1][0], e[1][1], f1))], arrive="20:02:00")
        # Where it was drawn 5 s after its fix (a little past it, at its speed), and no farther.
        self.assertLess(ent.metres(out[-1][:2], e[1]), 300)
        self.assertLess(ent.metres(out[-1][:2], out[1][:2]), 1)
        self.assertLess(ent.metres(out[-2][:2], out[1][:2]), 1)


class TestOperators(unittest.TestCase):
    def test_registered(self):
        vy, goa = operators.OPERATORS["vy"], operators.OPERATORS["go_ahead_norge"]
        self.assertEqual((vy.name, vy.short, vy.regions), ("Vy", "Vy", ("NO",)))
        self.assertEqual((goa.name, goa.short, goa.regions), ("Go-Ahead Norge", "Go-Ahead", ("NO",)))
        for op, cs in ((vy, "VYG"), (goa, "GOA")):
            self.assertEqual(op.source, operators.SOURCE_ENTUR)
            self.assertEqual(op.source_options, {"consumer": lib.INTERCITY, "codespace": cs})
            self.assertEqual(op.attribution, lib.ATTRIBUTION)
            self.assertEqual(op.terms_url, lib.TERMS_URL)
            self.assertTrue(op.derive_speed and op.gtfs_from_source and op.timed_without_fix)
            self.assertIsNone(op.timed_after_s)
            self.assertFalse(op.needs_key)
            self.assertEqual(op.scan_interval_s, 30)
        self.assertEqual(operators.regions_in_use()["NO"], "Norway")
        # SJ Nord since 2026-11-08, on Entur's SIRI ET (tests/test_entur_et_source.py).
        self.assertEqual([o.id for o in operators.operators_in("NO")], ["go_ahead_norge", "sj_nord", "vy"])

    def test_lateness(self):
        lt = norway.norway_lateness
        self.assertEqual(lt({"route_code": "R13"}), {"late_threshold_min": 4, "very_late_threshold_min": 8})
        self.assertEqual(lt({"route_code": "RE10"}), {"late_threshold_min": 4, "very_late_threshold_min": 8})
        self.assertEqual(lt({"route_code": "F4"}), {"late_threshold_min": 6, "very_late_threshold_min": 12})
        self.assertEqual(lt({"route_code": "F5"}), {"late_threshold_min": 6, "very_late_threshold_min": 12})
        self.assertEqual(lt({"route_code": "RE20"}), {"late_threshold_min": 6, "very_late_threshold_min": 12})
        self.assertEqual(lt({"route_code": "RX20"}), {"late_threshold_min": 6, "very_late_threshold_min": 12})
        self.assertEqual(lt({}), {"late_threshold_min": 4, "very_late_threshold_min": 8})
        rec = {"route_code": "F1", "train": "1", "line_name": "x"}
        self.assertEqual(operators.OPERATORS["vy"].lateness_for(rec)["late_threshold_min"], 6)

    def test_look(self):
        style = operators.OPERATORS["vy"].marker_keys
        away = style({"route_code": "R13", "route_color": "DF2027", "toward_hub": False})
        self.assertEqual(away, {"marker_color": "#DF2027", "marker_ring_color": "#FFFFFF", "marker_ring_width": 3,
                                "marker_label_color": "#FFFFFF", "marker_label_outline_color": "none",
                                "marker_arrow_color": "#DF2027", "marker_arrow_outline_color": "#FFFFFF",
                                "marker_label": "R13"})
        toward = style({"route_code": "RE10", "route_color": "44c8f5", "toward_hub": True})
        self.assertEqual((toward["marker_color"], toward["marker_ring_color"], toward["marker_label_color"],
                          toward["marker_arrow_color"], toward["marker_arrow_outline_color"]),
                         ("#FFFFFF", "#44C8F5", "#44C8F5", "#FFFFFF", "#44C8F5"))
        unknown = style({"route_code": "R13", "route_color": "DF2027"})
        self.assertEqual(unknown["marker_color"], "#DF2027")
        self.assertEqual(style({"route_color": "DF2027", "toward_hub": "true"})["marker_color"], "#DF2027")  # True only
        no_colour = style({"route_code": "R12", "route_color": "red"})
        self.assertEqual(no_colour["marker_color"], "#DF2027")          # Vy's own red
        goa = operators.OPERATORS["go_ahead_norge"].marker_keys({"toward_hub": False})
        self.assertEqual(goa["marker_color"], "#0054A6")
        self.assertNotIn("marker_label", goa)                            # no code: Fleet's number stays
        self.assertNotIn("marker_label", style({"route_code": "  "}))


class Replay(unittest.TestCase):
    """The fixtures through the shared client (fed the recorded bodies) and the parse."""

    def run_code(self, code, cs):
        doc = json.load(gzip.open(FIX / f"entur_{code}_rt_20261107.json.gz", "rt", encoding="utf-8"))
        geo = json.load(gzip.open(FIX / f"entur_{code}_geometry_20261107.json.gz", "rt", encoding="utf-8"))
        state = {"t": 0}

        class Resp:
            headers = {}

            def __init__(self, b):
                self.b = io.BytesIO(b)

            def read(self, n=-1):
                return self.b.read() if n is None or n < 0 else self.b.read(n)

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def opener(req, timeout=None):
            _, g, u = state["poll"]
            if req.get_method() == "POST":
                return Resp(doc["gql"][g].encode())
            if u is None:
                raise OSError("no update captured")
            return Resp(base64.b64decode(doc["tu"][u]))

        client = lib.EnturClient([(lib.INTERCITY, cs)], opener=opener, clock=lambda: float(state["t"]))
        rt_ = ent.EnturRealtime()
        out = []
        for poll in doc["polls"]:
            state["poll"], state["t"] = poll, poll[0]
            vp, tu = client.for_consumer(lib.INTERCITY, cs, force=True)
            out.append(rt_.parse(vp, tu, float(poll[0]), geo))
        return doc, geo, out

    def test_vy(self):
        doc, geo, snaps = self.run_code("vyg", "VYG")
        self.assertEqual(len(snaps), 40)
        obs = [o for s in snaps for o in s.observations]
        self.assertGreater(len(obs), 200)
        # No bus reached a train's feed; every train has a line code, a line and a hub answer.
        self.assertTrue(all(not lib.is_bus(s.route_keys[o.vehicle_id]) for s in snaps for o in s.observations))
        self.assertTrue(all(s.extras[o.vehicle_id].get("route_code") for s in snaps for o in s.observations))
        self.assertTrue(all(s.route_keys[o.vehicle_id] in geo["trains"] for s in snaps for o in s.observations))
        self.assertTrue(all(isinstance(s.extras[o.vehicle_id].get("toward_hub"), bool)
                            for s in snaps for o in s.observations))
        with_next = sum(1 for s in snaps for o in s.observations if o.vehicle_id in s.next_stops)
        self.assertGreater(with_next, len(obs) // 2)
        # One identity per number; RE20's 398-138 is train 138 (Vy's own vehicle id).
        ids = {}
        for s in snaps:
            for o in s.observations:
                ids.setdefault(o.train, set()).add(o.vehicle_id)
        self.assertTrue(all(len(v) == 1 for v in ids.values()))
        if any("398-138" in t for t in doc["trips"]):
            self.assertIn("138", ids)
            self.assertNotIn("398", ids)
        self.assertTrue(all(o.observed_at is not None for o in obs))

    def test_go_ahead(self):
        _, geo, snaps = self.run_code("goa", "GOA")
        obs = [o for s in snaps for o in s.observations]
        self.assertGreater(len(obs), 20)
        codes = {s.extras[o.vehicle_id].get("route_code") for s in snaps for o in s.observations}
        self.assertTrue(codes <= {"F5", "R50"})


if __name__ == "__main__":
    unittest.main()
