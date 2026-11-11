"""The Netherlands on NS's vehicle feed (Intercity SSOT 8.11): the source adapter, its lines from SpoorKaart, the three
operators' look and lateness, the coordinator's branch, the key form, the route store taking a geometry whose trips
come with the trains, and option B's observed_at_source on the map. Offline. Run from the repo root:
python -m unittest tests.test_ns_source
"""

import asyncio
import datetime as dt
import hashlib
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

from saw_livetrack import ns as lib  # noqa: E402

src = load("sources.ns")
base = load("sources.base")
operators = load("operators")
nsops = load("operators.ns")
coordinator = load("coordinator")
const = load("const")
flow = load("config_flow")
route_store = load("route_store")
geometry = load("geometry")
attributes = load("attributes")

run = asyncio.run
NOW = 1794389454.0
HERE = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_intercity_rail"
STATIONS = {"EHV": {"name": "Eindhoven Centraal", "lat": 51.443, "lon": 5.481},
            "TB": {"name": "Tilburg", "lat": 51.560, "lon": 5.084},
            "BD": {"name": "Breda", "lat": 51.595, "lon": 4.780},
            "RTD": {"name": "Rotterdam Centraal", "lat": 51.925, "lon": 4.469},
            "GVC": {"name": "Den Haag Centraal", "lat": 52.080, "lon": 4.325}}
LINES = {"EHV|TB": [5144300, 548100, 11700, -39700], "BD|TB": [5159500, 478000, -3500, 30400],
         "BD|RTD": [5159500, 478000, 33000, -31100]}


def call(code, name, aa, ad, ea=None, ed=None):
    c = {"stop_id": code.lower(), "code": code, "name": name, "aimed_arrival": aa, "aimed_departure": ad}
    if ea is not None:
        c["expected_arrival"] = ea
    if ed is not None:
        c["expected_departure"] = ed
    return c


def train(number="1126", type_="IC", updated=True, **kw):
    t = {"number": number, "type": type_, "lat": 51.70, "lon": 4.62, "speed_kmh": 136.01, "heading": 320.99,
         "observed_at": NOW - 4, "observed_at_source": "first_seen", "operator": "ns", "trip_id": "393120897",
         "service_date": "20261111", "agency": "NS", "brand": None, "route_name": "Intercity",
         "route_long": "Den Haag Centraal <-> Eindhoven Centraal IC1100", "headsign": "Den Haag Centraal",
         "updated": updated,
         "calls": [call("EHV", "Eindhoven Centraal", None, NOW - 3600, None, NOW - 3500),
                   call("TB", "Tilburg", NOW - 2400, NOW - 2340),
                   call("BD", "Breda", NOW - 1200, NOW - 1140),
                   call("RTD", "Rotterdam Centraal", NOW + 300, NOW + 360, NOW + 420, NOW + 480),
                   call("GVC", "Den Haag Centraal", NOW + 1500, None)],
         "path": ["EHV", "TB", "BD", "RTD", "GVC"]}
    t.update(kw)
    return t


def geo():
    return {"stops": {c: [v["lat"], v["lon"]] for c, v in STATIONS.items()},
            "stop_names": {c: v["name"] for c, v in STATIONS.items()}, "pair_lines": dict(LINES),
            "shape_legs": {}, "trains": {}}


class Parse(unittest.TestCase):
    def test_a_train(self):
        g = geo()
        snap = src.NsRealtime().parse([train()], NOW, g)
        o = snap.observations[0]
        self.assertEqual((o.vehicle_id, o.train, o.trip_id), ("1126-11", "1126", "1126-11"))
        self.assertEqual(o.observed_at, dt.datetime.fromtimestamp(NOW - 4, dt.timezone.utc))
        self.assertEqual(o.reported_course, 320.99)
        ex = snap.extras["1126-11"]
        self.assertEqual(ex["speed_kmh"], 136.0)
        self.assertEqual(ex["observed_at_source"], "first_seen")
        self.assertEqual(ex["line_name"], "Intercity 1126 · Eindhoven Centraal–Den Haag Centraal")
        self.assertNotIn("brand", ex)
        # Next stop Rotterdam, delay 120 s from the updates.
        self.assertEqual(snap.stop_codes["1126-11"], "RTD")
        self.assertEqual(snap.next_stops["1126-11"], ("Rotterdam Centraal", NOW + 420))
        self.assertEqual(snap.trip_delays["1126-11"], 120)

    def test_the_line_is_spoorkaart_legs(self):
        g = geo()
        snap = src.NsRealtime().parse([train()], NOW, g)
        sid = snap.route_keys["1126-11"]
        self.assertTrue(sid.startswith("nl"))
        self.assertEqual(g["shape_legs"][sid], [["EHV", "TB", "EHV|TB"], ["TB", "BD", "BD|TB"],
                                                ["BD", "RTD", "BD|RTD"], ["RTD", "GVC", None]])
        self.assertEqual(g["trains"][sid], [sid])
        pts = geometry.line_from_legs(g, sid, {})
        self.assertEqual(pts[0], [51.443, 5.481])
        self.assertEqual(pts[-1], [52.08, 4.325])

    def test_no_delay_without_the_updates(self):
        snap = src.NsRealtime().parse([train(updated=False)], NOW, geo())
        self.assertNotIn("1126-11", snap.trip_delays)
        self.assertIn("1126-11", snap.next_stops)

    def test_an_unmatched_train_is_at_its_fix(self):
        t = {"number": "703670", "type": "IC", "lat": 52.0, "lon": 5.0, "speed_kmh": 0.0, "heading": 10.0,
             "observed_at": NOW - 30, "observed_at_source": "first_seen", "operator": "ns"}
        snap = src.NsRealtime().parse([t], NOW, geo())
        self.assertEqual(snap.observations[0].vehicle_id, "703670")
        self.assertEqual(snap.route_keys, {})
        self.assertNotIn("line_name", snap.extras["703670"])

    def test_a_regional_train(self):
        t = train(number="8038", type_="ARR", operator="arriva", brand="Blauwnet", route_name="RS20",
                  calls=[call("EHV", "Emmen", None, NOW - 100), call("TB", "Zwolle", NOW + 900, None)],
                  path=["EHV", "TB"])
        snap = src.NsRealtime().parse([t], NOW, geo())
        ex = snap.extras["8038-11"]
        self.assertEqual(ex["line_name"], "Blauwnet RS20 8038 · Emmen–Zwolle")
        self.assertEqual(ex["brand"], "Blauwnet")

    def test_quiet_none_and_duplicates(self):
        self.assertIsNone(src.NsRealtime().parse(None, NOW, geo()))
        self.assertEqual(src.NsRealtime().parse([], NOW, geo()).observations, [])
        snap = src.NsRealtime().parse([train(), train(), {"number": ""}], NOW, geo())
        self.assertEqual(len(snap.observations), 1)
        self.assertEqual(snap.skipped, {"duplicate": 1, "no_number": 1})

    def test_without_a_geometry(self):
        snap = src.NsRealtime().parse([train()], NOW, None)
        self.assertEqual(snap.route_keys, {})
        self.assertEqual(snap.next_stops["1126-11"][0], "Rotterdam Centraal")

    def test_identity(self):
        self.assertEqual(src.identity("1126", "20261101"), "1126-1")
        self.assertEqual(src.identity("1126", None), "1126")


class Map(unittest.TestCase):
    def test_observed_at_source_reaches_the_map_and_brand_does_not(self):
        rec = {"vehicle_id": "8038-11", "marker_label": "8038", "in_service": True,
               "observed_at": "2026-11-11T09:30:50+00:00", "observed_at_source": "first_seen", "brand": "Blauwnet"}
        a = attributes.to_attributes(rec, "arriva")
        self.assertEqual(a["observed_at_source"], "first_seen")
        self.assertNotIn("brand", a)
        self.assertIn("observed_at_source", base.EXTRA_KEYS)
        self.assertIn("brand", base.RECORD_ONLY_KEYS)


class View(unittest.TestCase):
    def client(self, stations, lines, version="ns1.1:abc:def"):
        return types.SimpleNamespace(stations=lambda: dict(stations), pair_lines=lambda: dict(lines),
                                     static_version=lambda: version)

    def test_version_and_distill(self):
        v = src.StaticView(self.client(STATIONS, LINES))
        self.assertEqual(v.static_version(), "nsv1:ns1.1:abc:def")
        d = v.distill_geometry()
        self.assertTrue(d["live_trains"])
        self.assertEqual(d["stops"]["RTD"], [51.925, 4.469])
        self.assertEqual(d["stop_names"]["GVC"], "Den Haag Centraal")
        self.assertEqual(d["pair_lines"], LINES)
        self.assertEqual(d["v"], geometry.GEOMETRY_VERSION)
        self.assertIsNone(src.StaticView(self.client({}, LINES)).distill_geometry())
        self.assertIsNone(src.StaticView(self.client(STATIONS, {})).distill_geometry())
        self.assertIsNone(src.StaticView(self.client(STATIONS, LINES, None)).static_version())

    def test_route_store_keeps_a_live_geometry(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        hass = _ha_stub.Hass(tmp)
        s = route_store.RouteStore(hass, None, operators.OPERATORS["ns"])
        view = src.StaticView(self.client(STATIONS, LINES))
        s.static_client = view
        s.note_static(view.static_version())
        run(s.async_refresh())
        self.assertIsNotNone(s.projector)
        self.assertTrue(s.projector.geometry["live_trains"])


class Operators(unittest.TestCase):
    def test_three_entries(self):
        for op_id in ("ns", "arriva", "keolis"):
            op = operators.OPERATORS[op_id]
            self.assertEqual(op.regions, ("NL",))
            self.assertEqual(op.source, "ns")
            self.assertEqual(op.source_options, {"consumer": lib.INTERCITY, "operator": op_id})
            self.assertTrue(op.needs_key)
            self.assertEqual(op.key_url, lib.KEY_URL)
            self.assertEqual(op.lateness_keys(), {"late_threshold_min": 3, "very_late_threshold_min": 10})
            self.assertEqual(op.scan_interval_s, 15)
            self.assertIn("OVapi", op.attribution)
        self.assertEqual(operators.regions_in_use()["NL"], "Netherlands")
        self.assertEqual([op.id for op in operators.operators_in("NL")], ["arriva", "keolis", "ns"])

    def test_the_look(self):
        k = operators.OPERATORS["ns"].marker_keys({"train": "1126"})
        self.assertEqual(k["marker_color"], "#FFC917")
        self.assertEqual(k["marker_ring_color"], "#003082")
        self.assertEqual(k["marker_label_color"], "#003082")
        self.assertEqual(operators.OPERATORS["arriva"].marker_keys({}), {})


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

    def test_one_shared_client_for_the_three(self):
        n = self.make("ns")
        client = n._ns_client
        self.assertIsInstance(client, lib.NsClient)
        self.assertIs(self.hass.data[lib.SHARED_KEY]["client"], client)
        self.assertEqual(client.storage_dir, self.dir)
        self.assertIsInstance(n.routes.static_client, src.StaticView)
        a = self.make("arriva", key="j" * 32)
        self.assertIs(a._ns_client, client)
        self.assertEqual(self.hass.data[lib.SHARED_KEY]["consumers"], {lib.INTERCITY: 2})
        a.async_release()
        self.assertIsNone(a.routes.static_client)
        self.assertEqual(client.consumers, {lib.INTERCITY})
        n.async_release()
        self.assertNotIn(lib.SHARED_KEY, self.hass.data)
        n.async_release()

    def test_failures(self):
        def refused(*a):
            raise lib.AuthRefused("no usable API key is registered")
        self.patch_read(refused)
        c = self.make("ns")
        with self.assertRaises(_ha_stub.ConfigEntryAuthFailed):
            run(c._fetch())

        def busy(*a):
            raise lib.RateLimited("HTTP 429 from x")
        src.read = busy
        self.assertIsNone(run(c._fetch()))
        self.assertIn("HTTP 429", c._last_reason)

    def test_a_good_read(self):
        seen = []

        def read(client, consumer, operator, view):
            seen.append((client, consumer, operator, view))
            return [train(observed_at=time.time() - 3)], "nsv1:x"
        self.patch_read(read)
        c = self.make("keolis")
        snap = run(c._fetch())
        self.assertEqual([o.train for o in snap.observations], ["1126"])
        self.assertEqual(seen, [(c._ns_client, lib.INTERCITY, "keolis", c.routes.static_client)])
        self.assertEqual(c.routes._static_version, "nsv1:x")

    def test_read_asks_the_client(self):
        calls = []
        client = types.SimpleNamespace(for_consumer=lambda c, o: calls.append((c, o)) or ["t"],
                                       static_version=lambda: "c")
        view = types.SimpleNamespace(static_version=lambda: "v")
        self.assertEqual(src.read(client, "intercity", "ns", view), (["t"], "v"))
        self.assertEqual(src.read(client, "intercity", "ns"), (["t"], "c"))
        self.assertEqual(calls, [("intercity", "ns"), ("intercity", "ns")])


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

    def test_the_netherlands_asks_for_an_ns_key(self):
        f = self.new()
        run(f.async_step_user({"region": "NL"}))
        s = run(f.async_step_operator({"operator": "ns"}))
        self.assertEqual((s["step_id"], s["placeholders"]["url"]), ("key", lib.KEY_URL))
        s = run(f.async_step_key({"api_key": " abc "}))
        self.assertEqual(s["data"], {"operator": "ns", "api_key": "abc"})
        self.assertEqual(self.calls, [("intercity", "abc")])

    def test_a_second_dutch_entry_is_offered_the_key(self):
        f = self.new([{"operator": "ns", "api_key": "K1"}, {"operator": "sj", "api_key": "SE"}])
        run(f.async_step_user({"region": "NL"}))
        s = run(f.async_step_operator({"operator": "arriva"}))
        self.assertEqual(s["schema"]["suggested"], {"api_key": "K1"})


class SharedCopy(unittest.TestCase):
    def test_the_copy_is_byte_exact_with_the_reference(self):
        mine = (HERE / "shared_ns.py").read_bytes()
        import saw_livetrack
        ref = pathlib.Path(saw_livetrack.__file__).resolve().parents[2] / "reference" / "shared_ns.py"
        if not ref.exists():
            self.skipTest("the library's reference/ is not beside an installed wheel")
        self.assertEqual(hashlib.sha256(mine).hexdigest(), hashlib.sha256(ref.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
