#!/usr/bin/env python3
"""Run the dependency-free LLM accessibility reproduction sequence."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
CHECKS = [
    [PYTHON, "scripts/generate_scientific_knowledge.py", "--check"],
    [PYTHON, "scripts/generate_llm_corpus.py", "--check"],
    [PYTHON, "scripts/check_llm_accessibility.py"],
    [PYTHON, "scripts/evaluate_llm_retrieval.py", "--check"],
    [PYTHON, "scripts/generate_llm_access_fixtures.py", "--check"],
    [PYTHON, "scripts/evaluate_llm_adversarial.py", "--check"],
    [PYTHON, "scripts/check_llm_routes.py"],
    [PYTHON, "scripts/check_llm_answer_contract.py"],
]
# scripts/check_neural_benchmark.py is deliberately excluded: it pins a
# sentence-transformers/torch benchmark that must be regenerated with the
# real (heavy, opt-in) model stack whenever corpus content changes, so it
# does not belong in the check run on every ordinary content edit. Run it
# manually when re-pinning, and see scripts/check_release_candidate.py for
# the maintainer release gate that still includes it.


def main() -> int:
    for command in CHECKS:
        result = subprocess.run(command, cwd=ROOT, text=True)
        if result.returncode:
            print(f"LLM reproducibility failed: {' '.join(command)}")
            return result.returncode
    print("LLM reproducibility: scientific knowledge, corpus, retrieval, fixtures, adversarial cases, routes, and answer contracts pass (neural benchmark excluded; see scripts/check_neural_benchmark.py)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
