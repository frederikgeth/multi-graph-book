#!/usr/bin/env python3
"""Check that high-precision prose numbers are artifact-bound or explicitly derived."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/src"
ARTIFACTS = ROOT / "experiments/generated"
BINDINGS = ROOT / "review/prose-number-bindings.toml"
EXCLUDED_DOCS = {
    "docs/src/reference/chapter-status.md",
    "docs/src/reference/evidence-map.md",
    "docs/src/reference/knowledge-base-index.md",
    "docs/src/reference/vocabulary-indexes.md",
}
NUMBER = re.compile(r"(?<![A-Za-z0-9_.])[-+]?(?:\d+\.\d+|\.\d+)(?:[eE][-+]?\d+)?")
SCHEMA_VERSION = "0.1.0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decimal_places(literal: str) -> int:
    mantissa = re.split(r"[eE]", literal, maxsplit=1)[0]
    return len(mantissa.split(".", 1)[1]) if "." in mantissa else 0


def quantized(literal: str) -> Decimal:
    places = decimal_places(literal)
    return Decimal(literal).quantize(Decimal(1).scaleb(-places))


def strip_non_prose(text: str) -> str:
    output = []
    in_code_fence = False
    in_math_fence = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```math"):
            in_math_fence = True
            output.append("")
            continue
        if stripped == "```" and in_math_fence:
            in_math_fence = False
            output.append("")
            continue
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            output.append("")
            continue
        if in_code_fence:
            output.append("")
            continue
        output.append(re.sub(r"https?://[^)\s]+", "", line))
    return "\n".join(output)


def prose_numbers() -> list[dict]:
    values = []
    for path in sorted(DOCS.rglob("*.md")):
        relative = path.relative_to(ROOT).as_posix()
        if relative in EXCLUDED_DOCS:
            continue
        text = strip_non_prose(path.read_text())
        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in NUMBER.finditer(line):
                literal = match.group(0)
                if decimal_places(literal) < 4:
                    continue
                values.append({"path": relative, "line": line_number, "literal": literal})
    return values


def numeric_values(value: object) -> list[Decimal]:
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float, Decimal)):
        try:
            return [Decimal(str(value))]
        except InvalidOperation:
            return []
    if isinstance(value, dict):
        values = []
        for item in value.values():
            values.extend(numeric_values(item))
        return values
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(numeric_values(item))
        return values
    return []


def artifact_values() -> list[Decimal]:
    values: list[Decimal] = []
    for path in sorted(ARTIFACTS.rglob("*")):
        if not path.is_file() or path.suffix not in {".json", ".toml"}:
            continue
        try:
            if path.suffix == ".json":
                parsed = json.loads(path.read_text(), parse_float=Decimal, parse_int=Decimal)
            else:
                parsed = tomllib.loads(path.read_text())
        except (OSError, ValueError, tomllib.TOMLDecodeError):
            continue
        values.extend(numeric_values(parsed))
    return values


def main() -> int:
    errors: list[str] = []
    try:
        document = tomllib.loads(BINDINGS.read_text())
    except (OSError, tomllib.TOMLDecodeError) as error:
        print(f"prose-number audit failed to load bindings: {error}")
        return 1
    if document.get("schema_version") != SCHEMA_VERSION:
        errors.append("prose-number binding schema version drift")
    bindings = document.get("binding", [])
    binding_keys = set()
    for binding in bindings:
        key = (binding.get("path"), binding.get("line"), binding.get("literal"))
        if key in binding_keys:
            errors.append(f"duplicate prose-number binding: {key}")
        binding_keys.add(key)
        artifact = ROOT / str(binding.get("source_artifact", ""))
        if not artifact.is_file():
            errors.append(f"binding source artifact is missing: {binding.get('source_artifact')}")
        elif binding.get("source_sha256") != sha256(artifact):
            errors.append(f"binding source artifact hash is stale: {binding.get('source_artifact')}")
        if not str(binding.get("derivation", "")).strip():
            errors.append(f"binding has no derivation explanation: {key}")

    values = prose_numbers()
    current_keys = {(value["path"], value["line"], value["literal"]) for value in values}
    artifacts = artifact_values()
    direct_matches = 0
    unmatched = []
    for value in values:
        places = decimal_places(value["literal"])
        target = quantized(value["literal"])
        if any(candidate.quantize(Decimal(1).scaleb(-places)) == target for candidate in artifacts):
            direct_matches += 1
        elif (value["path"], value["line"], value["literal"]) not in binding_keys:
            unmatched.append((value["path"], value["line"], value["literal"]))
    for key in binding_keys - current_keys:
        errors.append(f"prose-number binding does not match a current literal: {key}")
    errors.extend(f"unbound high-precision prose number: {key}" for key in unmatched)
    if errors:
        print("prose-number audit failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"prose numbers: {len(values)} high-precision literals checked; "
        f"{direct_matches} direct artifact matches and {len(bindings)} explicit derived bindings pass"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
