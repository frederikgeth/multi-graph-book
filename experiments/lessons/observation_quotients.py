#!/usr/bin/env python3
"""Exact finite witnesses: a reference quotient, observable modes and rejected lifts.

This book-owned algebraic example does not implement a package audit or solver.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from delta_connection_maps import incidence, action, transpose
from solution_multiplicity import rational_json

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).with_suffix('.json')
OUTPUT = ROOT / 'experiments/generated/observation-quotients.json'


def rank(matrix):
    """Exact row rank; small rational matrices only."""
    a = [list(map(F, row)) for row in matrix]
    if not a or any(len(row) != len(a[0]) for row in a):
        raise ValueError('a nonempty rectangular matrix is required')
    pivot = 0
    for col in range(len(a[0])):
        found = next((k for k in range(pivot, len(a)) if a[k][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        scale = a[pivot][col]
        a[pivot] = [x / scale for x in a[pivot]]
        for k in range(len(a)):
            if k != pivot:
                scale = a[k][col]
                a[k] = [x - scale*y for x, y in zip(a[k], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def build():
    inputs = json.loads(FIXTURE.read_text())
    b = inputs['floating']
    floating_g, injection, offset, ge, vmax = (F(b[k]) for k in (
        'conductance_S', 'injection_A', 'offset_V', 'fixed_earth_shunt_S', 'absolute_upper_bound_V'))
    base = list(map(F, b['base_voltages_V']))
    floating = []
    for v in (base, [x+offset for x in base]):
        u = v[0]-v[1]
        i = floating_g*u
        floating.append(dict(voltage_V=v, difference_V=u, current_A=i, loss_W=u*i,
            kcl_residual_A=[i-injection, -i+injection],
            recovered_reference_V=[x-v[1] for x in v],
            fixed_earth_shunt_current_A=ge*v[1],
            augmented_kcl_residual_A=[i-injection, -i+injection+ge*v[1]],
            absolute_bounds_pass=all(0 <= x <= vmax for x in v),
            reference_dependent_objective_V2=v[1]**2))
    b = inputs['parallel']
    total = F(b['total_current_A']); caps = list(map(F, b['member_caps_A']))
    lower, upper = max(-caps[0], total-caps[1]), min(caps[0], total+caps[1])
    parallel = []
    for alpha in map(F, b['first_currents_A']):
        currents = [alpha, total-alpha]
        parallel.append(dict(member_currents_A=currents, total_A=sum(currents),
            kcl_residual_A=sum(currents)-total, terminal_power_W=F(0),
            member_caps_pass=all(abs(i) <= cap for i, cap in zip(currents, caps)),
            squared_current_objective_A2=sum(i*i for i in currents)))
    projection = []
    for t in map(F, [-18, -17, 0, 12, 17, 18]):
        lo, hi = max(-caps[0], t-caps[1]), min(caps[0], t+caps[1])
        recovered = [(lo+hi)/2, t-(lo+hi)/2] if lo <= hi else None
        projection.append(dict(total_A=t, feasible=lo <= hi, recovered_currents_A=recovered))
    b = inputs['delta']
    c = incidence(b['terminals'], b['coil_endpoints']); ct = transpose(c)
    v = list(map(F, b['terminal_voltages_V'])); u = action(c, v)
    g = list(map(F, b['coil_conductances_S']))
    j = [a*b for a, b in zip(g, u)]
    delta = []
    for current in (j, [x+F(b['circulation_A']) for x in j]):
        i = action(ct, current); p = [a*b for a, b in zip(u, current)]
        delta.append(dict(coil_current_A=current, terminal_current_A=i, coil_power_W=p,
            coil_law_residual_A=[a-b for a, b in zip(current, j)],
            terminal_total_power_W=sum(a*b for a, b in zip(v, i)), coil_total_power_W=sum(p)))
    identity = [[int(i == k) for i in range(3)] for k in range(3)]
    sources = [FIXTURE, Path(__file__), Path(__file__).with_name('delta_connection_maps.py'),
               Path(__file__).with_name('solution_multiplicity.py')]
    return rational_json(dict(schema_version='0.1.0', evidence_state='self_checked_exact_finite_witness',
        inputs=inputs, source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        floating=floating, parallel=parallel, projected_totals=projection, parallel_admissible_interval_A=[lower, upper],
        delta_incidence=c, delta_coil_voltages_V=u, delta=delta,
        ranks=dict(floating_equations=rank([[floating_g, -floating_g], [-floating_g, floating_g]]),
            floating_with_reference=rank([[1, -1], [0, 1]]),
            parallel_kcl=rank([[1, 1]]), parallel_with_member_observation=rank([[1, 1], [1, 0]]),
            delta_terminal_map=rank(ct), delta_with_coil_laws=rank(ct+identity),
            delta_with_one_coil_observation=rank(ct+[[1, 0, 0]])),
        not_established=['automatic nonlinear symmetry detection', 'generic feasible-set quotient certification',
                         'native package coverage', 'independent scientific review']))


def check():
    d = build(); a, b = d['floating']
    assert a['voltage_V'] == ['3', '0'] and b['voltage_V'] == ['8', '5']
    for key in ('difference_V', 'current_A', 'loss_W', 'kcl_residual_A', 'recovered_reference_V'):
        assert a[key] == b[key]
    assert a['current_A'] == '6' and a['loss_W'] == '18'
    assert a['kcl_residual_A'] == b['kcl_residual_A'] == ['0', '0']
    assert a['augmented_kcl_residual_A'] == ['0', '0'] and b['augmented_kcl_residual_A'] == ['0', '5']
    assert a['absolute_bounds_pass'] and not b['absolute_bounds_pass']
    assert a['reference_dependent_objective_V2'] == '0' and b['reference_dependent_objective_V2'] == '25'
    assert d['parallel_admissible_interval_A'] == ['2', '7']
    assert [r['member_caps_pass'] for r in d['parallel']] == [True, True, True, False]
    assert all(r['total_A'] == '12' and r['kcl_residual_A'] == r['terminal_power_W'] == '0' for r in d['parallel'])
    assert [r['squared_current_objective_A2'] for r in d['parallel']] == ['104', '72', '74', '80']
    for row in d['projected_totals']:
        assert row['feasible'] == (abs(F(row['total_A'])) <= 17)
        if row['feasible']:
            i1, i2 = map(F, row['recovered_currents_A'])
            assert i1+i2 == F(row['total_A']) and abs(i1) <= 7 and abs(i2) <= 10
        else:
            assert row['recovered_currents_A'] is None
    a, b = d['delta']; c = d['delta_incidence']; ct = transpose(c)
    assert action(c, [1, 1, 1]) == action(ct, [1, 1, 1]) == [0, 0, 0]
    assert d['delta_coil_voltages_V'] == ['2', '2', '-4']
    assert a['terminal_current_A'] == b['terminal_current_A'] == ['14', '2', '-16']
    assert a['coil_law_residual_A'] == ['0', '0', '0'] and b['coil_law_residual_A'] == ['1', '1', '1']
    assert a['coil_power_W'] == ['4', '8', '48'] and b['coil_power_W'] == ['6', '10', '44']
    assert a['terminal_total_power_W'] == a['coil_total_power_W'] == b['coil_total_power_W'] == b['terminal_total_power_W'] == '60'
    assert d['ranks'] == dict(floating_equations=1, floating_with_reference=2, parallel_kcl=1,
        parallel_with_member_observation=2, delta_terminal_map=2, delta_with_coil_laws=3,
        delta_with_one_coil_observation=3)
    # Transfer: one oriented coil has no hidden current direction.
    assert rank(transpose(incidence(['a', 'c'], [('a', 'c')]))) == 1
    print('Exact reference quotient, rejected extensions, observable current family and delta coil-law checks pass.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true'); mode.add_argument('--check', action='store_true')
    args = parser.parse_args(); check()
    content = json.dumps(build(), indent=2, sort_keys=True)+'\n'
    if args.write:
        OUTPUT.write_text(content)
    elif args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != content:
            raise SystemExit('stale witness; run with --write')
    else:
        print(content, end='')


if __name__ == '__main__':
    main()
