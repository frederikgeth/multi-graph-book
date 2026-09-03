#!/usr/bin/env python3
"""Validate the controlled pilot design and its synthetic run-record dry run."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import check_agent_benchmark as benchmark

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "benchmarks/agent/pilot/parallel-member-limits-pilot-v1.json"
PILOT_SCHEMA = ROOT / "schemas/agent-benchmark-pilot.schema.json"
RUN_SCHEMA = ROOT / "schemas/agent-benchmark-run.schema.json"
BENCHMARK_MANIFEST = ROOT / "benchmarks/agent/generated/benchmark-manifest.json"
OUTPUT_DIR = ROOT / "benchmarks/agent/generated"
DESIGN_MANIFEST = OUTPUT_DIR / "pilot-design-manifest.json"
DRY_RUN_REPORT = OUTPUT_DIR / "pilot-dry-run-evaluation.json"

SCHEMA_VERSION = "0.1.0"
PILOT_ID = re.compile(r"^APILOT-[A-Z0-9-]+$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ACTIVE_CONDITIONS = [
    "C0_MODEL_ONLY",
    "C1_REPOSITORY_DOCS",
    "C5_EXECUTABLE_CONTRACTS",
    "C6_NEGATIVE_KNOWLEDGE",
]
EXPECTED_RESEARCH_QUESTION = (
    "Within one fixed agent system, how reliably does the agent locate and correctly apply "
    "the resources supplied by four cumulative bundles when producing qualified rejection "
    "and abstention on the transparent PSK-000001 slice?"
)
PRIVATE_ORACLE_SOURCES = {
    ("BMOPFTools.jl", "test/fixtures/negative/parallel-rating-outer-relaxation/expected.json"),
    ("multi-graph-book", "llm/evaluation-cases.toml"),
}
LOCAL_SOURCES = (
    Path("benchmarks/agent/README.md"),
    Path("benchmarks/agent/pilot/parallel-member-limits-pilot-v1.json"),
    Path("schemas/agent-benchmark-pilot.schema.json"),
    Path("schemas/agent-benchmark-run.schema.json"),
    Path("scripts/check_agent_benchmark_pilot.py"),
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


def require_nonempty_string(value: object, label: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a nonempty string")
        return ""
    return value


def source_identity(item: dict) -> tuple[str, str] | None:
    repository = item.get("repository")
    path = item.get("path")
    if repository in {"multi-graph-book", "BMOPFTools.jl"} and isinstance(path, str) and path:
        return repository, path
    return None


def tool_source_identity(source: object) -> tuple[str, str] | None:
    if not isinstance(source, str) or "/" not in source:
        return None
    repository, path = source.split("/", 1)
    if repository not in {"multi-graph-book", "BMOPFTools.jl"} or not path:
        return None
    return repository, path


def validate_design(plan: dict, spec: dict, errors: list[str]) -> None:
    required = {
        "schema_version", "pilot_id", "benchmark_id", "status", "research_question",
        "active_conditions", "design", "system_slots", "sampling_settings", "budgets",
        "resource_bundles", "exclusion_rules", "aggregation", "human_review_gate",
        "dry_run_records", "limitations",
    }
    add_if(set(plan) != required,
           f"pilot fields differ: missing={sorted(required - set(plan))}, extra={sorted(set(plan) - required)}",
           errors)
    add_if(plan.get("schema_version") != SCHEMA_VERSION, "pilot schema version drift", errors)
    pilot_id = plan.get("pilot_id", "")
    add_if(not isinstance(pilot_id, str) or not PILOT_ID.fullmatch(pilot_id),
           f"invalid pilot ID: {pilot_id}", errors)
    add_if(plan.get("benchmark_id") != spec.get("benchmark_id"), "pilot benchmark ID mismatch", errors)
    add_if(plan.get("status") != "design_complete_execution_not_authorized",
           "pilot must remain design_complete_execution_not_authorized until the human gate is passed", errors)
    add_if(plan.get("research_question") != EXPECTED_RESEARCH_QUESTION,
           "pilot research question must measure locating and applying supplied resources", errors)
    add_if(plan.get("active_conditions") != ACTIVE_CONDITIONS,
           f"initial pilot conditions must be {ACTIVE_CONDITIONS}", errors)
    add_if(not set(ACTIVE_CONDITIONS) <= set(spec.get("condition_order", [])),
           "pilot condition is absent from the benchmark lattice", errors)

    design = plan.get("design", {})
    if not isinstance(design, dict):
        errors.append("design must be an object")
        design = {}
    repetitions = design.get("repetitions_per_condition_per_system")
    add_if(repetitions != 4, "first pilot must freeze four repetitions per condition", errors)
    add_if(design.get("total_runs_per_system") != len(ACTIVE_CONDITIONS) * 4,
           "total_runs_per_system must match conditions times repetitions", errors)
    sequences = design.get("condition_sequences", [])
    add_if(not isinstance(sequences, list) or len(sequences) != 4,
           "condition_sequences must contain the four balanced rotations", errors)
    if isinstance(sequences, list):
        add_if(any(sorted(sequence) != sorted(ACTIVE_CONDITIONS) for sequence in sequences
                   if isinstance(sequence, list)),
               "every condition sequence must contain each active condition exactly once", errors)
        positions = [
            [sequence[position] for sequence in sequences]
            for position in range(4)
            if all(isinstance(sequence, list) and len(sequence) == 4 for sequence in sequences)
        ]
        add_if(any(sorted(column) != sorted(ACTIVE_CONDITIONS) for column in positions),
               "condition sequences must balance every condition across ordinal positions", errors)
    for field in ("experimental_unit", "conversation_reset", "case_order_rule", "prompt_policy",
                  "write_policy", "capture_policy"):
        require_nonempty_string(design.get(field), f"design.{field}", errors)

    slots = plan.get("system_slots", [])
    add_if(not isinstance(slots, list) or not slots, "system_slots must be nonempty", errors)
    if isinstance(slots, list):
        for slot in slots:
            if not isinstance(slot, dict):
                errors.append("system slot must be an object")
                continue
            add_if(slot.get("selection_status") != "pending_human_selection",
                   f"{slot.get('slot_id')}: system selection must remain pending", errors)
            add_if(any(slot.get(field) is not None for field in
                       ("provider", "model_id", "model_revision", "execution_interface")),
                   f"{slot.get('slot_id')}: unreviewed system fields must remain null", errors)

    settings = plan.get("sampling_settings", {})
    add_if(not isinstance(settings, dict)
           or settings.get("status") != "pending_exact_provider_settings",
           "sampling settings must remain pending exact provider settings", errors)
    if isinstance(settings, dict):
        add_if(any(settings.get(field) is not None for field in
                   ("temperature", "top_p", "seed", "reasoning_effort")),
               "unreviewed provider-dependent settings must remain null", errors)
        add_if(settings.get("max_output_tokens") != 4000,
               "pilot output-token budget drift", errors)

    budgets = plan.get("budgets", {})
    expected_budgets = {
        "wall_time_seconds_per_run": 600,
        "tool_calls_per_run": 20,
        "max_output_tokens_per_run": 4000,
    }
    add_if(budgets != expected_budgets, "pilot budgets differ from the frozen draft", errors)

    bundles = plan.get("resource_bundles", [])
    if not isinstance(bundles, list):
        errors.append("resource_bundles must be an array")
        bundles = []
    bundle_by_condition = {
        item.get("condition_id"): item for item in bundles if isinstance(item, dict)
    }
    add_if(len(bundle_by_condition) != len(bundles),
           "resource bundle condition IDs must be unique", errors)
    add_if(list(bundle_by_condition) != ACTIVE_CONDITIONS,
           "resource bundles must follow the active condition order", errors)
    add_if(bundle_by_condition.get("C0_MODEL_ONLY", {}).get("exposed_sources") != [],
           "C0 must not expose repository sources", errors)
    add_if(bundle_by_condition.get("C0_MODEL_ONLY", {}).get("allowed_tools") != [],
           "C0 must not expose tools", errors)
    add_if(bundle_by_condition.get("C5_EXECUTABLE_CONTRACTS", {}).get("inherits") != "BUNDLE-C1",
           "C5 must inherit the C1 documentation bundle", errors)
    add_if(bundle_by_condition.get("C6_NEGATIVE_KNOWLEDGE", {}).get("inherits") != "BUNDLE-C5",
           "C6 must inherit the C5 executable bundle", errors)
    required_capabilities = {
        "C1_REPOSITORY_DOCS": {"repository_documentation"},
        "C5_EXECUTABLE_CONTRACTS": {
            "scientific_knowledge_export", "agent_workflow_guidance", "execution_tools",
            "executable_contract_and_recipe",
        },
        "C6_NEGATIVE_KNOWLEDGE": {"misconception_and_counterexample_retrieval"},
    }
    for condition, required_capability_set in required_capabilities.items():
        bundle = bundle_by_condition.get(condition, {})
        sources = bundle.get("exposed_sources", [])
        tools = bundle.get("allowed_tools", [])
        if not isinstance(sources, list) or not isinstance(tools, list):
            errors.append(f"{condition}: exposed_sources and allowed_tools must be arrays")
            continue
        capabilities = {
            item.get("capability") for item in sources + tools if isinstance(item, dict)
        }
        add_if(not required_capability_set <= capabilities,
               f"{condition}: missing capabilities {sorted(required_capability_set - capabilities)}", errors)
        for item in sources:
            if not isinstance(item, dict) or source_identity(item) is None:
                errors.append(f"{condition}: malformed source record")
                continue
            add_if(source_identity(item) in PRIVATE_ORACLE_SOURCES,
                   f"{condition}: harness-private oracle or evaluation rubric is exposed: "
                   f"{source_identity(item)}", errors)
        for tool in tools:
            if not isinstance(tool, dict) or tool_source_identity(tool.get("source")) is None:
                errors.append(f"{condition}: malformed tool source")

    exclusions = plan.get("exclusion_rules", {})
    allowed_reasons = exclusions.get("allowed_reason_codes", []) if isinstance(exclusions, dict) else []
    add_if(not isinstance(allowed_reasons, list) or not allowed_reasons,
           "exclusion rules must declare reason codes", errors)
    never_exclude = exclusions.get("never_exclude_for", []) if isinstance(exclusions, dict) else []
    add_if("wrong scientific answer" not in never_exclude,
           "wrong scientific answers must never be excluded", errors)
    aggregation = plan.get("aggregation", {})
    add_if(not isinstance(aggregation, dict) or aggregation.get("missing_data") != "no imputation",
           "aggregation must prohibit imputation", errors)
    add_if(not isinstance(aggregation, dict) or aggregation.get("top_line_accuracy") != "not reported",
           "pilot must not collapse results to top-line accuracy", errors)
    effect_language = aggregation.get("condition_effect_language", "") if isinstance(aggregation, dict) else ""
    add_if(not all(fragment in effect_language for fragment in (
        "locating and applying supplied resources", "cannot attribute effects",
        "seven-condition ladder")),
        "condition-effect language must preserve the supplied-resource and bundled-ladder boundary",
        errors)

    gate = plan.get("human_review_gate", {})
    add_if(not isinstance(gate, dict)
           or gate.get("status") != "reviewed_changes_required_before_preregistration_or_execution",
           "human review must record changes required before preregistration or execution", errors)
    latest_review = gate.get("latest_review", {}) if isinstance(gate, dict) else {}
    add_if(not isinstance(latest_review, dict)
           or latest_review.get("outcome") != "changes_required"
           or latest_review.get("correction_status") != "applied_pending_re_review",
           "latest human review must remain changes-required and pending re-review", errors)
    add_if(not isinstance(latest_review.get("findings"), list)
           or len(latest_review.get("findings", [])) < 4,
           "latest human review must retain its four corrective findings", errors)
    prohibited = gate.get("prohibited_before_gate", []) if isinstance(gate, dict) else []
    add_if("execute a hosted model" not in prohibited or "commit measured_run records" not in prohibited,
           "human gate must prohibit real execution and measured records", errors)
    add_if(not isinstance(plan.get("limitations"), list) or not plan.get("limitations"),
           "pilot limitations must be nonempty", errors)
    limitations = " ".join(plan.get("limitations", []))
    add_if("does not test or attribute effects across the complete seven-condition ladder" not in limitations,
           "pilot limitations must state that the seven-condition ladder is not tested", errors)


def collect_source_paths(plan: dict, errors: list[str]) -> dict[str, list[str]]:
    paths: dict[str, list[str]] = {"multi-graph-book": [], "BMOPFTools.jl": []}
    for bundle in plan.get("resource_bundles", []):
        if not isinstance(bundle, dict):
            continue
        for item in bundle.get("exposed_sources", []):
            identity = source_identity(item) if isinstance(item, dict) else None
            if identity is None:
                continue
            repository, path = identity
            if path not in paths[repository]:
                paths[repository].append(path)
        for tool in bundle.get("allowed_tools", []):
            identity = tool_source_identity(tool.get("source")) if isinstance(tool, dict) else None
            if identity is None:
                continue
            repository, path = identity
            if path not in paths[repository]:
                paths[repository].append(path)
    if not paths["multi-graph-book"] or not paths["BMOPFTools.jl"]:
        errors.append("pilot must bind sources from both repositories")
    return paths


def source_records(base: Path, paths: list[str], errors: list[str]) -> list[dict]:
    records: list[dict] = []
    for path_string in paths:
        path = base / path_string
        if not path.is_file():
            errors.append(f"missing source file: {path}")
            continue
        records.append({"path": path_string, "sha256": sha256(path)})
    return records


def validate_run_record(record: dict, plan: dict, spec: dict, provenance: dict,
                        errors: list[str]) -> dict | None:
    required = {
        "schema_version", "record_kind", "pilot_id", "benchmark_id", "run_id",
        "execution_status", "condition_id", "repetition_index", "condition_sequence_index",
        "case_order", "system", "settings", "budgets", "exposure", "timing",
        "provenance", "submission", "exclusion",
    }
    run_id = record.get("run_id", "<missing>")
    add_if(set(record) != required,
           f"{run_id}: run fields differ: missing={sorted(required - set(record))}, extra={sorted(set(record) - required)}",
           errors)
    add_if(record.get("schema_version") != SCHEMA_VERSION, f"{run_id}: schema version drift", errors)
    add_if(record.get("record_kind") != "synthetic_dry_run",
           f"{run_id}: committed dry-run fixture must be synthetic_dry_run", errors)
    add_if(record.get("pilot_id") != plan.get("pilot_id"), f"{run_id}: pilot ID mismatch", errors)
    add_if(record.get("benchmark_id") != spec.get("benchmark_id"), f"{run_id}: benchmark ID mismatch", errors)
    condition_id = record.get("condition_id")
    add_if(condition_id not in ACTIVE_CONDITIONS, f"{run_id}: inactive condition", errors)
    repetition = record.get("repetition_index")
    add_if(not isinstance(repetition, int) or not 1 <= repetition <= 4,
           f"{run_id}: repetition index outside pilot design", errors)
    expected_case_order = ["ABENCH-PAR-001-UNSAFE", "ABENCH-PAR-002-BOUNDARY"]
    if isinstance(repetition, int) and repetition % 2 == 0:
        expected_case_order.reverse()
    add_if(record.get("case_order") != expected_case_order, f"{run_id}: case order rule drift", errors)
    sequence_index = record.get("condition_sequence_index")
    sequences = plan.get("design", {}).get("condition_sequences", [])
    expected_sequence_index = None
    if isinstance(repetition, int) and 1 <= repetition <= len(sequences) and condition_id in ACTIVE_CONDITIONS:
        expected_sequence_index = sequences[repetition - 1].index(condition_id)
    add_if(sequence_index != expected_sequence_index,
           f"{run_id}: condition sequence position drift", errors)
    expected_bundle = {
        "C0_MODEL_ONLY": "BUNDLE-C0",
        "C1_REPOSITORY_DOCS": "BUNDLE-C1",
        "C5_EXECUTABLE_CONTRACTS": "BUNDLE-C5",
        "C6_NEGATIVE_KNOWLEDGE": "BUNDLE-C6",
    }.get(condition_id)
    add_if(record.get("exposure", {}).get("bundle_id") != expected_bundle,
           f"{run_id}: resource bundle mismatch", errors)
    system = record.get("system", {})
    for field in ("provider", "model_id", "model_revision"):
        require_nonempty_string(system.get(field) if isinstance(system, dict) else None,
                                f"{run_id}.system.{field}", errors)
    for field in ("settings", "budgets", "exposure", "timing", "provenance"):
        add_if(not isinstance(record.get(field), dict), f"{run_id}.{field} must be an object", errors)
    settings = record.get("settings", {})
    add_if(isinstance(settings, dict) and settings.get("max_output_tokens") != 4000,
           f"{run_id}: output setting differs from pilot budget", errors)
    budgets = record.get("budgets", {})
    expected_tool_calls = 0 if condition_id in {"C0_MODEL_ONLY", "C1_REPOSITORY_DOCS"} else 20
    expected_run_budgets = {
        "wall_time_seconds": 600,
        "tool_calls": expected_tool_calls,
        "max_output_tokens": 4000,
    }
    add_if(isinstance(budgets, dict) and budgets != expected_run_budgets,
           f"{run_id}: run budgets differ from the condition design", errors)

    exclusion = record.get("exclusion", {})
    if not isinstance(exclusion, dict):
        errors.append(f"{run_id}: exclusion must be an object")
        return None
    add_if(set(exclusion) != {"included", "reason_code", "detail"},
           f"{run_id}: exclusion fields differ", errors)
    included = exclusion.get("included")
    submission_record = record.get("submission")
    allowed_reasons = set(plan.get("exclusion_rules", {}).get("allowed_reason_codes", []))
    if included:
        add_if(record.get("execution_status") != "completed",
               f"{run_id}: included run must be completed", errors)
        add_if(exclusion.get("reason_code") is not None or exclusion.get("detail") is not None,
               f"{run_id}: included run cannot have an exclusion reason", errors)
        if not isinstance(submission_record, dict):
            errors.append(f"{run_id}: included run must name a submission")
            return None
        submission_path = ROOT / str(submission_record.get("path", ""))
        if not submission_path.is_file():
            errors.append(f"{run_id}: missing submission {submission_record.get('path')}")
            return None
        add_if(submission_record.get("sha256") != sha256(submission_path),
               f"{run_id}: submission hash mismatch", errors)
        add_if(not SHA256.fullmatch(str(submission_record.get("sha256", ""))),
               f"{run_id}: malformed submission hash", errors)
        submission = load_json(submission_path)
        add_if(submission.get("condition_id") != condition_id,
               f"{run_id}: submission condition mismatch", errors)
        add_if(submission.get("system") != system, f"{run_id}: submission system mismatch", errors)
        return benchmark.score_submission(submission, spec, provenance)
    add_if(submission_record is not None, f"{run_id}: excluded pre-response run must not name a submission", errors)
    add_if(exclusion.get("reason_code") not in allowed_reasons,
           f"{run_id}: unknown exclusion reason", errors)
    require_nonempty_string(exclusion.get("detail"), f"{run_id}.exclusion.detail", errors)
    return None


def aggregate_dry_runs(records: list[dict], reports: dict[str, dict]) -> dict:
    condition_summary: dict[str, dict] = {
        condition: {
            "records": 0,
            "eligible_runs": 0,
            "excluded_runs": 0,
            "overall_passed": 0,
            "dimension_counts": {},
        }
        for condition in ACTIVE_CONDITIONS
    }
    dimension_values: dict[str, dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))
    exclusions: list[dict] = []
    for record in records:
        condition = record["condition_id"]
        summary = condition_summary[condition]
        summary["records"] += 1
        if not record["exclusion"]["included"]:
            summary["excluded_runs"] += 1
            exclusions.append({
                "run_id": record["run_id"],
                "condition_id": condition,
                "reason_code": record["exclusion"]["reason_code"],
            })
            continue
        summary["eligible_runs"] += 1
        report = reports.get(record["run_id"])
        if report is None:
            continue
        summary["overall_passed"] += int(report["pass"])
        for case in report["cases"]:
            for dimension, value in case["scores"].items():
                if value is not None:
                    dimension_values[condition][dimension].append(value)
    for condition, by_dimension in dimension_values.items():
        condition_summary[condition]["dimension_counts"] = {
            dimension: {
                "scored": len(values),
                "passed": sum(value is True for value in values),
                "failed": sum(value is False for value in values),
            }
            for dimension, values in sorted(by_dimension.items())
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "pilot_id": "APILOT-PARALLEL-LIMITS-001",
        "status": "synthetic_dry_run_harness_only_not_agent_results",
        "summary": {
            "records": len(records),
            "eligible_runs": sum(item["eligible_runs"] for item in condition_summary.values()),
            "excluded_runs": sum(item["excluded_runs"] for item in condition_summary.values()),
            "conditions": condition_summary,
        },
        "exclusions": exclusions,
        "does_not_establish": [
            "Any model or hosted agent was executed.",
            "Any condition changes agent performance.",
            "The pending system and provider settings are suitable for a real pilot.",
        ],
    }


def expected_outputs(plan: dict, spec: dict, pair: dict, corpus: dict,
                     bmopf_root: Path | None, recorded_manifest: dict | None,
                     errors: list[str]) -> tuple[dict, dict]:
    sources = collect_source_paths(plan, errors)
    book_records = source_records(ROOT, sources["multi-graph-book"], errors)
    if bmopf_root is not None:
        bmopf_records = source_records(bmopf_root, sources["BMOPFTools.jl"], errors)
    elif recorded_manifest is not None:
        bmopf_records = recorded_manifest.get("resource_sources", {}).get("BMOPFTools.jl", [])
        recorded_paths = [item.get("path") for item in bmopf_records if isinstance(item, dict)]
        add_if(recorded_paths != sources["BMOPFTools.jl"],
               "recorded BMOPFTools pilot source list differs from the design", errors)
        add_if(any(not isinstance(item, dict) or not SHA256.fullmatch(str(item.get("sha256", "")))
                   for item in bmopf_records),
               "recorded BMOPFTools pilot source hashes are malformed", errors)
    else:
        errors.append("--write requires --bmopf-root for source-bound BMOPFTools resources")
        bmopf_records = []

    dry_paths = plan.get("dry_run_records", [])
    records: list[dict] = []
    reports: dict[str, dict] = {}
    seen_run_ids: set[str] = set()
    provenance = benchmark.current_provenance(pair, corpus)
    for path_string in dry_paths:
        path = ROOT / path_string
        if not path.is_file():
            errors.append(f"missing dry-run record: {path_string}")
            continue
        record = load_json(path)
        run_id = str(record.get("run_id", ""))
        add_if(run_id in seen_run_ids, f"duplicate dry-run ID: {run_id}", errors)
        seen_run_ids.add(run_id)
        report = validate_run_record(record, plan, spec, provenance, errors)
        records.append(record)
        if report is not None:
            reports[run_id] = report

    add_if(any(path.is_file() for path in (ROOT / "benchmarks/agent/runs").glob("*.json")),
           "measured run records exist before the human review gate", errors)
    dry_report = aggregate_dry_runs(records, reports)
    local_paths = [path.as_posix() for path in LOCAL_SOURCES] + list(dry_paths)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "pilot_id": plan.get("pilot_id"),
        "benchmark_id": plan.get("benchmark_id"),
        "status": plan.get("status"),
        "human_review_gate": plan.get("human_review_gate", {}).get("status"),
        "provenance": provenance,
        "pilot_schema_sha256": sha256(PILOT_SCHEMA),
        "run_schema_sha256": sha256(RUN_SCHEMA),
        "benchmark_manifest_sha256": sha256(BENCHMARK_MANIFEST),
        "local_sources": source_records(ROOT, local_paths, errors),
        "resource_sources": {
            "multi-graph-book": book_records,
            "BMOPFTools.jl": bmopf_records,
        },
        "dry_run_status": dry_report["status"],
    }
    return manifest, dry_report


def dump(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def refresh_synthetic_submission_hashes(plan: dict) -> None:
    """Repin dry-run envelopes after deterministic conformance fixtures move."""
    for path_string in plan.get("dry_run_records", []):
        path = ROOT / path_string
        record = load_json(path)
        if record.get("record_kind") != "synthetic_dry_run":
            raise ValueError(f"refusing to rewrite non-synthetic run record: {path.relative_to(ROOT)}")
        submission = record.get("submission")
        if not isinstance(submission, dict):
            continue
        submission_path = ROOT / submission.get("path", "")
        if not submission_path.is_file():
            raise ValueError(f"missing dry-run submission: {submission.get('path')}")
        submission["sha256"] = sha256(submission_path)
        path.write_text(dump(record))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="write generated pilot design artifacts")
    mode.add_argument("--check", action="store_true", help="check committed artifacts (default)")
    parser.add_argument("--bmopf-root", type=Path, help="live BMOPFTools sibling checkout")
    args = parser.parse_args()
    errors: list[str] = []
    try:
        plan = load_json(PILOT)
        spec = load_json(benchmark.BENCHMARK)
        pair = load_json(benchmark.PAIR)
        corpus = load_json(benchmark.CORPUS_MANIFEST)
        pilot_schema = load_json(PILOT_SCHEMA)
        run_schema = load_json(RUN_SCHEMA)
        recorded_manifest = load_json(DESIGN_MANIFEST) if DESIGN_MANIFEST.is_file() else None
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"agent benchmark pilot check failed to load inputs: {error}")
        return 1

    validate_design(plan, spec, errors)
    for label, schema in (("pilot", pilot_schema), ("run", run_schema)):
        add_if(schema.get("properties", {}).get("schema_version", {}).get("const") != SCHEMA_VERSION,
               f"{label} JSON schema version drift", errors)
    if args.write:
        try:
            refresh_synthetic_submission_hashes(plan)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"agent benchmark pilot check failed to repin synthetic dry-run fixture: {error}")
            return 1
    bmopf_root = args.bmopf_root.resolve() if args.bmopf_root else None
    expected_manifest, expected_report = expected_outputs(
        plan, spec, pair, corpus, bmopf_root, recorded_manifest, errors
    )

    if errors:
        print("agent benchmark pilot check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    if args.write:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        DESIGN_MANIFEST.write_text(dump(expected_manifest))
        DRY_RUN_REPORT.write_text(dump(expected_report))
        print(f"wrote {DESIGN_MANIFEST.relative_to(ROOT)} and {DRY_RUN_REPORT.relative_to(ROOT)}")
    else:
        if not DESIGN_MANIFEST.is_file() or DESIGN_MANIFEST.read_text() != dump(expected_manifest):
            errors.append("pilot design manifest is missing or stale")
        if not DRY_RUN_REPORT.is_file() or DRY_RUN_REPORT.read_text() != dump(expected_report):
            errors.append("pilot dry-run evaluation is missing or stale")
        if errors:
            print("agent benchmark pilot check failed:")
            for error in errors:
                print(f"- {error}")
            return 1
    print(
        "agent benchmark pilot design: 4 conditions, 16 planned runs per selected system, "
        "synthetic dry-run harness valid; corrections applied and human re-review required "
        "before real execution"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
