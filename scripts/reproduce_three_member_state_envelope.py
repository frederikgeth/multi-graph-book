#!/usr/bin/env python3
"""Independent reproduction of the finite three-member AC state envelope."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/generated/three-member-four-wire-parallel-ac-certificate.json"
OUTPUT = ROOT / "experiments/generated/three-member-state-envelope-independent-reproduction.json"


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


def norm_inf(values: list[float]) -> float:
    return max(abs(value) for value in values)


def real_state(voltage: list[complex]) -> list[float]:
    return [value.real for value in voltage] + [value.imag for value in voltage]


def complex_state(state: list[float]) -> list[complex]:
    return [state[index] + 1j * state[index + 4] for index in range(4)]


def impedance_data() -> tuple[list[list[complex]], list[list[complex]]]:
    z1 = [
        [0.040 + 0.080j, 0.008 + 0.018j, 0.007 + 0.016j, 0.006 + 0.014j],
        [0.008 + 0.018j, 0.043 + 0.084j, 0.009 + 0.019j, 0.007 + 0.015j],
        [0.007 + 0.016j, 0.009 + 0.019j, 0.046 + 0.088j, 0.008 + 0.017j],
        [0.006 + 0.014j, 0.007 + 0.015j, 0.008 + 0.017j, 0.060 + 0.105j],
    ]
    z2_base = [
        [0.050 + 0.095j, 0.006 + 0.014j, 0.005 + 0.012j, 0.004 + 0.010j],
        [0.006 + 0.014j, 0.056 + 0.102j, 0.007 + 0.015j, 0.005 + 0.011j],
        [0.005 + 0.012j, 0.007 + 0.015j, 0.061 + 0.110j, 0.006 + 0.013j],
        [0.004 + 0.010j, 0.005 + 0.011j, 0.006 + 0.013j, 0.075 + 0.130j],
    ]
    z2 = [[4.0 * value for value in row] for row in z2_base]
    return z1, z2


def state_admittances(state: str) -> list[list[list[complex]]]:
    z1, z2 = impedance_data()
    y1, y2 = invert(z1), invert(z2)
    if state == "higher_admittance":
        y1 = [[1.08 * value for value in row] for row in y1]
        y2 = [[1.08 * value for value in row] for row in y2]
    elif state == "lower_admittance":
        y1 = [[0.92 * value for value in row] for row in y1]
        y2 = [[0.92 * value for value in row] for row in y2]
    elif state == "phase_selective":
        s1 = [1.03, 0.97, 1.02, 1.00]
        s2 = [0.98, 1.04, 0.96, 1.00]
        y1 = [[s1[row] * value for value in row_values] for row, row_values in enumerate(y1)]
        y2 = [[s2[row] * value for value in row_values] for row, row_values in enumerate(y2)]
    y3 = [[0.10 * (y1[row][column] + y2[row][column]) for column in range(4)] for row in range(4)]
    return [y1, y2, y3]


SLACK = [1.0 + 0j, complex(-0.5, -0.8660254037844386), complex(-0.5, 0.8660254037844386), 0j]
LOAD_DIRECTION = [0.70 + 0.14j, 0.55 + 0.12j, 0.42 + 0.09j]
LIMITS = [[0.72] * 4, [0.72] * 4, [0.15] * 4]


def residual(state: list[float], served: float, admittances: list[list[list[complex]]]) -> list[float]:
    voltage = complex_state(state)
    total = [0j] * 4
    for y in admittances:
        current = matvec(y, [SLACK[index] - voltage[index] for index in range(4)])
        total = [total[index] + current[index] for index in range(4)]
    phase_voltage = [voltage[index] - voltage[3] for index in range(3)]
    powers = [phase_voltage[index] * total[index].conjugate() for index in range(3)]
    complex_residual = [powers[index] - served * LOAD_DIRECTION[index] for index in range(3)] + [sum(total)]
    return [value.real for value in complex_residual] + [value.imag for value in complex_residual]


def power_flow(served: float, start: list[complex], admittances: list[list[list[complex]]]) -> tuple[bool, list[complex], float]:
    state = real_state(start)
    for _ in range(50):
        r = residual(state, served, admittances)
        rnorm = norm_inf(r)
        if rnorm <= 1e-10:
            return True, complex_state(state), rnorm
        jacobian = [[0.0] * 8 for _ in range(8)]
        for column in range(8):
            increment = 1e-7 * max(abs(state[column]), 1.0)
            perturbed = state[:]
            perturbed[column] += increment
            rp = residual(perturbed, served, admittances)
            for row in range(8):
                jacobian[row][column] = (rp[row] - r[row]) / increment
        step = solve([[complex(value) for value in row] for row in jacobian], [-value + 0j for value in r])
        accepted = False
        damping = 1.0
        for _ in range(20):
            candidate = [state[index] + damping * step[index].real for index in range(8)]
            candidate_norm = norm_inf(residual(candidate, served, admittances))
            if candidate_norm < rnorm:
                state = candidate
                accepted = True
                break
            damping /= 2.0
        if not accepted:
            break
    return False, complex_state(state), norm_inf(residual(state, served, admittances))


def feasibility(served: float, start: list[complex], admittances: list[list[list[complex]]]) -> dict:
    converged, voltage, residual_norm = power_flow(served, start, admittances)
    currents = [matvec(y, [SLACK[index] - voltage[index] for index in range(4)]) for y in admittances]
    phase_voltage = [abs(voltage[index] - voltage[3]) for index in range(3)]
    current_margin = min(LIMITS[line][conductor] - abs(currents[line][conductor]) for line in range(3) for conductor in range(4))
    voltage_margin = min(min(value - 0.88 for value in phase_voltage), min(1.05 - value for value in phase_voltage))
    return {"served": served, "converged": converged, "voltage": voltage, "residual": residual_norm, "current_margin": current_margin, "voltage_margin": voltage_margin, "feasible": converged and current_margin >= -1e-8 and voltage_margin >= -1e-8}


def boundary(admittances):
    voltage = SLACK[:]
    lower = feasibility(0.0, voltage, admittances)
    upper = None
    served = 0.05
    while served <= 3.0:
        point = feasibility(served, voltage, admittances)
        if point["converged"]:
            voltage = point["voltage"]
        if not point["feasible"]:
            upper = point
            break
        lower = point
        served += 0.05
    if upper is None:
        raise ValueError("failed to bracket boundary")
    for _ in range(80):
        if upper["served"] - lower["served"] <= 1e-8:
            break
        midpoint = 0.5 * (lower["served"] + upper["served"])
        point = feasibility(midpoint, lower["voltage"], admittances)
        if point["feasible"]:
            lower = point
        else:
            upper = point
    return lower


def main() -> None:
    reference = json.loads(SOURCE.read_text())
    rows, matches = [], []
    for expected in reference["finite_state_envelope"]["states"]:
        calculated = boundary(state_admittances(expected["state"]))
        match = abs(calculated["served"] - expected["independent_boundary"]) <= 5e-7
        matches.append(match)
        rows.append({"state": expected["state"], "boundary_served_fraction": calculated["served"], "power_flow_residual": calculated["residual"], "matches_julia": match})
    checks = {"all_state_boundaries_match_julia": all(matches), "all_boundaries_converged": all(row["power_flow_residual"] <= 1e-9 for row in rows), "independent_solver_used": True, "no_numpy_or_julia_import": True}
    result = {"witness_id": "TR-PAR-STATE-001-REPRO", "claim_id": "TR-PAR-STATE-001", "method": "independent pure-Python finite-difference Newton continuation and bisection", "source_witness": "experiments/generated/three-member-four-wire-parallel-ac-certificate.json", "rows": rows, "checks": checks, "all_checks_pass": all(checks.values()), "interpretation": "Independent reproduction of all four local state-envelope boundaries; not a global AC optimality proof."}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT.relative_to(ROOT))
    if not result["all_checks_pass"]:
        raise SystemExit("three-member state envelope reproduction failed")


if __name__ == "__main__":
    main()
