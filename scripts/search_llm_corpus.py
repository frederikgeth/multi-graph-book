#!/usr/bin/env python3
"""Search the book corpus or emit a qualification-aware context packet."""

from __future__ import annotations

import argparse
import json
import sys

from llm_embeddings import EmbeddingConfig, EmbeddingRuntimeError, SentenceTransformerEmbeddings
from llm_retrieval import AUDIENCES, CorpusIndex


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="question or search phrase")
    parser.add_argument("--audience", choices=sorted(AUDIENCES), default="student")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--context-packet", action="store_true")
    parser.add_argument(
        "--method",
        choices=["lexical", "char_tfidf", "hybrid", "neural", "graph"],
        default="hybrid",
        help="ranking method; neural requires the optional pinned model arguments",
    )
    parser.add_argument("--neural-model-id", help="sentence-transformers model ID")
    parser.add_argument("--neural-revision", help="immutable model revision or commit hash")
    parser.add_argument("--neural-model-path", help="local sentence-transformers model bundle")
    parser.add_argument("--neural-artifact-sha256", help="SHA-256 of the exact model artifact/cache bundle")
    parser.add_argument("--neural-device", default="cpu")
    parser.add_argument("--neural-local-files-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")

    try:
        index = CorpusIndex()
        embedder = None
        if args.method == "neural":
            if not args.neural_model_id or not args.neural_revision:
                parser.error("--method neural requires --neural-model-id and --neural-revision")
            embedder = SentenceTransformerEmbeddings(
                EmbeddingConfig(
                    model_id=args.neural_model_id,
                    revision=args.neural_revision,
                    device=args.neural_device,
                    artifact_sha256=args.neural_artifact_sha256,
                    model_path=args.neural_model_path,
                    local_files_only=args.neural_local_files_only,
                )
            )
        if args.context_packet:
            payload = index.context_packet(
                args.query, args.audience, supporting_limit=args.limit, method=args.method, embedder=embedder
            )
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0
        if args.method == "lexical":
            results = index.search(args.query, limit=args.limit)
        elif args.method == "char_tfidf":
            results = index.search_char_tfidf(args.query, limit=args.limit)
        elif args.method == "hybrid":
            results = index.search_hybrid(args.query, limit=args.limit)
        elif args.method == "graph":
            results = index.search_graph(args.query, limit=args.limit)
        else:
            results = index.search_neural(args.query, embedder, limit=args.limit)
    except (OSError, ValueError, KeyError, json.JSONDecodeError, EmbeddingRuntimeError) as error:
        print(f"search failed: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps([result.as_dict() for result in results], indent=2, ensure_ascii=False))
        return 0
    routes = index.route_misconceptions(args.query)
    if routes:
        route = routes[0]
        print(f"ranking method: {args.method}")
        print(f"qualification route: {route['misconception_id']} ({route['score']:.3f})")
    for position, result in enumerate(results, start=1):
        anchor = result.source.get("anchor", "")
        location = result.source["path"] + (f"#{anchor}" if anchor else "")
        print(f"{position:>2}. {result.score:8.4f}  {result.record_id}")
        print(f"    {result.title}")
        print(f"    {location}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
