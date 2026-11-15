"""sources/qrt.py and operators/qrt.py (Intercity SSOT 8.14): Queensland Rail Travel from its Service Updates page,
times only. The shipped lines are read as installed. QRT's answers are NOT in this repository (05_SHARED_LESSONS_DATA.md
B18 condition 5): every answer below is made up here, in QRT's shape, on the shipped stop patterns."""

import datetime as dt
import json
import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _load import load  # noqa: E402

src = load("sources.qrt")
base = load("sources.base")
geometry = load("geometry")
projection = load("projection")
ops = load("operators")
pictures = load("pictures")
LOADED = src.load()
DATA = LOADED["data"]
GEO = src.distill(LOADED)
BNE = dt.timezone(dt.timedelta(hours=10))
SENT = "0001-01-01T00:00:00"


def bne(y, mo, d, h, mi=0):
    return dt.datetime(y, mo, d, h, mi, tzinfo=BNE).timestamp()


def iso(t):
    return SENT if t is None else dt.datetime.fromtimestamp(t, BNE).strftime("%Y-%m-%dT%H:%M:%S")


def body(pid, way, start, kmh=60.0, dwell=300.0, actual_shift=None):
    """A made-up GetService answer on the shipped pattern: run at `kmh`, stand `dwell` at each call; `actual_shift`
    (s) fills Actual* from the third call on, as QRT does for a train not on time."""
    calls = DATA["patterns"][pid][way]["calls"]
    t, mv, last_m = start, [], 0
    for i, (code, m) in enumerate(calls):
        t += (m - last_m) / (kmh / 3.6)
        last_m = m
        arr = None if i == 0 else t
        dep = None if i == len(calls) - 1 else (start if i == 0 else t + dwell)
        if i:
            t += dwell
        a_arr = a_dep = None
        if actual_shift is not None and i >= 2:
            a_arr = None if arr is None else arr + actual_shift
            a_dep = None if dep is None else dep + actual_shift
        mv.append({"PlaceCode": code, "PlaceName": DATA["stations"][code][0], "KStation": False, "Status": "On time",
                   "TrainPosition": "NotArrived", "PlannedArrival": iso(arr), "PlannedDeparture": iso(dep),
                   "ActualArrival": iso(a_arr), "ActualDeparture": iso(a_dep)})
    return {"ServiceId": "x", "ServiceDisruption": None, "TrainMovements": mv, "Modified": SENT, "Success": True}


def item(line, sid, sdate, b):
    return {"service": {"ServiceId": sid, "ServiceDate": f"{sdate}T00:00:00",
                        "DepartureDate": b["TrainMovements"][0]["PlannedDeparture"]},
            "line": line, "direction": "x", "body": b}


class Data(unittest.TestCase):
    def test_version_licence_and_no_times(self):
        self.assertEqual(DATA["v"], src.DATA_VERSION)
        self.assertIn("ODbL", DATA["meta"]["licence"])
        raw = json.dumps(DATA)
        self.assertNotIn("Planned", raw)                     # SAW's own material only (B18 5)
        self.assertNotIn("2026-", json.dumps(DATA["patterns"]) + json.dumps(DATA["stations"]))

    def test_every_call_is_paired(self):
        for pid, p in DATA["patterns"].items():
            for way in ("out", "back"):
                for code, _ in p[way]["calls"]:
                    self.assertIn(code, DATA["stations"], (pid, code))
        self.assertEqual(len(DATA["stations"]), 72)

    def test_lengths_and_sections(self):
        lines = DATA["lines"]
        km = {pid: sum(v[0] for k, v in lines.items() if k.startswith(pid + "_out#")) / 1000 for pid in DATA["patterns"]}
        # Queensland Rail publishes about 1,681 km Brisbane-Cairns and 977 km Townsville-Mount Isa.
        self.assertAlmostEqual(km["soq"], 1681, delta=60)
        self.assertAlmostEqual(km["inlander"], 977, delta=30)
        cuts = {pid: [p["out"]["calls"][s][0] for s in p["out"]["sections"][1:]] for pid, p in DATA["patterns"].items()}
        self.assertEqual({k: v for k, v in cuts.items() if v}, {"sob": ["ROK"], "westlander": ["TWP"]})
        for pid, p in DATA["patterns"].items():
            back_cuts = [p["back"]["calls"][s][0] for s in p["back"]["sections"][1:]]
            self.assertEqual(back_cuts, cuts[pid][::-1], pid)
            for way in ("out", "back"):
                ms = [m for _, m in p[way]["calls"]]
                self.assertEqual(ms, sorted(ms), (pid, way))

    def test_stops_are_lat_lon(self):
        name, la, lo = DATA["stations"]["RST"]
        self.assertEqual(GEO["stops"]["RST"], [la, lo])
        self.assertLess(la, -27.0)                            # Brisbane: south of -27, east of 153
        self.assertGreater(lo, 153.0)

    def test_a_file_of_another_version_is_refused(self):
        import gzip, tempfile, os
        d = dict(DATA, v=src.DATA_VERSION + 1)
        with tempfile.NamedTemporaryFile(suffix=".json.gz", delete=False) as fh:
            fh.write(gzip.compress(json.dumps(d).encode()))
        try:
            with self.assertRaises(ValueError):
                src.load(fh.name)
        finally:
            os.unlink(fh.name)

    def test_back_line_is_the_out_line_reversed(self):
        a, b = GEO["shapes"]["sob_out#0"], GEO["shapes"]["sob_back#1"]
        self.assertEqual(a[::-1], b)


class Rules(unittest.TestCase):
    def test_train_number(self):
        self.assertEqual(src.train_number("980T", "V"), "V980")
        self.assertEqual(src.train_number("W57T", "P"), "PW57")
        self.assertEqual(src.train_number("J11T", "Q"), "QJ11")
        self.assertEqual(src.train_number("K30T", "3"), "3K30")

    def test_times_are_brisbane_wall_clock(self):
        self.assertIsNone(src.t_epoch(SENT))
        self.assertIsNone(src.t_epoch(None))
        self.assertEqual(src.t_epoch("2026-11-15T07:40:00"), bne(2026, 11, 15, 7, 40))
        self.assertEqual(src.t_epoch("2026-11-15T11:38:22.8629005"), bne(2026, 11, 15, 11, 38) + 22)

    def test_section_of(self):
        self.assertEqual([src.section_of([0, 10], i) for i in (0, 9, 10, 20)], [0, 0, 1, 1])
        self.assertEqual(src.pattern_of("tilt_rok_back#0"), "tilt_rok")


class Parse(unittest.TestCase):
    def setUp(self):
        self.start = bne(2026, 11, 14, 15, 45)
        self.soq = body("soq", "out", self.start)

    def test_running_aims_at_the_next_call(self):
        s = src.QrtService().parse([item("Spirit of Queensland", "C81T", "2026-11-14", self.soq)], self.start + 3600, GEO)
        self.assertEqual([o.vehicle_id for o in s.observations], ["VC81-14"])
        k = "VC81-14"
        self.assertEqual(s.route_keys[k], "soq_out#0")
        self.assertEqual(s.extras[k]["service_family"], "soq")
        self.assertEqual(s.extras[k]["service_direction"], "out")
        self.assertTrue(s.extras[k][base.NO_FIX_KEY])
        self.assertIn(s.stop_codes[k], DATA["stations"])
        name, eta = s.next_stops[k]
        self.assertGreater(eta, self.start + 3600)
        self.assertEqual(name, DATA["stations"][s.stop_codes[k]][0])
        self.assertEqual(s.extras[k][base.AIM_ETA_KEY], eta)      # aimed at the next call's ARRIVAL
        nxt = [m for m in self.soq["TrainMovements"] if m["PlaceCode"] == s.stop_codes[k]][0]
        self.assertEqual(eta, src.t_epoch(nxt["PlannedArrival"]))
        self.assertEqual(s.extras[k]["line_name"], "Spirit of Queensland VC81 · Brisbane - Roma Street–Cairns")

    def test_actual_wins_over_planned(self):
        late = body("soq", "out", self.start, actual_shift=1800.0)
        t = self.start + 6 * 3600
        on = src.QrtService().parse([item("Spirit of Queensland", "C81T", "2026-11-14", self.soq)], t, GEO)
        lt = src.QrtService().parse([item("Spirit of Queensland", "C81T", "2026-11-14", late)], t, GEO)
        self.assertGreater(lt.next_stops["VC81-14"][1], on.next_stops["VC81-14"][1])

    def test_an_arrival_forecast_on_its_own_is_believed(self):
        # QRT fills each Actual cell on its own (the note 2.1): a call ahead with only ActualArrival.
        t = self.start + 3600
        s0 = src.QrtService().parse([item("Spirit of Queensland", "C81T", "2026-11-14", self.soq)], t, GEO)
        code = s0.stop_codes["VC81-14"]
        b = json.loads(json.dumps(self.soq))
        m = [x for x in b["TrainMovements"] if x["PlaceCode"] == code][0]
        late = src.t_epoch(m["PlannedArrival"]) + 1200
        m["ActualArrival"] = iso(late)
        s = src.QrtService().parse([item("Spirit of Queensland", "C81T", "2026-11-14", b)], t, GEO)
        self.assertEqual(s.next_stops["VC81-14"][1], late)

    def test_too_few_known_calls(self):
        b = json.loads(json.dumps(self.soq))
        b["TrainMovements"] = b["TrainMovements"][:1]
        s = src.QrtService().parse([item("Spirit of Queensland", "C81T", "2026-11-14", b)], self.start, GEO)
        self.assertEqual(s.skipped, {"too_few_known_calls": 1})

    def test_back_direction_and_section_after_the_reversal(self):
        b = body("sob", "back", bne(2026, 11, 16, 10))
        calls = DATA["patterns"]["sob"]["back"]["calls"]
        rok = [c for c, _ in calls].index("ROK")
        t = src.t_epoch(b["TrainMovements"][rok + 1]["PlannedArrival"]) - 600     # past Rockhampton, toward Mount Larcom
        s = src.QrtService().parse([item("Spirit of the Outback", "986T", "2026-11-16", b)], t, GEO)
        k = "P986-16"
        self.assertEqual(s.extras[k]["service_direction"], "back")
        self.assertEqual(s.route_keys[k], "sob_back#1")

    def test_not_out_unknown_line_and_no_lines(self):
        s = src.QrtService().parse([item("Spirit of Queensland", "C81T", "2026-11-14", self.soq)], self.start - 3600, GEO)
        self.assertEqual(s.observations, [])
        s = src.QrtService().parse([item("Sunlander", "X1T", "2026-11-14", self.soq)], self.start + 60, GEO)
        self.assertEqual(s.skipped, {"unknown_line": 1})
        s = src.QrtService().parse([], self.start, {})
        self.assertEqual(s.skipped, {"no_lines": 1})


class Client(unittest.TestCase):
    """The B18 conditions as built: cached, paced, only trains out or near, backoff, fails closed."""

    def setUp(self):
        self.t = bne(2026, 11, 15, 11, 15)
        self.calls, self.fail = [], False
        self.sleeps = []
        self.near = body("soq", "back", self.t - 3600)
        self.far = body("tilt_rok", "out", self.t + 6 * 3600)
        self.all = {"Success": True, "ServiceLines": [
            {"ServiceLineName": "Spirit of Queensland", "Directions": [{"DirectionName": "Southbound", "Services": [
                {"ServiceId": "980T", "ServiceDate": "2026-11-15T00:00:00", "DepartureDate": iso(self.t - 3600)}]}]},
            {"ServiceLineName": "Rockhampton Tilt Train", "Directions": [{"DirectionName": "Northbound", "Services": [
                {"ServiceId": "311T", "ServiceDate": "2026-11-15T00:00:00", "DepartureDate": iso(self.t + 6 * 3600)}]}]}]}

        def opener(url):
            self.calls.append(url)
            if self.fail:
                raise OSError("down")
            if "AllServices" in url:
                return json.dumps(self.all).encode()
            return json.dumps(self.near if "980T" in url else self.far).encode()
        self.c = src.QrtClient("UA", opener=opener, clock=lambda: self.t, sleep=self.sleeps.append)

    def test_reads_the_list_and_only_the_near_train(self):
        out = self.c.poll()
        self.assertEqual(len(self.calls), 2)
        self.assertIn("serviceId=980T", self.calls[1])
        self.assertIn("serivceDate=2026-11-15T00%3A00%3A00.000Z", self.calls[1])     # their spelling, as the page sends
        self.assertEqual([o["service"]["ServiceId"] for o in out], ["980T"])
        self.assertEqual(self.sleeps, [src.ADDED_GAP_S])

    def test_cached_within_the_ttl(self):
        self.c.poll()
        self.t += 120
        self.c.poll()
        self.assertEqual(len(self.calls), 2)
        self.t += src.ALL_TTL_S
        self.c.poll()
        self.assertEqual(len(self.calls), 4)

    def test_backoff_then_fails_closed(self):
        self.c.poll()
        self.fail = True
        self.t += src.ALL_TTL_S
        self.assertEqual(len(self.c.poll()), 1)              # the last good answer, still within STALE_S
        n = len(self.calls)
        self.t += src.BACKOFF_S / 2
        self.c.poll()
        self.assertEqual(len(self.calls), n)                 # backing off: no request
        self.t += src.STALE_S
        with self.assertRaises(src.QrtUnavailable):
            self.c.poll()

    def test_a_finished_train_is_not_read_again(self):
        self.near = body("kuranda", "out", self.t - 4 * 3600)
        self.c.poll()
        n = len(self.calls)
        self.t += src.SVC_TTL_S + 1
        self.c.poll()
        self.assertEqual(len(self.calls) - n, 1)             # the list only

    def test_a_train_gone_from_the_list_is_dropped(self):
        self.c.poll()
        self.all["ServiceLines"][0]["Directions"][0]["Services"] = []
        self.t += src.ALL_TTL_S
        self.assertEqual(self.c.poll(), [])
        self.assertEqual(self.c._svc, {})                     # not kept, so not read again


class Operator(unittest.TestCase):
    def test_registered(self):
        op = ops.OPERATORS["queensland_rail_travel"]
        self.assertEqual((op.name, op.short, op.regions), ("Queensland Rail Travel", "QRT", ("AU",)))
        self.assertEqual(op.source, ops.SOURCE_QRT)
        self.assertIn(ops.SOURCE_QRT, ops.SOURCES)
        self.assertEqual(op.lateness_keys(), {})
        self.assertTrue(op.timed_without_fix and op.gtfs_from_source)
        self.assertFalse(op.needs_key)
        self.assertEqual(op.attribution, "Service updates: Queensland Rail Travel (queenslandrailtravel.com.au)")
        self.assertIn(op, ops.operators_in("AU"))

    def test_every_pattern_has_both_pictures_and_a_tag(self):
        op = ops.OPERATORS["queensland_rail_travel"]
        for p in DATA["patterns"].values():
            for way in ("out", "back"):
                k = op.marker_keys({"service_family": p["picture"], "service_direction": way, "train": "V980"})
                self.assertEqual(k["entity_picture"], pictures.url(f"qrt_{p['picture']}_{way}"))
                self.assertTrue(pictures.path(f"qrt_{p['picture']}_{way}").is_file())
                self.assertEqual((k["marker_label"], k["marker_label_placement"]), ("V980", "heading"))
        self.assertEqual(op.marker_keys({"service_family": "other"}), {})

    def test_the_picture_through_the_record(self):
        op = ops.OPERATORS["queensland_rail_travel"]
        b = body("soq", "back", bne(2026, 11, 15, 7, 40))
        s = src.QrtService().parse([item("Spirit of Queensland", "980T", "2026-11-15", b)], bne(2026, 11, 15, 9), GEO)
        rec = {"train": s.observations[0].train,
               **{k: v for k, v in s.extras["V980-15"].items() if k in base.EXTRA_KEYS}}
        self.assertEqual(op.marker_keys(rec)["entity_picture"], pictures.url("qrt_soq_back"))


class Replay(unittest.TestCase):
    """Every line both ways, made-up times, every 120 s through projection.apply: ON its own line, never backwards,
    to its terminus."""

    def test_every_line_both_ways(self):
        p, proj = src.QrtService(), geometry.Projector(GEO)
        lines = {v["line"]: pid for pid, v in DATA["patterns"].items()}
        items, start = [], bne(2026, 11, 16, 6)
        for n, (line, pid) in enumerate(lines.items()):
            for way in ("out", "back"):
                items.append(item(line, f"{n}{way[0]}T", "2026-11-16", body(pid, way, start, kmh=90, dwell=120)))
        worst, back, prev, sec, reach = 0.0, 0, {}, {}, {}
        t = start - 600
        while t < start + 30 * 3600:
            s = p.parse(items, t, GEO)
            veh = {o.vehicle_id: {"latitude": o.lat, "longitude": o.lon, "in_service": True} for o in s.observations}
            projection.apply(proj, s, {"vehicles": veh}, t, False, True, None)
            for k, r in veh.items():
                line = GEO["shapes"][s.route_keys[k]]
                off, along = _nearest(r["latitude"], r["longitude"], line)
                worst = max(worst, off)
                if sec.get(k) != s.route_keys[k]:
                    sec[k] = s.route_keys[k]
                    prev.pop(k, None)
                if k in prev and along < prev[k] - 0.5:
                    back += 1
                prev[k] = along
                reach[k] = (s.route_keys[k], along / max(1e-9, _nearest(*line[-1], line)[1]))
            t += 120
        print(f"\nQRT REPLAY: {len(reach)} runs, worst off its line {worst * 1000:.0f} m, moves back {back}")
        self.assertEqual(len(reach), 2 * len(lines))
        self.assertLess(worst, 0.3)
        self.assertEqual(back, 0)
        self.assertTrue(all(v > 0.99 for _, v in reach.values()), reach)


def _nearest(lat, lon, line):
    def km(a, b, c, d):
        q = math.pi / 180
        h = math.sin((c - a) * q / 2) ** 2 + math.cos(a * q) * math.cos(c * q) * math.sin((d - b) * q / 2) ** 2
        return 12742 * math.asin(math.sqrt(h))
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


if __name__ == "__main__":
    unittest.main()
