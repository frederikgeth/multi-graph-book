#!/usr/bin/env python3
"""Independent reproduction of the scalar load continuation probe."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/generated/load-grounding-witnesses.json"
OUTPUT = ROOT / "experiments/generated/load-continuation-independent-reproduction.json"


def solve(z: complex, s_nominal: complex, family: str, scale: float, initial: complex, p_coeffs: tuple[float, float, float], q_coeffs: tuple[float, float, float]) -> dict:
    voltage = initial
    converged = False
    iterations = 2000

    def factor(ratio: float, coeffs: tuple[float, float, float]) -> float:
        if family == "CP":
            return 1.0
        if family == "CI":
            return ratio
        if family == "CZ":
            return ratio**2
        return coeffs[0] * ratio**2 + coeffs[1] * ratio + coeffs[2]

    for iteration in range(1, 2001):
        ratio = abs(voltage)
        power = complex(
            scale * s_nominal.real * factor(ratio, p_coeffs),
            scale * s_nominal.imag * factor(ratio, q_coeffs),
        )
        current = (power / voltage).conjugate()
        updated = 0.5 * voltage + 0.5 * (1.0 - z * current)
        if abs(updated - voltage) <= 1.0e-13:
            voltage = updated
            converged = True
            iterations = iteration
            break
        voltage = updated
    ratio = abs(voltage)
    power = complex(
        scale * s_nominal.real * factor(ratio, p_coeffs),
        scale * s_nominal.imag * factor(ratio, q_coeffs),
    )
    current = (power / voltage).conjugate()
    return {
        "voltage_magnitude_pu": ratio,
        "residual_pu": abs(1.0 - voltage - z * current),
        "converged": converged,
        "iterations": iterations,
        "voltage": voltage,
    }


def main() -> None:
    source = json.loads(SOURCE.read_text())
    continuation = source["load_continuation"]
    p_data = source["load_models"]["zip_coefficients"]["active_power"]
    q_data = source["load_models"]["zip_coefficients"]["reactive_power"]
    p_coeffs = (p_data["alpha_Z"], p_data["alpha_I"], p_data["alpha_P"])
    q_coeffs = (q_data["alpha_Z"], q_data["alpha_I"], q_data["alpha_P"])
    z = complex(0.08, 0.16)
    s_nominal = complex(0.90, 0.25)
    expected_rows = continuation["rows"]
    rows = []
    comparisons = []
    offset = 0
    for family in ("CP", "CI", "CZ", "ZIP"):
        previous = 1.0 + 0.0j
        while offset < len(expected_rows) and expected_rows[offset]["family"] == family:
            expected = expected_rows[offset]
            calculated = solve(z, s_nominal, family, expected["scale"], previous, p_coeffs, q_coeffs)
            if calculated["converged"]:
                previous = calculated["voltage"]
            matches = calculated["converged"] == expected["converged"]
            if calculated["converged"]:
                matches = matches and abs(calculated["voltage_magnitude_pu"] - expected["voltage_magnitude_pu"]) <= 1.0e-9
                matches = matches and abs(calculated["residual_pu"] - expected["residual_pu"]) <= 1.0e-9
            rows.append({"family": family, "scale": expected["scale"], "converged": calculated["converged"], "voltage_magnitude_pu": calculated["voltage_magnitude_pu"], "residual_pu": calculated["residual_pu"], "matches_julia": matches})
            comparisons.append(matches)
            offset += 1
            if not calculated["converged"]:
                break
    result = {
        "witness_id": "LOAD-CONTINUATION-001-REPRO",
        "claim_id": "LOAD-CONTINUATION-001",
        "method": "independent pure-Python damped fixed-point continuation",
        "source_witness": "experiments/generated/load-grounding-witnesses.json",
        "rows": rows,
        "checks": {
            "all_rows_match_julia": all(comparisons),
            "independent_iteration_used": True,
            "cp_first_failure_is_scale_1_8": next(row["scale"] for row in rows if row["family"] == "CP" and not row["converged"]) == 1.8,
            "no_numpy_or_julia_import": True,
        },
        "all_checks_pass": all(comparisons),
        "interpretation": "Independent reproduction of the declared iteration-scoped scalar continuation probe; not a global collapse or saddle-node calculation.",
    }
    result["all_checks_pass"] = result["all_checks_pass"] and all(result["checks"].values())
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    if not result["all_checks_pass"]:
        raise SystemExit("independent load continuation reproduction failed")


if __name__ == "__main__":
    main()
