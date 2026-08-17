#!/usr/bin/env python3
"""Validate the review seed snapshot manifest and row-level joins."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review"
MATRIX = REVIEW / "evidence-matrix.csv"
DEDUP = REVIEW / "deduplication-register.csv"
MANIFEST = REVIEW / "snapshot-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = json.loads(MANIFEST.read_text())
errors: list[str] = []
with MATRIX.open(newline="") as stream:
    matrix = list(csv.DictReader(stream))
with DEDUP.open(newline="") as stream:
    dedup = list(csv.DictReader(stream))

matrix_ids = [row["record_id"] for row in matrix]
dedup_ids = [row["record_id"] for row in dedup]
if set(matrix_ids) != set(dedup_ids):
    errors.append("matrix and deduplication register record IDs differ")
if len(matrix_ids) != len(set(matrix_ids)):
    errors.append("matrix contains duplicate record IDs")
if len(dedup_ids) != len(set(dedup_ids)):
    errors.append("deduplication register contains duplicate record IDs")
for row in dedup:
    if row["decision"] == "unique" and row["canonical_record"] != row["record_id"]:
        errors.append(f"{row['record_id']} unique row does not point to itself")

if manifest.get("matrix", {}).get("sha256") != sha256(MATRIX):
    errors.append("matrix hash does not match snapshot manifest")
if manifest.get("deduplication", {}).get("sha256") != sha256(DEDUP):
    errors.append("deduplication hash does not match snapshot manifest")
if manifest.get("record_ids") != matrix_ids:
    errors.append("snapshot record ID order does not match matrix")
for relative, recorded_hash in manifest.get("inputs", {}).items():
    path = ROOT / relative
    if not path.is_file():
        errors.append(f"snapshot input is missing: {relative}")
    elif sha256(path) != recorded_hash:
        errors.append(f"snapshot input hash changed: {relative}")
if manifest.get("independent_double_coding"):
    errors.append("seed snapshot must not claim independent double-coding")

if errors:
    print("review snapshot validation failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print(f"review snapshot: {len(matrix)} records joined to deduplication register; seed remains single-coded")
