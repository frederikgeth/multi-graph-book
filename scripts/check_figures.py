#!/usr/bin/env python3
"""Check the maintained figure family and its monochrome audit manifest."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs/src/assets"
MANIFEST = ASSETS / "figure-audit.json"


def main() -> int:
    errors: list[str] = []
    manifest = json.loads(MANIFEST.read_text())
    figures = manifest.get("figures", {})
    svg_paths = {path.relative_to(ROOT).as_posix() for path in ASSETS.glob("*.svg")}
    listed_svg_paths = {entry.get("svg") for entry in figures.values()}
    if svg_paths != listed_svg_paths:
        errors.append("figure audit does not list exactly the maintained SVG family")

    for name, entry in sorted(figures.items()):
        svg_path = ROOT / entry.get("svg", "")
        png_path = ROOT / entry.get("png", "")
        if not svg_path.is_file():
            errors.append(f"{name} is missing its SVG source")
            continue
        if not png_path.is_file():
            errors.append(f"{name} is missing its PDF-safe PNG companion")
        source = svg_path.read_text()
        for marker in ("<title>", "<desc>", "<text"):
            if marker not in source:
                errors.append(f"{name} SVG lacks {marker} accessibility/content marker")
        if entry.get("monochrome_safe") is not True:
            errors.append(f"{name} is not marked monochrome-safe")
        channels = entry.get("distinguishing_channels")
        if not isinstance(channels, list) or not channels:
            errors.append(f"{name} lacks non-colour distinguishing channels")

    if errors:
        print("figure audit failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"figures: {len(figures)} SVG/PNG pairs pass the monochrome audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
