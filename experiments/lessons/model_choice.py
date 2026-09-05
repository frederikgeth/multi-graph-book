#!/usr/bin/env python3
"""Current-sharing choice under declared conductance uncertainty.

Fixed scalar resistive members: g2=1 S, g1 in [8,12] S, both rated 100 A.
Reported timing is local microbenchmark evidence, not a solver comparison.
"""
import argparse
from fractions import Fraction as F
from statistics import median
from timeit import repeat


def evaluate(total):
    nominal = F(10, 11) * total
    endpoints = [g / (g + 1) * total for g in (F(8), F(12))]
    all_member_currents = endpoints + [total - i for i in endpoints]
    worst = max(all_member_currents)
    return {'nominal_first': nominal, 'nominal_margin': 100 - nominal,
            'uncertainty_error': max(abs(i - nominal) for i in endpoints),
            'worst_current': worst, 'robust_margin': 100 - worst,
            'nominal_accept': total <= 110, 'robust_accept': worst <= 100}


def explicit(total):
    drop = total / (10.0 + 1.0)
    members = (10.0 * drop, drop)
    return all(abs(i) <= 100.0 for i in members), members


def reduced(total):
    cap = (10.0 + 1.0) * min(100.0 / 10.0, 100.0 / 1.0)
    drop = total / 11.0
    return abs(total) <= cap, (10.0 * drop, drop)


def robust(total):
    outcomes = []
    for g in (8.0, 12.0):
        drop = total / (g + 1.0)
        outcomes.append((g * drop, drop))
    return all(abs(i) <= 100.0 for pair in outcomes for i in pair), outcomes


def checks():
    low, high = evaluate(F(99)), evaluate(F(109))
    assert low['nominal_accept'] and low['robust_accept']
    assert high['nominal_accept'] and not high['robust_accept']
    assert high['worst_current'] == F(1308, 13)
    assert high['uncertainty_error'] > high['nominal_margin']
    assert evaluate(F(325, 3))['robust_margin'] == 0
    assert explicit(99) == reduced(99)
    assert robust(99)[0] and not robust(109)[0]
    print('Model-choice checks pass: safe margin, reversal near limit, exact robust boundary, nominal recovery.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--benchmark', action='store_true')
    args = parser.parse_args()
    if args.check:
        checks()
        return
    for total in (F(99), F(109)):
        r = evaluate(total)
        print(f'Total current: {total} A')
        print(f"  nominal first-member current: {r['nominal_first']} A")
        print(f"  worst member current over interval: {r['worst_current']} A")
        print(f"  robust current margin: {r['robust_margin']} A")
        print(f"  nominal accepts: {r['nominal_accept']}; robust accepts: {r['robust_accept']}")
    print('Exact robust aggregate cap: 325/3 A')
    if args.benchmark:
        print('Median local time per evaluation including recovery; 7 batches of 10000 calls:')
        for name, fn in [('nominal explicit', explicit), ('nominal reduced', reduced), ('interval robust', robust)]:
            seconds = median(repeat(lambda: fn(109.0), number=10000, repeat=7)) / 10000
            print(f'  {name}: {seconds * 1e6:.3f} microseconds')
        print('Includes local cap/current/check work; excludes imports and I/O. No PF solver or general speed claim.')


if __name__ == '__main__':
    main()
