#!/usr/bin/env python3
"""Display precision and wide exact-number regression tests for the prose gate."""
from decimal import Decimal, localcontext
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import check_prose_numbers as checker
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

    def test_explicit_pointer_cannot_borrow_an_unrelated_matching_number(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);docs=root/'docs';docs.mkdir();artifacts=root/'artifacts';artifacts.mkdir()
            (docs/'lesson.md').write_text('Observed magnitude 0.1234.\n')
            artifact=artifacts/'evidence.json'
            artifact.write_text(json.dumps({'unrelated':0.1234,'selected':'0.5678','array':['0.1234','0.5678']}))
            registry=root/'bindings.toml'
            def check(pointer):
                extra= 'source_pointer = '+json.dumps(pointer) if isinstance(pointer,str) else 'source_pointers = '+json.dumps(pointer)
                registry.write_text('schema_version = "0.1.0"\n[[binding]]\npath = "docs/lesson.md"\nline = 1\nliteral = "0.1234"\nsource_artifact = "artifacts/evidence.json"\nsource_sha256 = '+json.dumps(checker.sha256(artifact))+'\nderivation = "selected observation"\n'+extra+'\n')
                with patch.multiple(checker,ROOT=root,DOCS=docs,ARTIFACTS=artifacts,BINDINGS=registry),redirect_stdout(io.StringIO()):
                    return checker.main()
            self.assertEqual(check('/selected'),1)
            self.assertEqual(check('/missing'),1)
            self.assertEqual(check('/array/0'),0)
            self.assertEqual(check(['/array/0','/array/1']),1)
            self.assertEqual(check('/array/-1'),1)

    def test_pointer_rejects_non_numeric_or_nonfinite_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            artifact=Path(temporary)/'evidence.json'
            artifact.write_text(json.dumps({'bad':[True,{},'NaN','not a number']}))
            for k in range(4):
                with self.assertRaises((ValueError,checker.InvalidOperation)):
                    checker.pointer_values({'source_pointer':f'/bad/{k}'},artifact)


if __name__ == "__main__":
    unittest.main()
