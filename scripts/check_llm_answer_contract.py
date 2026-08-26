#!/usr/bin/env python3
"""Check claim coverage, citation presence, and audience packet integrity."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

from llm_service import BookLLMService, validate_answer_response

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "llm/evaluation-cases.toml"


def main() -> int:
    service = BookLLMService()
    errors: list[str] = []
    cases = tomllib.loads(CASES.read_text()).get("case", [])
    for case in cases:
        response = service.response(case["question"], case["audience"])
        validation_errors = validate_answer_response(service.index, response)
        expected = {
            *{f"claim:{item}" for item in case["required_claim_ids"]},
            *{f"concept:{item}" for item in case["required_concept_ids"]},
        }
        observed = {item["record_id"] for item in response["packet"]["mandatory_records"]}
        if expected - observed:
            validation_errors.append(f"missing mandatory records: {sorted(expected - observed)}")
        if response["packet"]["status"] != "qualified":
            validation_errors.append(f"expected qualified packet, got {response['packet']['status']}")
        if case["misconception_id"] == "parallel-admittance-implies-decision-equivalence":
            packet = response["packet"]
            if "knowledge:PSK-000001" not in observed:
                validation_errors.append("parallel route omits mandatory PSK-000001")
            if [item.get("knowledge_id") for item in packet["scientific_basis"]] != ["PSK-000001"]:
                validation_errors.append("parallel route scientific basis differs from PSK-000001")
            checks = packet["executable_checks"]
            if len(checks) != 1 or checks[0].get("contract_ids") != ["parallel_member_limit_preservation"]:
                validation_errors.append("parallel route omits the executable preservation contract")
            if len(packet["counterexamples"]) != 1 or packet["counterexamples"][0].get("counterexample_ids") != ["parallel-rating-outer-relaxation-001"]:
                validation_errors.append("parallel route omits the linked counterexample fixture")
            if checks and checks[0].get("implementation_status") != "implemented":
                validation_errors.append("parallel executable contract is not marked implemented")
        if case["misconception_id"] == "ground-neutral-reference-are-one-node":
            packet = response["packet"]
            if "knowledge:PSK-000002" not in observed:
                validation_errors.append("neutral/ground route omits mandatory PSK-000002")
            if [item.get("knowledge_id") for item in packet["scientific_basis"]] != ["PSK-000002"]:
                validation_errors.append("neutral/ground route scientific basis differs from PSK-000002")
            checks = packet["executable_checks"]
            if len(checks) != 1 or checks[0].get("contract_ids") != ["neutral_ground_reference_preservation"]:
                validation_errors.append("neutral/ground route omits the executable preservation contract")
            if len(packet["counterexamples"]) != 1 or packet["counterexamples"][0].get("counterexample_ids") != ["neutral-ground-reference-conflation-001"]:
                validation_errors.append("neutral/ground route omits the linked counterexample fixture")
            if checks and checks[0].get("implementation_status") != "implemented":
                validation_errors.append("neutral/ground executable contract is not marked implemented")
        if case["misconception_id"] == "solver-termination-implies-validated-solution":
            packet = response["packet"]
            if "knowledge:PSK-000003" not in observed:
                validation_errors.append("solver-validity route omits mandatory PSK-000003")
            if [item.get("knowledge_id") for item in packet["scientific_basis"]] != ["PSK-000003"]:
                validation_errors.append("solver-validity route scientific basis differs from PSK-000003")
            checks = packet["executable_checks"]
            if len(checks) != 1 or checks[0].get("contract_ids") != ["claimed_solution_validity"]:
                validation_errors.append("solver-validity route omits the executable validation contract")
            if len(packet["counterexamples"]) != 1 or packet["counterexamples"][0].get("counterexample_ids") != ["claimed-feasible-invalid-solution-001"]:
                validation_errors.append("solver-validity route omits the linked counterexample fixture")
            if checks and checks[0].get("implementation_status") != "implemented":
                validation_errors.append("solver-validity executable contract is not marked implemented")
        if case["misconception_id"] == "wye-delta-share-nominal-voltage-base":
            packet = response["packet"]
            if "knowledge:PSK-000004" not in observed:
                validation_errors.append("load-voltage-base route omits mandatory PSK-000004")
            if [item.get("knowledge_id") for item in packet["scientific_basis"]] != ["PSK-000004"]:
                validation_errors.append("load-voltage-base route scientific basis differs from PSK-000004")
            checks = packet["executable_checks"]
            if len(checks) != 1 or checks[0].get("contract_ids") != ["load_voltage_base_consistency"]:
                validation_errors.append("load-voltage-base route omits the executable consistency contract")
            if len(packet["counterexamples"]) != 1 or packet["counterexamples"][0].get("counterexample_ids") != ["load-voltage-base-mismatch-001"]:
                validation_errors.append("load-voltage-base route omits the linked counterexample fixture")
            if checks and checks[0].get("implementation_status") != "implemented":
                validation_errors.append("load-voltage-base executable contract is not marked implemented")
        if case["misconception_id"] == "fixed-tap-snapshot-preserves-adjustable-transformer":
            packet = response["packet"]
            if "knowledge:PSK-000005" not in observed:
                validation_errors.append("transformer-tap route omits mandatory PSK-000005")
            if [item.get("knowledge_id") for item in packet["scientific_basis"]] != ["PSK-000005"]:
                validation_errors.append("transformer-tap route scientific basis differs from PSK-000005")
            checks = packet["executable_checks"]
            if len(checks) != 1 or checks[0].get("contract_ids") != ["transformer_tap_domain_preservation"]:
                validation_errors.append("transformer-tap route omits the executable domain-preservation contract")
            if len(packet["counterexamples"]) != 1 or packet["counterexamples"][0].get("counterexample_ids") != ["transformer-tap-domain-loss-001"]:
                validation_errors.append("transformer-tap route omits the linked counterexample fixture")
            if checks and checks[0].get("implementation_status") != "implemented":
                validation_errors.append("transformer-tap executable contract is not marked implemented")
        if case["misconception_id"] == "transformer-end-swap-is-ordinary-edge-reversal":
            packet = response["packet"]
            if "knowledge:PSK-000006" not in observed:
                validation_errors.append("transformer-winding route omits mandatory PSK-000006")
            if [item.get("knowledge_id") for item in packet["scientific_basis"]] != ["PSK-000006"]:
                validation_errors.append("transformer-winding route scientific basis differs from PSK-000006")
            checks = packet["executable_checks"]
            if len(checks) != 1 or checks[0].get("contract_ids") != ["transformer_winding_convention_preservation"]:
                validation_errors.append("transformer-winding route omits the executable convention-preservation contract")
            if len(packet["counterexamples"]) != 1 or packet["counterexamples"][0].get("counterexample_ids") != ["transformer-winding-role-swap-001"]:
                validation_errors.append("transformer-winding route omits the linked counterexample fixture")
            if checks and checks[0].get("implementation_status") != "implemented":
                validation_errors.append("transformer-winding executable contract is not marked implemented")
        for error in validation_errors:
            errors.append(f"{case['case_id']}/{case['audience']}: {error}")
    if errors:
        print("LLM answer-contract check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"LLM answer contract: {len(cases)} audience-specific packets have claim, citation, and source validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
