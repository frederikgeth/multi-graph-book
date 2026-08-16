#!/usr/bin/env python3
"""Create a blank independent second-coding worksheet from the canonical matrix."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "review/evidence-matrix.csv"
OUTPUT = ROOT / "review/second-coding-template.csv"

with MATRIX.open(newline="") as stream:
    rows = list(csv.DictReader(stream))

fields = [
    "record_id",
    "citation_key",
    "primary_screening_status",
    "primary_transformation_type",
    "primary_exactness",
    "primary_exactness_object",
    "primary_review_basis",
    "second_screening_status",
    "second_transformation_type",
    "second_exactness",
    "second_exactness_object",
    "second_reviewer",
    "second_review_date",
    "resolution_status",
    "resolution_note",
]

with OUTPUT.open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "record_id": row["record_id"],
                "citation_key": row["citation_key"],
                "primary_screening_status": row["screening_status"],
                "primary_transformation_type": row["transformation_type"],
                "primary_exactness": row["exactness"],
                "primary_exactness_object": row["exactness_object"],
                "primary_review_basis": row["review_basis"],
                "second_screening_status": "",
                "second_transformation_type": "",
                "second_exactness": "",
                "second_exactness_object": "",
                "second_reviewer": "",
                "second_review_date": "",
                "resolution_status": "pending",
                "resolution_note": "",
            }
        )

print(f"wrote {OUTPUT} with {len(rows)} pending records")
