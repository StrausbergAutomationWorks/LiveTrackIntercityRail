"""V/Line's key step, route store and coordinator, with Home Assistant stubbed (tests/_ha_stub.py).
Our branches, never HA's API. Run from the repo root: python -m unittest tests.test_vline_flow
"""

import asyncio
import os
import pathlib
import shutil
import sys
import tempfile
import types
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _ha_stub  # noqa: E402
_ha_stub.install()
from _load import load  # noqa: E402
from test_vline_source import write_zip  # noqa: E402

flow = load("config_flow")
const = load("const")
operators = load("operators")
nsw = load("sources.tfnsw")
src = load("sources.vline")
route_store = load("route_store")
coordinator = load("coordinator")

run = asyncio.run


class KeyDispatch(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.addCleanup(setattr, src, "check_key", src.check_key)
        self.addCleanup(setattr, nsw, "check_key", nsw.check_key)
        src.check_key = lambda c, k: self.calls.append(("vline", c, k))
        nsw.check_key = lambda c, k: self.calls.append(("tfnsw", c, k))

    def flow(self):
        f = flow.IntercityRailConfigFlow()
        f._ids = ()
        f.hass = _ha_stub.Hass(tempfile.gettempdir())
        return f

    def test_vline_asks_for_a_key_and_checks_it_with_its_own_source(self):
        f = self.flow()
        run(f.async_step_user({"region": "AU"}))
        s = run(f.async_step_operator({"operator": "vline"}))
        self.assertEqual((s["type"], s["step_id"], s["placeholders"]["name"]), ("form", "key", "V/Line"))
        s = run(f.async_step_key({"api_key": " abc "}))
        self.assertEqual(s["data"], {"operator": "vline", "api_key": "abc"})
        self.assertEqual(self.calls, [("vline", "intercity", "abc")])

    def test_nsw_still_checks_with_its_own(self):
        f = self.flow()
        run(f.async_step_user({"region": "AU"}))
        run(f.async_step_operator({"operator": "nsw_trainlink"}))
        run(f.async_step_key({"api_key": "abc"}))
        self.assertEqual(self.calls, [("tfnsw", "intercity", "abc")])

    def test_reauth_goes_to_the_same_source(self):
        f = self.flow()
        f._reauth = types.SimpleNamespace(data={"operator": "vline", "api_key": "old"})
        run(f.async_step_reauth_confirm({"api_key": "new"}))
        self.assertEqual(self.calls, [("vline", "intercity", "new")])
        self.assertEqual(f._reauth.data["api_key"], "new")


class FakeClient:
    def __init__(self, path, version):
        self.path, self.version, self.opens = path, version, 0

    def static_version(self):
        return self.version

    def static_path(self):
        self.opens += 1
        return self.path


class RouteStoreStreamed(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.zip = os.path.join(self.dir, "z.zip")
        write_zip(self.zip)
        self.hass = _ha_stub.Hass(self.dir)
        self.op = operators.OPERATORS["vline"]

    def store(self, version="v1"):
        s = route_store.RouteStore(self.hass, None, self.op)
        c = FakeClient(self.zip, version)
        s.static_client = c
        s.note_static(version)
        return s, c

    def test_distilled_from_the_file_with_its_version(self):
        s, _ = self.store()
        run(s.async_refresh())
        g = s.projector.geometry
        self.assertEqual(g["source_version"], "v1")
        self.assertTrue(g["stable_lines"])
        self.assertIn("T1", g["trip_tables"])
        self.assertEqual(g["source"], "shared client")

    def test_no_daily_distill_the_same_version_is_not_stale(self):
        s, c = self.store()
        run(s.async_refresh())
        n = c.opens
        s._next_try = 0
        self.assertFalse(s.due())
        run(s.async_refresh())
        self.assertEqual(c.opens, n)

    def test_a_restart_reads_the_copy(self):
        s, c = self.store()
        run(s.async_refresh())
        s2, _ = self.store()
        run(s2.async_load_cached())
        self.assertIn("T1", s2.projector.geometry["trip_tables"])
        self.assertFalse(s2.due())

    def test_a_new_copy_keeps_running_trains(self):
        s, c = self.store()
        run(s.async_refresh())
        s.projector.estimate("x", "T1", (-37.5, 145.0), 100.0, None, 0.0, 110.0)
        write_zip(self.zip, **{"trips.txt": "route_id,service_id,trip_id,shape_id\nR1,S,NEW,X\n"})
        c.version = "v2"
        s.note_static("v2")
        s._next_try = 0
        run(s.async_refresh())
        self.assertEqual(s.projector.geometry["source_version"], "v2")
        self.assertIn("x", s.projector._state)

    def test_a_timetable_that_will_not_read_keeps_the_copy(self):
        s, c = self.store()
        run(s.async_refresh())
        rows = ("shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n"
                "X,-37.8,145.0,1\nX,-37.0,145.0,2\nY,-37.0,145.0,1\nY,-37.8,145.0,2\nX,-36.0,145.0,3\n")
        write_zip(self.zip, **{"shapes.txt": rows})
        c.version = "v2"
        s.note_static("v2")
        s._next_try = 0
        with self.assertLogs(route_store._LOGGER, "WARNING") as logs:
            run(s.async_refresh())
        self.assertEqual(s.projector.geometry["source_version"], "v1")
        self.assertIn("not contiguous", logs.output[0])

    def test_nsw_does_not_stream(self):
        self.assertFalse(operators.OPERATORS["nsw_trainlink"].gtfs_stream)


class Coordinator(unittest.TestCase):
    def make(self, read=None):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        hass = _ha_stub.Hass(self.dir)
        entry = types.SimpleNamespace(data={"operator": "vline", "api_key": "K"}, options={}, domain=const.DOMAIN)
        if read is not None:
            self.addCleanup(setattr, src, "read", src.read)
            src.read = read
        return coordinator.IntercityRailCoordinator(hass, entry, operators.OPERATORS["vline"]), hass

    def test_registers_its_consumer_and_key(self):
        c, hass = self.make()
        self.assertEqual(c._vic_client.consumers, {"intercity"})
        self.assertEqual(c._vic_client._ring.active(), "K")
        self.assertIsInstance(c.routes.static_client, src.StaticView)
        self.assertEqual(c.routes.static_client.consumer, "intercity")
        self.assertIs(c.routes.static_client.client, c._vic_client)
        self.assertEqual(hass.data["saw_transport_vic_v1"]["consumers"], {"intercity": 1})

    def test_release_unregisters(self):
        c, hass = self.make()
        c.async_release()
        self.assertNotIn("saw_transport_vic_v1", hass.data)
        self.assertIsNone(c.routes.static_client)
        c.async_release()   # idempotent

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

    def test_transport_victorias_errors_are_those_it_catches(self):
        from saw_livetrack import transport_vic
        self.assertIs(transport_vic.AuthRefused, coordinator.AuthRefused)
        self.assertTrue(issubclass(transport_vic.FeedUnavailable, coordinator.KeyedError))

    def test_a_good_read_notes_the_version_and_parses(self):
        from google.transit import gtfs_realtime_pb2 as pb
        f = pb.FeedMessage()
        f.header.gtfs_realtime_version = "2.0"
        c, _ = self.make(lambda client, consumer: (f, None, "v7"))
        snap = run(c._fetch())
        self.assertEqual(snap.observations, [])
        self.assertEqual(c.routes._static_version, "v7")

    def test_nsw_is_not_sent_here(self):
        hass = _ha_stub.Hass(tempfile.gettempdir())
        entry = types.SimpleNamespace(data={"operator": "nsw_trainlink", "api_key": "K"}, options={}, domain=const.DOMAIN)
        c = coordinator.IntercityRailCoordinator(hass, entry, operators.OPERATORS["nsw_trainlink"])
        self.assertIsNone(c._vline)
        self.assertIsNone(c._vic_client)
        c.async_release()


if __name__ == "__main__":
    unittest.main()
