"""sources/irish_rail.py and operators/irish_rail.py on the 2026-11-09 capture (Intercity SSOT 8.10): the NTA timetable
distilled for that day (tests/fixtures/irish_rail_geometry_20261109.json.gz) and every Hacon read 02:48Z-13:59Z
(tests/fixtures/irish_rail_hacon_20261109.json.gz)."""

import bisect
import copy
import datetime as dt
import gzip
import json
import math
import pathlib
import statistics
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _load import load  # noqa: E402

src = load("sources.irish_rail")
geometry = load("geometry")
projection = load("projection")
ops = load("operators")
FIX = pathlib.Path(__file__).resolve().parent / "fixtures"
GEO = json.loads(gzip.open(FIX / "irish_rail_geometry_20261109.json.gz").read())
POLLS = json.loads(gzip.open(FIX / "irish_rail_hacon_20261109.json.gz").read())
TIMES = [p[0] for p in POLLS]
UTC = dt.timezone.utc


def at(h, m=0):
    return dt.datetime(2026, 11, 9, h, m, tzinfo=UTC).timestamp()


def poll_at(t):
    return POLLS[max(0, bisect.bisect_right(TIMES, t) - 1)]


def km(a, b, c, d):
    p = math.pi / 180
    h = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


class Rules(unittest.TestCase):
    def test_direction(self):
        self.assertTrue(src.toward_dublin("Galway (Ceannt)", "Dublin Heuston"))
        self.assertFalse(src.toward_dublin("Connolly", "Belfast"))
        self.assertFalse(src.toward_dublin("Limerick (Colbert)", "Limerick Junction"))   # leaves the town
        self.assertTrue(src.toward_dublin("Limerick Junction", "Limerick (Colbert)"))
        self.assertFalse(src.toward_dublin("Galway (Ceannt)", "Athenry"))
        self.assertIsNone(src.toward_dublin("Nowhere", "Galway (Ceannt)"))
        self.assertEqual(sum(1 for v in GEO["ir_trips"].values() if v[2] is None), 0)

    def test_service_day(self):
        self.assertEqual(src.service_base(dt.date(2026, 11, 9)), at(0))
        self.assertEqual(src.service_base(dt.date(2026, 7, 1)),
                         dt.datetime(2026, 6, 30, 23, tzinfo=UTC).timestamp())

    def test_enterprise_and_codes(self):
        ent = {v[0] for v in GEO["ir_trips"].values() if v[5]}
        self.assertTrue({"A100", "A101", "A131", "B182"} <= ent)
        self.assertNotIn("A700", ent)
        self.assertTrue(all(v[0][0] in "AB" for v in GEO["ir_trips"].values()))

    def test_stations_join(self):
        names, st = GEO["stop_names"], GEO["ir_stations"]
        self.assertEqual(names[st["CNLLY"]], "Connolly")
        self.assertEqual(names[st["HSTON"]], "Dublin Heuston")
        self.assertEqual(names[st["BFSTC"]], "Belfast")          # 2.43 km apart: joined by name
        self.assertNotIn("CITYJ", st)                             # 0,0 and no such stop

    def test_line_name(self):
        self.assertEqual(src.line_name("A100", True, "Connolly", "Belfast"), "Enterprise A100 · Dublin Connolly–Belfast")
        self.assertEqual(src.line_name("A700", False, "Dublin Heuston", "Galway (Ceannt)"),
                         "Irish Rail A700 · Dublin Heuston–Galway (Ceannt)")


def mini_gtfs():
    """A made-up timetable: the Enterprise A100 Connolly-Belfast, A701 Galway-Heuston, and a commuter P100 that is not
    this consumer's."""
    import io
    import zipfile
    files = {
        "stops.txt": "stop_id,stop_name,stop_lat,stop_lon\nCON,Connolly,53.3531,-6.2459\nDRO,Drogheda (MacBride),53.712,-6.335\n"
                     "BEL,Belfast,54.596,-5.917\nHEU,Dublin Heuston,53.3464,-6.2925\nATH,Athlone,53.4237,-7.9407\n"
                     "GAL,Galway (Ceannt),53.2733,-9.0471\nBRA,Bray,53.2043,-6.1009\n",
        "routes.txt": "route_id,route_short_name,route_long_name,route_type\nR1,,Dublin - Belfast,2\nR2,,Dublin - Galway,2\nR3,,DART,2\n",
        "trips.txt": "route_id,service_id,trip_id,trip_short_name,shape_id\nR1,S1,T1,A100,SH1\nR2,S1,T2,A701,SH2\nR3,S1,T3,P100,SH3\n",
        "shapes.txt": "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\nSH1,53.3531,-6.2459,1\nSH1,54.596,-5.917,2\n"
                      "SH2,53.2733,-9.0471,1\nSH2,53.3464,-6.2925,2\nSH3,53.3531,-6.2459,1\nSH3,53.2043,-6.1009,2\n",
        "stop_times.txt": "trip_id,arrival_time,departure_time,stop_id,stop_sequence\nT1,07:00:00,07:00:00,CON,1\n"
                          "T1,07:30:00,07:32:00,DRO,2\nT1,09:10:00,09:10:00,BEL,3\nT2,06:00:00,06:00:00,GAL,1\n"
                          "T2,07:00:00,07:02:00,ATH,2\nT2,08:30:00,08:30:00,HEU,3\nT3,07:00:00,07:00:00,CON,1\n"
                          "T3,07:40:00,07:40:00,BRA,2\n",
        "calendar.txt": "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n"
                        "S1,1,1,1,1,1,0,0,20261101,20261231\n",
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for k, v in files.items():
            z.writestr(k, v)
    return buf.getvalue()


API = [{"code": "CNLLY", "name": "Dublin Connolly", "lat": 53.3531, "lon": -6.24591},
       {"code": "BFSTC", "name": "Belfast", "lat": 54.6123, "lon": -5.91744},          # 2.4 km off: by name
       {"code": "ATLNE", "name": "Athlone Town", "lat": 53.4239, "lon": -7.9409},      # no such name: by distance
       {"code": "CITYJ", "name": "CITY JUNCTION", "lat": None, "lon": None}]


class Distill(unittest.TestCase):
    def test_cut_flags_dates_and_stations(self):
        d = src.distill(mini_gtfs(), API, "intercity", dt.date(2026, 11, 9))
        self.assertEqual(set(d["ir_trips"]), {"T1", "T2"})                  # P100 is the commuter consumer's
        self.assertEqual(set(d["trains"]), {"T1", "T2"})
        self.assertNotIn("T3", d["trip_stops"])
        self.assertNotIn("SH3", d["shapes"])
        self.assertEqual(d["ir_trips"]["T1"], ["A100", "S1", False, 7 * 3600, 9 * 3600 + 600, True])
        self.assertEqual(d["ir_trips"]["T2"], ["A701", "S1", True, 6 * 3600, 8 * 3600 + 1800, False])
        self.assertEqual(d["ir_dates"]["S1"], ["2026-11-09", "2026-11-10", "2026-11-11", "2026-11-12", "2026-11-13"])
        self.assertEqual(d["ir_stations"], {"CNLLY": "CON", "BFSTC": "BEL", "ATLNE": "ATH"})


class Look(unittest.TestCase):
    def test_shamrock_both_ways(self):
        op = ops.OPERATORS["irish_rail"]
        away = op.marker_keys({"service_family": "InterCity", "toward_hub": False})
        self.assertEqual((away["marker_shape"], away["marker_color"], away["marker_ring_color"], away["marker_label_color"],
                          away["marker_label_outline_color"]), ("shamrock", "#009444", "#FBAF41", "#FBAF41", "#009444"))
        home = op.marker_keys({"service_family": "InterCity", "toward_hub": True})
        self.assertEqual((home["marker_color"], home["marker_ring_color"], home["marker_label_color"],
                          home["marker_label_outline_color"]), ("#FBAF41", "#009444", "#009444", "#FBAF41"))
        self.assertEqual(op.marker_keys({"service_family": "InterCity"}), away)    # unknown: the leaving look

    def test_enterprise_disc(self):
        op = ops.OPERATORS["irish_rail"]
        away = op.marker_keys({"service_family": "Enterprise", "toward_hub": False})
        self.assertNotIn("marker_shape", away)
        # Lee 22:49: the red ring 2 px and outermost, the magenta band (3 px) inside it.
        self.assertEqual((away["marker_color"], away["marker_ring_color"], away["marker_ring_width"],
                          away["marker_inner_ring_color"], away["marker_inner_ring_width"], away["marker_label_color"]),
                         ("#B0BDC0", "#F9031D", 2, "#C10181", 3, "#C10181"))
        home = op.marker_keys({"service_family": "Enterprise", "toward_hub": True})
        self.assertEqual((home["marker_color"], home["marker_ring_color"], home["marker_inner_ring_color"],
                          home["marker_label_color"]), ("#C10181", "#F9031D", "#B0BDC0", "#B0BDC0"))
        self.assertIs(type(away["marker_ring_width"]), int)
        self.assertEqual(op.lateness_keys(), {"late_threshold_min": 10, "very_late_threshold_min": 20})
        self.assertIn("IE", op.regions)


class Parse(unittest.TestCase):
    def setUp(self):
        self.rt = src.IrishRailRealtime()

    def snap(self, t, trains=None):
        return self.rt.parse(poll_at(t)[1] if trains is None else trains, t, GEO)

    def test_ghosts_are_not_drawn(self):
        # The first read with all three (the 02:48Z read was an empty answer, MEASURED).
        t, trains = next(p for p in POLLS if {"A222", "A227", "A229"} <= {x["code"] for x in p[1] if x["status"] == "R"})
        self.assertLess(t, at(5))      # 04:00:40Z, MEASURED
        self.assertTrue({"A222", "A227", "A229"} <= {x["code"] for x in trains if x["status"] == "R"})
        s = self.rt.parse(trains, t, GEO)
        drawn = {o.vehicle_id.split("-")[0] for o in s.observations}
        self.assertFalse({"A222", "A227", "A229"} & drawn)
        self.assertGreaterEqual(s.skipped.get("ghost_or_unmatched", 0), 3)

    def test_genuine(self):
        day, start, end = dt.date(2026, 11, 9), at(17), at(19, 45)
        rep = {"status": "R", "origin_time": start, "delay_s": 600, "date": "2026-11-09"}
        g = src.IrishRailRealtime.genuine
        self.assertTrue(g(rep, day, start, end, at(18)))
        self.assertFalse(g(dict(rep, status="N"), day, start, end, at(18)))
        self.assertFalse(g(dict(rep, origin_time=start - 86400), day, start, end, at(18)))     # yesterday's run
        self.assertFalse(g(rep, day, start, end, end + 600 + src.GHOST_S + 1))                # a ghost
        self.assertTrue(g(rep, day, start, end, end + 600 + src.GHOST_S - 1))
        self.assertFalse(g(rep, day, start, end, start - src.PRE_DEPARTURE_S - src.MATCH_S - 1))
        self.assertTrue(g(dict(rep, origin_time=None), day, start, end, at(18)))             # the documented call
        self.assertFalse(g(dict(rep, origin_time=None, date="2026-11-08"), day, start, end, at(18)))

    def test_a_run_past_midnight_is_yesterdays(self):
        # The timetable's latest run past midnight, on any date it runs; drawn a minute before it arrives.
        late = sorted(((v[4], v, d) for v in GEO["ir_trips"].values() for d in GEO["ir_dates"][v[1]]
                       if v[4] > 24 * 3600), key=lambda x: (x[0], x[2]))
        self.assertTrue(late)
        last, v, iso = late[-1]
        day = dt.date.fromisoformat(iso)
        now = src.service_base(day) + last - 60
        self.assertEqual(src.local_day(now), day + dt.timedelta(days=1))
        s = self.rt.parse([], now, GEO)
        self.assertIn(f"{v[0]}-{day.day}", {o.vehicle_id for o in s.observations})

    def test_timed_to_the_next_arrival(self):
        s = self.snap(at(8))
        timed = [k for k, e in s.extras.items() if e.get("aim_eta") is not None]
        self.assertTrue(timed)
        for k in timed:
            self.assertEqual(s.extras[k]["aim_eta"], s.next_stops[k][1])

    def test_failed_read_is_none_and_empty_still_runs_the_timetable(self):
        self.assertIsNone(self.rt.parse(None, at(8), GEO))
        s = self.rt.parse([], at(8), GEO)
        self.assertGreater(len(s.observations), 20)
        self.assertFalse(s.trip_delays)                      # nobody's word: no delay published
        for o in s.observations:
            self.assertTrue(s.extras[o.vehicle_id]["no_fix"])

    def test_live_delay_and_identity(self):
        t = at(8)
        s = self.snap(t)
        live = {x["code"]: x for x in poll_at(t)[1] if x["status"] == "R" and x["delay_s"] is not None}
        hits = [o for o in s.observations if o.vehicle_id.split("-")[0] in live]
        self.assertGreater(len(hits), 10)
        for o in hits:
            self.assertTrue(o.vehicle_id.endswith("-9"))
            self.assertEqual(o.train, o.vehicle_id.split("-")[0][1:])           # label 700
        some = [o.vehicle_id for o in hits if o.vehicle_id in s.trip_delays]
        self.assertTrue(some)

    def test_last_delay_is_kept_when_the_train_drops_out(self):
        t = at(8)
        s = self.snap(t)
        k = next(k for k in s.trip_delays if s.trip_delays[k] != 0)
        code = k.split("-")[0]
        later = [x for x in poll_at(t + 60)[1] if x["code"] != code]
        s2 = self.rt.parse(later, t + 60, GEO)
        if k in {o.vehicle_id for o in s2.observations}:
            self.assertIn(k, s2.trip_delays)

    def test_terminated_ends_the_run(self):
        t = at(8)
        s = self.snap(t)
        rep = next(x for x in poll_at(t)[1] if x["status"] == "R" and f"{x['code']}-9" in
                   {o.vehicle_id for o in s.observations})
        t2 = copy.deepcopy(poll_at(t + 60)[1])
        for x in t2:
            if x["code"] == rep["code"]:
                x["status"] = "T"
        s2 = self.rt.parse(t2, t + 60, GEO)
        self.assertNotIn(f"{rep['code']}-9", {o.vehicle_id for o in s2.observations})

    def test_a_report_is_a_floor(self):
        t = at(8)
        s = self.snap(t)
        o = next(o for o in s.observations if o.vehicle_id in s.stop_codes)
        tid = s.route_keys[o.vehicle_id]
        rows = GEO["trip_stops"][tid]
        code = o.vehicle_id.split("-")[0]
        back = {v: k for k, v in GEO["ir_stations"].items()}
        target = next(r[1] for r in reversed(rows[:-1]) if r[1] in back)
        trains = [x for x in copy.deepcopy(poll_at(t)[1]) if x["code"] != code]
        base = src.service_base(dt.date(2026, 11, 9))
        trains.append({"code": code, "status": "R", "lat": 1.0, "lon": 1.0, "date": "2026-11-09", "delay_s": 0,
                       "last_location": back[target], "last_location_type": "A", "origin_time": base + rows[0][3]})
        s2 = src.IrishRailRealtime().parse(trains, t, GEO)
        o2 = next(x for x in s2.observations if x.vehicle_id == o.vehicle_id)
        self.assertEqual([round(o2.lat, 6), round(o2.lon, 6)], GEO["stops"][target])


class Replay(unittest.TestCase):
    """The whole capture through the estimate as drawn (projection.apply): each time a train's fix changes, how far was
    it drawn, one poll before, from the new fix? MEASURED, not assumed: the numbers are printed and bounded."""

    def test_drawn_against_the_next_fix(self):
        rt, proj = src.IrishRailRealtime(), geometry.Projector(GEO)
        last_fix, drawn, errs, counts = {}, {}, [], []
        for t, trains in POLLS:
            for x in trains:
                k = f"{x['code']}-9"
                if x["status"] != "R" or x["lat"] is None:
                    continue
                f = (round(x["lat"], 4), round(x["lon"], 4))
                if k in last_fix and last_fix[k] != f and k in drawn:
                    errs.append(km(drawn[k][0], drawn[k][1], x["lat"], x["lon"]))
                last_fix[k] = f
            s = rt.parse(trains, t, GEO)
            counts.append(len(s.observations))
            vehicles = {}
            for o in s.observations:
                vehicles[o.vehicle_id] = {"latitude": o.lat, "longitude": o.lon, "in_service": True}
            projection.apply(proj, s, {"vehicles": vehicles}, t, False, True, None)
            drawn = {k: (r["latitude"], r["longitude"]) for k, r in vehicles.items()}
        errs.sort()
        p50, p90 = statistics.median(errs), errs[int(0.9 * len(errs))]
        print(f"\nIRISH RAIL REPLAY: {len(POLLS)} polls, trains drawn per poll max {max(counts)}, "
              f"{len(errs)} fix changes, drawn vs next fix p50 {p50:.2f} km p90 {p90:.2f} km max {errs[-1]:.1f} km")
        self.assertGreater(len(errs), 500)
        # MEASURED 2026-11-10 on `EARLY_S`: p50 2.47, p90 8.59, max 17.2 km (holding at the fix: 6.63, 22.56, 111.5).
        # Before EARLY_S the max was 60.3 km (A713, believed 62 minutes early).
        self.assertLess(p50, 3.0)
        self.assertLess(p90, 10.0)
        self.assertLess(errs[-1], 25.0)


if __name__ == "__main__":
    unittest.main()
