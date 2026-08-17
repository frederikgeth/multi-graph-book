#!/usr/bin/env python3
"""Maintain an explicit inventory of generated experiment artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "experiments/generated"
MANIFEST = GENERATED / "artifact-manifest.json"
SCHEMA_VERSION = "0.1.0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload() -> str:
    files = []
    for path in sorted(GENERATED.rglob("*.json")):
        if path == MANIFEST:
            continue
        files.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )
    result = {
        "schema_version": SCHEMA_VERSION,
        "purpose": (
            "Inventory of generated experiment JSON artifacts. Semantic validation remains in the "
            "artifact-specific checks; this manifest prevents new generated files from becoming invisible."
        ),
        "artifact_count": len(files),
        "artifacts": files,
    }
    return json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = payload()
    if args.write:
        MANIFEST.write_text(expected)
        print(f"wrote {MANIFEST.relative_to(ROOT)}")
        return 0
    if not MANIFEST.is_file() or MANIFEST.read_text() != expected:
        print("generated artifact manifest is stale or missing")
        print("run: python3 scripts/generate_artifact_manifest.py --write")
        return 1
    result = json.loads(expected)
    print(f"generated artifact manifest: {result['artifact_count']} JSON artifacts are inventoried")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
