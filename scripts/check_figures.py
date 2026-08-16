#!/usr/bin/env python3
"""Check the maintained figure family and its monochrome audit manifest."""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs/src/assets"
MANIFEST = ASSETS / "figure-audit.json"


def grayscale_stats(path: Path, max_width: int = 512, max_height: int = 256) -> tuple[int, int, int, float, float]:
    """Decode a committed rendered PNG and compute luminance coverage.

    This is intentionally dependency-free so the gate can run in CI. The
    renderers in this repository emit 8-bit, non-interlaced RGB/RGBA PNGs.
    """
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    pos = 8
    width = height = bit_depth = colour_type = None
    raw = bytearray()
    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        kind = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, colour_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", chunk)
            if bit_depth != 8 or colour_type not in (2, 6) or interlace != 0:
                raise ValueError("unsupported PNG encoding")
        elif kind == b"IDAT":
            raw.extend(chunk)
        elif kind == b"IEND":
            break
    if width is None or height is None:
        raise ValueError("PNG has no IHDR")
    channels = 3 if colour_type == 2 else 4
    stride = width * channels
    decoded = zlib.decompress(bytes(raw))
    rows: list[bytes] = []
    offset = 0
    sample_stride = min(width, max_width) * channels
    previous = bytearray(sample_stride)
    for row_index in range(height):
        filter_type = decoded[offset]
        offset += 1
        # The committed PNG is a rendered companion. A bounded raster sample
        # keeps this dependency-free gate fast even for large plates while
        # still exercising the actual PNG decode and grayscale conversion.
        row = bytearray(decoded[offset : offset + sample_stride])
        offset += stride
        for i in range(sample_stride):
            left = row[i - channels] if i >= channels else 0
            up = previous[i]
            up_left = previous[i - channels] if i >= channels else 0
            if filter_type == 1:
                row[i] = (row[i] + left) & 0xFF
            elif filter_type == 2:
                row[i] = (row[i] + up) & 0xFF
            elif filter_type == 3:
                row[i] = (row[i] + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                p = left + up - up_left
                pa, pb, pc = abs(p - left), abs(p - up), abs(p - up_left)
                predictor = left if pa <= pb and pa <= pc else up if pb <= pc else up_left
                row[i] = (row[i] + predictor) & 0xFF
            elif filter_type != 0:
                raise ValueError(f"unsupported PNG filter {filter_type}")
        if row_index < max_height:
            rows.append(bytes(row))
        previous = row
        if row_index + 1 >= max_height:
            break
    luminance: list[int] = []
    for row in rows:
        for i in range(0, len(row), channels):
            r, g, b = row[i : i + 3]
            if channels == 4:
                alpha = row[i + 3] / 255.0
                # Render transparent SVG background over white, matching the
                # reader-facing raster rather than treating transparent black
                # RGB payloads as visible ink.
                r = int(alpha * r + (1 - alpha) * 255)
                g = int(alpha * g + (1 - alpha) * 255)
                b = int(alpha * b + (1 - alpha) * 255)
            luminance.append((2126 * r + 7152 * g + 722 * b) // 10000)
    dark = sum(value < 64 for value in luminance) / len(luminance)
    light = sum(value > 200 for value in luminance) / len(luminance)
    return min(luminance), max(luminance), len(set(luminance)), dark, light


def main() -> int:
    errors: list[str] = []
    manifest = json.loads(MANIFEST.read_text())
    figures = manifest.get("figures", {})
    grammar = manifest.get("visual_grammar", {})
    required_grammar = {
        "background", "ink", "semantic_channels", "colour_role",
        "required_svg_markers", "required_companion", "audit_rule",
    }
    if not required_grammar <= set(grammar):
        errors.append("figure audit lacks the shared visual-grammar contract")
    if grammar.get("colour_role") != "secondary cue only":
        errors.append("figure audit does not state the colour-only limitation")
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
        else:
            try:
                minimum, maximum, levels, dark_fraction, light_fraction = grayscale_stats(png_path)
                if maximum - minimum < 100 or levels < 8 or dark_fraction < 0.001 or light_fraction < 0.05:
                    errors.append(
                        f"{name} grayscale render has weak coverage "
                        f"(range={minimum}-{maximum}, levels={levels}, "
                        f"dark={dark_fraction:.3f}, light={light_fraction:.3f})"
                    )
            except (ValueError, struct.error, zlib.error) as error:
                errors.append(f"{name} grayscale render could not be checked: {error}")
        source = svg_path.read_text()
        for marker in ("<title>", "<desc>", "<text"):
            if marker not in source:
                errors.append(f"{name} SVG lacks {marker} accessibility/content marker")
        if entry.get("monochrome_safe") is not True:
            errors.append(f"{name} is not marked monochrome-safe")
        channels = entry.get("distinguishing_channels")
        if not isinstance(channels, list) or not channels:
            errors.append(f"{name} lacks non-colour distinguishing channels")
        if not any(png_path.name in markdown.read_text() for markdown in (ROOT / "docs/src").rglob("*.md")):
            errors.append(f"{name} has no captioned Markdown use")

    if errors:
        print("figure audit failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"figures: {len(figures)} SVG/PNG pairs pass the rendered grayscale and accessibility audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
