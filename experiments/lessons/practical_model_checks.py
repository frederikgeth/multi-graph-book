#!/usr/bin/env python3
"""Three exact, standard-library teaching witnesses; no file writes or package API claims.

The field adapter handles only the documented MATPOWER v2 RATE_A/TAP conventions.
The network is a three-arm resistive star; the dispatch example is a scalar LP.
Run normally for worked results, or with --check for executable counterexamples.
"""
import argparse
from dataclasses import dataclass
from fractions import Fraction as F
import unittest


def number(value):
    """Accept finite numeric data, retaining decimal spelling for float inputs."""
    if isinstance(value, bool) or not isinstance(value, (int, float, F)):
        raise ValueError('expected a finite number, not a string or Boolean')
    try:
        return F(str(value))
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError('expected a finite number') from error


@dataclass(frozen=True)
class Rating:
    state: str
    value_MVA: F | None = None

    def __post_init__(self):
        if self.state not in ('finite', 'unbounded', 'unknown', 'not_applicable'):
            raise ValueError('unknown rating state')
        if self.state == 'finite':
            value = number(self.value_MVA)
            if value < 0:
                raise ValueError('negative magnitude bound')
            object.__setattr__(self, 'value_MVA', value)
        elif self.value_MVA is not None:
            raise ValueError('only finite ratings carry numeric bounds')


def decode_rate_a(raw):
    # An absent field is incomplete input, not MATPOWER's explicit zero sentinel.
    if raw is None:
        return Rating('unknown')
    value = number(raw)
    return Rating('unbounded') if value == 0 else Rating('finite', value)


def encode_rate_a(rating):
    if rating.state == 'unbounded':
        return F(0)
    if rating.state == 'finite' and rating.value_MVA > 0:
        return rating.value_MVA
    raise ValueError('this field cannot encode that state without changing meaning')


def rating_check(rating, apparent_power_MVA):
    value = abs(number(apparent_power_MVA))
    if rating.state == 'unknown':
        return 'indeterminate'
    if rating.state == 'not_applicable':
        return 'not_applicable'
    return 'passed' if rating.state == 'unbounded' or value <= rating.value_MVA else 'failed'


def decode_tap(raw):
    if raw is None:
        raise ValueError('missing tap is not a declared line')
    value = number(raw)
    if value < 0:
        raise ValueError('this lesson accepts nonnegative tap magnitudes only')
    return ('line', F(1)) if value == 0 else ('transformer', value)


@dataclass(frozen=True)
class Star:
    # Ordered boundary terminals (a,b,c); center has zero injected current.
    g_S: tuple

    def __post_init__(self):
        g = tuple(number(value) for value in self.g_S)
        if len(g) != 3 or min(g) < 0 or sum(g) == 0:
            raise ValueError('need three nonnegative conductances and a connected center')
        object.__setattr__(self, 'g_S', g)


@dataclass(frozen=True)
class ReducedStar:
    source: Star
    matrix_S: tuple


def compile_star(source):
    g, total = source.g_S, sum(source.g_S)
    matrix = tuple(tuple((g[i] if i == j else 0) - g[i]*g[j]/total
                        for j in range(3)) for i in range(3))
    return ReducedStar(source, matrix)


def source_currents(source, volts):
    # Separate equipment evaluation: recover the center, then apply each arm law.
    center = sum(g*v for g, v in zip(source.g_S, volts))/sum(source.g_S)
    return tuple(g*(v-center) for g, v in zip(source.g_S, volts))


def matrix_currents(reduced, volts):
    return tuple(sum(y*v for y, v in zip(row, volts)) for row in reduced.matrix_S)


def use_cached(reduced, source, volts):
    if reduced.source != source:
        raise ValueError('stale reduction: rebuild from the changed source')
    return matrix_currents(reduced, volts)


def wrong_delete_triangle_edges(reduced):
    # Deliberate bug: open source arm c by deleting its two derived triangle edges.
    ab = -reduced.matrix_S[0][1]
    return ReducedStar(Star((1, 1, 0)), ((ab, -ab, F(0)), (-ab, ab, F(0)), (F(0),)*3))


def dispatch(cost, demand, alpha=1, beta=1):
    """Analytical LP solution; alpha scales the constraint, beta the objective.

    min beta*c*p subject to alpha*(d-p)<=0, with p real and c,d,alpha,beta>0.
    The returned physical marginal cost is the demand derivative of c*p*.
    """
    c, d, a, b = map(number, (cost, demand, alpha, beta))
    if min(c, d, a, b) <= 0:
        raise ValueError('the stated LP domain requires positive inputs')
    multiplier = b*c/a
    return {'p_MW': d, 'physical_cost_per_hour': c*d,
            'raw_multiplier': multiplier, 'physical_marginal_cost': a*multiplier/b}


def duplicate_kkt(cost, demand, p, multipliers):
    # Two copies of d-p<=0, unscaled objective c*p.
    c, d, p = map(number, (cost, demand, p))
    lam = tuple(map(number, multipliers))
    return (len(lam) == 2 and p >= d and min(lam) >= 0
            and sum(lam) == c and all(x*(d-p) == 0 for x in lam))


class ImportChecks(unittest.TestCase):
    def test_zero_sentinel_is_not_a_zero_bound(self):
        self.assertEqual(rating_check(decode_rate_a(0), 10), 'passed')
        self.assertEqual(rating_check(Rating('finite', F(0)), 10), 'failed')

    def test_numeric_round_trip_can_hide_the_bug(self):
        broken_decode, broken_encode = F, lambda rating: rating
        self.assertEqual(broken_encode(broken_decode(0)), 0)
        self.assertNotEqual(rating_check(Rating('finite', broken_decode(0)), 10),
                            rating_check(decode_rate_a(0), 10))

    def test_absence_never_becomes_unbounded(self):
        self.assertEqual(rating_check(decode_rate_a(None), 10), 'indeterminate')
        self.assertEqual(rating_check(Rating('not_applicable'), 10), 'not_applicable')

    def test_unsupported_export_is_refused(self):
        for rating in (Rating('finite', F(0)), Rating('unknown'), Rating('not_applicable')):
            with self.assertRaises(ValueError):
                encode_rate_a(rating)
        for raw in (0, 10, F(7, 2)):
            self.assertEqual(encode_rate_a(decode_rate_a(raw)), raw)

    def test_finite_limits_and_invalid_data(self):
        bound = decode_rate_a(10)
        self.assertEqual(rating_check(bound, -10), 'passed')
        self.assertEqual(rating_check(bound, 11), 'failed')
        for raw in (-1, float('nan'), float('inf'), True, '0'):
            with self.assertRaises(ValueError):
                decode_rate_a(raw)

    def test_unity_ratio_does_not_erase_source_kind(self):
        self.assertEqual(decode_tap(0), ('line', F(1)))
        self.assertEqual(decode_tap(1), ('transformer', F(1)))
        with self.assertRaises(ValueError):
            decode_tap(None)


class UpdateChecks(unittest.TestCase):
    def test_known_star_and_open_arm(self):
        old, new = compile_star(Star((1, 1, 1))), compile_star(Star((1, 1, 0)))
        self.assertEqual(-old.matrix_S[0][1], F(1, 3))
        self.assertEqual(-new.matrix_S[0][1], F(1, 2))
        self.assertEqual(new.matrix_S[2], (0, 0, 0))

    def test_wrong_update_passes_balance_but_fails_equipment(self):
        new = Star((1, 1, 0))
        wrong = wrong_delete_triangle_edges(compile_star(Star((1, 1, 1))))
        self.assertTrue(all(sum(row) == 0 for row in wrong.matrix_S))
        actual = source_currents(new, (1, 0, 0))
        self.assertEqual(actual, (F(1, 2), -F(1, 2), 0))
        self.assertNotEqual(matrix_currents(wrong, (1, 0, 0)), actual)

    def test_stale_cache_rejected_and_rebuild_validated(self):
        old, new = Star((1, 1, 1)), Star((1, 1, 0))
        with self.assertRaises(ValueError):
            use_cached(compile_star(old), new, (1, 0, 0))
        self.assertEqual(use_cached(compile_star(new), new, (1, 0, 0)), (F(1, 2), -F(1, 2), 0))

    def test_basis_checks_for_asymmetric_changed_inputs(self):
        # Basis vectors suffice for equality of these fixed linear maps.
        for source in (Star((1, 1, 1)), Star((1, 1, 0)), Star((1, 2, 0)), Star((2, 3, 4))):
            for i in range(3):
                volts = tuple(F(i == j) for j in range(3))
                self.assertEqual(matrix_currents(compile_star(source), volts), source_currents(source, volts))
        self.assertEqual(-compile_star(Star((1, 2, 0))).matrix_S[0][1], F(2, 3))

    def test_floating_center_outside_inverse_formula(self):
        with self.assertRaises(ValueError):
            Star((0, 0, 0))


class DualChecks(unittest.TestCase):
    def test_same_dispatch_different_raw_multiplier(self):
        a, b = dispatch(50, 10), dispatch(50, 10, alpha=100)
        self.assertEqual(a['p_MW'], b['p_MW'])
        self.assertEqual(a['physical_cost_per_hour'], b['physical_cost_per_hour'])
        self.assertEqual((a['raw_multiplier'], b['raw_multiplier']), (50, F(1, 2)))

    def test_physical_sensitivity_includes_both_scales(self):
        base = dispatch(50, 10, alpha=100, beta=F(1, 1000))
        step = F(1, 10)
        changed = dispatch(50, 10+step, alpha=100, beta=F(1, 1000))
        slope = (changed['physical_cost_per_hour']-base['physical_cost_per_hour'])/step
        self.assertEqual(base['physical_marginal_cost'], slope)
        self.assertNotEqual(base['raw_multiplier'], slope)

    def test_duplicate_constraints_have_nonunique_multipliers(self):
        for pair in ((50, 0), (0, 50), (20, 30)):
            self.assertTrue(duplicate_kkt(50, 10, 10, pair))
        self.assertFalse(duplicate_kkt(50, 10, 10, (50, 50)))
        self.assertFalse(duplicate_kkt(50, 10, 9, (20, 30)))

    def test_domain_not_silently_extended(self):
        with self.assertRaises(ValueError):
            dispatch(50, 10, alpha=-1)


def demonstrate():
    print('IMPORT: raw RATE_A=0, tested at 10 MVA')
    print('  documented meaning:', rating_check(decode_rate_a(0), 10))
    print('  incorrect literal bound:', rating_check(Rating('finite', F(0)), 10))
    print('  missing rating:', rating_check(decode_rate_a(None), 10))
    print('  TAP=0:', decode_tap(0), '; TAP=1:', decode_tap(1))
    print('UPDATE: open star arm c; terminal voltages (1,0,0) V')
    old, new = Star((1, 1, 1)), Star((1, 1, 0))
    print('  rebuilt boundary current A:', matrix_currents(compile_star(new), (1, 0, 0)))
    print('  wrong edge deletion current A:', matrix_currents(wrong_delete_triangle_edges(compile_star(old)), (1, 0, 0)))
    print('  original-equipment current A:', source_currents(new, (1, 0, 0)))
    print('DUALS: c=50 currency/MWh, d=10 MW')
    for alpha, beta in ((1, 1), (100, 1), (100, F(1, 1000))):
        print(f'  alpha={alpha}, beta={beta}:', dispatch(50, 10, alpha, beta))
    print('Checks are teaching witnesses, not a full importer, general updater, or OPF solver.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        suite = unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
        raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
    demonstrate()
