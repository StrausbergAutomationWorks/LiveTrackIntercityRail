"""projection.apply: what a published train carries when it is moved along its
route, and the estimate on REAL rows against Amtrak's own lines. No HA.

Replay: tests/fixtures/amtraker_amtrak_20261009.json.gz (21 polls 120 s
apart) through the adapter, Fleet and projection.apply at 30 s steps, as the
coordinator polls, against tests/fixtures/amtrak_geometry_20261009.json.gz
(Amtrak's GTFS of 2026-10-09 distilled by geometry.distill, cut to the
fixture's trains; fixtures/README.md).
"""

import datetime as dt
import gzip
import json
import math
import pathlib
import statistics
import unittest

from _load import load

from saw_livetrack.gtfs import Fleet
from saw_livetrack.gtfs.realtime import Obs

amtraker = load("sources.amtraker")
sources_base = load("sources.base")
geometry = load("geometry")
projection = load("projection")
operators = load("operators")

FIX = pathlib.Path(__file__).parent / "fixtures"
ROWS = json.loads(gzip.open(FIX / "amtraker_amtrak_20261009.json.gz").read().decode("utf-8"))
GEOMETRY = json.loads(gzip.open(FIX / "amtrak_geometry_20261009.json.gz").read().decode("utf-8"))
POLLS = [(dt.datetime.strptime(p["t"], "%Y%m%dT%H%M%SZ")
          .replace(tzinfo=dt.timezone.utc).timestamp(), p["rows"])
         for p in ROWS["polls"]]
AMTRAK = operators.OPERATORS["amtrak"]
T0 = 1_791_504_000.0
UTC = dt.timezone.utc


def km(a, b):
    """Equirectangular distance, km: plenty at these separations."""
    k = math.cos(math.radians((a[0] + b[0]) / 2))
    return math.hypot((a[0] - b[0]) * 111.195, (a[1] - b[1]) * 111.195 * k)


def snap_of(obs, stop="C", eta=None, kmh=360.0):
    s = sources_base.Snapshot(observations=list(obs))
    for o in obs:
        s.next_stops[o.vehicle_id] = ("Somewhere", eta)
        s.stop_codes[o.vehicle_id] = stop
        if kmh is not None:
            s.extras[o.vehicle_id] = {"speed_kmh": kmh}
    return s


def obs(lon, t, vid="7-9", train="7"):
    return Obs(vehicle_id=vid, lat=0.0, lon=lon,
               observed_at=dt.datetime.fromtimestamp(t, UTC), in_service=True,
               train=train, line=None, reported_course=None, trip_id=vid)


def rec(lon, **extra):
    return {"vehicle_id": "7-9", "latitude": 0.0, "longitude": lon, "in_service": True,
            "previous_latitude": 0.0, "previous_longitude": lon - 0.01,
            "previous_observed_at": "x", "segment_duration_s": 120.0, **extra}


def line_geo():
    return {"v": 1, "stops": {"C": [0.0, 0.2]}, "trains": {"7": ["S1"]},
            "shapes": {"S1": [[0.0, 0.0], [0.0, 1.0]]}}


class ApplyTests(unittest.TestCase):

    def test_an_estimate_says_so_and_keeps_the_fix(self):
        p = geometry.Projector(line_geo())
        res = {"vehicles": {"7-9": rec(0.1)}, "departed": []}
        counts = projection.apply(p, snap_of([obs(0.1, T0)], eta=T0 + 1000, kmh=36.0),
                                  res, T0 + 500)
        r = res["vehicles"]["7-9"]
        self.assertEqual(counts, {"estimated": 1, "observed": 0})
        self.assertEqual(r["position_source"], "estimated")
        self.assertEqual((r["fix_latitude"], r["fix_longitude"]), (0.0, 0.1))
        # 36 km/h is 10 m/s: 5 km along in 500 s.
        self.assertAlmostEqual(r["longitude"], 0.1 + 5000 / (geometry.R * math.pi / 180), places=6)
        for k in projection.SEGMENT_KEYS:
            self.assertNotIn(k, r)

    def test_at_its_fix_a_train_is_observed_and_keeps_its_segment(self):
        p = geometry.Projector(line_geo())
        res = {"vehicles": {"7-9": rec(0.1)}, "departed": []}
        counts = projection.apply(p, snap_of([obs(0.1, T0)], eta=T0 + 1000), res, T0)
        r = res["vehicles"]["7-9"]
        self.assertEqual(counts, {"estimated": 0, "observed": 1})
        self.assertEqual(r["position_source"], "observed")
        self.assertNotIn("fix_latitude", r)
        self.assertIn("previous_latitude", r)

    def test_no_lines_yet_publishes_every_fix_as_observed(self):
        res = {"vehicles": {"7-9": rec(0.1)}, "departed": []}
        projection.apply(None, snap_of([obs(0.1, T0)], eta=T0 + 1000), res, T0 + 500)
        self.assertEqual(res["vehicles"]["7-9"]["longitude"], 0.1)
        self.assertEqual(res["vehicles"]["7-9"]["position_source"], "observed")

    def test_a_position_fleet_chose_is_left_alone(self):
        p = geometry.Projector(line_geo())
        res = {"vehicles": {"7-9": rec(0.09)}, "departed": []}
        projection.apply(p, snap_of([obs(0.1, T0)], eta=T0 + 1000), res, T0 + 500)
        self.assertEqual(res["vehicles"]["7-9"]["longitude"], 0.09)

    def test_a_departed_train_is_forgotten(self):
        p = geometry.Projector(line_geo())
        projection.apply(p, snap_of([obs(0.1, T0)], eta=T0 + 1000),
                         {"vehicles": {"7-9": rec(0.1)}, "departed": []}, T0 + 1000)
        self.assertIn("7-9", p._state)
        projection.apply(p, snap_of([]), {"vehicles": {}, "departed": ["7-9"]}, T0 + 1030)
        self.assertNotIn("7-9", p._state)

    def test_a_moving_train_faces_its_line(self):
        p = geometry.Projector(line_geo())
        res = {"vehicles": {"7-9": rec(0.1, course_deg=37.0, icon_rotation_deg=37.0,
                                       icon_rotation_basis="course")}, "departed": []}
        projection.apply(p, snap_of([obs(0.1, T0)], kmh=36.0), res, T0 + 60)
        r = res["vehicles"]["7-9"]
        self.assertEqual((r["course_deg"], r["icon_rotation_deg"], r["icon_rotation_basis"]),
                         (90.0, 90.0, "course"))

    def test_a_train_at_rest_holds_its_lines_bearing_and_has_no_course(self):
        p = geometry.Projector(line_geo())
        res = {"vehicles": {"7-9": rec(0.1, course_deg=37.0)}, "departed": []}
        projection.apply(p, snap_of([obs(0.1, T0)], kmh=0.0), res, T0 + 60)
        r = res["vehicles"]["7-9"]
        self.assertNotIn("course_deg", r)
        self.assertEqual((r["icon_rotation_deg"], r["icon_rotation_basis"]), (90.0, "held"))
        self.assertEqual(r["position_source"], "observed")

    def test_a_moved_train_carries_its_track_path(self):
        p = geometry.Projector(line_geo())
        projection.apply(p, snap_of([obs(0.1, T0)], kmh=36.0),
                         {"vehicles": {"7-9": rec(0.1)}, "departed": []}, T0 + 30)
        res = {"vehicles": {"7-9": rec(0.1)}, "departed": []}
        projection.apply(p, snap_of([obs(0.1, T0)], kmh=36.0), res, T0 + 60)
        r = res["vehicles"]["7-9"]
        self.assertEqual(r["track_path"][-1], [r["latitude"], r["longitude"]])
        self.assertEqual(len(r["track_path"]), 2)            # a straight line: no vertex between

    def test_no_line_keeps_fleets_course(self):
        res = {"vehicles": {"7-9": rec(0.1, course_deg=37.0, icon_rotation_deg=37.0)}, "departed": []}
        projection.apply(None, snap_of([obs(0.1, T0)]), res, T0 + 60)
        self.assertEqual(res["vehicles"]["7-9"]["course_deg"], 37.0)

    def test_no_speed_no_move(self):
        p = geometry.Projector(line_geo())
        res = {"vehicles": {"7-9": rec(0.1)}, "departed": []}
        projection.apply(p, snap_of([obs(0.1, T0)], eta=T0 + 1000, kmh=None), res, T0 + 500)
        self.assertEqual(res["vehicles"]["7-9"]["position_source"], "observed")


def replay(step_s=30):
    """Every poll through adapter, Fleet and apply at step_s, as the box does.
    Returns (published records by time, the Fleet-only fix by id and time)."""
    fleet = Fleet(**dict(AMTRAK.fleet))
    proj = geometry.Projector(GEOMETRY)
    frames = []
    for i, (t, rows) in enumerate(POLLS):
        end = POLLS[i + 1][0] if i + 1 < len(POLLS) else t + 1
        now = t
        while now < end:
            snap = amtraker.parse(rows, now)
            if snap is not None:
                res = fleet.update(snap.observations, now, next_stops=snap.next_stops,
                                   trip_delays=snap.trip_delays)
                for vid, r in res["vehicles"].items():
                    r.update((snap.extras.get(vid) or {}))
                counts = projection.apply(proj, snap, res, now)
                frames.append((now, snap, res, counts))
            now += step_s
    return frames


class ReplayTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.frames = replay()

    def test_every_published_train_says_where_its_position_came_from(self):
        for _, snap, res, _ in self.frames:
            fixes = {o.vehicle_id: (o.lat, o.lon) for o in snap.observations}
            for vid, r in res["vehicles"].items():
                self.assertIn(r["position_source"], ("observed", "estimated"))
                if r["position_source"] == "estimated":
                    self.assertEqual((r["fix_latitude"], r["fix_longitude"]), fixes[vid])
                    self.assertNotIn("previous_latitude", r)
                else:
                    self.assertEqual((r["latitude"], r["longitude"]), fixes[vid])

    def test_a_moved_train_faces_the_line_it_moves_along(self):
        checked = 0
        for _, snap, res, _ in self.frames:
            kmh = {vid: (snap.extras.get(vid) or {}).get("speed_kmh") for vid in res["vehicles"]}
            for vid, r in res["vehicles"].items():
                if r["position_source"] != "estimated":
                    continue
                self.assertIn("icon_rotation_deg", r, vid)
                if (kmh[vid] or 0) >= projection.MOVING_KMH:
                    self.assertEqual(r["icon_rotation_basis"], "course")
                    self.assertEqual(r["course_deg"], r["icon_rotation_deg"])
                else:
                    self.assertEqual(r["icon_rotation_basis"], "held")
                    self.assertNotIn("course_deg", r)
                checked += 1
        self.assertGreater(checked, 500)

    def test_a_moved_train_carries_the_line_it_moved_along(self):
        # Measured 2026-10-09 (bin\ltir_path_measure.txt): 495 of 580
        # estimated records, at most 15 points, every one ending where drawn.
        with_path = 0
        for _, _, res, _ in self.frames:
            for r in res["vehicles"].values():
                p = r.get("track_path")
                if p:
                    with_path += 1
                    self.assertEqual(p[-1], [r["latitude"], r["longitude"]])
                    self.assertLessEqual(len(p), 50)
        self.assertGreater(with_path, 450)

    def test_most_moving_trains_are_moved(self):
        est = sum(c["estimated"] for *_, c in self.frames)
        obs_ = sum(c["observed"] for *_, c in self.frames)
        self.assertGreater(est, MEASURED_ESTIMATED_FLOOR, (est, obs_))

    def errors(self):
        """For each new fix of a train: (km from the position drawn just
        before it arrived, km from simply holding the last fix)."""
        drawn, last_fix, out = {}, {}, []
        for _, snap, res, _ in self.frames:
            for o in snap.observations:
                vid, fix = o.vehicle_id, (o.lat, o.lon)
                if vid in last_fix and fix != last_fix[vid] and vid in drawn:
                    out.append((km(drawn[vid], fix), km(last_fix[vid], fix)))
                last_fix[vid] = fix
            for vid, r in res["vehicles"].items():
                drawn[vid] = (r["latitude"], r["longitude"])
        return out

    def test_closer_to_the_next_fix_than_holding_the_last(self):
        errs = self.errors()
        self.assertGreater(len(errs), 60)
        drawn = statistics.median(e for e, _ in errs)
        held = statistics.median(h for _, h in errs)
        self.assertLess(drawn, held / 2, (drawn, held))
        self.assertLess(drawn, MEASURED_P50_KM_CEILING, drawn)


# Measured on these fixtures 2026-10-09 (bin\ltir_proj_measure.txt), the
# speed-only rule: 575 records estimated and 65 observed over 77 polls; 74 new
# fixes, the drawn position p50 2.20 km from each (p90 7.08), holding the last
# fix p50 5.05 km. (The ETA-and-speed rule of 4a2e469: p50 1.91, p90 6.33.)
# Set with a margin; a change past either is a change in the estimate.
MEASURED_ESTIMATED_FLOOR = 500
MEASURED_P50_KM_CEILING = 2.5


if __name__ == "__main__":
    unittest.main()
