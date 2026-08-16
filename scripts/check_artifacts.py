#!/usr/bin/env python3
"""Check local links, generated artifacts, claims, and view provenance."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data/running-network/v0.1.0.json"
TRANSFORMER_CONTRACT = ROOT / "data/transformer-contracts/x1-fixed-linear-v0.1.0.json"
TRANSFORMER_TAP_CONTRACT = ROOT / "data/transformer-contracts/x1-discrete-tap-v0.1.0.json"
TRANSFORMER_CONTRACTS = (TRANSFORMER_CONTRACT, TRANSFORMER_TAP_CONTRACT)
GENERATED = ROOT / "experiments/generated"
PORT_FACTOR_ARCHITECTURE = GENERATED / "port-factor-architecture.json"
FIVE_BUS_PORT_FACTOR = GENERATED / "five-bus-port-factor-witness.json"
TOPOLOGY_PROJECTION_WITNESS = GENERATED / "topology-projection-witness.json"
NODAL_SOURCE_RECOVERY_WITNESS = GENERATED / "nodal-source-recovery-witness.json"
NODAL_RECOVERY_GUARDS_WITNESS = GENERATED / "nodal-recovery-guards-witness.json"
MULTICONDUCTOR_RECOVERY_WITNESS = GENERATED / "multiconductor-recovery-witness.json"
NOISY_MULTICONDUCTOR_RECOVERY_WITNESS = GENERATED / "noisy-multiconductor-recovery-witness.json"
NONLINEAR_GROUNDING_LOCAL_BOUND = GENERATED / "nonlinear-grounding-local-bound-witness.json"
POSITIVE_SEQUENCE_WITNESS = GENERATED / "positive-sequence-collapse-witness.json"
FOUR_WIRE_IMPEDANCE_LADDER = GENERATED / "four-wire-impedance-model-ladder.json"
BALANCED_TRANSMISSION_WITNESS = GENERATED / "balanced-transmission-witness.json"
BALANCED_TRANSMISSION_REPRODUCTION = GENERATED / "balanced-transmission-independent-reproduction.json"
KRON_WARD_SCENARIO = GENERATED / "kron-ward-scenario-comparison.json"
CERTIFIED_APPROXIMATION = GENERATED / "certified-approximation-witness.json"
NONLINEAR_WARD_WITNESS = GENERATED / "nonlinear-ward-witness.json"
SOLVER_DIAGNOSTICS_CROSSWALK = GENERATED / "solver-diagnostics-crosswalk.json"
DATA_MODEL_CROSSWALK = GENERATED / "data-model-crosswalk-witness.json"
RUNNING_NETWORK_TYPED_KRON = GENERATED / "running-network-typed-kron-witness.json"
GUARDED_PARALLEL_REDUCTION = GENERATED / "guarded-parallel-reduction-witness.json"
THREE_MEMBER_FOUR_WIRE_PARALLEL_AC = GENERATED / "three-member-four-wire-parallel-ac-certificate.json"
THREE_MEMBER_STATE_REPRODUCTION = GENERATED / "three-member-state-envelope-independent-reproduction.json"
TRANSFORMER_CONTROL_FAMILY = GENERATED / "transformer-control-family-witness.json"
TRANSFORMER_TAP_AC = GENERATED / "transformer-tap-ac-decision-certificate.json"
TRANSFORMER_TAP_THREE_SCENARIO_REPRO = GENERATED / "transformer-tap-three-scenario-independent-certificate.json"
NODE_BREAKER_STATE = GENERATED / "node-breaker-state-witness.json"
COMPILED_VIEWS_SURGERY = GENERATED / "compiled-views-surgery-witness.json"
LOAD_GROUNDING_WITNESS = GENERATED / "load-grounding-witnesses.json"
LOAD_MODEL_REPRODUCTION = GENERATED / "load-model-independent-reproduction.json"
CONNECTION_MAP_REPRODUCTION = GENERATED / "connection-map-independent-reproduction.json"
LOAD_CONTINUATION_REPRODUCTION = GENERATED / "load-continuation-independent-reproduction.json"
NEUTRAL_KRON_REPRODUCTION = GENERATED / "neutral-kron-independent-reproduction.json"
EXPLICIT_EARTH_KRON_WITNESS = GENERATED / "explicit-earth-kron-witness.json"
EXPLICIT_EARTH_KRON_REPRODUCTION = GENERATED / "explicit-earth-kron-independent-reproduction.json"
GROUNDING_IMPEDANCE_SWEEP = GENERATED / "grounding-impedance-sweep-witness.json"
GROUNDING_IMPEDANCE_REPRODUCTION = GENERATED / "grounding-impedance-sweep-independent-reproduction.json"
NONLINEAR_GROUNDING_PROBE = GENERATED / "nonlinear-grounding-probe-witness.json"
NONLINEAR_GROUNDING_REPRODUCTION = GENERATED / "nonlinear-grounding-probe-independent-reproduction.json"
NONLINEAR_TWO_POINT_GROUNDING = GENERATED / "nonlinear-two-point-grounding-witness.json"
NONLINEAR_TWO_POINT_REPRODUCTION = GENERATED / "nonlinear-two-point-grounding-independent-reproduction.json"
NONLINEAR_TWO_POINT_CONTINUATION = GENERATED / "nonlinear-two-point-grounding-continuation.json"
NONLINEAR_TWO_POINT_CONTINUATION_REPRODUCTION = GENERATED / "nonlinear-two-point-grounding-continuation-independent-reproduction.json"
EXPLICIT_EARTH_REPRODUCTION = GENERATED / "explicit-earth-independent-reproduction.json"
RUNNING_NETWORK_RADIALITY = GENERATED / "running-network-radiality-witness.json"
FIVE_BUS_ACTIVE_RADIALITY = GENERATED / "five-bus-active-radiality-witness.json"
FIVE_BUS_TYPED_KRON = GENERATED / "five-bus-typed-kron-witness.json"
CONDUCTOR_TERMINAL_LIFT = GENERATED / "conductor-terminal-lift-witness.json"
FIVE_BUS_CONDUCTOR_TERMINAL_LIFT = GENERATED / "five-bus-conductor-terminal-lift-witness.json"
FIVE_BUS_TRANSFORMER_LOWERING = GENERATED / "five-bus-transformer-lowering-witness.json"
MULTIWINDING_TERMINAL_LIFT = GENERATED / "multiwinding-terminal-lift-witness.json"
MULTIWINDING_TYPED_KRON = GENERATED / "multiwinding-typed-kron-witness.json"
HIERARCHY_BOUNDARY = GENERATED / "hierarchy-boundary-witness.json"
PUBLIC_API_MANIFEST = GENERATED / "public-api-manifest.json"
STATE_SPACE_UNIT = GENERATED / "state-space-unit-witness.json"
SEMANTIC_EVALUATOR_MATRIX = GENERATED / "semantic-evaluator-matrix.json"
FIXTURE_COVERAGE_MATRIX = GENERATED / "fixture-coverage-matrix.json"
CLEAN_PACKAGE_MATRIX = GENERATED / "clean-package-matrix.json"
STANDALONE_PACKAGE = ROOT / "package/GraphModelsForPowerNetworks"
FIGURE = ROOT / "docs/src/assets/running-network-views.png"
FIGURE_AUDIT = ROOT / "docs/src/assets/figure-audit.json"
FIVE_BUS_ANALYSIS = GENERATED / "five-bus-cycle-space-analysis.json"
NUMERICAL_STRUCTURE_WITNESS = GENERATED / "numerical-structure-witness.json"
NUMERICAL_FILL_FIGURE = ROOT / "docs/src/assets/numerical-fill-in.svg"
NUMERICAL_JACOBIAN_FIGURE = ROOT / "docs/src/assets/numerical-jacobian-dependency.svg"
YBUS_JACOBIAN_WITNESS = GENERATED / "ybus-jacobian-witness.json"
YBUS_JACOBIAN_FIGURE = ROOT / "docs/src/assets/ybus-jacobian-witness.svg"
NONLINEAR_KKT_WITNESS = GENERATED / "nonlinear-kkt-witness.json"
NARROW_CIRCUIT_TRANSFORMATIONS = GENERATED / "narrow-circuit-transformations-witness.json"
NONLINEAR_KKT_FIGURE = ROOT / "docs/src/assets/nonlinear-kkt-witness.svg"
PRESERVATION_CONTRACT_CARD = ROOT / "docs/src/assets/preservation-contract-card.svg"
EARTH_RETURN_LADDER = ROOT / "docs/src/assets/earth-return-ladder.svg"
TRANSFORMER_ANATOMY = ROOT / "docs/src/assets/transformer-anatomy.svg"
PARALLEL_FEASIBLE_SET_CARD = ROOT / "docs/src/assets/parallel-feasible-set-card.svg"
KNOWLEDGE_BASE_INDEX = ROOT / "docs/src/reference/knowledge-base-index.md"
CHAPTER_STATUS = ROOT / "docs/src/reference/chapter-status.md"
PAGE_STATUS = re.compile(r"^\*\*Page status:\*\*[ \t]*(?P<status>[^\r\n]+)$", re.MULTILINE)
FIVE_BUS_FIGURES = {
    "cycle_basis": ROOT / "docs/src/assets/five-bus-cycle-basis.png",
    "transformation_map": ROOT / "docs/src/assets/five-bus-transformation-map.png",
    "feasible_sets": ROOT / "docs/src/assets/five-bus-feasible-sets.png",
}
FIVE_BUS_FIGURE_MANIFEST = GENERATED / "five-bus-figure-manifest.json"
SOURCE_MAP = GENERATED / "view-source-maps.json"
CLEAN_REPRODUCTION = GENERATED / "clean-reproduction"
CERTIFICATE_SCHEMA = ROOT / "schemas/transformation-certificate.schema.json"
CERTIFICATES = (
    "parallel-branch-certificate.json",
    "degree-two-series-certificate.json",
    "coordinate-normalization-certificate.json",
    "coordinate-series-composition-certificate.json",
    "parallel-opf-comparison.json",
    "transformer-winding-normalization-certificate.json",
    "multiwinding-leakage-compilation-certificate.json",
    "multiwinding-terminal-assembly-certificate.json",
    "transformer-factor-completion-certificate.json",
    "transformer-tap-decision-certificate.json",
    "transformer-tap-ac-decision-certificate.json",
    "transformer-tap-ac-independent-certificate.json",
    "multiconductor-parallel-ac-certificate.json",
    "four-wire-parallel-ac-certificate.json",
    "pi-four-wire-parallel-ac-certificate.json",
    "typed-kron-certificate.json",
)
EXPECTED_VIEWS = {
    "asset_property",
    "terminal_connectivity",
    "bus_branch_multigraph",
    "simple_topology",
    "port_factor",
    "opf_equation",
    "sparsity",
}
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)|!\[[^\]]*\]\(([^)]+)\)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    with path.open() as stream:
        return json.load(stream)


def source_ids(network: dict) -> set[str]:
    result: set[str] = set()
    for family in ("bus", "line", "switch", "shunt", "load", "generator", "voltage_source"):
        result.update(f"{family}/{identifier}" for identifier in network.get(family, {}))
    for family, devices in network.get("transformer", {}).items():
        result.update(f"transformer/{family}/{identifier}" for identifier in devices)
    return result


def validate_certificate(certificate: dict, schema: dict, artifact: str) -> list[str]:
    errors: list[str] = []
    required = set(schema["required"])
    missing = required - set(certificate)
    extra = set(certificate) - set(schema["properties"])
    if missing:
        errors.append(f"{artifact} is missing schema fields {sorted(missing)}")
    if extra:
        errors.append(f"{artifact} has undeclared schema fields {sorted(extra)}")
    if certificate.get("schema_version") != "1.1.0":
        errors.append(f"{artifact} has unsupported schema version")
    if not re.fullmatch(r"TR-[A-Z]+-[0-9]{3}", certificate.get("certificate_id", "")):
        errors.append(f"{artifact} has an invalid certificate ID")
    classifications = schema["properties"]["classification"]["enum"]
    if certificate.get("classification") not in classifications:
        errors.append(f"{artifact} has an invalid classification")
    for side in ("source", "target"):
        model = certificate.get(side)
        if not isinstance(model, dict):
            errors.append(f"{artifact} {side} is not an object")
            continue
        if not isinstance(model.get("model_category"), str) or not model["model_category"]:
            errors.append(f"{artifact} {side} lacks a model category")
        object_ids = model.get("object_ids")
        if (
            not isinstance(object_ids, list)
            or not object_ids
            or not all(isinstance(item, str) and item for item in object_ids)
            or len(object_ids) != len(set(object_ids))
        ):
            errors.append(f"{artifact} {side} object IDs must be unique nonempty strings")
    for field in ("preconditions", "preserves", "forgets"):
        values = certificate.get(field)
        if (
            not isinstance(values, list)
            or not all(isinstance(item, str) for item in values)
            or len(values) != len(set(values))
        ):
            errors.append(f"{artifact} {field} must contain unique strings")
    for field in ("recovery_map", "constraint_map"):
        mapping = certificate.get(field)
        if not isinstance(mapping, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in mapping.items()
        ):
            errors.append(f"{artifact} {field} must map strings to strings")
    for field in ("provenance", "evidence"):
        if not isinstance(certificate.get(field), dict):
            errors.append(f"{artifact} {field} must be an object")
    interfaces = certificate.get("interfaces")
    interface_fields = (
        "state_variables", "constraints", "decisions", "objectives", "units", "boundary_quantities"
    )
    if not isinstance(interfaces, dict) or set(interfaces) != set(interface_fields):
        errors.append(f"{artifact} interfaces must contain the six typed interface fields")
    else:
        for name in interface_fields:
            mapping = interfaces[name]
            if not isinstance(mapping, dict) or set(mapping) != {"source", "target", "relation"}:
                errors.append(f"{artifact} interfaces.{name} has an invalid shape")
                continue
            for side in ("source", "target"):
                values = mapping[side]
                if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
                    errors.append(f"{artifact} interfaces.{name}.{side} must be a string array")
            if not isinstance(mapping["relation"], str) or not mapping["relation"]:
                errors.append(f"{artifact} interfaces.{name}.relation must be a nonempty string")
    typed = certificate.get("typed_interfaces")
    typed_fields = {
        "state_space_ref",
        "source_variable_labels",
        "target_variable_labels",
        "source_unit_families",
        "target_unit_families",
        "source_boundary_labels",
        "target_boundary_labels",
        "state_domain_ids",
        "unit_family_map",
        "unresolved_unit_labels",
        "attachment_rule",
    }
    if not isinstance(typed, dict) or set(typed) != typed_fields:
        errors.append(f"{artifact} typed_interfaces has an invalid shape")
    else:
        if not isinstance(typed["state_space_ref"], str) or not typed["state_space_ref"]:
            errors.append(f"{artifact} typed_interfaces.state_space_ref must be nonempty")
        for field in (
            "source_variable_labels", "target_variable_labels", "source_unit_families",
            "target_unit_families", "source_boundary_labels", "target_boundary_labels",
            "state_domain_ids", "unresolved_unit_labels",
        ):
            values = typed[field]
            if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
                errors.append(f"{artifact} typed_interfaces.{field} must be a string array")
            elif len(values) != len(set(values)):
                errors.append(f"{artifact} typed_interfaces.{field} must be unique")
        unit_map = typed["unit_family_map"]
        if not isinstance(unit_map, dict) or not all(
            isinstance(key, str)
            and isinstance(value, list)
            and all(isinstance(family, str) for family in value)
            and len(value) == len(set(value))
            for key, value in unit_map.items()
        ):
            errors.append(f"{artifact} typed_interfaces.unit_family_map has an invalid shape")
        if not isinstance(typed["attachment_rule"], str) or not typed["attachment_rule"]:
            errors.append(f"{artifact} typed_interfaces.attachment_rule must be nonempty")
    return errors


def is_complex_value(value) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"real", "imag"}
        and all(isinstance(value[key], (int, float)) for key in ("real", "imag"))
    )


def validate_transformer_contract(contract: dict, network: dict, contract_path: Path) -> list[str]:
    errors: list[str] = []
    prefix = contract_path.relative_to(ROOT)
    if contract.get("schema_version") != "0.1.0":
        errors.append(f"{prefix} has an unsupported schema version")
    if contract.get("voltage_transfer_convention") != (
        "v_leakage_xkc = coefficient_xkc * v_connected_coil_xkc"
    ):
        errors.append(f"{prefix} has an unsupported voltage-transfer convention")
    transformer_id = contract.get("transformer_id")
    source = network.get("transformer", {}).get("n_winding", {}).get(transformer_id)
    if source is None:
        return errors + [f"{prefix} references an unknown n-winding transformer"]
    source_windings = source.get("windings", [])
    transfers = contract.get("winding_transfers")
    if not isinstance(transfers, list) or len(transfers) != len(source_windings):
        return errors + [f"{prefix} must contain one transfer per source winding"]
    for position, (transfer, winding) in enumerate(zip(transfers, source_windings), start=1):
        expected_terminals = winding.get("terminal_map", [])
        expected_coils = (
            [label for label in expected_terminals if label != "n"]
            if winding.get("configuration") == "WYE"
            else expected_terminals
        )
        if transfer.get("winding_position") != position:
            errors.append(f"{prefix} transfer {position} has the wrong winding position")
        if transfer.get("winding_id") != f"{transformer_id}/winding/{position}":
            errors.append(f"{prefix} transfer {position} has the wrong winding identity")
        if transfer.get("terminal_order") != expected_terminals:
            errors.append(f"{prefix} transfer {position} does not retain terminal order")
        if set(transfer.get("coil_order", [])) != set(expected_coils):
            errors.append(f"{prefix} transfer {position} does not retain coil identities")
        coefficients = transfer.get("coefficient")
        if (
            not isinstance(coefficients, list)
            or len(coefficients) != len(expected_coils)
            or not all(is_complex_value(value) for value in coefficients)
        ):
            errors.append(f"{prefix} transfer {position} has invalid coefficients")
        mode = transfer.get("control_mode")
        if mode not in {"fixed", "continuous", "discrete"}:
            errors.append(f"{prefix} transfer {position} has an invalid control mode")
        if mode != "fixed" and not transfer.get("decision_id"):
            errors.append(f"{prefix} adjustable transfer {position} lacks a decision identity")
        if mode != "fixed":
            attributes = transfer.get("attributes", {})
            if attributes.get("coefficient_parameterization") != (
                "coefficient_xkc(tap) = tap * base_coefficient_xkc"
            ):
                errors.append(f"{prefix} adjustable transfer {position} has an invalid parameterization")
            start = attributes.get("tap_start")
            if not isinstance(start, (int, float)) or start <= 0:
                errors.append(f"{prefix} adjustable transfer {position} has an invalid start")
            if mode == "continuous":
                lower, upper = attributes.get("tap_min"), attributes.get("tap_max")
                if not all(isinstance(value, (int, float)) for value in (lower, upper)) or not 0 < lower < upper:
                    errors.append(f"{prefix} continuous transfer {position} has invalid bounds")
            elif mode == "discrete":
                positions = attributes.get("tap_positions")
                if (
                    not isinstance(positions, list)
                    or not positions
                    or not all(isinstance(value, (int, float)) and value > 0 for value in positions)
                    or positions != sorted(set(positions))
                    or start not in positions
                ):
                    errors.append(f"{prefix} discrete transfer {position} has invalid positions")
    shunt = contract.get("excitation_shunt")
    if shunt is not None:
        coil_order = shunt.get("coil_order", [])
        rows = shunt.get("admittance_S")
        if (
            not isinstance(rows, list)
            or len(rows) != len(coil_order)
            or not all(isinstance(row, list) and len(row) == len(coil_order) for row in rows)
            or not all(is_complex_value(value) for row in rows for value in row)
        ):
            errors.append(f"{prefix} has an invalid excitation admittance matrix")
    for grounding in contract.get("internal_groundings", []):
        position = grounding.get("winding_position")
        if grounding.get("scope") != "transformer_internal":
            errors.append(f"{prefix} contains non-internal grounding")
        if not isinstance(position, int) or not 1 <= position <= len(source_windings):
            errors.append(f"{prefix} contains grounding with an invalid winding position")
            continue
        if grounding.get("terminal") not in source_windings[position - 1].get("terminal_map", []):
            errors.append(f"{prefix} grounding references an unknown terminal")
        if not is_complex_value(grounding.get("admittance_S")):
            errors.append(f"{prefix} grounding has an invalid admittance")
    return errors


def check_links(errors: list[str]) -> int:
    checked = 0
    candidates = [ROOT / name for name in ("README.md", "ROADMAP.md", "HANDOVER.md", "BOOK_PLAN.md", "CONTRIBUTING.md")]
    candidates += sorted((ROOT / "docs/src").rglob("*.md"))
    candidates += sorted((ROOT / "review").rglob("*.md")) if (ROOT / "review").exists() else []
    for document in candidates:
        if not document.is_file():
            continue
        for match in LINK.finditer(document.read_text()):
            destination = next(group for group in match.groups() if group is not None).strip()
            if destination.startswith(("http://", "https://", "mailto:", "#", "@ref", "@cite", "@id")):
                continue
            if " " in destination and not destination.startswith("<"):
                destination = destination.split(" ", 1)[0]
            destination = unquote(destination.strip("<> ")).split("#", 1)[0]
            if not destination:
                continue
            checked += 1
            target = Path(destination)
            target = target if target.is_absolute() else (document.parent / target).resolve()
            if not target.exists():
                errors.append(f"broken local link in {document.relative_to(ROOT)}: {destination}")
    return checked


def main() -> int:
    errors: list[str] = []
    required = [
        FIXTURE,
        *TRANSFORMER_CONTRACTS,
        FIGURE,
        FIGURE_AUDIT,
        *FIVE_BUS_FIGURES.values(),
        GENERATED / "summary.json",
        FIVE_BUS_ANALYSIS,
        GENERATED / "running-network-cycle-space-witness.json",
        NUMERICAL_STRUCTURE_WITNESS,
        NUMERICAL_FILL_FIGURE,
        NUMERICAL_JACOBIAN_FIGURE,
        YBUS_JACOBIAN_WITNESS,
        YBUS_JACOBIAN_FIGURE,
        NONLINEAR_KKT_WITNESS,
        NARROW_CIRCUIT_TRANSFORMATIONS,
        NONLINEAR_KKT_FIGURE,
        PRESERVATION_CONTRACT_CARD,
        EARTH_RETURN_LADDER,
        TRANSFORMER_ANATOMY,
        PARALLEL_FEASIBLE_SET_CARD,
        KNOWLEDGE_BASE_INDEX,
        CHAPTER_STATUS,
        FIVE_BUS_FIGURE_MANIFEST,
        CERTIFICATE_SCHEMA,
        *(GENERATED / artifact for artifact in CERTIFICATES),
        GENERATED / "provenance.json",
        PORT_FACTOR_ARCHITECTURE,
        FIVE_BUS_PORT_FACTOR,
        TOPOLOGY_PROJECTION_WITNESS,
        NODAL_SOURCE_RECOVERY_WITNESS,
        NODAL_RECOVERY_GUARDS_WITNESS,
        MULTICONDUCTOR_RECOVERY_WITNESS,
        NOISY_MULTICONDUCTOR_RECOVERY_WITNESS,
        NONLINEAR_GROUNDING_LOCAL_BOUND,
        POSITIVE_SEQUENCE_WITNESS,
        FOUR_WIRE_IMPEDANCE_LADDER,
        BALANCED_TRANSMISSION_WITNESS,
        BALANCED_TRANSMISSION_REPRODUCTION,
        KRON_WARD_SCENARIO,
        CERTIFIED_APPROXIMATION,
        NONLINEAR_WARD_WITNESS,
        SOLVER_DIAGNOSTICS_CROSSWALK,
        DATA_MODEL_CROSSWALK,
        RUNNING_NETWORK_TYPED_KRON,
        GUARDED_PARALLEL_REDUCTION,
        THREE_MEMBER_FOUR_WIRE_PARALLEL_AC,
        THREE_MEMBER_STATE_REPRODUCTION,
        TRANSFORMER_CONTROL_FAMILY,
        TRANSFORMER_TAP_THREE_SCENARIO_REPRO,
        NODE_BREAKER_STATE,
        COMPILED_VIEWS_SURGERY,
        LOAD_GROUNDING_WITNESS,
        LOAD_MODEL_REPRODUCTION,
        CONNECTION_MAP_REPRODUCTION,
        LOAD_CONTINUATION_REPRODUCTION,
        NEUTRAL_KRON_REPRODUCTION,
        EXPLICIT_EARTH_KRON_WITNESS,
        EXPLICIT_EARTH_KRON_REPRODUCTION,
        GROUNDING_IMPEDANCE_SWEEP,
        GROUNDING_IMPEDANCE_REPRODUCTION,
        NONLINEAR_GROUNDING_PROBE,
        NONLINEAR_GROUNDING_REPRODUCTION,
        NONLINEAR_TWO_POINT_GROUNDING,
        NONLINEAR_TWO_POINT_REPRODUCTION,
        NONLINEAR_TWO_POINT_CONTINUATION,
        NONLINEAR_TWO_POINT_CONTINUATION_REPRODUCTION,
        EXPLICIT_EARTH_REPRODUCTION,
        RUNNING_NETWORK_RADIALITY,
        FIVE_BUS_ACTIVE_RADIALITY,
        FIVE_BUS_TYPED_KRON,
        CONDUCTOR_TERMINAL_LIFT,
        FIVE_BUS_CONDUCTOR_TERMINAL_LIFT,
        MULTIWINDING_TERMINAL_LIFT,
        MULTIWINDING_TYPED_KRON,
        HIERARCHY_BOUNDARY,
        PUBLIC_API_MANIFEST,
        STATE_SPACE_UNIT,
        SEMANTIC_EVALUATOR_MATRIX,
        FIXTURE_COVERAGE_MATRIX,
        CLEAN_PACKAGE_MATRIX,
        STANDALONE_PACKAGE / "Project.toml",
        STANDALONE_PACKAGE / "README.md",
        STANDALONE_PACKAGE / "src/GraphModelsForPowerNetworks.jl",
        STANDALONE_PACKAGE / "src/MultigraphCycleSpace.jl",
        STANDALONE_PACKAGE / "src/TypedKronReduction.jl",
        STANDALONE_PACKAGE / "src/TypedStateSpace.jl",
        STANDALONE_PACKAGE / "src/TransformationContracts.jl",
        STANDALONE_PACKAGE / "test/runtests.jl",
        GENERATED / "typed-kron-witness.json",
        SOURCE_MAP,
        CLEAN_REPRODUCTION / "v0.1.0.json",
        CLEAN_REPRODUCTION / "summary.json",
        CLEAN_REPRODUCTION / "provenance.json",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required artifact: {path.relative_to(ROOT)}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    network = load_json(FIXTURE)
    for contract_path in TRANSFORMER_CONTRACTS:
        errors.extend(validate_transformer_contract(load_json(contract_path), network, contract_path))
    sources = source_ids(network)
    summary = load_json(GENERATED / "summary.json")
    fixture_version = network.get("meta", {}).get("version")
    if summary.get("fixture_version") != fixture_version:
        errors.append("fixture version differs between fixture and summary")

    claims = tomllib.loads((ROOT / "claims/claims.toml").read_text()).get("claim", [])
    claim_ids = {claim["claim_id"] for claim in claims}
    claims_hash = sha256(ROOT / "claims/claims.toml")
    for generated_page in (KNOWLEDGE_BASE_INDEX, CHAPTER_STATUS):
        first_lines = generated_page.read_text().splitlines()[:4]
        stamp = next((line for line in first_lines if "generated-from claims/claims.toml sha256:" in line), "")
        if not stamp.endswith(claims_hash + " -->"):
            errors.append(f"{generated_page.relative_to(ROOT)} is stale relative to claims/claims.toml")

    for chapter_path in sorted((ROOT / "docs/src").rglob("*.md")):
        if chapter_path in (KNOWLEDGE_BASE_INDEX, CHAPTER_STATUS):
            continue
        chapter = chapter_path.relative_to(ROOT).as_posix()
        if PAGE_STATUS.search(chapter_path.read_text()) is None:
            errors.append(f"reader-facing page lacks Page status metadata: {chapter}")

    architecture = load_json(PORT_FACTOR_ARCHITECTURE)
    if architecture.get("claim_id") not in claim_ids:
        errors.append("port-factor architecture uses an unregistered claim ID")
    if architecture.get("source_fixture") != "data/running-network/v0.1.0.json":
        errors.append("port-factor architecture names an unexpected source fixture")
    model = architecture.get("model", {})
    if model.get("object_type") != "hierarchical_port_factor_model":
        errors.append("port-factor architecture has an unexpected object type")
    if model.get("notation") != "𝔓=(Q,J,Φ,j,f,H,X,R)":
        errors.append("port-factor architecture notation contract changed")

    five_bus_port_factor = load_json(FIVE_BUS_PORT_FACTOR)
    if five_bus_port_factor.get("claim_id") not in claim_ids:
        errors.append("five-bus port-factor witness uses an unregistered claim ID")
    if five_bus_port_factor.get("source_fixture") != "experiments/generated/five-bus-cycle-space-analysis.json":
        errors.append("five-bus port-factor witness names an unexpected source fixture")
    five_model = five_bus_port_factor.get("model", {})
    five_validation = five_bus_port_factor.get("validation", {})
    if five_validation.get("valid") is not True:
        errors.append("five-bus port-factor witness failed structural validation")
    if (
        len(five_model.get("ports", [])) != 14
        or len(five_model.get("junctions", [])) != 5
        or len(five_model.get("factors", [])) != 7
    ):
        errors.append("five-bus port-factor witness changed its incidence cardinalities")

    five_bus_terminal_lift = load_json(FIVE_BUS_CONDUCTOR_TERMINAL_LIFT)
    if five_bus_terminal_lift.get("witness_id") != "ARCH-CONDUCTOR-002":
        errors.append("five-bus conductor-terminal lift has an invalid witness ID")
    if five_bus_terminal_lift.get("source_fixture") != "experiments/generated/five-bus-cycle-space-analysis.json":
        errors.append("five-bus conductor-terminal lift names an unexpected source fixture")
    lift_checks = five_bus_terminal_lift.get("checks", {})
    for name in (
        "all_factor_ports_resolve",
        "scalar_line_factors_are_two_port",
        "terminal_junctions_preserved",
        "line_identity_preserved",
        "parallel_fibre_retained",
    ):
        if lift_checks.get(name) is not True:
            errors.append(f"five-bus conductor-terminal lift check failed: {name}")
    if len(five_bus_terminal_lift.get("ports", [])) != 14 or len(five_bus_terminal_lift.get("factors", [])) != 7:
        errors.append("five-bus conductor-terminal lift changed its incidence cardinalities")

    multiwinding_terminal_lift = load_json(MULTIWINDING_TERMINAL_LIFT)
    if multiwinding_terminal_lift.get("witness_id") != "ARCH-CONDUCTOR-MULTI-001":
        errors.append("multiwinding conductor-terminal lift has an invalid witness ID")
    if multiwinding_terminal_lift.get("source_fixture") != "data/transformer-contracts/x1-fixed-linear-v0.1.0.json":
        errors.append("multiwinding conductor-terminal lift names an unexpected source fixture")
    for name in (
        "all_transfer_ports_resolve",
        "multiwinding_factor_has_three_ports",
        "winding_identity_preserved",
        "wye_neutral_terminal_retained",
        "delta_winding_has_no_neutral_terminal",
        "internal_grounding_is_separate_observation",
        "excitation_shunt_is_separate_observation",
        "factor_incidence_is_acyclic",
        "clique_compilation_adds_cycle",
    ):
        if multiwinding_terminal_lift.get("checks", {}).get(name) is not True:
            errors.append(f"multiwinding conductor-terminal lift check failed: {name}")
    if len(multiwinding_terminal_lift.get("ports", [])) != 3 or len(multiwinding_terminal_lift.get("factors", [])) != 1:
        errors.append("multiwinding conductor-terminal lift changed its incidence cardinalities")

    five_bus_transformer = load_json(FIVE_BUS_TRANSFORMER_LOWERING)
    if five_bus_transformer.get("witness_id") != "ARCH-FIVEBUS-XFMR-001":
        errors.append("five-bus transformer lowering witness has an invalid witness ID")
    if five_bus_transformer.get("all_checks_pass") is not True:
        errors.append("five-bus transformer lowering witness failed its checks")
    lowering_checks = five_bus_transformer.get("checks", {})
    for name in (
        "base_member_cycle_rank_is_three",
        "base_simple_cycle_rank_is_two",
        "source_transformer_is_one_three_port_factor",
        "local_factor_incidence_is_acyclic",
        "local_star_is_acyclic",
        "local_clique_has_one_cycle",
        "embedded_incidence_cycle_rank_is_five",
        "embedded_star_member_cycle_rank_is_five",
        "embedded_clique_member_cycle_rank_is_six",
        "embedded_clique_simple_cycle_rank_is_three",
        "three_winding_star_is_declared_special_case",
        "winding_current_and_internal_observations_remain_declared",
    ):
        if lowering_checks.get(name) is not True:
            errors.append(f"five-bus transformer lowering check failed: {name}")
    source_dependencies = five_bus_transformer.get("source_dependencies", {})
    for source_path, recorded_hash in source_dependencies.items():
        path = ROOT / source_path
        if not path.is_file() or sha256(path) != recorded_hash:
            errors.append(f"five-bus transformer lowering dependency is stale: {source_path}")

    multiwinding_typed_kron = load_json(MULTIWINDING_TYPED_KRON)
    if multiwinding_typed_kron.get("witness_id") != "TR-KRON-MULTI-001":
        errors.append("multiwinding typed Kron witness has an invalid witness ID")
    if multiwinding_typed_kron.get("source_fixture") != "data/transformer-contracts/x1-fixed-linear-v0.1.0.json":
        errors.append("multiwinding typed Kron witness names an unexpected source fixture")
    for name in (
        "internal_block_is_singular",
        "retained_wye_ports_have_eight_terminals",
        "eliminated_delta_port_has_three_terminals",
        "reduction_refused_without_pseudoinverse",
        "internal_current_recovery_is_explicit",
        "eliminated_winding_constraint_observation_retained",
        "eliminated_delta_limits_are_positive",
    ):
        if multiwinding_typed_kron.get("checks", {}).get(name) is not True:
            errors.append(f"multiwinding typed Kron check failed: {name}")
    if multiwinding_typed_kron.get("residuals", {}).get("internal_block_rank", 99) >= multiwinding_typed_kron.get("residuals", {}).get("internal_block_dimension", 0):
        errors.append("multiwinding typed Kron witness lost its singular-block boundary")

    five_bus_active = load_json(FIVE_BUS_ACTIVE_RADIALITY)
    if five_bus_active.get("witness_id") != "TR-GRAPH-ACTIVE-001":
        errors.append("five-bus active radiality witness has an invalid witness ID")
    if five_bus_active.get("source_fixture") != "experiments/generated/five-bus-cycle-space-analysis.json":
        errors.append("five-bus active radiality witness names an unexpected source fixture")
    if five_bus_active.get("all_checks_pass") is not True:
        errors.append("five-bus active radiality witness failed its checks")
    active_checks = five_bus_active.get("checks", {})
    for name in (
        "inventory_member_cycle_rank_is_three",
        "inventory_adjacency_cycle_rank_is_two",
        "inventory_is_not_radial",
        "declared_tree_is_member_radial",
        "declared_tree_is_adjacency_radial",
        "declared_tree_has_five_bus_tree_size",
    ):
        if active_checks.get(name) is not True:
            errors.append(f"five-bus active radiality check failed: {name}")

    topology_projection = load_json(TOPOLOGY_PROJECTION_WITNESS)
    if topology_projection.get("witness_id") != "ARCH-TOPOLOGY-001":
        errors.append("topology projection witness has an invalid witness ID")
    if set(topology_projection.get("claim_ids", [])) != {
        "ARCH-NODAL-001", "ARCH-SUPPORT-001", "ARCH-CHORDAL-001"
    }:
        errors.append("topology projection witness has an unexpected claim set")
    if topology_projection.get("all_checks_pass") is not True:
        errors.append("topology projection witness failed its checks")
    parallel_projection = topology_projection.get("parallel_split", {})
    for name in (
        "splits_are_distinct",
        "assembled_operators_are_bit_identical",
        "base_round_trip_passes",
        "alternate_round_trip_passes",
        "base_split_is_passive",
        "alternate_split_is_passive",
        "all_primitives_are_reciprocal",
        "consistency_test_is_attribution_blind",
    ):
        if parallel_projection.get("checks", {}).get(name) is not True:
            errors.append(f"topology parallel-split check failed: {name}")
    chordal_projection = topology_projection.get("radial_clique_support", {})
    for name in (
        "macro_graph_is_tree",
        "scalar_support_contains_cycles",
        "line_cliques_share_declared_separator",
        "leaf_block_order_is_perfect",
        "leaf_block_order_has_zero_fill",
        "bad_order_has_positive_fill",
    ):
        if chordal_projection.get("checks", {}).get(name) is not True:
            errors.append(f"topology radial-clique check failed: {name}")

    source_recovery = load_json(NODAL_SOURCE_RECOVERY_WITNESS)
    if source_recovery.get("witness_id") != "ARCH-RECOVERY-001":
        errors.append("nodal source recovery witness has an invalid witness ID")
    if source_recovery.get("claim_ids") != ["ARCH-RECOVERY-001"]:
        errors.append("nodal source recovery witness has an unexpected claim set")
    if source_recovery.get("all_checks_pass") is not True:
        errors.append("nodal source recovery witness failed its checks")
    expected_statuses = {
        "support_separated": "identifiable",
        "parallel_multiplicity": "non-identifiable",
        "eliminated_coordinate": "non-identifiable",
        "over_parameterized": "set-identifiable",
    }
    for class_name, status in expected_statuses.items():
        class_record = source_recovery.get("classes", {}).get(class_name, {})
        if class_record.get("status") != status:
            errors.append(f"nodal source recovery class {class_name} has an unexpected status")
        for check_name, check_value in class_record.get("checks", {}).items():
            if check_value is not True:
                errors.append(f"nodal source recovery class {class_name} failed check: {check_name}")

    recovery_guards = load_json(NODAL_RECOVERY_GUARDS_WITNESS)
    if recovery_guards.get("witness_id") != "ARCH-RECOVERY-GUARDS-001":
        errors.append("nodal recovery guards witness has an invalid witness ID")
    if recovery_guards.get("claim_ids") != ["ARCH-RECOVERY-002"]:
        errors.append("nodal recovery guards witness has an unexpected claim set")
    if recovery_guards.get("all_checks_pass") is not True:
        errors.append("nodal recovery guards witness failed its checks")
    expected_guard_statuses = {
        "catalog_bounds": "bounded-non-identifiable",
        "member_current_measurement": "identifiable",
        "grounding_declaration": "identifiable-with-declaration",
        "transformer_state_declaration": "identifiable-with-state",
    }
    for case_name, status in expected_guard_statuses.items():
        case_record = recovery_guards.get("cases", {}).get(case_name, {})
        if case_record.get("status") != status:
            errors.append(f"nodal recovery guard {case_name} has an unexpected status")
        for check_name, check_value in case_record.get("checks", {}).items():
            if check_value is not True:
                errors.append(f"nodal recovery guard {case_name} failed check: {check_name}")

    multiconductor_recovery = load_json(MULTICONDUCTOR_RECOVERY_WITNESS)
    if multiconductor_recovery.get("witness_id") != "ARCH-RECOVERY-MULTI-001":
        errors.append("multiconductor recovery witness has an invalid witness ID")
    if multiconductor_recovery.get("claim_ids") != ["ARCH-RECOVERY-003"]:
        errors.append("multiconductor recovery witness has an unexpected claim set")
    if multiconductor_recovery.get("all_checks_pass") is not True:
        errors.append("multiconductor recovery witness failed its checks")
    expected_multiconductor_statuses = {
        "full_rank_voltage_sweep": "identifiable",
        "single_snapshot": "non-identifiable",
        "phase_selective": "non-identifiable",
    }
    for case_name, status in expected_multiconductor_statuses.items():
        case_record = multiconductor_recovery.get("cases", {}).get(case_name, {})
        if case_record.get("status") != status:
            errors.append(f"multiconductor recovery case {case_name} has an unexpected status")
        for check_name, check_value in case_record.get("checks", {}).items():
            if check_value is not True:
                errors.append(f"multiconductor recovery case {case_name} failed check: {check_name}")

    noisy_multiconductor = load_json(NOISY_MULTICONDUCTOR_RECOVERY_WITNESS)
    if noisy_multiconductor.get("witness_id") != "ARCH-RECOVERY-NOISE-001":
        errors.append("noisy multiconductor recovery witness has an invalid witness ID")
    if noisy_multiconductor.get("claim_ids") != ["ARCH-RECOVERY-004"]:
        errors.append("noisy multiconductor recovery witness has an unexpected claim set")
    if noisy_multiconductor.get("all_checks_pass") is not True:
        errors.append("noisy multiconductor recovery witness failed its checks")
    for case_name in ("well_conditioned", "ill_conditioned"):
        case_record = noisy_multiconductor.get(case_name, {})
        if case_record.get("status") != "bounded-uncertain":
            errors.append(f"noisy multiconductor case {case_name} has an unexpected status")
        for check_name, check_value in case_record.get("checks", {}).items():
            if check_value is not True:
                errors.append(f"noisy multiconductor case {case_name} failed check: {check_name}")
    if not noisy_multiconductor.get("checks", {}).get("ill_conditioning_amplifies_uncertainty"):
        errors.append("noisy multiconductor witness lost its conditioning comparison")

    nonlinear_grounding = load_json(NONLINEAR_GROUNDING_LOCAL_BOUND)
    if nonlinear_grounding.get("witness_id") != "TR-KRON-NEUTRAL-008":
        errors.append("local nonlinear grounding bound has an invalid witness ID")
    if nonlinear_grounding.get("claim_ids") != ["TR-KRON-NEUTRAL-008"]:
        errors.append("local nonlinear grounding bound has an unexpected claim set")
    if nonlinear_grounding.get("all_checks_pass") is not True:
        errors.append("local nonlinear grounding bound failed its checks")
    for check_name, check_value in nonlinear_grounding.get("checks", {}).items():
        if check_value is not True:
            errors.append(f"local nonlinear grounding bound failed check: {check_name}")

    five_bus_kron = load_json(FIVE_BUS_TYPED_KRON)
    if five_bus_kron.get("witness_id") != "TR-KRON-FIVE-001":
        errors.append("five-bus typed Kron witness has an invalid witness ID")
    if five_bus_kron.get("source_fixture") != "experiments/generated/five-bus-cycle-space-analysis.json":
        errors.append("five-bus typed Kron witness names an unexpected source fixture")
    if five_bus_kron.get("all_checks_pass") is not True:
        errors.append("five-bus typed Kron witness failed its checks")
    kron_checks = five_bus_kron.get("checks", {})
    for name in (
        "internal_block_is_invertible",
        "reduced_matches_direct_leaf_deletion",
        "boundary_current_recovery",
        "full_nodal_residual_is_zero",
        "eliminated_bus_is_pendant",
        "provenance_retained",
    ):
        if kron_checks.get(name) is not True:
            errors.append(f"five-bus typed Kron check failed: {name}")
    for name in (
        "non_pendant_internal_block_is_invertible",
        "non_pendant_boundary_current_recovery",
        "non_pendant_fill_jm_is_present",
        "non_pendant_fill_km_is_present",
        "recovered_line_u_current_is_exact",
        "tight_line_u_limit_is_not_satisfied",
    ):
        if kron_checks.get(name) is not True:
            errors.append(f"five-bus non-pendant Kron check failed: {name}")
    if five_bus_kron.get("non_pendant_fill_edges") != ["j-m", "k-m"]:
        errors.append("five-bus non-pendant Kron fill provenance changed")
    validation = architecture.get("validation", {})
    if validation.get("valid") is not True or validation.get("n_ports") != 8:
        errors.append("port-factor architecture validation failed")
    if validation.get("n_factors") != 4 or validation.get("n_lambda_relations") != 7:
        errors.append("port-factor architecture cardinalities changed")

    sequence_witness = load_json(POSITIVE_SEQUENCE_WITNESS)
    if sequence_witness.get("claim_id") not in claim_ids:
        errors.append("positive-sequence witness uses an unregistered claim ID")
    circulant = sequence_witness.get("circulant", {})
    rejected_sequence = sequence_witness.get("non_circulant_rejection", {})
    if circulant.get("sequence_diagonal_residual", float("inf")) > 1.0e-12:
        errors.append("positive-sequence circulant witness is not diagonal in sequence coordinates")
    if circulant.get("positive_subspace_residual", float("inf")) > 1.0e-12:
        errors.append("positive-sequence circulant witness does not preserve the positive subspace")
    if rejected_sequence.get("sequence_diagonal_residual", 0.0) <= 1.0e-3:
        errors.append("positive-sequence negative witness no longer mixes sequences")

    impedance_ladder = load_json(FOUR_WIRE_IMPEDANCE_LADDER)
    if impedance_ladder.get("witness_id") != "IMPEDANCE-LADDER-001":
        errors.append("four-wire impedance ladder has an invalid witness ID")
    if impedance_ladder.get("claim_id") not in claim_ids:
        errors.append("four-wire impedance ladder uses an unregistered claim ID")
    if impedance_ladder.get("all_checks_pass") is not True:
        errors.append("four-wire impedance ladder witness failed its checks")
    impedance_checks = impedance_ladder.get("checks", {})
    for name in (
        "source_matrix_is_complex_symmetric",
        "source_matrix_is_not_hermitian",
        "neutral_block_is_invertible",
        "kron_phase_relation_is_defined",
        "phase_neutral_current_is_recoverable",
        "phase_neutral_drop_is_recovered",
        "fortescue_transform_is_invertible",
        "sequence_mixing_is_visible",
        "positive_sequence_guard_is_required",
        "shunt_deletion_changes_declared_factor",
        "every_path_rule_has_risk_tags",
    ):
        if impedance_checks.get(name) is not True:
            errors.append(f"four-wire impedance ladder check failed: {name}")
    path = impedance_ladder.get("transformation_path", [])
    if len(path) != 7 or any(not row.get("risk_tags") for row in path):
        errors.append("four-wire impedance ladder transformation path lost risk metadata")

    balanced_transmission = load_json(BALANCED_TRANSMISSION_WITNESS)
    if balanced_transmission.get("witness_id") != "COLLAPSE-NETWORK-001":
        errors.append("balanced transmission witness has an invalid witness ID")
    if balanced_transmission.get("claim_id") not in claim_ids:
        errors.append("balanced transmission witness uses an unregistered claim ID")
    if balanced_transmission.get("all_checks_pass") is not True:
        errors.append("balanced transmission witness failed its checks")
    for name in (
        "circulant_series_and_shunt",
        "nominal_pi_shunts_included",
        "phase_solution_matches_embedded_scalar",
        "phase_nodal_residual_is_small",
        "phase_solution_stays_positive_sequence",
        "branch_currents_match_embedded_scalar",
        "balanced_transmission_fixture_has_two_arcs",
    ):
        if balanced_transmission.get("checks", {}).get(name) is not True:
            errors.append(f"balanced transmission witness check failed: {name}")

    balanced_reproduction = load_json(BALANCED_TRANSMISSION_REPRODUCTION)
    if balanced_reproduction.get("claim_id") != "COLLAPSE-001":
        errors.append("balanced transmission independent reproduction has an invalid claim ID")
    if balanced_reproduction.get("all_checks_pass") is not True:
        errors.append("balanced transmission independent reproduction failed")
    for name in (
        "all_values_match_julia",
        "independent_solver_used",
        "nominal_pi_shunts_reconstructed",
        "no_numpy_or_julia_import",
    ):
        if balanced_reproduction.get("checks", {}).get(name) is not True:
            errors.append(f"balanced transmission independent reproduction check failed: {name}")

    kron_ward = load_json(KRON_WARD_SCENARIO)
    if kron_ward.get("claim_id") not in claim_ids or kron_ward.get("witness_id") != "TR-KRON-002":
        errors.append("Kron/Ward/scenario comparison uses an invalid claim or witness ID")
    if kron_ward.get("selected_candidate") == "full_kron" or kron_ward.get("selected_is_exact") is not False:
        errors.append("scenario comparison no longer demonstrates a non-exact structural selection")
    checks = kron_ward.get("checks", {})
    for name in (
        "exact_kron_base_relation",
        "ward_is_operating_point_only",
        "extended_support_is_exact_for_fixture",
        "extended_support_is_nontrivial_off_base",
        "scenario_selection_is_structural",
        "all_candidate_observations_reported",
    ):
        if checks.get(name) is not True:
            errors.append(f"Kron/Ward/scenario comparison check failed: {name}")
    if not any(row.get("base_exact") and row.get("current_error_norm", 1.0) <= 1e-12 for row in kron_ward.get("ward_rows", [])):
        errors.append("Ward comparison lost its exact base operating-point row")
    if not any((not row.get("base_exact")) and row.get("current_error_norm", 0.0) > 1e-4 for row in kron_ward.get("ward_rows", [])):
        errors.append("Ward comparison no longer exposes off-base error")
    if not all(row.get("current_error_norm", 1.0) <= 1e-12 for row in kron_ward.get("extended_ward_rows", [])):
        errors.append("extended Ward support rows are no longer exact for the declared fixture")

    approximation = load_json(CERTIFIED_APPROXIMATION)
    if approximation.get("claim_id") not in claim_ids or approximation.get("witness_id") != "TR-KRON-003":
        errors.append("certified approximation witness uses an invalid claim or witness ID")
    approximation_checks = approximation.get("checks", {})
    for name in (
        "bound_dominates_direct_constraint_error",
        "base_is_exactly_calibrated",
        "has_certified_feasible_case",
        "has_ambiguous_case",
        "has_certified_violated_case",
    ):
        if approximation_checks.get(name) is not True:
            errors.append(f"certified approximation check failed: {name}")

    nonlinear_ward = load_json(NONLINEAR_WARD_WITNESS)
    if nonlinear_ward.get("witness_id") != "nonlinear_ward_probe_v0.1.0":
        errors.append("nonlinear Ward witness has an invalid witness ID")
    if nonlinear_ward.get("evidence_type") != "scoped_exploratory_nonlinear_witness":
        errors.append("nonlinear Ward witness has an invalid evidence type")
    nonlinear_checks = nonlinear_ward.get("checks", {})
    for name in (
        "base_residual_is_small",
        "small_shift_is_locally_bounded",
        "large_shift_exposes_nonlinear_residual",
        "all_newton_solves_converged",
        "has_local_feasible_case",
        "has_local_ambiguous_case",
    ):
        if nonlinear_checks.get(name) is not True:
            errors.append(f"nonlinear Ward witness check failed: {name}")

    crosswalk = load_json(SOLVER_DIAGNOSTICS_CROSSWALK)
    if crosswalk.get("witness_id") != "NUM-SOLVER-CROSSWALK-001":
        errors.append("solver diagnostics crosswalk has an invalid witness ID")
    if crosswalk.get("solver_boundary", {}).get("solver_internal_kkt_export") is not False:
        errors.append("solver diagnostics crosswalk must state that solver-internal KKT export is unavailable")
    if crosswalk.get("solver_boundary", {}).get("checked_kkt_callback_api") != (
        "BMOPFTools.opf_checked_kkt_factorization"
    ):
        errors.append("solver diagnostics crosswalk lost the checked-KKT callback boundary")
    callback_probe = crosswalk.get("solver_callback_probe", {})
    if callback_probe.get("diagnostic_status") != "accepted":
        errors.append("solver diagnostics callback probe did not accept the regular matrix")
    if callback_probe.get("diagnostic_dimension") != 6:
        errors.append("solver diagnostics callback probe dimension changed")
    if callback_probe.get("rejected_near_singular_probe") is not True:
        errors.append("solver diagnostics callback probe lost its near-singular rejection")
    diffopt_probe = crosswalk.get("diffopt_sensitivity_probe", {})
    if diffopt_probe.get("solver_status") not in ("LOCALLY_SOLVED", "OPTIMAL"):
        errors.append("DiffOpt sensitivity probe did not solve the staged OPF")
    if diffopt_probe.get("diagnostic_status") != "accepted":
        errors.append("DiffOpt sensitivity probe did not record an accepted KKT diagnostic")
    if abs(diffopt_probe.get("forward_sensitivity", 0.0) - 0.5) > 1e-7:
        errors.append("DiffOpt sensitivity probe changed its analytic forward sensitivity")
    if diffopt_probe.get("sensitivity_residual", 1.0) > 1e-7:
        errors.append("DiffOpt sensitivity probe no longer agrees with central difference")
    if diffopt_probe.get("callback_invocations", 0) < 1:
        errors.append("DiffOpt sensitivity probe did not capture a callback invocation")
    if diffopt_probe.get("captured_kkt_rows") != diffopt_probe.get("diagnostic_dimension"):
        errors.append("captured DiffOpt KKT dimension disagrees with its diagnostic")
    if diffopt_probe.get("captured_kkt_columns") != diffopt_probe.get("captured_kkt_rows"):
        errors.append("captured DiffOpt KKT matrix is not square")
    if diffopt_probe.get("captured_kkt_nonzeros", 0) <= 0:
        errors.append("captured DiffOpt KKT matrix has no nonzeros")
    if diffopt_probe.get("kkt_unaccounted_rows") != 4:
        errors.append("captured DiffOpt KKT internal-row count changed")
    if diffopt_probe.get("native_nlp_jacobian_rows") != diffopt_probe.get("model_constraint_count"):
        errors.append("native JuMP/MOI Jacobian row count disagrees with declared constraints")
    if diffopt_probe.get("native_nlp_jacobian_nonzeros", 0) <= 0:
        errors.append("native JuMP/MOI Jacobian export has no nonzeros")
    if diffopt_probe.get("native_nlp_export_is_solver_internal") is not False:
        errors.append("native JuMP/MOI Jacobian export boundary was not marked non-internal")
    if diffopt_probe.get("differentiability_termination_status") not in ("LOCALLY_SOLVED", "OPTIMAL"):
        errors.append("DiffOpt differentiability report has an invalid termination status")
    if not isinstance(diffopt_probe.get("active_constraints"), list):
        errors.append("DiffOpt differentiability report lost active constraints")
    if not isinstance(diffopt_probe.get("near_active_constraints"), list):
        errors.append("DiffOpt differentiability report lost near-active constraints")
    if not isinstance(diffopt_probe.get("violated_constraints"), list):
        errors.append("DiffOpt differentiability report lost violated constraints")
    parallel_comparison = crosswalk.get("diffopt_parallel_comparison", {})
    parallel_checks = parallel_comparison.get("checks", {})
    for name in (
        "source_and_reduced_solve", "sensitivity_is_preserved",
        "finite_difference_is_preserved", "kkt_structure_changes",
        "native_jacobian_support_changes",
    ):
        if parallel_checks.get(name) is not True:
            errors.append(f"DiffOpt parallel comparison check failed: {name}")
    parallel_source = parallel_comparison.get("source", {})
    parallel_reduced = parallel_comparison.get("reduced", {})
    if abs(parallel_source.get("forward_sensitivity", 0.0) - 0.25) > 1e-7 or abs(
        parallel_reduced.get("forward_sensitivity", 0.0) - 0.25
    ) > 1e-7:
        errors.append("DiffOpt parallel comparison lost its exact scalar sensitivity")
    if parallel_source.get("captured_kkt_rows", 0) <= parallel_reduced.get("captured_kkt_rows", 0):
        errors.append("DiffOpt parallel comparison no longer exposes source KKT growth")
    density = diffopt_probe.get("captured_kkt_density", 0.0)
    if not (0.0 < density <= 1.0):
        errors.append("captured DiffOpt KKT density is invalid")
    crosswalk_checks = crosswalk.get("checks", {})
    for name in (
        "ybus_uses_bmopftools_builders",
        "realified_jacobian_has_declared_dimension",
        "kkt_source_and_aggregate_are_both_present",
        "ordering_diagnostics_are_recorded",
        "ordering_changes_symbolic_fill",
        "crosswalk_retains_node_order",
    ):
        if crosswalk_checks.get(name) is not True:
            errors.append(f"solver diagnostics crosswalk check failed: {name}")

    data_crosswalk = load_json(DATA_MODEL_CROSSWALK)
    if data_crosswalk.get("witness_id") != "DATA-XWALK-001" or data_crosswalk.get("claim_id") not in claim_ids:
        errors.append("data-model crosswalk has an invalid witness or claim ID")
    if data_crosswalk.get("source_fixture") != "data/running-network/v0.1.0.json":
        errors.append("data-model crosswalk names an unexpected source fixture")
    data_checks = data_crosswalk.get("checks", {})
    for name in (
        "all_profiles_version_pinned",
        "canonical_bus_ids_are_unique",
        "canonical_asset_ids_are_unique",
        "terminal_records_have_provenance",
        "rating_records_have_owner_and_unit",
        "profile_asset_round_trip",
        "matpower_projection_is_marked",
        "state_provenance_is_retained",
    ):
        if data_checks.get(name) is not True:
            errors.append(f"data-model crosswalk check failed: {name}")
    if len(data_crosswalk.get("profiles", [])) != 4:
        errors.append("data-model crosswalk must contain four pinned ecosystem profiles")

    running_kron = load_json(RUNNING_NETWORK_TYPED_KRON)
    if running_kron.get("witness_id") != "TR-KRON-RUNNING-001" or running_kron.get("claim_id") not in claim_ids:
        errors.append("running-network typed Kron witness has an invalid witness or claim ID")
    if running_kron.get("source_fixture") != "data/running-network/v0.1.0.json" or running_kron.get("asset_id") != "line/l1":
        errors.append("running-network typed Kron witness names an unexpected fixture or asset")
    running_kron_checks = running_kron.get("checks", {})
    for name in (
        "internal_block_is_invertible",
        "reduced_matches_direct_line_primitive",
        "midpoint_recovery_is_exact_for_equal_halves",
        "boundary_relation_is_satisfied",
        "terminal_order_is_preserved",
        "source_identity_is_retained",
        "neutral_current_recovery_is_exact",
        "neutral_limit_is_not_silently_dropped",
        "shunt_internal_block_is_invertible",
        "neutral_shunt_recovery_kcl_is_exact",
        "neutral_shunt_changes_recovered_current",
        "neutral_shunt_limit_is_evaluated",
    ):
        if running_kron_checks.get(name) is not True:
            errors.append(f"running-network typed Kron check failed: {name}")
    if running_kron.get("residuals", {}).get("primitive", 1.0) > 1.0e-11:
        errors.append("running-network typed Kron primitive residual is too large")

    guarded = load_json(GUARDED_PARALLEL_REDUCTION)
    if guarded.get("witness_id") != "TR-PAR-GUARDED-001":
        errors.append("guarded parallel reduction witness has an invalid witness ID")
    if guarded.get("evidence_type") != "scoped_guarded_reduction_witness":
        errors.append("guarded parallel reduction witness has an invalid evidence type")
    guarded_checks = guarded.get("checks", {})
    for name in (
        "singular_full_map_is_rank_deficient",
        "singular_guard_rejects_full_map",
        "reduced_voltage_drop_map_certified",
        "joint_retained_support_certified",
        "fixed_map_fails_off_state",
        "recomputed_state_map_is_consistent",
    ):
        if guarded_checks.get(name) is not True:
            errors.append(f"guarded parallel reduction witness check failed: {name}")

    three_member = load_json(THREE_MEMBER_FOUR_WIRE_PARALLEL_AC)
    if three_member.get("retained_members") != ["l1", "l2"] or three_member.get("candidate_member") != "l3":
        errors.append("three-member AC witness has an unexpected retained/candidate partition")
    if three_member.get("certified") is not True:
        errors.append("three-member AC witness is not certified")
    supports = three_member.get("exact_worst_case_component_magnitudes", [])
    limits = three_member.get("candidate_limits", [])
    if not supports or len(supports) != len(limits) or any(support > limit + 1.0e-12 for support, limit in zip(supports, limits)):
        errors.append("three-member AC support bound does not fit candidate limits")
    if abs(three_member.get("objective_gap", 1.0)) > 1.0e-7:
        errors.append("three-member AC source/pruned objective gap is too large")
    independent = three_member.get("independent_source_boundary", {})
    if independent.get("bracket_width", 1.0) > 1.0e-8 or independent.get("power_flow_residual", 1.0) > 1.0e-9:
        errors.append("three-member AC independent boundary reproduction is too loose")
    if abs(three_member.get("independent_source_objective_gap", 1.0)) > 3.0e-8:
        errors.append("three-member AC independent boundary differs too far from the source solve")
    three_member_envelope = three_member.get("finite_state_envelope", {})
    if three_member_envelope.get("witness_id") != "TR-PAR-STATE-001" or three_member_envelope.get("claim_id") not in claim_ids:
        errors.append("three-member state envelope has an invalid witness or claim ID")
    if three_member_envelope.get("all_checks_pass") is not True:
        errors.append("three-member state envelope failed")
    for name in (
        "all_states_certify_joint_pruning",
        "all_source_and_pruned_solves_terminate",
        "pruned_matches_source_in_each_state",
        "independent_boundary_matches_source_in_each_state",
        "state_changes_decision_value",
        "state_rows_are_explicit",
    ):
        if three_member_envelope.get("checks", {}).get(name) is not True:
            errors.append(f"three-member state envelope check failed: {name}")
    if len(three_member_envelope.get("states", [])) != 4:
        errors.append("three-member state envelope must contain four states")
    state_reproduction = load_json(THREE_MEMBER_STATE_REPRODUCTION)
    if state_reproduction.get("claim_id") != "TR-PAR-STATE-001":
        errors.append("three-member state envelope reproduction has an invalid claim ID")
    if state_reproduction.get("all_checks_pass") is not True:
        errors.append("three-member state envelope reproduction failed")
    for name in (
        "all_state_boundaries_match_julia",
        "all_boundaries_converged",
        "independent_solver_used",
        "no_numpy_or_julia_import",
    ):
        if state_reproduction.get("checks", {}).get(name) is not True:
            errors.append(f"three-member state envelope reproduction check failed: {name}")
    if len(state_reproduction.get("rows", [])) != 4:
        errors.append("three-member state envelope reproduction must contain four rows")

    pi_certificate = load_json(GENERATED / "pi-four-wire-parallel-ac-certificate.json")
    envelope = pi_certificate.get("evidence", {}).get("finite_state_decision_envelope", {})
    if envelope.get("declared_state_count") != 3 or envelope.get("all_maps_certified") is not True:
        errors.append("finite nominal-pi state envelope is incomplete or uncertified")
    if envelope.get("maximum_absolute_pruned_objective_gap", 1.0) > 1.0e-7:
        errors.append("finite nominal-pi state envelope has a large pruning gap")
    states = envelope.get("states", [])
    if len(states) != 3 or any(
        state.get("source_status") not in ("LOCALLY_SOLVED", "OPTIMAL")
        or state.get("pruned_status") not in ("LOCALLY_SOLVED", "OPTIMAL")
        for state in states
    ):
        errors.append("finite nominal-pi state envelope lost a solver-backed state record")
    reduced_guard = pi_certificate.get("evidence", {}).get("series_reduced_coordinate_guard", {})
    if reduced_guard.get("full_terminal_map_rank", 0) >= reduced_guard.get("full_terminal_map_dimension", 0):
        errors.append("series-only singular guard lost its rank-deficient full-map record")
    if reduced_guard.get("reduced_coordinate_recovery_residual", 1.0) > 1.0e-12:
        errors.append("series-only singular reduced-coordinate recovery residual is too large")
    if reduced_guard.get("neutral_current_retained_as_zero") is not True:
        errors.append("series-only singular guard lost its explicit zero-neutral invariant")

    controls = load_json(TRANSFORMER_CONTROL_FAMILY)
    if controls.get("witness_id") != "TR-XFMR-CONTROL-001":
        errors.append("transformer control family witness has an invalid witness ID")
    if controls.get("evidence_type") != "scoped_transformer_control_witness":
        errors.append("transformer control family witness has an invalid evidence type")
    control_checks = controls.get("checks", {})
    for name in (
        "scalar_magnitude_is_pointwise_exact",
        "phase_angle_is_pointwise_exact",
        "independent_phase_is_pointwise_exact",
        "mechanical_coupling_is_explicit",
        "automatic_deadband_output_is_explicit",
        "solver_backed_control_probes_solve",
        "network_control_probes_solve",
        "tap_dependent_loss_rejects_frozen_base",
    ):
        if control_checks.get(name) is not True:
            errors.append(f"transformer control family witness check failed: {name}")
    if not isinstance(controls.get("automatic_probe", {}).get("solver_status"), str):
        errors.append("transformer control family witness lost automatic solver probe provenance")
    network_probes = controls.get("network_probes", {})
    for name in ("phase_angle", "tap_dependent_loss", "independent_phase", "mechanically_coupled"):
        if network_probes.get(name, {}).get("status") not in ("LOCALLY_SOLVED", "OPTIMAL"):
            errors.append(f"transformer network control probe did not solve: {name}")

    transformer_tap = load_json(TRANSFORMER_TAP_AC)
    switching = transformer_tap.get("evidence", {}).get("switching_decision", {})
    if switching.get("branch_completeness") is not True:
        errors.append("transformer tap switching ledger is not branch-complete")
    if switching.get("cost_sweep_branch_complete") is not True:
        errors.append("transformer tap switching-cost sweep is not branch-complete")
    if len(switching.get("cost_sweep", [])) != 5:
        errors.append("transformer tap switching-cost sweep changed size")
    if switching.get("positive_breakpoint_count", 0) <= 0:
        errors.append("transformer tap switching ledger lost positive breakpoints")
    if len(switching.get("positive_breakpoints", [])) != switching.get("positive_breakpoint_count"):
        errors.append("transformer tap switching breakpoint count disagrees with ledger")
    unbalanced_switching = transformer_tap.get("evidence", {}).get("unbalanced_switching_decision", {})
    if unbalanced_switching.get("branch_completeness") is not True:
        errors.append("unbalanced transformer tap switching ledger is not branch-complete")
    if unbalanced_switching.get("cost_sweep_branch_complete") is not True:
        errors.append("unbalanced transformer tap switching-cost sweep is not branch-complete")
    if unbalanced_switching.get("branch_count") != 9:
        errors.append("unbalanced transformer tap switching ledger must enumerate nine tap pairs")
    if len(unbalanced_switching.get("scenario_phase_scale", [])) != 3:
        errors.append("unbalanced transformer tap witness lost its three phase-selective scales")
    if unbalanced_switching.get("scenario_1_phase_directions") == unbalanced_switching.get("scenario_2_phase_directions"):
        errors.append("unbalanced transformer tap witness collapsed the two phase-selective scenarios")
    three_scenario = transformer_tap.get("evidence", {}).get("three_scenario_decision", {})
    if three_scenario.get("branch_completeness") is not True:
        errors.append("three-scenario transformer tap ledger is not branch-complete")
    if three_scenario.get("cost_sweep_branch_complete") is not True:
        errors.append("three-scenario transformer tap cost sweep is not branch-complete")
    if three_scenario.get("branch_count") != 27:
        errors.append("three-scenario transformer tap ledger must enumerate 27 tap triples")
    if len(three_scenario.get("scenario_phase_scales", [])) != 3:
        errors.append("three-scenario transformer tap witness lost its three phase-selective scenarios")
    operation_limited = transformer_tap.get("evidence", {}).get("operation_limited_three_scenario_decision", {})
    if operation_limited.get("max_tap_operations") != 1:
        errors.append("operation-limited tap witness lost its one-operation policy")
    if operation_limited.get("branch_count") != 27 or operation_limited.get("admissible_branch_count") != 15:
        errors.append("operation-limited tap witness has an unexpected admissible branch count")
    if operation_limited.get("branch_completeness") is not True or operation_limited.get("cost_sweep_branch_complete") is not True:
        errors.append("operation-limited tap witness is not branch-complete")
    three_reproduction = load_json(TRANSFORMER_TAP_THREE_SCENARIO_REPRO)
    if three_reproduction.get("certificate_id") != "TR-XFMR-009-REPRO":
        errors.append("three-scenario transformer tap reproduction has an invalid certificate ID")
    if three_reproduction.get("evidence", {}).get("ipopt_branch_count") != 27:
        errors.append("three-scenario transformer tap reproduction lost its 27-branch reference")
    if three_reproduction.get("evidence", {}).get("selected_path_matches") is not True:
        errors.append("three-scenario transformer tap reproduction selected a different path")
    if three_reproduction.get("evidence", {}).get("operation_limited_selected_path_matches") is not True:
        errors.append("operation-limited transformer tap reproduction selected a different path")
    if three_reproduction.get("evidence", {}).get("operation_limited_ipopt_branch_count") != 15:
        errors.append("operation-limited transformer tap reproduction lost its 15 admissible branches")
    if three_reproduction.get("evidence", {}).get("maximum_absolute_net_objective_difference", 1.0) > 1.0e-8:
        errors.append("three-scenario transformer tap reproduction has a large objective gap")
    if three_reproduction.get("evidence", {}).get("operation_limited_maximum_absolute_net_objective_difference", 1.0) > 1.0e-8:
        errors.append("operation-limited transformer tap reproduction has a large objective gap")

    node_breaker = load_json(NODE_BREAKER_STATE)
    if node_breaker.get("witness_id") != "TOPO-NB-001":
        errors.append("node-breaker state witness has an invalid witness ID")
    if node_breaker.get("evidence_type") != "scoped_node_breaker_state_witness":
        errors.append("node-breaker state witness has an invalid evidence type")
    node_checks = node_breaker.get("checks", {})
    for name in (
        "radial_open_is_resolved_radial",
        "parallel_closed_separates_member_and_adjacency_radiality",
        "cycle_closed_is_nonradial",
        "unknown_state_is_not_collapsed",
        "unknown_state_has_both_radialities",
    ):
        if node_checks.get(name) is not True:
            errors.append(f"node-breaker state witness check failed: {name}")

    compiled_views = load_json(COMPILED_VIEWS_SURGERY)
    if compiled_views.get("witness_id") != "ARCH-VIEWS-SURGERY-001":
        errors.append("compiled views/surgery witness has an invalid witness ID")
    if compiled_views.get("claim_ids") != ["ARCH-VIEW-001", "ARCH-LOWER-001", "ARCH-SURGERY-001", "ARCH-SURGERY-002", "ARCH-DEGENERACY-001", "ARCH-DEGENERACY-002"]:
        errors.append("compiled views/surgery witness has an unexpected claim set")
    if compiled_views.get("evidence_type") != "compiled_views_and_state_conditioned_surgery_witness":
        errors.append("compiled views/surgery witness has an invalid evidence type")
    if compiled_views.get("all_checks_pass") is not True:
        errors.append("compiled views/surgery witness failed its aggregate checks")
    if len(compiled_views.get("view_registry", [])) != 6:
        errors.append("compiled views/surgery witness must contain six registered views")
    view_map_ids = [entry.get("map_id") for entry in compiled_views.get("view_maps", [])]
    if view_map_ids != ["M-single-line", "M-port-factor", "M-nodal-support", "M-lowered-edge"]:
        errors.append("compiled views/surgery witness has an unexpected source-to-view map registry")
    if any(entry.get("reverse_status") in (None, "") for entry in compiled_views.get("view_maps", [])):
        errors.append("compiled views/surgery source-to-view maps must declare reverse status")
    for case_name in ("nport_lowering", "parallel_ideal_switches", "phase_only_switching", "zone_surgery", "nterminal_surgery", "model_quality_diagnostics"):
        case = compiled_views.get("cases", {}).get(case_name, {})
        if not case.get("checks") or not all(value is True for value in case["checks"].values()):
            errors.append(f"compiled views/surgery case failed checks: {case_name}")
    if compiled_views.get("cases", {}).get("parallel_ideal_switches", {}).get("diagnostic") != "asset_attribution_ambiguity_for_duplicate_ideal_switches":
        errors.append("duplicate ideal-switch witness must classify asset attribution, not electrical degeneracy")

    load_grounding = load_json(LOAD_GROUNDING_WITNESS)
    if load_grounding.get("all_witnesses_pass") is not True:
        errors.append("load/grounding witness aggregate check failed")
    for family, names in {
        "load_models": (
            "same_bus_branch_graph",
            "all_residuals_small",
            "families_produce_distinct_voltages",
            "decision_margin_changes",
            "zip_coefficients_are_normalized",
            "zip_reactive_coefficients_are_distinct",
        ),
        "grounding_models": (
            "same_bus_branch_graph",
            "floating_ground_current_zero",
            "impedance_grounding_changes_neutral_voltage",
            "ideal_grounding_neutral_voltage_small",
            "grounding_changes_current_allocation",
        ),
        "connection_maps": (
            "same_bus_branch_graph",
            "terminal_order_retained",
            "wye_phase_to_neutral_map_is_explicit",
            "delta_phase_to_phase_map_is_explicit",
            "wye_and_delta_observations_differ",
            "wye_magnitudes_are_one",
            "delta_magnitudes_are_sqrt_three",
        ),
        "load_continuation": (
            "same_bus_branch_graph",
            "base_scale_converges_for_all_families",
            "continuation_scales_are_ordered",
            "converged_rows_have_small_residuals",
            "constant_power_failure_is_observed",
            "constant_power_fails_before_voltage_dependent_families",
            "continuation_is_not_global_certificate",
        ),
        "explicit_earth": (
            "same_bus_branch_graph",
            "earth_port_retained",
            "outage_changes_earth_current",
            "fault_increases_fault_current",
            "fault_crosses_protection_threshold",
            "outage_does_not_equal_ideal_reference",
            "asset_identity_retained",
            "touch_voltage_observation_changes",
            "maintenance_changes_availability",
            "multiple_fault_classes_retained",
            "ct_measurement_map_retained",
            "relay_curve_observation_retained",
            "relay_time_limit_is_evaluated",
            "ct_saturation_can_change_trip_decision",
        ),
    }.items():
        checks = load_grounding.get(family, {}).get("checks", {})
        for name in names:
            if checks.get(name) is not True:
                errors.append(f"load/grounding witness check failed: {family}.{name}")

    load_reproduction = load_json(LOAD_MODEL_REPRODUCTION)
    if load_reproduction.get("claim_id") != "LOAD-DECISION-001":
        errors.append("load-model independent reproduction has an invalid claim ID")
    if load_reproduction.get("all_checks_pass") is not True:
        errors.append("load-model independent reproduction failed")
    for name in (
        "all_rows_match_julia",
        "independent_iteration_used",
        "same_graph_and_limits_reused",
        "zip_coefficients_reconstructed",
        "zip_reactive_coefficients_reconstructed",
        "no_numpy_or_julia_import",
    ):
        if load_reproduction.get("checks", {}).get(name) is not True:
            errors.append(f"load-model independent reproduction check failed: {name}")

    connection_reproduction = load_json(CONNECTION_MAP_REPRODUCTION)
    if connection_reproduction.get("claim_id") != "LOAD-CONNECTION-001":
        errors.append("connection-map independent reproduction has an invalid claim ID")
    if connection_reproduction.get("all_checks_pass") is not True:
        errors.append("connection-map independent reproduction failed")
    for name in (
        "wye_matches_julia",
        "delta_matches_julia",
        "wye_magnitudes_are_one",
        "delta_magnitudes_are_sqrt_three",
        "no_numpy_or_julia_import",
    ):
        if connection_reproduction.get("checks", {}).get(name) is not True:
            errors.append(f"connection-map independent reproduction check failed: {name}")

    continuation_reproduction = load_json(LOAD_CONTINUATION_REPRODUCTION)
    if continuation_reproduction.get("claim_id") != "LOAD-CONTINUATION-001":
        errors.append("load continuation independent reproduction has an invalid claim ID")
    if continuation_reproduction.get("all_checks_pass") is not True:
        errors.append("load continuation independent reproduction failed")
    for name in (
        "all_rows_match_julia",
        "independent_iteration_used",
        "cp_first_failure_is_scale_1_8",
        "no_numpy_or_julia_import",
    ):
        if continuation_reproduction.get("checks", {}).get(name) is not True:
            errors.append(f"load continuation independent reproduction check failed: {name}")

    neutral_reproduction = load_json(NEUTRAL_KRON_REPRODUCTION)
    if neutral_reproduction.get("claim_id") != "TR-KRON-NEUTRAL-001":
        errors.append("neutral Kron independent reproduction has an invalid claim ID")
    if neutral_reproduction.get("all_checks_pass") is not True:
        errors.append("neutral Kron independent reproduction failed")
    for name in (
        "left_current_matches_julia",
        "right_current_matches_julia",
        "recovery_is_exact",
        "limit_violation_is_retained",
        "shunt_left_current_matches_julia",
        "shunt_right_current_matches_julia",
        "shunt_kcl_is_exact",
        "shunt_limit_violation_is_retained",
        "no_numpy_or_julia_import",
    ):
        if neutral_reproduction.get("checks", {}).get(name) is not True:
            errors.append(f"neutral Kron independent reproduction check failed: {name}")

    explicit_earth_kron = load_json(EXPLICIT_EARTH_KRON_WITNESS)
    if explicit_earth_kron.get("witness_id") != "TR-KRON-NEUTRAL-002" or explicit_earth_kron.get("claim_id") not in claim_ids:
        errors.append("explicit-earth Kron witness has an invalid witness or claim ID")
    if explicit_earth_kron.get("all_checks_pass") is not True:
        errors.append("explicit-earth Kron witness failed")
    for name in (
        "internal_block_is_invertible",
        "terminal_order_retains_earth",
        "earth_port_is_explicit",
        "neutral_kcl_recovery_is_exact",
        "earth_kcl_recovery_is_exact",
        "bond_current_is_observed",
        "neutral_limit_is_evaluated",
        "earth_return_is_not_collapsed_to_neutral",
    ):
        if explicit_earth_kron.get("checks", {}).get(name) is not True:
            errors.append(f"explicit-earth Kron check failed: {name}")
    if explicit_earth_kron.get("terminal_order") != ["a", "b", "c", "n", "e"]:
        errors.append("explicit-earth Kron witness lost its declared terminal order")
    multiple_grounding = explicit_earth_kron.get("multiple_grounding_witness", {})
    for name in (
        "two_internal_blocks_are_invertible",
        "multiple_grounding_points_are_explicit",
        "first_bond_kcl_is_exact",
        "second_bond_kcl_is_exact",
        "both_bonds_are_observed",
        "neutral_limit_is_evaluated_at_each_segment",
    ):
        if multiple_grounding.get("checks", {}).get(name) is not True:
            errors.append(f"multiple-grounding Kron check failed: {name}")
    if multiple_grounding.get("all_checks_pass") is not True:
        errors.append("multiple-grounding Kron witness failed")

    explicit_earth_kron_reproduction = load_json(EXPLICIT_EARTH_KRON_REPRODUCTION)
    if explicit_earth_kron_reproduction.get("claim_id") != "TR-KRON-NEUTRAL-002":
        errors.append("explicit-earth Kron independent reproduction has an invalid claim ID")
    if explicit_earth_kron_reproduction.get("all_checks_pass") is not True:
        errors.append("explicit-earth Kron independent reproduction failed")
    for name in (
        "all_values_match_julia",
        "neutral_kcl_is_exact",
        "earth_kcl_is_exact",
        "earth_port_retained",
        "no_numpy_or_julia_import",
        "multiple_grounding_values_match_julia",
        "multiple_grounding_kcl_is_exact",
    ):
        if explicit_earth_kron_reproduction.get("checks", {}).get(name) is not True:
            errors.append(f"explicit-earth Kron independent reproduction check failed: {name}")

    grounding_sweep = load_json(GROUNDING_IMPEDANCE_SWEEP)
    if grounding_sweep.get("witness_id") != "TR-KRON-NEUTRAL-004" or grounding_sweep.get("claim_id") not in claim_ids:
        errors.append("grounding impedance sweep has an invalid witness or claim ID")
    if grounding_sweep.get("all_checks_pass") is not True:
        errors.append("grounding impedance sweep failed")
    for name in (
        "all_internal_blocks_are_invertible",
        "all_grounding_kcl_residuals_are_small",
        "impedance_changes_recovered_neutral_current",
        "feasibility_classification_changes",
        "limit_margin_is_recorded_per_case",
    ):
        if grounding_sweep.get("checks", {}).get(name) is not True:
            errors.append(f"grounding impedance sweep check failed: {name}")
    if len(grounding_sweep.get("rows", [])) != 4:
        errors.append("grounding impedance sweep must contain four declared cases")

    grounding_reproduction = load_json(GROUNDING_IMPEDANCE_REPRODUCTION)
    if grounding_reproduction.get("claim_id") != "TR-KRON-NEUTRAL-004":
        errors.append("grounding impedance independent reproduction has an invalid claim ID")
    if grounding_reproduction.get("all_checks_pass") is not True:
        errors.append("grounding impedance independent reproduction failed")
    for name in (
        "all_rows_match_julia",
        "feasibility_classification_changes",
        "all_kcl_residuals_are_small",
        "independent_solver_used",
        "no_numpy_or_julia_import",
    ):
        if grounding_reproduction.get("checks", {}).get(name) is not True:
            errors.append(f"grounding impedance independent reproduction check failed: {name}")

    nonlinear_grounding = load_json(NONLINEAR_GROUNDING_PROBE)
    if nonlinear_grounding.get("witness_id") != "TR-KRON-NEUTRAL-005" or nonlinear_grounding.get("claim_id") not in claim_ids:
        errors.append("nonlinear grounding probe has an invalid witness or claim ID")
    if nonlinear_grounding.get("all_checks_pass") is not True:
        errors.append("nonlinear grounding probe failed")
    for name in (
        "base_nonlinear_solve_converged",
        "shifted_nonlinear_solve_converged",
        "state_changes_bond_admittance",
        "frozen_map_is_not_exact_at_shifted_state",
        "recomputed_map_is_exact_at_shifted_state",
        "bond_current_changes_after_recompute",
        "neutral_limit_is_evaluated_after_recompute",
    ):
        if nonlinear_grounding.get("checks", {}).get(name) is not True:
            errors.append(f"nonlinear grounding probe check failed: {name}")

    nonlinear_reproduction = load_json(NONLINEAR_GROUNDING_REPRODUCTION)
    if nonlinear_reproduction.get("claim_id") != "TR-KRON-NEUTRAL-005":
        errors.append("nonlinear grounding independent reproduction has an invalid claim ID")
    if nonlinear_reproduction.get("all_checks_pass") is not True:
        errors.append("nonlinear grounding independent reproduction failed")
    for name in (
        "base_values_match_julia",
        "shifted_values_match_julia",
        "frozen_values_match_julia",
        "base_solve_is_exact",
        "shifted_solve_is_exact",
        "frozen_map_is_not_exact",
        "neutral_limit_is_evaluated",
        "no_numpy_or_julia_import",
    ):
        if nonlinear_reproduction.get("checks", {}).get(name) is not True:
            errors.append(f"nonlinear grounding independent reproduction check failed: {name}")

    nonlinear_two_point = load_json(NONLINEAR_TWO_POINT_GROUNDING)
    if nonlinear_two_point.get("witness_id") != "TR-KRON-NEUTRAL-006" or nonlinear_two_point.get("claim_id") not in claim_ids:
        errors.append("nonlinear two-point grounding probe has an invalid witness or claim ID")
    if nonlinear_two_point.get("all_checks_pass") is not True:
        errors.append("nonlinear two-point grounding probe failed")
    for name in (
        "base_nonlinear_chain_converged",
        "shifted_nonlinear_chain_converged",
        "both_bond_maps_change_with_state",
        "frozen_chain_map_is_not_exact",
        "recomputed_chain_map_is_exact",
        "neutral_limit_is_evaluated_on_recomputed_chain",
        "frozen_and_recomputed_neutral_currents_differ",
    ):
        if nonlinear_two_point.get("checks", {}).get(name) is not True:
            errors.append(f"nonlinear two-point grounding check failed: {name}")

    nonlinear_two_point_reproduction = load_json(NONLINEAR_TWO_POINT_REPRODUCTION)
    if nonlinear_two_point_reproduction.get("claim_id") != "TR-KRON-NEUTRAL-006":
        errors.append("nonlinear two-point grounding independent reproduction has an invalid claim ID")
    if nonlinear_two_point_reproduction.get("all_checks_pass") is not True:
        errors.append("nonlinear two-point grounding independent reproduction failed")
    for name in (
        "base_values_match_julia",
        "shifted_values_match_julia",
        "frozen_values_match_julia",
        "base_solve_is_exact",
        "shifted_solve_is_exact",
        "frozen_chain_map_is_not_exact",
        "neutral_limit_is_evaluated",
        "no_numpy_or_julia_import",
    ):
        if nonlinear_two_point_reproduction.get("checks", {}).get(name) is not True:
            errors.append(f"nonlinear two-point grounding independent reproduction check failed: {name}")

    continuation = load_json(NONLINEAR_TWO_POINT_CONTINUATION)
    if continuation.get("witness_id") != "TR-KRON-NEUTRAL-007" or continuation.get("claim_id") not in claim_ids:
        errors.append("nonlinear grounding continuation has an invalid witness or claim ID")
    if continuation.get("all_checks_pass") is not True:
        errors.append("nonlinear grounding continuation failed")
    for name in (
        "all_continuation_points_converged",
        "all_limit_margins_recorded",
        "frozen_nominal_map_fails_off_base",
        "recomputed_path_has_multiple_states",
        "endpoint_state_path_is_explicit",
    ):
        if continuation.get("checks", {}).get(name) is not True:
            errors.append(f"nonlinear grounding continuation check failed: {name}")
    if len(continuation.get("rows", [])) != 5:
        errors.append("nonlinear grounding continuation must contain five state points")

    continuation_reproduction = load_json(NONLINEAR_TWO_POINT_CONTINUATION_REPRODUCTION)
    if continuation_reproduction.get("claim_id") != "TR-KRON-NEUTRAL-007":
        errors.append("nonlinear grounding continuation independent reproduction has an invalid claim ID")
    if continuation_reproduction.get("all_checks_pass") is not True:
        errors.append("nonlinear grounding continuation independent reproduction failed")
    for name in (
        "all_rows_match_julia",
        "all_continuation_points_converged",
        "frozen_nominal_map_fails_off_base",
        "recomputed_path_has_multiple_states",
        "independent_solver_used",
        "no_numpy_or_julia_import",
    ):
        if continuation_reproduction.get("checks", {}).get(name) is not True:
            errors.append(f"nonlinear grounding continuation independent reproduction check failed: {name}")

    reproduction = load_json(EXPLICIT_EARTH_REPRODUCTION)
    if reproduction.get("claim_id") != "GROUND-SCOPE-004":
        errors.append("explicit-earth independent reproduction has an invalid claim ID")
    if reproduction.get("all_checks_pass") is not True:
        errors.append("explicit-earth independent reproduction failed")
    for name in ("all_rows_match_julia", "independent_solver_used", "no_numpy_or_julia_import"):
        if reproduction.get("checks", {}).get(name) is not True:
            errors.append(f"explicit-earth independent reproduction check failed: {name}")

    running_radiality = load_json(RUNNING_NETWORK_RADIALITY)
    if running_radiality.get("witness_id") != "TOPO-RUNNING-001":
        errors.append("running-network radiality witness has an invalid witness ID")
    if running_radiality.get("evidence_type") != "running_network_state_radiality_witness":
        errors.append("running-network radiality witness has an invalid evidence type")
    running_checks = running_radiality.get("checks", {})
    for name in (
        "base_preserves_parallel_member_cycle",
        "switch_open_preserves_member_cycle",
        "line_outage_removes_parallel_cycle",
        "switch_and_line_outage_remain_radial",
        "terminal_provenance_retained",
        "transformer_factor_provenance_retained",
    ):
        if running_checks.get(name) is not True:
            errors.append(f"running-network radiality witness check failed: {name}")

    conductor_lift = load_json(CONDUCTOR_TERMINAL_LIFT)
    if conductor_lift.get("witness_id") != "ARCH-CONDUCTOR-001":
        errors.append("conductor-terminal lift has an invalid witness ID")
    if conductor_lift.get("evidence_type") != "conductor_terminal_incidence_witness":
        errors.append("conductor-terminal lift has an invalid evidence type")
    lift_checks = conductor_lift.get("checks", {})
    for name in (
        "all_factor_ports_resolve",
        "line_factors_are_two_port",
        "transformer_is_multi_terminal",
        "switch_has_three_state_domain",
        "closed_switch_contraction_is_per_conductor",
        "unknown_switch_has_no_forced_contraction",
    ):
        if lift_checks.get(name) is not True:
            errors.append(f"conductor-terminal lift check failed: {name}")

    hierarchy = load_json(HIERARCHY_BOUNDARY)
    if hierarchy.get("witness_id") != "ARCH-BOUNDARY-001":
        errors.append("hierarchy boundary witness has an invalid witness ID")
    if hierarchy.get("evidence_type") != "hierarchy_boundary_refinement_witness":
        errors.append("hierarchy boundary witness has an invalid evidence type")
    hierarchy_checks = hierarchy.get("checks", {})
    for name in (
        "hierarchy_is_acyclic_by_parent_chain",
        "source_boundary_is_typed",
        "target_boundary_is_typed",
        "refinement_is_total_on_declared_subset",
        "gluing_reuses_shared_boundary",
        "unknown_state_defers_boundary_map",
        "all_structural_checks_pass",
    ):
        if hierarchy_checks.get(name) is not True:
            errors.append(f"hierarchy boundary witness check failed: {name}")

    api_manifest = load_json(PUBLIC_API_MANIFEST)
    if api_manifest.get("package") != "GraphModelsForPowerNetworks":
        errors.append("public API manifest names an unexpected package")
    if api_manifest.get("version") != "0.1.0":
        errors.append("public API manifest has an unsupported version")
    stable_exports = api_manifest.get("stable_exports")
    if (
        not isinstance(stable_exports, list)
        or not stable_exports
        or len(stable_exports) != len(set(stable_exports))
        or not all(isinstance(value, str) and value for value in stable_exports)
    ):
        errors.append("public API manifest has invalid stable exports")
    expected_exports = {
        "IdentifiedEdge", "canonical_pair", "connected_components", "cycle_rank",
        "incidence_matrix", "simple_projection", "kron_reduce", "transform_blocks",
        "recovered_current", "UnitSpec", "UnitSystem", "VariableSpec", "StateDomain",
        "BoundarySpec", "StateSpaceSpec", "convert_value", "to_per_unit", "from_per_unit",
        "state_variables", "boundary_variables", "validate_state_space", "state_space_dict",
        "running_state_space", "attach_typed_interfaces", "validate_certificate",
        "compose_certificates", "api_manifest",
    }
    if set(stable_exports or []) != expected_exports:
        errors.append("public API manifest stable exports differ from the facade")
    for layer in ("multigraph primitives", "typed linear Kron reduction", "typed state-space and units", "certificate contracts"):
        if layer not in api_manifest.get("stable_layers", []):
            errors.append(f"public API manifest omits stable layer {layer!r}")
    if "solver-backed AC decision cases" not in api_manifest.get("experimental_layers", []):
        errors.append("public API manifest omits solver-backed experimental layer")
    if not isinstance(api_manifest.get("boundary_rule"), str) or not api_manifest["boundary_rule"]:
        errors.append("public API manifest lacks a boundary rule")

    state_space = load_json(STATE_SPACE_UNIT)
    if state_space.get("witness_id") != "ARCH-STATE-UNIT-001":
        errors.append("typed state-space witness has an invalid witness ID")
    if state_space.get("evidence_type") != "typed_state_space_unit_witness":
        errors.append("typed state-space witness has an invalid evidence type")
    if state_space.get("source_fixture") != "data/running-network/v0.1.0.json":
        errors.append("typed state-space witness names an unexpected source fixture")
    state_checks = state_space.get("checks", {})
    for name in (
        "state_space_valid",
        "boundary_projection_is_typed",
        "switch_state_domain_is_explicit",
        "unit_conversion_is_family_checked",
    ):
        if state_checks.get(name) is not True:
            errors.append(f"typed state-space witness check failed: {name}")
    space = state_space.get("space", {})
    validation = space.get("validation", {})
    if validation.get("valid") is not True or validation.get("n_variables") != 4:
        errors.append("typed state-space validation summary changed")
    if validation.get("n_state_variables") != 2 or validation.get("n_boundaries") != 2:
        errors.append("typed state-space cardinalities changed")
    domains = space.get("state_domains", [])
    if domains != [{"values": ["open", "closed", "unknown"], "id": "switch_state"}]:
        errors.append("typed state-space switch domain changed")

    semantic_matrix = load_json(SEMANTIC_EVALUATOR_MATRIX)
    if semantic_matrix.get("witness_id") != "PKG-SEMANTIC-001":
        errors.append("semantic evaluator matrix has an invalid witness ID")
    if semantic_matrix.get("schema_version") != "0.1.0":
        errors.append("semantic evaluator matrix has an unsupported schema version")
    if semantic_matrix.get("state_space_ref") != "experiments/generated/state-space-unit-witness.json":
        errors.append("semantic evaluator matrix names an unexpected state-space witness")
    semantic_rows = semantic_matrix.get("rows", [])
    expected_semantic_artifacts = {
        f"experiments/generated/{artifact}" for artifact in CERTIFICATES
    }
    if len(semantic_rows) != len(expected_semantic_artifacts):
        errors.append("semantic evaluator matrix row count changed")
    if {row.get("artifact") for row in semantic_rows} != expected_semantic_artifacts:
        errors.append("semantic evaluator matrix does not cover the certificate set")
    for row in semantic_rows:
        row_checks = row.get("checks", {})
        if row.get("valid") is not True or not all(row_checks.values()):
            errors.append(f"semantic evaluator matrix row is not valid: {row.get('artifact')}")
        for field in ("evaluator", "semantic_test", "evaluator_symbol"):
            path = row.get(field)
            if field != "evaluator_symbol" and (not isinstance(path, str) or not (ROOT / path).is_file()):
                errors.append(f"semantic evaluator matrix {field} is not a repository path: {path}")
    semantic_checks = semantic_matrix.get("checks", {})
    for name in (
        "all_certificates_covered", "all_evaluators_exist", "all_tests_exist",
        "all_typed_contracts_present", "all_semantic_evidence_bound",
    ):
        if semantic_checks.get(name) is not True:
            errors.append(f"semantic evaluator matrix check failed: {name}")

    fixture_matrix = load_json(FIXTURE_COVERAGE_MATRIX)
    if fixture_matrix.get("witness_id") != "PKG-FIXTURE-001":
        errors.append("fixture coverage matrix has an invalid witness ID")
    if fixture_matrix.get("schema_version") != "0.1.0":
        errors.append("fixture coverage matrix has an unsupported schema version")
    if fixture_matrix.get("status_vocabulary") != ["direct", "related", "not_yet_tested", "not_applicable"]:
        errors.append("fixture coverage matrix status vocabulary changed")
    fixture_checks = fixture_matrix.get("checks", {})
    for name in (
        "fixture_definitions_exist", "all_fixture_families_present",
        "all_map_families_have_declared_scope", "direct_evidence_has_artifact",
        "not_yet_tested_is_explicit",
    ):
        if fixture_checks.get(name) is not True:
            errors.append(f"fixture coverage matrix check failed: {name}")
    fixture_rows = fixture_matrix.get("rows", [])
    if len(fixture_rows) != 27:
        errors.append("fixture coverage matrix row count changed")
    valid_statuses = set(fixture_matrix.get("status_vocabulary", []))
    for row in fixture_rows:
        if row.get("status") not in valid_statuses:
            errors.append(f"fixture coverage row has an unknown status: {row}")

    clean_package = load_json(CLEAN_PACKAGE_MATRIX)
    if clean_package.get("witness_id") != "PKG-CLEAN-001":
        errors.append("clean package matrix has an invalid witness ID")
    if clean_package.get("schema_version") != "0.1.0":
        errors.append("clean package matrix has an unsupported schema version")
    if not re.fullmatch(r"[0-9a-f]{40}", clean_package.get("dependency_commit", "")):
        errors.append("clean package matrix does not pin a full dependency commit")
    if clean_package.get("diffopt_version") != "0.6.2":
        errors.append("clean package matrix does not pin the DiffOpt compatibility version")
    if clean_package.get("environment") != "separately instantiated package checkout":
        errors.append("clean package matrix has an unexpected environment description")
    if clean_package.get("tests") != [
        "experiments/test/public_api.jl",
        "experiments/test/state_space_units.jl",
        "experiments/test/certificate_api_matrix.jl",
        "experiments/test/solver_diagnostics_crosswalk.jl",
        "package/GraphModelsForPowerNetworks/test/runtests.jl",
    ]:
        errors.append("clean package matrix test set changed")
    if clean_package.get("semantic_matrix_sha256") != sha256(SEMANTIC_EVALUATOR_MATRIX):
        errors.append("clean package matrix is stale relative to the semantic evaluator matrix")
    if clean_package.get("valid") is not True:
        errors.append("clean package matrix is not marked valid")
    classifications = approximation.get("classifications", {})
    if classifications.get("high_load") != "ambiguous":
        errors.append("certified approximation lost its ambiguous high-load case")
    if classifications.get("low_voltage") != "certified_feasible":
        errors.append("certified approximation lost its feasible low-voltage case")
    if classifications.get("internal_outage_proxy") != "certified_violated":
        errors.append("certified approximation lost its violated outage-proxy case")

    cycle_analysis = load_json(FIVE_BUS_ANALYSIS)
    if cycle_analysis.get("analysis_id") not in claim_ids:
        errors.append("five-bus cycle analysis uses an unregistered claim ID")
    source_cycle = cycle_analysis.get("cycle_space", {})
    simple_cycle = cycle_analysis.get("simple_projection", {})
    electrical = cycle_analysis.get("electrical_check", {})
    witness = electrical.get("parallel_decision_witness", {})
    bmopf = cycle_analysis.get("bmopftools_cross_check", {})
    if source_cycle.get("cycle_rank") != 3 or source_cycle.get("incidence_rank") != 4:
        errors.append("five-bus source cycle-space invariants changed")
    if source_cycle.get("incidence_cycle_residual") != 0:
        errors.append("five-bus fundamental cycles are not in the incidence nullspace")
    if source_cycle.get("bridges") != ["u"]:
        errors.append("five-bus bridge set changed")
    if simple_cycle.get("cycle_rank") != 2 or simple_cycle.get("lost_cycle_dimension") != 1:
        errors.append("five-bus simple-projection cycle-space invariants changed")
    if electrical.get("maximum_ybus_difference", float("inf")) > 1.0e-12:
        errors.append("five-bus source and aggregated nodal admittances differ")
    if witness.get("aggregate_feasible") is not True or witness.get("source_feasible") is not False:
        errors.append("five-bus parallel decision witness no longer exposes the relaxation")
    if witness.get("source_voltage_limit_V") != 10.0:
        errors.append("five-bus source feasible-voltage boundary changed")
    if abs(witness.get("aggregate_voltage_limit_V", float("inf")) - 200 / 11) > 1.0e-12:
        errors.append("five-bus naive-aggregate feasible-voltage boundary changed")
    if bmopf.get("n_extra_edges") != 3 or bmopf.get("expected") != 3:
        errors.append("BMOPFTools five-bus cycle-rank cross-check changed")

    numerical = load_json(NUMERICAL_STRUCTURE_WITNESS)
    if numerical.get("witness_id") != "NUM-STRUCT-001":
        errors.append("numerical structure witness ID changed")
    physical = numerical.get("physical_incidence", {})
    if physical.get("member_edge_count") != 7 or physical.get("simple_projection_edge_count") != 6:
        errors.append("numerical structure witness lost the five-bus parallel-member distinction")
    elimination = numerical.get("elimination", {})
    if elimination.get("eliminated_node") != "j":
        errors.append("numerical structure witness elimination node changed")
    if elimination.get("fill_edges") != [["i", "l"]]:
        errors.append("numerical structure witness fill edge changed")
    dependency = numerical.get("jacobian_dependency", {})
    if dependency.get("nonzero_dependencies") != 30:
        errors.append("numerical structure witness dependency count changed")
    checks = numerical.get("checks", {})
    for name in ("neighbour_clique_verified", "fill_is_not_a_source_asset", "physical_and_jacobian_graphs_are_distinct"):
        if checks.get(name) is not True:
            errors.append(f"numerical structure witness check failed: {name}")
    for name in (
        "typed_kron_fill_crosswalk_matches",
        "typed_kron_boundary_residual_is_small",
        "typed_kron_constraint_observation_retained",
    ):
        if checks.get(name) is not True:
            errors.append(f"numerical/typed-Kron crosswalk check failed: {name}")
    crosswalk = numerical.get("typed_kron_crosswalk", {})
    if crosswalk.get("fill_edges") != ["j-m", "k-m"] or crosswalk.get("eliminated_node") != "l":
        errors.append("numerical/typed-Kron crosswalk provenance changed")

    ybus = load_json(YBUS_JACOBIAN_WITNESS)
    if ybus.get("claim_id") not in claim_ids or ybus.get("witness_id") != "NUM-YBUS-001":
        errors.append("Ybus/Jacobian witness uses an invalid claim or witness ID")
    if ybus.get("source_fixture") != "data/running-network/v0.1.0.json":
        errors.append("Ybus/Jacobian witness names an unexpected source fixture")
    passive = ybus.get("passive_ybus", {})
    linearized = ybus.get("linearized_ybus", {})
    realified = ybus.get("realified_current_jacobian", {})
    if passive.get("rows") != 20 or passive.get("cols") != 20 or passive.get("nnz_atol") != 166:
        errors.append("running-network passive Ybus dimensions or sparsity changed")
    if linearized.get("rows") != 20 or linearized.get("nnz_atol") != 166:
        errors.append("running-network linearized Ybus dimensions or sparsity changed")
    if realified.get("rows") != 40 or realified.get("cols") != 40 or realified.get("nnz_atol") != 664:
        errors.append("running-network realified current Jacobian dimensions or sparsity changed")
    ybus_checks = ybus.get("checks", {})
    for name in ("linearized_matches_passive_at_constant_z", "reciprocal_complex_symmetry", "realification_is_real", "realification_dimension_doubles"):
        if ybus_checks.get(name) is not True:
            errors.append(f"Ybus/Jacobian witness check failed: {name}")

    kkt = load_json(NONLINEAR_KKT_WITNESS)
    if kkt.get("claim_id") not in claim_ids or kkt.get("witness_id") != "NUM-KKT-001":
        errors.append("nonlinear KKT witness uses an invalid claim or witness ID")
    source_kkt = kkt.get("source", {})
    aggregate_kkt = kkt.get("aggregate", {})
    if source_kkt.get("jacobian", {}).get("nnz_atol") != 26 or source_kkt.get("kkt", {}).get("dimension") != 13:
        errors.append("nonlinear source Jacobian/KKT dimensions changed")
    if aggregate_kkt.get("jacobian", {}).get("nnz_atol") != 16 or aggregate_kkt.get("kkt", {}).get("dimension") != 9:
        errors.append("nonlinear aggregate Jacobian/KKT dimensions changed")
    if source_kkt.get("kkt", {}).get("orders", {}).get("natural", {}).get("fill_edges") != 15:
        errors.append("nonlinear source natural-order fill count changed")
    if aggregate_kkt.get("kkt", {}).get("orders", {}).get("natural", {}).get("fill_edges") != 6:
        errors.append("nonlinear aggregate natural-order fill count changed")
    kkt_checks = kkt.get("checks", {})
    for name in ("source_operating_point_is_exact", "aggregate_operating_point_is_exact", "source_retains_more_current_variables", "ordering_changes_fill"):
        if kkt_checks.get(name) is not True:
            errors.append(f"nonlinear KKT witness check failed: {name}")

    figure_manifest = load_json(FIVE_BUS_FIGURE_MANIFEST)
    if figure_manifest.get("schema_version") != "1.0.0":
        errors.append("five-bus figure manifest has an unsupported schema version")
    if figure_manifest.get("generator") != "experiments/generate_five_bus_cycle_figure.py":
        errors.append("five-bus figure manifest names an unexpected generator")
    if figure_manifest.get("source_analysis") != "experiments/generated/five-bus-cycle-space-analysis.json":
        errors.append("five-bus figure manifest names an unexpected analysis source")
    if figure_manifest.get("source_analysis_sha256") != sha256(FIVE_BUS_ANALYSIS):
        errors.append("five-bus figures were not generated from the current analysis")
    recorded_figures = figure_manifest.get("figures", {})
    if set(recorded_figures) != set(FIVE_BUS_FIGURES):
        errors.append("five-bus figure manifest does not list the expected figure set")
    for name, path in FIVE_BUS_FIGURES.items():
        record = recorded_figures.get(name, {})
        if record.get("path") != str(path.relative_to(ROOT)):
            errors.append(f"five-bus figure {name} has an unexpected manifest path")
        if record.get("sha256") != sha256(path):
            errors.append(f"five-bus figure {name} does not match its manifest hash")

    certificate_schema = load_json(CERTIFICATE_SCHEMA)
    for artifact in CERTIFICATES:
        certificate = load_json(GENERATED / artifact)
        errors.extend(validate_certificate(certificate, certificate_schema, artifact))
        if certificate.get("typed_interfaces", {}).get("state_space_ref") != (
            "experiments/generated/state-space-unit-witness.json"
        ):
            errors.append(f"{artifact} is not attached to the canonical typed state-space witness")
        certificate_id = certificate.get("certificate_id")
        if certificate_id not in claim_ids:
            errors.append(f"{artifact} uses unregistered claim/certificate ID {certificate_id!r}")

    provenance = load_json(GENERATED / "provenance.json")
    repository = provenance.get("bmopftools_repository", {})
    if not re.fullmatch(r"[0-9a-f]{40}", repository.get("commit", "")):
        errors.append("provenance does not contain a full BMOPFTools commit")
    if not isinstance(repository.get("dirty"), bool):
        errors.append("provenance dirty state is not boolean")

    clean_repository = load_json(CLEAN_REPRODUCTION / "provenance.json").get(
        "bmopftools_repository", {}
    )
    if clean_repository.get("dirty") is not False:
        errors.append("clean reproduction records a dirty BMOPFTools checkout")
    if clean_repository.get("commit") != repository.get("commit"):
        errors.append("local and clean reproductions use different BMOPFTools commits")
    if (CLEAN_REPRODUCTION / "v0.1.0.json").read_bytes() != FIXTURE.read_bytes():
        errors.append("clean reproduction fixture differs from the canonical fixture")
    clean_summary = load_json(CLEAN_REPRODUCTION / "summary.json")
    for field in ("power_flow", "optimal_power_flow"):
        if clean_summary.get(field, {}).get("termination_status") != summary.get(field, {}).get("termination_status"):
            errors.append(f"clean and local {field} termination statuses differ")

    maps = load_json(SOURCE_MAP)
    if set(maps.get("views", {})) != EXPECTED_VIEWS:
        errors.append("view source-map set does not match the required generated views")
    if maps.get("fixture_sha256") != sha256(FIXTURE):
        errors.append("view source map was not generated from the current fixture")
    if maps.get("figure_sha256") != sha256(FIGURE):
        errors.append("view source map does not match the current figure")
    for view_name, view in maps.get("views", {}).items():
        generated_ids: set[str] = set()
        objects = view.get("generated_objects", [])
        if not objects:
            errors.append(f"view {view_name} has no mapped generated objects")
        for generated in objects:
            generated_id = generated.get("generated_id", "")
            if generated_id in generated_ids:
                errors.append(f"view {view_name} repeats generated ID {generated_id}")
            generated_ids.add(generated_id)
            object_sources = generated.get("sources", [])
            if not object_sources:
                errors.append(f"view {view_name} object {generated_id} has no source")
            unknown = set(object_sources) - sources
            if unknown:
                errors.append(f"view {view_name} object {generated_id} has unknown sources {sorted(unknown)}")

    checked_links = check_links(errors)
    if errors:
        print("artifact validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"artifacts: {len(required)} required files, {len(CERTIFICATES)} certificates, "
        f"{len(TRANSFORMER_CONTRACTS)} transformer contracts, "
        f"{len(sources)} source objects, {len(EXPECTED_VIEWS)} view maps, "
        f"and {checked_links} local links valid"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
