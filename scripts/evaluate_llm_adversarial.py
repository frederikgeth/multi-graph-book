#!/usr/bin/env python3
"""Evaluate adversarial retrieval, qualification routing, and abstention."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from pathlib import Path

from llm_retrieval import CorpusIndex, ROOT, record_ids
from llm_service import BookLLMService

CASES = ROOT / "llm/adversarial-cases.toml"
JSON_OUTPUT = ROOT / "llm/generated/adversarial-evaluation.json"
MARKDOWN_OUTPUT = ROOT / "llm/generated/adversarial-evaluation.md"
RAW_LIMIT = 20


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recall(expected: set[str], observed: list[str]) -> float:
    return round(len(expected & set(observed)) / len(expected), 6) if expected else 1.0


def evaluate() -> dict:
    index = CorpusIndex()
    service = BookLLMService(index)
    cases = tomllib.loads(CASES.read_text()).get("case", [])
    rows = []
    for case in cases:
        expected = {
            *{f"claim:{item}" for item in case["expected_claim_ids"]},
            *{f"concept:{item}" for item in case["expected_concept_ids"]},
        }
        methods = {}
        evidence_types = {"claim_bundle", "concept_bundle"}
        for method in ("lexical", "hybrid", "graph"):
            if method == "lexical":
                results = index.search(case["question"], RAW_LIMIT, evidence_types)
            elif method == "hybrid":
                results = index.search_hybrid(case["question"], RAW_LIMIT, evidence_types)
            else:
                results = index.search_graph(case["question"], RAW_LIMIT, evidence_types)
            ids = record_ids(results)
            methods[method] = {
                "top_10": ids[:10],
                "recall_at_10": recall(expected, ids[:10]),
                "complete_at_10": expected <= set(ids[:10]),
            }
        response = service.response(case["question"], case["audience"])
        packet = response["packet"]
        mandatory_ids = [item["record_id"] for item in packet["mandatory_records"]]
        rows.append(
            {
                "case_id": case["case_id"],
                "audience": case["audience"],
                "question": case["question"],
                "expected_status": case["expected_status"],
                "observed_status": packet["status"],
                "status_correct": packet["status"] == case["expected_status"],
                "detected_routes": packet["retrieval"]["detected_misconceptions"],
                "expected_record_ids": sorted(expected),
                "mandatory_record_recall": recall(expected, mandatory_ids),
                "contract_complete": expected <= set(mandatory_ids),
                **methods,
            }
        )
    qualified = [row for row in rows if row["expected_status"] == "qualified"]
    unsupported = [row for row in rows if row["expected_status"] == "unsupported"]
    summary = {
        "cases": len(rows),
        "status_accuracy": round(sum(row["status_correct"] for row in rows) / len(rows), 6),
        "qualified_contract_complete": round(
            sum(row["contract_complete"] for row in qualified) / len(qualified), 6
        ),
        "unsupported_abstention_accuracy": round(
            sum(row["status_correct"] for row in unsupported) / len(unsupported), 6
        ),
        "graph_recall_at_10": round(sum(row["graph"]["recall_at_10"] for row in rows) / len(rows), 6),
        "hybrid_recall_at_10": round(sum(row["hybrid"]["recall_at_10"] for row in rows) / len(rows), 6),
    }
    thresholds = {
        "status_accuracy": 1.0,
        "qualified_contract_complete": 1.0,
        "unsupported_abstention_accuracy": 1.0,
    }
    threshold_results = {key: summary[key] >= value for key, value in thresholds.items()}
    manifest = json.loads((ROOT / "llm/generated/corpus-manifest.json").read_text())
    return {
        "schema_version": "0.1.0",
        "status": "pass" if all(threshold_results.values()) else "fail",
        "purpose": tomllib.loads(CASES.read_text()).get("purpose", ""),
        "corpus": {"corpus_id": manifest["corpus_id"], "corpus_sha256": manifest["corpus_sha256"]},
        "inputs": {"adversarial_cases": {"path": "llm/adversarial-cases.toml", "sha256": sha256(CASES)}},
        "thresholds": thresholds,
        "threshold_results": threshold_results,
        "summary": summary,
        "cases": rows,
    }


def markdown_report(result: dict) -> str:
    summary = result["summary"]
    lines = [
        "# Adversarial LLM retrieval evaluation",
        "",
        f"**Status:** `{result['status']}`",
        f"**Cases:** {summary['cases']}",
        "",
        "This is a deterministic robustness and abstention check, not human-calibrated answer-quality evidence.",
        "",
        "| Measure | Result | Gate |",
        "| --- | ---: | --- |",
        f"| Status accuracy | {100 * summary['status_accuracy']:.1f}% | yes |",
        f"| Qualified contract completeness | {100 * summary['qualified_contract_complete']:.1f}% | yes |",
        f"| Unsupported-query abstention | {100 * summary['unsupported_abstention_accuracy']:.1f}% | yes |",
        f"| Hybrid retrieval recall@10 | {100 * summary['hybrid_recall_at_10']:.1f}% | diagnostic |",
        f"| Graph retrieval recall@10 | {100 * summary['graph_recall_at_10']:.1f}% | diagnostic |",
        "",
        "| Case | Expected status | Observed status | Hybrid recall@10 | Graph recall@10 | Contract complete |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in result["cases"]:
        lines.append(
            f"| `{row['case_id']}` | `{row['expected_status']}` | `{row['observed_status']}` | "
            f"{100 * row['hybrid']['recall_at_10']:.1f}% | {100 * row['graph']['recall_at_10']:.1f}% | "
            f"{'yes' if row['contract_complete'] else 'no'} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = evaluate()
    except (OSError, ValueError, KeyError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        print(f"adversarial evaluation failed: {error}")
        return 1
    json_text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    markdown_text = markdown_report(result)
    if args.write:
        JSON_OUTPUT.write_text(json_text)
        MARKDOWN_OUTPUT.write_text(markdown_text)
    elif not JSON_OUTPUT.is_file() or JSON_OUTPUT.read_text() != json_text or not MARKDOWN_OUTPUT.is_file() or MARKDOWN_OUTPUT.read_text() != markdown_text:
        print("stale adversarial evaluation outputs; run with --write")
        return 1
    summary = result["summary"]
    print(
        f"LLM adversarial evaluation: {summary['cases']} cases; status={100 * summary['status_accuracy']:.1f}%; "
        f"abstention={100 * summary['unsupported_abstention_accuracy']:.1f}%; "
        f"graph_recall_at_10={100 * summary['graph_recall_at_10']:.1f}%; {result['status']}"
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
