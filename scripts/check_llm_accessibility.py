#!/usr/bin/env python3
"""Validate the generated LLM corpus, misconception registry, and eval set."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib
from collections import Counter, defaultdict
from pathlib import Path

from generate_llm_corpus import (
    CORPUS_MANIFEST,
    EXCLUDED_DOCS,
    EVALUATIONS,
    MISCONCEPTIONS,
    OUTPUT,
    RELEASE_MANIFEST,
    ROOT,
    SCHEMA_VERSION,
    rendered_payloads,
)

CLAIMS = ROOT / "claims/claims.toml"
VOCABULARY = ROOT / "vocabulary/vocabulary.toml"
CORPUS_SCHEMA = ROOT / "schemas/llm-corpus-record.schema.json"
EVAL_SCHEMA = ROOT / "schemas/llm-evaluation-case.schema.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
AUDIENCES = {"student", "software_engineer", "power_engineer"}
RECORD_TYPES = {"section", "claim_bundle", "concept_bundle", "scientific_knowledge"}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail_if(condition: bool, message: str, errors: list[str]) -> None:
    if condition:
        errors.append(message)


def load_records(errors: list[str]) -> list[dict]:
    records = []
    if not OUTPUT.is_file():
        errors.append("generated LLM corpus is missing")
        return records
    for line_number, line in enumerate(OUTPUT.read_text().splitlines(), start=1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"corpus line {line_number} is invalid JSON: {error}")
            continue
        if not isinstance(value, dict):
            errors.append(f"corpus line {line_number} is not an object")
            continue
        records.append(value)
    return records


def validate_common_record(record: dict, release: dict, errors: list[str]) -> None:
    record_id = record.get("record_id", "<missing>")
    for field in ("schema_version", "record_id", "record_type", "title", "text", "source", "release"):
        fail_if(field not in record, f"{record_id}: missing {field}", errors)
    fail_if(record.get("schema_version") != SCHEMA_VERSION, f"{record_id}: wrong schema version", errors)
    fail_if(record.get("record_type") not in RECORD_TYPES, f"{record_id}: unknown record type", errors)
    fail_if(not str(record.get("title", "")).strip(), f"{record_id}: empty title", errors)
    fail_if(not str(record.get("text", "")).strip(), f"{record_id}: empty retrieval text", errors)
    fail_if(record.get("release") != release, f"{record_id}: release identity drift", errors)

    source = record.get("source", {})
    path_string = source.get("path", "") if isinstance(source, dict) else ""
    source_path = ROOT / path_string
    fail_if(not source_path.is_file(), f"{record_id}: source path does not exist: {path_string}", errors)
    source_hash = source.get("sha256", "") if isinstance(source, dict) else ""
    fail_if(not SHA256.fullmatch(source_hash), f"{record_id}: invalid source hash", errors)
    if source_path.is_file() and SHA256.fullmatch(source_hash):
        fail_if(file_hash(source_path) != source_hash, f"{record_id}: stale source hash", errors)


def main() -> int:
    errors: list[str] = []
    try:
        claims = tomllib.loads(CLAIMS.read_text()).get("claim", [])
        concepts = tomllib.loads(VOCABULARY.read_text()).get("concept", [])
        misconceptions = tomllib.loads(MISCONCEPTIONS.read_text()).get("misconception", [])
        evaluations = tomllib.loads(EVALUATIONS.read_text()).get("case", [])
        heldout = tomllib.loads((ROOT / "llm/heldout-paraphrases.toml").read_text()).get("case", [])
        release_manifest = json.loads(RELEASE_MANIFEST.read_text())
        corpus_schema = json.loads(CORPUS_SCHEMA.read_text())
        eval_schema = json.loads(EVAL_SCHEMA.read_text())
        manifest = json.loads(CORPUS_MANIFEST.read_text()) if CORPUS_MANIFEST.is_file() else {}
        expected_corpus, expected_manifest = rendered_payloads()
    except (OSError, ValueError, KeyError, tomllib.TOMLDecodeError, json.JSONDecodeError) as error:
        print(f"LLM accessibility audit failed to load inputs: {error}")
        return 1

    fail_if(CORPUS_SCHEMA == EVAL_SCHEMA, "schema paths unexpectedly alias", errors)
    fail_if(corpus_schema.get("properties", {}).get("schema_version", {}).get("const") != SCHEMA_VERSION,
            "corpus JSON schema version drift", errors)
    fail_if(set(eval_schema.get("properties", {}).get("audience", {}).get("enum", [])) != AUDIENCES,
            "evaluation JSON schema audience vocabulary drift", errors)

    if OUTPUT.is_file():
        fail_if(OUTPUT.read_text() != expected_corpus, "generated corpus is stale", errors)
    else:
        errors.append("generated corpus is missing")
    if CORPUS_MANIFEST.is_file():
        fail_if(CORPUS_MANIFEST.read_text() != expected_manifest, "generated corpus manifest is stale", errors)
    else:
        errors.append("generated corpus manifest is missing")

    records = load_records(errors)
    record_ids = [record.get("record_id") for record in records]
    duplicates = sorted(record_id for record_id, count in Counter(record_ids).items() if count > 1)
    fail_if(bool(duplicates), f"duplicate corpus record IDs: {duplicates}", errors)

    release = manifest.get("release", {})
    expected_release_fields = {
        "release_candidate_id": release_manifest.get("release_candidate_id"),
        "status": release_manifest.get("status"),
        "external_reviewed_claims": release_manifest.get("external_reviewed_claims"),
        "independent_human_double_coding": release_manifest.get("independent_human_double_coding"),
    }
    fail_if(any(release.get(key) != value for key, value in expected_release_fields.items()),
            "corpus release identity does not match the release candidate", errors)
    fail_if(not SHA256.fullmatch(str(release.get("release_identity_sha256", ""))),
            "invalid release identity hash", errors)

    for record in records:
        validate_common_record(record, release, errors)

    claim_ids = {claim["claim_id"] for claim in claims}
    concept_ids = {concept["id"] for concept in concepts}
    claim_records = {
        record.get("claim", {}).get("claim_id"): record
        for record in records
        if record.get("record_type") == "claim_bundle"
    }
    concept_records = {
        record.get("concept", {}).get("id"): record
        for record in records
        if record.get("record_type") == "concept_bundle"
    }
    scientific_records = {
        record.get("knowledge_id"): record
        for record in records
        if record.get("record_type") == "scientific_knowledge"
    }
    fail_if(set(claim_records) != claim_ids,
            f"claim bundle coverage differs: missing={sorted(claim_ids - set(claim_records))}, extra={sorted(set(claim_records) - claim_ids)}",
            errors)
    fail_if(set(concept_records) != concept_ids,
            f"concept bundle coverage differs: missing={sorted(concept_ids - set(concept_records))}, extra={sorted(set(concept_records) - concept_ids)}",
            errors)
    scientific_manifest = json.loads((ROOT / "generated/scientific-knowledge-manifest.json").read_text())
    fail_if(set(scientific_records) != set(scientific_manifest.get("knowledge_ids", [])),
            "scientific-knowledge corpus coverage differs from its manifest", errors)
    for knowledge_id, record in scientific_records.items():
        fail_if(record.get("record_id") != f"knowledge:{knowledge_id}",
                f"{knowledge_id}: unstable corpus record ID", errors)
        fail_if(not record.get("misconception_ids"),
                f"{knowledge_id}: scientific record has no misconception route", errors)
        if record.get("kind") == "negative-result":
            fail_if(not record.get("negative_result"),
                    f"{knowledge_id}: negative-result record lacks its quality-standard fields", errors)
            fail_if(record.get("executable", {}).get("implementation_status") not in {"implemented", "not_applicable"},
                    f"{knowledge_id}: negative-result executable relationship is ambiguous", errors)
        else:
            fail_if("negative_result" in record,
                    f"{knowledge_id}: non-negative record carries negative-result fields", errors)
        if record.get("kind") == "numerical-pathology":
            fail_if(not record.get("numerical_pathology"),
                    f"{knowledge_id}: numerical-pathology record lacks its diagnostic fields", errors)
            fail_if(record.get("executable", {}).get("implementation_status") not in {"implemented", "not_applicable"},
                    f"{knowledge_id}: numerical-pathology executable relationship is ambiguous", errors)
        else:
            fail_if("numerical_pathology" in record,
                    f"{knowledge_id}: non-pathology record carries numerical-pathology fields", errors)
    for claim_id, record in claim_records.items():
        passage = record.get("supporting_passage", {})
        fail_if(not str(passage.get("text", "")).strip(), f"{claim_id}: empty supporting passage", errors)
        fail_if(passage.get("selection_method") not in {"claim_id_mention", "lexical_claim_coverage", "chapter_fallback"},
                f"{claim_id}: unknown supporting-passage selection method", errors)
        fail_if(record.get("claim") != next(item for item in claims if item["claim_id"] == claim_id),
                f"{claim_id}: claim bundle changed canonical claim fields", errors)

    misconception_ids = [item.get("id") for item in misconceptions]
    fail_if(len(misconception_ids) != len(set(misconception_ids)), "duplicate misconception IDs", errors)
    misconception_by_id = {item["id"]: item for item in misconceptions if item.get("id")}
    for item in misconceptions:
        item_id = item.get("id", "<missing>")
        for field in (
            "title", "severity", "query_patterns", "tempting_answer", "required_qualification",
            "safe_shorthand", "operational_consequence", "mandatory_claim_ids",
            "mandatory_concept_ids", "source_paths",
        ):
            fail_if(not item.get(field), f"{item_id}: missing or empty misconception field {field}", errors)
        fail_if(item.get("severity") not in {"medium", "high", "critical"},
                f"{item_id}: unknown severity", errors)
        unknown_claims = set(item.get("mandatory_claim_ids", [])) - claim_ids
        unknown_concepts = set(item.get("mandatory_concept_ids", [])) - concept_ids
        fail_if(bool(unknown_claims), f"{item_id}: unknown mandatory claims {sorted(unknown_claims)}", errors)
        fail_if(bool(unknown_concepts), f"{item_id}: unknown mandatory concepts {sorted(unknown_concepts)}", errors)
        for path in item.get("source_paths", []):
            fail_if(not (ROOT / path).is_file(), f"{item_id}: missing source path {path}", errors)
        for claim_id in item.get("mandatory_claim_ids", []):
            fail_if(item_id not in claim_records.get(claim_id, {}).get("misconception_ids", []),
                    f"{item_id}: not linked from mandatory claim {claim_id}", errors)
        for concept_id in item.get("mandatory_concept_ids", []):
            fail_if(item_id not in concept_records.get(concept_id, {}).get("misconception_ids", []),
                    f"{item_id}: not linked from mandatory concept {concept_id}", errors)

    case_ids = [case.get("case_id") for case in evaluations]
    fail_if(len(case_ids) != len(set(case_ids)), "duplicate evaluation case IDs", errors)
    cases_by_misconception: dict[str, list[dict]] = defaultdict(list)
    for case in evaluations:
        case_id = case.get("case_id", "<missing>")
        misconception_id = case.get("misconception_id")
        cases_by_misconception[misconception_id].append(case)
        fail_if(not re.fullmatch(r"EVAL-[A-Z0-9-]+", case_id), f"{case_id}: invalid case ID", errors)
        fail_if(case.get("audience") not in AUDIENCES, f"{case_id}: unknown audience", errors)
        fail_if(len(str(case.get("question", ""))) < 10, f"{case_id}: question is too short", errors)
        fail_if(misconception_id not in misconception_by_id, f"{case_id}: unknown misconception", errors)
        required_claims = set(case.get("required_claim_ids", []))
        required_concepts = set(case.get("required_concept_ids", []))
        fail_if(bool(required_claims - claim_ids), f"{case_id}: unknown required claims", errors)
        fail_if(bool(required_concepts - concept_ids), f"{case_id}: unknown required concepts", errors)
        fail_if(len(case.get("required_answer_elements", [])) < 2, f"{case_id}: too few answer elements", errors)
        fail_if(not case.get("forbidden_simplifications"), f"{case_id}: no forbidden simplification", errors)
        if misconception_id in misconception_by_id:
            misconception = misconception_by_id[misconception_id]
            fail_if(required_claims != set(misconception["mandatory_claim_ids"]),
                    f"{case_id}: required claims drift from misconception contract", errors)
            fail_if(required_concepts != set(misconception["mandatory_concept_ids"]),
                    f"{case_id}: required concepts drift from misconception contract", errors)

    for misconception_id in misconception_by_id:
        audiences = {case.get("audience") for case in cases_by_misconception.get(misconception_id, [])}
        fail_if(audiences != AUDIENCES,
                f"{misconception_id}: evaluation audiences differ: {sorted(audiences)}", errors)

    if OUTPUT.is_file():
        fail_if(manifest.get("corpus_sha256") != file_hash(OUTPUT), "corpus hash differs from manifest", errors)
    fail_if(manifest.get("record_count") != len(records), "corpus record count differs from manifest", errors)
    observed_counts = dict(sorted(Counter(record.get("record_type") for record in records).items()))
    fail_if(manifest.get("record_counts") != observed_counts, "record-type counts differ from manifest", errors)
    fail_if(manifest.get("misconception_count") != len(misconceptions), "misconception count differs from manifest", errors)
    fail_if(manifest.get("evaluation_case_count") != len(evaluations), "evaluation count differs from manifest", errors)
    fail_if(manifest.get("heldout_case_count") != len(heldout), "held-out evaluation count differs from manifest", errors)
    selection = manifest.get("document_selection", {})
    fail_if(selection.get("excluded_docs") != sorted(EXCLUDED_DOCS), "document exclusion rule differs from corpus manifest", errors)
    fail_if(selection.get("excluded_doc_count") != len(EXCLUDED_DOCS), "document exclusion count differs from corpus manifest", errors)
    fail_if(selection.get("included_doc_count") != len([path for path in (ROOT / "docs/src").rglob("*.md") if path.relative_to(ROOT).as_posix() not in EXCLUDED_DOCS]), "included document count differs from corpus manifest", errors)
    for source in manifest.get("source_files", []):
        path = ROOT / source.get("path", "")
        fail_if(not path.is_file(), f"manifest source missing: {source.get('path')}", errors)
        if path.is_file():
            fail_if(file_hash(path) != source.get("sha256"), f"manifest source hash stale: {source.get('path')}", errors)

    if errors:
        print("LLM accessibility audit failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    section_count = sum(record.get("record_type") == "section" for record in records)
    print(
        "LLM accessibility: "
        f"{len(records)} records: {section_count} sections, {len(claim_records)} claim bundles, "
        f"{len(concept_records)} concept bundles, {len(scientific_records)} scientific records, "
        f"{len(misconceptions)} misconception contracts, "
        f"and {len(evaluations)} evaluation cases pass"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
