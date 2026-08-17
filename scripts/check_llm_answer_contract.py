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
