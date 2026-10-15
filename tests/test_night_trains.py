"""VR's night-train markers and the mokki (Intercity Rail SSOT 8.4, "The Santa
Claus Express"; Lee 2026-10-14 23:53 to 2026-10-15 03:38). Offline.

Which runs are the Santa Claus Express (sources/digitraffic_rail.py), the two
seasons and the picture each train gets (operators/vr.py), the pictures
themselves (pictures.py, pictures/), and what reaches the map (attributes.py).
"""

import datetime as dt
import hashlib
import json
import pathlib
import unittest

from _load import COMP, load

src = load("sources.digitraffic_rail")
vr = load("operators.vr")
operators = load("operators")
pictures = load("pictures")
attributes = load("attributes")
sources_base = load("sources.base")

D = dt.date


def train(first, last):
    return {"timeTableRows": [{"stationShortCode": first}, {"stationShortCode": "TPE"},
                              {"stationShortCode": last}]}


class SantaRouteTests(unittest.TestCase):
    """Lee 02:42: "from Helsinki or Turku to Rovaniemi, Kolari or Kemijarvi"."""

    def test_the_lapland_night_trains_both_ways(self):
        for first, last in (("HKI", "ROI"), ("HKI", "KLI"), ("HKI", "KJÄ"), ("ROI", "HKI"),
                            ("KLI", "HKI"), ("KJÄ", "HKI"), ("TKU", "ROI"), ("TUS", "KLI")):
            self.assertTrue(src.santa_express("PYO", "265", "2026-12-01", train(first, last), {}),
                            (first, last))

    def test_not_another_type_or_another_route(self):
        self.assertFalse(src.santa_express("IC", "27", "2026-12-01", train("HKI", "ROI"), {}))
        self.assertFalse(src.santa_express("PYO", "1", "2026-12-01", train("HKI", "OL"), {}))
        self.assertFalse(src.santa_express("PYO", "1", "2026-12-01", train("ROI", "KLI"), {}))
        self.assertFalse(src.santa_express("PYO", "1", "2026-12-01", train("HKI", "TKU"), {}))
        self.assertFalse(src.santa_express(None, "1", "2026-12-01", train("HKI", "ROI"), {}))
        self.assertFalse(src.santa_express("PYO", "1", "2026-12-01", None, {}))
        self.assertFalse(src.santa_express("PYO", "1", "2026-12-01", {"timeTableRows": []}, {}))

    def test_933_rides_with_265_on_the_same_date(self):
        t = train("TUS", "TPE")
        self.assertTrue(src.santa_express("PYO", "933", "2026-12-01", t, {"PYO 265|2026-12-01": "x"}))
        self.assertFalse(src.santa_express("PYO", "933", "2026-12-01", t, {"PYO 265|2026-11-30": "x"}))
        self.assertFalse(src.santa_express("PYO", "933", "2026-12-01", t, {"PYO 274|2026-12-01": "x"}))
        self.assertFalse(src.santa_express("PYO", "933", "2026-12-01", t, {}))

    def test_904_rides_with_274_from_the_evening_before(self):
        t = train("TPE", "TUS")
        self.assertTrue(src.santa_express("PYO", "904", "2026-12-02", t, {"PYO 274|2026-12-01": "x"}))
        self.assertFalse(src.santa_express("PYO", "904", "2026-12-02", t, {"PYO 274|2026-12-02": "x"}))
        self.assertFalse(src.santa_express("PYO", "904", "2026-12-02", t, {"PYO 265|2026-12-01": "x"}))

    def test_a_leg_needs_a_usable_date(self):
        t = train("TUS", "TPE")
        for date in (None, "", "not a date"):
            self.assertFalse(src.santa_express("PYO", "933", date, t, {"PYO 265|2026-12-01": "x"}))

    def test_the_adapter_marks_the_run_and_its_date(self):
        now = dt.datetime(2026, 12, 1, 20, 0, tzinfo=dt.timezone.utc).timestamp()
        iso = lambda m: dt.datetime.fromtimestamp(now + m * 60, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        rows = [{"stationShortCode": "HKI", "type": "DEPARTURE", "trainStopping": True, "commercialStop": True,
                 "scheduledTime": iso(-60), "actualTime": iso(-60), "differenceInMinutes": 0},
                {"stationShortCode": "TPE", "type": "ARRIVAL", "trainStopping": True, "commercialStop": True,
                 "scheduledTime": iso(60)},
                {"stationShortCode": "KJÄ", "type": "ARRIVAL", "trainStopping": True, "commercialStop": True,
                 "scheduledTime": iso(900)}]
        trains = {("265", "2026-12-01"): {"timeTableRows": rows},
                  ("27", "2026-12-01"): {"timeTableRows": [dict(r) for r in rows]}}
        recs = [{"key": (n, "2026-12-01"), "number": n, "departure_date": "2026-12-01", "lat": 61.0,
                 "lon": 24.0, "speed_kmh": 100, "observed_at": None, "train_type": t, "cancelled": False}
                for n, t in (("265", "PYO"), ("27", "IC"))]
        snap = src.DigitrafficRail().parse(recs, trains, now, {}, {})
        self.assertEqual(snap.extras["265-1"]["santa_express"], True)
        self.assertEqual(snap.extras["265-1"]["departure_date"], "2026-12-01")
        self.assertNotIn("santa_express", snap.extras["27-1"])
        self.assertEqual(snap.extras["27-1"]["departure_date"], "2026-12-01")


class SeasonTests(unittest.TestCase):

    def test_first_sunday_of_advent(self):
        # The fourth Sunday before Christmas: 27 November to 3 December.
        for year, day in ((2022, D(2022, 11, 27)), (2023, D(2023, 12, 3)), (2025, D(2025, 11, 30)),
                          (2026, D(2026, 11, 29)), (2027, D(2027, 11, 28))):
            got = vr.first_advent(year)
            self.assertEqual(got, day, year)
            self.assertEqual(got.weekday(), 6)

    def test_santa_season_is_advent_to_epiphany(self):
        self.assertFalse(vr.santa_season(D(2026, 11, 28)))
        self.assertTrue(vr.santa_season(D(2026, 11, 29)))
        self.assertTrue(vr.santa_season(D(2026, 12, 31)))
        self.assertTrue(vr.santa_season(D(2027, 1, 6)))
        self.assertFalse(vr.santa_season(D(2027, 1, 7)))
        self.assertFalse(vr.santa_season(D(2026, 7, 1)))

    def test_midsummer_eve_is_the_friday_from_19_to_25_june(self):
        for year, day in ((2025, D(2025, 6, 20)), (2026, D(2026, 6, 19)), (2027, D(2027, 6, 25)),
                          (2028, D(2028, 6, 23))):
            got = vr.midsummer_eve(year)
            self.assertEqual(got, day, year)
            self.assertEqual(got.weekday(), 4)

    def test_mokki_season_is_midsummer_eve_to_31_july(self):
        self.assertFalse(vr.mokki_season(D(2026, 6, 18)))
        self.assertTrue(vr.mokki_season(D(2026, 6, 19)))
        self.assertTrue(vr.mokki_season(D(2026, 7, 31)))
        self.assertFalse(vr.mokki_season(D(2026, 8, 1)))
        self.assertFalse(vr.mokki_season(D(2026, 12, 1)))


def rec(train="PYO 265", date="2026-12-01", santa=True, delay=None):
    r = {"train": train, "departure_date": date}
    if santa:
        r["santa_express"] = True
    if delay is not None:
        r["delay_min"] = delay
    return r


class MarkerTests(unittest.TestCase):

    def test_going_north_the_snowman_coming_back_the_reindeer(self):
        self.assertEqual(vr.vr_marker(rec("PYO 265")), {"entity_picture": pictures.url("snowman")})
        self.assertEqual(vr.vr_marker(rec("PYO 274")), {"entity_picture": pictures.url("reindeer")})
        self.assertEqual(vr.vr_marker(rec("PYO 933")), {"entity_picture": pictures.url("snowman")})
        self.assertEqual(vr.vr_marker(rec("PYO 904")), {"entity_picture": pictures.url("reindeer")})

    def test_very_late_flips_with_nuuttipukki_from_12_minutes(self):
        self.assertEqual(vr.VERY_LATE_MIN, 12)
        self.assertEqual(vr.VR.very_late_threshold_min, vr.VERY_LATE_MIN)
        self.assertEqual(vr.vr_marker(rec("PYO 265", delay=11)), {"entity_picture": pictures.url("snowman")})
        self.assertEqual(vr.vr_marker(rec("PYO 265", delay=12)), {"entity_picture": pictures.url("snowman_late")})
        self.assertEqual(vr.vr_marker(rec("PYO 274", delay=40)), {"entity_picture": pictures.url("reindeer_late")})
        self.assertEqual(vr.vr_marker(rec("PYO 274", delay=-12)), {"entity_picture": pictures.url("reindeer")})
        self.assertEqual(vr.vr_marker(rec("PYO 274", delay=True)), {"entity_picture": pictures.url("reindeer")})
        self.assertEqual(vr.vr_marker(rec("PYO 274", delay=12.5)), {"entity_picture": pictures.url("reindeer")})

    def test_no_number_and_no_rotation_keys_on_the_figures(self):
        keys = vr.vr_marker(rec("PYO 265"))
        self.assertEqual(set(keys), {"entity_picture"})

    def test_outside_the_season_the_disc(self):
        self.assertEqual(vr.vr_marker(rec("PYO 265", date="2026-11-28")), vr.vr_styling("PYO 265"))
        self.assertEqual(vr.vr_marker(rec("PYO 265", date="2027-01-07")), vr.vr_styling("PYO 265"))

    def test_a_run_that_is_not_the_express_keeps_the_disc_at_christmas(self):
        self.assertEqual(vr.vr_marker(rec("IC 27", santa=False)), vr.vr_styling("IC 27"))

    def test_the_departure_date_decides_not_today(self):
        # A run that left on 6 January keeps its figure into the 7th.
        self.assertIn("entity_picture", vr.vr_marker(rec("PYO 274", date="2027-01-06")))

    def test_the_mokki_on_every_train_in_summer_with_its_number_beside_it(self):
        for label, ring in (("IC 23", vr.VR_GREEN), ("S 46", vr.VR_DARK), ("PYO 265", vr.VR_GREEN)):
            keys = vr.vr_marker(rec(label, date="2026-07-04", santa=label.startswith("PYO")))
            self.assertEqual(keys, {"entity_picture": pictures.url("mokki"),
                                    "marker_label_placement": "heading",
                                    "marker_ring_color": ring, "marker_label_color": vr.WHITE}, label)

    def test_the_mokki_does_not_flip(self):
        keys = vr.vr_marker(rec("IC 23", date="2026-07-04", santa=False, delay=45))
        self.assertEqual(keys["entity_picture"], pictures.url("mokki"))

    def test_without_a_date_or_a_number_the_disc(self):
        self.assertEqual(vr.vr_marker(rec("PYO 265", date=None)), vr.vr_styling("PYO 265"))
        self.assertEqual(vr.vr_marker(rec("PYO 265", date="soon")), vr.vr_styling("PYO 265"))
        self.assertEqual(vr.vr_marker({"departure_date": "2026-07-04"}), {})

    def test_the_operator_uses_it(self):
        self.assertIs(operators.OPERATORS["vr"].record_styling, vr.vr_marker)
        self.assertEqual(operators.OPERATORS["vr"].marker_keys(rec("PYO 265")),
                         {"entity_picture": pictures.url("snowman")})

    def test_other_railroads_keep_their_styling(self):
        for op_id in ("amtrak", "via_rail", "brightline"):
            self.assertIsNone(operators.OPERATORS[op_id].record_styling, op_id)


class PictureTests(unittest.TestCase):

    def test_urls_carry_the_artwork_version(self):
        self.assertEqual(pictures.url("reindeer"),
                         f"/api/live_track_intercity_rail/picture/reindeer.svg?v={pictures.ARTWORK_VERSION}")
        with self.assertRaises(ValueError):
            pictures.url("rudolph")

    def test_only_the_named_files_are_served(self):
        for bad in ("../manifest", "manifest", "reindeer.svg", "", "REINDEER"):
            self.assertIsNone(pictures.path(bad), bad)

    def test_every_picture_ships_as_an_svg(self):
        for name in pictures.NAMES:
            data = pictures.path(name).read_bytes()
            self.assertTrue(data.startswith(b"<svg xmlns=\"http://www.w3.org/2000/svg\""), name)
            self.assertFalse(data.startswith(b"\xef\xbb\xbf"), name)
        files = sorted(p.name for p in (COMP / "pictures").iterdir())
        self.assertEqual(files, sorted(f"{n}.svg" for n in pictures.NAMES))

    def test_the_figures_are_the_drafts_lee_chose(self):
        # bin\\vr_icons\\f0.svg, f1.svg (round 3, 02:08) and icon8.svg (M3).
        sha = lambda n: hashlib.sha256(pictures.path(n).read_bytes()).hexdigest()[:12]
        self.assertEqual(sha("reindeer"), "8eb27acfd8df")
        self.assertEqual(sha("snowman"), "053975a07f6b")
        self.assertEqual(sha("mokki"), "7a3b5d7b9078")

    def test_the_late_pictures_flip_every_4_seconds(self):
        import base64
        for name, figure in (("reindeer_late", "reindeer"), ("snowman_late", "snowman")):
            text = pictures.path(name).read_text("ascii")
            self.assertEqual(text.count("8s steps(1,end) infinite"), 2, name)
            self.assertIn(base64.b64encode(pictures.path(figure).read_bytes()).decode(), text, name)
            self.assertEqual(text.count("data:image/svg+xml;base64,"), 2, name)


class MapTests(unittest.TestCase):

    def test_a_picture_has_no_rotation_but_keeps_its_course(self):
        r = {"vehicle_id": "265-1", "marker_label": "PYO 265", "in_service": True, "course_deg": 12.0,
             "icon_rotation_deg": 12.0, "icon_rotation_basis": "course",
             "entity_picture": pictures.url("snowman"), "santa_express": True,
             "departure_date": "2026-12-01"}
        attrs = attributes.to_attributes(r, "vr")
        self.assertNotIn("icon_rotation_deg", attrs)
        self.assertNotIn("icon_rotation_basis", attrs)
        self.assertEqual(attrs["course_deg"], 12.0)
        # Published by the entity's own entity_picture property, and the
        # record-only keys never.
        for key in ("entity_picture", "santa_express", "departure_date"):
            self.assertNotIn(key, attrs)

    def test_a_disc_keeps_its_arrow(self):
        r = {"vehicle_id": "27-1", "marker_label": "IC 27", "in_service": True,
             "icon_rotation_deg": 12.0, "icon_rotation_basis": "course"}
        self.assertEqual(attributes.to_attributes(r, "vr")["icon_rotation_deg"], 12.0)

    def test_the_cottage_tag_reaches_the_map(self):
        for key in ("marker_label_placement", "marker_ring_color", "marker_label_color"):
            self.assertIn(key, attributes.PASSTHROUGH)

    def test_the_new_keys_are_record_only(self):
        for key in ("departure_date", "santa_express"):
            self.assertIn(key, sources_base.EXTRA_KEYS)
            self.assertIn(key, sources_base.RECORD_ONLY_KEYS)

    def test_the_manifest_asks_for_http(self):
        manifest = json.loads((COMP / "manifest.json").read_text("utf-8"))
        self.assertIn("http", manifest["dependencies"])


if __name__ == "__main__":
    unittest.main()
