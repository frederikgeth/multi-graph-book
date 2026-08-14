#!/usr/bin/env python3
"""Independent reproduction of the two-point nonlinear grounding probe."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/generated/nonlinear-two-point-grounding-witness.json"
OUTPUT = ROOT / "experiments/generated/nonlinear-two-point-grounding-independent-reproduction.json"


def solve(matrix: list[list[complex]], rhs: list[complex]) -> list[complex]:
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


def matvec(matrix: list[list[complex]], vector: list[complex]) -> list[complex]:
    return [sum(value * vector[column] for column, value in enumerate(row)) for row in matrix]


def invert(matrix: list[list[complex]]) -> list[list[complex]]:
    columns = [solve(matrix, [1.0 + 0j if row == column else 0j for row in range(len(matrix))]) for column in range(len(matrix))]
    return [[columns[column][row] for column in range(len(matrix))] for row in range(len(matrix))]


def z5() -> list[list[complex]]:
    diagonal = [0.10 + 0.20j, 0.11 + 0.21j, 0.12 + 0.22j, 0.20 + 0.30j, 0.40 + 0.50j]
    mutual = 0.006 + 0.012j
    return [[diagonal[row] if row == column else mutual for column in range(5)] for row in range(5)]


def bond(v: list[complex], y0: complex, alpha: float) -> complex:
    delta = v[3] - v[4]
    return y0 * (1 + alpha * abs(delta) ** 2) * delta


def residual(v: list[complex], vi: list[complex], vj: list[complex], y: list[list[complex]], y0s: list[complex], alphas: list[float]) -> list[complex]:
    m1, m2 = v[:5], v[5:]
    first = [a + b for a, b in zip(matvec(y, [m1[i] - vi[i] for i in range(5)]), matvec(y, [m1[i] - m2[i] for i in range(5)]))]
    second = [a + b for a, b in zip(matvec(y, [m2[i] - m1[i] for i in range(5)]), matvec(y, [m2[i] - vj[i] for i in range(5)]))]
    b1 = bond(m1, y0s[0], alphas[0])
    b2 = bond(m2, y0s[1], alphas[1])
    first[3] += b1; first[4] -= b1
    second[3] += b2; second[4] -= b2
    return first + second


def coords(v: list[complex]) -> list[float]:
    return [x.real for x in v] + [x.imag for x in v]


def uncoords(x: list[float]) -> list[complex]:
    return [x[i] + 1j * x[i + 10] for i in range(10)]


def magnitude(v: list[complex]) -> float:
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
            perturbed = x[:]
            perturbed[column] += 1e-7
            rp = coords(residual(uncoords(perturbed), vi, vj, y, y0s, alphas))
            for row in range(20):
                jacobian[row].append((rp[row] - rr[row]) / 1e-7)
        step = solve(jacobian, [-x for x in rr])
        for damping in (1.0, 0.5, 0.25, 0.125, 0.0625):
            candidate = uncoords([x[i] + damping * step[i] for i in range(20)])
            if magnitude(residual(candidate, vi, vj, y, y0s, alphas)) < rnorm:
                v = candidate
                break
        else:
            raise ValueError("Newton step was not accepted")
    raise ValueError("Newton solve did not converge")


def pairs(values):
    return [{"real": x.real, "imag": x.imag} for x in values]


def main() -> None:
    reference = json.loads(SOURCE.read_text())
    z = z5()
    y = invert([[(1 / 3) * value for value in row] for row in z])
    y0s = [1 / (0.20 + 0.10j), 1 / (0.35 + 0.12j)]
    alphas = [4.0, 6.0]
    vi = [1.00 + 0.02j, 0.99 - 0.01j, 0.98 + 0.01j, 0.02 + 0j, 0j]
    vj = [0.97 - 0.02j, 0.96 + 0.01j, 0.95 - 0.01j, 0.01 + 0j, 0.04 + 0j]
    vj_shifted = vj[:]
    vj_shifted[3] = 0.10 + 0j; vj_shifted[4] = -0.02 + 0j
    base, base_residual = newton(vi, vj, y, y0s, alphas)
    shifted, shifted_residual = newton(vi, vj_shifted, y, y0s, alphas)
    mids = [base[:5], base[5:]]
    shifted_mids = [shifted[:5], shifted[5:]]
    frozen_y0s = [y0s[k] * (1 + alphas[k] * abs(mids[k][3] - mids[k][4]) ** 2) for k in range(2)]
    matrix = [[0j for _ in range(10)] for _ in range(10)]
    for offset, admittance in ((0, frozen_y0s[0]), (5, frozen_y0s[1])):
        for row in range(5):
            for column in range(5):
                matrix[offset + row][offset + column] = 2 * y[row][column]
        matrix[offset + 3][offset + 3] += admittance; matrix[offset + 3][offset + 4] -= admittance
        matrix[offset + 4][offset + 3] -= admittance; matrix[offset + 4][offset + 4] += admittance
    for row in range(5):
        for column in range(5):
            matrix[row][5 + column] = -y[row][column]
            matrix[5 + row][column] = -y[row][column]
    frozen = solve(matrix, matvec(y, vi) + matvec(y, vj_shifted))
    shifted_currents = [matvec(y, [vi[i] - shifted_mids[0][i] for i in range(5)]), matvec(y, [shifted_mids[0][i] - shifted_mids[1][i] for i in range(5)]), matvec(y, [shifted_mids[1][i] - vj_shifted[i] for i in range(5)])]
    frozen_currents = [matvec(y, [vi[i] - frozen[:5][i] for i in range(5)]), matvec(y, [frozen[:5][i] - frozen[5:][i] for i in range(5)]), matvec(y, [frozen[5:][i] - vj_shifted[i] for i in range(5)])]
    frozen_residual = magnitude(residual(frozen, vi, vj_shifted, y, y0s, alphas))
    checks = {
        "base_values_match_julia": all(abs(a - complex(b["real"], b["imag"])) <= 1e-8 for a, b in zip(base, reference["base"]["midpoint_voltages"])),
        "shifted_values_match_julia": all(abs(a - complex(b["real"], b["imag"])) <= 1e-8 for a, b in zip(shifted, reference["shifted"]["midpoint_voltages"])),
        "frozen_values_match_julia": all(abs(a - complex(b["real"], b["imag"])) <= 1e-8 for a, b in zip(frozen, reference["frozen_shifted"]["midpoint_voltages"])),
        "base_solve_is_exact": base_residual <= 1e-11,
        "shifted_solve_is_exact": shifted_residual <= 1e-11,
        "frozen_chain_map_is_not_exact": frozen_residual > 1e-5,
        "neutral_limit_is_evaluated": max(abs(current[3]) for current in shifted_currents) > reference["declared_neutral_limit"],
        "no_numpy_or_julia_import": True,
    }
    result = {"witness_id": "TR-KRON-NEUTRAL-006-REPRO", "claim_id": "TR-KRON-NEUTRAL-006", "method": "independent pure-Python finite-difference Newton solve", "source_witness": "experiments/generated/nonlinear-two-point-grounding-witness.json", "base_midpoint_voltages": pairs(base), "shifted_midpoint_voltages": pairs(shifted), "frozen_shifted_midpoint_voltages": pairs(frozen), "residuals": {"base": base_residual, "shifted": shifted_residual, "frozen_nonlinear": frozen_residual}, "checks": checks, "all_checks_pass": all(checks.values()), "interpretation": "Independent reproduction of the local two-point state-dependent grounding probe; not a global nonlinear grounding or protection theorem."}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    if not result["all_checks_pass"]:
        raise SystemExit("two-point nonlinear grounding reproduction failed")


if __name__ == "__main__":
    main()
