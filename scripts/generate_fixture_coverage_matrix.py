#!/usr/bin/env python3
"""Record which canonical fixtures currently exercise each map family."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "experiments/generated/fixture-coverage-matrix.json"
FIXTURES = {
    "running_network": "data/running-network/v0.1.0.json",
    "five_bus_cycle_space": "experiments/generated/five-bus-cycle-space-analysis.json",
    "multiwinding_transformer": "data/transformer-contracts/x1-fixed-linear-v0.1.0.json",
}
ROWS = [
    ("port_factor_architecture", "running_network", "direct", "port-factor-architecture.json"),
    ("port_factor_architecture", "five_bus_cycle_space", "direct", "five-bus-port-factor-witness.json"),
    ("port_factor_architecture", "multiwinding_transformer", "direct", "port-factor-architecture.json"),
    ("conductor_terminal_lift", "running_network", "direct", "conductor-terminal-lift-witness.json"),
    ("conductor_terminal_lift", "five_bus_cycle_space", "direct", "five-bus-conductor-terminal-lift-witness.json"),
    ("conductor_terminal_lift", "multiwinding_transformer", "direct", "multiwinding-terminal-lift-witness.json"),
    ("active_radiality", "running_network", "direct", "running-network-radiality-witness.json"),
    ("active_radiality", "five_bus_cycle_space", "direct", "five-bus-active-radiality-witness.json"),
    ("active_radiality", "multiwinding_transformer", "not_applicable", ""),
    ("five_bus_cycle_space", "running_network", "direct", "running-network-cycle-space-witness.json"),
    ("five_bus_cycle_space", "five_bus_cycle_space", "direct", "five-bus-cycle-space-analysis.json"),
    ("five_bus_cycle_space", "multiwinding_transformer", "not_yet_tested", ""),
    ("multiwinding_compilation", "running_network", "direct", "multiwinding-terminal-assembly-certificate.json"),
    ("multiwinding_compilation", "five_bus_cycle_space", "not_applicable", ""),
    ("multiwinding_compilation", "multiwinding_transformer", "direct", "multiwinding-terminal-assembly-certificate.json"),
    ("typed_kron_reduction", "running_network", "direct", "running-network-typed-kron-witness.json"),
    ("typed_kron_reduction", "five_bus_cycle_space", "direct", "five-bus-typed-kron-witness.json"),
    ("typed_kron_reduction", "multiwinding_transformer", "direct", "multiwinding-typed-kron-witness.json"),
]


def main() -> int:
    rows = []
    for map_family, fixture, status, artifact in ROWS:
        artifact_path = ROOT / "experiments/generated" / artifact if artifact else None
        rows.append({
            "map_family": map_family,
            "fixture": fixture,
            "status": status,
            "evidence_artifact": f"experiments/generated/{artifact}" if artifact else None,
            "evidence_exists": artifact_path.is_file() if artifact_path else False,
        })
    checks = {
        "fixture_definitions_exist": all((ROOT / path).is_file() for path in FIXTURES.values()),
        "all_fixture_families_present": {row["fixture"] for row in rows} == set(FIXTURES),
        "all_map_families_have_declared_scope": len({row["map_family"] for row in rows}) >= 6,
        "direct_evidence_has_artifact": all(row["status"] != "direct" or row["evidence_exists"] for row in rows),
        "not_yet_tested_is_explicit": any(row["status"] == "not_yet_tested" for row in rows),
    }
    result = {
        "witness_id": "PKG-FIXTURE-001",
        "schema_version": "0.1.0",
        "fixtures": FIXTURES,
        "status_vocabulary": ["direct", "related", "not_yet_tested", "not_applicable"],
        "rows": rows,
        "checks": checks,
        "valid": all(checks.values()),
        "interpretation": "Coverage is declared per map family and canonical fixture. Related evidence is not direct fixture validation, and not_yet_tested remains an explicit open boundary.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
