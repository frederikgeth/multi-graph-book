#!/usr/bin/env python3
"""Display precision and wide exact-number regression tests for the prose gate."""
from decimal import Decimal, localcontext
import unittest

from check_prose_numbers import matches_displayed_number


class ProseNumberTests(unittest.TestCase):
    def test_wide_artifact_integer_does_not_crash_or_match_small_literal(self):
        self.assertFalse(matches_displayed_number(Decimal(10 ** 90 + 1), "0.1234"))
        self.assertTrue(matches_displayed_number(Decimal(10 ** 90), "1.0000e90"))

    def test_scientific_precision_does_not_collapse_to_zero(self):
        self.assertFalse(matches_displayed_number(Decimal(0), "1.2345e-6"))
        self.assertFalse(matches_displayed_number(Decimal("0.000001"), "1.2345e-6"))
        self.assertTrue(matches_displayed_number(Decimal("0.00000123450001"), "1.2345e-6"))

    def test_rounding_and_sign_remain_discriminating(self):
        self.assertTrue(matches_displayed_number(Decimal("0.123449"), "0.1234"))
        self.assertFalse(matches_displayed_number(Decimal("0.123451"), "0.1234"))
        self.assertTrue(matches_displayed_number(Decimal("-0.123449"), "-0.1234"))
        self.assertFalse(matches_displayed_number(Decimal("0.123449"), "-0.1234"))

    def test_nonfinite_values_are_not_evidence(self):
        for value in ("NaN", "sNaN", "Infinity", "-Infinity"):
            self.assertFalse(matches_displayed_number(Decimal(value), "0.0000"))

    def test_local_precision_is_not_changed(self):
        with localcontext() as context:
            context.prec = 3
            self.assertTrue(matches_displayed_number(Decimal("12.34560001"), "12.3456"))
            self.assertEqual(context.prec, 3)


if __name__ == "__main__":
    unittest.main()
