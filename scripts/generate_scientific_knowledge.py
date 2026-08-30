#!/usr/bin/env python3
"""Generate and validate stable cross-repository scientific-knowledge records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "knowledge/psk.toml"
CLAIMS = ROOT / "claims/claims.toml"
MISCONCEPTIONS = ROOT / "llm/misconceptions.toml"
SCHEMA = ROOT / "schemas/power-system-knowledge.schema.json"
RELEASE_MANIFEST = ROOT / "review/release-candidate-manifest.json"
OUTPUT = ROOT / "generated/scientific_knowledge.jsonl"
MANIFEST = ROOT / "generated/scientific-knowledge-manifest.json"
SCHEMA_VERSION = "0.1.0"
PSK_ID = re.compile(r"^PSK-[0-9]{6}$")
FINDING_CODE = re.compile(r"^[EWI]\.[A-Z0-9_]+(?:\.[A-Z0-9_]+)+$")
CONTRACT_ID = re.compile(r"^[a-z][a-z0-9_]*$")
KINDS = {
    "misconception",
    "modelling-antipattern",
    "counterexample",
    "negative-result",
    "failure-mode",
    "invalid-inference",
    "numerical-pathology",
    "software-antipattern",
    "scope-boundary",
    "open-question",
}
EVIDENCE_STATUSES = {
    "definition",
    "established_result",
    "empirical_result",
    "engineering_practice",
    "hypothesis",
    "conjecture",
    "open_question",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def release_identity() -> dict:
    manifest = json.loads(RELEASE_MANIFEST.read_text())
    identity = {
        "release_candidate_id": manifest["release_candidate_id"],
        "status": manifest["status"],
        "external_reviewed_claims": manifest["external_reviewed_claims"],
        "independent_human_double_coding": manifest["independent_human_double_coding"],
    }
    identity["release_identity_sha256"] = sha256_bytes(canonical_json(identity).encode())
    return identity


def require_unique_strings(
    record_id: str,
    field: str,
    values: object,
    errors: list[str],
    *,
    allow_empty: bool = False,
) -> list[str]:
    if (
        not isinstance(values, list)
        or (not values and not allow_empty)
        or not all(isinstance(item, str) and item.strip() for item in values)
    ):
        qualifier = "a string array" if allow_empty else "a nonempty string array"
        errors.append(f"{record_id}: {field} must be {qualifier}")
        return []
    if len(values) != len(set(values)):
        errors.append(f"{record_id}: {field} contains duplicates")
    return values


def knowledge_text(item: dict) -> str:
    book = item["book"]
    executable = item["executable"]
    lines = [
        f"Knowledge object {item['id']}: {item['title']}",
        f"Kind: {item['kind']}; evidence status: {item['evidence_status']}.",
        f"Scientific statement: {item['scientific_statement']}",
        f"Scope: {item['scope']}",
        "Does not establish: " + " ".join(item["does_not_establish"]),
        "Book claims: " + ", ".join(book["claim_ids"]) + ".",
        "Book misconceptions: " + ", ".join(book["misconception_ids"]) + ".",
        "Executable contracts: " + (", ".join(executable["contract_ids"]) or "none") + ".",
        "Executable status: " + executable["implementation_status"] + ".",
    ]
    negative_result = item.get("negative_result")
    if negative_result:
        lines.extend([
            "Negative-result question: " + negative_result["question"],
            "Hypothesis tested: " + negative_result["hypothesis"],
            "Observed result: " + negative_result["observed_result"],
            "Failure criterion: " + negative_result["failure_criterion"],
            "Interpretation: " + negative_result["interpretation"],
            "Conditions that may change the result: " + " ".join(negative_result["conditions_might_work"]),
        ])
    numerical_pathology = item.get("numerical_pathology")
    if numerical_pathology:
        lines.extend([
            "Numerical pathology: " + numerical_pathology["phenomenon"],
            "Observed behavior: " + numerical_pathology["observed_behavior"],
            "Algorithmic boundary: " + numerical_pathology["algorithmic_boundary"],
            "Invalid inferences: " + " ".join(numerical_pathology["invalid_inferences"]),
            "Discriminating checks: " + " ".join(numerical_pathology["discriminating_checks"]),
            "Conditions that may change the behavior: " + " ".join(numerical_pathology["conditions_might_change"]),
        ])
    return "\n".join(lines)


def validate_and_build() -> tuple[list[dict], dict, list[str]]:
    errors: list[str] = []
    registry = tomllib.loads(REGISTRY.read_text())
    claims = tomllib.loads(CLAIMS.read_text()).get("claim", [])
    misconceptions = tomllib.loads(MISCONCEPTIONS.read_text()).get("misconception", [])
    schema = json.loads(SCHEMA.read_text())
    if registry.get("schema_version") != SCHEMA_VERSION:
        errors.append("unexpected PSK registry schema version")
    schema_const = schema.get("properties", {}).get("schema_version", {}).get("const")
    if schema_const != SCHEMA_VERSION:
        errors.append("PSK JSON schema version differs from the registry generator")

    claim_ids = {item["claim_id"] for item in claims}
    misconception_ids = {item["id"] for item in misconceptions}
    records: list[dict] = []
    knowledge = registry.get("knowledge", [])
    ids = [item.get("id") for item in knowledge]
    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"duplicate PSK IDs: {duplicates}")

    for item in knowledge:
        record_id = item.get("id", "<missing>")
        if not isinstance(record_id, str) or not PSK_ID.fullmatch(record_id):
            errors.append(f"invalid PSK ID: {record_id}")
            continue
        for field in ("title", "scientific_statement", "scope"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{record_id}: missing or empty {field}")
        if item.get("kind") not in KINDS:
            errors.append(f"{record_id}: unknown knowledge kind {item.get('kind')}")
        if item.get("evidence_status") not in EVIDENCE_STATUSES:
            errors.append(f"{record_id}: unknown evidence status {item.get('evidence_status')}")
        require_unique_strings(record_id, "does_not_establish", item.get("does_not_establish"), errors)

        book = item.get("book", {})
        executable = item.get("executable", {})
        referenced_claims = set(require_unique_strings(record_id, "book.claim_ids", book.get("claim_ids"), errors))
        referenced_misconceptions = set(
            require_unique_strings(record_id, "book.misconception_ids", book.get("misconception_ids"), errors)
        )
        certificate_ids = require_unique_strings(
            record_id,
            "book.certificate_ids",
            book.get("certificate_ids"),
            errors,
            allow_empty=True,
        )
        require_unique_strings(
            record_id,
            "book.counterexample_ids",
            book.get("counterexample_ids"),
            errors,
            allow_empty=True,
        )
        artifact_paths = require_unique_strings(record_id, "book.artifact_paths", book.get("artifact_paths"), errors)
        source_paths = require_unique_strings(record_id, "book.source_paths", book.get("source_paths"), errors)
        unknown_claims = sorted(referenced_claims - claim_ids)
        unknown_misconceptions = sorted(referenced_misconceptions - misconception_ids)
        if unknown_claims:
            errors.append(f"{record_id}: unknown claim IDs {unknown_claims}")
        if unknown_misconceptions:
            errors.append(f"{record_id}: unknown misconception IDs {unknown_misconceptions}")

        observed_certificate_ids: set[str] = set()
        for path_string in artifact_paths:
            path = ROOT / path_string
            if not path.is_file():
                errors.append(f"{record_id}: missing artifact {path_string}")
                continue
            try:
                artifact = json.loads(path.read_text())
            except json.JSONDecodeError as error:
                errors.append(f"{record_id}: invalid JSON artifact {path_string}: {error}")
                continue
            certificate_id = artifact.get("certificate_id")
            if isinstance(certificate_id, str):
                observed_certificate_ids.add(certificate_id)
        if set(certificate_ids) != observed_certificate_ids:
            errors.append(
                f"{record_id}: certificate IDs differ from referenced artifacts: "
                f"declared={sorted(certificate_ids)}, observed={sorted(observed_certificate_ids)}"
            )
        for path_string in source_paths:
            if not (ROOT / path_string).is_file():
                errors.append(f"{record_id}: missing scientific source {path_string}")

        implementation_status = executable.get("implementation_status")
        if implementation_status not in {"planned", "partial", "implemented", "not_applicable"}:
            errors.append(f"{record_id}: invalid implementation status")
        book_only = implementation_status == "not_applicable"
        if book_only:
            if "repository" in executable:
                errors.append(f"{record_id}: book-only negative knowledge must not name an executable repository")
        elif executable.get("repository") != "frederikgeth/BMOPFTools.jl":
            errors.append(f"{record_id}: unexpected executable repository")
        contract_ids = require_unique_strings(
            record_id,
            "executable.contract_ids",
            executable.get("contract_ids"),
            errors,
            allow_empty=book_only,
        )
        finding_codes = require_unique_strings(
            record_id,
            "executable.finding_codes",
            executable.get("finding_codes"),
            errors,
            allow_empty=book_only,
        )
        related_codes = require_unique_strings(
            record_id,
            "executable.related_finding_codes",
            executable.get("related_finding_codes"),
            errors,
            allow_empty=book_only,
        )
        fixture_ids = require_unique_strings(
            record_id,
            "executable.fixture_ids",
            executable.get("fixture_ids"),
            errors,
            allow_empty=book_only,
        )
        if book_only and any((contract_ids, finding_codes, related_codes, fixture_ids)):
            errors.append(f"{record_id}: not_applicable executable metadata must have empty link arrays")
        for contract_id in contract_ids:
            if not CONTRACT_ID.fullmatch(contract_id):
                errors.append(f"{record_id}: invalid executable contract ID {contract_id}")
        for code in [*finding_codes, *related_codes]:
            if not FINDING_CODE.fullmatch(code):
                errors.append(f"{record_id}: invalid Finding code {code}")

        negative_result = item.get("negative_result")
        if item.get("kind") == "negative-result":
            if not isinstance(negative_result, dict):
                errors.append(f"{record_id}: negative-result kind requires a negative_result table")
            else:
                for field in (
                    "question", "hypothesis", "motivation", "experimental_setup",
                    "software_environment", "observed_result", "failure_criterion",
                    "interpretation", "review_status",
                ):
                    if not isinstance(negative_result.get(field), str) or not negative_result[field].strip():
                        errors.append(f"{record_id}: missing or empty negative_result.{field}")
                for field in (
                    "cases", "attempted_methods", "establishes", "conditions_might_work",
                    "reproducer_commands",
                ):
                    require_unique_strings(
                        record_id,
                        f"negative_result.{field}",
                        negative_result.get(field),
                        errors,
                    )
                require_unique_strings(
                    record_id,
                    "negative_result.literature_keys",
                    negative_result.get("literature_keys"),
                    errors,
                    allow_empty=True,
                )
        elif negative_result is not None:
            errors.append(f"{record_id}: negative_result table is only valid for negative-result kind")

        numerical_pathology = item.get("numerical_pathology")
        if item.get("kind") == "numerical-pathology":
            if not isinstance(numerical_pathology, dict):
                errors.append(f"{record_id}: numerical-pathology kind requires a numerical_pathology table")
            else:
                for field in (
                    "phenomenon", "experimental_setup", "observed_behavior",
                    "algorithmic_boundary", "review_status",
                ):
                    if not isinstance(numerical_pathology.get(field), str) or not numerical_pathology[field].strip():
                        errors.append(f"{record_id}: missing or empty numerical_pathology.{field}")
                for field in (
                    "invalid_inferences", "discriminating_checks", "conditions_might_change",
                    "reproducer_commands",
                ):
                    require_unique_strings(
                        record_id,
                        f"numerical_pathology.{field}",
                        numerical_pathology.get(field),
                        errors,
                    )
        elif numerical_pathology is not None:
            errors.append(f"{record_id}: numerical_pathology table is only valid for numerical-pathology kind")

        record = {
            "schema_version": SCHEMA_VERSION,
            "record_id": f"knowledge:{record_id}",
            "record_type": "scientific_knowledge",
            "knowledge_id": record_id,
            "kind": item["kind"],
            "title": item["title"],
            "scientific_statement": item["scientific_statement"],
            "scope": item["scope"],
            "evidence_status": item["evidence_status"],
            "does_not_establish": item["does_not_establish"],
            "book": book,
            "executable": executable,
            "source": {
                "repository": "frederikgeth/multi-graph-book",
                "path": "knowledge/psk.toml",
                "anchor": record_id,
                "sha256": sha256_file(REGISTRY),
            },
            "release": release_identity(),
            "text": knowledge_text(item),
        }
        if negative_result is not None:
            record["negative_result"] = negative_result
        if numerical_pathology is not None:
            record["numerical_pathology"] = numerical_pathology
        records.append(record)

    records.sort(key=lambda item: item["knowledge_id"])
    # The rendered records already embed `release_identity()`, so changes to
    # its ID/status/review fields make the generated output stale. Do not also
    # hash the complete release-candidate inventory here: that inventory hashes
    # the derived LLM artifacts and would create a release-manifest ↔ corpus
    # dependency cycle in which regeneration can never reach a fixed point.
    source_paths = {REGISTRY, CLAIMS, MISCONCEPTIONS, SCHEMA}
    for item in knowledge:
        for path_string in item.get("book", {}).get("artifact_paths", []):
            source_paths.add(ROOT / path_string)
        for path_string in item.get("book", {}).get("source_paths", []):
            source_paths.add(ROOT / path_string)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": "multi-graph-book-scientific-knowledge-0.1.0",
        "record_count": len(records),
        "knowledge_ids": [item["knowledge_id"] for item in records],
        "corpus_sha256": sha256_bytes(
            ("\n".join(canonical_json(item) for item in records) + ("\n" if records else "")).encode()
        ),
        "release": release_identity(),
        "source_files": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}
            for path in sorted(source_paths)
            if path.is_file()
        ],
    }
    return records, manifest, errors


def rendered_payloads() -> tuple[str, str, list[str]]:
    records, manifest, errors = validate_and_build()
    corpus = "\n".join(canonical_json(item) for item in records) + ("\n" if records else "")
    manifest_text = json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    return corpus, manifest_text, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        corpus, manifest, errors = rendered_payloads()
    except (OSError, KeyError, TypeError, ValueError, tomllib.TOMLDecodeError, json.JSONDecodeError) as error:
        print(f"scientific-knowledge generation failed: {error}")
        return 1
    if errors:
        print("scientific-knowledge validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(corpus)
        MANIFEST.write_text(manifest)
        print(f"wrote {OUTPUT.relative_to(ROOT)} and {MANIFEST.relative_to(ROOT)}")
        return 0
    stale = []
    if not OUTPUT.is_file() or OUTPUT.read_text() != corpus:
        stale.append(OUTPUT.relative_to(ROOT).as_posix())
    if not MANIFEST.is_file() or MANIFEST.read_text() != manifest:
        stale.append(MANIFEST.relative_to(ROOT).as_posix())
    if stale:
        print("scientific-knowledge generated files are missing or stale: " + ", ".join(stale))
        return 1
    print(f"scientific knowledge: {len(corpus.splitlines())} PSK record(s) pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
