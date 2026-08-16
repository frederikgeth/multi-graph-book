#!/usr/bin/env python3
"""Check that reader-facing admonitions use the controlled callout vocabulary."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/src"
CLAIMS = ROOT / "claims/claims.toml"
VOCABULARY_POLICY = DOCS / "start/one-network-five-languages.md"
VOCABULARY_CLAIM_ID = "VOCAB-BRIDGE-001"
ALLOWED = {
    "Graph-theory trap",
    "Circuit-theory trap",
    "Power-system shorthand",
    "Decision-model consequence",
    "Vocabulary bridge",
}
ADMONITION = re.compile(r'^!!!\s+[^\s]+\s+"([^"]+)"\s*$', re.MULTILINE)


def main() -> int:
    failures: list[str] = []
    counts = {label: 0 for label in sorted(ALLOWED)}
    total = 0
    for path in sorted(DOCS.rglob("*.md")):
        text = path.read_text()
        for match in ADMONITION.finditer(text):
            label = match.group(1)
            total += 1
            # Documenter admonitions require a genuinely indented body.  An
            # empty callout is easy to create when editing a long chapter and
            # silently turns the following prose into ordinary body text.
            line_end = text.find("\n", match.end())
            body_start = len(text) if line_end < 0 else line_end + 1
            body_line = text[body_start:].splitlines()[0] if body_start < len(text) else ""
            if not body_line.startswith("    "):
                line = text.count("\n", 0, match.start()) + 1
                failures.append(f"{path.relative_to(ROOT)}:{line}: callout body must be indented by four spaces")
            if label not in ALLOWED:
                line = text.count("\n", 0, match.start()) + 1
                failures.append(f"{path.relative_to(ROOT)}:{line}: unknown callout {label!r}")
            else:
                counts[label] += 1
    missing = [label for label, count in counts.items() if count == 0]
    failures.extend(f"controlled callout is unused: {label}" for label in missing)
    if VOCABULARY_CLAIM_ID not in CLAIMS.read_text():
        failures.append(f"controlled vocabulary claim is missing: {VOCABULARY_CLAIM_ID}")
    if VOCABULARY_CLAIM_ID not in VOCABULARY_POLICY.read_text():
        failures.append(f"vocabulary policy page does not mention {VOCABULARY_CLAIM_ID}")
    if failures:
        print("callout vocabulary audit failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    summary = ", ".join(f"{label}={counts[label]}" for label in sorted(counts))
    print(f"callouts: {total} admonitions use the controlled vocabulary ({summary})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
