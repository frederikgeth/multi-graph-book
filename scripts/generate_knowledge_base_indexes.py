#!/usr/bin/env python3
"""Generate HTML-first knowledge-base indexes from the claims and artifacts ledgers."""

from __future__ import annotations

import json
import hashlib
import re
import tomllib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "claims/claims.toml"
DOCS = ROOT / "docs/src"
GENERATED = ROOT / "experiments/generated"
INDEX = DOCS / "reference/knowledge-base-index.md"
STATUS = DOCS / "reference/chapter-status.md"


def title_for(path: Path) -> str:
    for line in path.read_text().splitlines():
        match = re.match(r"^#\s+(?:\[[^]]+\]\(@id\s+[^)]+\)|.+)$", line)
        if match:
            value = line[2:].strip()
            value = re.sub(r"^\[([^]]+)\]\(@id\s+[^)]+\)$", r"\1", value)
            return value
    return path.stem.replace("-", " ").title()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def link_to_chapter(path_string: str) -> str:
    path = ROOT / path_string
    return f"[{title_for(path)}](../{path.relative_to(DOCS).as_posix()})"


def load_claims() -> list[dict]:
    return tomllib.loads(CLAIMS.read_text()).get("claim", [])


def source_stamp() -> str:
    return hashlib.sha256(CLAIMS.read_bytes()).hexdigest()


def artifact_summary(path: Path) -> str:
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return "JSON artifact"
    identifiers = [data.get(key) for key in ("certificate_id", "claim_id", "witness_id", "analysis_id")]
    identifier = next((value for value in identifiers if value), None)
    scope = data.get("model_scope") or data.get("source_fixture") or "generated evidence"
    return f"`{identifier}` — {scope}" if identifier else str(scope)


def generate_index(claims: list[dict]) -> None:
    by_type: dict[str, list[dict]] = defaultdict(list)
    by_verification: dict[str, list[dict]] = defaultdict(list)
    for claim in claims:
        by_type[claim["claim_type"]].append(claim)
        by_verification[claim["verification"]].append(claim)

    lines = [
        "# Knowledge-base indexes",
        "",
        f"<!-- generated-from claims/claims.toml sha256:{source_stamp()} -->",
        "This page is generated from `claims/claims.toml` and the JSON artifacts under",
        "`experiments/generated/`. It is the HTML knowledge base's retrieval layer; the curated",
        "PDF route does not attempt to reproduce these indexes as a linear chapter sequence.",
        "",
        f"**Indexed claims:** {len(claims)}  ",
        f"**Indexed chapters:** {len({claim['chapter'] for claim in claims})}",
        "",
        "## Claims by type",
        "",
    ]
    for key in sorted(by_type):
        lines += [f"### `{key}` ({len(by_type[key])})", "", "| Claim | Chapter | Verification |", "| --- | --- | --- |"]
        for claim in sorted(by_type[key], key=lambda item: item["claim_id"]):
            lines.append(f"| `{claim['claim_id']}` — {claim['claim_text']} | {link_to_chapter(claim['chapter'])} | `{claim['verification']}` |")
        lines.append("")

    lines += ["## Claims by verification state", "", "| Verification | Claims |", "| --- | ---: |"]
    for key in sorted(by_verification):
        lines.append(f"| `{key}` | {len(by_verification[key])} |")
    lines += ["", "## Unresolved issues", "", "| Claim | Issue |", "| --- | --- |"]
    for claim in sorted(claims, key=lambda item: item["claim_id"]):
        issue = claim.get("unresolved_issue", "").strip()
        if issue:
            lines.append(f"| `{claim['claim_id']}` | {issue} |")
    lines += ["", "## Generated artifacts", "", "| Artifact | Evidence summary |", "| --- | --- |"]
    for path in sorted(GENERATED.glob("*.json")):
        lines.append(f"| `{path.name}` | {artifact_summary(path)} |")
    lines += ["", "_This file is regenerated during the documentation build._", ""]
    INDEX.write_text("\n".join(lines))


def generate_status(claims: list[dict]) -> None:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for claim in claims:
        grouped[claim["chapter"]].append(claim)
    chapter_paths = sorted(DOCS.rglob("*.md"))
    lines = [
        "# Chapter status",
        "",
        f"<!-- generated-from claims/claims.toml sha256:{source_stamp()} -->",
        "This page is generated from the claims ledger. It makes the evidence state visible without",
        "requiring readers to inspect TOML or generated JSON files. A chapter with no claim entry is",
        "not automatically unscientific; it is marked as needing explicit scope/status metadata.",
        "",
        "| Chapter | Claims | Claim types | Verification | Open issue |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for path in chapter_paths:
        if path in (INDEX, STATUS):
            continue
        chapter = rel(path)
        records = grouped.get(chapter, [])
        if records:
            types = ", ".join(sorted({record["claim_type"] for record in records}))
            verification = ", ".join(sorted({record["verification"] for record in records}))
            issues = "; ".join(record.get("unresolved_issue", "").strip() for record in records if record.get("unresolved_issue", "").strip())
            issue = issues if issues else "—"
        else:
            types, verification, issue = "—", "untracked", "Add chapter-level scope/status metadata"
        lines.append(f"| [{title_for(path)}](../{path.relative_to(DOCS).as_posix()}) | {len(records)} | {types} | `{verification}` | {issue} |")
    lines += ["", "_This file is regenerated during the documentation build._", ""]
    STATUS.write_text("\n".join(lines))


def main() -> None:
    claims = load_claims()
    generate_index(claims)
    generate_status(claims)
    print(f"generated {INDEX.relative_to(ROOT)} and {STATUS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
