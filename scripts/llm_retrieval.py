#!/usr/bin/env python3
"""Model-independent lexical retrieval and qualification-aware context assembly."""

from __future__ import annotations

import json
import math
import re
import tomllib
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from llm_embeddings import EmbeddingRuntimeError

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "llm/generated/corpus.jsonl"
CORPUS_MANIFEST = ROOT / "llm/generated/corpus-manifest.json"
MISCONCEPTIONS = ROOT / "llm/misconceptions.toml"
FEDERATED_PAIR = ROOT / "generated/federated-knowledge-pair-manifest.json"
SCHEMA_VERSION = "0.1.0"
AUDIENCES = {"student", "software_engineer", "power_engineer"}
TOKEN = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]+")
ROUTER_GENERIC_TERMS = {
    "a", "asset", "branch", "circuit", "data", "device", "equivalent", "graph", "line",
    "matrix", "model", "network", "node", "power", "source", "state", "study", "system",
    "the", "topology", "view", "loop",
}

STOPWORDS = {
    "a", "about", "after", "all", "also", "an", "and", "any", "are", "as", "at",
    "be", "because", "been", "before", "being", "between", "both", "but", "by",
    "can", "could", "did", "do", "does", "each", "for", "from", "had", "has",
    "have", "how", "if", "in", "into", "is", "it", "its", "may", "more", "most",
    "not", "of", "on", "one", "or", "our", "should", "so", "some", "than", "that",
    "the", "their", "then", "there", "these", "they", "this", "through", "to", "under",
    "use", "used", "using", "was", "we", "what", "when", "where", "which", "while",
    "why", "will", "with", "without", "would", "you",
}

NORMALIZED_ALIASES = {
    "y-bus": "ybus",
    "y_bus": "ybus",
    "bus-admittance": "ybus",
    "bus_admittance": "ybus",
    "opti-kron": "optikron",
    "constant-z": "constantz",
    "constant-impedance": "constantz",
    "positive-sequence": "positivesequence",
    "multi-terminal": "multiterminal",
    "multi-conductor": "multiconductor",
}


def normalize_word(word: str) -> str:
    word = NORMALIZED_ALIASES.get(word.lower(), word.lower()).replace("-", "").replace("_", "")
    if len(word) > 5 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 5 and word.endswith("sses"):
        return word[:-2]
    if len(word) > 4 and word.endswith("ses") and word not in {"losses"}:
        return word[:-2]
    if len(word) > 4 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def tokenize(text: str, keep_stopwords: bool = False) -> list[str]:
    prepared = text.lower()
    for source, target in NORMALIZED_ALIASES.items():
        prepared = prepared.replace(source, target)
    result = [normalize_word(word) for word in TOKEN.findall(prepared)]
    if keep_stopwords:
        return result
    return [word for word in result if word not in STOPWORDS and len(word) > 1]


def character_ngrams(text: str, minimum: int = 3, maximum: int = 5) -> list[str]:
    """Return word-local character n-grams for a dependency-free surface-semantic signal."""
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    ngrams = []
    for word in words:
        if len(word) < minimum:
            continue
        padded = f"^{word}$"
        for size in range(minimum, min(maximum, len(padded)) + 1):
            ngrams.extend(padded[index:index + size] for index in range(len(padded) - size + 1))
    return ngrams


@dataclass(frozen=True)
class SearchResult:
    record_id: str
    record_type: str
    title: str
    score: float
    source: dict

    def as_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "record_type": self.record_type,
            "title": self.title,
            "score": round(self.score, 6),
            "source": self.source,
        }


class CorpusIndex:
    """Small in-memory BM25 index over the committed model-independent corpus."""

    def __init__(self) -> None:
        self.records = [json.loads(line) for line in CORPUS.read_text().splitlines() if line.strip()]
        self.by_id = {record["record_id"]: record for record in self.records}
        self.manifest = json.loads(CORPUS_MANIFEST.read_text())
        self.misconceptions = tomllib.loads(MISCONCEPTIONS.read_text()).get("misconception", [])
        self.federated_pair = json.loads(FEDERATED_PAIR.read_text())
        self.federated_links = self.federated_pair.get("links", {})
        self.misconception_by_id = {item["id"]: item for item in self.misconceptions}
        self.knowledge_by_misconception: dict[str, list[str]] = defaultdict(list)
        for record in self.records:
            if record["record_type"] != "scientific_knowledge":
                continue
            for misconception_id in record.get("misconception_ids", []):
                self.knowledge_by_misconception[misconception_id].append(record["record_id"])
        self.documents: list[Counter[str]] = []
        self.lengths: list[int] = []
        document_frequency: Counter[str] = Counter()
        for record in self.records:
            weighted = " ".join(
                [
                    record["record_id"],
                    record["title"],
                    record["title"],
                    record["text"],
                ]
            )
            terms = tokenize(weighted)
            counts = Counter(terms)
            self.documents.append(counts)
            self.lengths.append(sum(counts.values()))
            document_frequency.update(counts.keys())
        self.average_length = sum(self.lengths) / len(self.lengths) if self.lengths else 1.0
        count = len(self.records)
        self.idf = {
            term: math.log(1.0 + (count - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequency.items()
        }
        self.concept_aliases = self._concept_aliases()
        self.char_documents: list[Counter[str]] = []
        char_document_frequency: Counter[str] = Counter()
        for record in self.records:
            weighted = " ".join([record["record_id"], record["title"], record["title"], record["text"]])
            counts = Counter(character_ngrams(weighted))
            self.char_documents.append(counts)
            char_document_frequency.update(counts.keys())
        self.char_idf = {
            term: math.log(1.0 + (count - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in char_document_frequency.items()
        }
        self.char_weights: list[dict[str, float]] = []
        self.char_norms: list[float] = []
        for counts in self.char_documents:
            weights = {
                term: (1.0 + math.log(frequency)) * self.char_idf[term]
                for term, frequency in counts.items()
            }
            self.char_weights.append(weights)
            self.char_norms.append(math.sqrt(sum(weight * weight for weight in weights.values())))
        self._neural_document_embeddings: dict[str, list[list[float]]] = {}
        self.graph_neighbors: dict[str, set[str]] = defaultdict(set)
        self._build_record_graph()

    @staticmethod
    def _embedding_text(record: dict) -> str:
        return " ".join([record["record_id"], record["title"], record["title"], record["text"]])

    def _build_record_graph(self) -> None:
        """Build a provenance graph from shared source and misconception identities."""
        groups: dict[str, set[str]] = defaultdict(set)
        for record in self.records:
            record_id = record["record_id"]
            source = record.get("source", {})
            if source.get("path"):
                groups[f"source:{source['path']}"].add(record_id)
            for misconception_id in record.get("misconception_ids", []):
                groups[f"misconception:{misconception_id}"].add(record_id)
        for members in groups.values():
            for record_id in members:
                self.graph_neighbors[record_id].update(members - {record_id})

    def _concept_aliases(self) -> list[tuple[list[set[str]], set[str]]]:
        aliases = []
        distinctive_singletons = {
            "adjacency", "asset", "bus", "constraint", "cycle", "direction", "earth",
            "edge", "equivalence", "factor", "flow", "ground", "injection", "limit",
            "neutral", "normalization", "parallel", "phase", "port", "provenance",
            "radial", "rating", "sequence", "state", "terminal", "topology", "vertex", "ybus",
        }
        for record in self.records:
            if record["record_type"] != "concept_bundle":
                continue
            concept = record["concept"]
            source_phrases: list[set[str]] = []
            for field in (
                "house_terms", "power_engineering", "software_data", "mathematical_modelling",
                "graph_theory", "graph_machine_learning", "circuit_theory",
            ):
                for phrase in concept.get(field, []):
                    phrase_terms = set(tokenize(phrase))
                    if len(phrase_terms) > 1 or phrase_terms & distinctive_singletons:
                        source_phrases.append(phrase_terms)
            target_terms = set()
            for phrase in concept.get("house_terms", []):
                target_terms.update(tokenize(phrase))
            aliases.append((source_phrases, target_terms))
        return aliases

    def expand_query(self, query: str) -> list[str]:
        original = tokenize(query)
        expanded = set(original)
        original_set = set(original)
        for alias_phrases, house_terms in self.concept_aliases:
            if any(phrase and phrase <= original_set for phrase in alias_phrases):
                expanded.update(house_terms)
        return sorted(expanded)

    def search(self, query: str, limit: int = 10, record_types: set[str] | None = None) -> list[SearchResult]:
        query_terms = self.expand_query(query)
        query_counts = Counter(query_terms)
        scored: list[tuple[float, str, int]] = []
        k1 = 1.5
        b = 0.75
        type_boost = {
            "scientific_knowledge": 1.3, "claim_bundle": 1.25,
            "concept_bundle": 1.15, "section": 1.0,
        }
        for index, (record, counts, length) in enumerate(zip(self.records, self.documents, self.lengths)):
            if record_types and record["record_type"] not in record_types:
                continue
            score = 0.0
            for term, query_frequency in query_counts.items():
                frequency = counts.get(term, 0)
                if not frequency:
                    continue
                denominator = frequency + k1 * (1.0 - b + b * length / self.average_length)
                score += self.idf.get(term, 0.0) * frequency * (k1 + 1.0) / denominator
                score *= 1.0 + 0.03 * min(query_frequency - 1, 3)
            score *= type_boost[record["record_type"]]
            if score > 0:
                scored.append((score, record["record_id"], index))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [
            SearchResult(
                record_id=self.records[index]["record_id"],
                record_type=self.records[index]["record_type"],
                title=self.records[index]["title"],
                score=score,
                source=self.records[index]["source"],
            )
            for score, _, index in scored[:limit]
        ]

    def search_char_tfidf(
        self, query: str, limit: int = 10, record_types: set[str] | None = None
    ) -> list[SearchResult]:
        query_counts = Counter(character_ngrams(" ".join([query, " ".join(self.expand_query(query))])))
        query_weights = {
            term: (1.0 + math.log(frequency)) * self.char_idf.get(term, 0.0)
            for term, frequency in query_counts.items()
            if term in self.char_idf
        }
        query_norm = math.sqrt(sum(weight * weight for weight in query_weights.values()))
        if not query_norm:
            return []
        scored: list[tuple[float, str, int]] = []
        type_boost = {
            "scientific_knowledge": 1.3, "claim_bundle": 1.25,
            "concept_bundle": 1.15, "section": 1.0,
        }
        for index, record in enumerate(self.records):
            if record_types and record["record_type"] not in record_types:
                continue
            document_norm = self.char_norms[index]
            if not document_norm:
                continue
            dot = sum(weight * self.char_weights[index].get(term, 0.0) for term, weight in query_weights.items())
            score = dot / (query_norm * document_norm)
            score *= type_boost[record["record_type"]]
            if score > 0:
                scored.append((score, record["record_id"], index))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [
            SearchResult(
                record_id=self.records[index]["record_id"],
                record_type=self.records[index]["record_type"],
                title=self.records[index]["title"],
                score=score,
                source=self.records[index]["source"],
            )
            for score, _, index in scored[:limit]
        ]

    def search_hybrid(
        self, query: str, limit: int = 10, record_types: set[str] | None = None
    ) -> list[SearchResult]:
        """Fuse lexical and character-TF-IDF rankings without pretending either is neural semantic search."""
        candidate_limit = max(limit * 4, 40)
        lexical = self.search(query, limit=candidate_limit, record_types=record_types)
        character = self.search_char_tfidf(query, limit=candidate_limit, record_types=record_types)
        by_id = {record.record_id: record for record in [*lexical, *character]}
        lexical_rank = {record.record_id: rank for rank, record in enumerate(lexical, start=1)}
        character_rank = {record.record_id: rank for rank, record in enumerate(character, start=1)}
        reciprocal_rank_constant = 60.0
        fused = []
        for record_id, record in by_id.items():
            score = 0.0
            if record_id in lexical_rank:
                score += 1.0 / (reciprocal_rank_constant + lexical_rank[record_id])
            if record_id in character_rank:
                score += 1.0 / (reciprocal_rank_constant + character_rank[record_id])
            fused.append((score, record_id, record))
        fused.sort(key=lambda item: (-item[0], item[1]))
        return [
            SearchResult(
                record_id=record_id,
                record_type=record.record_type,
                title=record.title,
                score=score,
                source=record.source,
            )
            for score, record_id, record in fused[:limit]
        ]

    def search_neural(
        self, query: str, embedder, limit: int = 10, record_types: set[str] | None = None
    ) -> list[SearchResult]:
        """Rank records with an explicitly supplied, provenance-aware embedder."""
        if embedder is None:
            raise ValueError("neural retrieval requires an embedding provider")
        provenance = embedder.provenance()
        cache_key = json.dumps(provenance, sort_keys=True)
        document_embeddings = self._neural_document_embeddings.get(cache_key)
        if document_embeddings is None:
            document_embeddings = embedder.encode([self._embedding_text(record) for record in self.records])
            if len(document_embeddings) != len(self.records):
                raise EmbeddingRuntimeError("embedding provider returned the wrong corpus size")
            self._neural_document_embeddings[cache_key] = document_embeddings
        query_text = " ".join([query, " ".join(self.expand_query(query))])
        query_embedding = embedder.encode([query_text])[0]
        query_norm = math.sqrt(sum(value * value for value in query_embedding))
        if not query_norm:
            return []
        type_boost = {
            "scientific_knowledge": 1.3, "claim_bundle": 1.25,
            "concept_bundle": 1.15, "section": 1.0,
        }
        scored: list[tuple[float, str, int]] = []
        for index, record in enumerate(self.records):
            if record_types and record["record_type"] not in record_types:
                continue
            embedding = document_embeddings[index]
            document_norm = math.sqrt(sum(value * value for value in embedding))
            if not document_norm:
                continue
            score = sum(left * right for left, right in zip(query_embedding, embedding))
            score /= query_norm * document_norm
            score *= type_boost[record["record_type"]]
            if score > 0:
                scored.append((score, record["record_id"], index))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [
            SearchResult(
                record_id=self.records[index]["record_id"],
                record_type=self.records[index]["record_type"],
                title=self.records[index]["title"],
                score=score,
                source=self.records[index]["source"],
            )
            for score, _, index in scored[:limit]
        ]

    def search_graph(
        self, query: str, limit: int = 10, record_types: set[str] | None = None
    ) -> list[SearchResult]:
        """Traverse source/provenance neighbors from lexical and surface seeds.

        This is a benchmark-only diagnostic. It does not replace the ordinary
        ranker or the explicit misconception-contract expansion.
        """
        candidate_limit = max(limit * 4, 40)
        seeds = self.search(query, limit=candidate_limit, record_types=record_types)
        if not seeds:
            seeds = self.search_char_tfidf(query, limit=candidate_limit, record_types=record_types)
        by_id = {record.record_id: record for record in seeds}
        scores: defaultdict[str, float] = defaultdict(float)
        for rank, seed in enumerate(seeds, start=1):
            seed_weight = 1.0 / (20.0 + rank)
            scores[seed.record_id] += seed_weight
            for neighbor_id in self.graph_neighbors.get(seed.record_id, set()):
                neighbor = self.by_id[neighbor_id]
                if record_types and neighbor["record_type"] not in record_types:
                    continue
                by_id.setdefault(
                    neighbor_id,
                    SearchResult(
                        record_id=neighbor_id,
                        record_type=neighbor["record_type"],
                        title=neighbor["title"],
                        score=0.0,
                        source=neighbor["source"],
                    ),
                )
                scores[neighbor_id] += 0.5 * seed_weight
        type_boost = {
            "scientific_knowledge": 1.3, "claim_bundle": 1.25,
            "concept_bundle": 1.15, "section": 1.0,
        }
        ranked = []
        for record_id, result in by_id.items():
            score = scores[record_id] * type_boost[result.record_type]
            if score > 0:
                ranked.append((score, record_id, result))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [
            SearchResult(
                record_id=record_id,
                record_type=result.record_type,
                title=result.title,
                score=score,
                source=result.source,
            )
            for score, record_id, result in ranked[:limit]
        ]

    def search_reranked(
        self,
        query: str,
        reranker,
        base_method: str = "hybrid",
        limit: int = 10,
        candidate_limit: int = 40,
        record_types: set[str] | None = None,
        embedder=None,
    ) -> list[SearchResult]:
        """Rerank a bounded first-stage candidate set with a cross-encoder."""
        if base_method == "lexical":
            candidates = self.search(query, limit=candidate_limit, record_types=record_types)
        elif base_method == "char_tfidf":
            candidates = self.search_char_tfidf(query, limit=candidate_limit, record_types=record_types)
        elif base_method == "hybrid":
            candidates = self.search_hybrid(query, limit=candidate_limit, record_types=record_types)
        elif base_method == "neural":
            candidates = self.search_neural(query, embedder, limit=candidate_limit, record_types=record_types)
        else:
            raise ValueError(f"unknown reranker base method: {base_method}")
        pairs = [
            (query, f"{self.by_id[result.record_id]['title']}\n{self.by_id[result.record_id]['text']}")
            for result in candidates
        ]
        scores = reranker.predict(pairs)
        ranked = sorted(
            zip(scores, candidates), key=lambda item: (-item[0], item[1].record_id)
        )
        return [
            SearchResult(
                record_id=result.record_id,
                record_type=result.record_type,
                title=result.title,
                score=score,
                source=result.source,
            )
            for score, result in ranked[:limit]
        ]

    def route_misconceptions(self, query: str, limit: int = 1, threshold: float = 0.34) -> list[dict]:
        query_normalized = " ".join(tokenize(query, keep_stopwords=True))
        query_terms = set(tokenize(query))
        ranked = []
        for item in self.misconceptions:
            pattern_scores = []
            exact_match = False
            for pattern in item["query_patterns"]:
                normalized_pattern = " ".join(tokenize(pattern, keep_stopwords=True))
                pattern_terms = set(tokenize(pattern))
                exact = bool(normalized_pattern and normalized_pattern in query_normalized)
                exact_match = exact_match or exact
                specific_pattern_terms = pattern_terms - ROUTER_GENERIC_TERMS
                specific_query_terms = query_terms - ROUTER_GENERIC_TERMS
                overlap = specific_query_terms & specific_pattern_terms
                if not exact and not overlap:
                    continue
                coverage = len(overlap) / max(1, len(specific_pattern_terms))
                precision = len(overlap) / max(1, len(specific_query_terms))
                pattern_scores.append(0.72 * coverage + 0.28 * precision)
            title_terms = set(tokenize(item["title"])) - ROUTER_GENERIC_TERMS
            title_score = len((query_terms - ROUTER_GENERIC_TERMS) & title_terms) / max(1, len(title_terms))
            score = max(pattern_scores or [0.0]) + 0.15 * title_score + (0.4 if exact_match else 0.0)
            if item["id"] == "one-universal-network-graph" and {"graph", "network"} <= query_terms:
                score = max(score, 0.8)
            ranked.append((score, item["id"], exact_match))
        ranked.sort(key=lambda value: (-value[0], value[1]))
        return [
            {"misconception_id": item_id, "score": round(score, 6), "exact_pattern": exact}
            for score, item_id, exact in ranked[:limit]
            if score >= threshold
        ]

    def _record_summary(self, record_id: str, mandatory_reason: str | None = None) -> dict:
        record = self.by_id[record_id]
        summary = {
            "record_id": record_id,
            "record_type": record["record_type"],
            "title": record["title"],
            "source": record["source"],
        }
        if mandatory_reason:
            summary["mandatory_reason"] = mandatory_reason
        if record["record_type"] == "claim_bundle":
            claim = record["claim"]
            summary["claim"] = {
                field: claim.get(field)
                for field in (
                    "claim_id", "claim_text", "claim_type", "verification", "exactness_object",
                    "model_scope", "assumptions", "preservation_dimensions", "evidence_type",
                    "citation_keys", "unresolved_issue",
                )
            }
        elif record["record_type"] == "concept_bundle":
            concept = record["concept"]
            summary["concept"] = {
                field: concept.get(field)
                for field in (
                    "id", "house_terms", "relation_class", "usage_status", "required_question",
                    "unsafe_inference", "power_engineering", "software_data",
                    "mathematical_modelling", "graph_theory", "graph_machine_learning", "circuit_theory",
                )
            }
        elif record["record_type"] == "scientific_knowledge":
            summary["knowledge"] = {
                field: record.get(field)
                for field in (
                    "knowledge_id", "kind", "scientific_statement", "scope",
                    "evidence_status", "does_not_establish",
                )
            }
            summary["book"] = record["book"]
            summary["executable"] = record["executable"]
        else:
            summary["excerpt"] = record["text"][:1200]
        return summary

    def context_packet(
        self, query: str, audience: str, supporting_limit: int = 6, method: str = "hybrid", embedder=None
    ) -> dict:
        if audience not in AUDIENCES:
            raise ValueError(f"unknown audience: {audience}")
        if method not in {"lexical", "char_tfidf", "hybrid", "neural", "graph"}:
            raise ValueError(f"unknown retrieval method: {method}")
        if method == "neural" and embedder is None:
            raise ValueError("neural context packets require an embedding provider")
        routes = self.route_misconceptions(query)
        mandatory: list[dict] = []
        mandatory_ids: set[str] = set()
        qualifications: list[str] = []
        consequences: list[str] = []
        safe_shorthand: list[str] = []
        for route in routes:
            misconception = self.misconception_by_id[route["misconception_id"]]
            qualifications.append(misconception["required_qualification"])
            consequences.append(misconception["operational_consequence"])
            safe_shorthand.append(misconception["safe_shorthand"])
            for claim_id in misconception["mandatory_claim_ids"]:
                record_id = f"claim:{claim_id}"
                if record_id not in mandatory_ids:
                    mandatory.append(self._record_summary(record_id, f"mandatory for {misconception['id']}"))
                    mandatory_ids.add(record_id)
            for concept_id in misconception["mandatory_concept_ids"]:
                record_id = f"concept:{concept_id}"
                if record_id not in mandatory_ids:
                    mandatory.append(self._record_summary(record_id, f"mandatory for {misconception['id']}"))
                    mandatory_ids.add(record_id)
            for record_id in self.knowledge_by_misconception.get(misconception["id"], []):
                if record_id not in mandatory_ids:
                    mandatory.append(
                        self._record_summary(record_id, f"scientific basis for {misconception['id']}")
                    )
                    mandatory_ids.add(record_id)

        if method == "lexical":
            ranked = self.search(query, limit=supporting_limit + len(mandatory_ids) + 8)
        elif method == "char_tfidf":
            ranked = self.search_char_tfidf(query, limit=supporting_limit + len(mandatory_ids) + 8)
        elif method == "hybrid":
            ranked = self.search_hybrid(query, limit=supporting_limit + len(mandatory_ids) + 8)
        elif method == "neural":
            ranked = self.search_neural(
                query, embedder, limit=supporting_limit + len(mandatory_ids) + 8
            )
        else:
            ranked = self.search_graph(query, limit=supporting_limit + len(mandatory_ids) + 8)
        supporting = []
        for result in ranked:
            if result.record_id in mandatory_ids:
                continue
            supporting.append({**self._record_summary(result.record_id), "score": round(result.score, 6)})
            if len(supporting) >= supporting_limit:
                break

        claims = [item["claim"] for item in mandatory if item["record_type"] == "claim_bundle"]
        knowledge = [item for item in mandatory if item["record_type"] == "scientific_knowledge"]
        scientific_basis = [
            {
                "knowledge_id": item["knowledge"]["knowledge_id"],
                "title": item["title"],
                "scientific_statement": item["knowledge"]["scientific_statement"],
                "scope": item["knowledge"]["scope"],
                "evidence_status": item["knowledge"]["evidence_status"],
            }
            for item in knowledge
        ]
        known_misconceptions = []
        for route in routes:
            item = self.misconception_by_id[route["misconception_id"]]
            known_misconceptions.append(
                {
                    "misconception_id": item["id"],
                    "title": item["title"],
                    "severity": item["severity"],
                    "tempting_answer": item["tempting_answer"],
                    "required_qualification": item["required_qualification"],
                }
            )
        counterexamples = [
            {
                "knowledge_id": item["knowledge"]["knowledge_id"],
                "counterexample_ids": item["book"]["counterexample_ids"],
                "artifact_paths": item["book"]["artifact_paths"],
            }
            for item in knowledge
        ]
        executable_checks = []
        implementation_examples = []
        for item in knowledge:
            knowledge_id = item["knowledge"]["knowledge_id"]
            pair_link = self.federated_links.get(knowledge_id, {})
            contracts = pair_link.get("contracts", [])
            recipes = [
                recipe
                for contract in contracts
                for recipe in contract.get("recipes", [])
            ]
            executable_checks.append({
                "knowledge_id": knowledge_id,
                **item["executable"],
                "pinned_contracts": contracts,
                "pair_id": self.federated_pair.get("pair_id"),
                "pair_sha256": self.federated_pair.get("pair_sha256"),
            })
            implementation_examples.append({
                "knowledge_id": knowledge_id,
                "repository": item["executable"]["repository"],
                "fixture_ids": item["executable"]["fixture_ids"],
                "recipes": recipes,
            })
        scientific_boundaries = [
            {"knowledge_id": item["knowledge"]["knowledge_id"], "boundary": boundary}
            for item in knowledge
            for boundary in item["knowledge"]["does_not_establish"]
        ]
        sources = []
        seen_sources = set()
        for item in [*mandatory, *supporting]:
            source = item["source"]
            key = (source["path"], source.get("anchor", ""))
            if key not in seen_sources:
                sources.append(source)
                seen_sources.add(key)

        if mandatory:
            status = "qualified"
        elif supporting:
            status = "under_retrieved"
        else:
            status = "unsupported"
        retrieval_warning = ""
        if status == "under_retrieved":
            retrieval_warning = (
                "Related book material was retrieved, but no qualified claim contract was found. "
                "Do not treat relevance as a book-supported conclusion; broaden or reformulate the query."
            )
        elif status == "unsupported":
            retrieval_warning = "No book-supported material was retrieved for this query."
        audience_guidance = {
            "student": "Use intuition and a minimal example, then show the counterexample before adding notation.",
            "software_engineer": "Name object types, preconditions, generated views, invariants, provenance, and failure handling.",
            "power_engineer": "Use equipment and study language; state model assumptions and operational or protection consequences.",
        }[audience]
        packet = {
            "schema_version": SCHEMA_VERSION,
            "query": query,
            "audience": audience,
            "status": status,
            "release": self.manifest["release"],
            "retrieval": {
                "method": f"{method}_with_contract_expansion",
                "expanded_query_terms": self.expand_query(query),
                "detected_misconceptions": routes,
            },
            "mandatory_records": mandatory,
            "supporting_records": supporting,
            "scientific_basis": scientific_basis,
            "known_misconceptions": known_misconceptions,
            "counterexamples": counterexamples,
            "executable_checks": executable_checks,
            "implementation_examples": implementation_examples,
            "unresolved_boundaries": scientific_boundaries,
            "answer_contract": {
                "direct_answer_basis": [
                    *[claim["claim_text"] for claim in claims],
                    *[item["scientific_statement"] for item in scientific_basis],
                ],
                "scope_and_assumptions": [
                    {
                        "claim_id": claim["claim_id"],
                        "exactness_object": claim["exactness_object"],
                        "model_scope": claim["model_scope"],
                        "assumptions": claim["assumptions"],
                    }
                    for claim in claims
                ],
                "required_qualifications": qualifications,
                "failure_consequences": consequences,
                "safe_shorthand": safe_shorthand,
                "audience_guidance": audience_guidance,
                "retrieval_warning": retrieval_warning,
                "unresolved_boundaries": [
                    {"claim_id": claim["claim_id"], "boundary": claim["unresolved_issue"]}
                    for claim in claims
                    if claim.get("unresolved_issue")
                ],
            },
            "sources": sources,
        }
        if method == "neural":
            packet["retrieval"]["embedding_provenance"] = embedder.provenance()
        return packet


def record_ids(results: list[SearchResult]) -> list[str]:
    return [result.record_id for result in results]
