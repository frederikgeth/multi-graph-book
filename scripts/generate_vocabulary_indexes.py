#!/usr/bin/env python3
"""Generate bidirectional cross-community vocabulary indexes from the registry."""

from __future__ import annotations

import argparse
import os
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "vocabulary/vocabulary.toml"
OUTPUT = ROOT / "docs/src/reference/vocabulary-indexes.md"

COMMUNITY_LABELS = {
    "power_engineering": "Power engineering",
    "software_data": "Software and network data",
    "mathematical_modelling": "Mathematical modelling and optimization",
    "graph_theory": "Mathematical graph theory",
    "graph_machine_learning": "Graph machine learning",
    "circuit_theory": "Circuit theory (shared technical vocabulary)",
}

RELATION_LABELS = {
    "exact_alias": "exact alias",
    "scoped_alias": "scoped alias",
    "broader_narrower": "broader / narrower",
    "representation_dependent": "representation dependent",
    "false_friend": "false friend",
}

STATUS_LABELS = {
    "preferred_house_term": "preferred house term",
    "accepted_qualified_shorthand": "accepted qualified shorthand",
    "unsafe_unqualified_term": "unsafe unqualified term",
}


def cell(values: list[str]) -> str:
    return "; ".join(f"`{value}`" for value in values) if values else "—"


def route(concept: dict[str, object]) -> str:
    target = ROOT / str(concept["definition_path"])
    relative = Path(os.path.relpath(target, OUTPUT.parent)).as_posix()
    anchor = str(concept.get("definition_anchor", ""))
    href = f"{relative}#{anchor}" if anchor else relative
    return f"[definition]({href})"


def render(registry: dict[str, object]) -> str:
    concepts = list(registry["concept"])
    targets = list(registry["target_communities"])
    shared = list(registry["shared_technical_vocabularies"])
    lines = [
        "# [Cross-community vocabulary indexes](@id vocabulary-indexes)",
        "",
        "**Page status:** generated bidirectional vocabulary index; not a standards crosswalk.",
        "",
        "This page is generated from `vocabulary/vocabulary.toml`. It does not declare",
        "community terms to be synonyms. Each row records a dominant relation class, an",
        "editorial usage status, a diagnostic question, and a route to the maintained",
        "definition. The conceptual introduction remains [One network, five languages](@ref",
        "one-network-five-languages); the compact house definitions remain on the",
        "[Terminology](@ref) page.",
        "",
        "The five target communities are indexed separately. Circuit theory is included",
        "after them as shared technical vocabulary rather than as a sixth audience route.",
        "",
        "## Relation and usage keys",
        "",
        "The **relation class** describes the map between a community phrase and the house",
        "vocabulary. The **usage status** describes how the phrase may be used in this book.",
        "These axes are orthogonal.",
        "",
        "| Registry value | Reader-facing meaning |",
        "| --- | --- |",
    ]
    for key in registry["relation_classes"]:
        lines.append(f"| `{key}` | {RELATION_LABELS[key]} |")
    for key in registry["usage_statuses"]:
        lines.append(f"| `{key}` | {STATUS_LABELS[key]} |")

    lines += ["", "## Community-to-book index", ""]
    for community in targets + shared:
        lines += [f"### {COMMUNITY_LABELS[community]}", ""]
        lines += [
            "| Familiar terms | House terms | Relation / usage | Diagnostic question | Unsafe inference | Route |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for concept in concepts:
            terms = concept[community]
            if not terms:
                continue
            relation = RELATION_LABELS[concept["relation_class"]]
            status = STATUS_LABELS[concept["usage_status"]]
            lines.append(
                f"| {cell(terms)} | {cell(concept['house_terms'])} | {relation}; {status} | "
                f"{concept['required_question']} | {concept['unsafe_inference']} | {route(concept)} |"
            )
        lines.append("")

    lines += [
        "## Book-to-community index",
        "",
        "Use this view when a house term is familiar but the language likely to appear in",
        "another community is not. Blank cells are meaningful: the registry does not invent",
        "an alias merely to complete a row.",
        "",
        "| House-term cluster | Power engineering | Software / data | Mathematical modelling | Graph theory | Graph ML | Circuit theory | Relation | Route |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for concept in concepts:
        lines.append(
            f"| {cell(concept['house_terms'])} | {cell(concept['power_engineering'])} | "
            f"{cell(concept['software_data'])} | {cell(concept['mathematical_modelling'])} | "
            f"{cell(concept['graph_theory'])} | {cell(concept['graph_machine_learning'])} | "
            f"{cell(concept['circuit_theory'])} | {RELATION_LABELS[concept['relation_class']]} | "
            f"{route(concept)} |"
        )

    lines += [
        "",
        "## Scope and review boundary",
        "",
        f"This first registry contains {len(concepts)} collision concepts. It is a controlled",
        "book vocabulary, not an empirical claim that every practitioner uses the recorded",
        "terms identically. Community review remains required. Changes should update the",
        "registry first and regenerate this page rather than editing the generated tables.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the generated page is stale")
    args = parser.parse_args()
    registry = tomllib.loads(REGISTRY.read_text())
    content = render(registry)
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text() != content:
            print(f"vocabulary index is stale relative to {REGISTRY.relative_to(ROOT)}")
            return 1
        print(f"vocabulary index: {len(registry['concept'])} concepts are current")
        return 0
    OUTPUT.write_text(content)
    print(f"generated {OUTPUT.relative_to(ROOT)} from {len(registry['concept'])} concepts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
