#!/usr/bin/env python3
"""Check the recorded neural benchmark without loading neural models."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from datetime import date
from pathlib import Path

from evaluate_llm_retrieval import evaluate, ROOT
from benchmark_llm_embeddings import markdown_report

REPORT = ROOT / "llm/generated/neural-retrieval-evaluation.json"
MARKDOWN = ROOT / "llm/generated/neural-retrieval-evaluation.md"
NEGATIVE_RESULT = ROOT / "llm/generated/neural-retrieval-negative-result.json"
CONFIG = ROOT / "llm/neural-models.toml"
CORPUS_MANIFEST = ROOT / "llm/generated/corpus-manifest.json"
HELDOUT = ROOT / "llm/heldout-paraphrases.toml"
SHA256_LENGTH = 64


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(errors: list[str], condition: bool, message: str) -> None:
    if condition:
        errors.append(message)


def negative_result_snapshot(report: dict) -> dict:
    """Freeze benchmark evidence without its mutable current-corpus marker."""
    return {
        "schema_version": "0.1.0",
        "negative_result_id": "neural-retrieval-pinned-candidates-001",
        "knowledge_id": "PSK-000015",
        "source_report": "llm/generated/neural-retrieval-evaluation.json",
        "benchmark": {
            key: value
            for key, value in report.items()
            if key != "compatibility"
        },
    }


def negative_result_text(report: dict) -> str:
    return json.dumps(
        negative_result_snapshot(report),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    ) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--archive-current-drift",
        action="store_true",
        help="record that the pinned experiment belongs to its prior corpus and that the current corpus requires a rerun",
    )
    mode.add_argument(
        "--write-negative-result",
        action="store_true",
        help="write the immutable negative-result evidence snapshot",
    )
    args = parser.parse_args()
    errors: list[str] = []
    try:
        report = json.loads(REPORT.read_text())
        # This historical snapshot is an input to scientific/corpus generation.
        # Do not evaluate new cases against the old corpus before it is rebuilt.
        if args.write_negative_result:
            NEGATIVE_RESULT.write_text(negative_result_text(report))
            print("wrote immutable neural retrieval negative-result evidence")
            return 0
        config = tomllib.loads(CONFIG.read_text())
        manifest = json.loads(CORPUS_MANIFEST.read_text())
        current_retrieval = evaluate()
    except (OSError, ValueError, KeyError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        print(f"LLM neural benchmark check failed to load inputs: {error}")
        return 1

    if args.archive_current_drift:
        if report.get("corpus", {}).get("corpus_sha256") == manifest.get("corpus_sha256"):
            print("neural benchmark already matches the current corpus; no archive marker written")
            return 0
        report["compatibility"] = {
            "status": "archived_prior_corpus",
            "archived_on": date.today().isoformat(),
            "current_corpus_id": manifest.get("corpus_id"),
            "current_corpus_sha256": manifest.get("corpus_sha256"),
            "current_record_count": manifest.get("record_count"),
            "current_heldout_sha256": sha256(HELDOUT),
            "current_lexical_summary": {
                method: current_retrieval["heldout"]["summary"][method]
                for method in ("lexical", "char_tfidf", "hybrid")
            },
            "required_action": "rerun both pinned neural retriever and reranker before comparing them with the current corpus",
        }
        REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
        MARKDOWN.write_text(markdown_report(report))
        print("archived the pinned neural result against its prior corpus; current-corpus rerun remains required")
        return 0

    fail(errors, report.get("schema_version") != "0.1.0", "neural benchmark schema version drift")
    fail(errors, report.get("corpus", {}).get("corpus_id") != manifest.get("corpus_id"), "neural benchmark corpus ID drift")
    current_corpus = report.get("corpus", {}).get("corpus_sha256") == manifest.get("corpus_sha256")
    compatibility = report.get("compatibility", {})
    if not current_corpus:
        fail(errors, compatibility.get("status") != "archived_prior_corpus", "neural benchmark corpus hash drift is not explicitly archived")
        fail(errors, compatibility.get("current_corpus_id") != manifest.get("corpus_id"), "archived neural benchmark current corpus ID drift")
        fail(errors, compatibility.get("current_corpus_sha256") != manifest.get("corpus_sha256"), "archived neural benchmark current corpus hash drift")
        fail(errors, compatibility.get("current_record_count") != manifest.get("record_count"), "archived neural benchmark current record count drift")
        fail(errors, compatibility.get("current_heldout_sha256") != sha256(HELDOUT), "archived neural benchmark current held-out input hash drift")
        fail(errors, not compatibility.get("archived_on"), "archived neural benchmark lacks an archive date")
        fail(errors, not compatibility.get("current_lexical_summary"), "archived neural benchmark lacks current lexical baselines")
        fail(errors, not compatibility.get("required_action"), "archived neural benchmark lacks a required rerun action")
    heldout_input = report.get("inputs", {}).get("heldout_paraphrases", {})
    if current_corpus:
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

    report_summary = report.get("summary", {})
    current_summary = current_retrieval["heldout"]["summary"]
    recorded_lexical = report_summary if current_corpus else compatibility.get("current_lexical_summary", {})
    for method in ("lexical", "char_tfidf", "hybrid"):
        for metric in ("recall_at_5", "recall_at_10", "complete_at_10", "mean_reciprocal_rank_at_20"):
            fail(
                errors,
                recorded_lexical.get(method, {}).get(metric) != current_summary[method][metric],
                f"recorded {method} {metric} differs from the current baseline",
            )
    fail(errors, not REPORT.is_file(), "neural benchmark JSON report is missing")
    if REPORT.is_file() and MARKDOWN.is_file():
        fail(errors, MARKDOWN.read_text() != markdown_report(report), "neural benchmark Markdown report is stale")
    else:
        errors.append("neural benchmark Markdown report is missing")
    fail(
        errors,
        not NEGATIVE_RESULT.is_file() or NEGATIVE_RESULT.read_text() != negative_result_text(report),
        "immutable neural negative-result evidence is missing or stale",
    )

    if errors:
        print("LLM neural benchmark check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    neural = report_summary["neural"]
    reranked = report_summary.get("hybrid_reranked", {})
    compatibility_text = "current corpus" if current_corpus else "archived prior corpus; current rerun required"
    print(
        f"LLM neural benchmark ({compatibility_text}): recorded pinned models; "
        f"neural_recall_at_10={100 * neural['recall_at_10']:.1f}%; "
        f"hybrid_recall_at_10={100 * report_summary['hybrid']['recall_at_10']:.1f}%; "
        f"reranked_recall_at_10={100 * reranked.get('recall_at_10', 0.0):.1f}%; "
        f"candidate_status={report.get('status')} (negative results retained)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
