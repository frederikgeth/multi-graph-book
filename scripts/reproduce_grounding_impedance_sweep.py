#!/usr/bin/env python3
"""Independent reproduction of the explicit-grounding impedance sweep."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/generated/grounding-impedance-sweep-witness.json"
OUTPUT = ROOT / "experiments/generated/grounding-impedance-sweep-independent-reproduction.json"


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


def chain(z: list[list[complex]]) -> list[list[complex]]:
    y = [[0j for _ in range(5)] for _ in range(5)]
    for column in range(5):
        unit = [0j] * 5
        unit[column] = 1.0 + 0j
        solved = solve([[(1 / 3) * value for value in row] for row in z], unit)
        for row in range(5):
            y[row][column] = solved[row]
    relation = [[0j for _ in range(20)] for _ in range(20)]
    for p, q, sign in ((0, 0, 1), (0, 1, -1), (1, 0, -1), (1, 1, 2),
                       (1, 2, -1), (2, 1, -1), (2, 2, 2), (2, 3, -1),
                       (3, 2, -1), (3, 3, 1)):
        for row in range(5):
            for column in range(5):
                relation[p * 5 + row][q * 5 + column] = sign * y[row][column]
    return relation


def row(z: list[list[complex]], vi: list[complex], vj: list[complex], z1: complex, z2: complex) -> dict:
    relation = chain(z)
    for offset, admittance in ((5, 1 / z1), (10, 1 / z2)):
        relation[offset + 3][offset + 3] += admittance
        relation[offset + 3][offset + 4] -= admittance
        relation[offset + 4][offset + 3] -= admittance
        relation[offset + 4][offset + 4] += admittance
    retained = list(range(5)) + list(range(15, 20))
    internal = list(range(5, 15))
    yii = [[relation[r][c] for c in internal] for r in internal]
    yib = [[relation[r][c] for c in retained] for r in internal]
    midpoint = solve(yii, [-value for value in matvec(yib, vi + vj)])
    ythird = [[0j for _ in range(5)] for _ in range(5)]
    for column in range(5):
        unit = [0j] * 5
        unit[column] = 1.0 + 0j
        solved = solve([[(1 / 3) * value for value in r] for r in z], unit)
        for r in range(5):
            ythird[r][column] = solved[r]
    m1, m2 = midpoint[:5], midpoint[5:]
    currents = [
        matvec(ythird, [vi[i] - m1[i] for i in range(5)]),
        matvec(ythird, [m1[i] - m2[i] for i in range(5)]),
        matvec(ythird, [m2[i] - vj[i] for i in range(5)]),
    ]
    bonds = [(1 / z1) * (m1[3] - m1[4]), (1 / z2) * (m2[3] - m2[4])]
    residuals = [
        abs(currents[0][3] - currents[1][3] - bonds[0]),
        abs(currents[0][4] - currents[1][4] + bonds[0]),
        abs(currents[1][3] - currents[2][3] - bonds[1]),
        abs(currents[1][4] - currents[2][4] + bonds[1]),
    ]
    neutral = [current[3] for current in currents]
    return {
        "maximum_neutral_current": max(abs(value) for value in neutral),
        "bond_currents": bonds,
        "kcl_residuals": residuals,
    }


def main() -> None:
    reference = json.loads(SOURCE.read_text())
    z = z5()
    vi = [1.00 + 0.02j, 0.99 - 0.01j, 0.98 + 0.01j, 0.02 + 0j, 0j]
    vj = [0.97 - 0.02j, 0.96 + 0.01j, 0.95 - 0.01j, 0.01 + 0j, 0.04 + 0j]
    cases = {
        "nominal": (0.20 + 0.10j, 0.35 + 0.12j),
        "strong_first": (0.08 + 0.04j, 0.35 + 0.12j),
        "weak_first": (0.60 + 0.20j, 0.35 + 0.12j),
        "asymmetric": (0.08 + 0.04j, 0.90 + 0.30j),
    }
    rows = []
    matches = []
    for expected in reference["rows"]:
        z1, z2 = cases[expected["case"]]
        calculated = row(z, vi, vj, z1, z2)
        values_match = abs(calculated["maximum_neutral_current"] - expected["maximum_neutral_current"]) <= 1e-9
        values_match = values_match and all(abs(value - complex(item["real"], item["imag"])) <= 1e-9 for value, item in zip(calculated["bond_currents"], expected["bond_currents"]))
        limit_satisfied = calculated["maximum_neutral_current"] <= expected["declared_neutral_limit"]
        row_out = {"case": expected["case"], "maximum_neutral_current": calculated["maximum_neutral_current"], "limit_satisfied": limit_satisfied, "kcl_residuals": calculated["kcl_residuals"], "matches_julia": values_match and limit_satisfied == expected["limit_satisfied"]}
        rows.append(row_out)
        matches.append(row_out["matches_julia"])
    checks = {
        "all_rows_match_julia": all(matches),
        "feasibility_classification_changes": any(row["limit_satisfied"] for row in rows) and any(not row["limit_satisfied"] for row in rows),
        "all_kcl_residuals_are_small": all(max(row["kcl_residuals"]) <= 1e-11 for row in rows),
        "independent_solver_used": True,
        "no_numpy_or_julia_import": True,
    }
    result = {"witness_id": "TR-KRON-NEUTRAL-004-REPRO", "claim_id": "TR-KRON-NEUTRAL-004", "method": "independent pure-Python complex Gaussian elimination", "source_witness": "experiments/generated/grounding-impedance-sweep-witness.json", "rows": rows, "checks": checks, "all_checks_pass": all(checks.values()), "interpretation": "Independent reproduction of the finite grounding-impedance sensitivity sweep; not an uncertainty quantification or standards-aligned grounding study."}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    if not result["all_checks_pass"]:
        raise SystemExit("grounding impedance sweep reproduction failed")


if __name__ == "__main__":
    main()
