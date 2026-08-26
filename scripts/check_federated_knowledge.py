#!/usr/bin/env python3
"""Validate and pin the scientific/executable knowledge pair across both repositories."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCIENTIFIC = ROOT / "generated/scientific_knowledge.jsonl"
SCIENTIFIC_MANIFEST = ROOT / "generated/scientific-knowledge-manifest.json"
PAIR_MANIFEST = ROOT / "generated/federated-knowledge-pair-manifest.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SCHEMA_VERSION = "0.1.0"


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def records(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def book_identity() -> dict:
    manifest = json.loads(SCIENTIFIC_MANIFEST.read_text())
    return {
        "repository": "frederikgeth/multi-graph-book",
        "schema_version": manifest["schema_version"],
        "manifest_sha256": sha256_file(SCIENTIFIC_MANIFEST),
        "corpus_sha256": manifest["corpus_sha256"],
        "knowledge_ids": manifest["knowledge_ids"],
        "release": manifest["release"],
    }


def bmopf_identity(root: Path) -> tuple[dict, dict[str, dict]]:
    manifest_path = root / "generated/executable-knowledge-manifest.json"
    corpus_path = root / "generated/executable_knowledge.jsonl"
    manifest = json.loads(manifest_path.read_text())
    executable = records(corpus_path)
    if sha256_file(corpus_path) != manifest["corpus_sha256"]:
        raise ValueError("BMOPFTools executable corpus hash differs from its manifest")
    by_id = {item["record_id"]: item for item in executable}
    links: dict[str, dict] = {}
    for scientific in records(SCIENTIFIC):
        knowledge_id = scientific["knowledge_id"]
        declared = scientific["executable"]
        contract_links = []
        for contract_id in declared["contract_ids"]:
            record = by_id.get(f"contract:{contract_id}")
            if record is None:
                raise ValueError(f"{knowledge_id}: BMOPFTools export lacks contract {contract_id}")
            if knowledge_id not in record["knowledge_ids"]:
                raise ValueError(f"{knowledge_id}: BMOPFTools contract omits the PSK backlink")
            contract_links.append(
                {
                    "contract_id": contract_id,
                    "entrypoint": record["entrypoint"],
                    "finding_codes": record["finding_codes"],
                    "fixture_ids": record["fixture_ids"],
                    "source_sha256": record["source"]["sha256"],
                }
            )
        links[knowledge_id] = {
            "repository": declared["repository"],
            "implementation_status": declared["implementation_status"],
            "contracts": contract_links,
        }
    identity = {
        "repository": "frederikgeth/BMOPFTools.jl",
        "schema_version": manifest["schema_version"],
        "manifest_id": manifest["manifest_id"],
        "manifest_sha256": sha256_file(manifest_path),
        "corpus_sha256": manifest["corpus_sha256"],
        "package": manifest["package"],
        "knowledge_ids": manifest["knowledge_ids"],
        "contract_ids": manifest["contract_ids"],
    }
    return identity, links


def assemble(bmopf_root: Path) -> dict:
    bmopf, links = bmopf_identity(bmopf_root)
    pair = {
        "schema_version": SCHEMA_VERSION,
        "pair_id": "multi-graph-book--bmopftools-executable-knowledge-0.1.0",
        "book": book_identity(),
        "bmopftools": bmopf,
        "links": links,
    }
    pair["pair_sha256"] = sha256_bytes(canonical_json(pair).encode())
    return pair


def validate_committed(pair: dict) -> list[str]:
    errors: list[str] = []
    if pair.get("schema_version") != SCHEMA_VERSION:
        errors.append("pair manifest schema version drift")
    identity = dict(pair)
    observed_pair_hash = identity.pop("pair_sha256", "")
    if not SHA256.fullmatch(observed_pair_hash) or observed_pair_hash != sha256_bytes(canonical_json(identity).encode()):
        errors.append("pair manifest identity hash is invalid")
    if pair.get("book") != book_identity():
        errors.append("pair manifest book identity is stale")
    scientific_by_id = {item["knowledge_id"]: item for item in records(SCIENTIFIC)}
    links = pair.get("links", {})
    if set(links) != set(scientific_by_id):
        errors.append("pair manifest PSK coverage differs from the scientific export")
    for knowledge_id, scientific in scientific_by_id.items():
        link = links.get(knowledge_id, {})
        executable = scientific["executable"]
        contracts = link.get("contracts", [])
        if executable["implementation_status"] != "implemented":
            errors.append(f"{knowledge_id}: executable status is not implemented")
        if link.get("implementation_status") != executable["implementation_status"]:
            errors.append(f"{knowledge_id}: implementation status differs across the pair")
        if link.get("repository") != executable["repository"]:
            errors.append(f"{knowledge_id}: executable repository differs across the pair")
        if [item.get("contract_id") for item in contracts] != executable["contract_ids"]:
            errors.append(f"{knowledge_id}: contract IDs differ across the pair")
        observed_findings = sorted({code for item in contracts for code in item.get("finding_codes", [])})
        if observed_findings != sorted(executable["finding_codes"]):
            errors.append(f"{knowledge_id}: Finding codes differ across the pair")
        observed_fixtures = sorted({value for item in contracts for value in item.get("fixture_ids", [])})
        if observed_fixtures != sorted(executable["fixture_ids"]):
            errors.append(f"{knowledge_id}: fixture IDs differ across the pair")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--bmopf-root", type=Path)
    args = parser.parse_args()
    try:
        if args.write:
            if args.bmopf_root is None:
                parser.error("--write requires --bmopf-root")
            payload = assemble(args.bmopf_root.resolve())
            PAIR_MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
            print(f"wrote {PAIR_MANIFEST.relative_to(ROOT)}")
            return 0
        if not PAIR_MANIFEST.is_file():
            print("federated knowledge check failed: pair manifest is missing")
            return 1
        pair = json.loads(PAIR_MANIFEST.read_text())
        errors = validate_committed(pair)
        if args.bmopf_root is not None and pair != assemble(args.bmopf_root.resolve()):
            errors.append("pair manifest is stale against the supplied BMOPFTools checkout")
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"federated knowledge check failed: {error}")
        return 1
    if errors:
        print("federated knowledge check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    scope = "book snapshot"
    if args.bmopf_root is not None:
        scope += " and supplied BMOPFTools checkout"
    print(f"federated knowledge pair is valid against {scope}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
