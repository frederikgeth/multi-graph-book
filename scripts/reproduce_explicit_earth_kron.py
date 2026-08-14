#!/usr/bin/env python3
"""Independent standard-library reproduction of the explicit-earth Kron probe."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/generated/explicit-earth-kron-witness.json"
OUTPUT = ROOT / "experiments/generated/explicit-earth-kron-independent-reproduction.json"


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


def z5() -> list[list[complex]]:
    diagonal = [0.10 + 0.20j, 0.11 + 0.21j, 0.12 + 0.22j, 0.20 + 0.30j, 0.40 + 0.50j]
    mutual = 0.006 + 0.012j
    return [[diagonal[row] if row == column else mutual for column in range(5)] for row in range(5)]


def matvec(matrix: list[list[complex]], vector: list[complex]) -> list[complex]:
    return [sum(value * vector[column] for column, value in enumerate(row)) for row in matrix]


def block_series(z: list[list[complex]]) -> list[list[complex]]:
    y = [[0j for _ in range(5)] for _ in range(5)]
    for column in range(5):
        unit = [0j] * 5
        unit[column] = 1.0 + 0j
        solved = solve([[0.5 * value for value in row] for row in z], unit)
        for row in range(5):
            y[row][column] = solved[row]
    relation = [[0j for _ in range(15)] for _ in range(15)]
    for p, q, sign in ((0, 0, 1), (0, 1, -1), (1, 0, -1), (1, 1, 2),
                       (1, 2, -1), (2, 1, -1), (2, 2, 1)):
        for row in range(5):
            for column in range(5):
                relation[p * 5 + row][q * 5 + column] = sign * y[row][column]
    return relation


def block_three_segment_series(z: list[list[complex]]) -> list[list[complex]]:
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


def main() -> None:
    reference = json.loads(SOURCE.read_text())
    z = z5()
    relation = block_series(z)
    bond = 1 / (0.20 + 0.10j)
    internal_offset = 5
    relation[internal_offset + 3][internal_offset + 3] += bond
    relation[internal_offset + 3][internal_offset + 4] -= bond
    relation[internal_offset + 4][internal_offset + 3] -= bond
    relation[internal_offset + 4][internal_offset + 4] += bond
    vi = [1.00 + 0.02j, 0.99 - 0.01j, 0.98 + 0.01j, 0.02 + 0j, 0j]
    vj = [0.97 - 0.02j, 0.96 + 0.01j, 0.95 - 0.01j, 0.01 + 0j, 0.04 + 0j]
    vb = vi + vj
    retained = list(range(5)) + list(range(10, 15))
    internal = list(range(5, 10))
    yii = [[relation[row][column] for column in internal] for row in internal]
    yib = [[relation[row][column] for column in retained] for row in internal]
    rhs = [-value for value in matvec(yib, vb)]
    midpoint = solve(yii, rhs)
    yhalf = [[value for value in row] for row in z]
    yhalf = [[0j for _ in range(5)] for _ in range(5)]
    for column in range(5):
        unit = [0j] * 5
        unit[column] = 1.0 + 0j
        solved = solve([[0.5 * value for value in row] for row in z], unit)
        for row in range(5):
            yhalf[row][column] = solved[row]
    left = matvec(yhalf, [vi[index] - midpoint[index] for index in range(5)])
    right = matvec(yhalf, [midpoint[index] - vj[index] for index in range(5)])
    bond_current = bond * (midpoint[3] - midpoint[4])
    reference_rows = reference["recovered_midpoint_voltage"], reference["recovered_left_current"], reference["recovered_right_current"]

    def pairs(values: list[complex]) -> list[dict[str, float]]:
        return [{"real": value.real, "imag": value.imag} for value in values]

    calculated_rows = [midpoint, left, right]
    matches = []
    for calculated, expected in zip(calculated_rows, reference_rows):
        matches.append(all(abs(value - complex(item["real"], item["imag"])) <= 1e-9 for value, item in zip(calculated, expected)))
    neutral_kcl = abs(left[3] - right[3] - bond_current)
    earth_kcl = abs(left[4] - right[4] + bond_current)
    checks = {
        "all_values_match_julia": all(matches),
        "neutral_kcl_is_exact": neutral_kcl <= 1e-11,
        "earth_kcl_is_exact": earth_kcl <= 1e-11,
        "earth_port_retained": reference.get("terminal_order") == ["a", "b", "c", "n", "e"],
        "no_numpy_or_julia_import": True,
    }
    chain = block_three_segment_series(z)
    first_bond = 1 / (0.20 + 0.10j)
    second_bond = 1 / (0.35 + 0.12j)
    for offset, admittance in ((5, first_bond), (10, second_bond)):
        chain[offset + 3][offset + 3] += admittance
        chain[offset + 3][offset + 4] -= admittance
        chain[offset + 4][offset + 3] -= admittance
        chain[offset + 4][offset + 4] += admittance
    chain_retained = list(range(5)) + list(range(15, 20))
    chain_internal = list(range(5, 15))
    chain_yii = [[chain[row][column] for column in chain_internal] for row in chain_internal]
    chain_yib = [[chain[row][column] for column in chain_retained] for row in chain_internal]
    chain_rhs = [-value for value in matvec(chain_yib, vb)]
    chain_internal_voltage = solve(chain_yii, chain_rhs)
    m1 = chain_internal_voltage[:5]
    m2 = chain_internal_voltage[5:]
    ythird = [[0j for _ in range(5)] for _ in range(5)]
    for column in range(5):
        unit = [0j] * 5
        unit[column] = 1.0 + 0j
        solved = solve([[(1 / 3) * value for value in row] for row in z], unit)
        for row in range(5):
            ythird[row][column] = solved[row]
    current1 = matvec(ythird, [vi[index] - m1[index] for index in range(5)])
    current2 = matvec(ythird, [m1[index] - m2[index] for index in range(5)])
    current3 = matvec(ythird, [m2[index] - vj[index] for index in range(5)])
    bond_current1 = first_bond * (m1[3] - m1[4])
    bond_current2 = second_bond * (m2[3] - m2[4])
    multiple_reference = reference["multiple_grounding_witness"]
    multiple_matches = (
        all(abs(value - complex(item["real"], item["imag"])) <= 1e-9 for value, item in zip(m1, multiple_reference["recovered_midpoint_voltages"][0]))
        and all(abs(value - complex(item["real"], item["imag"])) <= 1e-9 for value, item in zip(m2, multiple_reference["recovered_midpoint_voltages"][1]))
        and all(abs(value - complex(item["real"], item["imag"])) <= 1e-9 for value, item in zip((current1[3], current2[3], current3[3]), [multiple_reference["segment_neutral_currents"][0], multiple_reference["segment_neutral_currents"][1], multiple_reference["segment_neutral_currents"][2]]))
    )
    multiple_checks = {
        "all_values_match_julia": multiple_matches,
        "first_bond_kcl_is_exact": abs(current1[3] - current2[3] - bond_current1) <= 1e-11 and abs(current1[4] - current2[4] + bond_current1) <= 1e-11,
        "second_bond_kcl_is_exact": abs(current2[3] - current3[3] - bond_current2) <= 1e-11 and abs(current2[4] - current3[4] + bond_current2) <= 1e-11,
        "no_numpy_or_julia_import": True,
    }
    checks["multiple_grounding_values_match_julia"] = multiple_checks["all_values_match_julia"]
    checks["multiple_grounding_kcl_is_exact"] = multiple_checks["first_bond_kcl_is_exact"] and multiple_checks["second_bond_kcl_is_exact"]
    result = {
        "witness_id": "TR-KRON-NEUTRAL-002-REPRO",
        "claim_id": "TR-KRON-NEUTRAL-002",
        "method": "independent pure-Python complex Gaussian elimination",
        "source_witness": "experiments/generated/explicit-earth-kron-witness.json",
        "recovered_midpoint_voltage": pairs(midpoint),
        "recovered_left_current": pairs(left),
        "recovered_right_current": pairs(right),
        "recovered_bond_current": {"real": bond_current.real, "imag": bond_current.imag},
        "multiple_grounding": {
            "recovered_midpoint_voltages": [pairs(m1), pairs(m2)],
            "segment_neutral_currents": [
                {"real": current1[3].real, "imag": current1[3].imag},
                {"real": current2[3].real, "imag": current2[3].imag},
                {"real": current3[3].real, "imag": current3[3].imag},
            ],
            "bond_currents": [
                {"real": bond_current1.real, "imag": bond_current1.imag},
                {"real": bond_current2.real, "imag": bond_current2.imag},
            ],
            "checks": multiple_checks,
        },
        "residuals": {"neutral_kcl": neutral_kcl, "earth_kcl": earth_kcl},
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": "Independent reproduction of the synthetic five-conductor linear Kron recovery; not an independent grounding or protection model.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    if not result["all_checks_pass"]:
        raise SystemExit("independent explicit-earth Kron reproduction failed")


if __name__ == "__main__":
    main()
