#!/usr/bin/env python3
"""Exact author spot checks for five bounded passages, without package helpers."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(__file__).with_suffix('.json')


def add(a, b): return a[0]+b[0], a[1]+b[1]
def sub(a, b): return a[0]-b[0], a[1]-b[1]
def norm2(a): return a[0]**2+a[1]**2
def power(u, i): return u[0]*i[0]+u[1]*i[1], u[1]*i[0]-u[0]*i[1]
def pair(a, b=0): return F(a), F(b)
def total(xs):
    answer = pair(0)
    for x in xs: answer = add(answer, x)
    return answer


def witnesses():
    # Original phasors, not the displayed answer, are the inputs.
    phase, neutral = pair(4, 6), pair(1, 2)
    pn2 = norm2(sub(phase, neutral))
    assert pn2 == 25
    # If sqrt(52)-sqrt(5) were 5, squaring would require sqrt(5)=11/5.
    assert F(5) != F(11, 5)**2

    voltages = [pair(10, -10), pair(6, 18), pair(-16, -8)]
    currents = [pair(F(3,10), -F(1,10)), pair(-F(1,5), F(3,20)), pair(F(1,10), F(1,20))]
    circulated = [add(i, pair(F(1,2), F(1,5))) for i in currents]
    injection = lambda cs: [sub(cs[k], cs[k-1]) for k in range(3)]
    assert injection(currents) == injection(circulated)
    before = total(power(u, i) for u, i in zip(voltages, currents))
    after = total(power(u, i) for u, i in zip(voltages, circulated))
    assert before == after
    current_caps = [F(7,20), F(3,10), F(1,5)]
    power_caps = [F(6), F(6), F(3)]
    assert all(norm2(i) <= cap**2 for i, cap in zip(currents, current_caps))
    assert all(norm2(power(u,i)) <= cap**2 for u,i,cap in zip(voltages,currents,power_caps))
    assert all(norm2(i) > cap**2 for i,cap in zip(circulated,current_caps))
    assert all(norm2(power(u,i)) > cap**2 for u,i,cap in zip(voltages,circulated,power_caps))

    # Negative magnitude stays fixed; the positive-sequence denominator changes.
    negative = F(1); ratio_cap = F(1,8)
    assert negative/F(10) <= ratio_cap < negative/F(5)
    # Cross multiplication accepts the all-zero origin without defining 0/0.
    assert F(0)**2 <= ratio_cap**2*F(0)**2

    f, b, p = F(4,5), F(3,5), F(4)
    assert f**2+b**2 == 1
    original = abs(f*F(-3)+b*p)
    clipped = abs(f*F(-2)+b*p)
    assert original == 0 and clipped > 0
    tiny = F(1,10**20); tolerance = F(1,10**6)
    assert 0 < tiny < tolerance  # P=0, Q=1 gives weighted excess m, PF ratio 0.

    paths = ['docs/src/reference/numerical-audit-reference.md',
             'docs/src/foundations/ibr-power-factor-controls.md',
             Path(__file__).relative_to(ROOT).as_posix()]
    return {'schema_version':'1.0.0',
            'evidence_state':'bounded_author_algebra_checks_not_external_review',
            'scope':'Only the stated phasor/current points and algebraic counterexamples; no native build, network feasibility, physical adequacy or deployment-rate certificate.',
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
            'checks':{
                'phase_neutral':{'difference_squared_V2':str(pn2), 'magnitude_V':'5',
                                 'subtracting_magnitudes_is_different':True},
                'delta_generator':{'terminal_injections_unchanged':True,
                                   'total_power_VA':[str(x) for x in before],
                                   'original_coil_caps_pass':6, 'circulated_coil_caps_fail':6},
                'sequence_ratio':{'first_ratio':str(negative/F(10)), 'second_ratio':str(negative/F(5)),
                                  'cap':str(ratio_cap), 'zero_origin_polynomial_passes':True,
                                  'zero_origin_ratio':None},
                'constant_pf_clipping':{'original_weighted_residual_VA':str(original),
                                        'clipped_weighted_residual_VA':str(clipped)},
                'tiny_minimum_pf':{'P_W':'0','Q_var':'1','minimum':str(tiny),
                                   'weighted_excess_VA':str(tiny),'tolerance_VA':str(tolerance),
                                   'weighted_check_passes':True,'PF_ratio':'0','exact_envelope_passes':False}}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    expected = json.dumps(witnesses(), indent=2, sort_keys=True)+'\n'
    if args.write: OUTPUT.write_text(expected)
    elif not OUTPUT.is_file() or OUTPUT.read_text() != expected:
        raise SystemExit('Bounded witness snapshot is stale; rerun with --write')
    print('Bounded author witnesses: 5 exact point/observation checks pass')


if __name__ == '__main__':
    main()
