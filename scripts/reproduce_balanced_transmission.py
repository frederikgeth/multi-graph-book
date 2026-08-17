#!/usr/bin/env python3
"""Independent standard-library reproduction of the balanced transmission witness."""

from __future__ import annotations

import cmath
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/generated/balanced-transmission-witness.json"
OUTPUT = ROOT / "experiments/generated/balanced-transmission-independent-reproduction.json"


def solve(matrix: list[list[complex]], rhs: list[complex]) -> list[complex]:
    """Small Gaussian elimination with partial pivoting, independent of Julia."""
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
    return [sum(left * right for left, right in zip(row, vector)) for row in matrix]


def matmul(left: list[list[complex]], right: list[list[complex]]) -> list[list[complex]]:
    columns = list(zip(*right))
    return [[sum(a * b for a, b in zip(row, column)) for column in columns] for row in left]


def inverse(matrix: list[list[complex]]) -> list[list[complex]]:
    n = len(matrix)
    columns = [solve(matrix, [1 + 0j if row == column else 0j for row in range(n)]) for column in range(n)]
    return [list(row) for row in zip(*columns)]


def add_block(matrix: list[list[complex]], row0: int, col0: int, block: list[list[complex]], sign: int = 1) -> None:
    for row, values in enumerate(block):
        for column, value in enumerate(values):
            matrix[row0 + row][col0 + column] += sign * value


def encode(value: complex) -> dict[str, float]:
    return {"re": value.real, "im": value.imag}


def decode(value: dict[str, float]) -> complex:
    return complex(value["re"], value["im"])


def max_norm(left: list[complex], right: list[complex]) -> float:
    return max(abs(a - b) for a, b in zip(left, right))


def main() -> None:
    expected = json.loads(SOURCE.read_text())
    a = cmath.exp(2j * cmath.pi / 3)
    fortescue = [[1 + 0j, 1 + 0j, 1 + 0j], [1 + 0j, a**2, a], [1 + 0j, a, a**2]]
    z = [
        [0.12 + 0.36j, 0.01 + 0.06j, 0.01 + 0.06j],
        [0.01 + 0.06j, 0.12 + 0.36j, 0.01 + 0.06j],
        [0.01 + 0.06j, 0.01 + 0.06j, 0.12 + 0.36j],
    ]
    ysh = [
        [0.002 + 0.010j, 0.0002 + 0.001j, 0.0002 + 0.001j],
        [0.0002 + 0.001j, 0.002 + 0.010j, 0.0002 + 0.001j],
        [0.0002 + 0.001j, 0.0002 + 0.001j, 0.002 + 0.010j],
    ]
    inv_a = inverse(fortescue)
    z012 = matmul(matmul(inv_a, z), fortescue)
    ysh012 = matmul(matmul(inv_a, ysh), fortescue)
    z1 = z012[1][1]
    ysh1 = ysh012[1][1]

    phase_ybus = [[0j for _ in range(9)] for _ in range(9)]
    yseries = inverse(z)
    for from_bus, to_bus in ((0, 1), (1, 2)):
        from0, to0 = 3 * from_bus, 3 * to_bus
        add_block(phase_ybus, from0, from0, [[yseries[r][c] + ysh[r][c] / 2 for c in range(3)] for r in range(3)])
        add_block(phase_ybus, to0, to0, [[yseries[r][c] + ysh[r][c] / 2 for c in range(3)] for r in range(3)])
        add_block(phase_ybus, from0, to0, yseries, -1)
        add_block(phase_ybus, to0, from0, yseries, -1)

    current_1 = matvec(fortescue, [0j, 0.40 - 0.10j, 0j])
    current_2 = matvec(fortescue, [0j, 0.20 - 0.05j, 0j])
    injections = current_1 + current_2
    slack = matvec(fortescue, [0j, 1 + 0j, 0j])
    reduced = [row[3:9] for row in phase_ybus[3:9]]
    coupling = [row[:3] for row in phase_ybus[3:9]]
    rhs = [value - sum(left * right for left, right in zip(row, slack)) for value, row in zip(injections, coupling)]
    phase_reduced = solve(reduced, rhs)
    phase_voltage = slack + phase_reduced

    scalar_ybus = [[0j for _ in range(3)] for _ in range(3)]
    yseries1 = 1 / z1
    for from_bus, to_bus in ((0, 1), (1, 2)):
        scalar_ybus[from_bus][from_bus] += yseries1 + ysh1 / 2
        scalar_ybus[to_bus][to_bus] += yseries1 + ysh1 / 2
        scalar_ybus[from_bus][to_bus] -= yseries1
        scalar_ybus[to_bus][from_bus] -= yseries1
    scalar_rhs = [0.40 - 0.10j - scalar_ybus[1][0], 0.20 - 0.05j - scalar_ybus[2][0]]
    scalar_voltage = [1 + 0j] + solve([row[1:3] for row in scalar_ybus[1:3]], scalar_rhs)
    embedded = slack + matvec(fortescue, [0j, scalar_voltage[1], 0j]) + matvec(fortescue, [0j, scalar_voltage[2], 0j])
    phase_voltage_residual = max_norm(phase_voltage, embedded)
    nodal_residual = max_norm(matvec(reduced, phase_reduced), rhs)
    positive_residual = max(
        max_norm(
            phase_voltage[3 * bus : 3 * bus + 3],
            matvec(fortescue, [0j, matvec(inv_a, phase_voltage[3 * bus : 3 * bus + 3])[1], 0j]),
        )
        for bus in range(3)
    )

    branches = []
    current_residuals = []
    for from_bus, to_bus in ((0, 1), (1, 2)):
        vf = phase_voltage[3 * from_bus : 3 * from_bus + 3]
        vt = phase_voltage[3 * to_bus : 3 * to_bus + 3]
        current_phase = [
            series + sh / 2
            for series, sh in zip(
                matvec(yseries, [x - y for x, y in zip(vf, vt)]),
                matvec(ysh, vf),
            )
        ]
        current_scalar = yseries1 * (scalar_voltage[from_bus] - scalar_voltage[to_bus]) + ysh1 / 2 * scalar_voltage[from_bus]
        current_embedded = matvec(fortescue, [0j, current_scalar, 0j])
        residual = max_norm(current_phase, current_embedded)
        current_residuals.append(residual)
        branches.append({"arc": f"l{from_bus + 1}{to_bus + 1}", "current_residual": residual})

    expected_voltage = [decode(value) for value in expected["phase_voltages"]]
    expected_embedded = [decode(value) for value in expected["embedded_scalar_voltages"]]
    matches = max_norm(phase_voltage, expected_voltage) <= 1e-9 and max_norm(embedded, expected_embedded) <= 1e-9
    matches = matches and abs(phase_voltage_residual - expected["residuals"]["phase_voltage_inf_norm"]) <= 1e-12
    matches = matches and abs(positive_residual - expected["residuals"]["positive_subspace_inf_norm"]) <= 1e-12
    matches = matches and all(value <= 1e-10 for value in current_residuals)
    result = {
        "witness_id": "COLLAPSE-NETWORK-001-REPRO",
        "claim_id": "COLLAPSE-001",
        "method": "independent pure-Python complex Gaussian elimination",
        "source_witness": "experiments/generated/balanced-transmission-witness.json",
        "residuals": {
            "phase_voltage_inf_norm": phase_voltage_residual,
            "phase_nodal_inf_norm": nodal_residual,
            "positive_subspace_inf_norm": positive_residual,
        },
        "branches": branches,
        "matches_julia": matches,
        "checks": {
            "all_values_match_julia": matches,
            "independent_solver_used": True,
            "nominal_pi_shunts_reconstructed": True,
            "no_numpy_or_julia_import": True,
        },
        "all_checks_pass": matches,
        "interpretation": "Independent reproduction of the declared balanced nominal-pi network and its positive-sequence embedding; not a global decision-equivalence or unbalanced-network validation.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    if not result["all_checks_pass"]:
        raise SystemExit("independent balanced transmission reproduction failed")


if __name__ == "__main__":
    main()
