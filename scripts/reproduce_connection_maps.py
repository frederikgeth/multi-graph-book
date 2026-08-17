#!/usr/bin/env python3
"""Independent reproduction of the wye/delta terminal-map witness."""

from __future__ import annotations

import cmath
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/generated/load-grounding-witnesses.json"
OUTPUT = ROOT / "experiments/generated/connection-map-independent-reproduction.json"


def decode(value: dict[str, float]) -> complex:
    return complex(value["real"], value["imag"])


def apply_map(matrix: list[list[int]], vector: list[complex]) -> list[complex]:
    return [sum(coefficient * value for coefficient, value in zip(row, vector)) for row in matrix]


def max_norm(left: list[complex], right: list[complex]) -> float:
    return max(abs(a - b) for a, b in zip(left, right))


def main() -> None:
    expected = json.loads(SOURCE.read_text())["connection_maps"]
    a = cmath.exp(2j * cmath.pi / 3)
    phase = [1 + 0j, a**2, a]
    terminals = phase + [0j]
    wye_map = [[1, 0, 0, -1], [0, 1, 0, -1], [0, 0, 1, -1]]
    delta_map = [[1, -1, 0, 0], [0, 1, -1, 0], [-1, 0, 1, 0]]
    wye = apply_map(wye_map, terminals)
    delta = apply_map(delta_map, terminals)
    expected_wye = [decode(value) for value in expected["wye_voltage"]]
    expected_delta = [decode(value) for value in expected["delta_voltage"]]
    result = {
        "witness_id": "LOAD-CONNECTION-001-REPRO",
        "claim_id": "LOAD-CONNECTION-001",
        "method": "independent pure-Python complex terminal-map evaluation",
        "source_witness": "experiments/generated/load-grounding-witnesses.json",
        "wye_inf_norm": max_norm(wye, expected_wye),
        "delta_inf_norm": max_norm(delta, expected_delta),
        "checks": {
            "wye_matches_julia": max_norm(wye, expected_wye) <= 1.0e-12,
            "delta_matches_julia": max_norm(delta, expected_delta) <= 1.0e-12,
            "wye_magnitudes_are_one": all(abs(abs(value) - 1.0) <= 1.0e-12 for value in wye),
            "delta_magnitudes_are_sqrt_three": all(abs(abs(value) - (3.0**0.5)) <= 1.0e-12 for value in delta),
            "no_numpy_or_julia_import": True,
        },
        "all_checks_pass": True,
        "interpretation": "Independent reproduction of the declared linear wye/delta terminal maps; not a multiconductor load-flow or rating validation.",
    }
    result["all_checks_pass"] = all(result["checks"].values())
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    if not result["all_checks_pass"]:
        raise SystemExit("independent connection-map reproduction failed")


if __name__ == "__main__":
    main()
