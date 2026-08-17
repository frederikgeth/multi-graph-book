#!/usr/bin/env python3
"""Benchmark an explicitly pinned neural embedder against corpus baselines.

This is intentionally a separate, opt-in benchmark.  The release-safe
dependency-free evaluation remains deterministic on a fresh checkout; this
command adds neural metrics only when the caller supplies a pinned model and
complete artifact provenance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from pathlib import Path

from evaluate_llm_retrieval import RAW_LIMIT, ROOT, recall, reciprocal_rank
from llm_embeddings import (
    CrossEncoderReranker,
    EmbeddingConfig,
    EmbeddingConfigurationError,
    EmbeddingRuntimeError,
    SentenceTransformerEmbeddings,
)
from llm_retrieval import CorpusIndex, record_ids

HELDOUT = ROOT / "llm/heldout-paraphrases.toml"
SCHEMA_VERSION = "0.1.0"
BASE_METHODS = ("lexical", "char_tfidf", "hybrid", "neural")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def retrieve(
    index: CorpusIndex, method: str, question: str, embedder, reranker, limit: int
) -> list[str]:
    evidence_types = {"claim_bundle", "concept_bundle"}
    if method == "lexical":
        results = index.search(question, limit=limit, record_types=evidence_types)
    elif method == "char_tfidf":
        results = index.search_char_tfidf(question, limit=limit, record_types=evidence_types)
    elif method == "hybrid":
        results = index.search_hybrid(question, limit=limit, record_types=evidence_types)
    elif method == "neural":
        results = index.search_neural(question, embedder, limit=limit, record_types=evidence_types)
    elif method == "hybrid_reranked":
        results = index.search_reranked(
            question, reranker, base_method="hybrid", limit=limit,
            candidate_limit=max(limit * 4, 40), record_types=evidence_types,
        )
    else:
        raise ValueError(f"unknown benchmark method: {method}")
    return record_ids(results)


def summarize(rows: list[dict], methods: tuple[str, ...]) -> dict:
    count = len(rows)
    summary = {}
    for method in methods:
        summary[method] = {
            "recall_at_5": round(sum(row[method]["recall_at_5"] for row in rows) / count, 6),
            "recall_at_10": round(sum(row[method]["recall_at_10"] for row in rows) / count, 6),
            "complete_at_10": round(sum(row[method]["complete_at_10"] for row in rows) / count, 6),
            "mean_reciprocal_rank_at_20": round(
                sum(row[method]["mean_reciprocal_rank_at_20"] for row in rows) / count, 6
            ),
        }
    summary["cases"] = count
    for method in methods[1:]:
        summary[f"{method}_recall_at_10_minus_lexical"] = round(
            summary[method]["recall_at_10"] - summary["lexical"]["recall_at_10"], 6
        )
    if "neural" in summary:
        summary["neural_recall_at_10_minus_hybrid"] = round(
            summary["neural"]["recall_at_10"] - summary["hybrid"]["recall_at_10"], 6
        )
        summary["neural_complete_at_10_minus_hybrid"] = round(
            summary["neural"]["complete_at_10"] - summary["hybrid"]["complete_at_10"], 6
        )
    if "hybrid_reranked" in summary:
        summary["hybrid_reranked_recall_at_10_minus_hybrid"] = round(
            summary["hybrid_reranked"]["recall_at_10"] - summary["hybrid"]["recall_at_10"], 6
        )
        summary["hybrid_reranked_complete_at_10_minus_hybrid"] = round(
            summary["hybrid_reranked"]["complete_at_10"] - summary["hybrid"]["complete_at_10"], 6
        )
    return summary


def benchmark(embedder: SentenceTransformerEmbeddings, reranker: CrossEncoderReranker | None = None) -> dict:
    index = CorpusIndex()
    benchmark_methods = BASE_METHODS + (("hybrid_reranked",) if reranker else ())
    cases = tomllib.loads(HELDOUT.read_text()).get("case", [])
    rows = []
    for case in cases:
        expected = {
            *{f"claim:{claim_id}" for claim_id in case["expected_claim_ids"]},
            *{f"concept:{concept_id}" for concept_id in case["expected_concept_ids"]},
        }
        method_results = {}
        for method in benchmark_methods:
            ids = retrieve(index, method, case["question"], embedder, reranker, RAW_LIMIT)
            method_results[method] = {
                "top_10": ids[:10],
                "recall_at_5": recall(expected, ids[:5]),
                "recall_at_10": recall(expected, ids[:10]),
                "complete_at_10": expected <= set(ids[:10]),
                "mean_reciprocal_rank_at_20": reciprocal_rank(expected, ids[:RAW_LIMIT]),
            }
        rows.append(
            {
                "case_id": case["case_id"],
                "audience": case["audience"],
                "question": case["question"],
                "expected_record_ids": sorted(expected),
                **method_results,
            }
        )

    summary = summarize(rows, benchmark_methods)
    threshold_results = {
        "neural_provenance_complete": bool(embedder.provenance()["artifact_hash_complete"]),
        "neural_recall_at_10_not_worse_than_hybrid": summary["neural_recall_at_10_minus_hybrid"] >= 0.0,
        "neural_complete_at_10_not_worse_than_hybrid": summary["neural_complete_at_10_minus_hybrid"] >= 0.0,
    }
    if reranker:
        threshold_results.update(
            {
                "reranker_provenance_complete": bool(reranker.provenance()["artifact_hash_complete"]),
                "hybrid_reranked_recall_at_10_not_worse_than_hybrid": summary[
                    "hybrid_reranked_recall_at_10_minus_hybrid"
                ] >= 0.0,
                "hybrid_reranked_complete_at_10_not_worse_than_hybrid": summary[
                    "hybrid_reranked_complete_at_10_minus_hybrid"
                ] >= 0.0,
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if all(threshold_results.values()) else "fail",
        "purpose": "Compare an explicitly pinned neural embedder with the committed retrieval baselines.",
        "corpus": {
            "corpus_id": index.manifest["corpus_id"],
            "corpus_sha256": index.manifest["corpus_sha256"],
            "release": index.manifest["release"],
            "record_count": index.manifest["record_count"],
        },
        "embedding_provenance": embedder.provenance(),
        "reranker_provenance": reranker.provenance() if reranker else None,
        "inputs": {
            "heldout_paraphrases": {
                "path": "llm/heldout-paraphrases.toml",
                "sha256": sha256(HELDOUT),
            }
        },
        "methods": {
            "lexical": "BM25 lexical retrieval with controlled vocabulary expansion",
            "char_tfidf": "character n-gram TF-IDF surface-semantic proxy",
            "hybrid": "reciprocal-rank fusion of lexical and character TF-IDF",
            "neural": "cosine similarity over sentence-transformers embeddings",
            "hybrid_reranked": "cross-encoder reranking of the bounded hybrid candidate set",
        },
        "thresholds": threshold_results,
        "summary": summary,
        "cases": rows,
    }


def markdown_report(result: dict) -> str:
    summary = result["summary"]
    provenance = result["embedding_provenance"]
    lines = [
        "# Neural LLM retrieval benchmark",
        "",
        f"**Status:** `{result['status']}`",
        f"**Corpus:** `{result['corpus']['corpus_id']}`",
        f"**Model:** `{provenance['model_id']}` at revision `{provenance['model_revision']}`",
        f"**Embedding artifact hash:** `{provenance['artifact_sha256']}`",
        "",
        "This report is an opt-in comparison. It does not promote neural retrieval into the release path",
        "or prove answer faithfulness; it measures only held-out evidence-record retrieval.",
        "",
        "| Method | Recall@5 | Recall@10 | Complete@10 | MRR@20 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for method in ("lexical", "char_tfidf", "hybrid", "neural", "hybrid_reranked"):
        if method not in result["summary"]:
            continue
        metrics = summary[method]
        lines.append(
            f"| `{method}` | {100 * metrics['recall_at_5']:.1f}% | {100 * metrics['recall_at_10']:.1f}% | "
            f"{100 * metrics['complete_at_10']:.1f}% | {metrics['mean_reciprocal_rank_at_20']:.3f} |"
        )
    lines += [
        "",
        f"Neural minus hybrid recall@10: **{100 * summary['neural_recall_at_10_minus_hybrid']:.1f}%**.",
        f"Neural minus hybrid complete@10: **{100 * summary['neural_complete_at_10_minus_hybrid']:.1f}%**.",
    ]
    if result.get("reranker_provenance"):
        reranker = result["reranker_provenance"]
        lines += [
            f"**Reranker:** `{reranker['model_id']}` at revision `{reranker['model_revision']}`.",
            f"**Reranker artifact hash:** `{reranker['artifact_sha256']}`.",
            f"Hybrid-reranked minus hybrid recall@10: **{100 * summary['hybrid_reranked_recall_at_10_minus_hybrid']:.1f}%**.",
            f"Hybrid-reranked minus hybrid complete@10: **{100 * summary['hybrid_reranked_complete_at_10_minus_hybrid']:.1f}%**.",
        ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True, help="immutable model revision or commit hash")
    parser.add_argument("--model-path", help="local model bundle; its tree is hashed when no hash is supplied")
    parser.add_argument("--artifact-sha256", help="SHA-256 of the exact model artifact/cache bundle")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--reranker-model-id")
    parser.add_argument("--reranker-revision")
    parser.add_argument("--reranker-model-path")
    parser.add_argument("--reranker-artifact-sha256")
    parser.add_argument("--reranker-max-length", type=int, default=512)
    parser.add_argument("--output", type=Path, help="optional JSON report path")
    args = parser.parse_args()
    try:
        config = EmbeddingConfig(
            model_id=args.model_id,
            revision=args.revision,
            device=args.device,
            artifact_sha256=args.artifact_sha256,
            model_path=args.model_path,
            local_files_only=args.local_files_only,
        ).validated()
        if not config.model_path and not config.artifact_sha256:
            raise EmbeddingConfigurationError(
                "remote neural benchmarks require --artifact-sha256; use --model-path to hash a local bundle"
            )
        embedder = SentenceTransformerEmbeddings(config)
        reranker = None
        reranker_args = (
            args.reranker_model_id, args.reranker_revision,
            args.reranker_model_path, args.reranker_artifact_sha256,
        )
        if any(value is not None for value in reranker_args):
            if not args.reranker_model_id or not args.reranker_revision:
                raise EmbeddingConfigurationError(
                    "reranker configuration requires --reranker-model-id and --reranker-revision"
                )
            reranker_config = EmbeddingConfig(
                model_id=args.reranker_model_id,
                revision=args.reranker_revision,
                device=args.device,
                artifact_sha256=args.reranker_artifact_sha256,
                model_path=args.reranker_model_path,
                local_files_only=args.local_files_only,
            ).validated()
            if not reranker_config.model_path and not reranker_config.artifact_sha256:
                raise EmbeddingConfigurationError(
                    "remote reranker benchmarks require --reranker-artifact-sha256; "
                    "use --reranker-model-path to hash a local bundle"
                )
            reranker = CrossEncoderReranker(reranker_config, max_length=args.reranker_max_length)
        result = benchmark(embedder, reranker=reranker)
    except (EmbeddingConfigurationError, EmbeddingRuntimeError, OSError, ValueError, KeyError) as error:
        print(f"neural retrieval benchmark failed: {error}", file=sys.stderr)
        return 1

    json_text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    markdown_text = markdown_report(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json_text)
        args.output.with_suffix(".md").write_text(markdown_text)
        print(f"wrote {args.output} and {args.output.with_suffix('.md')}")
    else:
        print(json_text, end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
