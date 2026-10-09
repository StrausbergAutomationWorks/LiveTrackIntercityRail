"""Record -> attributes. No Home Assistant. Live Track Commuter Rail's tests,
with this integration's two additions (speed_kmh, heading_octant)."""

import unittest

from _load import load

attributes = load("attributes")

D10_LAYERS = {"fixed", "water", "rail", "air_low", "air"}
NEVER = {"heading_deg", "max_extrapolation_s", "object_ids", "z_index_offset",
         "mmsi", "imo", "icao24", "registration", "latitude", "longitude"}

REC = {"vehicle_id": "5-8", "latitude": 40.1, "longitude": -104.9,
       "in_service": True, "marker_label": "5", "train": "5",
       "line_name": "California Zephyr",
       "observed_at": "2026-10-09T07:00:39+00:00", "course_deg": 271.4,
       "icon_rotation_deg": 271.4, "icon_rotation_basis": "course",
       "speed_kmh": 101.4, "heading_octant": "W", "next_stop": "Denver",
       "arrival_estimated_at": "2026-10-09T13:05:00+00:00", "delay_min": 12}


class AttributeTests(unittest.TestCase):

    def test_required_keys(self):
        a = attributes.to_attributes(dict(REC), "amtrak")
        self.assertEqual(a["identity"], "5-8")
        self.assertEqual(a["marker_label"], "5")
        self.assertEqual(a["operator"], "amtrak")
        self.assertIs(a["in_service"], True)
        self.assertEqual(a["map_layer"], "rail")
        self.assertIn(a["map_layer"], D10_LAYERS)

    def test_source_keys_pass_through(self):
        a = attributes.to_attributes(dict(REC), "amtrak")
        for key in ("line_name", "speed_kmh", "heading_octant", "next_stop",
                    "arrival_estimated_at", "delay_min", "observed_at",
                    "course_deg"):
            self.assertEqual(a[key], REC[key], key)

    def test_an_estimate_says_so_and_carries_its_fix(self):
        # D3 provenance (projection.py): the drawn position is the state; the
        # source's fix rides in attributes, so the recorder keeps the real track.
        rec = dict(REC, position_source="estimated", fix_latitude=40.09, fix_longitude=-104.88)
        a = attributes.to_attributes(rec, "amtrak")
        self.assertEqual(a["position_source"], "estimated")
        self.assertEqual((a["fix_latitude"], a["fix_longitude"]), (40.09, -104.88))
        path = [[40.09, -104.88], [40.1, -104.9]]
        self.assertEqual(attributes.to_attributes(dict(rec, track_path=path), "amtrak")["track_path"], path)
        a = attributes.to_attributes(dict(REC, position_source="observed"), "amtrak")
        self.assertEqual(a["position_source"], "observed")
        self.assertNotIn("fix_latitude", a)

    def test_position_is_not_an_attribute(self):
        a = attributes.to_attributes(dict(REC), "amtrak")
        self.assertNotIn("latitude", a)
        self.assertNotIn("longitude", a)

    def test_none_is_omitted_never_published(self):
        a = attributes.to_attributes(dict(REC, delay_min=None, speed_kmh=None,
                                          line_name=None), "amtrak")
        for key in ("delay_min", "speed_kmh", "line_name"):
            self.assertNotIn(key, a)

    def test_zero_is_published_not_dropped(self):
        # 0 is a value, not "unknown": a train on time, a train standing.
        a = attributes.to_attributes(dict(REC, delay_min=0, speed_kmh=0.0), "amtrak")
        self.assertEqual(a["delay_min"], 0)
        self.assertEqual(a["speed_kmh"], 0.0)

    def test_unlisted_and_forbidden_keys_never_reach_the_map(self):
        rec = dict(REC, map_layer="air", heading_deg=90.0,
                   max_extrapolation_s=60, object_ids={"mmsi": "1"},
                   z_index_offset=5, surprise="x")
        a = attributes.to_attributes(rec, "amtrak")
        self.assertEqual(a["map_layer"], "rail")
        self.assertFalse(NEVER & set(a), sorted(NEVER & set(a)))
        self.assertNotIn("surprise", a)


if __name__ == "__main__":
    unittest.main()
