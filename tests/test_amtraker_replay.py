"""The Amtraker adapter and Fleet on REAL Amtrak rows. No Home Assistant.

tests/fixtures/amtraker_amtrak_20261009.json.gz: 21 polls 120 s apart from
the 2026-10-09 capture (fixtures/README.md). It holds the source's outage
(poll 17: no Amtrak row), Predeparture -> Active and Active -> Completed
transitions, and train numbers 5 and 8 each running on two departure dates.
"""

import datetime as dt
import gzip
import json
import pathlib
import unittest

from _load import load

from saw_livetrack import parse_ts
from saw_livetrack.gtfs import Fleet

amtraker = load("sources.amtraker")
sources_base = load("sources.base")
operators = load("operators")

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "amtraker_amtrak_20261009.json.gz"
DATA = json.loads(gzip.open(FIXTURE).read().decode("utf-8"))
POLLS = [(dt.datetime.strptime(p["t"], "%Y%m%dT%H%M%SZ")
          .replace(tzinfo=dt.timezone.utc).timestamp(), p["rows"])
         for p in DATA["polls"]]
AMTRAK = operators.OPERATORS["amtrak"]


def run(fleet):
    """Every poll through the adapter and Fleet, as the coordinator does."""
    out = []
    for t, rows in POLLS:
        snap = amtraker.parse(rows, t)
        if snap is None:
            out.append((t, None, None))
            continue
        res = fleet.update(snap.observations, t, next_stops=snap.next_stops,
                           trip_delays=snap.trip_delays)
        out.append((t, snap, res))
    return out


class RealRowsTests(unittest.TestCase):

    def test_the_fixture_is_what_it_says(self):
        self.assertEqual(len(POLLS), 21)
        self.assertEqual([i for i, (_, rows) in enumerate(POLLS) if not rows], [16])

    def test_the_outage_poll_and_only_it_is_refused(self):
        refused = [i for i, (t, rows) in enumerate(POLLS)
                   if amtraker.parse(rows, t) is None]
        self.assertEqual(refused, [16])

    def test_identity_label_and_state_on_every_poll(self):
        for t, rows in POLLS:
            snap = amtraker.parse(rows, t)
            if snap is None:
                continue
            ids = [o.vehicle_id for o in snap.observations]
            self.assertEqual(len(ids), len(set(ids)))
            active = {r["trainID"]: r for r in rows if r["trainState"] == "Active"}
            self.assertEqual(set(ids), set(active))
            for o in snap.observations:
                self.assertEqual(o.train, active[o.vehicle_id]["trainNumRaw"])

    def test_one_number_on_two_dates_is_two_trains_with_one_label(self):
        snap = amtraker.parse(POLLS[0][1], POLLS[0][0])
        by_id = {o.vehicle_id: o.train for o in snap.observations}
        for num in ("5", "8"):
            runs = {k: v for k, v in by_id.items() if k.split("-")[0] == num}
            self.assertEqual(len(runs), 2, num)
            self.assertEqual(set(runs.values()), {num})

    def test_the_count_is_runs_not_numbers(self):
        # Measured on the box: a count of numbers read 112 for 124 trains.
        for t, rows in POLLS:
            snap = amtraker.parse(rows, t)
            if snap is None:
                continue
            active = {r["trainID"] for r in rows if r["trainState"] == "Active"}
            self.assertEqual(sources_base.trains_in_service(snap), len(active))
        snap = amtraker.parse(POLLS[0][1], POLLS[0][0])
        numbers = {o.train for o in snap.observations}
        self.assertGreater(sources_base.trains_in_service(snap), len(numbers))

    def test_next_stop_is_ahead_of_every_departed_stop(self):
        checked = 0
        for t, rows in POLLS:
            snap = amtraker.parse(rows, t)
            if snap is None:
                continue
            for r in rows:
                tid = r["trainID"]
                if tid not in snap.next_stops:
                    continue
                st = r["stations"]
                names = [s["name"] for s in st]
                i = names.index(snap.next_stops[tid][0])
                last_dep = max((j for j, s in enumerate(st)
                                if s["status"] == "Departed"), default=-1)
                self.assertGreater(i, last_dep, tid)
                self.assertGreater(i, 0, tid)
                est, sch = parse_ts(st[i]["arr"]), parse_ts(st[i]["schArr"])
                if est and sch:
                    self.assertEqual(snap.trip_delays[tid],
                                     int((est - sch).total_seconds()))
                checked += 1
        # Measured on this fixture: every published train with a stop ahead.
        self.assertEqual(checked, 169)


class FleetOnRealRowsTests(unittest.TestCase):

    def test_no_running_train_is_removed_and_the_finished_one_is(self):
        out = run(Fleet(**dict(AMTRAK.fleet)))
        departed = {vid for _, _, res in out if res for vid in res["departed"]}
        final_active = {r["trainID"] for r in POLLS[-1][1] if r["trainState"] == "Active"}
        self.assertFalse(departed & final_active, sorted(departed & final_active))
        self.assertIn("794-8", departed)       # Active -> Completed in the window

    def test_a_predeparture_train_appears_only_once_active(self):
        out = run(Fleet(**dict(AMTRAK.fleet)))
        for (t, rows), (_, snap, res) in zip(POLLS, out):
            if res is None:
                continue
            state = {r["trainID"]: r["trainState"] for r in rows}
            for vid in res["vehicles"]:
                self.assertEqual(state[vid], "Active", vid)

    def test_a_segment_always_carries_its_times(self):
        out = run(Fleet(**dict(AMTRAK.fleet)))
        segs = 0
        for _, _, res in out:
            for rec in (res or {}).get("vehicles", {}).values():
                if "previous_latitude" in rec:
                    segs += 1
                    for k in ("observed_at", "previous_observed_at", "segment_duration_s"):
                        self.assertIn(k, rec)
        self.assertGreater(segs, 50)

    def test_amtraks_rest_s_keeps_moving_trains_moving(self):
        def course_records(fleet):
            return sum("course_deg" in rec for _, _, res in run(fleet) if res
                       for rec in res["vehicles"].values())
        self.assertGreater(course_records(Fleet(**dict(AMTRAK.fleet))),
                           course_records(Fleet()))


if __name__ == "__main__":
    unittest.main()
