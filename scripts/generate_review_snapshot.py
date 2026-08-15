#!/usr/bin/env python3
"""Write a reproducible manifest for the literature-review seed snapshot."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review"
MATRIX = REVIEW / "evidence-matrix.csv"
DEDUP = REVIEW / "deduplication-register.csv"
AUDIT = REVIEW / "bibliography-audit.toml"
PROTOCOL = REVIEW / "protocol.md"
GUIDE = REVIEW / "coding-guide.md"
SEARCH_STRINGS = REVIEW / "search-strings.md"
SEARCH_RUNS = sorted((REVIEW / "search-runs").glob("*.md"))
OUTPUT = REVIEW / "snapshot-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


with MATRIX.open(newline="") as stream:
    rows = list(csv.DictReader(stream))
with DEDUP.open(newline="") as stream:
    dedup_rows = list(csv.DictReader(stream))

manifest = {
    "schema_version": "0.1.0",
    "snapshot_date": date.today().isoformat(),
    "matrix": {
        "path": "review/evidence-matrix.csv",
        "sha256": sha256(MATRIX),
        "row_count": len(rows),
        "coding_status_counts": dict(Counter(row["coding_status"] for row in rows)),
    },
    "deduplication": {
        "path": "review/deduplication-register.csv",
        "sha256": sha256(DEDUP),
        "row_count": len(dedup_rows),
    },
    "inputs": {
        str(path.relative_to(ROOT)): sha256(path)
        for path in [AUDIT, PROTOCOL, GUIDE, SEARCH_STRINGS, *SEARCH_RUNS]
    },
    "record_ids": [row["record_id"] for row in rows],
    "search_runs": [str(path.relative_to(ROOT)) for path in SEARCH_RUNS],
    "status": "single_coded_seed_snapshot",
    "independent_double_coding": False,
}

with OUTPUT.open("w") as stream:
    json.dump(manifest, stream, indent=2, sort_keys=True)
    stream.write("\n")

print(f"wrote {OUTPUT}")
