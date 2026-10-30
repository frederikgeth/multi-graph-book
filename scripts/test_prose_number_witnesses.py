#!/usr/bin/env python3
"""Regression checks for arithmetic/reference choices in prose witnesses."""
from decimal import Decimal as D
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f'experiments/lessons/{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


recorded = load('recorded_generator_bound')
arithmetic = load('prose_number_witnesses')


class WitnessTests(unittest.TestCase):
    def data(self):
        return json.loads(recorded.INPUT.read_text(), parse_float=D, parse_int=D)

    def test_frozen_reconstruction_and_changed_current(self):
        data = self.data()
        values = recorded.reconstruct(data)
        for phase in ('a', 'b', 'c'):
            self.assertEqual(D(values[phase]['excess_W']).quantize(D('.00001')), D('.00997'))
        data['generator_result']['a']['crg'] += D('.001')
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            recorded.reconstruct(data)

    def test_boundary_change_changes_observation(self):
        data = self.data()
        before = recorded.reconstruct(data)
        data['generator_input']['p_max'][0] -= D(1)
        data['audit_rows'][0]['residual'] += D(1)
        after = recorded.reconstruct(data)
        self.assertAlmostEqual(D(after['a']['excess_W'])-D(before['a']['excess_W']), D(1))
        self.assertEqual(after['b'], before['b'])

    def test_neutral_reference_is_used(self):
        data = self.data()
        # Earth phase voltage 10+j3, neutral 2+j1, injection 2-j1:
        # P=Re((8+j2)*(2+j1))=14, not earth-referenced P=17.
        data['bus_result'] = {'n': {'vr': D(2), 'vi': D(1)},
                              **{p: {'vr': D(10), 'vi': D(3)} for p in ('a', 'b', 'c')}}
        data['generator_result'] = {p: {'crg': D(2), 'cig': D(-1), 'pg': D(14)} for p in ('a', 'b', 'c')}
        data['generator_input']['p_max'] = [D(13)]*3
        for row in data['audit_rows']:
            row['residual'] = D(1)
        self.assertEqual(recorded.reconstruct(data)['a']['excess_W'], '1')
        data['generator_input']['configuration'] = 'DELTA'
        with self.assertRaisesRegex(ValueError, 'WYE'):
            recorded.reconstruct(data)

    def test_exact_atan_bracket_and_all_point_invariants(self):
        lo, hi = arithmetic.atan_bounds(arithmetic.F(1, 10))
        self.assertLess(lo, hi)
        self.assertLess(hi-lo, arithmetic.F(1, 10**100))
        with self.assertRaises(ValueError):
            arithmetic.atan_bounds(arithmetic.F(1))
        # Executes exact ampere-turn, ideal-power, leakage/excitation power,
        # and cyclic-voltage invariants across the declared witness points.
        result = arithmetic.calculations()
        self.assertEqual(result['precision_decimal_digits'], 90)


if __name__ == '__main__':
    unittest.main()
