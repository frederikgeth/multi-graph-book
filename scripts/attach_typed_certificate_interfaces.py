#!/usr/bin/env python3
"""Repair or migrate legacy certificates with the checked typed crosswalk.

Current Julia generators attach the crosswalk directly through
TransformationContracts.attach_typed_interfaces; this script remains useful
for older generated artifacts and bulk migrations.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "experiments/generated"
STATE_SPACE_REF = "experiments/generated/state-space-unit-witness.json"


def families(label: str) -> list[str]:
    text = label.lower()
    found: list[str] = []
    if "voltage" in text or re.search(r"(^|[^a-z])v([^a-z]|$)", text):
        found.append("voltage")
    if "current" in text or re.search(r"(^|[^a-z])a([^a-z]|$)", text):
        found.append("current")
    if any(token in text for token in ("power", "mva", "mw", "kw")):
        found.append("power")
    if "ohm" in text or "impedance" in text:
        found.append("impedance")
    if "siemens" in text or re.search(r"(^|[^a-z])s([^a-z]|$)", text) or "admittance" in text:
        found.append("admittance")
    if "dimensionless" in text or "per-unit" in text or "pu" in text:
        found.append("dimensionless")
    return sorted(set(found))


def attachment(certificate: dict) -> dict:
    units = certificate["interfaces"]["units"]
    source_units = [str(value) for value in units["source"]]
    target_units = [str(value) for value in units["target"]]
    unit_map: dict[str, list[str]] = {}
    unresolved: list[str] = []
    for label in sorted(set(source_units + target_units)):
        mapped = families(label)
        unit_map[label] = mapped
        if not mapped:
            unresolved.append(label)

    return {
        "state_space_ref": STATE_SPACE_REF,
        "source_variable_labels": list(dict.fromkeys(map(str, certificate["interfaces"]["state_variables"]["source"]))),
        "target_variable_labels": list(dict.fromkeys(map(str, certificate["interfaces"]["state_variables"]["target"]))),
        "source_unit_families": sorted({family for label in source_units for family in families(label)}),
        "target_unit_families": sorted({family for label in target_units for family in families(label)}),
        "source_boundary_labels": list(dict.fromkeys(map(str, certificate["interfaces"]["boundary_quantities"]["source"]))),
        "target_boundary_labels": list(dict.fromkeys(map(str, certificate["interfaces"]["boundary_quantities"]["target"]))),
        "state_domain_ids": [],
        "unit_family_map": unit_map,
        "unresolved_unit_labels": unresolved,
        "attachment_rule": "certificate-local interface labels are crosswalked to the checked typed state-space/unit vocabulary; unresolved labels remain explicit rather than being guessed",
    }


def main() -> int:
    paths = sorted(GENERATED.glob("*-certificate.json"))
    paths.append(GENERATED / "parallel-opf-comparison.json")
    paths = [path for path in paths if path.is_file()]
    if not paths:
        raise SystemExit("no transformation certificates found")
    for path in paths:
        certificate = json.loads(path.read_text())
        certificate["typed_interfaces"] = attachment(certificate)
        path.write_text(json.dumps(certificate, indent=2, ensure_ascii=False) + "\n")
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
