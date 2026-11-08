"""The coordinator's Entur branches (Intercity SSOT 8.8, backlog 326): one shared client per process, one claim per
config entry in its railroad's codespace, the timetable view handed to the route store, a failure ridden out, a good
read parsed. Run from the repo root: python -m unittest tests.test_entur_coordinator
"""

import asyncio
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

from google.transit import gtfs_realtime_pb2 as pb  # noqa: E402
from saw_livetrack import entur as lib  # noqa: E402

ent = load("sources.entur")
operators = load("operators")
coordinator = load("coordinator")
const = load("const")

run = asyncio.run


def positions(now):
    f = pb.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    e = f.entity.add()
    e.id = "1672-2026-11-07"
    v = e.vehicle
    v.trip.trip_id = "VYG:ServiceJourney:1672_443368-R"
    v.trip.route_id = "VYG:Line:R13"
    v.trip.start_date = "20261107"
    v.vehicle.id = "1672-2026-11-07"
    v.position.latitude, v.position.longitude = 59.80, 10.40
    v.timestamp = int(now) - 10
    return f


class EnturCoordinator(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.hass = _ha_stub.Hass(self.dir)

    def make(self, op_id):
        entry = types.SimpleNamespace(data={"operator": op_id}, options={}, domain=const.DOMAIN)
        return coordinator.IntercityRailCoordinator(self.hass, entry, operators.OPERATORS[op_id])

    def patch_read(self, fn):
        self.addCleanup(setattr, ent, "read", ent.read)
        ent.read = fn

    def test_one_shared_client_one_claim_each_and_the_view(self):
        vy = self.make("vy")
        client = vy._entur_client
        self.assertIsInstance(client, lib.EnturClient)
        self.assertIs(self.hass.data[lib.SHARED_KEY]["client"], client)
        self.assertEqual(client.storage_dir, self.dir)
        view = vy.routes.static_client
        self.assertIsInstance(view, ent.StaticView)
        self.assertIs(view.client, client)
        self.assertEqual(view.codespace, "VYG")
        self.assertEqual(view.keep_letters, ("F", "R", "RE", "RX"))
        self.assertIsInstance(vy._entur, ent.EnturRealtime)
        goa = self.make("go_ahead_norge")
        self.assertIs(goa._entur_client, client)
        self.assertEqual(goa.routes.static_client.codespace, "GOA")
        self.assertEqual(client.claims, {(lib.INTERCITY, "VYG"), (lib.INTERCITY, "GOA")})
        goa.async_release()
        self.assertEqual(client.claims, {(lib.INTERCITY, "VYG")})
        self.assertIsNone(goa.routes.static_client)
        self.assertIn(lib.SHARED_KEY, self.hass.data)
        vy.async_release()
        self.assertNotIn(lib.SHARED_KEY, self.hass.data)
        self.assertIsNone(vy._entur_client)

    def test_a_failure_is_ridden_out(self):
        def read(client, consumer, codespace, view):
            raise lib.RateLimited("HTTP 429 from x")
        self.patch_read(read)
        c = self.make("vy")
        self.assertIsNone(run(c._fetch()))
        self.assertIn("HTTP 429", c._last_reason)

    def test_a_good_read_is_parsed_and_its_version_noted(self):
        seen = []
        now = time.time()

        def read(client, consumer, codespace, view):
            seen.append((client, consumer, codespace, view))
            return positions(now), None, "entur1:v9:2026-11-07"
        self.patch_read(read)
        c = self.make("vy")
        snap = run(c._fetch())
        self.assertEqual([o.train for o in snap.observations], ["1672"])
        self.assertEqual(snap.extras["1672-7"]["route_code"], "R13")
        self.assertEqual(seen, [(c._entur_client, lib.INTERCITY, "VYG", c.routes.static_client)])
        self.assertEqual(c.routes._static_version, "entur1:v9:2026-11-07")


class SjNordCoordinator(unittest.TestCase):
    """SJ Nord's branch (Intercity SSOT 8.8, "SJ NORD"): the same shared client, its SIRI ET, its own view."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir)
        self.hass = _ha_stub.Hass(self.dir)
        self.et = load("sources.entur_et")

    def make(self, op_id):
        entry = types.SimpleNamespace(data={"operator": op_id}, options={}, domain=const.DOMAIN)
        return coordinator.IntercityRailCoordinator(self.hass, entry, operators.OPERATORS[op_id])

    def patch_read(self, fn):
        self.addCleanup(setattr, self.et, "read", self.et.read)
        self.et.read = fn

    def test_the_shared_client_its_claim_and_view(self):
        vy = self.make("vy")
        sjn = self.make("sj_nord")
        self.assertIs(sjn._entur_client, vy._entur_client)
        self.assertIsNone(sjn._entur)
        self.assertIsInstance(sjn._entur_et, self.et.EnturEtRealtime)
        view = sjn.routes.static_client
        self.assertIsInstance(view, ent.StaticView)
        self.assertEqual((view.codespace, view.keep_letters), ("SJN", ("F", "R", "RE", "RX")))
        self.assertEqual(sjn._entur_client.claims, {(lib.INTERCITY, "VYG"), (lib.INTERCITY, "SJN")})
        sjn.async_release()
        self.assertEqual(vy._entur_client.claims, {(lib.INTERCITY, "VYG")})
        self.assertIsNone(sjn.routes.static_client)
        vy.async_release()
        self.assertNotIn(lib.SHARED_KEY, self.hass.data)

    def test_a_failure_is_ridden_out(self):
        def read(client, consumer, codespace, view):
            raise lib.FeedUnavailable("HTTP 503 from x")
        self.patch_read(read)
        c = self.make("sj_nord")
        self.assertIsNone(run(c._fetch()))
        self.assertIn("HTTP 503", c._last_reason)

    def test_a_good_read_is_parsed_and_its_version_noted(self):
        seen = []
        now = time.time()
        journey = {"id": "453:x", "number": "453", "date": "20261108", "line": "R70", "cancelled": False,
                   "calls": [{"order": 1, "stop": "NSR:Quay:1", "name": "A", "recorded": True, "cancelled": False,
                              "aimed_arrival": None, "aimed_departure": now - 60, "expected_arrival": None,
                              "expected_departure": None, "actual_arrival": None, "actual_departure": now - 30},
                             {"order": 2, "stop": "NSR:Quay:2", "name": "B", "recorded": False, "cancelled": False,
                              "aimed_arrival": now + 600, "aimed_departure": now + 660, "expected_arrival": now + 630,
                              "expected_departure": None, "actual_arrival": None, "actual_departure": None}]}

        def read(client, consumer, codespace, view):
            seen.append((client, consumer, codespace, view))
            return [journey], "entur2:v1:2026-11-08"
        self.patch_read(read)
        c = self.make("sj_nord")
        snap = run(c._fetch())
        # No timetable yet: no stop position, so nothing drawn, and said why.
        self.assertEqual((snap.observations, snap.skipped), ([], {"no_stop_position": 1}))
        self.assertEqual(seen, [(c._entur_client, lib.INTERCITY, "SJN", c.routes.static_client)])
        self.assertEqual(c.routes._static_version, "entur2:v1:2026-11-08")


if __name__ == "__main__":
    unittest.main()
