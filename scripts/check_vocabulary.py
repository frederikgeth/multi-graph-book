#!/usr/bin/env python3
"""Validate the controlled cross-community vocabulary registry."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "vocabulary/vocabulary.toml"

TARGETS = {
    "power_engineering",
    "software_data",
    "mathematical_modelling",
    "graph_theory",
    "graph_machine_learning",
}
SHARED = {"circuit_theory"}
RELATIONS = {
    "exact_alias",
    "scoped_alias",
    "broader_narrower",
    "representation_dependent",
    "false_friend",
}
STATUSES = {
    "preferred_house_term",
    "accepted_qualified_shorthand",
    "unsafe_unqualified_term",
}
REQUIRED_CONCEPTS = {
    "object-node-interface",
    "element-edge-relation",
    "factor",
    "graph-topology-adjacency",
    "direction-orientation-hierarchy",
    "flow-current-power-message",
    "parallel",
    "mutual-coupling-relation",
    "cycle-radial-tree",
    "state",
    "rating-limit-constraint",
    "equivalence-exactness-preservation",
    "transformation-family",
    "normalization",
    "loss",
    "ground-neutral-reference",
    "phase-conductor-sequence-coordinate",
    "nodal-operator-alias",
}


def main() -> int:
    data = tomllib.loads(REGISTRY.read_text())
    errors: list[str] = []

    if data.get("schema_version") != "0.1.0":
        errors.append("unexpected vocabulary schema version")
    if set(data.get("target_communities", [])) != TARGETS:
        errors.append("target community set is incomplete or uncontrolled")
    if set(data.get("shared_technical_vocabularies", [])) != SHARED:
        errors.append("shared technical vocabulary set is incomplete or uncontrolled")
    if set(data.get("relation_classes", [])) != RELATIONS:
        errors.append("relation-class vocabulary is incomplete or uncontrolled")
    if set(data.get("usage_statuses", [])) != STATUSES:
        errors.append("usage-status vocabulary is incomplete or uncontrolled")

    concepts = data.get("concept", [])
    ids: set[str] = set()
    community_coverage = {community: 0 for community in TARGETS | SHARED}
    fields = {
        "id",
        "house_terms",
        "relation_class",
        "usage_status",
        "required_question",
        "unsafe_inference",
        "definition_path",
        "definition_anchor",
        *TARGETS,
        *SHARED,
    }
    for concept in concepts:
        concept_id = concept.get("id", "<unknown>")
        missing = fields - set(concept)
        if missing:
            errors.append(f"{concept_id} missing fields: {sorted(missing)}")
            continue
        if concept_id in ids:
            errors.append(f"duplicate concept id: {concept_id}")
        ids.add(concept_id)
        if concept["relation_class"] not in RELATIONS:
            errors.append(f"{concept_id} has unknown relation class")
        if concept["usage_status"] not in STATUSES:
            errors.append(f"{concept_id} has unknown usage status")
        for field in ("required_question", "unsafe_inference"):
            if not isinstance(concept[field], str) or not concept[field].strip():
                errors.append(f"{concept_id} has empty {field}")
        house_terms = concept["house_terms"]
        if not isinstance(house_terms, list) or not house_terms or len(house_terms) != len(set(house_terms)):
            errors.append(f"{concept_id} house terms must be a unique nonempty array")
        for community in TARGETS | SHARED:
            terms = concept[community]
            if not isinstance(terms, list) or len(terms) != len(set(terms)):
                errors.append(f"{concept_id}.{community} must be a unique array")
            elif terms:
                community_coverage[community] += 1

        target = ROOT / concept["definition_path"]
        if not target.is_file():
            errors.append(f"{concept_id} definition path does not exist: {concept['definition_path']}")
        elif concept["definition_anchor"]:
            marker = f"(@id {concept['definition_anchor']})"
            if marker not in target.read_text():
                errors.append(f"{concept_id} definition anchor is absent: {concept['definition_anchor']}")

    if ids != REQUIRED_CONCEPTS:
        errors.append(f"concept set differs from the controlled initial set: {sorted(ids ^ REQUIRED_CONCEPTS)}")
    if not any(concept.get("relation_class") == "exact_alias" for concept in concepts):
        errors.append("registry does not exercise the exact-alias class")
    if not any(concept.get("usage_status") == "preferred_house_term" for concept in concepts):
        errors.append("registry does not exercise the preferred-house-term status")
    for community, count in sorted(community_coverage.items()):
        if count == 0:
            errors.append(f"registry does not exercise the {community} vocabulary")

    if errors:
        print("vocabulary registry audit failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(
        f"vocabulary registry: {len(concepts)} concepts, {len(TARGETS)} target communities, "
        f"and {len(SHARED)} shared technical vocabulary pass"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
