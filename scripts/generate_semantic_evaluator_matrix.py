#!/usr/bin/env python3
"""Bind every public certificate to its semantic evaluator and test path."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "experiments/generated"
OUTPUT = GENERATED / "semantic-evaluator-matrix.json"
STATE_SPACE_REF = "experiments/generated/state-space-unit-witness.json"

CASES = {
    "parallel-branch-certificate.json": ("experiments/run_vertical_slice.jl", "experiments/test/runtests.jl", "parallel_branch_certificate"),
    "degree-two-series-certificate.json": ("experiments/transformations/SeriesElimination.jl", "experiments/test/series_elimination.jl", "eliminate_degree_two"),
    "coordinate-normalization-certificate.json": ("experiments/transformations/ConductorNormalization.jl", "experiments/test/coordinate_normalization.jl", "normalize_conductor_coordinates"),
    "coordinate-series-composition-certificate.json": ("experiments/transformations/TransformationContracts.jl", "experiments/test/coordinate_normalization.jl", "compose_certificates"),
    "parallel-opf-comparison.json": ("experiments/transformations/ParallelDecisionComparison.jl", "experiments/test/parallel_decision_comparison.jl", "parallel_decision_certificate"),
    "transformer-winding-normalization-certificate.json": ("experiments/transformations/TransformerWindingNormalization.jl", "experiments/test/transformer_winding_normalization.jl", "normalize_winding_terminals"),
    "multiwinding-leakage-compilation-certificate.json": ("experiments/transformations/MultiwindingLeakageCompilation.jl", "experiments/test/multiwinding_leakage_compilation.jl", "compile_pairwise_leakage"),
    "multiwinding-terminal-assembly-certificate.json": ("experiments/transformations/MultiwindingTerminalAssembly.jl", "experiments/test/multiwinding_terminal_assembly.jl", "assemble_terminal_leakage"),
    "transformer-factor-completion-certificate.json": ("experiments/transformations/TransformerFactorCompletion.jl", "experiments/test/transformer_factor_completion.jl", "assemble_complete_transformer"),
    "transformer-tap-decision-certificate.json": ("experiments/transformations/TransformerTapDecisionCompilation.jl", "experiments/test/transformer_tap_decision_compilation.jl", "compile_parameterized_transformer"),
    "transformer-tap-ac-decision-certificate.json": ("experiments/transformations/TransformerTapACDecision.jl", "experiments/test/transformer_tap_ac_decision.jl", "transformer_tap_ac_certificate"),
    "transformer-tap-ac-independent-certificate.json": ("experiments/transformations/TransformerTapACIndependentReproduction.jl", "experiments/test/transformer_tap_ac_independent_reproduction.jl", "independent_transformer_tap_certificate"),
    "multiconductor-parallel-ac-certificate.json": ("experiments/transformations/MulticonductorParallelACDecision.jl", "experiments/test/multiconductor_parallel_ac.jl", "multiconductor_ac_certificate"),
    "four-wire-parallel-ac-certificate.json": ("experiments/transformations/FourWireParallelACDecision.jl", "experiments/test/four_wire_parallel_ac.jl", "four_wire_parallel_certificate"),
    "pi-four-wire-parallel-ac-certificate.json": ("experiments/transformations/PiFourWireParallelACDecision.jl", "experiments/test/pi_four_wire_parallel_ac.jl", "pi_four_wire_certificate"),
    "typed-kron-certificate.json": ("experiments/transformations/TypedKronReduction.jl", "experiments/test/typed_kron.jl", "kron_reduce"),
}


def main() -> int:
    rows = []
    for artifact, (evaluator, test_path, symbol) in CASES.items():
        certificate = json.loads((GENERATED / artifact).read_text())
        typed = certificate.get("typed_interfaces", {})
        evaluator_path = ROOT / evaluator
        test_file = ROOT / test_path
        evaluator_text = evaluator_path.read_text() if evaluator_path.is_file() else ""
        checks = {
            "source_target_declared": bool(certificate.get("source", {}).get("object_ids"))
            and bool(certificate.get("target", {}).get("object_ids")),
            "typed_interfaces_declared": bool(typed.get("state_space_ref"))
            and bool(typed.get("source_variable_labels") is not None)
            and bool(typed.get("target_variable_labels") is not None),
            "typed_state_space_is_canonical": typed.get("state_space_ref") == STATE_SPACE_REF,
            "unit_coverage_is_explicit": bool(typed.get("source_unit_families"))
            or bool(typed.get("target_unit_families"))
            or bool(typed.get("unresolved_unit_labels") is not None),
            "evaluator_path_exists": evaluator_path.is_file(),
            "evaluator_symbol_is_present": bool(
                f"function {symbol}" in evaluator_text or f"{symbol}(" in evaluator_text
            ),
            "semantic_test_path_exists": test_file.is_file(),
            "evidence_is_present": isinstance(certificate.get("evidence"), dict)
            and bool(certificate["evidence"]),
        }
        rows.append({
            "artifact": f"experiments/generated/{artifact}",
            "certificate_id": certificate.get("certificate_id"),
            "classification": certificate.get("classification"),
            "evaluator": evaluator,
            "evaluator_symbol": symbol,
            "semantic_test": test_path,
            "checks": checks,
            "valid": all(checks.values()),
        })

    artifact_set = {row["artifact"] for row in rows}
    result = {
        "witness_id": "PKG-SEMANTIC-001",
        "schema_version": "0.1.0",
        "state_space_ref": STATE_SPACE_REF,
        "rows": rows,
        "checks": {
            "all_certificates_covered": artifact_set == {
                f"experiments/generated/{name}" for name in CASES
            },
            "all_evaluators_exist": all(row["checks"]["evaluator_path_exists"] for row in rows),
            "all_tests_exist": all(row["checks"]["semantic_test_path_exists"] for row in rows),
            "all_typed_contracts_present": all(row["checks"]["typed_interfaces_declared"] for row in rows),
            "all_semantic_evidence_bound": all(row["valid"] for row in rows),
        },
    }
    result["valid"] = all(result["checks"].values())
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
