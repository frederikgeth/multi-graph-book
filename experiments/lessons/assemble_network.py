#!/usr/bin/env python3
"""From named equipment to nodal equations: exact, fixed resistive teaching case.

No solver package, files, or network access. Values are V, A, S, and W.
The equipment evaluator is separate from matrix stamping; both share input data.
"""
from fractions import Fraction as F
import argparse

NODES = ('s', 'm', 't')
BRANCHES = (('e1', 's', 'm', F(2)), ('e2', 'm', 't', F(1)))


def assemble(order=NODES, load=F(1, 2), load_node='t', branches=BRANCHES):
    index = {name: k for k, name in enumerate(order)}
    y = [[F(0) for _ in order] for _ in order]
    for _, tail, head, g in branches:
        i, j = index[tail], index[head]
        y[i][i] += g
        y[j][j] += g
        y[i][j] -= g
        y[j][i] -= g
    y[index[load_node]][index[load_node]] += load
    return y


def linear_solve(a, b):
    """Small exact Gaussian elimination with row pivoting, for this lesson."""
    rows = [list(row) + [rhs] for row, rhs in zip(a, b)]
    for k in range(len(rows)):
        pivot = next((j for j in range(k, len(rows)) if rows[j][k]), None)
        if pivot is None:
            raise ValueError('singular retained system')
        rows[k], rows[pivot] = rows[pivot], rows[k]
        divisor = rows[k][k]
        rows[k] = [value / divisor for value in rows[k]]
        for j in range(len(rows)):
            if j != k:
                scale = rows[j][k]
                rows[j] = [v - scale * w for v, w in zip(rows[j], rows[k])]
    return [row[-1] for row in rows]


def solve(order=NODES, load=F(1, 2), load_node='t', branches=BRANCHES):
    y = assemble(order, load, load_node, branches)
    source = order.index('s')
    free = [k for k in range(len(order)) if k != source]
    vfree = linear_solve([[y[i][j] for j in free] for i in free],
                         [-y[i][source] * 12 for i in free])
    volts = {'s': F(12)}
    volts.update({order[k]: v for k, v in zip(free, vfree)})
    return y, volts


def source_check(volts, load=F(1, 2)):
    """Re-evaluate original equipment, never the assembled matrix."""
    net_out = {name: F(0) for name in NODES}
    currents = {}
    dissipation = F(0)
    for name, tail, head, g in BRANCHES:
        drop = volts[tail] - volts[head]
        current = g * drop
        currents[name] = current
        net_out[tail] += current
        net_out[head] -= current
        dissipation += drop * current
    load_current = load * volts['t']
    net_out['t'] += load_current
    dissipation += volts['t'] * load_current
    return {'currents': currents, 'load_current': load_current,
            'kcl': {n: net_out[n] for n in ('m', 't')},
            'power_mismatch': volts['s'] * net_out['s'] - dissipation,
            'source_voltage_error': volts['s'] - 12}


def checks():
    _, v = solve()
    assert v == {'s': 12, 'm': F(72, 7), 't': F(48, 7)}
    good = source_check(v)
    assert good['currents'] == {'e1': F(24, 7), 'e2': F(24, 7)}
    assert all(x == 0 for x in good['kcl'].values()) and good['power_mismatch'] == 0
    assert solve(('t', 's', 'm'))[1] == v
    reversed_edges = tuple((name, head, tail, g) for name, tail, head, g in BRANCHES)
    assert assemble(branches=reversed_edges) == assemble()
    wrong = solve(load_node='m')[1]
    assert wrong == {'s': 12, 'm': F(48, 5), 't': F(48, 5)}
    assert any(source_check(wrong)['kcl'].values())
    altered = dict(v, t=v['t'] + 1)
    assert any(source_check(altered)['kcl'].values())
    assert solve(load=F(1, 4))[1]['t'] == F(96, 11)
    floating = assemble(load=F(0))
    assert all(sum(row) == 0 for row in floating)
    assert all(value == 12 for value in solve(load=F(0))[1].values())
    print('Assembly checks pass: analytic solution, permutation, orientation, wrong attachment, altered state, changed load, gauge.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--misattach-load', action='store_true')
    args = parser.parse_args()
    if args.check:
        checks()
        return
    y, volts = solve(load_node='m' if args.misattach_load else 't')
    print('Node order: s, m, t')
    print('Y [S]:')
    for row in y:
        print('  ' + ', '.join(map(str, row)))
    for name in NODES:
        print(f'U_{name}: {volts[name]} V')
    audit = source_check(volts)
    for name, value in audit['currents'].items():
        print(f'I_{name}: {value} A')
    print('Source equipment KCL: ' + ('pass' if not any(audit['kcl'].values()) else 'fail'))
    print(f"Source equipment power mismatch: {audit['power_mismatch']} W")


if __name__ == '__main__':
    main()
