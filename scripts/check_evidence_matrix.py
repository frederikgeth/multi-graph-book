#!/usr/bin/env python3
"""Validate the versioned scoping-review evidence matrix.

The current matrix is intentionally a seed set.  This check validates its
shape and controlled vocabulary without pretending that a single-coded row is
double-coded.  Pass ``--require-double-coded`` only for a release snapshot
whose second-coder fields have actually been added.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "review/evidence-matrix.csv"
SCHEMA = ROOT / "review/evidence-schema.json"

REQUIRED = {
    "record_id", "citation_key", "screening_status", "source_model",
    "target_model", "transformation_type", "exactness", "model_scope",
    "decision_scope", "evidence_type", "coding_status",
}
ENUMS = {
    "screening_status": {"include", "exclude", "uncertain"},
    "transformation_type": {
        "projection", "compilation", "normalization",
        "exact_behavioral_reduction", "approximate_reduction",
        "topology_quotient", "other", "not_reported",
    },
    "exactness": {"exact", "inner", "outer", "scenario_approximate", "unclassified", "not_reported"},
    "evidence_type": {"proof", "derivation", "empirical", "software", "standard", "engineering_practice", "mixed", "not_reported"},
    "coding_status": {"seed", "single_coded", "double_checked", "conflict"},
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-double-coded", action="store_true")
    args = parser.parse_args()
    schema = json.loads(SCHEMA.read_text())
    expected_columns = list(schema["properties"])
    errors: list[str] = []
    with MATRIX.open(newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != expected_columns:
            errors.append("evidence matrix columns do not match evidence-schema.json")
        rows = list(reader)

    seen: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        missing = sorted(field for field in REQUIRED if not row.get(field, "").strip())
        if missing:
            errors.append(f"row {row_number} is missing required fields {missing}")
        record_id = row.get("record_id", "")
        if record_id in seen:
            errors.append(f"row {row_number} repeats record ID {record_id}")
        seen.add(record_id)
        if record_id and not record_id.startswith("EV-"):
            errors.append(f"row {row_number} has invalid record ID {record_id}")
        for field, allowed in ENUMS.items():
            if row.get(field) not in allowed:
                errors.append(f"row {row_number} has invalid {field}={row.get(field)!r}")
        if row.get("screening_status") == "exclude" and not row.get("exclusion_reason", ""):
            errors.append(f"row {row_number} excludes a record without an exclusion reason")
        if row.get("screening_status") != "exclude" and row.get("exclusion_reason", ""):
            errors.append(f"row {row_number} has an exclusion reason for a non-excluded record")
        if args.require_double_coded and row.get("coding_status") != "double_checked":
            errors.append(f"row {row_number} is not double_checked in a release-required run")

    if errors:
        print("evidence-matrix validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    counts: dict[str, int] = {}
    for row in rows:
        key = row["coding_status"]
        counts[key] = counts.get(key, 0) + 1
    print(f"evidence matrix: {len(rows)} rows valid; coding statuses {counts}; release double-coding requirement={args.require_double_coded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
