#!/usr/bin/env python3
"""Generate the reader-facing review protocol and evidence-status page."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review"
MATRIX = REVIEW / "evidence-matrix.csv"
MANIFEST = REVIEW / "snapshot-manifest.json"
PROTOCOL = REVIEW / "protocol.md"
OUTPUT = ROOT / "docs/src/literature/review-protocol-and-evidence-status.md"
SEARCH_OUTPUT_DIR = ROOT / "docs/src/literature/search-runs"

manifest = json.loads(MANIFEST.read_text())
rows = list(csv.DictReader(MATRIX.open(newline="")))
protocol = PROTOCOL.read_text()
protocol_version = re.search(r"Protocol version\s+([0-9.]+)", protocol).group(1)
sources = re.search(r"Search ([^.]+)\. Use publisher", protocol, re.S).group(1)
sources = re.sub(r",\s+and relevant standards and\s+official software documentation", ", relevant standards and official software documentation", sources)
database_names = [item.strip() for item in sources.split(",")]
database_names = [item for item in database_names if item]
screening = Counter(row["screening_status"] for row in rows)
coding = Counter(row["coding_status"] for row in rows)
exactness = Counter(row["exactness"] for row in rows)
search_runs = manifest.get("search_runs", [])

def link(path: str) -> str:
    return f"[`{Path(path).name}`](search-runs/{Path(path).name})"


# Keep the reader-facing record self-contained: Documenter deliberately rejects
# links that escape `docs/src`, so publish verbatim, dated copies of the search
# run notes alongside the generated status page. The review directory remains
# the source of truth; these files are regenerated on every build.
SEARCH_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
for path in search_runs:
    source = ROOT / path
    target = SEARCH_OUTPUT_DIR / source.name
    target.write_text(
        source.read_text().replace(
            "\n\n**Protocol:**",
            "\n\n**Page status:** generated search-run record.\n\n**Protocol:**",
            1,
        )
    )

lines = [
    "# [Review protocol and evidence status](@id review-protocol-evidence-status)",
    "",
    "**Page status:** generated scoping-review snapshot and evidence-status record.",
    "",
    "This page is generated from `review/snapshot-manifest.json` and the canonical",
    "evidence matrix. It publishes the review state without implying that a",
    "single-coded seed corpus is an independently validated systematic review.",
    "",
    "## Published snapshot",
    "",
    "| field | value |",
    "| --- | --- |",
    f"| protocol version | `{protocol_version}` |",
    f"| snapshot date | `{manifest.get('snapshot_date', 'not recorded')}` |",
    f"| matrix records | {len(rows)} |",
    f"| matrix SHA-256 | `{manifest['matrix']['sha256']}` |",
f"| deduplication rows | {manifest['deduplication']['row_count']} |",
f"| deduplication SHA-256 | `{manifest['deduplication']['sha256']}` |",
f"| independent human double-coding | {'yes' if manifest.get('independent_double_coding', False) else 'no'} |",
    "",
    "### Screening and coding counts",
    "",
    "| dimension | counts |",
    "| --- | --- |",
    f"| screening status | include: **{screening.get('include', 0)}**; exclude: **{screening.get('exclude', 0)}**; uncertain: **{screening.get('uncertain', 0)}** |",
    f"| coding status | " + "; ".join(f"`{key}`: **{value}**" for key, value in sorted(coding.items())) + " |",
    f"| exactness labels | " + "; ".join(f"`{key}`: **{value}**" for key, value in sorted(exactness.items())) + " |",
    "",
    "The current snapshot is therefore a **single-coded seed snapshot**, not a",
    "double-coded corpus. The 2026-08-15 second-coding log recommends eight",
    "rows for promotion after slot repairs and identifies six substantive coding",
    "conflicts; those recommendations remain pending and are not silently",
    "reflected in the canonical matrix.",
    "",
    "## Search coverage",
    "",
    "The protocol names the following information sources:",
    "",
]
lines.extend(f"- {name}" for name in database_names)
lines += [
    "",
    "The dated search runs included in this snapshot are:",
    "",
]
lines.extend(f"- {link(path)}" for path in search_runs)
lines += [
    "",
    "The search-run files record query families, available platforms, and",
    "limitations for each run. The protocol also requires backward and forward",
    "citation chasing, duplicate resolution, and a saved-search rerun before a",
    "tagged release; these are not claimed complete merely because a row is in",
    "the matrix.",
    "",
    "## Evidence-status interpretation",
    "",
    "A populated matrix row means that one source-to-target result was coded at a",
    "declared scope. It does not mean that the source is a proof of the book's",
    "architecture, that an exactness label applies to a feasible set, or that a",
    "software conversion preserves provenance and limits. The `exactness_object`,",
    "`recovery_map`, `constraint_map`, and `provenance_map` fields must be read",
    "together.",
    "",
    "The second-coding and independent-technical-review documents are retained",
    "as review evidence, but they are not substitutes for an independent human",
    "double-coding pass. The canonical matrix remains the source of published",
    "counts; dated snapshots and reconciliation notes explain proposed changes",
    "without rewriting history.",
    "",
    "## Reproducibility inputs",
    "",
    f"The manifest records {len(manifest.get('inputs', {}))} hashed protocol, coding, bibliography, and search-run inputs.",
    "Run `scripts/check_review_snapshot.py` to verify the matrix,",
    "deduplication register, record identifiers, and input hashes against this",
    "published snapshot.",
    "",
    "The protocol's promised PRISMA-style flow is represented here as a scoped",
    "count table rather than a clinical-review claim: the available evidence is",
    "a seed search with one explicit exclusion, and the screening/coding pipeline",
    "is still being expanded.",
]
OUTPUT.write_text("\n".join(lines) + "\n")
print(f"generated {OUTPUT}")
