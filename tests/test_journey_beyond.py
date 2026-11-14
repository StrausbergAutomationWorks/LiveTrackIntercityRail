"""sources/journey_beyond.py and operators/journey_beyond.py on the SHIPPED data (Intercity SSOT 8.13): the timetable
transcribed 2026-11-14 and the lines built on OpenStreetMap (tools/journey_beyond.py). The data is the input, so these
tests read it as installed."""

import datetime as dt
import gzip
import json
import math
import os
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _load import load  # noqa: E402

src = load("sources.journey_beyond")
geometry = load("geometry")
projection = load("projection")
ops = load("operators")
pictures = load("pictures")
DATA = src.load()
TT = DATA["tt"]
GEO = src.distill(DATA)
UTC = dt.timezone.utc


def z(y, mo, d, h, mi=0):
    return dt.datetime(y, mo, d, h, mi, tzinfo=UTC).timestamp()


def km(a, b, c, d):
    p = math.pi / 180
    h = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def nearest(lat, lon, line):
    """(km off the line, km along it) of a point, flat-earth per segment."""
    best, along, run = float("inf"), 0.0, 0.0
    kx = math.cos(math.radians(lat)) * 111.32
    for (a, b), (c, d) in zip(line, line[1:]):
        ax, ay, bx, by = (b - lon) * kx, (a - lat) * 110.57, (d - lon) * kx, (c - lat) * 110.57
        dx, dy = bx - ax, by - ay
        t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / (dx * dx + dy * dy)))
        off = math.hypot(ax + t * dx, ay + t * dy)
        seg = km(a, b, c, d)
        if off < best:
            best, along = off, run + t * seg
        run += seg
    return best, along


class Data(unittest.TestCase):
    def test_version_and_horizon(self):
        self.assertEqual(TT["v"], src.DATA_VERSION)
        self.assertEqual(src.last_departure(TT), dt.date(2027, 12, 29))     # the Indian Pacific's last listed
        self.assertEqual(TT["credit"], "Timetable: Journey Beyond (journeybeyondrail.com.au)")

    def test_zones(self):
        zones = {sid: s[3] for sid, s in TT["stations"].items()}
        self.assertEqual(zones["BKH"], "Australia/Broken_Hill")             # NSW on Adelaide time (decision 6)
        self.assertEqual((zones["COK"], zones["RWL"]), ("Australia/Adelaide", "Australia/Perth"))
        self.assertEqual((zones["ASP"], zones["DRW"], zones["CBR"]), ("Australia/Darwin",) * 2 + ("Australia/Sydney",))
        self.assertTrue(all(zones.values()))

    def test_lines_and_distances(self):
        lines = DATA["lines"]["lines"]
        self.assertEqual({k.split("#")[0] for k in lines}, set(TT["patterns"]))
        for pid, p in TT["patterns"].items():
            ms = [c[3] for c in p["calls"]]
            self.assertEqual(ms, sorted(ms), pid)
            secs = [lines[f"{pid}#{n}"][0] for n in range(len(p["sections"]))]
            self.assertAlmostEqual(ms[-1], sum(secs), delta=2.0)
        # Journey Beyond publishes 2,979 km for the Ghan and 828 km for The Overland.
        self.assertAlmostEqual(lines["GHAN_N_3D#0"][0] / 1000, 2979, delta=15)
        self.assertAlmostEqual(lines["OVL_W_SUN#0"][0] / 1000, 828, delta=10)
        ip = lines["IP_W#0"][0] + lines["IP_W#1"][0]
        self.assertAlmostEqual(ip / 1000, 4352, delta=60)

    def test_sections_where_the_train_reverses(self):
        # Adelaide for the Indian Pacific both ways, Canberra for the Great Southern north; nowhere else.
        cuts = {pid: [p["calls"][s][0] for s in p["sections"][1:]] for pid, p in TT["patterns"].items()}
        self.assertEqual({k: v for k, v in cuts.items() if v}, {"IP_W": ["ADL"], "IP_E": ["ADL"], "GS_N": ["CBR"]})
        p = TT["patterns"]["IP_E"]                                            # EPT KAL COK LPL ADL BKH KTM SYD
        self.assertEqual([src.section_of(p, i) for i in range(8)], [0, 0, 0, 0, 1, 1, 1, 1])

    def test_every_departure_runs_forward(self):
        n = 0
        for pid, first, weeks, dep, arr in TT["runs"]:
            for k in range(weeks):
                day = dt.date.fromisoformat(first) + dt.timedelta(weeks=k)
                self.assertIsNotNone(src.run_calls(TT, pid, day, dep, arr), (pid, day))
                n += 1
        self.assertEqual(n, 507)


class Rules(unittest.TestCase):
    def test_decode(self):
        self.assertEqual(src.decode([-3493806, 13858113, 100, -200]), [[-34.93806, 138.58113], [-34.93706, 138.57913]])

    def test_local_clock_per_station(self):
        day = dt.date(2026, 11, 22)                                          # South Australia and NSW on daylight saving
        self.assertEqual(src.local_epoch(day, 12 * 60 + 15, "Australia/Adelaide"), z(2026, 11, 22, 1, 45))
        self.assertEqual(src.local_epoch(day, 2 * 1440 + 17 * 60 + 30, "Australia/Darwin"), z(2026, 11, 24, 8, 0))
        self.assertEqual(src.local_epoch(day, 0, "Australia/Broken_Hill"), src.local_epoch(day, 0, "Australia/Adelaide"))
        self.assertEqual(src.local_epoch(day, 1440, "Australia/Adelaide"), z(2026, 11, 22, 13, 30))   # next midnight
        winter = dt.date(2027, 6, 5)
        self.assertEqual(src.local_epoch(winter, 14 * 60 + 30, "Australia/Adelaide"), z(2027, 6, 5, 5, 0))

    def test_ghan_22_november(self):
        calls = src.run_calls(TT, "GHAN_N_3D", dt.date(2026, 11, 22), 12 * 60 + 15, 2 * 1440 + 17 * 60 + 30)
        self.assertEqual([c["stop"] for c in calls], ["ADL", "MLA", "ASP", "KTR", "DRW"])
        self.assertEqual(calls[0]["aimed_departure"], z(2026, 11, 22, 1, 45))
        self.assertEqual((calls[2]["aimed_arrival"], calls[2]["aimed_departure"]), (z(2026, 11, 23, 4, 15),
                                                                                     z(2026, 11, 23, 8, 45)))
        self.assertEqual(calls[-1]["aimed_arrival"], z(2026, 11, 24, 8, 0))
        # Marla and Katherine have no time: paced by distance between the timed calls either side (decision 3).
        for i, a in ((1, (0, 2)), (3, (2, 4))):
            t0, t1 = calls[a[0]]["aimed_departure"], calls[a[1]]["aimed_arrival"]
            share = (calls[i]["m"] - calls[a[0]]["m"]) / (calls[a[1]]["m"] - calls[a[0]]["m"])
            self.assertAlmostEqual(calls[i]["aimed_arrival"], t0 + share * (t1 - t0), places=3)
            self.assertTrue(calls[i]["paced"])
            self.assertEqual(calls[i]["aimed_arrival"], calls[i]["aimed_departure"])

    def test_the_calendar_wins_for_the_ends(self):
        # Indian Pacific: calendar 14:15 from Sydney and 12:25 into Sydney; the pages 14:10 and 12:30.
        w = src.run_calls(TT, "IP_W", dt.date(2026, 12, 2), 14 * 60 + 15, 3 * 1440 + 14 * 60 + 45)
        self.assertEqual(w[0]["aimed_departure"], z(2026, 12, 2, 3, 15))      # 14:15 AEDT
        self.assertEqual(w[-1]["aimed_arrival"], z(2026, 12, 5, 6, 45))       # 14:45 AWST
        e = src.run_calls(TT, "IP_E", dt.date(2026, 11, 21), 17 * 60 + 55, 4 * 1440 + 12 * 60 + 25)
        self.assertEqual(e[-1]["aimed_arrival"], z(2026, 11, 25, 1, 25))      # 12:25 AEDT, the page's 12:30 not used
        runs = {(r[0], r[1]): r for r in TT["runs"]}
        self.assertEqual(runs[("IP_E", "2026-11-21")][3:], [17 * 60 + 55, 4 * 1440 + 12 * 60 + 25])
        self.assertEqual(runs[("EXP_S_SAT", "2027-04-10")][4], 3 * 1440 + 10 * 60 + 30)
        self.assertEqual(runs[("GS_N", "2026-12-24")][3], 15 * 60 + 30)       # the Thursday before Christmas

    def test_a_run_that_does_not_run_forward_is_refused(self):
        self.assertIsNone(src.run_calls(TT, "OVL_W_SUN", dt.date(2026, 11, 22), 20 * 60, 18 * 60 + 50))
        self.assertIsNone(src.run_calls(TT, "NOPE", dt.date(2026, 11, 22), 0, 60))

    def test_departures_window(self):
        got = {(p, d.isoformat()) for p, d, _, _ in src.departures(TT, z(2026, 11, 14, 18))}
        self.assertIn(("IP_E", "2026-11-14"), got)
        self.assertIn(("GHAN_N_3D", "2026-11-15"), got)
        self.assertNotIn(("GHAN_N_3D", "2026-11-22"), got)
        self.assertFalse(list(src.departures(TT, z(2028, 3, 1, 0))))         # after the horizon, nothing
        # The Indian Pacific from Perth is out four days and more: still listed on its fourth day.
        self.assertIn(("IP_E", "2026-11-14"), {(p, d.isoformat()) for p, d, _, _ in src.departures(TT, z(2026, 11, 18, 0))})

    def test_hover(self):
        self.assertEqual(src.hover("The Ghan", ["Adelaide", "Marla", "Darwin"]), "The Ghan · Adelaide–Darwin")


class View(unittest.TestCase):
    def test_version_is_the_files_digest(self):
        v = src.StaticView()
        self.assertEqual(src.read(v), f"jb{DATA['digest'][:12]}|g1")
        self.assertIsNone(v.static_path())
        g = v.distill_geometry()
        self.assertEqual({k.split("#")[0] for k in g["trains"]}, set(TT["patterns"]))
        self.assertEqual((g["trains"]["IP_E#0"], g["trains"]["IP_E#1"]), (["IP_E#0"], ["IP_E#1"]))
        self.assertEqual(g["train_routes"]["GS_N#1"], "Great Southern")
        self.assertEqual(g["stop_names"]["BKH"], "Broken Hill")
        self.assertEqual(g["v"], geometry.GEOMETRY_VERSION)
        self.assertEqual(g["stops"]["ADL"], [-34.93806, 138.58113])         # latitude first

    def test_a_file_of_another_version_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            tt, ln = pathlib.Path(d) / "tt.json", pathlib.Path(d) / "ln.json.gz"
            tt.write_text(json.dumps(dict(TT, v=99)), encoding="utf-8")
            ln.write_bytes(gzip.compress(json.dumps(DATA["lines"]).encode("utf-8")))
            with self.assertRaises(ValueError):
                src.load(str(tt), str(ln))


class Parse(unittest.TestCase):
    def test_now_on_14_november(self):
        # 18:00 UTC 14 Nov 2026: the Indian Pacific left Perth 17:55 AWST (09:55 UTC); the Ghan leaves at 01:45 UTC.
        s = src.JourneyBeyondTimetable().parse(z(2026, 11, 14, 18), GEO)
        keys = {o.vehicle_id: o for o in s.observations}
        self.assertEqual(set(keys), {"indian_pacific-14"})
        e = s.extras["indian_pacific-14"]
        self.assertEqual(e["line_name"], "Indian Pacific · Perth–Sydney")
        self.assertEqual((e["service_family"], e["service_direction"], e["route_code"]), ("indian_pacific", "back", "IP_E"))
        self.assertEqual(s.route_keys["indian_pacific-14"], "IP_E#0")
        self.assertEqual(s.next_stops["indian_pacific-14"][0], "Kalgoorlie")
        self.assertEqual(s.next_stops["indian_pacific-14"][1], z(2026, 11, 14, 22, 0))   # 06:00 AWST
        self.assertEqual(keys["indian_pacific-14"].train, "Indian Pacific")
        self.assertNotIn("delay_min", e)

    def test_standing_at_origin_then_running(self):
        p = src.JourneyBeyondTimetable()
        s = p.parse(z(2026, 11, 15, 1, 42), GEO)                              # 3 minutes before 12:15 ACDT
        o = next(o for o in s.observations if o.vehicle_id == "the_ghan-15")
        self.assertAlmostEqual(o.lat, TT["stations"]["ADL"][1])
        self.assertEqual(s.next_stops["the_ghan-15"][0], "Marla")
        self.assertIsNone(s.extras["the_ghan-15"][src.AIM_ETA_KEY])           # standing: held, not timed
        s = p.parse(z(2026, 11, 15, 3), GEO)
        self.assertEqual(s.extras["the_ghan-15"][src.AIM_ETA_KEY], s.next_stops["the_ghan-15"][1])

    def test_running_aims_at_the_next_arrival(self):
        # The Ghan of 22 Nov toward Alice Springs, due 13:45 ACST (04:15 UTC), leaving 18:15: aimed at the arrival.
        s = src.JourneyBeyondTimetable().parse(z(2026, 11, 23, 3), GEO)
        self.assertEqual(s.next_stops["the_ghan-22"], ("Alice Springs", z(2026, 11, 23, 4, 15)))
        self.assertEqual(s.extras["the_ghan-22"][src.AIM_ETA_KEY], z(2026, 11, 23, 4, 15))

    def test_the_section_after_adelaide(self):
        # The Indian Pacific of 5 Dec leaves Adelaide 22:40 ACDT on 7 Dec (12:10 UTC): on its second section after.
        p = src.JourneyBeyondTimetable()
        self.assertEqual(p.parse(z(2026, 12, 7, 6), GEO).route_keys["indian_pacific-5"], "IP_E#0")
        self.assertEqual(p.parse(z(2026, 12, 8, 0), GEO).route_keys["indian_pacific-5"], "IP_E#1")

    def test_no_timetable(self):
        s = src.JourneyBeyondTimetable().parse(z(2026, 11, 14, 18), None)
        self.assertEqual((s.observations, s.skipped), ([], {"no_timetable": 1}))


class Operator(unittest.TestCase):
    def test_registered(self):
        op = ops.OPERATORS["journey_beyond"]
        self.assertEqual((op.name, op.short, op.regions), ("Journey Beyond", "Journey Beyond", ("AU",)))
        self.assertEqual(op.source, ops.SOURCE_JOURNEY_BEYOND)
        self.assertIn(ops.SOURCE_JOURNEY_BEYOND, ops.SOURCES)
        self.assertEqual(op.lateness_keys(), {})
        self.assertTrue(op.timed_without_fix and op.gtfs_from_source)
        self.assertFalse(op.needs_key)
        self.assertEqual(op.attribution, "Timetable: Journey Beyond (journeybeyondrail.com.au)")
        self.assertIn(op, ops.operators_in("AU"))

    def test_pictures(self):
        op = ops.OPERATORS["journey_beyond"]
        want = {("the_ghan", "out"): "jb_ghan_out", ("ghan_expedition", "back"): "jb_ghan_back",
                ("indian_pacific", "out"): "jb_indian_pacific_out", ("indian_pacific", "back"): "jb_indian_pacific_back",
                ("great_southern", "out"): "jb_great_southern_out", ("great_southern", "back"): "jb_great_southern_back",
                ("the_overland", "out"): "jb_overland_out", ("the_overland", "back"): "jb_overland_back"}
        for (svc, way), name in want.items():
            k = op.marker_keys({"service_family": svc, "service_direction": way})
            self.assertEqual(k, {"entity_picture": pictures.url(name)})       # no label tag (decision 8)
            self.assertTrue(pictures.path(name).is_file())
        self.assertEqual(op.marker_keys({"service_family": "other"}), {})

    def test_every_pattern_has_a_picture(self):
        op = ops.OPERATORS["journey_beyond"]
        for p in TT["patterns"].values():
            self.assertIn("entity_picture", op.marker_keys({"service_family": p["service"], "service_direction": p["dir"]}))


@unittest.skipIf(os.environ.get("JB_FAST"), "JB_FAST: replays skipped")
class Replay(unittest.TestCase):
    """Two windows through the estimate as drawn (projection.apply), every 60 s: each train ON its own line, never drawn
    backwards along it, and drawn to its terminus. MEASURED, printed and bounded."""

    def run_window(self, t, end, label):
        p, proj = src.JourneyBeyondTimetable(), geometry.Projector(GEO)
        worst, back, polls, prev, reach, seen, sec, sections = 0.0, 0, 0, {}, {}, set(), {}, 0
        while t <= end:
            s = p.parse(t, GEO)
            vehicles = {o.vehicle_id: {"latitude": o.lat, "longitude": o.lon, "in_service": True}
                        for o in s.observations}
            projection.apply(proj, s, {"vehicles": vehicles}, t, False, True, None)
            for k, r in vehicles.items():
                line = GEO["shapes"][s.route_keys[k]]
                off, along = nearest(r["latitude"], r["longitude"], line)
                worst = max(worst, off)
                if sec.get(k) != s.route_keys[k]:                         # a new section: measured along it afresh
                    sections += k in sec
                    sec[k] = s.route_keys[k]
                    prev.pop(k, None)
                if k in prev and along < prev[k] - 0.5:
                    back += 1
                prev[k] = along
                total = nearest(*line[-1], line)[1]
                reach[k] = max(reach.get(k, 0.0), along / total)
                seen.add(k)
            polls += 1
            t += 60
        done = {k: v for k, v in reach.items() if k not in vehicles}       # runs that ended inside the window
        print(f"\nJOURNEY BEYOND REPLAY {label}: {polls} polls, {len(seen)} runs {sorted(seen)}, worst off its "
              f"line {worst * 1000:.0f} m, moves back over 0.5 km: {back}, section changes {sections}, least share reached by "
              f"the {len(done)} runs that ended {min(done.values()):.3f}")
        self.assertLess(worst, 0.3)
        self.assertEqual(back, 0)
        self.assertGreater(min(done.values()), 0.99)
        return seen, sections

    def test_november(self):
        seen, sections = self.run_window(z(2026, 11, 21, 12), z(2026, 11, 27, 12), "21-27 Nov 2026")
        self.assertEqual(sections, 2)                                         # each Indian Pacific at Adelaide
        self.assertTrue({"the_ghan-22", "ghan_expedition-25", "indian_pacific-21", "the_overland-22"} <= seen)

    def test_december_great_southern(self):
        seen, sections = self.run_window(z(2026, 12, 3, 12), z(2026, 12, 11, 12), "3-11 Dec 2026")
        self.assertTrue({"great_southern-4", "great_southern-7"} <= seen)
        # The Indian Pacific of 5 Dec (Adelaide on the 7th) and of 9 Dec (the 10th), the Great Southern of 4 Dec at
        # Canberra. The 2 Dec Indian Pacific left Adelaide before the window opens (05:35 UTC 3 Dec).
        self.assertEqual(sections, 3)


if __name__ == "__main__":
    unittest.main()
