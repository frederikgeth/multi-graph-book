#!/usr/bin/env python3
"""Check the recorded neural benchmark without loading neural models."""

from __future__ import annotations

import hashlib
import json
import sys
import tomllib
from pathlib import Path

from evaluate_llm_retrieval import evaluate, ROOT
from benchmark_llm_embeddings import markdown_report

REPORT = ROOT / "llm/generated/neural-retrieval-evaluation.json"
MARKDOWN = ROOT / "llm/generated/neural-retrieval-evaluation.md"
CONFIG = ROOT / "llm/neural-models.toml"
CORPUS_MANIFEST = ROOT / "llm/generated/corpus-manifest.json"
HELDOUT = ROOT / "llm/heldout-paraphrases.toml"
SHA256_LENGTH = 64


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(errors: list[str], condition: bool, message: str) -> None:
    if condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    try:
        report = json.loads(REPORT.read_text())
        config = tomllib.loads(CONFIG.read_text())
        manifest = json.loads(CORPUS_MANIFEST.read_text())
        current_retrieval = evaluate()
    except (OSError, ValueError, KeyError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        print(f"LLM neural benchmark check failed to load inputs: {error}")
        return 1

    fail(errors, report.get("schema_version") != "0.1.0", "neural benchmark schema version drift")
    fail(errors, report.get("corpus", {}).get("corpus_id") != manifest.get("corpus_id"), "neural benchmark corpus ID drift")
    fail(errors, report.get("corpus", {}).get("corpus_sha256") != manifest.get("corpus_sha256"), "neural benchmark corpus hash drift")
    heldout_input = report.get("inputs", {}).get("heldout_paraphrases", {})
    fail(errors, heldout_input.get("sha256") != sha256(HELDOUT), "neural benchmark held-out input hash drift")

    embedding = report.get("embedding_provenance", {})
    embedding_config = config.get("embedding", {})
    for report_field, config_field in (("model_id", "model_id"), ("model_revision", "revision"), ("artifact_sha256", "artifact_sha256")):
        fail(errors, embedding.get(report_field) != embedding_config.get(config_field), f"embedding provenance drift: {report_field}")
    fail(errors, len(str(embedding.get("artifact_sha256", ""))) != SHA256_LENGTH, "embedding artifact hash is incomplete")

    reranker = report.get("reranker_provenance") or {}
    reranker_config = config.get("reranker", {})
    for report_field, config_field in (("model_id", "model_id"), ("model_revision", "revision"), ("artifact_sha256", "artifact_sha256")):
        fail(errors, reranker.get(report_field) != reranker_config.get(config_field), f"reranker provenance drift: {report_field}")
    fail(errors, len(str(reranker.get("artifact_sha256", ""))) != SHA256_LENGTH, "reranker artifact hash is incomplete")

    current_summary = current_retrieval["heldout"]["summary"]
    report_summary = report.get("summary", {})
    for method in ("lexical", "char_tfidf", "hybrid"):
        for metric in ("recall_at_5", "recall_at_10", "complete_at_10", "mean_reciprocal_rank_at_20"):
            fail(
                errors,
                report_summary.get(method, {}).get(metric) != current_summary[method][metric],
                f"recorded {method} {metric} differs from the current baseline",
            )
    fail(errors, not REPORT.is_file(), "neural benchmark JSON report is missing")
    if REPORT.is_file() and MARKDOWN.is_file():
        fail(errors, MARKDOWN.read_text() != markdown_report(report), "neural benchmark Markdown report is stale")
    else:
        errors.append("neural benchmark Markdown report is missing")

    if errors:
        print("LLM neural benchmark check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    neural = report_summary["neural"]
    reranked = report_summary.get("hybrid_reranked", {})
    print(
        "LLM neural benchmark: recorded pinned models; "
        f"neural_recall_at_10={100 * neural['recall_at_10']:.1f}%; "
        f"hybrid_recall_at_10={100 * report_summary['hybrid']['recall_at_10']:.1f}%; "
        f"reranked_recall_at_10={100 * reranked.get('recall_at_10', 0.0):.1f}%; "
        f"candidate_status={report.get('status')} (negative results retained)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
