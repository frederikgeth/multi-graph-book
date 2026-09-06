#!/usr/bin/env python3
"""A historical evidence snapshot must be writable before the new corpus exists."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import check_neural_benchmark as checker


class SnapshotCheck(unittest.TestCase):
    def test_snapshot_does_not_require_current_retrieval_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report, snapshot = root/'report.json', root/'snapshot.json'
            report.write_text(json.dumps({'status': 'recorded negative result',
                                          'compatibility': {'current_corpus_id': 'stale'}}))
            with (patch.object(checker, 'REPORT', report),
                  patch.object(checker, 'NEGATIVE_RESULT', snapshot),
                  patch.object(checker, 'CONFIG', root/'absent-config.toml'),
                  patch.object(checker, 'CORPUS_MANIFEST', root/'absent-corpus.json'),
                  patch.object(checker, 'evaluate', side_effect=AssertionError('must not evaluate')) as evaluate,
                  patch('sys.argv', ['check_neural_benchmark.py', '--write-negative-result'])):
                self.assertEqual(checker.main(), 0)
                evaluate.assert_not_called()
            evidence = json.loads(snapshot.read_text())
            self.assertEqual(evidence['benchmark'], {'status': 'recorded negative result'})
            self.assertIn('compatibility', json.loads(report.read_text()))


if __name__ == '__main__':
    unittest.main()
