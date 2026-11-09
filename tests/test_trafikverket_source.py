"""Sweden on Trafikverket (Intercity SSOT 8.9, backlog 327): the source adapter, its lines, the fifteen operators'
look and lateness, the coordinator's branch, the key form, and the route store taking a geometry whose trips come
with the runs. Offline. Run from the repo root: python -m unittest tests.test_trafikverket_source
"""

import asyncio
import gzip
import hashlib
import json
import pathlib
import shutil
import sys
import tempfile
import time
import types
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _ha_stub  # noqa: E402
_ha_stub.install()
from _load import load  # noqa: E402

from saw_livetrack import trafikverket as lib  # noqa: E402

src = load("sources.trafikverket")
lines_mod = load("sources.sweden_lines")
base = load("sources.base")
operators = load("operators")
sweden = load("operators.sweden")
coordinator = load("coordinator")
const = load("const")
flow = load("config_flow")
route_store = load("route_store")
geometry = load("geometry")
projection = load("projection")

run = asyncio.run
NOW = 1794200000.0
HERE = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_intercity_rail"
STATIONS = {"Cst": {"name": "Stockholm C", "lat": 59.3303, "lon": 18.0582},
            "Söc": {"name": "Södertälje Syd", "lat": 59.1627, "lon": 17.6461},
            "G": {"name": "Göteborg C", "lat": 57.7089, "lon": 11.9733},
            "Hie": {"name": "Hyllie", "lat": 55.5636, "lon": 12.9757},
            "Kac": {"name": "Kalmar C", "lat": 56.6616, "lon": 16.3635},
            "Str": {"name": "Storlien", "lat": 63.3175, "lon": 12.1009}}
ENDS = {"Cst": {"population": 1652895}, "G": {"population": 674529}, "Hie": {"population": 339316},
        "Kac": {"population": 42622}, "Söc": {"population": 1652895}, "Str": {"population": None}}


def call(sig, act, t, est=None, actual=None, public=True, canceled=False):
    return {"id": sig + act, "sig": sig, "activity": act, "advertised": t, "estimated": est, "actual": actual,
            "public": public, "canceled": canceled}


def run_(number="525", calls=None, ts=NOW - 20, speed=150.0, product="SJ Snabbtåg", lat=59.2, lon=17.8,
         date="2026-11-09"):
    if calls is None:
        calls = [call("Cst", "Avgang", NOW - 900, actual=NOW - 870),
                 call("Söc", "Ankomst", NOW + 300, est=NOW + 420),
                 call("Söc", "Avgang", NOW + 360, est=NOW + 480),
                 call("G", "Ankomst", NOW + 10000)]
    return {"key": f"{number}|{date}", "number": number, "date": date, "brand": "sj", "product": product,
            "operator": "SJ", "position": {"lat": lat, "lon": lon, "speed": speed, "bearing": 240.0, "ts": ts},
            "calls": calls}


def geo(lines=None):
    return {"stops": {s: [v["lat"], v["lon"]] for s, v in STATIONS.items()},
            "stop_names": {s: v["name"] for s, v in STATIONS.items()},
            "pair_lines": lines if lines is not None else {"Cst|Söc": [5933030, 1805820, -16760, -41210]},
            "trains": {}, "shape_legs": {}, "live_trains": True}


class Rules(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(src.identity("525", "2026-11-09"), "525-9")
        self.assertEqual(src.identity("525", "2026-11-30"), "525-30")
        self.assertEqual(src.identity("525", None), "525")
        self.assertEqual(src.identity("525", "2026-11-x"), "525")

    def test_hub(self):
        self.assertEqual(src.hub_index(["G", "Cst", "Söc", "Cst", "Kac"], ENDS), 3)    # the LAST Stockholm C
        self.assertEqual(src.hub_index(["Kac", "Hie"], ENDS), 1)
        self.assertEqual(src.hub_index(["Hie", "Kac"], ENDS), 0)
        self.assertEqual(src.hub_index(["Str", "Kac"], ENDS), 1)                       # one end in no tätort
        self.assertEqual(src.hub_index(["Kac", "Str"], ENDS), 0)
        self.assertIsNone(src.hub_index(["Str", "Str"], ENDS))
        self.assertIsNone(src.hub_index(["Hie", "Hie"], ENDS))                          # one tätort both ends
        self.assertIsNone(src.hub_index([], ENDS))
        self.assertIsNone(src.hub_index(["X", "Y"], {"X": {"population": True}, "Y": {}}))

    def test_stations_in_order(self):
        calls = [call("A", "Avgang", 1), call("B", "Ankomst", 2, public=False), call("C", "Ankomst", 3, canceled=True),
                 call("D", "Ankomst", 4), call("D", "Avgang", 5), call("", "Ankomst", 6)]
        self.assertEqual(src.stations_in_order(calls), ["A", "D"])

    def test_next_stop_and_delay(self):
        calls = run_()["calls"]
        delay, nxt, eta = src.delay_and_next(calls, NOW)
        self.assertEqual((delay, nxt["sig"], eta), (120, "Söc", NOW + 420))
        # No estimate: advertised plus the last actual's delay.
        calls = [call("Cst", "Avgang", NOW - 900, actual=NOW - 840), call("Söc", "Ankomst", NOW + 300)]
        self.assertEqual(src.delay_and_next(calls, NOW)[::2], (60, NOW + 360))
        # A stop with an actual is behind the train, and so is everything before it.
        calls = [call("Cst", "Avgang", NOW - 900, actual=NOW - 900), call("Söc", "Ankomst", NOW - 100, actual=NOW - 50),
                 call("G", "Ankomst", NOW + 9000)]
        self.assertEqual(src.delay_and_next(calls, NOW)[1]["sig"], "G")
        # Never the origin, never a departure, a hidden or a cancelled call.
        calls = [call("Cst", "Ankomst", NOW + 10), call("Cst", "Avgang", NOW + 20), call("Söc", "Ankomst", NOW + 30,
                 public=False), call("G", "Ankomst", NOW + 40, canceled=True), call("Kac", "Ankomst", NOW + 50)]
        self.assertEqual(src.delay_and_next(calls, NOW)[1]["sig"], "Kac")
        # A time more than the grace past, with no actual: passed.
        calls = [call("Cst", "Avgang", NOW - 900), call("Söc", "Ankomst", NOW - src.NEXT_GRACE_S - 1),
                 call("G", "Ankomst", NOW + 9000)]
        self.assertEqual(src.delay_and_next(calls, NOW)[1]["sig"], "G")
        calls[1]["advertised"] = NOW - src.NEXT_GRACE_S
        self.assertEqual(src.delay_and_next(calls, NOW)[1]["sig"], "Söc")
        # A call before the last actual is behind the train though it has none of its own.
        calls = [call("Cst", "Avgang", NOW - 900, actual=NOW - 900), call("Söc", "Ankomst", NOW - 30),
                 call("Flb", "Ankomst", NOW - 20, actual=NOW - 10), call("G", "Ankomst", NOW + 600)]
        self.assertEqual(src.delay_and_next(calls, NOW)[1]["sig"], "G")
        # A departure row alone is no next stop.
        calls = [call("Cst", "Avgang", NOW - 900), call("Söc", "Avgang", NOW + 30), call("G", "Ankomst", NOW + 600)]
        self.assertEqual(src.delay_and_next(calls, NOW)[1]["sig"], "G")
        # Nothing ahead.
        self.assertEqual(src.delay_and_next([call("Cst", "Avgang", NOW - 9)], NOW), (None, None, None))
        self.assertEqual(src.delay_and_next([], NOW), (None, None, None))
        # An actual with no advertised time says nothing.
        calls = [call("Cst", "Avgang", None, actual=NOW), call("Söc", "Ankomst", NOW + 300)]
        self.assertEqual(src.delay_and_next(calls, NOW)[0], None)
        # An arrival with no advertised time is no next stop.
        calls = [call("Cst", "Avgang", NOW - 9), call("Söc", "Ankomst", None), call("G", "Ankomst", NOW + 5)]
        self.assertEqual(src.delay_and_next(calls, NOW)[1]["sig"], "G")
        # An early estimate is a negative delay.
        calls = [call("Cst", "Avgang", NOW - 9), call("Söc", "Ankomst", NOW + 300, est=NOW + 240)]
        self.assertEqual(src.delay_and_next(calls, NOW)[0], -60)

    def test_terminal_time(self):
        self.assertEqual(src.terminal_time([call("A", "Avgang", 1), call("G", "Ankomst", 100, actual=130)], 5), 130)
        self.assertEqual(src.terminal_time([call("G", "Ankomst", 100, est=120)], 5), 120)
        self.assertEqual(src.terminal_time([call("G", "Ankomst", 100)], 5), 105)
        self.assertEqual(src.terminal_time([call("G", "Ankomst", 100)], None), 100)
        self.assertEqual(src.terminal_time([call("A", "Ankomst", 50), call("G", "Ankomst", 100, canceled=True)], 0), 50)
        self.assertIsNone(src.terminal_time([call("G", "Ankomst", None)], 0))
        self.assertIsNone(src.terminal_time([], 0))


class Parse(unittest.TestCase):
    def rt(self):
        return src.TrafikverketRealtime(ends=ENDS)

    def test_none_and_empty(self):
        self.assertIsNone(self.rt().parse(None, STATIONS, NOW, geo()))
        self.assertEqual(self.rt().parse([], STATIONS, NOW, geo()).observations, [])

    def test_one_train(self):
        g = geo()
        snap = self.rt().parse([run_()], STATIONS, NOW, g)
        (o,) = snap.observations
        self.assertEqual((o.vehicle_id, o.train, o.lat, o.lon, o.reported_course, o.trip_id, o.in_service),
                         ("525-9", "525", 59.2, 17.8, 240.0, "525-9", True))
        self.assertEqual(o.observed_at.timestamp(), NOW - 20)
        ex = snap.extras["525-9"]
        self.assertEqual(ex["line_name"], "SJ Snabbtåg 525 · Stockholm C–Göteborg C")
        self.assertEqual(ex["speed_kmh"], 150.0)
        self.assertIs(ex["toward_hub"], False)                 # Stockholm C behind it
        self.assertEqual(snap.next_stops["525-9"], ("Södertälje Syd", NOW + 420))
        self.assertEqual(snap.stop_codes["525-9"], "Söc")
        self.assertEqual(snap.trip_delays["525-9"], 120)
        sid = snap.route_keys["525-9"]
        self.assertEqual(g["trains"][sid], [sid])
        self.assertEqual(g["shape_legs"][sid], [["Cst", "Söc", "Cst|Söc"], ["Söc", "G", None]])
        self.assertEqual(sid, lines_mod.pattern_id(g["shape_legs"][sid]))
        for k in snap.extras["525-9"]:
            self.assertIn(k, base.EXTRA_KEYS)

    def test_no_speed_and_product_names(self):
        snap = self.rt().parse([run_(speed=None, product="VTAB")], STATIONS, NOW, geo())
        self.assertNotIn("speed_kmh", snap.extras["525-9"])
        self.assertTrue(snap.extras["525-9"]["line_name"].startswith("Värmlandstrafik 525 · "))
        for code, name in (("TiB", "Tåg i Bergslagen"), ("Östgötapendel", "Östgötapendeln"), ("Mälartåg", "Mälartåg")):
            ln = self.rt().parse([run_(product=code)], STATIONS, NOW, geo()).extras["525-9"]["line_name"]
            self.assertTrue(ln.startswith(name + " 525 · "), ln)
        ln = self.rt().parse([run_(product=None)], STATIONS, NOW, geo()).extras["525-9"]["line_name"]
        self.assertEqual(ln, "525 · Stockholm C–Göteborg C")

    def test_names_from_the_geometry_then_the_signature(self):
        snap = self.rt().parse([run_()], {}, NOW, geo())
        self.assertEqual(snap.extras["525-9"]["line_name"], "SJ Snabbtåg 525 · Stockholm C–Göteborg C")
        snap = self.rt().parse([run_()], {}, NOW, {})
        self.assertEqual(snap.extras["525-9"]["line_name"], "SJ Snabbtåg 525 · Cst–G")
        self.assertEqual(snap.next_stops["525-9"], ("Söc", NOW + 420))
        # Stations given win over the geometry's.
        snap = self.rt().parse([run_()], {"Cst": {"name": "Sthlm"}}, NOW, geo())
        self.assertTrue(snap.extras["525-9"]["line_name"].endswith("Sthlm–Göteborg C"))

    def test_toward_the_hub(self):
        calls = [call("G", "Avgang", NOW - 900), call("Söc", "Ankomst", NOW + 300), call("Cst", "Ankomst", NOW + 1200)]
        snap = self.rt().parse([run_(calls=calls)], STATIONS, NOW, geo())
        self.assertIs(snap.extras["525-9"]["toward_hub"], True)
        # Past its last stop, the hub its last: toward.
        calls = [call("G", "Avgang", NOW - 900), call("Cst", "Ankomst", NOW - 300, actual=NOW - 300)]
        snap = self.rt().parse([run_(calls=calls)], STATIONS, NOW, geo())
        self.assertIs(snap.extras["525-9"]["toward_hub"], True)
        calls = [call("Cst", "Avgang", NOW - 900), call("G", "Ankomst", NOW - 300, actual=NOW - 300)]
        snap = self.rt().parse([run_(calls=calls)], STATIONS, NOW, geo())
        self.assertIs(snap.extras["525-9"]["toward_hub"], False)
        # Larger end city: Kalmar to Hyllie (Malmö) goes toward Hyllie.
        calls = [call("Kac", "Avgang", NOW - 900), call("Hie", "Ankomst", NOW + 900)]
        snap = self.rt().parse([run_(calls=calls)], STATIONS, NOW, geo())
        self.assertIs(snap.extras["525-9"]["toward_hub"], True)
        # No hub: no key, the leaving look.
        calls = [call("Str", "Avgang", NOW - 900), call("Str", "Ankomst", NOW + 900)]
        snap = self.rt().parse([run_(calls=calls)], STATIONS, NOW, geo())
        self.assertNotIn("toward_hub", snap.extras["525-9"])

    def test_skips(self):
        rt = self.rt()
        done = [call("Cst", "Avgang", NOW - 9000), call("G", "Ankomst", NOW - 100, actual=NOW - 100)]
        rt.parse([run_("3", ts=NOW - 10, calls=done)], STATIONS, NOW - 400, geo())      # seen once, fresh
        snap = rt.parse([run_(calls=[]), run_("1", calls=[call("Cst", "Avgang", NOW, canceled=True),
                                                         call("G", "Ankomst", NOW + 9, canceled=True)]),
                         run_("2", ts=NOW - src.MAX_FIRST_AGE_S - 1),
                         run_("3", ts=NOW - src.FINISHED_AGE_S - 1, calls=done)],
                        STATIONS, NOW, geo())
        self.assertEqual(snap.observations, [])
        self.assertEqual(snap.skipped, {"no_calls": 1, "canceled": 1, "stale_first_sight": 1, "finished": 1})
        # Every public call cancelled is a cancelled run, whatever its hidden rows say.
        snap = rt.parse([run_("5", calls=[call("Cst", "Avgang", NOW - 9, canceled=True),
                                          call("Flb", "Avgang", NOW + 9, public=False),
                                          call("G", "Ankomst", NOW + 900, canceled=True)])], STATIONS, NOW, geo())
        self.assertEqual(snap.skipped, {"canceled": 1})
        # A hidden call alone does not make a run cancelled.
        snap = rt.parse([run_("4", calls=[call("Cst", "Avgang", NOW - 9, public=False, canceled=True),
                                          call("G", "Ankomst", NOW + 900)])], STATIONS, NOW, geo())
        self.assertEqual(len(snap.observations), 1)

    def test_a_train_seen_goes_on_when_its_fix_ages(self):
        rt = self.rt()
        rt.parse([run_(ts=NOW - 30)], STATIONS, NOW, geo())
        snap = rt.parse([run_(ts=NOW - 30)], STATIONS, NOW + src.MAX_FIRST_AGE_S, geo())
        self.assertEqual(len(snap.observations), 1)
        # Forgotten after FORGET_S: a first sight again.
        rt.parse([], STATIONS, NOW + src.MAX_FIRST_AGE_S + src.FORGET_S + 1, geo())
        snap = rt.parse([run_(ts=NOW - 30)], STATIONS, NOW + src.MAX_FIRST_AGE_S + src.FORGET_S + 2, geo())
        self.assertEqual(snap.skipped, {"stale_first_sight": 1})

    def test_finished_with_a_fresh_fix_is_still_drawn(self):
        calls = [call("Cst", "Avgang", NOW - 9000), call("G", "Ankomst", NOW - 100, actual=NOW - 100)]
        snap = self.rt().parse([run_(calls=calls, ts=NOW - 10)], STATIONS, NOW, geo())
        self.assertEqual(len(snap.observations), 1)
        self.assertNotIn("525-9", snap.next_stops)

    def test_no_geometry_no_line(self):
        snap = self.rt().parse([run_()], STATIONS, NOW, None)
        self.assertEqual(snap.route_keys, {})
        snap = self.rt().parse([run_()], STATIONS, NOW, {"stops": {}})
        self.assertEqual(snap.route_keys, {})
        # No station with coordinates in the trip: no line.
        snap = self.rt().parse([run_(calls=[call("Q", "Avgang", NOW - 9), call("Z", "Ankomst", NOW + 9)])],
                               STATIONS, NOW, geo())
        self.assertEqual(snap.route_keys, {})

    def test_the_drawn_train_is_on_its_line(self):
        g = geo()
        rt = self.rt()
        # Halfway along the (two-point) Stockholm C-Södertälje Syd line, 50 m to its side.
        snap = rt.parse([run_(lat=59.2465, lon=17.8530, ts=NOW - 5)], STATIONS, NOW, g)
        proj = geometry.Projector(g)
        fleet = __import__("saw_livetrack.gtfs", fromlist=["Fleet"]).Fleet()
        result = fleet.update(snap.observations, NOW, next_stops=snap.next_stops, trip_delays=snap.trip_delays)
        for vid, rec in result["vehicles"].items():
            rec.update({k: v for k, v in snap.extras[vid].items() if k in base.EXTRA_KEYS})
        counts = projection.apply(proj, snap, result, NOW, derive_speed=True)
        self.assertEqual(counts["estimated"], 1)
        rec = result["vehicles"]["525-9"]
        self.assertEqual(rec["position_source"], "estimated")
        route = proj._route(snap.route_keys["525-9"])
        d, off = route.project(rec["latitude"], rec["longitude"])
        self.assertLess(off, 1.0)


class Lines(unittest.TestCase):
    def test_plan_and_pattern(self):
        has = lambda a, b: lines_mod.pair_key(a, b) == "Cst|Söc"
        coords = {"Cst": 1, "Söc": 1, "G": 1}
        self.assertEqual(lines_mod.plan(["Cst", "Q", "Söc", "Söc", "G"], has, coords),
                         [["Cst", "Söc", "Cst|Söc"], ["Söc", "G", None]])
        self.assertEqual(lines_mod.plan(["Cst"], has, coords), [])
        self.assertEqual(lines_mod.signatures([{"sig": "A"}, {"sig": "A"}, {"sig": ""}, {"sig": "B"}, {"sig": "A"}]),
                         ["A", "B", "A"])
        legs = [["Cst", "Söc", "Cst|Söc"]]
        pid = lines_mod.pattern_id(legs)
        self.assertEqual(pid, "se" + hashlib.sha1(b'[["Cst","S\\u00f6c","Cst|S\\u00f6c"]]').hexdigest()[:12])
        self.assertNotEqual(pid, lines_mod.pattern_id([["Cst", "Söc", None]]))
        self.assertEqual(lines_mod.pair_key("Söc", "Cst"), "Cst|Söc")

    def test_the_shipped_lines(self):
        sl = lines_mod.ShippedLines.load()
        self.assertGreater(len(sl.lines), 700)
        self.assertIn("ODbL", sl.meta["licence"])
        enc = sl.encoded()
        k = next(iter(enc))
        self.assertEqual(enc[k], list(sl.lines[k][1]))
        a, b = k.split("|")
        self.assertTrue(sl.has(b, a))
        self.assertLess(a, b)
        with self.assertRaises(ValueError):
            lines_mod.ShippedLines({"v": 2})

    def test_the_ends(self):
        ends = lines_mod.load_ends()
        self.assertEqual(ends["Hie"]["settlement"], "Malmö")
        self.assertEqual(ends["Cst"]["settlement"], "Stockholm")
        self.assertEqual(ends["So"]["settlement"], "Stockholm")
        self.assertEqual(ends["Uåö"]["settlement"], "Umeå")
        self.assertIsNone(ends["Str"]["population"])
        self.assertEqual(len(ends), 1643)
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        p = pathlib.Path(tmp) / "e.json"
        self.assertEqual(lines_mod.load_ends(str(p)), {})
        p.write_text('{"v": 2, "ends": {"A": {}}}', encoding="utf-8")
        self.assertEqual(lines_mod.load_ends(str(p)), {})
        p.write_text("[]", encoding="utf-8")
        self.assertEqual(lines_mod.load_ends(str(p)), {})
        p.write_text("x", encoding="utf-8")
        self.assertEqual(lines_mod.load_ends(str(p)), {})


class View(unittest.TestCase):
    def client(self, stations, version=None):
        return types.SimpleNamespace(stations=lambda fetch=True: dict(stations), stations_version=lambda: version)

    def test_version_and_distill(self):
        v = src.StaticView(self.client(STATIONS, 1794000000))
        digest = hashlib.sha1((HERE / "data" / "sweden_lines.json.gz").read_bytes()).hexdigest()[:12]
        self.assertEqual(v.static_version(), f"trv{src.DISTILL_V}:{digest}:1794000000")
        self.assertEqual(src.StaticView(self.client({})).static_version(), f"trv{src.DISTILL_V}:{digest}:0")
        self.assertIsNone(v.static_path())
        d = v.distill_geometry()
        self.assertTrue(d["live_trains"])
        self.assertEqual(d["v"], geometry.GEOMETRY_VERSION)
        self.assertEqual(d["stops"]["Cst"], [59.3303, 18.0582])
        self.assertEqual(d["stop_names"]["G"], "Göteborg C")
        self.assertEqual((d["trains"], d["shape_legs"], d["shapes"]), ({}, {}, {}))
        self.assertGreater(len(d["pair_lines"]), 700)
        self.assertIsNotNone(d["osm_base"])
        self.assertIsNone(src.StaticView(self.client({})).distill_geometry())

    def test_route_store_keeps_a_live_geometry(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        hass = _ha_stub.Hass(tmp)
        op = operators.OPERATORS["sj"]
        s = route_store.RouteStore(hass, None, op)
        view = src.StaticView(self.client(STATIONS, 1))
        s.static_client = view
        s.note_static(view.static_version())
        run(s.async_refresh())
        self.assertIsNotNone(s.projector)
        self.assertTrue(s.projector.geometry["live_trains"])
        # A geometry with no lines at all is not kept.
        s2 = route_store.RouteStore(hass, None, operators.OPERATORS["oresundstag"])
        s2.static_client = types.SimpleNamespace(
            static_version=lambda: "x", distill_geometry=lambda: {"live_trains": True, "pair_lines": {}})
        s2.note_static("x")
        run(s2.async_refresh())
        self.assertIsNone(s2.projector)


class Operators(unittest.TestCase):
    def test_fifteen_brands(self):
        ids = {op.id for op in sweden.SWEDEN}
        self.assertEqual(len(ids), 15)
        expect = {"sj", "vr_snabbtag", "snalltaget", "oresundstag", "pagatagen", "malartag", "vasttagen",
                  "krosatagen", "ostgotapendeln", "norrtag", "tag_i_bergslagen", "x_taget", "varmlandstrafik",
                  "tagab", "inlandsbanan"}
        self.assertEqual(ids, expect)
        # Every intercity brand the client routes has an entry, and nothing else.
        routed = {b for b in lib.BRANDS.values() if b != "sl_pendeltag"} | {lib.INLANDSBANAN} | set(
            lib.OPERATOR_BRANDS.values())
        self.assertEqual(routed, ids)
        for op in sweden.SWEDEN:
            self.assertIs(operators.OPERATORS[op.id], op)
            self.assertEqual(op.regions, ("SE",))
            self.assertEqual(op.source, operators.SOURCE_TRAFIKVERKET)
            self.assertEqual(op.source_options, {"consumer": lib.INTERCITY, "brand": op.id})
            self.assertEqual(op.lateness_keys(), {"late_threshold_min": 6, "very_late_threshold_min": 12})
            self.assertTrue(op.needs_key and op.derive_speed and op.gtfs_from_source)
            self.assertEqual(op.key_url, lib.KEY_URL)
            self.assertEqual(op.attribution, "Data: Trafikverket (trafikverket.se), CC0")
            self.assertEqual(op.scan_interval_s, 30)
            self.assertFalse(op.timed_without_fix)
        self.assertEqual(operators.regions_in_use()["SE"], "Sweden")
        self.assertEqual([op.id for op in operators.operators_in("SE")][:3], ["inlandsbanan", "krosatagen", "malartag"])

    def test_the_look(self):
        sj = operators.OPERATORS["sj"]
        leaving = sj.marker_keys({"toward_hub": False})
        self.assertEqual(leaving, {"marker_color": "#000000", "marker_ring_color": "#00AB3B", "marker_ring_width": 3,
                                   "marker_label_color": "#00AB3B", "marker_label_outline_color": "none",
                                   "marker_arrow_color": "#000000", "marker_arrow_outline_color": "#00AB3B"})
        self.assertEqual(sj.marker_keys({}), leaving)
        self.assertEqual(sj.marker_keys({"toward_hub": 1}), leaving)
        toward = sj.marker_keys({"toward_hub": True})
        self.assertEqual((toward["marker_color"], toward["marker_ring_color"], toward["marker_label_color"],
                          toward["marker_arrow_color"], toward["marker_arrow_outline_color"]),
                         ("#00AB3B", "#000000", "#000000", "#00AB3B", "#000000"))
        vr = operators.OPERATORS["vr_snabbtag"]
        self.assertEqual([vr.marker_keys({})[k] for k in ("marker_color", "marker_ring_color", "marker_label_color")],
                         ["#14B250", "#FDE674", "#FFFFFF"])
        self.assertEqual([vr.marker_keys({"toward_hub": True})[k] for k in
                          ("marker_color", "marker_ring_color", "marker_label_color")],
                         ["#FFFFFF", "#14B250", "#14B250"])
        table = {"snalltaget": "#F9423A", "oresundstag": "#D72B14", "pagatagen": "#DC001B", "malartag": "#0949A1",
                 "vasttagen": "#00ACEA", "krosatagen": "#C40000", "ostgotapendeln": "#E10E1C", "norrtag": "#005AAA",
                 "tag_i_bergslagen": "#C0311A", "x_taget": "#E1071A", "varmlandstrafik": "#F9B000",
                 "tagab": "#D5322C", "inlandsbanan": "#E4173A"}
        for op_id, fill in table.items():
            self.assertEqual(operators.OPERATORS[op_id].marker_keys({})["marker_color"], fill, op_id)
        self.assertEqual(operators.OPERATORS["vasttagen"].marker_keys({})["marker_label_color"], "#00394D")
        self.assertEqual(operators.OPERATORS["ostgotapendeln"].marker_keys({})["marker_ring_color"], "#320010")
        self.assertEqual(operators.OPERATORS["norrtag"].marker_keys({})["marker_label_color"], "#F89C0E")
        self.assertEqual(operators.OPERATORS["varmlandstrafik"].marker_keys({})["marker_label_color"], "#000000")
        self.assertEqual(operators.OPERATORS["pagatagen"].marker_keys({})["marker_label_color"], "#FFFFFF")


class Coordinator(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.hass = _ha_stub.Hass(self.dir)

    def make(self, op_id, key="k" * 32):
        entry = types.SimpleNamespace(data={"operator": op_id, "api_key": key}, options={}, domain=const.DOMAIN)
        return coordinator.IntercityRailCoordinator(self.hass, entry, operators.OPERATORS[op_id])

    def patch_read(self, fn):
        self.addCleanup(setattr, src, "read", src.read)
        src.read = fn

    def test_one_shared_client_one_claim_each(self):
        sj = self.make("sj")
        client = sj._trv_client
        self.assertIsInstance(client, lib.TrafikverketClient)
        self.assertIs(self.hass.data[lib.SHARED_KEY]["client"], client)
        self.assertEqual(client.storage_dir, self.dir)
        self.assertIsInstance(sj.routes.static_client, src.StaticView)
        self.assertIs(sj.routes.static_client.client, client)
        self.assertIsInstance(sj._trv, src.TrafikverketRealtime)
        ot = self.make("oresundstag", key="j" * 32)
        self.assertIs(ot._trv_client, client)
        self.assertEqual(client.claims, {(lib.INTERCITY, "sj"), (lib.INTERCITY, "oresundstag")})
        ot.async_release()
        self.assertEqual(client.claims, {(lib.INTERCITY, "sj")})
        self.assertIsNone(ot.routes.static_client)
        self.assertIsNone(ot._trv_client)
        sj.async_release()
        self.assertNotIn(lib.SHARED_KEY, self.hass.data)
        sj.async_release()                                  # idempotent

    def test_failures(self):
        def refused(*a):
            raise lib.AuthRefused("no usable API key is registered")
        self.patch_read(refused)
        c = self.make("sj")
        with self.assertRaises(_ha_stub.ConfigEntryAuthFailed):
            run(c._fetch())

        def busy(*a):
            raise lib.RateLimited("HTTP 429 from x")
        src.read = busy
        self.assertIsNone(run(c._fetch()))
        self.assertIn("HTTP 429", c._last_reason)

    def test_a_good_read(self):
        seen = []

        def read(client, consumer, brand, view):
            seen.append((client, consumer, brand, view))
            return [run_(ts=time.time() - 10)], STATIONS, "trv1:x:1"
        self.patch_read(read)
        c = self.make("sj")
        snap = run(c._fetch())
        self.assertEqual([o.train for o in snap.observations], ["525"])
        self.assertEqual(seen, [(c._trv_client, lib.INTERCITY, "sj", c.routes.static_client)])
        self.assertEqual(c.routes._static_version, "trv1:x:1")

    def test_read_asks_the_client(self):
        calls = []
        client = types.SimpleNamespace(for_consumer=lambda c, b: calls.append((c, b)) or ["r"],
                                       stations=lambda fetch=True: calls.append(fetch) or {"A": {}})
        view = types.SimpleNamespace(static_version=lambda: "v")
        self.assertEqual(src.read(client, "intercity", "sj", view), (["r"], {"A": {}}, "v"))
        self.assertEqual(calls, [("intercity", "sj"), False])
        self.assertEqual(src.read(client, "intercity", "sj")[2], None)


class KeyForm(unittest.TestCase):
    def setUp(self):
        self.check = src.check_key
        self.calls = []

        def fake(consumer, key):
            self.calls.append((consumer, key))
            return None
        src.check_key = fake

    def tearDown(self):
        src.check_key = self.check

    def new(self, entries=()):
        f = flow.IntercityRailConfigFlow()
        f._entries = [types.SimpleNamespace(data=d) for d in entries]
        f._ids = {d["operator"] for d in entries}
        f.hass = _ha_stub.Hass(tempfile.gettempdir())
        return f

    def test_sweden_asks_for_a_key_and_checks_it_with_trafikverket(self):
        f = self.new()
        run(f.async_step_user({"region": "SE"}))
        s = run(f.async_step_operator({"operator": "sj"}))
        self.assertEqual((s["step_id"], s["placeholders"]["url"]), ("key", lib.KEY_URL))
        self.assertNotIn("suggested", s["schema"] if isinstance(s["schema"], dict) else {})
        s = run(f.async_step_key({"api_key": " abc "}))
        self.assertEqual(s["data"], {"operator": "sj", "api_key": "abc"})
        self.assertEqual(self.calls, [("intercity", "abc")])

    def test_a_second_swedish_brand_is_offered_the_key(self):
        f = self.new([{"operator": "sj", "api_key": "K1"}, {"operator": "nsw_trainlink", "api_key": "NSW"}])
        run(f.async_step_user({"region": "SE"}))
        s = run(f.async_step_operator({"operator": "oresundstag"}))
        self.assertEqual(s["schema"]["suggested"], {"api_key": "K1"})
        # An error re-shows the form without the suggestion overriding what was typed.
        src.check_key = lambda c, k: "invalid_key"
        s = run(f.async_step_key({"api_key": "bad"}))
        self.assertEqual(s["errors"], {"base": "invalid_key"})
        self.assertNotIn("suggested", s["schema"] if isinstance(s["schema"], dict) else {})

    def test_another_sources_key_is_not_offered(self):
        f = self.new([{"operator": "nsw_trainlink", "api_key": "NSW"}, {"operator": "vy"}])
        run(f.async_step_user({"region": "SE"}))
        s = run(f.async_step_operator({"operator": "sj"}))
        self.assertNotIn("suggested", s["schema"] if isinstance(s["schema"], dict) else {})


class SharedCopy(unittest.TestCase):
    def test_the_copy_is_byte_exact_with_the_reference(self):
        mine = (HERE / "shared_trafikverket.py").read_bytes()
        import saw_livetrack
        ref = pathlib.Path(saw_livetrack.__file__).resolve().parents[2] / "reference" / "shared_trafikverket.py"
        if not ref.exists():
            self.skipTest("the library's reference/ is not beside an installed wheel")
        self.assertEqual(hashlib.sha256(mine).hexdigest(), hashlib.sha256(ref.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
