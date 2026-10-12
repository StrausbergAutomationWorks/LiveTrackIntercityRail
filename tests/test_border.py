"""Customs at the US-Canada border (Lee 2026-10-11 20:23). No HA."""

import datetime as dt
import unittest

from _load import load

border = load("border")
amtraker = load("sources.amtraker")
attributes = load("attributes")
sources_base = load("sources.base")

NOW = dt.datetime(2026, 10, 11, 22, 0, 0, tzinfo=dt.timezone.utc).timestamp()
ET, CA = "America/New_York", "America/Toronto"
LACOLLE = (45.012445, -73.370126)
RSP = (44.99487, -73.371093)
NFL = (43.109908, -79.055276)
NFS = (43.108736, -79.063291)


def stop(code, tz, status, sch=None, arr=None):
    return {"name": code, "code": code, "tz": tz, "status": status,
            "schArr": sch, "schDep": sch, "arr": arr, "dep": arr}


def adk69(lat=LACOLLE[0], lon=LACOLLE[1], mph=0.0):
    """69 as Amtraker had it at Lacolle, 2026-10-11 ~17:59 EDT (the -60)."""
    return {"trainID": "69-11", "trainNum": "69", "trainNumRaw": "69", "routeName": "Adirondack",
            "trainState": "Active", "lat": lat, "lon": lon, "lastValTS": "2026-10-11T17:59:40-04:00",
            "velocity": mph, "heading": "N", "provider": "Amtrak",
            "stations": [stop("NYP", ET, "Departed", "2026-10-11T08:15:00-04:00", "2026-10-11T08:15:00-04:00"),
                         stop("RSP", ET, "Departed", "2026-10-11T16:35:00-04:00", "2026-10-11T16:20:00-04:00"),
                         stop("SLAM", CA, "Enroute", "2026-10-11T20:03:00-04:00", "2026-10-11T19:03:00-04:00"),
                         stop("MTRL", CA, "Enroute", "2026-10-11T20:16:00-04:00", "2026-10-11T19:16:00-04:00")]}


class CustomsStopTests(unittest.TestCase):

    def at(self, where, origin, dest, kmh=0.0):
        p = border.customs_stop(where[0], where[1], kmh, origin, dest)
        return p.name if p else None

    def test_each_crossing_entering_the_country(self):
        self.assertEqual(self.at(LACOLLE, ET, CA), "Lacolle, QC")          # 69
        self.assertEqual(self.at(RSP, CA, ET), "Rouses Point, NY")         # 68
        self.assertEqual(self.at(NFL, CA, ET), "Niagara Falls, NY")        # 64
        self.assertEqual(self.at(NFS, ET, CA), "Niagara Falls, ON")        # 63

    def test_leaving_a_country_is_no_customs(self):
        self.assertIsNone(self.at(RSP, ET, CA))       # 69's 3-minute stop
        self.assertIsNone(self.at(NFL, ET, CA))       # 63's 8-minute stop
        self.assertIsNone(self.at(NFS, CA, ET))       # 64's 2-minute stop
        self.assertIsNone(self.at(LACOLLE, CA, ET))   # 68 passing

    def test_a_domestic_train_is_never_at_customs(self):
        self.assertIsNone(self.at(NFL, ET, ET))       # Empire Service at its terminus
        self.assertIsNone(self.at(NFS, CA, CA))

    def test_moving_or_speed_unknown_is_no_customs(self):
        self.assertIsNone(self.at(LACOLLE, ET, CA, kmh=5.0))
        self.assertIsNone(self.at(LACOLLE, ET, CA, kmh=None))
        self.assertEqual(self.at(LACOLLE, ET, CA, kmh=4.9), "Lacolle, QC")

    def test_radius(self):
        self.assertEqual(self.at((LACOLLE[0] + 0.0044, LACOLLE[1]), ET, CA), "Lacolle, QC")    # ~490 m
        self.assertIsNone(self.at((LACOLLE[0] + 0.0046, LACOLLE[1]), ET, CA))                  # ~510 m
        self.assertEqual(self.at((RSP[0] + 0.0035, RSP[1]), CA, ET), "Rouses Point, NY")       # ~390 m
        self.assertIsNone(self.at((RSP[0] + 0.0037, RSP[1]), CA, ET))                          # ~410 m

    def test_niagara_radii_do_not_overlap(self):
        gap = border.distance_m(*NFL, *NFS)
        self.assertAlmostEqual(gap, 660, delta=15)
        self.assertLess(400 + 400, gap + 400)
        self.assertGreater(gap, 400)

    def test_zones(self):
        self.assertEqual(border.country_of_zone("America/Toronto"), "CA")
        self.assertEqual(border.country_of_zone("America/Vancouver"), "CA")
        self.assertEqual(border.country_of_zone("America/New_York"), "US")
        self.assertEqual(border.country_of_zone("America/Los_Angeles"), "US")
        for tz in (None, "", "Europe/Copenhagen", 5, "UTC"):
            self.assertIsNone(border.country_of_zone(tz))
        self.assertIsNone(self.at(LACOLLE, None, CA))
        self.assertIsNone(self.at(LACOLLE, ET, None))


class AdapterTests(unittest.TestCase):

    def test_69_at_lacolle_says_customs_and_drops_the_minus_60(self):
        snap = amtraker.parse([adk69()], NOW)
        self.assertEqual(snap.extras["69-11"]["marker_status"], "Customs")
        self.assertNotIn("69-11", snap.trip_delays)
        self.assertEqual(snap.next_stops["69-11"][0], "SLAM")
        self.assertEqual(snap.stop_codes["69-11"], "SLAM")

    def test_moving_on_the_delay_returns(self):
        snap = amtraker.parse([adk69(lat=45.06, mph=40.0)], NOW)
        self.assertNotIn("marker_status", snap.extras["69-11"])
        self.assertEqual(snap.trip_delays["69-11"], -3600)

    def test_no_stations_no_customs(self):
        r = adk69()
        r["stations"] = []
        self.assertFalse(amtraker.at_customs(r, *LACOLLE, 0.0))

    def test_it_reaches_the_map(self):
        self.assertIn("marker_status", sources_base.EXTRA_KEYS)
        self.assertNotIn("marker_status", sources_base.RECORD_ONLY_KEYS)
        rec = {"vehicle_id": "69-11", "marker_label": "69", "in_service": True, "marker_status": "Customs"}
        self.assertEqual(attributes.to_attributes(rec, "amtrak")["marker_status"], "Customs")


if __name__ == "__main__":
    unittest.main()
