#!/usr/bin/env python3
"""Validate and score the first scientifically constrained agent benchmark slice."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmarks/agent/parallel-member-limits-v1.json"
BENCHMARK_SCHEMA = ROOT / "schemas/agent-benchmark.schema.json"
SUBMISSION_SCHEMA = ROOT / "schemas/agent-benchmark-submission.schema.json"
PAIR = ROOT / "generated/federated-knowledge-pair-manifest.json"
CORPUS_MANIFEST = ROOT / "llm/generated/corpus-manifest.json"
OUTPUT_DIR = ROOT / "benchmarks/agent/generated"
MANIFEST = OUTPUT_DIR / "benchmark-manifest.json"
CONFORMANCE = OUTPUT_DIR / "conformance-evaluation.json"

SCHEMA_VERSION = "0.1.0"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
BENCHMARK_ID = re.compile(r"^ABENCH-[A-Z0-9-]+$")
CASE_ID = re.compile(r"^ABENCH-[A-Z0-9-]+$")
CONDITION_ID = re.compile(r"^C[0-9]+_[A-Z0-9_]+$")
PSK_ID = re.compile(r"^PSK-[0-9]{6}$")
STATUSES = {"passed", "failed", "inapplicable", "indeterminate"}
ACTIONS = {"accept", "reject", "abstain"}
DIMENSIONS = {
    "code_correctness",
    "schema_validity",
    "model_semantic_correctness",
    "physical_correctness",
    "numerical_validity",
    "scientific_inference_correctness",
    "reproducibility",
    "invalid_assumption_detection",
    "abstention",
}
LOCAL_SOURCES = (
    Path("benchmarks/agent/README.md"),
    Path("benchmarks/agent/parallel-member-limits-v1.json"),
    Path("benchmarks/agent/submissions/conforming-c6.json"),
    Path("benchmarks/agent/submissions/unsafe-c0.json"),
    Path("benchmarks/agent/submissions/boundary-overclaim-c1.json"),
    Path("schemas/agent-benchmark.schema.json"),
    Path("schemas/agent-benchmark-submission.schema.json"),
    Path("scripts/check_agent_benchmark.py"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain one JSON object")
    return value


def add_if(condition: bool, message: str, errors: list[str]) -> None:
    if condition:
        errors.append(message)


def require_string_list(value: object, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{label} must be a nonempty string array")
        return []
    if len(value) != len(set(value)):
        errors.append(f"{label} must not contain duplicates")
    return value


def validate_spec(spec: dict, pair: dict, errors: list[str]) -> None:
    required = {
        "schema_version", "benchmark_id", "status", "research_question", "scope",
        "condition_order", "conditions", "scoring_dimensions", "unscored_dimensions",
        "cases", "book_sources", "bmopftools_sources", "conformance_fixtures", "limitations",
    }
    add_if(not required <= set(spec), f"benchmark missing fields: {sorted(required - set(spec))}", errors)
    add_if(spec.get("schema_version") != SCHEMA_VERSION, "benchmark schema version drift", errors)
    benchmark_id = spec.get("benchmark_id", "")
    add_if(not isinstance(benchmark_id, str) or not BENCHMARK_ID.fullmatch(benchmark_id),
           f"invalid benchmark ID: {benchmark_id}", errors)
    add_if(spec.get("status") != "substrate_only_no_agent_runs",
           "first slice must remain substrate_only_no_agent_runs until controlled runs exist", errors)

    order = require_string_list(spec.get("condition_order"), "condition_order", errors)
    conditions = spec.get("conditions", [])
    if not isinstance(conditions, list):
        errors.append("conditions must be an array")
        conditions = []
    condition_ids = [item.get("condition_id") for item in conditions if isinstance(item, dict)]
    add_if(condition_ids != order, "condition_order must exactly match the ordered condition records", errors)
    add_if(any(not isinstance(item, str) or not CONDITION_ID.fullmatch(item) for item in order),
           "condition IDs must use the controlled Cn_NAME form", errors)
    cumulative: list[str] = []
    for item in conditions:
        if not isinstance(item, dict):
            errors.append("condition entries must be objects")
            continue
        condition_id = item.get("condition_id", "<missing>")
        added = item.get("added_capabilities", [])
        recorded = item.get("cumulative_capabilities", [])
        if not isinstance(added, list) or not all(isinstance(value, str) and value for value in added):
            errors.append(f"{condition_id}: added_capabilities must be a string array")
            continue
        for capability in added:
            if capability not in cumulative:
                cumulative.append(capability)
        add_if(recorded != cumulative, f"{condition_id}: cumulative capability lattice is stale", errors)

    dimensions = set(require_string_list(spec.get("scoring_dimensions"), "scoring_dimensions", errors))
    add_if(dimensions != DIMENSIONS,
           f"scoring dimensions differ: missing={sorted(DIMENSIONS - dimensions)}, extra={sorted(dimensions - DIMENSIONS)}",
           errors)
    unscored = spec.get("unscored_dimensions", {})
    add_if(not isinstance(unscored, dict) or set(unscored) != {"code_correctness"},
           "the first slice must explicitly mark only code_correctness as unscored", errors)

    cases = spec.get("cases", [])
    if not isinstance(cases, list):
        errors.append("cases must be an array")
        cases = []
    case_ids = [case.get("case_id") for case in cases if isinstance(case, dict)]
    add_if(len(case_ids) != len(set(case_ids)), "benchmark case IDs must be unique", errors)
    task_kinds: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            errors.append("case entries must be objects")
            continue
        case_id = case.get("case_id", "<missing>")
        add_if(not isinstance(case_id, str) or not CASE_ID.fullmatch(case_id),
               f"invalid case ID: {case_id}", errors)
        task_kind = case.get("task_kind")
        task_kinds.add(task_kind)
        add_if(task_kind not in {"invalid_assumption_detection", "abstention"},
               f"{case_id}: invalid task kind {task_kind}", errors)
        add_if(not str(case.get("prompt", "")).strip(), f"{case_id}: empty prompt", errors)
        expected = case.get("expected", {})
        if not isinstance(expected, dict):
            errors.append(f"{case_id}: expected must be an object")
            continue
        add_if(expected.get("action") not in ACTIONS, f"{case_id}: invalid expected action", errors)
        add_if(expected.get("contract_status") not in STATUSES, f"{case_id}: invalid expected status", errors)
        require_string_list(expected.get("knowledge_ids"), f"{case_id}.expected.knowledge_ids", errors)
        require_string_list(expected.get("finding_codes"), f"{case_id}.expected.finding_codes", errors)
        require_string_list(expected.get("qualification_codes"), f"{case_id}.expected.qualification_codes", errors)
        scored = set(require_string_list(case.get("dimensions_scored"), f"{case_id}.dimensions_scored", errors))
        add_if(not scored <= DIMENSIONS, f"{case_id}: unknown scoring dimension", errors)
        add_if("code_correctness" in scored, f"{case_id}: code_correctness is outside this slice", errors)
        require_string_list(case.get("does_not_establish"), f"{case_id}.does_not_establish", errors)
    add_if(task_kinds != {"invalid_assumption_detection", "abstention"},
           "first slice must contain invalid-assumption and abstention cases", errors)

    book_sources = require_string_list(spec.get("book_sources"), "book_sources", errors)
    for path_string in book_sources:
        add_if(not (ROOT / path_string).is_file(), f"missing book benchmark source: {path_string}", errors)
    require_string_list(spec.get("bmopftools_sources"), "bmopftools_sources", errors)
    require_string_list(spec.get("limitations"), "limitations", errors)

    links = pair.get("links", {}).get("PSK-000001", {})
    contracts = {item.get("contract_id"): item for item in links.get("contracts", [])}
    contract = contracts.get("parallel_member_limit_preservation", {})
    add_if(not contract, "federated pair lacks the PSK-000001 executable contract", errors)
    add_if("parallel-rating-outer-relaxation-001" not in contract.get("fixture_ids", []),
           "federated pair lacks the benchmark fixture", errors)
    add_if("parallel_member_limits" not in {item.get("recipe_id") for item in contract.get("recipes", [])},
           "federated pair lacks the benchmark recipe", errors)
    pair_findings = set(contract.get("finding_codes", []))
    add_if(not set(spec.get("finding_codes", [])) <= pair_findings,
           "benchmark Finding codes are outside the pinned contract", errors)


def validate_submission(submission: dict, spec: dict) -> list[str]:
    errors: list[str] = []
    required = {"schema_version", "benchmark_id", "run_id", "condition_id", "system", "provenance", "cases"}
    add_if(set(submission) != required,
           f"submission fields differ: missing={sorted(required - set(submission))}, extra={sorted(set(submission) - required)}",
           errors)
    add_if(submission.get("schema_version") != SCHEMA_VERSION, "submission schema version drift", errors)
    add_if(submission.get("benchmark_id") != spec.get("benchmark_id"), "submission benchmark ID mismatch", errors)
    add_if(not str(submission.get("run_id", "")).strip(), "submission run_id is empty", errors)
    add_if(submission.get("condition_id") not in spec.get("condition_order", []), "unknown submission condition", errors)
    system = submission.get("system", {})
    if not isinstance(system, dict):
        errors.append("submission system must be an object")
    else:
        for field in ("provider", "model_id", "model_revision"):
            add_if(not str(system.get(field, "")).strip(), f"submission system.{field} is empty", errors)
    provenance = submission.get("provenance", {})
    if not isinstance(provenance, dict):
        errors.append("submission provenance must be an object")
    else:
        expected_fields = {"federated_pair_id", "book_llm_corpus_sha256", "bmopftools_executable_corpus_sha256"}
        add_if(set(provenance) != expected_fields, "submission provenance fields differ", errors)

    expected_cases = {case["case_id"] for case in spec.get("cases", [])}
    cases = submission.get("cases", [])
    if not isinstance(cases, list):
        errors.append("submission cases must be an array")
        return errors
    case_ids = [case.get("case_id") for case in cases if isinstance(case, dict)]
    add_if(len(case_ids) != len(set(case_ids)), "submission case IDs must be unique", errors)
    add_if(set(case_ids) != expected_cases,
           f"submission case coverage differs: missing={sorted(expected_cases - set(case_ids))}, extra={sorted(set(case_ids) - expected_cases)}",
           errors)
    case_required = {
        "case_id", "action", "contract_status", "classification", "knowledge_ids",
        "finding_codes", "qualification_codes",
    }
    for case in cases:
        if not isinstance(case, dict):
            errors.append("submission case entries must be objects")
            continue
        case_id = case.get("case_id", "<missing>")
        allowed = case_required | {"witness"}
        add_if(not case_required <= set(case), f"{case_id}: missing submission case fields", errors)
        add_if(not set(case) <= allowed, f"{case_id}: unexpected submission case fields", errors)
        add_if(case.get("action") not in ACTIONS, f"{case_id}: invalid action", errors)
        add_if(case.get("contract_status") not in STATUSES, f"{case_id}: invalid contract status", errors)
        for field in ("knowledge_ids", "finding_codes", "qualification_codes"):
            value = case.get(field)
            add_if(not isinstance(value, list) or not all(isinstance(item, str) for item in value),
                   f"{case_id}: {field} must be a string array", errors)
        add_if(any(not PSK_ID.fullmatch(item) for item in case.get("knowledge_ids", []) if isinstance(item, str)),
               f"{case_id}: invalid PSK identity", errors)
    return errors


def equal_number(actual: object, expected: object, tolerance: float = 1e-9) -> bool:
    if isinstance(expected, bool):
        return actual is expected
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        return isinstance(actual, (int, float)) and not isinstance(actual, bool) and abs(float(actual) - float(expected)) <= tolerance
    return actual == expected


def score_submission(submission: dict, spec: dict, provenance: dict) -> dict:
    validation_errors = validate_submission(submission, spec)
    supplied = {
        case.get("case_id"): case
        for case in submission.get("cases", [])
        if isinstance(case, dict) and isinstance(case.get("case_id"), str)
    }
    expected_provenance = {
        "federated_pair_id": provenance["federated_pair_id"],
        "book_llm_corpus_sha256": provenance["book_llm_corpus_sha256"],
        "bmopftools_executable_corpus_sha256": provenance["bmopftools_executable_corpus_sha256"],
    }
    provenance_ok = submission.get("provenance") == expected_provenance
    case_reports: list[dict] = []
    for task in spec.get("cases", []):
        case_id = task["case_id"]
        answer = supplied.get(case_id, {})
        expected = task["expected"]
        qualification_ok = set(expected["qualification_codes"]) <= set(answer.get("qualification_codes", []))
        model_semantic_ok = all(
            answer.get(field) == expected.get(field)
            for field in ("action", "contract_status", "classification")
        )
        scientific_ok = (
            set(answer.get("knowledge_ids", [])) == set(expected["knowledge_ids"])
            and set(answer.get("finding_codes", [])) == set(expected["finding_codes"])
        )
        if "witness" in expected:
            actual_witness = answer.get("witness", {})
            numerical_ok: bool | None = isinstance(actual_witness, dict) and all(
                equal_number(actual_witness.get(field), value)
                for field, value in expected["witness"].items()
            )
        else:
            numerical_ok = None
        scores: dict[str, bool | None] = {
            "code_correctness": None,
            "schema_validity": not validation_errors,
            "model_semantic_correctness": model_semantic_ok,
            "physical_correctness": qualification_ok,
            "numerical_validity": numerical_ok,
            "scientific_inference_correctness": scientific_ok,
            "reproducibility": provenance_ok,
            "invalid_assumption_detection": (
                answer.get("action") == "reject"
                if task["task_kind"] == "invalid_assumption_detection" else None
            ),
            "abstention": (
                answer.get("action") == "abstain"
                if task["task_kind"] == "abstention" else None
            ),
        }
        scored_dimensions = set(task["dimensions_scored"])
        for dimension in DIMENSIONS - scored_dimensions:
            scores[dimension] = None
        case_pass = all(value for value in scores.values() if value is not None)
        case_reports.append({
            "case_id": case_id,
            "task_kind": task["task_kind"],
            "pass": case_pass,
            "scores": scores,
        })
    overall = not validation_errors and all(case["pass"] for case in case_reports)
    return {
        "run_id": submission.get("run_id"),
        "condition_id": submission.get("condition_id"),
        "pass": overall,
        "validation_errors": validation_errors,
        "cases": case_reports,
    }


def current_provenance(pair: dict, corpus: dict) -> dict:
    return {
        "federated_pair_id": pair.get("pair_id"),
        "federated_pair_sha256": pair.get("pair_sha256"),
        "book_llm_corpus_sha256": corpus.get("corpus_sha256"),
        "bmopftools_executable_corpus_sha256": pair.get("bmopftools", {}).get("corpus_sha256"),
        "bmopftools_manifest_sha256": pair.get("bmopftools", {}).get("manifest_sha256"),
    }


def source_records(base: Path, paths: list[str], errors: list[str]) -> list[dict]:
    records: list[dict] = []
    for path_string in paths:
        path = base / path_string
        if not path.is_file():
            errors.append(f"missing source file: {path}")
            continue
        records.append({"path": path_string, "sha256": sha256(path)})
    return records


def expected_outputs(spec: dict, pair: dict, corpus: dict, bmopf_root: Path | None,
                     recorded_manifest: dict | None, errors: list[str]) -> tuple[dict, dict]:
    provenance = current_provenance(pair, corpus)
    local_records = source_records(ROOT, [path.as_posix() for path in LOCAL_SOURCES], errors)
    if bmopf_root is not None:
        bmopf_records = source_records(bmopf_root, spec.get("bmopftools_sources", []), errors)
        bmopf_manifest = bmopf_root / "generated/executable-knowledge-manifest.json"
        if bmopf_manifest.is_file():
            add_if(sha256(bmopf_manifest) != provenance["bmopftools_manifest_sha256"],
                   "live BMOPFTools manifest differs from the federated pair", errors)
    elif recorded_manifest is not None:
        bmopf_records = recorded_manifest.get("bmopftools_sources", [])
        recorded_paths = [item.get("path") for item in bmopf_records if isinstance(item, dict)]
        add_if(recorded_paths != spec.get("bmopftools_sources", []),
               "recorded BMOPFTools source list differs from the benchmark specification", errors)
        add_if(any(
            not isinstance(item, dict)
            or not SHA256.fullmatch(str(item.get("sha256", "")))
            for item in bmopf_records
        ), "recorded BMOPFTools source hashes are malformed", errors)
    else:
        errors.append("--write requires --bmopf-root for source-bound BMOPFTools evidence")
        bmopf_records = []

    reports: list[dict] = []
    for fixture in spec.get("conformance_fixtures", []):
        path = ROOT / fixture.get("path", "")
        if not path.is_file():
            errors.append(f"missing conformance fixture: {fixture.get('path')}")
            continue
        submission = load_json(path)
        report = score_submission(submission, spec, provenance)
        expected_pass = fixture.get("expected_pass")
        add_if(report["pass"] is not expected_pass,
               f"{fixture.get('path')}: expected pass={expected_pass}, observed {report['pass']}", errors)
        report["fixture_path"] = fixture.get("path")
        report["expected_pass"] = expected_pass
        reports.append(report)

    dimension_counts: dict[str, dict[str, int]] = {}
    for dimension in sorted(DIMENSIONS):
        values = [
            case["scores"][dimension]
            for report in reports
            for case in report["cases"]
            if case["scores"][dimension] is not None
        ]
        dimension_counts[dimension] = {
            "scored": len(values),
            "passed": sum(value is True for value in values),
            "failed": sum(value is False for value in values),
        }

    conformance = {
        "schema_version": SCHEMA_VERSION,
        "benchmark_id": spec.get("benchmark_id"),
        "status": "harness_conformance_only_not_agent_results",
        "provenance": provenance,
        "summary": {
            "fixtures": len(reports),
            "expected_passing_fixtures": sum(item.get("expected_pass") is True for item in spec.get("conformance_fixtures", [])),
            "observed_passing_fixtures": sum(report["pass"] for report in reports),
            "dimension_counts": dimension_counts,
        },
        "reports": reports,
        "does_not_establish": [
            "Any model or agent performs better under a richer condition.",
            "The transparent task set is contamination-resistant.",
            "The benchmark measures code correctness.",
        ],
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "benchmark_id": spec.get("benchmark_id"),
        "status": spec.get("status"),
        "provenance": provenance,
        "benchmark_schema_sha256": sha256(BENCHMARK_SCHEMA),
        "submission_schema_sha256": sha256(SUBMISSION_SCHEMA),
        "local_sources": local_records,
        "bmopftools_sources": bmopf_records,
        "conformance_status": conformance["status"],
    }
    return manifest, conformance


def dump(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write the pinned manifest and conformance report")
    mode.add_argument("--check", action="store_true", help="check committed outputs (default)")
    mode.add_argument("--score", type=Path, help="score one submission and print JSON")
    parser.add_argument("--bmopf-root", type=Path, help="live BMOPFTools sibling checkout")
    args = parser.parse_args()

    errors: list[str] = []
    try:
        spec = load_json(BENCHMARK)
        pair = load_json(PAIR)
        corpus = load_json(CORPUS_MANIFEST)
        benchmark_schema = load_json(BENCHMARK_SCHEMA)
        submission_schema = load_json(SUBMISSION_SCHEMA)
        recorded_manifest = load_json(MANIFEST) if MANIFEST.is_file() else None
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"agent benchmark check failed to load inputs: {error}")
        return 1

    validate_spec(spec, pair, errors)
    add_if(benchmark_schema.get("properties", {}).get("schema_version", {}).get("const") != SCHEMA_VERSION,
           "benchmark JSON schema version drift", errors)
    add_if(submission_schema.get("properties", {}).get("schema_version", {}).get("const") != SCHEMA_VERSION,
           "submission JSON schema version drift", errors)

    bmopf_root = args.bmopf_root.resolve() if args.bmopf_root else None
    expected_manifest, expected_conformance = expected_outputs(
        spec, pair, corpus, bmopf_root, recorded_manifest, errors
    )

    if args.score:
        try:
            submission = load_json(args.score.resolve())
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"could not load submission: {error}", file=sys.stderr)
            return 1
        report = score_submission(submission, spec, current_provenance(pair, corpus))
        print(dump(report), end="")
        return 0 if not report["validation_errors"] else 1

    if errors:
        print("agent benchmark check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    if args.write:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(dump(expected_manifest))
        CONFORMANCE.write_text(dump(expected_conformance))
        print(f"wrote {MANIFEST.relative_to(ROOT)} and {CONFORMANCE.relative_to(ROOT)}")
    else:
        if not MANIFEST.is_file() or MANIFEST.read_text() != dump(expected_manifest):
            errors.append("agent benchmark manifest is missing or stale")
        if not CONFORMANCE.is_file() or CONFORMANCE.read_text() != dump(expected_conformance):
            errors.append("agent benchmark conformance report is missing or stale")
        if errors:
            print("agent benchmark check failed:")
            for error in errors:
                print(f"- {error}")
            return 1

    summary = expected_conformance["summary"]
    print(
        "agent benchmark substrate: "
        f"{len(spec['conditions'])} cumulative conditions, {len(spec['cases'])} cases, "
        f"{summary['fixtures']} conformance fixtures pass expected outcomes; no agent runs claimed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
