"""Brightline's own GTFS-Realtime (sources/brightline_rt.py), then Fleet and
the along-route estimate on REAL polls. No Home Assistant.

tests/fixtures/brightline_rt_20261009.json.gz: 180 polls 60 s apart,
16:20-19:19Z on 2026-10-09 (round 4), the raw protobuf files as the feed
served them. It holds trips leaving Miami and Orlando, fixes frozen on parked
equipment, and locomotive ids that sat on two and three trips (AAFL_121 on
5327, 5338 and 5340). tests/fixtures/brightline_geometry_20261003.json.gz:
Brightline's GTFS of 2026-10-03 distilled by geometry.distill. Both:
fixtures/README.md.
"""

import base64
import datetime as dt
import gzip
import json
import math
import pathlib
import statistics
import unittest

from _load import load

from google.transit import gtfs_realtime_pb2 as pb
from saw_livetrack.gtfs import Fleet, decode

bl = load("sources.brightline_rt")
sources_base = load("sources.base")
geometry = load("geometry")
projection = load("projection")
operators = load("operators")
brightline_op = load("operators.brightline")

FIX = pathlib.Path(__file__).parent / "fixtures"
RT = json.loads(gzip.open(FIX / "brightline_rt_20261009.json.gz").read().decode("utf-8"))
GEOMETRY = json.loads(gzip.open(FIX / "brightline_geometry_20261003.json.gz").read().decode("utf-8"))
NAMES = GEOMETRY["stop_names"]


def _t(stamp):
    return (dt.datetime.strptime(stamp, "%Y%m%dT%H%M%SZ")
            .replace(tzinfo=dt.timezone.utc).timestamp())


POLLS = [(_t(p["t"]), decode(base64.b64decode(p["vp"])), decode(base64.b64decode(p["tu"])))
         for p in RT["polls"]]
BRIGHTLINE = operators.OPERATORS["brightline"]
T0 = 1_791_504_000.0
TRIP = "5740_BL_63_1"
DAY = "20261003"


def feed(vehicles=(), trips=()):
    """A FeedMessage. vehicles: (trip_id, start_date, lat, lon, fix time,
    vehicle id); trips: (trip_id, start_date, [(stop, arr, dep, delay)])."""
    f = pb.FeedMessage()
    f.header.gtfs_realtime_version = "2.0"
    for trip, sd, lat, lon, when, vid in vehicles:
        e = f.entity.add()
        e.id = trip or "x"
        v = e.vehicle
        if trip is not None:
            v.trip.trip_id = trip
            if sd:
                v.trip.start_date = sd
        v.position.latitude, v.position.longitude = lat, lon
        if when is not None:
            v.timestamp = int(when)
        if vid:
            v.vehicle.id = vid
    for trip, sd, stops in trips:
        e = f.entity.add()
        e.id = "tu" + trip
        tu = e.trip_update
        tu.trip.trip_id, tu.trip.start_date = trip, sd
        for stop, arr, dep, delay in stops:
            s = tu.stop_time_update.add()
            s.stop_id = stop
            if arr is not None:
                s.arrival.time = int(arr)
                if delay is not None:
                    s.arrival.delay = delay
            if dep is not None:
                s.departure.time = int(dep)
    return f


def one(when=T0 - 58, trip=TRIP, sd=DAY, vid="AAFL_121", lat=25.9, lon=-80.15):
    return (trip, sd, lat, lon, when, vid)


def stops(origin_dep, nxt_arr, delay=120):
    return [("EKW", None, origin_dep, None), ("AVE", nxt_arr, nxt_arr + 60, delay),
            ("FBT", nxt_arr + 900, nxt_arr + 960, delay), ("MCO", nxt_arr + 9000, None, delay)]


class IdentityTests(unittest.TestCase):

    def test_number_and_day_of_the_service_date(self):
        self.assertEqual(bl.identity(TRIP, "20261003"), "5740-3")
        self.assertEqual(bl.identity(TRIP, "20261031"), "5740-31")

    def test_no_usable_date_is_the_bare_number(self):
        for sd in (None, "", "2026103", "2026-10-03"):
            self.assertEqual(bl.identity(TRIP, sd), "5740", sd)

    def test_no_number_no_identity(self):
        for trip in ("", "BL_63_1", "57a0_BL"):
            self.assertIsNone(bl.identity(trip, DAY), trip)


class ParseTests(unittest.TestCase):

    def parse(self, vp, tu=None, now=T0, names=NAMES, rt=None):
        return (rt or bl.BrightlineRealtime()).parse(vp, tu, now, names)

    def test_no_positions_is_an_outage_and_an_empty_feed_is_not(self):
        self.assertIsNone(self.parse(None))
        snap = self.parse(feed())
        self.assertIsNotNone(snap)
        self.assertEqual(snap.observations, [])

    def test_a_fresh_fix_is_the_trip_labelled_with_its_number(self):
        snap = self.parse(feed([one()]), feed(trips=[(TRIP, DAY, stops(T0 - 600, T0 + 300))]))
        (o,) = snap.observations
        self.assertEqual((o.vehicle_id, o.trip_id, o.train), ("5740-3", "5740-3", "5740"))
        self.assertTrue(o.in_service)
        self.assertIsNone(o.reported_course)
        self.assertEqual(o.observed_at.timestamp(), T0 - 58)
        self.assertEqual(snap.extras["5740-3"], {"line_name": "Brightline", "destination": "MCO"})
        self.assertNotIn("speed_kmh", snap.extras["5740-3"])

    def test_next_stop_name_time_and_delay(self):
        snap = self.parse(feed([one()]), feed(trips=[(TRIP, DAY, stops(T0 - 600, T0 + 300, delay=180))]))
        self.assertEqual(snap.next_stops["5740-3"], ("Aventura", T0 + 300))
        self.assertEqual(snap.stop_codes["5740-3"], "AVE")
        self.assertEqual(snap.trip_delays["5740-3"], 180)

    def test_standing_at_its_origin_the_next_stop_is_the_second(self):
        snap = self.parse(feed([one()]), feed(trips=[(TRIP, DAY, stops(T0 + 300, T0 + 900))]))
        self.assertEqual(snap.stop_codes["5740-3"], "AVE")

    def test_a_passed_stop_is_never_next(self):
        snap = self.parse(feed([one()]), feed(trips=[(TRIP, DAY, stops(T0 - 1200, T0 - 600))]))
        self.assertEqual(snap.stop_codes["5740-3"], "FBT")
        snap = self.parse(feed([one()]), feed(trips=[(TRIP, DAY, stops(T0 - 20000, T0 - 19000))]))
        self.assertNotIn("5740-3", snap.stop_codes)
        self.assertNotIn("5740-3", snap.next_stops)

    def test_no_name_yet_no_next_stop_but_the_code_is_kept(self):
        snap = self.parse(feed([one()]), feed(trips=[(TRIP, DAY, stops(T0 - 600, T0 + 300))]), names={})
        self.assertEqual(snap.stop_codes["5740-3"], "AVE")
        self.assertNotIn("5740-3", snap.next_stops)

    def test_without_trip_updates_the_train_is_still_published(self):
        snap = self.parse(feed([one()]), None)
        self.assertEqual([o.vehicle_id for o in snap.observations], ["5740-3"])
        self.assertEqual(snap.extras["5740-3"], {"line_name": "Brightline"})
        self.assertEqual(snap.next_stops, {})

    def test_one_locomotive_on_two_trips_is_two_trains(self):
        # Round 4: AAFL_121 on 5338 and 5340 at two live positions 45 km apart.
        vp = feed([one(trip="5338_BL_1_1", sd="20261009", lat=26.0),
                   one(trip="5340_BL_2_1", sd="20261009", lat=26.4)])
        snap = self.parse(vp)
        self.assertEqual(sorted(o.vehicle_id for o in snap.observations), ["5338-9", "5340-9"])

    def test_a_trip_twice_keeps_the_first(self):
        snap = self.parse(feed([one(lat=26.0), one(lat=26.5, vid="AAFL_117")]))
        self.assertEqual([o.lat for o in snap.observations], [26.0])
        self.assertEqual(snap.skipped, {"duplicate": 1})

    def test_what_is_skipped_says_why(self):
        vp = feed([one(trip=None), one(trip="BL_63_1"), one(trip="5741_BL_1_1", lat=0.0, lon=0.0)])
        snap = self.parse(vp, feed(trips=[("5999_BL_9_1", DAY, stops(T0 - 600, T0 + 300))]))
        self.assertEqual(snap.observations, [])
        self.assertEqual(snap.skipped, {"no_trip": 1, "no_trip_number": 1,
                                        "no_position": 1, "no_vehicle": 1})


class StaleFixTests(unittest.TestCase):
    """Lee 2026-10-10, rule 2: a fix older than MAX_AGE_S is not used; the
    trip's last usable fix is held HOLD_S, then it has no marker."""

    def test_the_limits_are_the_measured_ones(self):
        self.assertEqual((bl.MAX_AGE_S, bl.HOLD_S), (300.0, 600.0))

    def test_a_fix_just_inside_the_age_is_used(self):
        rt = bl.BrightlineRealtime()
        snap = rt.parse(feed([one(when=T0 - 300)]), None, T0, NAMES)
        self.assertEqual(len(snap.observations), 1)
        snap = bl.BrightlineRealtime().parse(feed([one(when=T0 - 301)]), None, T0, NAMES)
        self.assertEqual((snap.observations, snap.skipped), ([], {"stale": 1}))

    def test_a_stale_fix_holds_the_last_usable_one_then_drops_it(self):
        rt = bl.BrightlineRealtime()
        good = rt.parse(feed([one(when=T0 - 58, lat=26.0)]), None, T0, NAMES).observations[0]
        # The feed froze: the same trip, a fix now 458 s old, at a new spot.
        snap = rt.parse(feed([one(when=T0 - 58, lat=26.3)]), None, T0 + 400, NAMES)
        self.assertEqual(snap.observations, [good])
        self.assertEqual(snap.skipped, {"stale_held": 1})
        snap = rt.parse(feed([one(when=T0 - 58)]), None, T0 + 601, NAMES)
        self.assertEqual((snap.observations, snap.skipped), ([], {"stale": 1}))

    def test_a_fresh_fix_after_a_stale_spell_is_used(self):
        rt = bl.BrightlineRealtime()
        rt.parse(feed([one(when=T0 - 58)]), None, T0, NAMES)
        rt.parse(feed([one(when=T0 - 58)]), None, T0 + 900, NAMES)
        snap = rt.parse(feed([one(when=T0 + 900, lat=26.4)]), None, T0 + 960, NAMES)
        self.assertEqual([o.lat for o in snap.observations], [26.4])
        self.assertEqual(snap.skipped, {})

    def test_a_fix_with_no_time_is_not_usable(self):
        snap = bl.BrightlineRealtime().parse(feed([one(when=None)]), None, T0, NAMES)
        self.assertEqual((snap.observations, snap.skipped), ([], {"stale": 1}))

    def test_a_trip_gone_from_the_feed_is_forgotten(self):
        rt = bl.BrightlineRealtime()
        rt.parse(feed([one()]), None, T0, NAMES)
        rt.parse(feed(), None, T0 + 601, NAMES)
        self.assertEqual(rt._good, {})


def parse_all():
    rt = bl.BrightlineRealtime()
    return [(t, vp, tu, rt.parse(vp, tu, t, NAMES)) for t, vp, tu in POLLS]


class RealFeedTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parsed = parse_all()

    def test_the_fixture_is_what_it_says(self):
        self.assertEqual(len(POLLS), 180)
        self.assertEqual([b - a for (a, *_), (b, *_) in zip(POLLS, POLLS[1:])], [60.0] * 179)

    def test_every_train_is_its_trip_labelled_with_its_number(self):
        ids = set()
        for t, vp, _, snap in self.parsed:
            seen = [o.vehicle_id for o in snap.observations]
            self.assertEqual(len(seen), len(set(seen)))
            trips = {bl.identity(e.vehicle.trip.trip_id, e.vehicle.trip.start_date)
                     for e in vp.entity if e.HasField("vehicle")}
            for o in snap.observations:
                self.assertIn(o.vehicle_id, trips)
                self.assertEqual(o.vehicle_id, f"{o.train}-9")
            ids.update(seen)
        # Measured on this fixture: 15 trips.
        self.assertEqual(len(ids), 15)

    def test_a_locomotive_on_two_trips_never_merges_them(self):
        # Round 4: one vehicle.id on two trips in the same poll.
        both = 0
        for _, vp, _, snap in self.parsed:
            by_loco = {}
            for e in vp.entity:
                if e.HasField("vehicle") and e.vehicle.vehicle.id:
                    by_loco.setdefault(e.vehicle.vehicle.id, set()).add(
                        bl.identity(e.vehicle.trip.trip_id, e.vehicle.trip.start_date))
            published = {o.vehicle_id for o in snap.observations}
            for trips in by_loco.values():
                if len(trips) > 1 and trips <= published:
                    both += 1
        self.assertGreater(both, 0)

    def test_no_fix_used_is_older_than_the_rules_allow(self):
        for t, _, _, snap in self.parsed:
            for o in snap.observations:
                self.assertLessEqual(t - o.observed_at.timestamp(), bl.MAX_AGE_S + bl.HOLD_S)

    def test_frozen_fixes_are_refused(self):
        # Parked equipment (round 4: 5342 frozen 91 minutes) and its like.
        skipped = {}
        for *_, snap in self.parsed:
            for k, n in snap.skipped.items():
                skipped[k] = skipped.get(k, 0) + n
        self.assertGreater(skipped.get("stale", 0), 0)
        self.assertGreater(skipped.get("stale_held", 0), 0)

    def test_every_destination_has_its_colour(self):
        dests = set()
        for *_, snap in self.parsed:
            for extra in snap.extras.values():
                if "destination" in extra:
                    dests.add(extra["destination"])
        self.assertTrue(dests)
        self.assertLessEqual(dests, set(brightline_op.DESTINATION_COLOURS))

    def test_the_next_stop_is_ahead_and_never_the_origin(self):
        checked = 0
        for t, _, tu, snap in self.parsed:
            rows = {bl.identity(e.trip_update.trip.trip_id, e.trip_update.trip.start_date):
                    bl._stop_rows(e.trip_update) for e in tu.entity if e.HasField("trip_update")}
            for vid, code in snap.stop_codes.items():
                r = rows[vid]
                i = [x[0] for x in r].index(code)
                self.assertGreater(i, 0, vid)
                leave = r[i][2] if r[i][2] is not None else r[i][1]
                self.assertTrue(leave is None or leave > t, vid)
                self.assertEqual(snap.next_stops[vid][0], NAMES[code])
                checked += 1
        self.assertGreater(checked, 1000)


def km(a, b):
    k = math.cos(math.radians((a[0] + b[0]) / 2))
    return math.hypot((a[0] - b[0]) * 111.195, (a[1] - b[1]) * 111.195 * k)


def replay():
    """Every poll through the adapter, Fleet, the coordinator's extras and
    styling, and projection.apply with a derived speed, as the box runs it."""
    rt = bl.BrightlineRealtime()
    fleet = Fleet(**dict(BRIGHTLINE.fleet))
    proj = geometry.Projector(GEOMETRY)
    frames = []
    for t, vp, tu in POLLS:
        snap = rt.parse(vp, tu, t, NAMES)
        res = fleet.update(snap.observations, t, next_stops=snap.next_stops,
                           trip_delays=snap.trip_delays)
        for vid, rec in res["vehicles"].items():
            extra = snap.extras.get(vid) or {}
            rec.update({k: v for k, v in extra.items() if k in sources_base.EXTRA_KEYS})
            rec.update(BRIGHTLINE.marker_keys(rec))
        counts = projection.apply(proj, snap, res, t, BRIGHTLINE.derive_speed)
        frames.append((t, snap, res, counts))
    return frames


class ReplayTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.frames = replay()

    def test_the_operator_is_set_up_as_measured(self):
        self.assertEqual((BRIGHTLINE.scan_interval_s, BRIGHTLINE.derive_speed), (60, True))
        self.assertEqual(BRIGHTLINE.source, operators.SOURCE_BRIGHTLINE_RT)

    def test_every_moved_train_is_on_its_line(self):
        routes, checked = {}, 0
        for _, snap, res, _ in self.frames:
            number = {o.vehicle_id: o.train for o in snap.observations}
            for vid, r in res["vehicles"].items():
                if r.get("position_source") != "estimated":
                    continue
                off = []
                for sid in GEOMETRY["trains"][number[vid]]:
                    if sid not in routes:
                        routes[sid] = geometry.Route([tuple(q) for q in GEOMETRY["shapes"][sid]])
                    off.append(routes[sid].project(r["latitude"], r["longitude"])[1])
                self.assertLess(min(off), 1.0, (vid, min(off)))
                checked += 1
        self.assertGreater(checked, MEASURED_ESTIMATED_FLOOR)

    def test_no_speed_is_published_for_a_source_that_reports_none(self):
        for _, _, res, _ in self.frames:
            for r in res["vehicles"].values():
                self.assertNotIn("speed_kmh", r)

    def test_a_moving_train_has_a_course_and_a_standing_one_does_not(self):
        moving = held = 0
        for _, _, res, _ in self.frames:
            for r in res["vehicles"].values():
                basis = r.get("icon_rotation_basis")
                if basis == "course":
                    self.assertEqual(r["course_deg"], r["icon_rotation_deg"])
                    moving += 1
                elif basis == "held" and r.get("position_source") == "estimated":
                    self.assertNotIn("course_deg", r)
                    held += 1
        self.assertGreater(moving, 1000)
        self.assertGreater(held, 0)

    def test_each_disc_is_the_colour_of_where_it_is_going(self):
        checked = 0
        for _, _, res, _ in self.frames:
            for r in res["vehicles"].values():
                if not r.get("in_service"):
                    continue
                self.assertEqual(r["marker_label_color"], "#000000")
                dest = r.get("destination")
                if dest:
                    self.assertEqual(r["marker_color"], brightline_op.DESTINATION_COLOURS[dest])
                    checked += 1
        self.assertGreater(checked, 1000)

    def errors(self):
        """For each train drawn at a poll: (km from where it really was then,
        km from the fix that poll had). Where it really was is interpolated
        between its two fixes either side of the poll, at most MAX_BRACKET_S
        apart. NOT the next fix, as the Amtrak replay compares: Brightline's
        fixes reach a poll 60-120 s old, so the next fix describes a moment
        BEFORE the poll that drew the train, and an estimate that is right
        reads a minute's travel wrong (measured 2026-10-10, 1.12 km p50)."""
        fixes = {}
        for _, snap, _, _ in self.frames:
            for o in snap.observations:
                f = (o.observed_at.timestamp(), o.lat, o.lon)
                lst = fixes.setdefault(o.vehicle_id, [])
                if not lst or lst[-1][0] < f[0]:
                    lst.append(f)
        out = []
        for t, snap, res, _ in self.frames:
            held = {o.vehicle_id: (o.lat, o.lon) for o in snap.observations}
            for vid, r in res["vehicles"].items():
                if r.get("position_source") != "estimated" or vid not in held:
                    continue
                lst = fixes.get(vid) or []
                before = [f for f in lst if f[0] <= t]
                after = [f for f in lst if f[0] >= t]
                if not before or not after or after[0][0] - before[-1][0] > MAX_BRACKET_S:
                    continue
                (t0, a0, b0), (t1, a1, b1) = before[-1], after[0]
                w = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
                truth = (a0 + w * (a1 - a0), b0 + w * (b1 - b0))
                out.append((km((r["latitude"], r["longitude"]), truth), km(held[vid], truth)))
        return out

    def test_closer_to_where_it_was_than_its_fix_is(self):
        errs = self.errors()
        self.assertGreater(len(errs), 500)
        drawn = statistics.median(e for e, _ in errs)
        held = statistics.median(h for _, h in errs)
        self.assertLess(drawn, held / 2, (drawn, held))
        self.assertLess(drawn, MEASURED_P50_KM_CEILING, drawn)


# Two fixes 60 s apart, or one missed between them.
MAX_BRACKET_S = 150
# Measured on these fixtures 2026-10-10 (bin\ltir_bl_measure.txt): 1,531
# records estimated, 1 observed, over 180 polls; 1,467 drawn positions with a
# truth either side, p50 0.28 km from it (p90 1.30), the poll's own fix p50
# 2.79 km (p90 4.94). The worst are a locomotive handover (5339, 15 km, the
# fix itself as far off) and trains drawn up to 3 km ahead of where they
# stood (5341, 5330, 5340: the estimate never runs backwards). Set with a
# margin; a change past any is a change in the estimate.
MEASURED_ESTIMATED_FLOOR = 1300
MEASURED_P50_KM_CEILING = 0.5


if __name__ == "__main__":
    unittest.main()
