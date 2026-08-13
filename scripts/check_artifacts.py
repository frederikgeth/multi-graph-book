#!/usr/bin/env python3
"""Check local links, generated artifacts, claims, and view provenance."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data/running-network/v0.1.0.json"
GENERATED = ROOT / "experiments/generated"
FIGURE = ROOT / "docs/src/assets/running-network-views.png"
SOURCE_MAP = GENERATED / "view-source-maps.json"
CLEAN_REPRODUCTION = GENERATED / "clean-reproduction"
CERTIFICATE_SCHEMA = ROOT / "schemas/transformation-certificate.schema.json"
CERTIFICATES = (
    "parallel-branch-certificate.json",
    "degree-two-series-certificate.json",
    "coordinate-normalization-certificate.json",
    "coordinate-series-composition-certificate.json",
    "parallel-opf-comparison.json",
)
EXPECTED_VIEWS = {
    "asset_property",
    "terminal_connectivity",
    "bus_branch_multigraph",
    "port_factor",
    "opf_equation",
    "sparsity",
}
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)|!\[[^\]]*\]\(([^)]+)\)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    with path.open() as stream:
        return json.load(stream)


def source_ids(network: dict) -> set[str]:
    result: set[str] = set()
    for family in ("bus", "line", "switch", "shunt", "load", "generator", "voltage_source"):
        result.update(f"{family}/{identifier}" for identifier in network.get(family, {}))
    for family, devices in network.get("transformer", {}).items():
        result.update(f"transformer/{family}/{identifier}" for identifier in devices)
    return result


def validate_certificate(certificate: dict, schema: dict, artifact: str) -> list[str]:
    errors: list[str] = []
    required = set(schema["required"])
    missing = required - set(certificate)
    extra = set(certificate) - set(schema["properties"])
    if missing:
        errors.append(f"{artifact} is missing schema fields {sorted(missing)}")
    if extra:
        errors.append(f"{artifact} has undeclared schema fields {sorted(extra)}")
    if certificate.get("schema_version") != "1.0.0":
        errors.append(f"{artifact} has unsupported schema version")
    if not re.fullmatch(r"TR-[A-Z]+-[0-9]{3}", certificate.get("certificate_id", "")):
        errors.append(f"{artifact} has an invalid certificate ID")
    classifications = schema["properties"]["classification"]["enum"]
    if certificate.get("classification") not in classifications:
        errors.append(f"{artifact} has an invalid classification")
    for side in ("source", "target"):
        model = certificate.get(side)
        if not isinstance(model, dict):
            errors.append(f"{artifact} {side} is not an object")
            continue
        if not isinstance(model.get("model_category"), str) or not model["model_category"]:
            errors.append(f"{artifact} {side} lacks a model category")
        object_ids = model.get("object_ids")
        if (
            not isinstance(object_ids, list)
            or not object_ids
            or not all(isinstance(item, str) and item for item in object_ids)
            or len(object_ids) != len(set(object_ids))
        ):
            errors.append(f"{artifact} {side} object IDs must be unique nonempty strings")
    for field in ("preconditions", "preserves", "forgets"):
        values = certificate.get(field)
        if (
            not isinstance(values, list)
            or not all(isinstance(item, str) for item in values)
            or len(values) != len(set(values))
        ):
            errors.append(f"{artifact} {field} must contain unique strings")
    for field in ("recovery_map", "constraint_map"):
        mapping = certificate.get(field)
        if not isinstance(mapping, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in mapping.items()
        ):
            errors.append(f"{artifact} {field} must map strings to strings")
    for field in ("provenance", "evidence"):
        if not isinstance(certificate.get(field), dict):
            errors.append(f"{artifact} {field} must be an object")
    return errors


def check_links(errors: list[str]) -> int:
    checked = 0
    candidates = [ROOT / name for name in ("README.md", "ROADMAP.md", "HANDOVER.md", "BOOK_PLAN.md", "CONTRIBUTING.md")]
    candidates += sorted((ROOT / "docs/src").rglob("*.md"))
    candidates += sorted((ROOT / "review").rglob("*.md")) if (ROOT / "review").exists() else []
    for document in candidates:
        if not document.is_file():
            continue
        for match in LINK.finditer(document.read_text()):
            destination = next(group for group in match.groups() if group is not None).strip()
            if destination.startswith(("http://", "https://", "mailto:", "#", "@ref", "@cite", "@id")):
                continue
            if " " in destination and not destination.startswith("<"):
                destination = destination.split(" ", 1)[0]
            destination = unquote(destination.strip("<> ")).split("#", 1)[0]
            if not destination:
                continue
            checked += 1
            target = Path(destination)
            target = target if target.is_absolute() else (document.parent / target).resolve()
            if not target.exists():
                errors.append(f"broken local link in {document.relative_to(ROOT)}: {destination}")
    return checked


def main() -> int:
    errors: list[str] = []
    required = [
        FIXTURE,
        FIGURE,
        GENERATED / "summary.json",
        CERTIFICATE_SCHEMA,
        *(GENERATED / artifact for artifact in CERTIFICATES),
        GENERATED / "provenance.json",
        SOURCE_MAP,
        CLEAN_REPRODUCTION / "v0.1.0.json",
        CLEAN_REPRODUCTION / "summary.json",
        CLEAN_REPRODUCTION / "provenance.json",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required artifact: {path.relative_to(ROOT)}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    network = load_json(FIXTURE)
    sources = source_ids(network)
    summary = load_json(GENERATED / "summary.json")
    fixture_version = network.get("meta", {}).get("version")
    if summary.get("fixture_version") != fixture_version:
        errors.append("fixture version differs between fixture and summary")

    claims = tomllib.loads((ROOT / "claims/claims.toml").read_text()).get("claim", [])
    claim_ids = {claim["claim_id"] for claim in claims}
    certificate_schema = load_json(CERTIFICATE_SCHEMA)
    for artifact in CERTIFICATES:
        certificate = load_json(GENERATED / artifact)
        errors.extend(validate_certificate(certificate, certificate_schema, artifact))
        certificate_id = certificate.get("certificate_id")
        if certificate_id not in claim_ids:
            errors.append(f"{artifact} uses unregistered claim/certificate ID {certificate_id!r}")

    provenance = load_json(GENERATED / "provenance.json")
    repository = provenance.get("bmopftools_repository", {})
    if not re.fullmatch(r"[0-9a-f]{40}", repository.get("commit", "")):
        errors.append("provenance does not contain a full BMOPFTools commit")
    if not isinstance(repository.get("dirty"), bool):
        errors.append("provenance dirty state is not boolean")

    clean_repository = load_json(CLEAN_REPRODUCTION / "provenance.json").get(
        "bmopftools_repository", {}
    )
    if clean_repository.get("dirty") is not False:
        errors.append("clean reproduction records a dirty BMOPFTools checkout")
    if clean_repository.get("commit") != repository.get("commit"):
        errors.append("local and clean reproductions use different BMOPFTools commits")
    if (CLEAN_REPRODUCTION / "v0.1.0.json").read_bytes() != FIXTURE.read_bytes():
        errors.append("clean reproduction fixture differs from the canonical fixture")
    clean_summary = load_json(CLEAN_REPRODUCTION / "summary.json")
    for field in ("power_flow", "optimal_power_flow"):
        if clean_summary.get(field, {}).get("termination_status") != summary.get(field, {}).get("termination_status"):
            errors.append(f"clean and local {field} termination statuses differ")

    maps = load_json(SOURCE_MAP)
    if set(maps.get("views", {})) != EXPECTED_VIEWS:
        errors.append("view source-map set does not match the six required views")
    if maps.get("fixture_sha256") != sha256(FIXTURE):
        errors.append("view source map was not generated from the current fixture")
    if maps.get("figure_sha256") != sha256(FIGURE):
        errors.append("view source map does not match the current figure")
    for view_name, view in maps.get("views", {}).items():
        generated_ids: set[str] = set()
        objects = view.get("generated_objects", [])
        if not objects:
            errors.append(f"view {view_name} has no mapped generated objects")
        for generated in objects:
            generated_id = generated.get("generated_id", "")
            if generated_id in generated_ids:
                errors.append(f"view {view_name} repeats generated ID {generated_id}")
            generated_ids.add(generated_id)
            object_sources = generated.get("sources", [])
            if not object_sources:
                errors.append(f"view {view_name} object {generated_id} has no source")
            unknown = set(object_sources) - sources
            if unknown:
                errors.append(f"view {view_name} object {generated_id} has unknown sources {sorted(unknown)}")

    checked_links = check_links(errors)
    if errors:
        print("artifact validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"artifacts: {len(required)} required files, {len(CERTIFICATES)} certificates, "
        f"{len(sources)} source objects, {len(EXPECTED_VIEWS)} view maps, "
        f"and {checked_links} local links valid"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
