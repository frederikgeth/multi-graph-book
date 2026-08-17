#!/usr/bin/env python3
"""Independent reproduction of the finite two-point grounding continuation."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/generated/nonlinear-two-point-grounding-continuation.json"
OUTPUT = ROOT / "experiments/generated/nonlinear-two-point-grounding-continuation-independent-reproduction.json"


def solve(matrix, rhs):
    a = [row[:] + [value] for row, value in zip(matrix, rhs)]
    n = len(a)
    for column in range(n):
        pivot = max(range(column, n), key=lambda row: abs(a[row][column]))
        if abs(a[pivot][column]) <= 1e-14:
            raise ValueError("singular reproduction matrix")
        a[column], a[pivot] = a[pivot], a[column]
        scale = a[column][column]
        a[column] = [value / scale for value in a[column]]
        for row in range(n):
            if row == column:
                continue
            factor = a[row][column]
            a[row] = [left - factor * right for left, right in zip(a[row], a[column])]
    return [a[row][-1] for row in range(n)]


def matvec(matrix, vector):
    return [sum(value * vector[column] for column, value in enumerate(row)) for row in matrix]


def invert(matrix):
    columns = [solve(matrix, [1.0 + 0j if row == column else 0j for row in range(len(matrix))]) for column in range(len(matrix))]
    return [[columns[column][row] for column in range(len(matrix))] for row in range(len(matrix))]


def z5():
    diagonal = [0.10 + 0.20j, 0.11 + 0.21j, 0.12 + 0.22j, 0.20 + 0.30j, 0.40 + 0.50j]
    mutual = 0.006 + 0.012j
    return [[diagonal[row] if row == column else mutual for column in range(5)] for row in range(5)]


def bond(v, y0, alpha):
    delta = v[3] - v[4]
    return y0 * (1 + alpha * abs(delta) ** 2) * delta


def residual(v, vi, vj, y, y0s, alphas):
    m1, m2 = v[:5], v[5:]
    first = [a + b for a, b in zip(matvec(y, [m1[i] - vi[i] for i in range(5)]), matvec(y, [m1[i] - m2[i] for i in range(5)]))]
    second = [a + b for a, b in zip(matvec(y, [m2[i] - m1[i] for i in range(5)]), matvec(y, [m2[i] - vj[i] for i in range(5)]))]
    b1, b2 = bond(m1, y0s[0], alphas[0]), bond(m2, y0s[1], alphas[1])
    first[3] += b1; first[4] -= b1; second[3] += b2; second[4] -= b2
    return first + second


def coords(v):
    return [x.real for x in v] + [x.imag for x in v]


def uncoords(x):
    return [x[i] + 1j * x[i + 10] for i in range(10)]


def magnitude(v):
    return sum(abs(x) ** 2 for x in v) ** 0.5


def newton(vi, vj, y, y0s, alphas):
    v = [(vi[i] + vj[i]) / 2 for i in range(5)] * 2
    for _ in range(35):
        r = residual(v, vi, vj, y, y0s, alphas)
        rnorm = magnitude(r)
        if rnorm <= 1e-12:
            return v, rnorm
        x, rr = coords(v), coords(r)
        jacobian = [[] for _ in range(20)]
        for column in range(20):
            perturbed = x[:]; perturbed[column] += 1e-7
            rp = coords(residual(uncoords(perturbed), vi, vj, y, y0s, alphas))
            for row in range(20):
                jacobian[row].append((rp[row] - rr[row]) / 1e-7)
        step = solve(jacobian, [-value for value in rr])
        for damping in (1.0, 0.5, 0.25, 0.125, 0.0625):
            candidate = uncoords([x[i] + damping * step[i] for i in range(20)])
            if magnitude(residual(candidate, vi, vj, y, y0s, alphas)) < rnorm:
                v = candidate
                break
        else:
            raise ValueError("Newton step was not accepted")
    raise ValueError("Newton solve did not converge")


def main():
    reference = json.loads(SOURCE.read_text())
    z = z5()
    y = invert([[(1 / 3) * value for value in row] for row in z])
    y0s, alphas = [1 / (0.20 + 0.10j), 1 / (0.35 + 0.12j)], [4.0, 6.0]
    vi = [1.00 + 0.02j, 0.99 - 0.01j, 0.98 + 0.01j, 0.02 + 0j, 0j]
    vj_base = [0.97 - 0.02j, 0.96 + 0.01j, 0.95 - 0.01j, 0.01 + 0j, 0.04 + 0j]
    delta = [0j, 0j, 0j, 0.09 + 0j, -0.06 + 0j]
    base, _ = newton(vi, vj_base, y, y0s, alphas)
    frozen_y0s = [y0s[k] * (1 + alphas[k] * abs(base[k * 5 + 3] - base[k * 5 + 4]) ** 2) for k in range(2)]
    rows, matches = [], []
    for expected in reference["rows"]:
        lam = expected["lambda"]
        vj = [vj_base[i] + lam * delta[i] for i in range(5)]
        solved, residual_norm = newton(vi, vj, y, y0s, alphas)
        m1, m2 = solved[:5], solved[5:]
        currents = [matvec(y, [vi[i] - m1[i] for i in range(5)]), matvec(y, [m1[i] - m2[i] for i in range(5)]), matvec(y, [m2[i] - vj[i] for i in range(5)])]
        frozen_matrix = [[0j for _ in range(10)] for _ in range(10)]
        for offset, admittance in ((0, frozen_y0s[0]), (5, frozen_y0s[1])):
            for row in range(5):
                for column in range(5):
                    frozen_matrix[offset + row][offset + column] = 2 * y[row][column]
            frozen_matrix[offset + 3][offset + 3] += admittance; frozen_matrix[offset + 3][offset + 4] -= admittance
            frozen_matrix[offset + 4][offset + 3] -= admittance; frozen_matrix[offset + 4][offset + 4] += admittance
        for row in range(5):
            for column in range(5):
                frozen_matrix[row][5 + column] = -y[row][column]; frozen_matrix[5 + row][column] = -y[row][column]
        frozen = solve(frozen_matrix, matvec(y, vi) + matvec(y, vj))
        frozen_residual = magnitude(residual(frozen, vi, vj, y, y0s, alphas))
        maximum_neutral = max(abs(current[3]) for current in currents)
        matches.append(abs(maximum_neutral - expected["maximum_neutral_current"]) <= 1e-8 and abs(frozen_residual - expected["frozen_nominal_residual"]) <= 1e-8)
        rows.append({"lambda": lam, "maximum_neutral_current": maximum_neutral, "frozen_nominal_residual": frozen_residual, "limit_satisfied": maximum_neutral <= expected["declared_neutral_limit"], "nonlinear_residual": residual_norm, "matches_julia": matches[-1]})
    checks = {"all_rows_match_julia": all(matches), "all_continuation_points_converged": all(row["nonlinear_residual"] <= 1e-11 for row in rows), "frozen_nominal_map_fails_off_base": rows[0]["frozen_nominal_residual"] <= 1e-11 and max(row["frozen_nominal_residual"] for row in rows[1:]) > 1e-5, "recomputed_path_has_multiple_states": len({row["limit_satisfied"] for row in rows}) == 2, "independent_solver_used": True, "no_numpy_or_julia_import": True}
    result = {"witness_id": "TR-KRON-NEUTRAL-007-REPRO", "claim_id": "TR-KRON-NEUTRAL-007", "method": "independent pure-Python finite-difference Newton continuation", "source_witness": "experiments/generated/nonlinear-two-point-grounding-continuation.json", "rows": rows, "checks": checks, "all_checks_pass": all(checks.values()), "interpretation": "Independent reproduction of the finite local continuation; not a global continuation or uncertainty theorem."}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    if not result["all_checks_pass"]:
        raise SystemExit("nonlinear grounding continuation reproduction failed")


if __name__ == "__main__":
    main()
