#!/usr/bin/env python3
"""Independent standard-library reproduction of the explicit-earth witness."""

from __future__ import annotations

import cmath
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/generated/load-grounding-witnesses.json"
OUTPUT = ROOT / "experiments/generated/explicit-earth-independent-reproduction.json"


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


def row(z_earth: complex, y_phase_fault: complex, y_neutral_fault: complex) -> dict:
    z_phase = 0.05 + 0.10j
    z_neutral = 0.08 + 0.16j
    y_load = 1 / (1.0 + 0.30j)
    y_bond = 1 / (0.30 + 0.20j)
    y_phase = 1 / z_phase
    y_neutral = 1 / z_neutral
    y_earth = 1 / z_earth
    matrix = [
        [y_phase + y_load + y_phase_fault, -y_load, -y_phase_fault],
        [-y_load, y_neutral + y_load + y_bond + y_neutral_fault, -y_bond - y_neutral_fault],
        [-y_phase_fault, -y_bond - y_neutral_fault, y_earth + y_bond + y_phase_fault + y_neutral_fault],
    ]
    vp, vn, ve = solve(matrix, [y_phase, 0j, 0j])
    phase_fault = y_phase_fault * (vp - ve)
    neutral_fault = y_neutral_fault * (vn - ve)
    fault = phase_fault + neutral_fault
    earth_current = y_earth * ve
    secondary = abs(fault) / 10.0
    pickup = 0.20
    return {
        "earth_voltage_magnitude_pu": abs(ve),
        "earth_conductor_current_magnitude_pu": abs(earth_current),
        "fault_current_magnitude_pu": abs(fault),
        "ct_measured_current_magnitude_pu": secondary,
        "protection_trip_observed": secondary >= pickup,
        "relay_trip_time_s": 0.10 / (secondary / pickup - 1.0) if secondary > pickup else None,
        "touch_voltage_pu": abs(ve),
    }


def main() -> None:
    expected = json.loads(SOURCE.read_text())
    cases = [
        ("earth_in_service", "none", 0.12 + 0.24j, 0j, 0j),
        ("earth_conductor_maintenance_outage", "none", 1.0e6 + 0j, 0j, 0j),
        ("phase_to_earth_fault", "phase_earth", 0.12 + 0.24j, 1 / (0.02 + 0.04j), 0j),
        ("neutral_to_earth_fault", "neutral_earth", 0.12 + 0.24j, 0j, 1 / (0.03 + 0.06j)),
    ]
    expected_rows = {item["state"]: item for item in expected["explicit_earth"]["rows"]}
    rows = []
    comparisons = []
    numeric = (
        "earth_voltage_magnitude_pu",
        "earth_conductor_current_magnitude_pu",
        "fault_current_magnitude_pu",
        "ct_measured_current_magnitude_pu",
        "touch_voltage_pu",
    )
    for state, fault_class, z_earth, y_pf, y_nf in cases:
        calculated = row(z_earth, y_pf, y_nf)
        reference = expected_rows[state]
        matches = all(abs(calculated[key] - reference[key]) <= 1e-9 for key in numeric)
        matches = matches and calculated["protection_trip_observed"] == reference["protection_trip_observed"]
        reference_time = reference["relay_trip_time_s"]
        if reference_time is None:
            matches = matches and calculated["relay_trip_time_s"] is None
        else:
            matches = matches and abs(calculated["relay_trip_time_s"] - reference_time) <= 1e-9
        row_out = {"state": state, "fault_class": fault_class, **calculated, "matches_julia": matches}
        rows.append(row_out)
        comparisons.append(matches)
    result = {
        "witness_id": "GROUND-SCOPE-004-REPRO",
        "claim_id": "GROUND-SCOPE-004",
        "method": "independent pure-Python complex Gaussian elimination",
        "source_witness": "experiments/generated/load-grounding-witnesses.json",
        "rows": rows,
        "checks": {
            "all_rows_match_julia": all(comparisons),
            "independent_solver_used": True,
            "no_numpy_or_julia_import": True,
        },
        "all_checks_pass": all(comparisons),
        "interpretation": "Independent reproduction of the declared linear fixture, CT map, and illustrative relay calculation; not an independent physical protection model.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    if not result["all_checks_pass"]:
        raise SystemExit("independent explicit-earth reproduction failed")


if __name__ == "__main__":
    main()
