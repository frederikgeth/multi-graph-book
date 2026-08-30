#!/usr/bin/env python3
"""Regenerate the cross-repository scientific and LLM derived artifacts."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bmopf-root",
        type=Path,
        default=ROOT.parent / "BMOPFTools.jl",
        help="sibling BMOPFTools.jl checkout used by the federation check",
    )
    args = parser.parse_args()
    commands = [
        [sys.executable, "scripts/check_neural_benchmark.py", "--write-negative-result"],
        [sys.executable, "scripts/generate_scientific_knowledge.py", "--write"],
        [sys.executable, "scripts/check_federated_knowledge.py", "--write", "--bmopf-root", str(args.bmopf_root)],
        [sys.executable, "scripts/generate_llm_corpus.py", "--write"],
    ]
    for command in commands:
        print("[regenerate]", " ".join(map(str, command)))
        subprocess.run(command, cwd=ROOT, check=True)
    print("regenerated scientific, federated, and LLM corpus artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
