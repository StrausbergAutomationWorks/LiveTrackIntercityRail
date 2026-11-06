"""Renfe's regionals on recorded data: the shared client's intercity view polled every 30 s on 2026-11-06 from
05:2x Spain time (tests/fixtures/renfe_rt_20261106.json.gz) through the adapter, Fleet, the look and
projection.apply, on that day's timetable as StaticView distills it (renfe_regionals_geometry_20261106.json.gz).
Every figure asserted here was measured on the same data by bin\\es294_replay.py. Run from the repo root:
python -m unittest tests.test_renfe_replay
"""

import base64
import gzip
import json
import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _load import load  # noqa: E402

from google.transit import gtfs_realtime_pb2 as pb  # noqa: E402
from saw_livetrack.gtfs import Fleet  # noqa: E402

src = load("sources.renfe")
base = load("sources.base")
geometry = load("geometry")
projection = load("projection")
operators = load("operators")

FIX = pathlib.Path(__file__).resolve().parent / "fixtures"
GEO = json.loads(gzip.open(FIX / "renfe_regionals_geometry_20261106.json.gz").read())
POLLS = json.loads(gzip.open(FIX / "renfe_rt_20261106.json.gz").read())
OP = operators.OPERATORS["renfe_regionals_catalunya"]


def feed(b64):
    if b64 is None:
        return None
    f = pb.FeedMessage()
    f.ParseFromString(base64.b64decode(b64))
    return f


def metres(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(h))


def replay(derive=True, timed=True):
    rt, fleet, proj = src.RenfeRealtime("Barcelona"), Fleet(**dict(OP.fleet)), geometry.Projector(GEO)
    out = []
    for t, vp, tu in POLLS:
        now = t + 5.0
        snap = rt.parse(feed(vp), feed(tu), now, GEO)
        res = fleet.update(snap.observations, now, next_stops=snap.next_stops, trip_delays=snap.trip_delays)
        for vid, rec in res["vehicles"].items():
            rec.update({k: v for k, v in (snap.extras.get(vid) or {}).items() if k in base.EXTRA_KEYS})
            rec.update(OP.marker_keys(rec))
        projection.apply(proj, snap, res, now, derive, timed, OP.timed_after_s)
        out.append((snap, res))
    return out


class Recorded(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = replay()

    def test_the_timetable(self):
        self.assertEqual(len(GEO["trains"]), 401)
        self.assertEqual(sorted(set(GEO["trip_numbers"].values())), ["R11", "R13", "R14", "R15", "R16", "R17"])
        self.assertEqual(len(GEO["trip_dates"]), 401)

    def test_every_train_is_in_the_timetable_with_a_next_stop_and_a_direction(self):
        n = 0
        for snap, _ in self.built:
            for o in snap.observations:
                n += 1
                self.assertIn(snap.route_keys[o.vehicle_id], GEO["trains"])
                self.assertIn(o.vehicle_id, snap.next_stops)
                self.assertIn("toward_hub", snap.extras[o.vehicle_id])
        self.assertGreater(n, 300)

    def test_one_marker_per_run(self):
        for snap, _ in self.built:
            keys = [o.vehicle_id for o in snap.observations]
            self.assertEqual(len(keys), len(set(keys)))

    def test_the_label_is_the_vehicles_number(self):
        seen = {(snap.route_keys[o.vehicle_id], o.train) for snap, _ in self.built for o in snap.observations}
        self.assertIn(("5109V30530R15", "15030"), seen)
        self.assertIn(("5109V15000R15", "15000"), seen)

    def test_reus_to_tarragona_is_timed(self):
        # R15 15000 stood on Reus's coordinates until 05:58 and appeared on Tarragona's (13,973 m on)
        # at 05:58:47: held, the marker jumps that far; timed, it is near Tarragona when the fix comes.
        def gap(run):
            prev = None
            for snap, res in run:
                o = next((o for o in snap.observations if o.vehicle_id == "15000-6"), None)
                if o is None:
                    continue
                if prev is not None and metres(prev[1], (o.lat, o.lon)) > 5000:
                    return metres(prev[0], (o.lat, o.lon))
                rec = res["vehicles"]["15000-6"]
                prev = ((rec["latitude"], rec["longitude"]), (o.lat, o.lon))
            return None
        held, built = gap(replay(False, False)), gap(self.built)
        self.assertGreater(held, 13000)
        self.assertLess(built, 3000)


if __name__ == "__main__":
    unittest.main()
