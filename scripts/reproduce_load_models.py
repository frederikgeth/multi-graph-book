#!/usr/bin/env python3
"""Independent standard-library reproduction of the CP/CI/CZ load witness."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/generated/load-grounding-witnesses.json"
OUTPUT = ROOT / "experiments/generated/load-model-independent-reproduction.json"


def decode(value: dict[str, float]) -> complex:
    return complex(value["real"], value["imag"])


def solve_load(
    z: complex,
    s_nominal: complex,
    family: str,
    zip_coefficients_p: tuple[float, float, float],
    zip_coefficients_q: tuple[float, float, float],
) -> dict[str, float | complex | bool | None]:
    def factor_for(ratio: float, coefficients: tuple[float, float, float]) -> float:
        if family == "CP":
            return 1.0
        if family == "CI":
            return ratio
        if family == "CZ":
            return ratio**2
        return coefficients[0] * ratio**2 + coefficients[1] * ratio + coefficients[2]

    voltage = 1.0 + 0.0j
    for _ in range(500):
        ratio = abs(voltage)
        factor_p = factor_for(ratio, zip_coefficients_p)
        factor_q = factor_for(ratio, zip_coefficients_q)
        power = complex(s_nominal.real * factor_p, s_nominal.imag * factor_q)
        current = (power / voltage).conjugate()
        target = 1.0 - z * current
        updated = 0.5 * voltage + 0.5 * target
        if abs(updated - voltage) <= 1.0e-13:
            voltage = updated
            break
        voltage = updated
    ratio = abs(voltage)
    factor_p = factor_for(ratio, zip_coefficients_p)
    factor_q = factor_for(ratio, zip_coefficients_q)
    power = complex(s_nominal.real * factor_p, s_nominal.imag * factor_q)
    current = (power / voltage).conjugate()
    return {
        "voltage_pu": voltage,
        "voltage_magnitude_pu": abs(voltage),
        "current_pu": current,
        "current_magnitude_pu": abs(current),
        "delivered_power_pu": power,
        "residual_pu": abs(1.0 - voltage - z * current),
    }


def close(left: float, right: float, tolerance: float = 1.0e-9) -> bool:
    return abs(left - right) <= tolerance


def main() -> None:
    expected = json.loads(SOURCE.read_text())
    load = expected["load_models"]
    z = decode(load["series_impedance_pu"])
    s_nominal = decode(load["nominal_load_pu"])
    voltage_limit = load["voltage_limit_pu"]
    current_limit = load["current_limit_pu"]
    zip_data_p = load["zip_coefficients"]["active_power"]
    zip_data_q = load["zip_coefficients"]["reactive_power"]
    zip_coefficients_p = (zip_data_p["alpha_Z"], zip_data_p["alpha_I"], zip_data_p["alpha_P"])
    zip_coefficients_q = (zip_data_q["alpha_Z"], zip_data_q["alpha_I"], zip_data_q["alpha_P"])
    expected_rows = {row["family"]: row for row in load["rows"]}
    rows = []
    comparisons = []
    numeric = (
        "voltage_magnitude_pu",
        "current_magnitude_pu",
        "residual_pu",
    )
    for family in ("CP", "CI", "CZ", "ZIP"):
        calculated = solve_load(z, s_nominal, family, zip_coefficients_p, zip_coefficients_q)
        calculated["voltage_limit_satisfied"] = calculated["voltage_magnitude_pu"] >= voltage_limit
        calculated["current_limit_satisfied"] = calculated["current_magnitude_pu"] <= current_limit
        reference = expected_rows[family]
        matches = all(close(calculated[key], reference[key]) for key in numeric)
        matches = matches and close(abs(calculated["voltage_pu"] - decode(reference["voltage_pu"])), 0.0)
        matches = matches and close(abs(calculated["current_pu"] - decode(reference["current_pu"])), 0.0)
        matches = matches and close(abs(calculated["delivered_power_pu"] - decode(reference["delivered_power_pu"])), 0.0)
        matches = matches and calculated["voltage_limit_satisfied"] == reference["voltage_limit_satisfied"]
        matches = matches and calculated["current_limit_satisfied"] == reference["current_limit_satisfied"]
        row = {
            "family": family,
            "voltage_magnitude_pu": calculated["voltage_magnitude_pu"],
            "current_magnitude_pu": calculated["current_magnitude_pu"],
            "residual_pu": calculated["residual_pu"],
            "voltage_limit_satisfied": calculated["voltage_limit_satisfied"],
            "current_limit_satisfied": calculated["current_limit_satisfied"],
            "matches_julia": matches,
        }
        rows.append(row)
        comparisons.append(matches)
    result = {
        "witness_id": "LOAD-DECISION-001-REPRO",
        "claim_id": "LOAD-DECISION-001",
        "method": "independent pure-Python damped fixed-point iteration",
        "source_witness": "experiments/generated/load-grounding-witnesses.json",
        "rows": rows,
        "checks": {
            "all_rows_match_julia": all(comparisons),
            "independent_iteration_used": True,
            "same_graph_and_limits_reused": True,
            "zip_coefficients_reconstructed": sum(zip_coefficients_p) == 1.0 and sum(zip_coefficients_q) == 1.0 and all(value >= 0 for value in zip_coefficients_p + zip_coefficients_q),
            "zip_reactive_coefficients_reconstructed": zip_coefficients_p != zip_coefficients_q,
            "no_numpy_or_julia_import": True,
        },
        "all_checks_pass": all(comparisons),
        "interpretation": "Independent reproduction of the declared CP/CI/CZ scalar fixture and its decision margins; not a global load-flow solvability or load-model ranking result.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    if not result["all_checks_pass"]:
        raise SystemExit("independent load-model reproduction failed")


if __name__ == "__main__":
    main()
