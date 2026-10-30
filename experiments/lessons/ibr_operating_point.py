#!/usr/bin/env python3
"""Exact arithmetic for the book's single-pair IBR tutorial.

RMS phasors; positive P and Q are injected into the network. This checks
supplied local points, not a network solution or a physical controller.
Only Python's standard library is used. No files are written.
"""
import argparse
from fractions import Fraction as F
from math import isqrt
import unittest

PHASE = (F(12), F(4))
NEUTRAL = (F(3), F(4))
CURRENT = (F(4, 3), F(5, 9))
# Constant-PF target f = +12/13 and minimum PF m = 4/5, each with its exact
# complement sqrt(1 - a^2). Distinct values keep the constant-PF ray strictly
# inside the minimum-PF wedge, so the two laws are visibly different.
TARGET, TARGET_COMPLEMENT = F(12, 13), F(5, 13)
MINIMUM, MINIMUM_COMPLEMENT = F(4, 5), F(3, 5)
# Requested Volt-var graph, in the package field order q_limits=[q_absorb, q_inject].
BREAKPOINTS = (F(8), F(9), F(11), F(12))
Q_ABSORB, Q_INJECT = F(-3, 5), F(11, 25)
RATING = F(20)


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def magnitude_squared(z):
    return sum(v * v for v in z)


def power(voltage, current):
    ur, ui = voltage
    ir, ii = current
    return ur * ir + ui * ii, ui * ir - ur * ii


def residuals(p, q, q_min):
    return {
        'constant_VA': abs(TARGET * q + TARGET_COMPLEMENT * p),
        'generation_W': max(F(0), -p),
        'minimum_upper_VA': max(F(0), MINIMUM * q - MINIMUM_COMPLEMENT * p),
        'minimum_lower_VA': max(F(0), -MINIMUM * q - MINIMUM_COMPLEMENT * p),
        'q_cap_var': max(F(0), q_min - q),
    }


def requested_q(voltage_squared):
    """Stated PWL curve times the branch rating, evaluated exactly.

    Flat sections compare squared magnitudes and need no square root. Ramp
    sections are evaluated only for a rational magnitude; this lesson makes
    no approximate root choice.
    """
    x1, x2, x3, x4 = BREAKPOINTS
    q_inject, q_absorb = RATING * Q_INJECT, RATING * Q_ABSORB
    v2 = F(voltage_squared)
    if v2 < 0:
        raise ValueError('squared magnitude must be nonnegative')
    if v2 <= x1 * x1:
        return q_inject
    if x2 * x2 <= v2 <= x3 * x3:
        return F(0)
    if v2 >= x4 * x4:
        return q_absorb
    nr, dr = isqrt(v2.numerator), isqrt(v2.denominator)
    if nr * nr != v2.numerator or dr * dr != v2.denominator:
        raise ValueError('the exact ramp calculation requires a rational magnitude')
    u = F(nr, dr)
    if u < x2:
        return q_inject * (x2 - u) / (x2 - x1)
    return q_absorb * (u - x3) / (x4 - x3)


def lesson(q_min=F(-2)):
    if q_min > 0:
        raise ValueError('this lesson requires q_min <= 0')
    voltage = subtract(PHASE, NEUTRAL)
    p, q = power(voltage, CURRENT)
    endpoint_p = -TARGET * q_min / TARGET_COMPLEMENT
    points = {'A': (p, q), 'B': (p, q_min), 'C': (endpoint_p, q_min)}
    return {
        'voltage': voltage,
        'pn_squared_V2': magnitude_squared(voltage),
        'pg_squared_V2': magnitude_squared(PHASE),
        'points': points,
        'residuals': {name: residuals(*point, q_min) for name, point in points.items()},
    }


class LessonChecks(unittest.TestCase):
    def test_phasors_and_power(self):
        result = lesson()
        self.assertEqual(result['voltage'], (9, 0))
        self.assertEqual(result['points']['A'], (12, -5))
        self.assertEqual((result['pn_squared_V2'], result['pg_squared_V2']), (81, 160))
        self.assertEqual(requested_q(result['pn_squared_V2']), 0)
        self.assertEqual(requested_q(result['pg_squared_V2']), -12)
        self.assertEqual([requested_q(F(v)**2) for v in (8, F(17, 2), 9, 11, F(23, 2), 12)],
                         [F(44, 5), F(22, 5), 0, 0, -6, -12])

    def test_distinct_failure_rows(self):
        rows = lesson()['residuals']
        self.assertEqual([k for k, v in rows['A'].items() if v], ['q_cap_var'])
        self.assertEqual(rows['A']['q_cap_var'], 3)
        self.assertEqual([k for k, v in rows['B'].items() if v], ['constant_VA'])
        self.assertEqual(rows['B']['constant_VA'], F(36, 13))
        self.assertEqual(lesson()['points']['C'], (F(24, 5), -2))
        self.assertTrue(all(v == 0 for v in rows['C'].values()))

    def test_constant_pf_ray_is_inside_the_minimum_wedge(self):
        # With f != m the two laws differ: on the ray, both minimum-PF rows
        # have strictly positive slack for every P > 0.
        for p in (F(1, 10), F(1), F(12)):
            q = -TARGET_COMPLEMENT * p / TARGET
            self.assertLess(MINIMUM * q - MINIMUM_COMPLEMENT * p, 0)
            self.assertLess(-MINIMUM * q - MINIMUM_COMPLEMENT * p, 0)

    def test_endpoint_bounds_the_declared_intersection(self):
        # On the equality ray, points below C pass; any positive increment
        # above C violates the Q cap. Check several cap choices and steps.
        for cap in (F(0), F(-1), F(-2), F(-5)):
            endpoint = lesson(cap)['points']['C'][0]
            for fraction in (F(0), F(1, 7), F(1, 2), F(1)):
                p = endpoint * fraction
                q = -TARGET_COMPLEMENT * p / TARGET
                self.assertTrue(all(v == 0 for v in residuals(p, q, cap).values()))
            for step in (F(1, 100), F(1), F(10)):
                p = endpoint + step
                q = -TARGET_COMPLEMENT * p / TARGET
                self.assertGreater(residuals(p, q, cap)['q_cap_var'], 0)

    def test_current_reference_reversal_preserves_power(self):
        u = subtract(PHASE, NEUTRAL)
        self.assertEqual(power(u, CURRENT), power(tuple(-x for x in u), tuple(-x for x in CURRENT)))

    def test_common_voltage_shift_preserves_pn_but_changes_pg(self):
        shift = (F(2), F(-1))
        phase = tuple(x + y for x, y in zip(PHASE, shift))
        neutral = tuple(x + y for x, y in zip(NEUTRAL, shift))
        self.assertEqual(subtract(phase, neutral), subtract(PHASE, NEUTRAL))
        self.assertNotEqual(magnitude_squared(phase), magnitude_squared(PHASE))

    def test_aggregate_pf_hides_a_branch_failure(self):
        ps, qs = (1, 10, 10), (3, 0, 0)
        # Compare squared ratios, avoiding rounding and a square root.
        self.assertGreater(F(sum(ps)**2, sum(ps)**2 + sum(qs)**2), MINIMUM * MINIMUM)
        self.assertEqual(residuals(F(ps[0]), F(qs[0]), F(-2))['minimum_upper_VA'], F(9, 5))

    def test_origin_and_absorption(self):
        self.assertTrue(all(v == 0 for v in residuals(F(0), F(0), F(-2)).values()))
        # Equality alone admits absorption; the generation row rejects it.
        r = residuals(F(-12), F(5), F(-2))
        self.assertEqual(r['constant_VA'], 0)
        self.assertEqual(r['generation_W'], 12)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--q-min', type=F, default=F(-2), help='reactive injection lower bound in var (<= 0)')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(LessonChecks)
        raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
    if args.q_min > 0:
        parser.error('--q-min must be <= 0 for this lesson')
    result = lesson(args.q_min)
    print('Single-pair RMS phasors; injection signs; constant PF f = +12/13; minimum PF m = 4/5.')
    print(f"PN voltage: {result['voltage'][0]} + j{result['voltage'][1]} V")
    print(f"Squared monitor magnitudes: PN = {result['pn_squared_V2']} V^2; PG = {result['pg_squared_V2']} V^2")
    print(f"Alternative requested PWL targets: PN = {requested_q(result['pn_squared_V2'])} var; PG = {requested_q(result['pg_squared_V2'])} var")
    for name, (p, q) in result['points'].items():
        print(f'{name}: P = {p} W, Q = {q} var')
        for row, value in result['residuals'][name].items():
            print(f'  {row}: {value}')
    print('C is the upper endpoint of the three-constraint local intersection.')
    print('No network feasibility, controller dynamics or package applicability is certified.')


if __name__ == '__main__':
    main()
