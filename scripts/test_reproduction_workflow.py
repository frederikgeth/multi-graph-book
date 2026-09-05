#!/usr/bin/env python3
"""Regression checks for evidence comparison and non-overwriting run setup."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from reproduce_clean_fixture import compare_fixture, compare_summary

ROOT = Path(__file__).resolve().parents[1]


class ReproductionChecks(unittest.TestCase):
    def test_only_schema_uri_may_differ(self):
        source = {'meta': {'$schema': 'old'}, 'line': {'l1': {'i_max': 100}}}
        target = copy.deepcopy(source)
        target['meta']['$schema'] = 'new'
        self.assertTrue(compare_fixture(target, source)['engineering_payload_equal'])
        self.assertEqual(source['meta']['$schema'], 'old')
        target['line']['l1']['i_max'] = 101
        with self.assertRaises(ValueError):
            compare_fixture(target, source)

    def test_tolerances_reject_bad_or_nonfinite_results(self):
        reference = {'power_flow.loss': {'value': 1, 'absolute_tolerance': .01}}
        compare_summary({'power_flow': {'loss': 1.001}}, reference)
        for value in (1.02, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                compare_summary({'power_flow': {'loss': value}}, reference)

    def test_existing_directory_is_untouched(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            sentinel = path/'old-evidence.json'
            sentinel.write_text('untouched')
            proc = subprocess.run([sys.executable, str(ROOT/'scripts/reproduce_clean_fixture.py'),
                                   '--mode','current','--output',str(path)], capture_output=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertEqual(sentinel.read_text(), 'untouched')
            self.assertEqual(list(path.iterdir()), [sentinel])

    def test_recorded_profile_is_complete(self):
        profile = json.loads((ROOT/'experiments/reproduction/review-2026-09-06/profile.json').read_text())
        self.assertTrue(profile['expected_summary'])
        self.assertEqual(len(profile['exported_fixture_sha256']), 64)
        self.assertIn('scripts/reproduce_clean_fixture.py', profile['book_source_sha256'])


if __name__ == '__main__':
    unittest.main()
