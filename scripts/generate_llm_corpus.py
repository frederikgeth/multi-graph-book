#!/usr/bin/env python3
"""Generate deterministic, versioned records for book-grounded LLM retrieval."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/src"
CLAIMS = ROOT / "claims/claims.toml"
VOCABULARY = ROOT / "vocabulary/vocabulary.toml"
MISCONCEPTIONS = ROOT / "llm/misconceptions.toml"
EVALUATIONS = ROOT / "llm/evaluation-cases.toml"
HELDOUT = ROOT / "llm/heldout-paraphrases.toml"
RELEASE_MANIFEST = ROOT / "review/release-candidate-manifest.json"
SCIENTIFIC_KNOWLEDGE = ROOT / "generated/scientific_knowledge.jsonl"
SCIENTIFIC_MANIFEST = ROOT / "generated/scientific-knowledge-manifest.json"
OUTPUT = ROOT / "llm/generated/corpus.jsonl"
CORPUS_MANIFEST = ROOT / "llm/generated/corpus-manifest.json"
SCHEMA_VERSION = "0.1.0"

# Generated navigation pages duplicate source ledgers and would dominate lexical
# retrieval without adding scientific evidence.
EXCLUDED_DOCS = {
    "docs/src/reference/chapter-status.md",
    "docs/src/reference/evidence-map.md",
    "docs/src/reference/knowledge-base-index.md",
    "docs/src/reference/vocabulary-indexes.md",
}

HEADING = re.compile(r"^(?P<marks>#{1,6})\s+(?P<heading>.+?)\s*$")
EXPLICIT_ANCHOR = re.compile(r"^\[(?P<title>.+?)\]\(@id\s+(?P<anchor>[^)]+)\)$")
TOKEN = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]+")
STOPWORDS = {
    "about", "after", "again", "also", "among", "because", "been", "before",
    "being", "between", "both", "cannot", "could", "declared", "does", "each",
    "from", "have", "into", "model", "network", "only", "other", "same", "should",
    "that", "their", "there", "these", "this", "through", "under", "using", "when",
    "where", "which", "while", "with", "without", "would",
}


@dataclass(frozen=True)
class Section:
    path: str
    title: str
    anchor: str
    line: int
    level: int
    heading_path: tuple[str, ...]
    text: str
    sha256: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def slugify(value: str) -> str:
    value = re.sub(r"[`*_]", "", value.lower())
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "section"


def heading_parts(raw: str) -> tuple[str, str]:
    match = EXPLICIT_ANCHOR.match(raw)
    if match:
        return match.group("title"), match.group("anchor")
    title = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", raw)
    return title.strip(), slugify(title)


def parse_sections(path: Path) -> list[Section]:
    content = path.read_text()
    lines = content.splitlines()
    starts: list[tuple[int, int, str, str]] = []
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if not match:
            continue
        title, anchor = heading_parts(match.group("heading"))
        starts.append((index, len(match.group("marks")), title, anchor))
    if not starts:
        return []

    source_hash = sha256_file(path)
    anchor_counts: Counter[str] = Counter()
    stack: list[tuple[int, str]] = []
    sections: list[Section] = []
    for position, (start, level, title, base_anchor) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        anchor_counts[base_anchor] += 1
        occurrence = anchor_counts[base_anchor]
        anchor = base_anchor if occurrence == 1 else f"{base_anchor}-{occurrence}"
        text = "\n".join(lines[start:end]).strip()
        if not text:
            continue
        sections.append(
            Section(
                path=relative(path),
                title=title,
                anchor=anchor,
                line=start + 1,
                level=level,
                heading_path=tuple(item[1] for item in stack),
                text=text,
                sha256=source_hash,
            )
        )
    return sections


def tokens(value: str) -> set[str]:
    return {
        token.lower()
        for token in TOKEN.findall(value)
        if len(token) > 2 and token.lower() not in STOPWORDS
    }


def select_supporting_section(claim: dict, sections: list[Section]) -> tuple[Section, str, float]:
    if not sections:
        raise ValueError(f"no Markdown sections in {claim['chapter']}")
    claim_id = claim["claim_id"]
    direct = [section for section in sections if claim_id in section.text]
    if direct:
        return direct[0], "claim_id_mention", 1.0

    query = " ".join(
        str(claim.get(field, ""))
        for field in ("claim_text", "model_scope", "assumptions", "unresolved_issue")
    )
    query_tokens = tokens(query)
    if not query_tokens:
        return sections[0], "chapter_fallback", 0.0
    ranked = []
    for section in sections:
        overlap = len(query_tokens & tokens(section.text)) / len(query_tokens)
        ranked.append((overlap, -section.line, section))
    score, _, selected = max(ranked, key=lambda item: (item[0], item[1]))
    return selected, "lexical_claim_coverage", round(score, 6)


def release_identity() -> dict:
    manifest = json.loads(RELEASE_MANIFEST.read_text())
    identity = {
        "release_candidate_id": manifest["release_candidate_id"],
        "status": manifest["status"],
        "external_reviewed_claims": manifest["external_reviewed_claims"],
        "independent_human_double_coding": manifest["independent_human_double_coding"],
    }
    identity["release_identity_sha256"] = sha256_bytes(canonical_json(identity).encode())
    return identity


def source_object(section: Section) -> dict:
    return {
        "path": section.path,
        "anchor": section.anchor,
        "line": section.line,
        "sha256": section.sha256,
    }


def misconception_maps(misconceptions: list[dict]) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, list[str]]]:
    by_claim: dict[str, list[str]] = defaultdict(list)
    by_concept: dict[str, list[str]] = defaultdict(list)
    by_path: dict[str, list[str]] = defaultdict(list)
    for item in misconceptions:
        for claim_id in item["mandatory_claim_ids"]:
            by_claim[claim_id].append(item["id"])
        for concept_id in item["mandatory_concept_ids"]:
            by_concept[concept_id].append(item["id"])
        for path in item["source_paths"]:
            by_path[path].append(item["id"])
    return by_claim, by_concept, by_path


def claim_text(claim: dict, passage: Section) -> str:
    citations = ", ".join(claim.get("citation_keys", [])) or "none recorded"
    unresolved = claim.get("unresolved_issue", "").strip() or "none recorded"
    return "\n".join(
        [
            f"Claim {claim['claim_id']}: {claim['claim_text']}",
            f"Claim type: {claim['claim_type']}; verification: {claim['verification']}.",
            f"Exactness object: {claim['exactness_object']}.",
            f"Model scope: {claim['model_scope']}",
            f"Assumptions: {claim['assumptions']}",
            f"Preservation dimensions: {', '.join(claim['preservation_dimensions'])}.",
            f"Evidence type: {claim['evidence_type']}.",
            f"Literature keys: {citations}.",
            f"Unresolved boundary: {unresolved}",
            "",
            f"Supporting passage — {' > '.join(passage.heading_path)}:",
            passage.text,
        ]
    )


def concept_text(concept: dict) -> str:
    lines = [
        f"Vocabulary concept {concept['id']}.",
        f"Preferred house terms: {', '.join(concept['house_terms'])}.",
        f"Relation class: {concept['relation_class']}; usage status: {concept['usage_status']}.",
        f"Required qualifying question: {concept['required_question']}",
        f"Unsafe inference: {concept['unsafe_inference']}",
    ]
    for audience in (
        "power_engineering",
        "software_data",
        "mathematical_modelling",
        "graph_theory",
        "graph_machine_learning",
        "circuit_theory",
    ):
        terms = concept.get(audience, [])
        if terms:
            lines.append(f"{audience.replace('_', ' ').title()}: {', '.join(terms)}.")
    return "\n".join(lines)


def build_records() -> tuple[list[dict], list[Path], dict]:
    claims = tomllib.loads(CLAIMS.read_text()).get("claim", [])
    vocabulary = tomllib.loads(VOCABULARY.read_text())
    concepts = vocabulary.get("concept", [])
    misconception_doc = tomllib.loads(MISCONCEPTIONS.read_text())
    misconceptions = misconception_doc.get("misconception", [])
    release = release_identity()
    by_claim, by_concept, by_path = misconception_maps(misconceptions)

    doc_paths = [
        path
        for path in sorted(DOCS.rglob("*.md"))
        if relative(path) not in EXCLUDED_DOCS
    ]
    sections_by_path: dict[str, list[Section]] = {}
    all_sections: list[Section] = []
    for path in doc_paths:
        parsed = parse_sections(path)
        sections_by_path[relative(path)] = parsed
        all_sections.extend(parsed)

    records: list[dict] = []
    for section in all_sections:
        records.append(
            {
                "schema_version": SCHEMA_VERSION,
                "record_id": f"section:{section.path}#{section.anchor}",
                "record_type": "section",
                "title": " > ".join(section.heading_path),
                "text": section.text,
                "source": source_object(section),
                "heading_path": list(section.heading_path),
                "misconception_ids": sorted(set(by_path.get(section.path, []))),
                "release": release,
            }
        )

    for claim in sorted(claims, key=lambda item: item["claim_id"]):
        chapter_sections = sections_by_path.get(claim["chapter"], [])
        selected, method, score = select_supporting_section(claim, chapter_sections)
        records.append(
            {
                "schema_version": SCHEMA_VERSION,
                "record_id": f"claim:{claim['claim_id']}",
                "record_type": "claim_bundle",
                "title": f"{claim['claim_id']} — {claim['claim_text']}",
                "text": claim_text(claim, selected),
                "source": {
                    "path": claim["chapter"],
                    "anchor": selected.anchor,
                    "line": selected.line,
                    "sha256": selected.sha256,
                },
                "claim": claim,
                "supporting_passage": {
                    "heading_path": list(selected.heading_path),
                    "selection_method": method,
                    "selection_score": score,
                    "text": selected.text,
                },
                "misconception_ids": sorted(set(by_claim.get(claim["claim_id"], []))),
                "release": release,
            }
        )

    for concept in sorted(concepts, key=lambda item: item["id"]):
        source_path = ROOT / concept["definition_path"]
        if not source_path.is_file():
            raise ValueError(f"missing concept definition path: {concept['definition_path']}")
        records.append(
            {
                "schema_version": SCHEMA_VERSION,
                "record_id": f"concept:{concept['id']}",
                "record_type": "concept_bundle",
                "title": f"Vocabulary bridge — {concept['id']}",
                "text": concept_text(concept),
                "source": {
                    "path": concept["definition_path"],
                    "anchor": concept.get("definition_anchor", ""),
                    "sha256": sha256_file(source_path),
                },
                "concept": concept,
                "misconception_ids": sorted(set(by_concept.get(concept["id"], []))),
                "release": release,
            }
        )

    scientific_records = [
        json.loads(line)
        for line in SCIENTIFIC_KNOWLEDGE.read_text().splitlines()
        if line.strip()
    ]
    for scientific in scientific_records:
        if scientific.get("release") != release:
            raise ValueError(
                f"{scientific.get('record_id', '<missing>')}: scientific release identity differs from LLM corpus"
            )
        scientific = dict(scientific)
        scientific["misconception_ids"] = sorted(
            set(scientific.get("book", {}).get("misconception_ids", []))
        )
        records.append(scientific)

    records.sort(key=lambda item: item["record_id"])
    source_paths = [
        CLAIMS, VOCABULARY, MISCONCEPTIONS, EVALUATIONS, HELDOUT,
        SCIENTIFIC_KNOWLEDGE, SCIENTIFIC_MANIFEST, *doc_paths,
    ]
    metadata = {
        "claims": len(claims),
        "concepts": len(concepts),
        "misconceptions": len(misconceptions),
        "sections": len(all_sections),
        "scientific_knowledge": len(scientific_records),
        "heldout_cases": len(tomllib.loads(HELDOUT.read_text()).get("case", [])),
        "release": release,
    }
    return records, source_paths, metadata


def rendered_payloads() -> tuple[str, str]:
    records, source_paths, metadata = build_records()
    corpus = "".join(canonical_json(record) + "\n" for record in records)
    counts = Counter(record["record_type"] for record in records)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "corpus_id": f"multi-graph-book-{metadata['release']['release_candidate_id']}",
        "release": metadata["release"],
        "corpus_sha256": sha256_bytes(corpus.encode()),
        "record_count": len(records),
        "record_counts": dict(sorted(counts.items())),
        "misconception_count": metadata["misconceptions"],
        "evaluation_case_count": len(tomllib.loads(EVALUATIONS.read_text()).get("case", [])),
        "heldout_case_count": metadata["heldout_cases"],
        "document_selection": {
            "included_doc_count": sum(
                path.suffix == ".md" and relative(path).startswith("docs/src/")
                for path in source_paths
            ),
            "excluded_doc_count": len(EXCLUDED_DOCS),
            "excluded_docs": sorted(EXCLUDED_DOCS),
            "excluded_reason": (
                "Generated navigation pages duplicate source ledgers and are excluded from retrieval; "
                "their upstream canonical sources remain included."
            ),
        },
        "source_files": [
            {"path": relative(path), "sha256": sha256_file(path)}
            for path in sorted(set(source_paths), key=relative)
        ],
    }
    return corpus, json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def write_outputs(corpus: str, manifest: str) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(corpus)
    CORPUS_MANIFEST.write_text(manifest)
    print(f"wrote {relative(OUTPUT)} and {relative(CORPUS_MANIFEST)}")


def check_outputs(corpus: str, manifest: str) -> int:
    failures = []
    for path, expected in ((OUTPUT, corpus), (CORPUS_MANIFEST, manifest)):
        if not path.is_file():
            failures.append(f"missing generated output: {relative(path)}")
        elif path.read_text() != expected:
            failures.append(f"stale generated output: {relative(path)}")
    if failures:
        for failure in failures:
            print(failure)
        print("run: python3 scripts/generate_llm_corpus.py --write")
        return 1
    record_count = corpus.count("\n")
    print(f"LLM corpus generation: {record_count} deterministic records pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="regenerate corpus outputs")
    mode.add_argument("--check", action="store_true", help="check committed outputs (default)")
    args = parser.parse_args()
    try:
        corpus, manifest = rendered_payloads()
    except (OSError, ValueError, KeyError, tomllib.TOMLDecodeError, json.JSONDecodeError) as error:
        print(f"LLM corpus generation failed: {error}")
        return 1
    if args.write:
        write_outputs(corpus, manifest)
        return 0
    return check_outputs(corpus, manifest)


if __name__ == "__main__":
    sys.exit(main())
