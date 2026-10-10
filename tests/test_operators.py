"""The railroad registry. No Home Assistant."""

import unittest

from _load import load

operators = load("operators")
sources_base = load("sources.base")
attributes = load("attributes")
amtrak = load("operators.amtrak")


class RegistryTests(unittest.TestCase):

    def test_ids_are_keys_and_permanent_shape(self):
        for key, op in operators.OPERATORS.items():
            self.assertEqual(key, op.id)
            # An id becomes a config entry's unique_id and part of entity
            # names: lower-case, no spaces.
            self.assertRegex(op.id, r"^[a-z][a-z0-9_]*$")

    def test_amtrak_is_registered_on_amtraker(self):
        op = operators.OPERATORS["amtrak"]
        self.assertEqual(op.source, operators.SOURCE_AMTRAKER)
        self.assertEqual(op.source_options["provider"], "Amtrak")
        self.assertIn("Amtraker", op.attribution)
        self.assertIn("ODC-By", op.attribution)

    def test_every_source_is_known(self):
        for op in operators.OPERATORS.values():
            self.assertIn(op.source, operators.SOURCES)

    def test_every_region_has_a_label(self):
        regions = operators.regions_in_use()
        self.assertTrue(regions)
        for code in regions:
            self.assertIn(code, operators.REGIONS)
            self.assertTrue(operators.operators_in(code))

    def test_unknown_region_lists_nothing(self):
        self.assertEqual(operators.operators_in("XX"), [])

    def test_fleet_overrides_are_fleet_keywords(self):
        from saw_livetrack.gtfs import Fleet
        for op in operators.OPERATORS.values():
            Fleet(**dict(op.fleet))   # an unknown keyword raises TypeError

    def test_amtraks_own_definition_of_late(self):
        # 49 CFR 273.5(a)(1): on time up to 15 minutes; whole-minute times.
        op = operators.OPERATORS["amtrak"]
        self.assertEqual(op.lateness_keys(),
                         {"late_threshold_min": 16, "very_late_threshold_min": 30})
        self.assertGreaterEqual(op.very_late_threshold_min, op.late_threshold_min)

    def test_a_railroad_that_publishes_none_says_nothing(self):
        from dataclasses import replace
        op = replace(operators.OPERATORS["amtrak"], late_threshold_min=None,
                     very_late_threshold_min=None)
        self.assertEqual(op.lateness_keys(), {})
        op = replace(op, late_threshold_min=6)
        self.assertEqual(op.lateness_keys(), {"late_threshold_min": 6})

    def test_the_lateness_keys_reach_the_map(self):
        for key in operators.OPERATORS["amtrak"].lateness_keys():
            self.assertIn(key, attributes.PASSTHROUGH)

    def test_every_extra_key_can_reach_the_map(self):
        # A key an adapter may add but attributes.py drops would be dead.
        for key in sources_base.EXTRA_KEYS:
            self.assertIn(key, attributes.PASSTHROUGH)


class HoldLastTests(unittest.TestCase):
    """A failed poll rides on the last good answer for SOURCE_GAP_S."""

    def test_a_good_answer_is_published(self):
        a, b = sources_base.Snapshot(), sources_base.Snapshot()
        self.assertEqual(sources_base.hold_last(a, b, 0.0, 100.0, 600), (a, False))

    def test_a_failure_rides_on_the_last_good_answer(self):
        b = sources_base.Snapshot()
        self.assertEqual(sources_base.hold_last(None, b, 0.0, 600.0, 600), (b, True))

    def test_then_the_source_is_down(self):
        b = sources_base.Snapshot()
        self.assertEqual(sources_base.hold_last(None, b, 0.0, 600.5, 600), (None, False))

    def test_nothing_to_hold(self):
        self.assertEqual(sources_base.hold_last(None, None, None, 1.0, 600), (None, False))

    def test_ten_minutes(self):
        const = load("const")
        self.assertEqual(const.SOURCE_GAP_S, 600)


class AmtrakStarTests(unittest.TestCase):
    """Lee 2026-10-09 16:43: odd numbers D, even C, a star. 2026-10-10 00:11
    and 00:13: colours by route, the same three areas, white outlines kept."""

    def look(self, number, line=None):
        s = amtrak.amtrak_styling(number, line)
        return s["marker_ring_color"], s["marker_color"], s["marker_label_color"]

    def test_odd_is_d_blue_edge_red_number(self):
        s = amtrak.amtrak_styling("5")
        self.assertEqual(s["marker_shape"], "star")
        self.assertEqual((s["marker_ring_color"], s["marker_label_color"]), ("#3C3B6E", "#B22234"))
        self.assertEqual((s["marker_color"], s["marker_label_outline_color"]), ("#FFFFFF", "#FFFFFF"))

    def test_even_is_c_red_edge_blue_number(self):
        s = amtrak.amtrak_styling("2150")
        self.assertEqual((s["marker_ring_color"], s["marker_label_color"]), ("#B22234", "#3C3B6E"))

    def test_lees_route_colours_as_he_gave_them(self):
        # (band, fill, number): odd first, then the other direction.
        cases = {
            # 01:0x: Cascades option C6 (01:52: cream inside); Northeast
            # black on blue, white on red.
            "Amtrak Cascades": (("#004833", "#F8F2E6", "#7A3B26"), ("#7A3B26", "#F8F2E6", "#004833")),
            "Northeast Regional": (("#FB0001", "#3FC3F4", "#000000"), ("#3FC3F4", "#FB0001", "#FFFFFF")),
            "Pacific Surfliner": (("#003A7B", "#003A7B", "#CBD1D5"), ("#003A7B", "#CBD1D5", "#003A7B")),
            "Capitol Corridor": (("#001945", "#FFC709", "#001945"), ("#001945", "#001945", "#FFC709")),
            "Acela": (("#00537E", "#00537E", "#00B3E3"), ("#00537E", "#00B3E3", "#00537E")),
        }
        for line, (odd, even) in cases.items():
            self.assertEqual(self.look("501", line), odd, line)
            self.assertEqual(self.look("500", line), even, line)

    def test_number_outlines(self):
        # Lee 00:46 and 01:0x: no outline on Cascades, Northeast, Surfliner,
        # Caltrans and Acela numbers; the flag keeps its white outline.
        for line in ("Amtrak Cascades", "Northeast Regional", "Pacific Surfliner",
                     "Capitol Corridor", "Acela"):
            for n in ("1", "2"):
                self.assertEqual(amtrak.amtrak_styling(n, line)["marker_label_outline_color"], "none", line)
        for n in ("1", "2"):
            self.assertEqual(amtrak.amtrak_styling(n, "Empire Builder")["marker_label_outline_color"], "#FFFFFF")

    def test_every_route_lee_named_is_matched(self):
        ne = self.look("1", "Northeast Regional")
        for line in ("Northeast Regional", "Amtrak Virginia", "Carolinian", "Keystone",
                     "Keystone Service", "Vermonter", "Downeaster", "Amtrak Downeaster",
                     "Palmetto", "Pennsylvanian", "Adirondack", "Empire Service",
                     "Ethan Allen Express", "Maple Leaf",
                     "New Haven-Springfield-Greenfield Service", "Hartford Line",
                     "Amtrak Hartford Line", "Valley Flyer"):
            self.assertEqual(self.look("1", line), ne, line)
        self.assertEqual(self.look("1", "Capitol Corridor"), ("#001945", "#FFC709", "#001945"))
        # Lee 03:40: Gold Runner (G3), Piedmont (P1), Hiawatha on Surfliner.
        for line in ("San Joaquins", "Gold Runner"):
            self.assertEqual(self.look("1", line), ("#4741AF", "#FEDB18", "#4741AF"), line)
            self.assertEqual(self.look("2", line), ("#3DA7E9", "#FEDB18", "#4741AF"), line)
        self.assertEqual(self.look("73", "Piedmont"), ("#001E60", "#9D2235", "#E6DE0A"))
        self.assertEqual(self.look("74", "Piedmont"), ("#9D2235", "#001E60", "#E6DE0A"))
        for n in ("331", "332"):
            self.assertEqual(self.look(n, "Hiawatha"), self.look(n, "Pacific Surfliner"))
            self.assertEqual(self.look(n, "Hiawatha Service"), self.look(n, "Pacific Surfliner"))
        for line in ("Piedmont", "Gold Runner", "Hiawatha"):
            self.assertEqual(amtrak.amtrak_styling("1", line)["marker_label_outline_color"], "none")
        self.assertEqual(self.look("1", "Cascades"), self.look("1", "Amtrak Cascades"))

    def test_a_route_lee_did_not_name_keeps_the_flag(self):
        flag = self.look("5")
        # The rest of Amtrak Midwest keeps the flag (Lee 03:40).
        for line in ("California Zephyr", "Empire Builder", "Silver Meteor", "Lincoln Service",
                     "Borealis", "Wolverine", "Missouri River Runner", None, ""):
            self.assertEqual(self.look("5", line), flag, line)

    def test_the_arrow_is_the_band_outlined_white(self):
        for n, line in (("5", None), ("6", None), ("501", "Amtrak Cascades"), ("500", "Amtrak Cascades")):
            s = amtrak.amtrak_styling(n, line)
            self.assertEqual((s["marker_arrow_color"], s["marker_arrow_outline_color"]),
                             (s["marker_ring_color"], "#FFFFFF"))

    def test_no_number_no_style(self):
        for n in (None, "", "v28", "5A"):
            self.assertEqual(amtrak.amtrak_styling(n, "Acela"), {})

    def test_every_colour_is_the_contracts_form(self):
        import re
        for line in [None] + sorted(amtrak.ROUTE_SCHEMES):
            for n in ("1", "2"):
                for k, v in amtrak.amtrak_styling(n, line).items():
                    if k == "marker_label_outline_color" and v == "none":
                        continue   # D4a: "none", no outline (card, 2026-10-10)
                    if k.endswith("_color"):
                        self.assertRegex(v, re.compile(r"^#[0-9A-F]{6}$"), (k, line))

    def test_the_published_record_is_styled_by_its_line(self):
        op = operators.OPERATORS["amtrak"]
        self.assertIs(op.styling, amtrak.amtrak_styling)
        keys = op.marker_keys({"train": "2151", "line_name": "Acela"})
        self.assertEqual(keys["marker_label_color"], "#00B3E3")
        self.assertEqual(op.marker_keys({"train": "5"})["marker_ring_color"], "#3C3B6E")
        self.assertEqual(operators.Operator(id="x", name="x", short="x", regions=(), source="amtraker",
                                            attribution="x").marker_keys({"train": "5"}), {})

    def test_amtrak_uses_it_and_the_map_gets_the_shape(self):
        rec = {"vehicle_id": "5-8", "marker_label": "5", "in_service": True,
               **amtrak.amtrak_styling("5")}
        a = attributes.to_attributes(rec, "amtrak")
        for k in ("marker_shape", "marker_color", "marker_ring_color", "marker_label_color",
                  "marker_label_outline_color", "marker_arrow_color", "marker_arrow_outline_color"):
            self.assertIn(k, a)


if __name__ == "__main__":
    unittest.main()
