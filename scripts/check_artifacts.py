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
FIGURE = ROOT / "docs/src/assets/running-network-views.png"
FIVE_BUS_ANALYSIS = GENERATED / "five-bus-cycle-space-analysis.json"
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
        *FIVE_BUS_FIGURES.values(),
        GENERATED / "summary.json",
        FIVE_BUS_ANALYSIS,
        FIVE_BUS_FIGURE_MANIFEST,
        CERTIFICATE_SCHEMA,
        *(GENERATED / artifact for artifact in CERTIFICATES),
        GENERATED / "provenance.json",
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
    if source_cycle.get("bridges") != ["x"]:
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
