#!/usr/bin/env python3
"""Shared deterministic service for book-grounded LLM access routes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from llm_retrieval import AUDIENCES, CorpusIndex, SearchResult

ROOT = Path(__file__).resolve().parents[1]
API_SCHEMA_VERSION = "0.1.0"
SUPPORTED_METHODS = {"lexical", "char_tfidf", "hybrid", "graph"}
MAX_LIMIT = 20


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_location(source: dict) -> str:
    path = source.get("path", "")
    anchor = source.get("anchor", "")
    return f"{path}#{anchor}" if anchor else path


def result_payload(result: SearchResult) -> dict:
    return result.as_dict()


def validate_context_packet(index: CorpusIndex, packet: dict) -> list[str]:
    """Validate packet identity and source links before exposing it externally."""
    errors: list[str] = []
    if packet.get("release") != index.manifest.get("release"):
        errors.append("context packet release identity differs from the corpus manifest")
    if packet.get("status") == "qualified" and not packet.get("mandatory_records"):
        errors.append("qualified packet has no mandatory records")
    seen_records: set[str] = set()
    all_records = [*packet.get("mandatory_records", []), *packet.get("supporting_records", [])]
    for record in all_records:
        record_id = record.get("record_id", "")
        if record_id in seen_records:
            errors.append(f"duplicate packet record: {record_id}")
        seen_records.add(record_id)
        canonical = index.by_id.get(record_id)
        if canonical is None:
            errors.append(f"packet names an unknown corpus record: {record_id}")
            continue
        source = record.get("source", {})
        path = ROOT / source.get("path", "")
        if not path.is_file():
            errors.append(f"packet source is missing: {source.get('path', '')}")
            continue
        if source.get("sha256") != file_hash(path):
            errors.append(f"packet source hash is stale: {source.get('path', '')}")
        if source != canonical.get("source"):
            errors.append(f"packet source metadata differs from corpus record: {record_id}")
    source_keys = {
        (source.get("path", ""), source.get("anchor", ""))
        for source in packet.get("sources", [])
    }
    for record in all_records:
        source = record.get("source", {})
        if (source.get("path", ""), source.get("anchor", "")) not in source_keys:
            errors.append(f"packet omits source index entry for {record.get('record_id', '')}")
    return errors


def validate_answer_response(index: CorpusIndex, response: dict) -> list[str]:
    """Check claim coverage and citation presence for an externally exposed response."""
    errors = validate_context_packet(index, response.get("packet", {}))
    packet = response.get("packet", {})
    contract = packet.get("answer_contract", {})
    mandatory_claims = {
        record.get("claim", {}).get("claim_id"): record.get("claim", {}).get("claim_text")
        for record in packet.get("mandatory_records", [])
        if record.get("record_type") == "claim_bundle"
    }
    mandatory_scientific_statements = {
        record.get("knowledge", {}).get("scientific_statement")
        for record in packet.get("mandatory_records", [])
        if record.get("record_type") == "scientific_knowledge"
    }
    direct_basis = contract.get("direct_answer_basis", [])
    expected_basis = {
        *{value for value in mandatory_claims.values() if value},
        *{value for value in mandatory_scientific_statements if value},
    }
    if set(direct_basis) != expected_basis:
        errors.append("answer basis does not exactly cover mandatory claim and scientific records")
    scoped_claims = {
        item.get("claim_id") for item in contract.get("scope_and_assumptions", [])
    }
    unresolved_claims = {
        item.get("claim_id") for item in contract.get("unresolved_boundaries", [])
    }
    if not scoped_claims <= set(mandatory_claims):
        errors.append("answer scope names a claim that is not mandatory in the packet")
    if not unresolved_claims <= set(mandatory_claims):
        errors.append("answer boundary names a claim that is not mandatory in the packet")
    markdown = response.get("markdown", "")
    if not markdown.strip():
        errors.append("answer Markdown is empty")
    for source in packet.get("sources", []):
        if source_location(source) not in markdown:
            errors.append(f"answer Markdown omits citation location: {source_location(source)}")
    if response.get("validation", {}).get("source_hashes_checked") is not True:
        errors.append("response does not declare source-hash validation")
    if packet.get("status") in {"under_retrieved", "unsupported"} and not contract.get("retrieval_warning"):
        errors.append("degraded response does not name its retrieval warning")
    return errors


def render_markdown(packet: dict) -> str:
    """Render a non-generative, citation-bearing answer basis for human/LLM use."""
    contract = packet["answer_contract"]
    lines = [
        "# Book-grounded answer packet",
        "",
        f"**Status:** `{packet['status']}`<br>",
        f"**Audience:** `{packet['audience']}`<br>",
        f"**Corpus release:** `{packet['release']['release_candidate_id']}`",
        "",
    ]
    if packet["status"] == "unsupported":
        lines += [
            "The committed resource does not currently provide a qualified answer to this query.",
            "Use the retrieved material only as navigation, and label any external answer separately.",
            "",
        ]
    elif packet["status"] == "under_retrieved":
        lines += [
            "The corpus returned related material, but no qualified claim contract was found.",
            "Do not treat retrieval relevance as a book-supported conclusion; broaden or reformulate the query.",
            "",
        ]
    elif contract["direct_answer_basis"]:
        lines += ["## Book-supported answer basis", ""]
        lines.extend(f"- {claim}" for claim in contract["direct_answer_basis"])
        lines.append("")
    else:
        lines += [
            "The corpus returned supporting material, but no claim bundle supplies a direct answer basis.",
            "Do not turn retrieval relevance into an unsupported conclusion.",
            "",
        ]

    if contract["scope_and_assumptions"]:
        lines += ["## Scope and assumptions", ""]
        for item in contract["scope_and_assumptions"]:
            lines.append(f"- **{item['claim_id']}** — exactness object: `{item['exactness_object']}`")
            lines.append(f"  - Model scope: {item['model_scope']}")
            for assumption in item["assumptions"]:
                lines.append(f"  - Assumption: {assumption}")
        lines.append("")
    if contract["required_qualifications"]:
        lines += ["## Required qualifications", ""]
        lines.extend(f"- {item}" for item in contract["required_qualifications"])
        lines.append("")
    if packet["known_misconceptions"]:
        lines += ["## Known misconceptions", ""]
        for item in packet["known_misconceptions"]:
            lines.append(f"- **{item['misconception_id']}** ({item['severity']}): {item['required_qualification']}")
        lines.append("")
    if packet["counterexamples"]:
        lines += ["## Counterexamples", ""]
        for item in packet["counterexamples"]:
            lines.append(
                f"- **{item['knowledge_id']}** — fixtures: {', '.join(item['counterexample_ids'])}; "
                f"book artifacts: {', '.join(item['artifact_paths'])}"
            )
        lines.append("")
    if packet["negative_results"]:
        lines += ["## Negative results", ""]
        for item in packet["negative_results"]:
            lines.append(f"- **{item['knowledge_id']}** — {item['observed_result']}")
            lines.append(f"  - Failure criterion: {item['failure_criterion']}")
            lines.append(f"  - Interpretation: {item['interpretation']}")
        lines.append("")
    if packet["executable_checks"]:
        lines += ["## Executable checks", ""]
        for item in packet["executable_checks"]:
            lines.append(
                f"- **{item['knowledge_id']}** — `{item['repository']}` contracts: "
                f"{', '.join(item['contract_ids'])}; status: `{item['implementation_status']}`"
            )
        lines.append("")
    runnable = [
        (item["knowledge_id"], recipe)
        for item in packet["implementation_examples"]
        for recipe in item.get("recipes", [])
    ]
    if runnable:
        lines += ["## Implementation examples", ""]
        for knowledge_id, recipe in runnable:
            lines.append(
                f"- **{knowledge_id} / {recipe['recipe_id']}** — "
                f"`{recipe['command']}` (expected contract status: "
                f"`{recipe['expected_status']}`)"
            )
        lines.append("")
    if contract["failure_consequences"]:
        lines += ["## Failure consequences", ""]
        lines.extend(f"- {item}" for item in contract["failure_consequences"])
        lines.append("")
    if contract["safe_shorthand"]:
        lines += ["## Safe shorthand", ""]
        lines.extend(f"- {item}" for item in contract["safe_shorthand"])
        lines.append("")
    if contract["unresolved_boundaries"]:
        lines += ["## Unresolved boundaries", ""]
        lines.extend(f"- **{item['claim_id']}** — {item['boundary']}" for item in contract["unresolved_boundaries"])
        lines.append("")
    if contract.get("retrieval_warning"):
        lines += ["## Retrieval warning", "", contract["retrieval_warning"], ""]
    lines += ["## Audience guidance", "", contract["audience_guidance"], "", "## Sources", ""]
    for index, source in enumerate(packet["sources"], start=1):
        lines.append(f"{index}. `{source_location(source)}`")
    lines += ["", "## Retrieval record", "", f"- Method: `{packet['retrieval']['method']}`"]
    if packet["retrieval"]["detected_misconceptions"]:
        routes = ", ".join(item["misconception_id"] for item in packet["retrieval"]["detected_misconceptions"])
        lines.append(f"- Qualification routes: `{routes}`")
    lines.append("")
    return "\n".join(lines)


class BookLLMService:
    """Single source of behavior for CLI, HTTP, and MCP access routes."""

    def __init__(self, index: CorpusIndex | None = None) -> None:
        self.index = index or CorpusIndex()

    def _validate_request(self, query: str, audience: str, limit: int, method: str) -> None:
        if not query.strip():
            raise ValueError("query must not be empty")
        if audience not in AUDIENCES:
            raise ValueError(f"unknown audience: {audience}")
        if not 1 <= limit <= MAX_LIMIT:
            raise ValueError(f"limit must be between 1 and {MAX_LIMIT}")
        if method not in SUPPORTED_METHODS:
            raise ValueError(f"unsupported retrieval method: {method}")

    def context(self, query: str, audience: str = "student", limit: int = 6, method: str = "hybrid") -> dict:
        self._validate_request(query, audience, limit, method)
        packet = self.index.context_packet(query, audience, supporting_limit=limit, method=method)
        # The character component of the hybrid baseline can produce weak
        # surface matches for wholly unrelated questions. A production answer
        # route uses lexical support as a conservative abstention floor unless
        # a curated dangerous-shortcut contract has explicitly qualified the
        # query.
        if (
            packet["status"] == "under_retrieved"
            and not packet["retrieval"]["detected_misconceptions"]
            and not self.index.search(query, limit=1)
        ):
            packet["status"] = "unsupported"
            packet["supporting_records"] = []
            packet["sources"] = []
            packet["answer_contract"]["retrieval_warning"] = "No book-supported material was retrieved for this query."
        errors = validate_context_packet(self.index, packet)
        if errors:
            raise ValueError("invalid context packet: " + "; ".join(errors))
        return packet

    def response(self, query: str, audience: str = "student", limit: int = 6, method: str = "hybrid") -> dict:
        packet = self.context(query, audience, limit, method)
        result = {
            "api_schema_version": API_SCHEMA_VERSION,
            "type": "book_grounded_answer_packet",
            "corpus_id": self.index.manifest["corpus_id"],
            "release": self.index.manifest["release"],
            "packet": packet,
            "markdown": render_markdown(packet),
            "validation": {
                "valid": True,
                "source_hashes_checked": True,
                "claim_coverage_checked": True,
                "citation_presence_checked": True,
            },
        }
        errors = validate_answer_response(self.index, result)
        if errors:
            raise ValueError("invalid answer response: " + "; ".join(errors))
        return result

    def search(self, query: str, limit: int = 8, method: str = "hybrid") -> dict:
        self._validate_request(query, "student", limit, method)
        if method == "lexical":
            results = self.index.search(query, limit=limit)
        elif method == "char_tfidf":
            results = self.index.search_char_tfidf(query, limit=limit)
        elif method == "graph":
            results = self.index.search_graph(query, limit=limit)
        else:
            results = self.index.search_hybrid(query, limit=limit)
        return {
            "api_schema_version": API_SCHEMA_VERSION,
            "type": "book_search_results",
            "corpus_id": self.index.manifest["corpus_id"],
            "release": self.index.manifest["release"],
            "method": method,
            "query": query,
            "results": [result_payload(result) for result in results],
        }

    def health(self) -> dict:
        return {
            "api_schema_version": API_SCHEMA_VERSION,
            "status": "ok",
            "corpus_id": self.index.manifest["corpus_id"],
            "release": self.index.manifest["release"],
            "record_count": self.index.manifest["record_count"],
            "production_retrieval_method": "hybrid",
            "experimental_retrieval_methods": ["graph"],
        }
