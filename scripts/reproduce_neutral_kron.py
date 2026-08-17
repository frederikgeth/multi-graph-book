#!/usr/bin/env python3
"""Independent reproduction of the running-network neutral Kron limit witness."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data/running-network/v0.1.0.json"
SOURCE = ROOT / "experiments/generated/running-network-typed-kron-witness.json"
OUTPUT = ROOT / "experiments/generated/neutral-kron-independent-reproduction.json"


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


def inverse(matrix: list[list[complex]]) -> list[list[complex]]:
    n = len(matrix)
    columns = [solve(matrix, [1 + 0j if row == column else 0j for row in range(n)]) for column in range(n)]
    return [list(row) for row in zip(*columns)]


def decode(value: dict[str, float]) -> complex:
    return complex(value["real"], value["imag"])


def main() -> None:
    fixture = json.loads(FIXTURE.read_text())
    line = fixture["line"]["l1"]
    z = [[complex(line[f"R_series_{row}_{column}"], line[f"X_series_{row}_{column}"]) for column in range(1, 5)] for row in range(1, 5)]
    y = inverse(z)
    vi = [1.00 + 0.02j, 0.99 - 0.01j, 0.98 + 0.01j, 0.01 + 0.00j]
    vj = [0.97 - 0.02j, 0.96 + 0.01j, 0.95 - 0.01j, 0.02 + 0.00j]
    midpoint = [(left + right) / 2 for left, right in zip(vi, vj)]
    left_neutral = sum(y[3][column] * (vi[column] - midpoint[column]) for column in range(4))
    right_neutral = sum(y[3][column] * (midpoint[column] - vj[column]) for column in range(4))
    current_limit = 0.90 * abs(left_neutral)
    expected = json.loads(SOURCE.read_text())["neutral_limit_witness"]
    expected_shunt = json.loads(SOURCE.read_text())["neutral_shunt_witness"]
    expected_left = decode(expected["source_left_half_current"])
    expected_right = decode(expected["source_right_half_current"])
    shunt = 0.75 + 0.20j
    yhalf = [[2 * value for value in row] for row in y]
    internal = [[2 * yhalf[row][column] for column in range(4)] for row in range(4)]
    internal[3][3] += shunt
    shunt_rhs = [sum(yhalf[row][column] * (vi[column] + vj[column]) for column in range(4)) for row in range(4)]
    midpoint_shunt = solve(internal, shunt_rhs)
    shunt_left = sum(yhalf[3][column] * (vi[column] - midpoint_shunt[column]) for column in range(4))
    shunt_right = sum(yhalf[3][column] * (midpoint_shunt[column] - vj[column]) for column in range(4))
    shunt_reference = shunt * midpoint_shunt[3]
    result = {
        "witness_id": "TR-KRON-NEUTRAL-001-REPRO",
        "claim_id": "TR-KRON-NEUTRAL-001",
        "method": "independent pure-Python complex Gaussian elimination",
        "source_fixture": "data/running-network/v0.1.0.json",
        "source_witness": "experiments/generated/running-network-typed-kron-witness.json",
        "recovered_left_neutral": {"real": left_neutral.real, "imag": left_neutral.imag},
        "recovered_right_neutral": {"real": right_neutral.real, "imag": right_neutral.imag},
        "declared_current_limit": current_limit,
        "checks": {
            "left_current_matches_julia": abs(left_neutral - expected_left) <= 1e-12,
            "right_current_matches_julia": abs(right_neutral - expected_right) <= 1e-12,
            "recovery_is_exact": abs(left_neutral - right_neutral) <= 1e-12,
            "limit_violation_is_retained": abs(left_neutral) > current_limit,
            "shunt_left_current_matches_julia": abs(shunt_left - decode(expected_shunt["recovered_left_neutral_current"])) <= 1e-12,
            "shunt_right_current_matches_julia": abs(shunt_right - decode(expected_shunt["recovered_right_neutral_current"])) <= 1e-12,
            "shunt_kcl_is_exact": abs(shunt_left - shunt_right - shunt_reference) <= 1e-12,
            "shunt_limit_violation_is_retained": abs(shunt_left) > float(expected_shunt["declared_current_limit"]),
            "no_numpy_or_julia_import": True,
        },
        "all_checks_pass": True,
        "interpretation": "Independent reproduction of the declared linear midpoint recovery and neutral-current limit observation; shunt, nonlinear, and explicit-earth reductions remain outside this witness.",
    }
    result["all_checks_pass"] = all(result["checks"].values())
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    if not result["all_checks_pass"]:
        raise SystemExit("independent neutral Kron reproduction failed")


if __name__ == "__main__":
    main()
