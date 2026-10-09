"""geometry.py: the route, the distilling and the along-route estimate.

Synthetic lines on the equator, where one degree of longitude is KX metres,
so every expected position is arithmetic. Real Amtrak lines: the replay in
test_projection_replay.py.
"""

import csv
import io
import math
import unittest
import zipfile

from _load import load

geometry = load("geometry")
KX = geometry.R * math.pi / 180       # metres per degree on the equator
T0 = 1_791_504_000.0                  # 2026-10-09T00:00:00Z


def deg(m):
    return m / KX


def line(lat=0.0, lon0=0.0, lon1=1.0, n=101):
    return [[lat, lon0 + (lon1 - lon0) * i / (n - 1)] for i in range(n)]


def geo(**extra):
    g = {"v": geometry.GEOMETRY_VERSION,
         "stops": {"A": [0.0, 0.0], "B": [0.0, 0.05], "C": [0.0, 0.2], "D": [0.0, 0.3],
                   "E": [0.0, 0.9], "FAR": [0.03, 0.4]},
         "trains": {"7": ["S1"]},
         "shapes": {"S1": line()}}
    g.update(extra)
    return g


class RouteTests(unittest.TestCase):

    def test_project_and_point_agree(self):
        r = geometry.Route([tuple(p) for p in line()])
        d, off = r.project(0.0009, 0.25)
        self.assertAlmostEqual(d, 0.25 * KX, delta=0.01)
        self.assertAlmostEqual(off, 0.0009 * KX, delta=0.01)
        self.assertEqual(r.point(d), (0.0, 0.25))

    def test_point_is_clamped_to_the_ends(self):
        r = geometry.Route([(0.0, 0.0), (0.0, 1.0)])
        self.assertEqual(r.point(-5), (0.0, 0.0))
        self.assertEqual(r.point(r.length + 5), (0.0, 1.0))

    def test_a_route_needs_two_points(self):
        with self.assertRaises(ValueError):
            geometry.Route([(0.0, 0.0)])


class SimplifyTests(unittest.TestCase):

    def test_straight_points_go_and_a_corner_stays(self):
        pts = [(0.0, i / 10) for i in range(11)] + [(i / 10, 1.0) for i in range(1, 11)]
        out = geometry.simplify(pts, 15.0)
        self.assertEqual(out, [(0.0, 0.0), (0.0, 1.0), (1.0, 1.0)])

    def test_a_bend_wider_than_the_tolerance_stays(self):
        pts = [(0.0, 0.0), (deg(20), 0.5), (0.0, 1.0)]
        self.assertEqual(geometry.simplify(pts, 15.0), pts)
        self.assertEqual(geometry.simplify(pts, 25.0), [pts[0], pts[2]])


def gtfs_zip(feed_info=True):
    def table(rows):
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        for r in rows:
            w.writerow(r)
        return "﻿" + buf.getvalue()     # a BOM, as some feeds write
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("stops.txt", table([["stop_id", "stop_name", "stop_lat", "stop_lon"],
                                       ["CHI", "Chicago", "41.878", "-87.640"],
                                       ["NOPOS", "Nowhere", "", ""]]))
        z.writestr("trips.txt", table([["route_id", "trip_id", "trip_short_name", "shape_id"],
                                       ["r", "t1", "7", "S1"], ["r", "t2", "7", "S1"],
                                       ["r", "t3", "8", "GONE"], ["r", "t4", "", "S1"]]))
        z.writestr("shapes.txt", table([["shape_id", "shape_pt_lat", "shape_pt_lon",
                                         "shape_pt_sequence"],
                                        ["S1", "0.0", "1.0", "3"], ["S1", "0.0", "0.0", "1"],
                                        ["S1", "0.0", "0.5", "2"], ["ONE", "0.0", "0.0", "1"]]))
        if feed_info:
            z.writestr("feed_info.txt", table([["feed_version", "feed_start_date",
                                                "feed_end_date"],
                                               ["20261009", "20261010", "20261016"]]))
    return b.getvalue()


class DistillTests(unittest.TestCase):

    def test_what_the_estimate_needs_and_nothing_else(self):
        d = geometry.distill(gtfs_zip())
        self.assertEqual(d["v"], geometry.GEOMETRY_VERSION)
        self.assertEqual(d["stops"], {"CHI": [41.878, -87.64]})
        # Sorted by sequence, then the collinear middle point simplified away.
        self.assertEqual(d["shapes"], {"S1": [[0.0, 0.0], [0.0, 1.0]]})
        # A number whose only shape is missing, or a trip with no number: gone.
        self.assertEqual(d["trains"], {"7": ["S1"]})
        self.assertEqual((d["feed_version"], d["feed_start_date"], d["feed_end_date"]),
                         ("20261009", "20261010", "20261016"))

    def test_no_feed_info_is_no_dates(self):
        d = geometry.distill(gtfs_zip(feed_info=False))
        self.assertNotIn("feed_end_date", d)


class ProjectorTests(unittest.TestCase):

    def est(self, p, lon, t, stop="C", eta=None, speed=100.0, now=None, lat=0.0,
            tid="7-9", number="7"):
        # eta: kept in the calls as the record of what the source said; the
        # rule no longer reads it (Lee 2026-10-09 15:47: reported speed).
        return p.estimate(tid, number, (lat, lon), t, stop, speed,
                          t if now is None else now)

    def test_at_the_moment_of_a_fix_it_is_the_fix(self):
        p = geometry.Projector(geo())
        self.assertEqual(self.est(p, 0.1, T0, eta=T0 + 600), (0.0, 0.1))

    def test_at_its_reported_speed(self):
        p = geometry.Projector(geo())
        lat, lon = self.est(p, 0.1, T0, speed=10.0, now=T0 + 500)
        self.assertEqual(lat, 0.0)
        self.assertAlmostEqual(lon, 0.1 + deg(5000), places=6)

    def test_amtraks_arrival_estimate_is_not_an_input(self):
        # Due at the stop in 100 s, or long overdue: the same place either way.
        p1, p2 = geometry.Projector(geo()), geometry.Projector(geo())
        self.assertEqual(self.est(p1, 0.1, T0, eta=T0 + 100, speed=2.0, now=T0 + 500),
                         self.est(p2, 0.1, T0, eta=T0 - 900, speed=2.0, now=T0 + 500))

    def test_never_past_its_stop(self):
        p = geometry.Projector(geo())
        self.assertEqual(self.est(p, 0.1, T0, eta=T0 + 100, speed=1000.0, now=T0 + 900),
                         (0.0, 0.2))

    def test_no_speed_holds_the_fix(self):
        for speed in (0.0, None, -5.0):
            p = geometry.Projector(geo())
            self.assertEqual(self.est(p, 0.1, T0, speed=speed, now=T0 + 300), (0.0, 0.1), speed)

    def test_half_an_hour_is_the_horizon(self):
        p = geometry.Projector(geo())
        _, lon = self.est(p, 0.1, T0, stop="E", eta=T0 + 1000, speed=1.0, now=T0 + 5000)
        self.assertAlmostEqual(lon, 0.1 + deg(geometry.MAX_HORIZON_S * 1.0), places=6)

    def test_the_fix_is_moved_never_snapped(self):
        # 100 m north of the line: the estimate stays 100 m north of it.
        p = geometry.Projector(geo())
        lat, lon = self.est(p, 0.1, T0, speed=10.0, now=T0 + 500, lat=0.0009)
        self.assertEqual(lat, 0.0009)
        self.assertAlmostEqual(lon, 0.1 + deg(5000), places=6)

    def test_no_estimate_without_what_it_needs(self):
        p = geometry.Projector(geo())
        self.assertIsNone(self.est(p, 0.1, None, eta=T0 + 600, now=T0 + 60))
        self.assertIsNone(self.est(p, 0.1, T0, stop=None, eta=T0 + 600, now=T0 + 60))
        self.assertIsNone(self.est(p, 0.1, T0, stop="NOPE", eta=T0 + 600, now=T0 + 60))
        self.assertIsNone(self.est(p, 0.1, T0, number="99", eta=T0 + 600, now=T0 + 60))
        self.assertIsNone(self.est(p, 0.1, T0 + 100, eta=T0 + 600, now=T0))  # clock behind

    def test_a_fix_off_its_route_is_published_as_it_is(self):
        p = geometry.Projector(geo())
        self.assertIsNone(self.est(p, 0.1, T0, eta=T0 + 600, now=T0 + 60,
                                   lat=deg(geometry.MAX_FIX_OFF_M + 50)))
        self.assertIsNotNone(self.est(p, 0.1, T0, eta=T0 + 600, now=T0 + 60,
                                      lat=deg(geometry.MAX_FIX_OFF_M - 50)))

    def test_a_stop_off_the_route_is_no_target(self):
        p = geometry.Projector(geo())
        self.assertIsNone(self.est(p, 0.1, T0, stop="FAR", eta=T0 + 600, now=T0 + 60))

    def test_a_stop_behind_the_motion_was_passed(self):
        # Two fixes going east; the source still names a stop behind it.
        p = geometry.Projector(geo())
        self.est(p, 0.1, T0, stop="D", eta=T0 + 3000)
        _, lon = self.est(p, 0.11, T0 + 120, stop="B", eta=T0 + 3000, speed=20.0,
                          now=T0 + 180)
        self.assertAlmostEqual(lon, 0.11 + deg(20.0 * 60), places=6)

    def test_never_backwards_for_a_late_fix(self):
        p = geometry.Projector(geo())
        self.assertAlmostEqual(self.est(p, 0.1, T0, eta=T0 + 1000, now=T0 + 1000)[1], 0.2)
        # The next fix lands 3.3 km behind where the marker already is.
        self.assertEqual(self.est(p, 0.17, T0 + 1000, eta=T0 + 1000), (0.0, 0.2))

    def test_a_jump_back_beyond_5_km_is_published(self):
        p = geometry.Projector(geo())
        self.est(p, 0.1, T0, eta=T0 + 1000, now=T0 + 1000)
        self.assertEqual(self.est(p, 0.14, T0 + 1000, eta=T0 + 1000), (0.0, 0.14))

    def test_forget_drops_the_train(self):
        p = geometry.Projector(geo())
        self.est(p, 0.1, T0, eta=T0 + 1000, now=T0 + 1000)
        p.forget("7-9")
        self.assertEqual(self.est(p, 0.17, T0 + 1000, eta=T0 + 1000), (0.0, 0.17))

    def test_a_train_that_leaves_its_line_is_placed_on_the_one_it_is_on(self):
        # One number, two lines: first seen on S1, next fix 111 km away on S2.
        g = geo(trains={"7": ["S1", "S2"]},
                shapes={"S1": line(), "S2": line(lat=1.0)},
                stops={"C": [0.0, 0.2], "N": [1.0, 0.2]})
        p = geometry.Projector(g)
        self.assertEqual(self.est(p, 0.1, T0, eta=T0 + 1000), (0.0, 0.1))
        est = self.est(p, 0.1, T0 + 60, stop="N", speed=10.0, now=T0 + 560, lat=0.9995)
        self.assertIsNotNone(est)
        self.assertEqual(est[0], 0.9995)
        self.assertGreater(est[1], 0.1 + deg(4900))

    def test_the_nearest_of_the_numbers_lines(self):
        g = geo(trains={"7": ["S1", "S2"]},
                shapes={"S1": line(), "S2": line(lat=1.0)},
                stops={"N": [1.0, 0.2]})
        p = geometry.Projector(g)
        lat, lon = self.est(p, 0.1, T0, stop="N", speed=10.0, now=T0 + 500, lat=0.9995)
        self.assertEqual(lat, 0.9995)
        # On the line at 1 degree north, where a degree of longitude is shorter.
        self.assertAlmostEqual(lon, 0.1 + deg(5000) / math.cos(math.radians(1.0)), places=5)


if __name__ == "__main__":
    unittest.main()
