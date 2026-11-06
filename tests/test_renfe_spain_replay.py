"""Renfe (Spain) on recorded data: Renfe's long-distance feed every 30 s for 40 minutes from 2026-11-06 06:53 Spain
time, cut to 21 train numbers that carry every case the rules were written for (tests/fixtures/
renfe_ld_rt_20261106.json.gz: 03062's two vehicles, 00752's two units, 14123's legs, AVE, Avlo, Alvia, Avant,
MD, Regional, two R trains), through the adapter, Fleet, the look, the lateness and projection.apply, on that day's
timetable as StaticView distills it with the shipped lines, cut to those trips (renfe_ld_geometry_20261106.json.gz).
The figures were measured on the same data by bin\\es324_replay_fixture.py; the whole capture's by
bin\\es324_replay.py. Run from the repo root: python -m unittest tests.test_renfe_spain_replay
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

ld = load("sources.renfe_ld")
base = load("sources.base")
geometry = load("geometry")
projection = load("projection")
operators = load("operators")

FIX = pathlib.Path(__file__).resolve().parent / "fixtures"
GEO = json.loads(gzip.open(FIX / "renfe_ld_geometry_20261106.json.gz").read())
POLLS = json.loads(gzip.open(FIX / "renfe_ld_rt_20261106.json.gz").read())
OP = operators.OPERATORS["renfe_spain"]
REGIONALS = frozenset({"15000", "18120"})


def feed(b64):
    f = pb.FeedMessage()
    f.ParseFromString(base64.b64decode(b64))
    return f


def metres(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(h))


def replay(estimate=True, drop=REGIONALS):
    rt, fleet = ld.RenfeLdRealtime(), Fleet(**dict(OP.fleet))
    proj = geometry.Projector(GEO) if estimate else None
    out = []
    for t, vp, tu in POLLS:
        now = float(t)
        snap = rt.parse(feed(vp), feed(tu), now, GEO, drop)
        res = fleet.update(snap.observations, now, next_stops=snap.next_stops, trip_delays=snap.trip_delays)
        for vid, rec in res["vehicles"].items():
            rec.update({k: v for k, v in (snap.extras.get(vid) or {}).items() if k in base.EXTRA_KEYS})
            rec.update(OP.marker_keys(rec))
            if rec.get("in_service"):
                rec.update(OP.lateness_for(rec))
        if proj is not None:
            projection.apply(proj, snap, res, now, OP.derive_speed, OP.timed_without_fix, OP.timed_after_s)
        out.append((t, snap, res))
    return out


def tracks(run):
    tr = {}
    for t, snap, res in run:
        for o in snap.observations:
            rec = res["vehicles"].get(o.vehicle_id)
            if rec:
                tr.setdefault(o.vehicle_id, []).append((t, (rec["latitude"], rec["longitude"]), (o.lat, o.lon)))
    return tr


class Recorded(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = replay()

    def test_the_data(self):
        self.assertEqual(len(POLLS), 80)
        self.assertEqual(GEO["osm_base"], "2026-11-06T14:01:31Z")

    def test_one_marker_per_run_and_every_timetabled_train_placed(self):
        n = 0
        for _, snap, _ in self.built:
            keys = [o.vehicle_id for o in snap.observations]
            self.assertEqual(len(keys), len(set(keys)))
            for o in snap.observations:
                n += 1
                trip = snap.route_keys[o.vehicle_id]
                self.assertIn(trip, GEO["trains"])
                self.assertIn(o.vehicle_id, snap.next_stops, (o.vehicle_id, trip))
                self.assertIn("toward_hub", snap.extras[o.vehicle_id])
        self.assertGreater(n, 1000)

    def test_renfe_regionals_numbers_are_left_to_it(self):
        drawn = {o.train for _, s, _ in self.built for o in s.observations}
        self.assertFalse(drawn & REGIONALS)
        alone = {o.train for _, s, _ in replay(drop=frozenset()) for o in s.observations}
        self.assertEqual(alone & REGIONALS, REGIONALS)

    def test_03062_is_the_vehicle_at_lleida_on_time(self):
        snap = self.built[0][1]
        o = next(o for o in snap.observations if o.train == "03062")
        self.assertEqual(snap.route_keys[o.vehicle_id], "0306212026-11-05")
        # 4.3 km short of Lleida-Pirineus at 06:53 Spain time (its departure); the other vehicle west of Barcelona.
        self.assertLess(metres((o.lat, o.lon), GEO["stops"]["78400"]), 5000)
        self.assertGreater(sum(s.skipped.get("second_position", 0) for _, s, _ in self.built), 0)

    def test_no_identity_changes(self):
        ids = {}
        for _, snap, _ in self.built:
            for o in snap.observations:
                ids.setdefault(o.train, set()).add(o.vehicle_id)
        self.assertEqual({k: v for k, v in ids.items() if len(v) > 1}, {})

    def test_the_look_and_the_lateness(self):
        _, snap, res = self.built[0]
        for o in snap.observations:
            rec = res["vehicles"][o.vehicle_id]
            fam = snap.extras[o.vehicle_id].get("service_family")
            colour = {"AVE": "#001F4C", "AVE INT": "#001F4C", "AVLO": "#5FCBC6"}.get(fam, "#8A0072")
            self.assertIn(colour, (rec["marker_color"], rec["marker_ring_color"]), (o.train, fam))
            km = snap.extras[o.vehicle_id]["trip_km"]
            t = 10 if km <= 250 * 1.609344 else 15 if km <= 350 * 1.609344 else 20 if km <= 450 * 1.609344 \
                else 25 if km <= 550 * 1.609344 else 30
            self.assertEqual((rec["late_threshold_min"], rec["very_late_threshold_min"]), (t, 2 * t), o.train)

    def test_on_their_lines(self):
        for _, snap, res in self.built:
            for o in snap.observations:
                rec = res["vehicles"][o.vehicle_id]
                if rec.get("position_source") == "estimated":
                    self.assertIn("fix_latitude", rec)

    def test_no_drawn_jump_the_fix_did_not_make(self):
        for vid, rows in tracks(self.built).items():
            for a, b in zip(rows, rows[1:]):
                if b[0] - a[0] <= 60 and metres(a[2], b[2]) <= 5000:
                    self.assertLess(metres(a[1], b[1]), 5000, (vid, b[0]))

    def test_the_estimate_is_no_worse_than_holding(self):
        def gaps(run):
            out = []
            for rows in tracks(run).values():
                for a, b in zip(rows, rows[1:]):
                    if b[0] - a[0] <= 60 and metres(a[2], b[2]) > 50:
                        out.append(metres(a[1], b[2]))
            return sorted(out)
        built, held = gaps(self.built), gaps(replay(estimate=False))
        self.assertEqual(len(built), len(held))
        q = lambda v, f: v[int(f * (len(v) - 1))]
        self.assertLessEqual(q(built, .5), q(held, .5))
        self.assertLessEqual(q(built, .9), q(held, .9))


if __name__ == "__main__":
    unittest.main()
