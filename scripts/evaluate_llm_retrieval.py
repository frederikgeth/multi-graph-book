#!/usr/bin/env python3
"""Evaluate lexical and contract-aware retrieval over the curated question set."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

from llm_retrieval import CorpusIndex, ROOT, record_ids

EVALUATIONS = ROOT / "llm/evaluation-cases.toml"
HELDOUT = ROOT / "llm/heldout-paraphrases.toml"
MISCONCEPTIONS = ROOT / "llm/misconceptions.toml"
CONTEXT_SCHEMA = ROOT / "schemas/llm-context-packet.schema.json"
JSON_OUTPUT = ROOT / "llm/generated/retrieval-evaluation.json"
MARKDOWN_OUTPUT = ROOT / "llm/generated/retrieval-evaluation.md"
SCHEMA_VERSION = "0.1.0"
RAW_LIMIT = 20
REPORT_LIMIT = 10
HELDOUT_ROUTER_FIRED_MIN = 2 / 3


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ratio(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def recall(expected: set[str], observed: list[str]) -> float:
    return ratio(len(expected & set(observed)), len(expected))


def reciprocal_rank(expected: set[str], observed: list[str]) -> float:
    values = []
    for record_id in expected:
        try:
            values.append(1.0 / (observed.index(record_id) + 1))
        except ValueError:
            values.append(0.0)
    return round(sum(values) / len(values), 6) if values else 0.0


def validate_packet_shape(packet: dict, schema: dict) -> list[str]:
    errors = []
    required = schema.get("required", [])
    for field in required:
        if field not in packet:
            errors.append(f"missing packet field {field}")
    allowed_status = set(schema["properties"]["status"]["enum"])
    if packet.get("status") not in allowed_status:
        errors.append("unknown packet status")
    allowed_methods = set(schema["properties"]["retrieval"]["properties"]["method"]["enum"])
    if packet.get("retrieval", {}).get("method") not in allowed_methods:
        errors.append("unknown packet retrieval method")
    if packet.get("schema_version") != SCHEMA_VERSION:
        errors.append("packet schema version drift")
    return errors


def aggregate(rows: list[dict]) -> dict:
    count = len(rows)
    return {
        "cases": count,
        "route_top1_accuracy": ratio(sum(row["route_top1_correct"] for row in rows), count),
        "open_corpus_recall_at_5": ratio(sum(row["open_corpus_recall_at_5"] for row in rows), count),
        "open_corpus_recall_at_10": ratio(sum(row["open_corpus_recall_at_10"] for row in rows), count),
        "open_corpus_complete_at_10": ratio(sum(row["open_corpus_complete_at_10"] for row in rows), count),
        "evidence_only_recall_at_5": ratio(sum(row["evidence_only_recall_at_5"] for row in rows), count),
        "evidence_only_recall_at_10": ratio(sum(row["evidence_only_recall_at_10"] for row in rows), count),
        "evidence_only_complete_at_10": ratio(sum(row["evidence_only_complete_at_10"] for row in rows), count),
        "evidence_only_mean_reciprocal_rank_at_20": ratio(
            sum(row["evidence_only_mean_reciprocal_rank_at_20"] for row in rows), count
        ),
        "contract_record_recall": ratio(sum(row["contract_record_recall"] for row in rows), count),
        "contract_complete_rate": ratio(sum(row["contract_complete"] for row in rows), count),
        "qualification_complete_rate": ratio(sum(row["qualification_complete"] for row in rows), count),
        "release_match_rate": ratio(sum(row["release_match"] for row in rows), count),
        "packet_shape_valid_rate": ratio(sum(row["packet_shape_valid"] for row in rows), count),
    }


def heldout_aggregate(rows: list[dict]) -> dict:
    count = len(rows)
    metrics = {}
    for method in ("lexical", "char_tfidf", "hybrid", "graph"):
        recall_hits = sum(row[f"{method}_hits_at_10"] for row in rows)
        recall_denominator = sum(row["expected_record_count"] for row in rows)
        metrics[method] = {
            "recall_at_5": ratio(sum(row[f"{method}_recall_at_5"] for row in rows), count),
            "recall_at_10": ratio(sum(row[f"{method}_recall_at_10"] for row in rows), count),
            "complete_at_10": ratio(sum(row[f"{method}_complete_at_10"] for row in rows), count),
            "complete_at_10_count": sum(row[f"{method}_complete_at_10"] for row in rows),
            "zero_recall_at_10_count": sum(row[f"{method}_recall_at_10"] == 0 for row in rows),
            "recall_hits_at_10": recall_hits,
            "recall_expected_records_at_10": recall_denominator,
            "mean_reciprocal_rank_at_20": ratio(
                sum(row[f"{method}_mean_reciprocal_rank_at_20"] for row in rows), count
            ),
        }
    metrics["cases"] = count
    target_clusters = defaultdict(int)
    for row in rows:
        target_clusters[tuple(row["expected_record_ids"])] += 1
    metrics["target_cluster_count"] = len(target_clusters)
    metrics["target_cluster_sizes"] = sorted(target_clusters.values())
    metrics["router_fired_count"] = sum(row["route_fired"] for row in rows)
    metrics["router_fired_rate"] = ratio(metrics["router_fired_count"], count)
    metrics["router_top1_correct_count"] = sum(row["route_top1_correct"] for row in rows)
    metrics["router_top1_accuracy"] = ratio(metrics["router_top1_correct_count"], count)
    metrics["hybrid_recall_at_10_minus_lexical"] = round(
        metrics["hybrid"]["recall_at_10"] - metrics["lexical"]["recall_at_10"], 6
    )
    metrics["hybrid_complete_at_10_minus_lexical"] = round(
        metrics["hybrid"]["complete_at_10"] - metrics["lexical"]["complete_at_10"], 6
    )
    return metrics


def evaluate_heldout(index: CorpusIndex) -> tuple[list[dict], dict]:
    cases = tomllib.loads(HELDOUT.read_text()).get("case", [])
    expected_contracts = {}
    for misconception in index.misconceptions:
        key = tuple(sorted(
            [f"claim:{claim_id}" for claim_id in misconception["mandatory_claim_ids"]]
            + [f"concept:{concept_id}" for concept_id in misconception["mandatory_concept_ids"]]
        ))
        if key in expected_contracts:
            raise ValueError("misconception contracts have duplicate mandatory evidence sets")
        expected_contracts[key] = misconception["id"]
    rows = []
    evidence_types = {"claim_bundle", "concept_bundle"}
    seen_case_ids = set()
    for case in cases:
        if case["case_id"] in seen_case_ids:
            raise ValueError(f"duplicate held-out case ID: {case['case_id']}")
        seen_case_ids.add(case["case_id"])
        expected = {
            *{f"claim:{claim_id}" for claim_id in case["expected_claim_ids"]},
            *{f"concept:{concept_id}" for concept_id in case["expected_concept_ids"]},
        }
        unknown_records = expected - set(index.by_id)
        if unknown_records:
            raise ValueError(f"{case['case_id']} names unknown corpus records: {sorted(unknown_records)}")
        expected_misconception_id = expected_contracts.get(tuple(sorted(expected)))
        if expected_misconception_id is None:
            raise ValueError(f"{case['case_id']} does not map to a unique misconception contract")
        if case["audience"] not in {"student", "software_engineer", "power_engineer"}:
            raise ValueError(f"{case['case_id']} has an unknown audience")
        routes = index.route_misconceptions(case["question"])
        route_top1 = routes[0]["misconception_id"] if routes else ""
        method_results = {}
        for method in ("lexical", "char_tfidf", "hybrid", "graph"):
            if method == "lexical":
                results = index.search(case["question"], limit=RAW_LIMIT, record_types=evidence_types)
            elif method == "char_tfidf":
                results = index.search_char_tfidf(case["question"], limit=RAW_LIMIT, record_types=evidence_types)
            elif method == "hybrid":
                results = index.search_hybrid(case["question"], limit=RAW_LIMIT, record_types=evidence_types)
            else:
                results = index.search_graph(case["question"], limit=RAW_LIMIT, record_types=evidence_types)
            ids = record_ids(results)
            method_results[method] = {
                "top_10": ids[:REPORT_LIMIT],
                "recall_at_5": recall(expected, ids[:5]),
                "recall_at_10": recall(expected, ids[:10]),
                "hits_at_10": len(expected & set(ids[:10])),
                "complete_at_10": expected <= set(ids[:10]),
                "mean_reciprocal_rank_at_20": reciprocal_rank(expected, ids[:RAW_LIMIT]),
            }
        rows.append(
            {
                "case_id": case["case_id"],
                "audience": case["audience"],
                "question": case["question"],
                "expected_misconception_id": expected_misconception_id,
                "route_top1": route_top1,
                "route_fired": bool(routes),
                "route_top1_correct": route_top1 == expected_misconception_id,
                "expected_record_count": len(expected),
                "expected_record_ids": sorted(expected),
                **{
                    f"{method}_{metric}": value
                    for method, values in method_results.items()
                    for metric, value in values.items()
                    if metric != "top_10"
                },
                **{f"{method}_top_10": values["top_10"] for method, values in method_results.items()},
            }
        )
    return rows, heldout_aggregate(rows)


def evaluate() -> dict:
    index = CorpusIndex()
    cases = tomllib.loads(EVALUATIONS.read_text()).get("case", [])
    misconceptions = {
        item["id"]: item
        for item in tomllib.loads(MISCONCEPTIONS.read_text()).get("misconception", [])
    }
    context_schema = json.loads(CONTEXT_SCHEMA.read_text())
    rows = []
    for case in cases:
        expected_claims = {f"claim:{claim_id}" for claim_id in case["required_claim_ids"]}
        expected_concepts = {f"concept:{concept_id}" for concept_id in case["required_concept_ids"]}
        expected = expected_claims | expected_concepts
        open_results = index.search(case["question"], limit=RAW_LIMIT)
        evidence_results = index.search(
            case["question"], limit=RAW_LIMIT, record_types={"claim_bundle", "concept_bundle"}
        )
        open_ids = record_ids(open_results)
        evidence_ids = record_ids(evidence_results)
        routes = index.route_misconceptions(case["question"])
        route_id = routes[0]["misconception_id"] if routes else ""
        packet = index.context_packet(case["question"], case["audience"], method="hybrid")
        mandatory_ids = [record["record_id"] for record in packet["mandatory_records"]]
        contract_recall = recall(expected, mandatory_ids)
        packet_errors = validate_packet_shape(packet, context_schema)
        qualification_complete = bool(
            packet["answer_contract"]["required_qualifications"]
            and packet["answer_contract"]["failure_consequences"]
            and packet["answer_contract"]["safe_shorthand"]
            and packet["answer_contract"]["scope_and_assumptions"]
        )
        row = {
            "case_id": case["case_id"],
            "audience": case["audience"],
            "misconception_id": case["misconception_id"],
            "question": case["question"],
            "expected_record_ids": sorted(expected),
            "route_top1": route_id,
            "route_score": routes[0]["score"] if routes else 0.0,
            "route_top1_correct": route_id == case["misconception_id"],
            "open_corpus_top_10": open_ids[:REPORT_LIMIT],
            "open_corpus_recall_at_5": recall(expected, open_ids[:5]),
            "open_corpus_recall_at_10": recall(expected, open_ids[:10]),
            "open_corpus_complete_at_10": expected <= set(open_ids[:10]),
            "evidence_only_top_10": evidence_ids[:REPORT_LIMIT],
            "evidence_only_recall_at_5": recall(expected, evidence_ids[:5]),
            "evidence_only_recall_at_10": recall(expected, evidence_ids[:10]),
            "evidence_only_complete_at_10": expected <= set(evidence_ids[:10]),
            "evidence_only_mean_reciprocal_rank_at_20": reciprocal_rank(expected, evidence_ids[:20]),
            "contract_record_ids": mandatory_ids,
            "contract_record_recall": contract_recall,
            "contract_complete": expected <= set(mandatory_ids),
            "qualification_complete": qualification_complete,
            "release_match": packet["release"] == index.manifest["release"],
            "packet_shape_valid": not packet_errors,
            "packet_shape_errors": packet_errors,
            "forbidden_simplifications": case["forbidden_simplifications"],
            "severity": misconceptions[case["misconception_id"]]["severity"],
        }
        rows.append(row)

    summary = aggregate(rows)
    heldout_rows, heldout_summary = evaluate_heldout(index)
    by_audience = {
        audience: aggregate([row for row in rows if row["audience"] == audience])
        for audience in sorted({row["audience"] for row in rows})
    }
    by_misconception = {
        misconception_id: aggregate([row for row in rows if row["misconception_id"] == misconception_id])
        for misconception_id in sorted({row["misconception_id"] for row in rows})
    }
    thresholds = {
        "route_top1_accuracy": 1.0,
        "contract_record_recall": 1.0,
        "contract_complete_rate": 1.0,
        "qualification_complete_rate": 1.0,
        "release_match_rate": 1.0,
        "packet_shape_valid_rate": 1.0,
    }
    threshold_results = {
        metric: summary[metric] >= threshold
        for metric, threshold in thresholds.items()
    }
    thresholds["heldout_hybrid_recall_not_worse"] = 0.0
    threshold_results["heldout_hybrid_recall_not_worse"] = (
        heldout_summary["hybrid_recall_at_10_minus_lexical"] >= 0.0
    )
    thresholds["heldout_router_fired_rate"] = HELDOUT_ROUTER_FIRED_MIN
    threshold_results["heldout_router_fired_rate"] = (
        heldout_summary["router_fired_rate"] >= HELDOUT_ROUTER_FIRED_MIN
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "evaluation_id": f"retrieval-{index.manifest['corpus_id']}",
        "status": "pass" if all(threshold_results.values()) else "fail",
        "method": {
            "ranker": "BM25 lexical retrieval with controlled vocabulary expansion",
            "surface_semantic_proxy": "character n-gram TF-IDF over weighted titles, identifiers, and records",
            "hybrid": "reciprocal-rank fusion of BM25 and character n-gram TF-IDF",
            "graph": "benchmark-only provenance graph traversal from lexical and surface seeds",
            "router": "curated misconception-pattern routing without evaluation labels at query time",
            "contract_expansion": "mandatory claim and concept records from the detected misconception contract",
            "raw_limit": RAW_LIMIT,
            "report_limit": REPORT_LIMIT,
            "neural_embeddings": "not_implemented; no embedding model is bundled in this environment",
            "note": "Raw ranking metrics remain diagnostic; contract expansion is evaluated separately and cannot improve those scores.",
        },
        "corpus": {
            "corpus_id": index.manifest["corpus_id"],
            "corpus_sha256": index.manifest["corpus_sha256"],
            "record_count": index.manifest["record_count"],
            "release": index.manifest["release"],
        },
        "inputs": {
            "evaluation_cases": {"path": "llm/evaluation-cases.toml", "sha256": sha256(EVALUATIONS)},
            "heldout_paraphrases": {"path": "llm/heldout-paraphrases.toml", "sha256": sha256(HELDOUT)},
            "misconceptions": {"path": "llm/misconceptions.toml", "sha256": sha256(MISCONCEPTIONS)},
            "context_packet_schema": {"path": "schemas/llm-context-packet.schema.json", "sha256": sha256(CONTEXT_SCHEMA)},
        },
        "thresholds": thresholds,
        "threshold_results": threshold_results,
        "summary": summary,
        "by_audience": by_audience,
        "by_misconception": by_misconception,
        "cases": rows,
        "heldout": {
            "purpose": tomllib.loads(HELDOUT.read_text()).get("purpose", ""),
            "summary": heldout_summary,
            "cases": heldout_rows,
        },
    }


def percent(value: float) -> str:
    return f"{100.0 * value:.1f}%"


def markdown_report(result: dict) -> str:
    summary = result["summary"]
    heldout_summary = result["heldout"]["summary"]
    lines = [
        "# LLM retrieval evaluation",
        "",
        "**Generated report:** deterministic evaluation of the committed corpus and question contracts.",
        "",
        f"**Status:** `{result['status']}`<br>",
        f"**Corpus:** `{result['corpus']['corpus_id']}`<br>",
        f"**Corpus hash:** `{result['corpus']['corpus_sha256']}`<br>",
        f"**Cases:** {summary['cases']}",
        "",
        "This report separates ordinary lexical ranking from qualification-aware contract expansion.",
        "The latter is permitted to add mandatory claims and concepts only after the query router identifies",
        "a curated dangerous-shortcut contract. The character n-gram path is a reproducible surface-semantic proxy; neural embeddings are not bundled in this baseline. Graph traversal is diagnostic only and is not enabled by the production service.",
        "",
        "## Summary",
        "",
        "| Measure | Result | Release gate? |",
        "| --- | ---: | --- |",
        f"| Misconception top-1 routing accuracy | {percent(summary['route_top1_accuracy'])} | yes |",
        f"| Open-corpus lexical evidence recall@5 | {percent(summary['open_corpus_recall_at_5'])} | diagnostic |",
        f"| Open-corpus lexical evidence recall@10 | {percent(summary['open_corpus_recall_at_10'])} | diagnostic |",
        f"| Open-corpus complete evidence@10 | {percent(summary['open_corpus_complete_at_10'])} | diagnostic |",
        f"| Evidence-only lexical recall@5 | {percent(summary['evidence_only_recall_at_5'])} | diagnostic |",
        f"| Evidence-only lexical recall@10 | {percent(summary['evidence_only_recall_at_10'])} | diagnostic |",
        f"| Evidence-only complete evidence@10 | {percent(summary['evidence_only_complete_at_10'])} | diagnostic |",
        f"| Contract-expanded mandatory-record recall | {percent(summary['contract_record_recall'])} | yes |",
        f"| Complete contract packets | {percent(summary['contract_complete_rate'])} | yes |",
        f"| Packets with qualification, failure, shorthand, and scope | {percent(summary['qualification_complete_rate'])} | yes |",
        f"| Corpus-release identity agreement | {percent(summary['release_match_rate'])} | yes |",
        f"| Held-out contract-router firing | {heldout_summary['router_fired_count']}/{heldout_summary['cases']} ({percent(heldout_summary['router_fired_rate'])}) | yes |",
        f"| Held-out expected-contract top-1 | {heldout_summary['router_top1_correct_count']}/{heldout_summary['cases']} ({percent(heldout_summary['router_top1_accuracy'])}) | diagnostic |",
        f"| Held-out hybrid zero-recall@10 cases | {heldout_summary['hybrid']['zero_recall_at_10_count']}/{heldout_summary['cases']} | diagnostic |",
        "",
        "The diagnostic lexical scores are intentionally not release thresholds. A perfect contract score",
        "cannot be reported as a better ranker score: it measures whether an identified high-risk question",
        "received all evidence mandated by the curated contract.",
        "",
        "## Held-out paraphrase benchmark",
        "",
        "These questions are not used by the contract router during corpus construction. They test ordinary",
        "retrieval and routing generalization against synthetic paraphrases across the three audiences.",
        "They are not human-validated evidence: 27 cases are three audience phrasings for nine target",
        "evidence sets, so the effective target count is nine rather than 27 independent questions.",
        "",
        "| Method | Recall@5 | Recall@10 | Complete@10 | Complete cases | Zero-recall cases | MRR@20 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method in ("lexical", "char_tfidf", "hybrid", "graph"):
        metrics = heldout_summary[method]
        lines.append(
            f"| `{method}` | {percent(metrics['recall_at_5'])} | {percent(metrics['recall_at_10'])} | "
            f"{percent(metrics['complete_at_10'])} | {metrics['complete_at_10_count']}/{heldout_summary['cases']} | "
            f"{metrics['zero_recall_at_10_count']}/{heldout_summary['cases']} | "
            f"{metrics['mean_reciprocal_rank_at_20']:.3f} |"
        )
    lines += [
        "",
        f"Held-out contract-router firing: **{heldout_summary['router_fired_count']}/{heldout_summary['cases']} "
        f"({percent(heldout_summary['router_fired_rate'])})**; release floor: **{percent(HELDOUT_ROUTER_FIRED_MIN)}**.",
        f"Expected-contract top-1 agreement: **{heldout_summary['router_top1_correct_count']}/{heldout_summary['cases']} "
        f"({percent(heldout_summary['router_top1_accuracy'])})**; this remains diagnostic because the set is synthetic and clustered.",
        f"Target clusters: **{heldout_summary['target_cluster_count']}**, with cluster sizes "
        f"`{heldout_summary['target_cluster_sizes']}`; percentage differences are therefore not independent observations.",
        f"Hybrid versus lexical complete@10: **{heldout_summary['hybrid']['complete_at_10_count']}/"
        f"{heldout_summary['cases']}** versus **{heldout_summary['lexical']['complete_at_10_count']}/"
        f"{heldout_summary['cases']}**; hybrid zero-recall@10: **{heldout_summary['hybrid']['zero_recall_at_10_count']}/"
        f"{heldout_summary['cases']}**.",
        f"Graph versus hybrid complete@10: **{heldout_summary['graph']['complete_at_10_count']}/"
        f"{heldout_summary['cases']}** versus **{heldout_summary['hybrid']['complete_at_10_count']}/"
        f"{heldout_summary['cases']}**.",
        "",
        "| Held-out case | Audience | Expected route | Observed top-1 | Router fired | Lexical complete@10 | TF-IDF complete@10 | Hybrid complete@10 | Graph complete@10 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in result["heldout"]["cases"]:
        lines.append(
            f"| `{row['case_id']}` | `{row['audience']}` | `{row['expected_misconception_id']}` | "
            f"`{row['route_top1'] or 'none'}` | "
            f"{'yes' if row['route_fired'] else 'no'} | "
            f"{'yes' if row['lexical_complete_at_10'] else 'no'} | "
            f"{'yes' if row['char_tfidf_complete_at_10'] else 'no'} | "
            f"{'yes' if row['hybrid_complete_at_10'] else 'no'} | "
            f"{'yes' if row['graph_complete_at_10'] else 'no'} |"
        )
    lines += [
        "",
        "## Audience consistency",
        "",
        "| Audience | Cases | Route top-1 | Lexical recall@10 | Contract recall |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for audience, metrics in result["by_audience"].items():
        lines.append(
            f"| `{audience}` | {metrics['cases']} | {percent(metrics['route_top1_accuracy'])} | "
            f"{percent(metrics['evidence_only_recall_at_10'])} | {percent(metrics['contract_record_recall'])} |"
        )
    lines += [
        "",
        "## Case results",
        "",
        "| Case | Audience | Route | Evidence-only recall@10 | Contract complete |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in result["cases"]:
        lines.append(
            f"| `{row['case_id']}` | `{row['audience']}` | `{row['route_top1']}` | "
            f"{percent(row['evidence_only_recall_at_10'])} | {'yes' if row['contract_complete'] else 'no'} |"
        )
    lines += [
        "",
        "## Interpretation and next boundary",
        "",
        "This baseline proves deterministic corpus search, high-risk query routing, and complete context-packet",
        "assembly for the current curated cases. It does not prove robust paraphrase coverage outside the test",
        "set, answer-generation faithfulness, citation correctness in generated prose, neural embedding retrieval quality,",
        "or human-calibrated audience translation. Those remain separate roadmap gates.",
        "",
    ]
    return "\n".join(lines)


def payloads() -> tuple[str, str, dict]:
    result = evaluate()
    json_text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    return json_text, markdown_report(result), result


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        json_text, markdown_text, result = payloads()
    except (OSError, ValueError, KeyError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        print(f"LLM retrieval evaluation failed: {error}")
        return 1
    if args.write:
        JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        JSON_OUTPUT.write_text(json_text)
        MARKDOWN_OUTPUT.write_text(markdown_text)
        print(f"wrote {JSON_OUTPUT.relative_to(ROOT)} and {MARKDOWN_OUTPUT.relative_to(ROOT)}")
    else:
        stale = []
        for path, expected in ((JSON_OUTPUT, json_text), (MARKDOWN_OUTPUT, markdown_text)):
            if not path.is_file() or path.read_text() != expected:
                stale.append(path.relative_to(ROOT).as_posix())
        if stale:
            print(f"stale retrieval evaluation outputs: {', '.join(stale)}")
            print("run: python3 scripts/evaluate_llm_retrieval.py --write")
            return 1
    summary = result["summary"]
    print(
        f"LLM retrieval: {summary['cases']} cases; heldout={result['heldout']['summary']['cases']}; "
        f"route_top1={percent(summary['route_top1_accuracy'])}; "
        f"lexical_complete_at_10={percent(summary['evidence_only_complete_at_10'])}; "
        f"contract_complete={percent(summary['contract_complete_rate'])}; "
        f"heldout_hybrid_recall_at_10={percent(result['heldout']['summary']['hybrid']['recall_at_10'])}; "
        f"heldout_router_fired={percent(result['heldout']['summary']['router_fired_rate'])}; "
        f"heldout_hybrid_zero_recall_at_10={result['heldout']['summary']['hybrid']['zero_recall_at_10_count']}/"
        f"{result['heldout']['summary']['cases']}; {result['status']}"
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
