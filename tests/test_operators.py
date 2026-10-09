"""The railroad registry. No Home Assistant."""

import unittest

from _load import load

operators = load("operators")
sources_base = load("sources.base")
attributes = load("attributes")


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

    def test_every_extra_key_can_reach_the_map(self):
        # A key an adapter may add but attributes.py drops would be dead.
        for key in sources_base.EXTRA_KEYS:
            self.assertIn(key, attributes.PASSTHROUGH)


if __name__ == "__main__":
    unittest.main()
