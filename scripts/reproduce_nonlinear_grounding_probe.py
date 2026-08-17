#!/usr/bin/env python3
"""Independent reproduction of the local state-dependent grounding probe."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/generated/nonlinear-grounding-probe-witness.json"
OUTPUT = ROOT / "experiments/generated/nonlinear-grounding-probe-independent-reproduction.json"


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


def z5() -> list[list[complex]]:
    diagonal = [0.10 + 0.20j, 0.11 + 0.21j, 0.12 + 0.22j, 0.20 + 0.30j, 0.40 + 0.50j]
    mutual = 0.006 + 0.012j
    return [[diagonal[row] if row == column else mutual for column in range(5)] for row in range(5)]


def invert(matrix: list[list[complex]]) -> list[list[complex]]:
    columns = []
    for column in range(len(matrix)):
        unit = [1.0 + 0j if row == column else 0j for row in range(len(matrix))]
        columns.append(solve(matrix, unit))
    return [[columns[column][row] for column in range(len(matrix))] for row in range(len(matrix))]


def bond_current(v: list[complex], y0: complex, alpha: float) -> complex:
    delta = v[3] - v[4]
    return y0 * (1 + alpha * abs(delta) ** 2) * delta


def residual(v: list[complex], vi: list[complex], vj: list[complex], yhalf: list[list[complex]], y0: complex, alpha: float) -> list[complex]:
    left = matvec(yhalf, [v[i] - vi[i] for i in range(5)])
    right = matvec(yhalf, [v[i] - vj[i] for i in range(5)])
    out = [left[i] + right[i] for i in range(5)]
    current = bond_current(v, y0, alpha)
    out[3] += current
    out[4] -= current
    return out


def real_coords(v: list[complex]) -> list[float]:
    return [value.real for value in v] + [value.imag for value in v]


def complex_coords(x: list[float]) -> list[complex]:
    return [x[i] + 1j * x[i + 5] for i in range(5)]


def norm(v: list[complex]) -> float:
    return sum(abs(value) ** 2 for value in v) ** 0.5


def nonlinear_solve(vi: list[complex], vj: list[complex], yhalf: list[list[complex]], y0: complex, alpha: float) -> tuple[list[complex], float]:
    v = [(vi[i] + vj[i]) / 2 for i in range(5)]
    for _ in range(30):
        r = residual(v, vi, vj, yhalf, y0, alpha)
        residual_norm = norm(r)
        if residual_norm <= 1e-12:
            return v, residual_norm
        x = real_coords(v)
        rr = real_coords(r)
        jacobian = []
        for row in range(10):
            jacobian.append([])
        for column in range(10):
            perturbed = x[:]
            perturbed[column] += 1e-7
            rp = real_coords(residual(complex_coords(perturbed), vi, vj, yhalf, y0, alpha))
            for row in range(10):
                jacobian[row].append((rp[row] - rr[row]) / 1e-7)
        step = solve(jacobian, [-value for value in rr])
        accepted = False
        for damping in (1.0, 0.5, 0.25, 0.125, 0.0625):
            candidate = complex_coords([x[i] + damping * step[i] for i in range(10)])
            if norm(residual(candidate, vi, vj, yhalf, y0, alpha)) < residual_norm:
                v = candidate
                accepted = True
                break
        if not accepted:
            raise ValueError("nonlinear grounding Newton step was not accepted")
    raise ValueError("nonlinear grounding solve did not converge")


def pairs(values: list[complex]) -> list[dict[str, float]]:
    return [{"real": value.real, "imag": value.imag} for value in values]


def main() -> None:
    reference = json.loads(SOURCE.read_text())
    z = z5()
    yhalf = invert([[(0.5) * value for value in row] for row in z])
    y0 = 1 / (0.20 + 0.10j)
    alpha = 5.0
    vi = [1.00 + 0.02j, 0.99 - 0.01j, 0.98 + 0.01j, 0.02 + 0j, 0j]
    vj_base = [0.97 - 0.02j, 0.96 + 0.01j, 0.95 - 0.01j, 0.01 + 0j, 0.04 + 0j]
    vj_shifted = vj_base[:]
    vj_shifted[3] = 0.10 + 0j
    vj_shifted[4] = -0.02 + 0j
    base, base_residual = nonlinear_solve(vi, vj_base, yhalf, y0, alpha)
    shifted, shifted_residual = nonlinear_solve(vi, vj_shifted, yhalf, y0, alpha)
    y_base = y0 * (1 + alpha * abs(base[3] - base[4]) ** 2)
    frozen_bond = [[0j for _ in range(5)] for _ in range(5)]
    frozen_bond[3][3] += y_base
    frozen_bond[3][4] -= y_base
    frozen_bond[4][3] -= y_base
    frozen_bond[4][4] += y_base
    lhs = [[2 * yhalf[row][column] + frozen_bond[row][column] for column in range(5)] for row in range(5)]
    rhs = matvec(yhalf, [vi[i] + vj_shifted[i] for i in range(5)])
    frozen = solve(lhs, rhs)
    shifted_bond = bond_current(shifted, y0, alpha)
    frozen_bond_value = y_base * (frozen[3] - frozen[4])
    shifted_current = matvec(yhalf, [vi[i] - shifted[i] for i in range(5)])
    frozen_current = matvec(yhalf, [vi[i] - frozen[i] for i in range(5)])
    frozen_residual = norm(residual(frozen, vi, vj_shifted, yhalf, y0, alpha))
    checks = {
        "base_values_match_julia": all(abs(value - complex(item["real"], item["imag"])) <= 1e-8 for value, item in zip(base, reference["base"]["midpoint_voltage"])),
        "shifted_values_match_julia": all(abs(value - complex(item["real"], item["imag"])) <= 1e-8 for value, item in zip(shifted, reference["shifted"]["midpoint_voltage"])),
        "frozen_values_match_julia": all(abs(value - complex(item["real"], item["imag"])) <= 1e-8 for value, item in zip(frozen, reference["frozen_shifted"]["midpoint_voltage"])),
        "base_solve_is_exact": base_residual <= 1e-11,
        "shifted_solve_is_exact": shifted_residual <= 1e-11,
        "frozen_map_is_not_exact": frozen_residual > 1e-5,
        "neutral_limit_is_evaluated": abs(shifted_current[3]) > reference["declared_neutral_limit"],
        "no_numpy_or_julia_import": True,
    }
    result = {"witness_id": "TR-KRON-NEUTRAL-005-REPRO", "claim_id": "TR-KRON-NEUTRAL-005", "method": "independent pure-Python finite-difference Newton solve", "source_witness": "experiments/generated/nonlinear-grounding-probe-witness.json", "base_midpoint_voltage": pairs(base), "shifted_midpoint_voltage": pairs(shifted), "frozen_shifted_midpoint_voltage": pairs(frozen), "bond_currents": [{"real": shifted_bond.real, "imag": shifted_bond.imag}, {"real": frozen_bond_value.real, "imag": frozen_bond_value.imag}], "neutral_currents": [{"real": shifted_current[3].real, "imag": shifted_current[3].imag}, {"real": frozen_current[3].real, "imag": frozen_current[3].imag}], "residuals": {"base": base_residual, "shifted": shifted_residual, "frozen_nonlinear": frozen_residual}, "checks": checks, "all_checks_pass": all(checks.values()), "interpretation": "Independent reproduction of the local state-dependent grounding probe; not a global nonlinear grounding theorem or standards-aligned protection model."}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    if not result["all_checks_pass"]:
        raise SystemExit("nonlinear grounding reproduction failed")


if __name__ == "__main__":
    main()
