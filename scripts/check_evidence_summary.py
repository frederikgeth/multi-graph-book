#!/usr/bin/env python3
"""Check that generated evidence summaries agree with the claims ledger."""

from __future__ import annotations

import re
import tomllib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "claims/claims.toml"
KNOWLEDGE_BASE_INDEX = ROOT / "docs/src/reference/knowledge-base-index.md"
EVIDENCE_MAP = ROOT / "docs/src/reference/evidence-map.md"
EVIDENCE_FIGURE = ROOT / "docs/src/assets/reference-evidence-map.svg"
VERIFICATION_FIGURE = ROOT / "docs/src/assets/reference-verification-summary.svg"
STATES = ("self-checked", "independently-implemented", "externally-reviewed")


def expected_sentence(claims: list[dict]) -> str:
    totals = Counter(claim["verification"] for claim in claims)
    return (
        f"The verification summary reports {totals['self-checked']} self-checked, "
        f"{totals['independently-implemented']} independently implemented, and "
        f"{totals['externally-reviewed']} externally reviewed claims out of {len(claims)}"
    )


def find_evidence_summary_errors() -> list[str]:
    claims = tomllib.loads(CLAIMS.read_text()).get("claim", [])
    totals = Counter(claim["verification"] for claim in claims)
    errors: list[str] = []

    index = KNOWLEDGE_BASE_INDEX.read_text()
    indexed_match = re.search(r"\*\*Indexed claims:\*\* (\d+)", index)
    if not indexed_match or int(indexed_match.group(1)) != len(claims):
        errors.append("knowledge-base index claim count disagrees with claims.toml")
    for state in STATES:
        match = re.search(rf"\| `{re.escape(state)}` \| (\d+) \|", index)
        if not match or int(match.group(1)) != totals[state]:
            errors.append(f"knowledge-base index verification count disagrees for {state}")

    evidence = EVIDENCE_MAP.read_text()
    if "<!-- generated-evidence-summary:start -->" not in evidence or "<!-- generated-evidence-summary:end -->" not in evidence:
        errors.append("evidence-map.md lacks generated summary markers")
    if expected_sentence(claims) not in evidence:
        errors.append("evidence-map.md summary disagrees with claims.toml")

    evidence_figure = EVIDENCE_FIGURE.read_text()
    if f"{len(claims)} claims" not in evidence_figure:
        errors.append("reference-evidence-map.svg claim count disagrees with claims.toml")

    verification_figure = VERIFICATION_FIGURE.read_text()
    if f"{len(claims)} claims" not in verification_figure:
        errors.append("reference-verification-summary.svg claim count disagrees with claims.toml")
    expected_figure_counts = " · ".join(f"{totals[state]} {state}" for state in STATES)
    if expected_figure_counts not in verification_figure:
        errors.append("reference-verification-summary.svg verification counts disagree with claims.toml")

    return errors


def main() -> int:
    errors = find_evidence_summary_errors()
    if errors:
        for error in errors:
            print(f"evidence summary validation failed: {error}")
        return 1
    claims = tomllib.loads(CLAIMS.read_text()).get("claim", [])
    totals = Counter(claim["verification"] for claim in claims)
    print(
        f"evidence summary: {len(claims)} claims; "
        + ", ".join(f"{state}={totals[state]}" for state in STATES)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
