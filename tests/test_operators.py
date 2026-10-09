"""The railroad registry. No Home Assistant."""

import unittest

from _load import load

operators = load("operators")
sources_base = load("sources.base")
attributes = load("attributes")
amtrak = load("operators.amtrak")

from saw_livetrack.gtfs.realtime import Obs  # noqa: E402


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
    """Lee 2026-10-09 16:43: odd numbers D, even C, a star."""

    def obs(self, train):
        return Obs(vehicle_id="x", lat=0.0, lon=0.0, observed_at=None, in_service=True,
                   train=train, line=None, reported_course=None, trip_id="x")

    def test_odd_is_d_blue_edge_red_number(self):
        s = amtrak.amtrak_styling(self.obs("5"))
        self.assertEqual(s["marker_shape"], "star")
        self.assertEqual((s["marker_ring_color"], s["marker_label_color"]), ("#3C3B6E", "#B22234"))
        self.assertEqual((s["marker_color"], s["marker_label_outline_color"]), ("#FFFFFF", "#FFFFFF"))

    def test_even_is_c_red_edge_blue_number(self):
        s = amtrak.amtrak_styling(self.obs("2150"))
        self.assertEqual((s["marker_ring_color"], s["marker_label_color"]), ("#B22234", "#3C3B6E"))

    def test_the_arrow_is_the_edge_outlined_white(self):
        for n, edge in (("5", "#3C3B6E"), ("6", "#B22234")):
            s = amtrak.amtrak_styling(self.obs(n))
            self.assertEqual((s["marker_arrow_color"], s["marker_arrow_outline_color"]), (edge, "#FFFFFF"))

    def test_no_number_no_style(self):
        for n in (None, "", "v28", "5A"):
            self.assertEqual(amtrak.amtrak_styling(self.obs(n)), {})

    def test_every_colour_is_the_contracts_form(self):
        import re
        for n in ("1", "2"):
            for k, v in amtrak.amtrak_styling(self.obs(n)).items():
                if k.endswith("_color"):
                    self.assertRegex(v, re.compile(r"^#[0-9A-Fa-f]{6}$"), k)

    def test_amtrak_uses_it_and_the_map_gets_the_shape(self):
        self.assertIs(operators.OPERATORS["amtrak"].styling, amtrak.amtrak_styling)
        rec = {"vehicle_id": "5-8", "marker_label": "5", "in_service": True,
               **amtrak.amtrak_styling(self.obs("5"))}
        a = attributes.to_attributes(rec, "amtrak")
        for k in ("marker_shape", "marker_color", "marker_ring_color", "marker_label_color",
                  "marker_label_outline_color", "marker_arrow_color", "marker_arrow_outline_color"):
            self.assertIn(k, a)


if __name__ == "__main__":
    unittest.main()
