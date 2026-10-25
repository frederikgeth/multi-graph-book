#!/usr/bin/env python3
"""Scalar transformer relation, finite stamp and bordered equations in SI units.

Four terminal voltages are [primary phase, primary neutral, secondary phase,
secondary neutral]. Both winding currents point into the transformer. The
primary voltage is imposed; a resistor and magnetizing shunt span the secondary,
whose neutral has one finite earth connection and a diagnostic current injection.
"""

import argparse
import math
from zero_voltage_kcl import finite_complex

LOAD_Y = 1 / 23
MAG_Y = 0.001 - 0.002j
GROUND_Y = 0.1
GROUND_INJECTION = 0.2


def turns_ratio(primary, secondary):
    for value in (primary, secondary):
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise ValueError("both nominal winding voltages must be positive finite numbers")
    ratio = primary / secondary
    if not math.isfinite(ratio) or ratio == 0:
        raise ValueError("turns ratio is not representable")
    return ratio


def matvec(matrix, vector):
    return [sum(a*b for a, b in zip(row, vector)) for row in matrix]


def stamp(matrix, coefficients, admittance):
    for i, ci in enumerate(coefficients):
        for j, cj in enumerate(coefficients):
            matrix[i][j] += ci * admittance * cj


def solve(matrix, rhs):
    """Small partial-pivoting solve for the teaching matrices, not a network API."""
    rows = [list(row) + [b] for row, b in zip(matrix, rhs)]
    n = len(rhs)
    for k in range(n):
        pivot = max(range(k, n), key=lambda i: abs(rows[i][k]))
        rows[k], rows[pivot] = rows[pivot], rows[k]
        if rows[k][k] == 0:
            raise ValueError("singular teaching matrix")
        divisor = rows[k][k]
        rows[k] = [x/divisor for x in rows[k]]
        for i in range(n):
            if i != k:
                factor = rows[i][k]
                rows[i] = [x-factor*y for x, y in zip(rows[i], rows[k])]
    return [row[-1] for row in rows]


def blocks(z, ratio=2, y0=1, magnetizing_copies=1, grounding_copies=1):
    if not math.isfinite(y0) or y0 <= 0:
        raise ValueError("port scale y0 must be positive and finite")
    c = [1, -1, -ratio, ratio]
    passive = [[0j for _ in range(4)] for _ in range(4)]
    stamp(passive, [0, 0, 1, -1], magnetizing_copies*MAG_Y)
    passive[3][3] += grounding_copies*GROUND_Y
    border = [row + [y0*ci] for row, ci in zip(passive, c)]
    border.append([y0*ci for ci in c] + [-y0*y0*z])
    return c, passive, border


def boundary_solution(matrix, primary=230):
    n = len(matrix)
    matrix = [list(row) for row in matrix]
    stamp(matrix, [0, 0, 1, -1] + [0]*(n-4), LOAD_Y)
    fixed = [complex(primary), 0j]
    free = list(range(2, n))
    rhs = [0j]*n
    rhs[3] = GROUND_INJECTION
    reduced_rhs = [rhs[i] - sum(matrix[i][j]*fixed[j] for j in range(2)) for i in free]
    return fixed + solve([[matrix[i][j] for j in free] for i in free], reduced_rhs)


def scalar_solution(z, primary=230, ratio=2):
    # Independently reduced scalar equations: a*i = (YL+Ym)*u2 and u1-a*u2=z*i.
    secondary = ratio*primary / (ratio**2 + z*(LOAD_Y+MAG_Y))
    current = (LOAD_Y+MAG_Y)*secondary / ratio
    neutral = GROUND_INJECTION / GROUND_Y
    return [complex(primary), 0j, secondary+neutral, complex(neutral)], current


def terminal_currents(volts, current, ratio=2):
    secondary = volts[2]-volts[3]
    return [current, -current, -ratio*current+MAG_Y*secondary,
            ratio*current-MAG_Y*secondary+GROUND_Y*volts[3]]


def check():
    for values in ((None, 115), (230, None), (True, 115), (230, 0), (float('nan'), 115)):
        try:
            turns_ratio(*values)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid nominal voltage accepted")
    assert turns_ratio(230, 115) == 2
    errors = []
    ideal, _ = scalar_solution(0j)
    for z in (0.2+0.1j, 1e-3+0j, 1e-6+0j, 0j):
        volts, current = scalar_solution(z)
        errors.append(abs(volts[2]-ideal[2]))
        for scale in (0.1, 1, 10):
            c, shunts, bordered = blocks(z, y0=scale)
            state = boundary_solution(bordered)
            assert max(abs(a-b) for a, b in zip(state[:4], volts)) < 1e-9
            assert abs(scale*state[4]-current) < 1e-9
            terminal = terminal_currents(volts, current)
            recovered = [v+ci*current for v, ci in zip(matvec(shunts, volts), c)]
            assert max(abs(a-b) for a, b in zip(terminal, recovered)) < 1e-10
            power = sum(v*i.conjugate() for v, i in zip(volts, terminal))
            expected = z*abs(current)**2 + MAG_Y.conjugate()*abs(volts[2]-volts[3])**2 + GROUND_Y*abs(volts[3])**2
            assert abs(power-expected) < 1e-9
        if abs(z) >= 1e-3:
            finite = [list(row) for row in shunts]
            stamp(finite, c, 1/z)
            stamped_volts = boundary_solution(finite)
            assert max(abs(a-b) for a, b in zip(stamped_volts, volts)) < 1e-7
            assert max(abs(a-b) for a, b in zip(matvec(finite, stamped_volts), terminal)) < 1e-7
    assert errors == sorted(errors, reverse=True) and errors[-1] == 0
    # Mutations: use the SAME physical state to expose missing/doubled shunts.
    c, correct, _ = blocks(0j)
    _, current = scalar_solution(0j)
    expected = terminal_currents(ideal, current)
    for mag, ground in ((0, 1), (2, 1), (1, 0), (1, 2)):
        _, faulty, _ = blocks(0j, magnetizing_copies=mag, grounding_copies=ground)
        currents = [v+ci*current for v, ci in zip(matvec(faulty, ideal), c)]
        assert max(abs(a-b) for a, b in zip(currents, expected)) >= 0.19
    # Both common modes are invisible without earth branches. One finite earth
    # branch removes only the secondary mode; a primary boundary reference is still needed.
    c, floating, _ = blocks(0j, grounding_copies=0)
    for mode in ([1, 1, 0, 0], [0, 0, 1, 1]):
        assert sum(a*b for a, b in zip(c, mode)) == 0
        assert matvec(floating, mode) == [0j]*4
    assert matvec(correct, [0, 0, 1, 1])[-1] == GROUND_Y
    assert matvec(correct, [1, 1, 0, 0]) == [0j]*4
    unity, _ = scalar_solution(0j, ratio=1)
    assert unity[3] == 2 and unity[1] == 0  # unity ratio does not bond neutrals
    # Transfer: reverse excitation. Complex power is quadratic; currents reverse.
    reverse, reverse_i = scalar_solution(0.2+0.1j, primary=-230)
    forward, forward_i = scalar_solution(0.2+0.1j)
    assert reverse_i == -forward_i and reverse[2]-reverse[3] == -(forward[2]-forward[3])
    print("Finite-stamp/border/scalar agreement, power, scaling, shunt mutations, reference modes and transfer checks pass.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--leakage", type=finite_complex, default=0.2+0.1j, help="primary-referred leakage in ohms")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
        return
    if args.leakage.real < 0:
        parser.error("this passive example requires nonnegative leakage resistance")
    volts, current = scalar_solution(args.leakage)
    print(f"secondary differential voltage: {volts[2]-volts[3]} V")
    print(f"secondary neutral to earth: {volts[3]} V")
    print(f"primary coil current: {current} A")
    print(f"transformer terminal currents: {terminal_currents(volts, current)} A")
    print("Only exactly zero leakage gives the ideal voltage constraint; finite earth and magnetizing branches remain.")


if __name__ == "__main__":
    main()
