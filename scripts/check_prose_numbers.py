#!/usr/bin/env python3
"""Check displayed-number consistency and explicit derivation bindings.

Legacy matches against the artifact pool establish numerical agreement only;
they do not establish that the matching artifact supports the passage.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib
from decimal import Decimal, InvalidOperation, localcontext
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
    # The exponent is part of the displayed precision: 1.2345e-6 must not
    # round to four places after the decimal point and falsely match zero.
    return Decimal(literal)


def matches_displayed_number(candidate: Decimal, literal: str) -> bool:
    if not candidate.is_finite():
        return False
    target = quantized(literal)
    quantum = Decimal((0, (1,), target.as_tuple().exponent))
    # New exact-arithmetic artifacts can contain integers wider than the
    # default 28-digit context. Such unrelated values must not crash the gate.
    with localcontext() as context:
        context.prec = max(context.prec, len(candidate.as_tuple().digits),
                           candidate.adjusted() - quantum.as_tuple().exponent + 2)
        return candidate.quantize(quantum) == target


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


def pointer_values(binding: dict, artifact: Path) -> list[Decimal] | None:
    """Resolve explicitly selected JSON values; None retains legacy derivations."""
    if "source_pointer" not in binding and "source_pointers" not in binding:
        return None
    if "source_pointer" in binding and "source_pointers" in binding:
        raise ValueError("choose source_pointer or source_pointers, not both")
    pointers = binding.get("source_pointers", [binding.get("source_pointer")])
    if not isinstance(pointers, list) or not pointers or not all(isinstance(p, str) and p.startswith("/") for p in pointers):
        raise ValueError("source pointers must be a nonempty list of JSON pointers")
    source = json.loads(artifact.read_text(), parse_float=Decimal, parse_int=Decimal)
    values = []
    for pointer in pointers:
        item = source
        for token in pointer.split("/")[1:]:
            token = token.replace("~1", "/").replace("~0", "~")
            if isinstance(item, list):
                if not re.fullmatch(r"0|[1-9][0-9]*", token):
                    raise ValueError("invalid source array index")
                item = item[int(token)]
            else:
                item = item[token]
        if isinstance(item, bool) or not isinstance(item, (str, int, float, Decimal)):
            raise ValueError("source pointer must select a numeric scalar")
        number = Decimal(str(item))
        if not number.is_finite():
            raise ValueError("source pointer must select a finite value")
        values.append(number)
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
    selected_values = {}
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
        if artifact.is_file():
            try:
                selected_values[key] = pointer_values(binding, artifact)
            except (OSError, ValueError, KeyError, IndexError, TypeError, InvalidOperation) as error:
                errors.append(f"invalid source pointer for {key}: {error}")

    values = prose_numbers()
    current_keys = {(value["path"], value["line"], value["literal"]) for value in values}
    artifacts = artifact_values()
    direct_matches = 0
    unmatched = []
    for value in values:
        key = (value["path"], value["line"], value["literal"])
        # An explicit binding cannot fall back to an unrelated number elsewhere
        # in the corpus when its selected observation disagrees or is missing.
        if key in binding_keys:
            selected = selected_values.get(key)
            if selected is not None and not all(matches_displayed_number(n, value["literal"]) for n in selected):
                errors.append(f"selected source value does not match displayed precision: {key}")
        elif any(matches_displayed_number(candidate, value["literal"]) for candidate in artifacts):
            direct_matches += 1
        else:
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
        f"{direct_matches} unscoped numeric matches and {len(bindings)} explicit derived bindings pass"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
