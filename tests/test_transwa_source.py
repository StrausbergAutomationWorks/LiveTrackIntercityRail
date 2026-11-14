"""sources/transperth.py and operators/transwa.py on the PTA timetable of 2026-11-13 (Intercity SSOT 8.12): the zip cut
to Transwa with its shapes thinned to every 4th point (tests/fixtures/transwa_20261113.zip; bin\\tw_fixture.py)."""

import datetime as dt
import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _load import load  # noqa: E402

src = load("sources.transperth")
geometry = load("geometry")
projection = load("projection")
ops = load("operators")
FIX = pathlib.Path(__file__).resolve().parent / "fixtures"
RAW = (FIX / "transwa_20261113.zip").read_bytes()
SAT, MON = dt.date(2026, 11, 14), dt.date(2026, 11, 16)
GEO_SAT = src.distill(RAW, "intercity", SAT)
GEO_MON = src.distill(RAW, "intercity", MON)
PERTH = dt.timezone(dt.timedelta(hours=8))


def at(day, h, m=0, s=0):
    return dt.datetime(day.year, day.month, day.day, h, m, s, tzinfo=PERTH).timestamp()


def km(a, b, c, d):
    p = math.pi / 180
    h = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def off_line_km(lat, lon, line):
    """Distance from a point to a polyline, flat-earth per segment (short segments)."""
    best = float("inf")
    kx = math.cos(math.radians(lat)) * 111.32
    for (a, b), (c, d) in zip(line, line[1:]):
        ax, ay, bx, by = (b - lon) * kx, (a - lat) * 110.57, (d - lon) * kx, (c - lat) * 110.57
        dx, dy = bx - ax, by - ay
        t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(ax + t * dx, ay + t * dy))
    return best


def along_km(lat, lon, line):
    """Kilometres along a polyline to its vertex nearest the point."""
    best = min(range(len(line)), key=lambda i: (line[i][0] - lat) ** 2 + (line[i][1] - lon) ** 2)
    return sum(km(*line[i], *line[i + 1]) for i in range(best))


class Rules(unittest.TestCase):
    def test_show(self):
        self.assertEqual(src.show("Perth Stn Transwa Rail Perth"), "Perth")
        self.assertEqual(src.show("East Perth Stn Transwa East Perth"), "East Perth")
        self.assertEqual(src.show("Bonnie Vale Stn Transwa Rail Bonnie Vale"), "Bonnie Vale")
        self.assertEqual(src.show("Somewhere"), "Somewhere")
        self.assertEqual(src.show(" Stn x"), " Stn x".strip())
        # Every name in the timetable has the form (MEASURED 2026-11-14, 33 of 33).
        names = set(GEO_SAT["tw_table"]["stop_names"].values())
        self.assertEqual(len({src.show(n) for n in names}), 31)
        self.assertTrue(all(" Stn " in n for n in names))

    def test_toward_perth(self):
        self.assertTrue(src.toward_perth("Bunbury Stn Transwa Rail Bunbury", "Perth Stn Transwa Rail Perth"))
        self.assertFalse(src.toward_perth("East Perth Stn Transwa East Perth", "Kalgoorlie Stn Transwa Kalgoorlie"))
        self.assertTrue(src.toward_perth("Northam Stn Transwa Northam", "East Perth Stn Transwa East Perth"))
        self.assertIsNone(src.toward_perth("Northam Stn Transwa Northam", "Merredin Stn Transwa Merredin"))
        # Every Transwa trip ends or starts in Perth (MEASURED).
        t = GEO_SAT["tw_table"]
        for tid, calls in t["calls"].items():
            first, last = t["stop_names"][calls[0][0]], t["stop_names"][calls[-1][0]]
            self.assertIsNotNone(src.toward_perth(first, last), tid)

    def test_label_and_hover(self):
        self.assertEqual([src.label(r) for r in ("Australind", "Prospector", "MerredinLink", "AvonLink")],
                         ["AUS", "PRO", "MER", "AVO"])
        self.assertEqual(src.hover("Australind", ["Perth Stn Transwa Rail Perth", "x", "Bunbury Stn Transwa Rail Bunbury"]),
                         "Australind · Perth–Bunbury")
        self.assertEqual(src.hover("Australind", []), "Australind")
        self.assertEqual(src.hover("", ["Perth Stn A", "Bunbury Stn B"]), "Perth–Bunbury")


class Distill(unittest.TestCase):
    def test_transwa_only(self):
        t = GEO_SAT["tw_table"]
        self.assertEqual(set(t["routes"]), {"TRA-TRA-137", "TRA-TRA-145", "TRA-TRA-3527", "TRA-TRA-3528"})
        self.assertEqual(len(t["trips"]), 20)
        self.assertEqual(set(GEO_SAT["trains"]), set(t["trips"]))
        self.assertEqual(set(GEO_SAT["trip_stops"]), set(t["trips"]))
        used = {s for sh in GEO_SAT["trains"].values() for s in sh}
        self.assertEqual(set(GEO_SAT["shapes"]), used)
        self.assertEqual(GEO_SAT["tw_v"], src.GEO_V)

    def test_dates_by_day(self):
        def running(geo, day):
            t = geo["tw_table"]
            return sorted(v[0] for v in t["trips"].values() if day.isoformat() in t["dates"].get(v[1], ()))
        # MEASURED 2026-11-14 (bin\tw_measure.txt): Saturday 4 Australind and 2 Prospector; Monday 12 with MerredinLink
        # and AvonLink.
        self.assertEqual(running(GEO_SAT, SAT), ["TRA-TRA-137"] * 4 + ["TRA-TRA-145"] * 2)
        mon = running(GEO_MON, MON)
        self.assertEqual(len(mon), 12)
        self.assertEqual(mon.count("TRA-TRA-3527"), 2)
        self.assertEqual(mon.count("TRA-TRA-3528"), 2)

    def test_idempotent_on_a_cut_zip(self):
        # The fixture is already cut; the shared client's copy is the whole PTA zip, cut first (transperth.cut).
        self.assertEqual(src.distill(RAW, "intercity", SAT)["tw_table"], GEO_SAT["tw_table"])


class FakeClient:
    def __init__(self, version, path):
        self.version, self.path, self.paths_asked = version, path, 0

    def static_version(self):
        return self.version

    def static_path(self):
        self.paths_asked += 1
        return self.path


class View(unittest.TestCase):
    def test_version_carries_the_perth_date(self):
        v = src.StaticView(FakeClient("Thu, 12 Nov 2026 00:16:38 GMT", None), clock=lambda: at(SAT, 0, 30))
        self.assertEqual(v.static_version(), f"Thu, 12 Nov 2026 00:16:38 GMT|2026-11-14|g{src.GEO_V}")
        # 16:01 UTC on the 13th is already the 14th in Perth (UTC+8).
        v2 = src.StaticView(FakeClient("x", None), clock=lambda: dt.datetime(2026, 11, 13, 16, 1,
                                                                              tzinfo=dt.timezone.utc).timestamp())
        self.assertTrue(v2.static_version().startswith("x|2026-11-14|"))
        self.assertIsNone(src.StaticView(FakeClient(None, None)).static_version())

    def test_read_asks_for_the_path_and_distill_waits_for_a_zip(self):
        c = FakeClient("v1", None)
        v = src.StaticView(c, clock=lambda: at(SAT, 7))
        self.assertTrue(src.read(v).startswith("v1|"))
        self.assertEqual(c.paths_asked, 1)                       # starts the client's daily check when one is due
        self.assertIsNone(v.distill_geometry())

    def test_distill_geometry_from_the_clients_zip(self):
        v = src.StaticView(FakeClient("v1", str(FIX / "transwa_20261113.zip")), clock=lambda: at(SAT, 7))
        self.assertEqual(v.distill_geometry()["tw_table"], GEO_SAT["tw_table"])


class Parse(unittest.TestCase):
    def setUp(self):
        self.tw = src.TranswaTimetable()

    def test_saturday_seven_am(self):
        now = at(SAT, 7)
        s = self.tw.parse(now, GEO_SAT)
        keys = {o.vehicle_id for o in s.observations}
        # Australind 06:00 Bunbury-Perth running; both Prospectors (07:05) standing at their origins.
        self.assertEqual(keys, {"2560586-14", "3279601-14", "3559061-14"})
        by = {o.vehicle_id: o for o in s.observations}
        self.assertEqual(by["2560586-14"].train, "AUS")
        self.assertEqual(by["3279601-14"].train, "PRO")
        self.assertTrue(s.extras["2560586-14"]["toward_hub"])
        self.assertTrue(s.extras["3279601-14"]["toward_hub"])                 # Kalgoorlie to East Perth
        self.assertFalse(s.extras["3559061-14"]["toward_hub"])                # East Perth to Kalgoorlie
        self.assertEqual(s.extras["2560586-14"]["line_name"], "Australind · Bunbury–Perth")
        self.assertEqual(s.extras["3559061-14"]["line_name"], "Prospector · East Perth–Kalgoorlie")
        self.assertFalse(s.trip_delays)                                       # no delay exists
        for k in keys:
            e = s.extras[k]
            self.assertTrue(e["no_fix"])
            self.assertEqual(s.route_keys[k], k.split("-")[0])
            self.assertIn(e["route_code"], GEO_SAT["tw_table"]["routes"])
            self.assertEqual(e["destination"], GEO_SAT["tw_table"]["calls"][k.split("-")[0]][-1][0])

    def test_standing_at_origin_then_timed(self):
        s = self.tw.parse(at(SAT, 7), GEO_SAT)
        k = "3559061-14"
        o = next(o for o in s.observations if o.vehicle_id == k)
        origin = GEO_SAT["tw_table"]["calls"]["3559061"][0][0]
        self.assertEqual([round(o.lat, 6), round(o.lon, 6)], GEO_SAT["stops"][origin])
        self.assertEqual(o.observed_at.timestamp(), at(SAT, 7))               # before it leaves: now
        self.assertIsNone(s.extras[k]["aim_eta"])                             # standing: held (entur.HOLD)
        self.assertEqual(s.extras[k]["held_speed_kmh"], 0.0)
        self.assertEqual(s.next_stops[k][0], "Midland")
        # Running: aimed at the next call's arrival, drawn from the call it left, stamped with its departure.
        k2 = "2560586-14"
        e = s.extras[k2]
        self.assertEqual(e["aim_eta"], s.next_stops[k2][1])
        self.assertIsNone(e["held_speed_kmh"])
        self.assertEqual(e["timed_after_s"], 0.0)
        o2 = next(o for o in s.observations if o.vehicle_id == k2)
        # Stamped with its departure from the call it is drawn at: that call's own time, before now.
        tid_calls = GEO_SAT["tw_table"]["calls"]["2560586"]
        at_call = next(c for c in tid_calls if GEO_SAT["stops"][c[0]] == [round(o2.lat, 6), round(o2.lon, 6)])
        self.assertEqual(o2.observed_at.timestamp(), at(SAT, 0) + at_call[2])
        self.assertLess(o2.observed_at.timestamp(), at(SAT, 7))
        # Aimed at the call after it, by that call's arrival.
        after = tid_calls[tid_calls.index(at_call) + 1]
        self.assertEqual(s.stop_codes[k2], after[0])
        self.assertEqual(s.next_stops[k2][1], at(SAT, 0) + after[1])

    def test_window(self):
        # Australind 2560586 arrives Perth 08:30: kept 2 minutes (FINISHED_S 120), then gone.
        s = self.tw.parse(at(SAT, 8, 31), GEO_SAT)
        self.assertIn("2560586-14", {o.vehicle_id for o in s.observations})
        self.assertNotIn("2560586-14", s.next_stops)
        s = self.tw.parse(at(SAT, 8, 32, 30), GEO_SAT)
        self.assertNotIn("2560586-14", {o.vehicle_id for o in s.observations})
        # From 5 minutes before the first departure (06:00), not before.
        self.assertIn("2560586-14", {o.vehicle_id for o in self.tw.parse(at(SAT, 5, 55), GEO_SAT).observations})
        self.assertNotIn("2560586-14", {o.vehicle_id for o in self.tw.parse(at(SAT, 5, 54), GEO_SAT).observations})

    def test_quiet_night_and_no_timetable(self):
        s = self.tw.parse(at(SAT, 23), GEO_SAT)
        self.assertEqual(s.observations, [])
        self.assertNotIn("no_timetable", s.skipped)
        s = self.tw.parse(at(SAT, 7), None)
        self.assertEqual(s.observations, [])
        self.assertEqual(s.skipped, {"no_timetable": 1})

    def test_a_dwell_aims_at_the_arrival_and_stands_through_it(self):
        # Transwa's timetable has no dwell (arrival = departure at every call, MEASURED), so a synthetic one: the
        # timed rule aims at the next call's ARRIVAL, and a train stands at a call from its arrival to its departure,
        # stamped with the arrival.
        base = at(SAT, 0)
        geo = {"stops": {"A": [-31.95, 115.86], "B": [-32.0, 115.9], "C": [-32.1, 116.0]},
               "tw_table": {"stop_names": {"A": "Perth Stn X", "B": "Mid Stn Y", "C": "End Stn Z"},
                            "routes": {"R": ["Australind", "#CF4520"]},
                            "trips": {"T": ["R", "S", 36000, 43200, "", "1"]},
                            "calls": {"T": [["A", None, 36000], ["B", 39600, 40200], ["C", 43200, None]]},
                            "dates": {"S": [SAT.isoformat()]}}}
        s = self.tw.parse(base + 37800, geo)
        self.assertEqual(s.extras["T-14"]["aim_eta"], base + 39600)
        self.assertEqual(s.next_stops["T-14"], ("Mid", base + 39600))
        self.assertFalse(s.extras["T-14"]["toward_hub"])
        s = self.tw.parse(base + 39900, geo)
        o = s.observations[0]
        self.assertEqual([o.lat, o.lon], [-32.0, 115.9])
        self.assertEqual(o.observed_at.timestamp(), base + 39600)
        self.assertIsNone(s.extras["T-14"]["aim_eta"])
        # A call with no position: the run is skipped and said so, nothing raises.
        del geo["stops"]["B"]
        s = self.tw.parse(base + 39900, geo)
        self.assertEqual((s.observations, s.skipped), ([], {"no_stop_position": 1}))

    def test_monday_merredin_and_avon(self):
        s = self.tw.parse(at(MON, 9), GEO_MON)
        labels = {o.train for o in s.observations}
        self.assertIn("MER", labels)
        s = self.tw.parse(at(MON, 7), GEO_MON)
        self.assertIn("AVO", {o.train for o in s.observations})


class Operator(unittest.TestCase):
    def test_registered(self):
        op = ops.OPERATORS["wa_trains"]
        self.assertNotIn("transwa", ops.OPERATORS)
        self.assertEqual((op.name, op.short), ("WA Trains", "WA Trains"))     # Lee 2026-11-14 01:13 CST
        self.assertEqual(op.source, ops.SOURCE_TRANSPERTH)
        self.assertIn(ops.SOURCE_TRANSPERTH, ops.SOURCES)
        self.assertEqual(op.regions, ("AU",))
        self.assertEqual(op.source_options, {"consumer": "intercity"})
        self.assertEqual(op.lateness_keys(), {})                              # no delay, no thresholds
        self.assertTrue(op.timed_without_fix)
        self.assertTrue(op.gtfs_from_source)
        self.assertFalse(op.needs_key)
        from saw_livetrack.transperth import ATTRIBUTION, TERMS_URL
        self.assertEqual((op.attribution, op.terms_url), (ATTRIBUTION, TERMS_URL))
        self.assertIn(op, ops.operators_in("AU"))

    def test_look_per_route(self):
        # Lee 2026-11-14 01:13 CST, colours measured from his image: fill, label; ring and arrow outline the label's.
        op = ops.OPERATORS["wa_trains"]
        want = {"Australind": ("#614B79", "#FFFFFF"), "Prospector": ("#F2A900", "#000000"),
                "MerredinLink": ("#8F993E", "#FFFFFF"), "AvonLink": ("#8F993E", "#000000")}
        for route, (fill, text) in want.items():
            for toward in (True, False):                                      # the same both ways
                k = op.marker_keys({"service_family": route, "toward_hub": toward})
                self.assertEqual((k["marker_color"], k["marker_label_color"], k["marker_ring_color"],
                                  k["marker_label_outline_color"], k["marker_arrow_color"],
                                  k["marker_arrow_outline_color"], k["marker_ring_width"]),
                                 (fill, text, text, fill, fill, text, 3), route)
        # A route not in the table: its timetable colour, else Transwa's, label white.
        k = op.marker_keys({"service_family": "NewLink", "route_color": "#123456"})
        self.assertEqual((k["marker_color"], k["marker_label_color"]), ("#123456", "#FFFFFF"))
        self.assertEqual(op.marker_keys({})["marker_color"], "#CF4520")
        self.assertEqual(op.marker_keys({"route_color": "nonsense"})["marker_color"], "#CF4520")

    def test_every_drawn_train_gets_its_routes_look(self):
        s = src.TranswaTimetable().parse(at(MON, 9), GEO_MON)
        op = ops.OPERATORS["wa_trains"]
        fills = {"AUS": "#614B79", "PRO": "#F2A900", "MER": "#8F993E", "AVO": "#8F993E"}
        self.assertTrue(s.observations)
        for o in s.observations:
            e = s.extras[o.vehicle_id]
            self.assertEqual(e["route_color"], "#CF4520")                     # the timetable's, MEASURED
            self.assertEqual(op.marker_keys(e)["marker_color"], fills[o.train], o.vehicle_id)


class Replay(unittest.TestCase):
    """Saturday and Monday through the estimate as drawn (projection.apply), every 30 s: each train ON its own trip's
    shape and never drawn backwards along it. MEASURED, printed and bounded."""

    def run_day(self, geo, day):
        tw, proj = src.TranswaTimetable(), geometry.Projector(geo)
        worst, back, polls, seen, prev, reach = 0.0, 0, 0, set(), {}, {}
        t = at(day, 5)
        while t <= at(day, 23):
            s = tw.parse(t, geo)
            vehicles = {o.vehicle_id: {"latitude": o.lat, "longitude": o.lon, "in_service": True}
                        for o in s.observations}
            projection.apply(proj, s, {"vehicles": vehicles}, t, False, True, None)
            for k, r in vehicles.items():
                tid = s.route_keys[k]
                line = [p for sh in geo["trains"][tid] for p in geo["shapes"][sh]]
                worst = max(worst, off_line_km(r["latitude"], r["longitude"], line))
                # Along its line, not from its origin as the crow flies: the AvonLink's line curves through the Avon
                # Valley, where a train moving on draws nearer Northam (bin\tw_back.txt, 2026-11-14).
                d = along_km(r["latitude"], r["longitude"], line)
                if k in prev and d < prev[k] - 0.5:
                    back += 1
                prev[k] = d
                reach[k] = max(reach.get(k, 0.0), d / along_km(*line[-1], line))
                seen.add(k)
            polls += 1
            t += 30
        return worst, back, polls, seen, min(reach.values())

    def test_saturday_and_monday(self):
        for geo, day, n in ((GEO_SAT, SAT, 6), (GEO_MON, MON, 12)):
            worst, back, polls, seen, reach = self.run_day(geo, day)
            print(f"\nTRANSWA REPLAY {day}: {polls} polls, {len(seen)} runs, worst off its line {worst * 1000:.0f} m, "
                  f"moves back along its line over 0.5 km: {back}, least share of its line reached {reach:.3f}")
            self.assertEqual(len(seen), n)
            self.assertLess(worst, 0.3)
            self.assertEqual(back, 0)
            self.assertGreater(reach, 0.99)                                   # every run drawn to its terminus


if __name__ == "__main__":
    unittest.main()
