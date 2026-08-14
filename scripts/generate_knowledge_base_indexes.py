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
PAGE_STATUS = re.compile(r"^\*\*Page status:\*\*[ \t]*(?P<status>[^\r\n]+)$", re.MULTILINE)


def facets_for_claim(claim: dict) -> set[str]:
    """Return provisional retrieval facets until facets become explicit claim fields.

    The ledger keeps the claim schema deliberately small for now. These facets are
    therefore derived from stable claim IDs and chapter paths, rather than presented
    as additional scientific metadata. The mapping is deterministic and only supports
    HTML navigation while the schema is being normalised.
    """
    claim_id = claim["claim_id"]
    chapter = claim["chapter"]
    facets: set[str] = set()
    if chapter.startswith("docs/src/foundations/") or claim_id.startswith(("ARCH-", "THESIS-")):
        facets.add("representation")
    if "cycles" in chapter or "five-bus" in chapter or claim_id.startswith(("GRAPH-", "TR-PAR-")):
        facets.add("graph-and-topology")
    if chapter.startswith("docs/src/transformations/") or claim_id.startswith("TR-"):
        facets.add("transformations")
    if chapter.startswith("docs/src/cases/") or "decision" in chapter or claim_id.startswith(("TR-PAR-", "TR-XFMR-")):
        facets.add("decision-cases")
    if any(token in chapter for token in ("earth-ground", "rating", "orientation", "translation", "cycles")):
        facets.add("physical-modelling")
    if claim_id.startswith(("NUMERICAL-", "FIXTURE-")) or "executable" in chapter:
        facets.add("numerical-evidence")
    if claim_id.startswith("LIT-") or chapter.startswith("docs/src/literature/"):
        facets.add("study-and-literature")
    if claim_id.startswith(("FIXTURE-", "DATA-", "ARCH-")) or "executable" in chapter or "crosswalk" in chapter:
        facets.add("software-and-data")
    if not facets:
        facets.add("general")
    return facets


def title_for(path: Path) -> str:
    for line in path.read_text().splitlines():
        match = re.match(r"^#\s+(?:\[[^]]+\]\(@id\s+[^)]+\)|.+)$", line)
        if match:
            value = line[2:].strip()
            value = re.sub(r"^\[([^]]+)\]\(@id\s+[^)]+\)$", r"\1", value)
            return value
    return path.stem.replace("-", " ").title()


def page_status_for(path: Path) -> str:
    text = path.read_text()
    match = PAGE_STATUS.search(text)
    if match is None:
        raise ValueError(f"reader-facing page lacks Page status metadata: {rel(path)}")
    # Permit a deliberately wrapped metadata paragraph, but never consume the
    # first heading, table, or body paragraph after a blank line. The previous
    # expression allowed ``\\s*`` to cross line boundaries and flattened whole
    # chapters into the status table.
    lines = [match.group("status").strip()]
    remainder = text[match.end():]
    if remainder.startswith("\r\n"):
        remainder = remainder[2:]
    elif remainder.startswith("\n"):
        remainder = remainder[1:]
    if not remainder or remainder.startswith(("\n", "\r")):
        return lines[0]
    for line in remainder.splitlines():
        if not line.strip():
            break
        if line.lstrip().startswith(("#", "|", "```")):
            break
        lines.append(line.strip())
    return " ".join(lines)


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
    by_facet: dict[str, list[dict]] = defaultdict(list)
    for claim in claims:
        by_type[claim["claim_type"]].append(claim)
        by_verification[claim["verification"]].append(claim)
        for facet in facets_for_claim(claim):
            by_facet[facet].append(claim)

    lines = [
        "# [Knowledge-base indexes](@id knowledge-base-index)",
        "",
        f"<!-- generated-from claims/claims.toml sha256:{source_stamp()} -->",
        "This page is generated from `claims/claims.toml` and the JSON artifacts under",
        "`experiments/generated/`. It is the HTML knowledge base's retrieval layer; the curated",
        "PDF route does not attempt to reproduce these indexes as a linear chapter sequence.",
        "",
        f"**Indexed claims:** {len(claims)}",
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
    lines += [
        "",
        "## Facet indexes",
        "",
        "These retrieval facets are provisional and path-derived. They are navigation aids, not",
        "additional verification labels; explicit facet fields can replace them when the claims",
        "schema is normalised.",
    ]
    for facet in sorted(by_facet):
        lines += ["", f"### `{facet}` ({len(by_facet[facet])})", "", "| Claim | Chapter | Type |", "| --- | --- | --- |"]
        for claim in sorted(by_facet[facet], key=lambda item: item["claim_id"]):
            lines.append(
                f"| `{claim['claim_id']}` — {claim['claim_text']} | "
                f"{link_to_chapter(claim['chapter'])} | `{claim['claim_type']}` |"
            )
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
        "# [Chapter status](@id chapter-status)",
        "",
        f"<!-- generated-from claims/claims.toml sha256:{source_stamp()} -->",
        "This page is generated from the claims ledger. It makes the evidence state visible without",
        "requiring readers to inspect TOML or generated JSON files. Claim absence means the page is",
        "tracked as explanatory, definitional, or proposed material rather than silently treated as a",
        "verified empirical result.",
        "",
        "| Chapter | Page status | Claims | Claim types | Verification | Open issue |",
        "| --- | --- | ---: | --- | --- | --- |",
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
            types, verification, issue = "—", "untracked", "—"
        lines.append(
            f"| [{title_for(path)}](../{path.relative_to(DOCS).as_posix()}) | "
            f"{page_status_for(path)} | {len(records)} | {types} | `{verification}` | {issue} |"
        )
    lines += ["", "_This file is regenerated during the documentation build._", ""]
    STATUS.write_text("\n".join(lines))


def main() -> None:
    claims = load_claims()
    generate_index(claims)
    generate_status(claims)
    print(f"generated {INDEX.relative_to(ROOT)} and {STATUS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
