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
                registry.write_text('schema_version = "0.2.0"\n[[binding]]\npath = "docs/lesson.md"\nsection = "_preamble"\nliteral = "0.1234"\nsource_artifact = "artifacts/evidence.json"\nsource_sha256 = '+json.dumps(checker.sha256(artifact))+'\nderivation = "selected observation"\n'+extra+'\n')
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

    def run_registry(self, lesson, bindings):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);docs=root/'docs';docs.mkdir();artifacts=root/'artifacts';artifacts.mkdir()
            (docs/'lesson.md').write_text(lesson)
            artifact=artifacts/'evidence.json';artifact.write_text(json.dumps({'value':'0.1234'}))
            registry=root/'bindings.toml'
            entries=''.join('[[binding]]\npath = "docs/lesson.md"\nliteral = "0.1234"\n'+extra
                            +'source_artifact = "artifacts/evidence.json"\nsource_sha256 = '+json.dumps(checker.sha256(artifact))
                            +'\nsource_pointer = "/value"\nderivation = "selected observation"\n' for extra in bindings)
            registry.write_text('schema_version = "0.2.0"\n'+entries)
            with patch.multiple(checker,ROOT=root,DOCS=docs,ARTIFACTS=artifacts,BINDINGS=registry),redirect_stdout(io.StringIO()):
                return checker.main()

    def test_binding_survives_edits_above_its_line(self):
        binding=['section = "result"\n']
        self.assertEqual(self.run_registry('# Intro\n\n## Result\nValue 0.1234.\n',binding),0)
        self.assertEqual(self.run_registry('# Intro\nNew paragraph.\n\nMore text.\n\n## Result\nValue 0.1234.\n',binding),0)
        self.assertEqual(self.run_registry('# Intro\n\n## [Result](@id result)\nValue 0.1234.\n',binding),0)
        # Moving the literal to another section is a meaningful change and must fail.
        self.assertEqual(self.run_registry('# Intro\nValue 0.1234.\n\n## Result\nNone.\n',binding),1)

    def test_repeated_literal_requires_explicit_occurrence(self):
        text='## Result\nFirst 0.1234, then 0.1234 again.\n'
        self.assertEqual(self.run_registry(text,['section = "result"\n','section = "result"\noccurrence = 2\n']),1)
        self.assertEqual(self.run_registry(text,['section = "result"\noccurrence = 1\n','section = "result"\noccurrence = 2\n']),0)

    def test_line_keys_are_rejected(self):
        self.assertEqual(self.run_registry('## Result\nValue 0.1234.\n',['section = "result"\nline = 2\n']),1)

    def test_fenced_code_headings_do_not_change_sections(self):
        text='## Result\n```sh\n# not a heading\n```\nValue 0.1234.\n'
        self.assertEqual(self.run_registry(text,['section = "result"\n']),0)


if __name__ == "__main__":
    unittest.main()
