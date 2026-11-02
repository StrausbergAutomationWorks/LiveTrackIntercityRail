"""The key step, the reauth step, the redaction, the route store from the client, and the coordinator's
keyed fetch, with Home Assistant stubbed (tests/_ha_stub.py). Our branches, never HA's API.
Run from the repo root: python -m unittest tests.test_key_flow
"""

import asyncio
import io
import os
import pathlib
import shutil
import sys
import tempfile
import types
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _ha_stub  # noqa: E402
_ha_stub.install()
from _load import load  # noqa: E402

flow = load("config_flow")
const = load("const")
operators = load("operators")
src = load("sources.tfnsw")
diagnostics = load("diagnostics")
route_store = load("route_store")
coordinator = load("coordinator")
shared = load("shared_tfnsw")

run = asyncio.run


def new_flow(ids=()):
    f = flow.IntercityRailConfigFlow()
    f._ids = ids
    f.hass = _ha_stub.Hass(tempfile.gettempdir())
    return f


class KeyStep(unittest.TestCase):
    def setUp(self):
        self.check = src.check_key
        self.calls = []

    def tearDown(self):
        src.check_key = self.check

    def answer(self, result):
        def fake(consumer, key):
            self.calls.append((consumer, key))
            return result
        src.check_key = fake

    def to_key(self, f):
        run(f.async_step_user({"region": "AU"}))
        return run(f.async_step_operator({"operator": "nsw_trainlink"}))

    def test_australia_is_offered(self):
        s = run(new_flow().async_step_user())
        self.assertEqual(s["step_id"], "user")

    def test_a_railroad_with_a_key_asks_for_it(self):
        s = self.to_key(new_flow())
        self.assertEqual((s["type"], s["step_id"]), ("form", "key"))
        self.assertEqual(s["placeholders"]["name"], "NSW TrainLink")
        self.assertEqual(s["placeholders"]["url"], operators.OPERATORS["nsw_trainlink"].key_url)

    def test_a_railroad_with_no_key_does_not(self):
        f = new_flow()
        run(f.async_step_user({"region": "FI"}))
        s = run(f.async_step_operator({"operator": "vr"}))
        self.assertEqual(s["type"], "create_entry")
        self.assertEqual(s["data"], {"operator": "vr"})

    def test_a_good_key_makes_the_entry(self):
        self.answer(None)
        f = new_flow()
        self.to_key(f)
        s = run(f.async_step_key({"api_key": "  abc  "}))
        self.assertEqual(s["type"], "create_entry")
        self.assertEqual(s["data"], {"operator": "nsw_trainlink", "api_key": "abc"})
        self.assertEqual(s["title"], "NSW TrainLink")
        self.assertEqual(self.calls, [("intercity", "abc")])

    def test_a_refused_key_asks_again(self):
        self.answer("invalid_key")
        f = new_flow()
        self.to_key(f)
        s = run(f.async_step_key({"api_key": "abc"}))
        self.assertEqual((s["type"], s["step_id"], s["errors"]), ("form", "key", {"base": "invalid_key"}))

    def test_no_answer_is_another_error(self):
        self.answer("cannot_connect")
        f = new_flow()
        self.to_key(f)
        self.assertEqual(run(f.async_step_key({"api_key": "abc"}))["errors"], {"base": "cannot_connect"})

    def test_an_empty_key_is_not_tried(self):
        self.answer(None)
        f = new_flow()
        self.to_key(f)
        self.assertEqual(run(f.async_step_key({"api_key": "   "}))["errors"], {"base": "invalid_key"})
        self.assertEqual(self.calls, [])

    def test_already_set_up(self):
        f = new_flow(ids={"nsw_trainlink"})
        with self.assertRaises(_ha_stub.Abort):
            run(f.async_step_operator({"operator": "nsw_trainlink"}))

    def test_reauth_asks(self):
        f = new_flow()
        f._reauth = types.SimpleNamespace(data={"operator": "nsw_trainlink", "api_key": "old"})
        s = run(f.async_step_reauth({"operator": "nsw_trainlink"}))
        self.assertEqual((s["type"], s["step_id"]), ("form", "reauth_confirm"))
        self.assertEqual(s["placeholders"]["name"], "NSW TrainLink")

    def test_reauth_with_a_good_key(self):
        self.answer(None)
        f = new_flow()
        f._reauth = types.SimpleNamespace(data={"operator": "nsw_trainlink", "api_key": "old"})
        s = run(f.async_step_reauth_confirm({"api_key": " new "}))
        self.assertEqual(s["reason"], "reauth_successful")
        self.assertEqual(f._reauth.data, {"operator": "nsw_trainlink", "api_key": "new"})

    def test_reauth_with_a_bad_key_keeps_the_old(self):
        self.answer("invalid_key")
        f = new_flow()
        f._reauth = types.SimpleNamespace(data={"operator": "nsw_trainlink", "api_key": "old"})
        s = run(f.async_step_reauth_confirm({"api_key": "bad"}))
        self.assertEqual(s["errors"], {"base": "invalid_key"})
        self.assertEqual(f._reauth.data["api_key"], "old")

    def test_reauth_with_nothing(self):
        self.answer(None)
        f = new_flow()
        f._reauth = types.SimpleNamespace(data={"operator": "nsw_trainlink", "api_key": "old"})
        self.assertEqual(run(f.async_step_reauth_confirm({"api_key": " "}))["errors"], {"base": "invalid_key"})
        self.assertEqual(self.calls, [])


class CheckKey(unittest.TestCase):
    def setUp(self):
        self.client = src.TfnswClient

    def tearDown(self):
        src.TfnswClient = self.client

    def answer(self, exc):
        class Fake:
            def __init__(self, consumers):
                self.consumers = consumers

            def for_consumer(self, consumer):
                if exc:
                    raise exc("x")
                return None, None
        src.TfnswClient = Fake

    def test_ok(self):
        self.answer(None)
        self.assertIsNone(src.check_key("intercity", "k"))

    def test_refused(self):
        self.answer(src.KeyRefused)
        self.assertEqual(src.check_key("intercity", "k"), "invalid_key")

    def test_no_answer(self):
        self.answer(src.KeyedError)
        self.assertEqual(src.check_key("intercity", "k"), "cannot_connect")


class Diagnostics(unittest.TestCase):
    def test_the_key_is_redacted(self):
        c = types.SimpleNamespace(operator=operators.OPERATORS["nsw_trainlink"], data={}, skipped={},
                                  fleet=types.SimpleNamespace(stats=dict), routes=types.SimpleNamespace(info=None), placement={})
        hass = types.SimpleNamespace(data={const.DOMAIN: {"e": c}})
        entry = types.SimpleNamespace(entry_id="e", data={"operator": "nsw_trainlink", "api_key": "SECRET"}, options={})
        d = run(diagnostics.async_get_config_entry_diagnostics(hass, entry))
        self.assertNotIn("SECRET", repr(d))
        self.assertEqual(d["entry"]["data"]["operator"], "nsw_trainlink")


def timetable():
    files = {
        "routes.txt": "route_id,route_short_name,route_long_name,route_type\n4T.T.NT31,31,North Coast NSW,106\n4T.C.1,1,Coach,204\n",
        "trips.txt": "route_id,service_id,trip_id,trip_short_name,shape_id\n4T.T.NT31,S,T1,NT31,X\n4T.C.1,S,C1,C1,Y\n",
        "stops.txt": "stop_id,stop_name,stop_lat,stop_lon,parent_station\n1,One,-30,152,\n2,Two,-31,152,\n",
        "stop_times.txt": "trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type\nT1,08:00:00,08:00:00,1,1,0,0\nC1,09:00:00,09:00:00,2,1,0,0\n",
        "shapes.txt": "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\nX,-29,152,1\nX,-30,152,2\nY,-31,152,1\nY,-32,152,2\n",
    }
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        for n, t in files.items():
            z.writestr(n, t)
    return out.getvalue()


class FakeClient:
    def __init__(self, path, version):
        self.path, self.version, self.opens = path, version, 0

    def static_version(self):
        return self.version

    def static_path(self):
        self.opens += 1
        return self.path


class RouteStoreFromClient(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.zip = os.path.join(self.dir, "zip.zip")
        with open(self.zip, "wb") as fh:
            fh.write(timetable())
        self.hass = _ha_stub.Hass(self.dir)
        self.op = operators.OPERATORS["nsw_trainlink"]

    def store(self, client):
        s = route_store.RouteStore(self.hass, None, self.op)
        s.static_client = client
        return s

    def test_cut_and_by_trip(self):
        s = self.store(FakeClient(self.zip, "v1"))
        s.note_static("v1")
        run(s.async_refresh())
        self.assertEqual(s.projector.geometry["trains"], {"T1": ["X"]})
        self.assertEqual(s.projector.geometry["source_version"], "v1")
        self.assertIn("T1", s.projector.geometry["trip_stops"])

    def test_nothing_until_the_client_has_a_version(self):
        c = FakeClient(self.zip, None)
        s = self.store(c)
        run(s.async_refresh())
        self.assertIsNone(s.projector)
        self.assertEqual(c.opens, 0)

    def test_nothing_before_the_client_has_a_file(self):
        s = self.store(FakeClient(None, "v1"))
        self.assertIsNone(s._distill_from_client())
        s.note_static("v1")
        run(s.async_refresh())
        self.assertIsNone(s.projector)

    def test_same_version_not_again(self):
        c = FakeClient(self.zip, "v1")
        s = self.store(c)
        s.note_static("v1")
        run(s.async_refresh())
        n = c.opens
        s._next_try = 0
        self.assertFalse(s.due())
        run(s.async_refresh())
        self.assertEqual(c.opens, n)

    def test_a_new_version_again(self):
        c = FakeClient(self.zip, "v1")
        s = self.store(c)
        s.note_static("v1")
        run(s.async_refresh())
        c.version = "v2"
        s.note_static("v2")
        s._next_try = 0
        self.assertTrue(s.due())
        run(s.async_refresh())
        self.assertEqual(s.projector.geometry["source_version"], "v2")

    def test_a_restart_reads_the_copy(self):
        c = FakeClient(self.zip, "v1")
        s = self.store(c)
        s.note_static("v1")
        run(s.async_refresh())
        s2 = self.store(c)
        run(s2.async_load_cached())
        self.assertEqual(s2.projector.geometry["trains"], {"T1": ["X"]})
        s2.note_static("v1")
        self.assertFalse(s2.due())

    def test_a_bad_zip_keeps_the_copy(self):
        c = FakeClient(self.zip, "v1")
        s = self.store(c)
        s.note_static("v1")
        run(s.async_refresh())
        with open(self.zip, "wb") as fh:
            fh.write(b"not a zip")
        c.version = "v2"
        s.note_static("v2")
        s._next_try = 0
        run(s.async_refresh())
        self.assertEqual(s.projector.geometry["source_version"], "v1")

    def test_a_timetable_with_no_lines_keeps_the_copy(self):
        c = FakeClient(self.zip, "v1")
        s = self.store(c)
        s.note_static("v1")
        run(s.async_refresh())
        d0 = s.projector
        s._distill_from_client = lambda: {"shapes": {}, "trains": {}}
        c.version = "v2"
        s.note_static("v2")
        s._next_try = 0
        run(s.async_refresh())
        self.assertIs(s.projector, d0)

    def test_no_url_no_client_is_off(self):
        s = route_store.RouteStore(self.hass, None, self.op)
        self.assertFalse(s.due())
        run(s.async_load_cached())
        self.assertFalse(s._loaded)

    def test_a_url_railroad_is_as_before(self):
        s = route_store.RouteStore(self.hass, None, operators.OPERATORS["vr"])
        self.assertTrue(s.due())
        self.assertIsNone(s.static_client)


class Coordinator(unittest.TestCase):
    def make(self, read):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        hass = _ha_stub.Hass(self.dir)
        entry = types.SimpleNamespace(data={"operator": "nsw_trainlink", "api_key": "K"}, options={}, domain=const.DOMAIN)
        self.read = src.read
        self.addCleanup(setattr, src, "read", self.read)
        src.read = read
        return coordinator.IntercityRailCoordinator(hass, entry, operators.OPERATORS["nsw_trainlink"]), hass

    def test_registers_its_consumer_and_key(self):
        c, hass = self.make(None)
        self.assertEqual(c._tfnsw_client.consumers, {"intercity"})
        self.assertEqual(c._tfnsw_client.stats()["keys"], 1)
        self.assertEqual(c._tfnsw_client._ring.active(), "K")
        self.assertIs(c.routes.static_client, c._tfnsw_client)
        self.assertEqual(hass.data["saw_tfnsw_v1"]["consumers"], {"intercity": 1})

    def test_release_unregisters(self):
        c, hass = self.make(None)
        c.async_release()
        self.assertNotIn("saw_tfnsw_v1", hass.data)
        self.assertIsNone(c.routes.static_client)
        c.async_release()   # idempotent

    def test_releasing_twice_leaves_another_entrys_claim(self):
        c, hass = self.make(None)
        entry = types.SimpleNamespace(data={"operator": "nsw_trainlink", "api_key": "K2"}, options={}, domain=const.DOMAIN)
        other = coordinator.IntercityRailCoordinator(hass, entry, operators.OPERATORS["nsw_trainlink"])
        c.async_release()
        c.async_release()
        self.assertEqual(hass.data["saw_tfnsw_v1"]["consumers"], {"intercity": 1})
        self.assertIn("intercity", other._tfnsw_client.consumers)

    def test_every_key_refused_asks_for_a_new_one(self):
        def read(client, consumer):
            raise coordinator.AuthRefused("x")
        c, _ = self.make(read)
        with self.assertRaises(_ha_stub.ConfigEntryAuthFailed):
            run(c._fetch())

    def test_a_failure_is_ridden_out(self):
        def read(client, consumer):
            raise coordinator.KeyedError("HTTP 500 from x")
        c, _ = self.make(read)
        self.assertIsNone(run(c._fetch()))
        self.assertIn("HTTP 500", c._last_reason)

    def test_a_good_read_notes_the_version_and_parses(self):
        from google.transit import gtfs_realtime_pb2 as pb
        f = pb.FeedMessage()
        f.header.gtfs_realtime_version = "2.0"
        c, _ = self.make(lambda client, consumer: (f, None, "v7"))
        snap = run(c._fetch())
        self.assertEqual(snap.observations, [])
        self.assertEqual(c.routes._static_version, "v7")

    def test_the_library_read(self):
        class Client:
            def for_consumer(self, consumer):
                return "P", "U"

            def static_version(self):
                return "V"
        self.assertEqual(self.read_real(Client()), ("P", "U", "V"))

    def read_real(self, client):
        return src.read(client, "intercity")


if __name__ == "__main__":
    unittest.main()
