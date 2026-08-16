#!/usr/bin/env python3
"""Render the semantic-label to storage-coordinate bridge."""

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/src/assets"


def esc(value):
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, value, cls="body", anchor="start"):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


def render():
    style = """
<style>
text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:27px;font-weight:bold}
.sub{font-size:16px;fill:#5f6b76}.head{font-size:19px;font-weight:bold}.body{font-size:15px}
.small{font-size:13px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}
.label{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.coord{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}
.matrix{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.arrow{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}
.grid{stroke:#17212b;stroke-width:1.5}.dash{stroke:#8a3232;stroke-width:2;stroke-dasharray:8 6;fill:none}
</style>
"""
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="650" viewBox="0 0 1300 650">',
        '<title>Semantic labels are enumerated into storage coordinates</title>',
        '<desc>A labelled bus and line relation is mapped through explicit enumeration functions to an ordinary integer-indexed matrix. Reordering storage positions does not change the semantic network.</desc>',
        '<rect width="100%" height="100%" fill="white"/>', style,
        '<defs><marker id="arrow" markerWidth="11" markerHeight="11" refX="9" refY="4" orient="auto"><path d="M0,0 L9,4 L0,8 z" fill="#17212b"/></marker></defs>',
        text(34, 40, "Labels first, coordinates second", "title"),
        text(34, 68, "The same relation can be named semantically and stored as an ordinary numeric array.", "sub"),
        '<rect x="34" y="105" width="365" height="390" rx="14" class="panel"/>',
        '<rect x="468" y="105" width="365" height="390" rx="14" class="panel"/>',
        '<rect x="902" y="105" width="365" height="390" rx="14" class="panel"/>',
        text(58, 140, "1. Semantic index sets", "head"),
        text(492, 140, "2. Explicit enumeration", "head"),
        text(926, 140, "3. Stored matrix", "head"),
        text(58, 176, "B = {source, load, neutral}", "body"),
        text(58, 209, "L = {ℓmain, ℓtap}", "body"),
        '<circle cx="118" cy="300" r="35" class="label"/><circle cx="300" cy="300" r="35" class="label"/><circle cx="210" cy="405" r="35" class="label"/>',
        text(118, 306, "source", "small", "middle"), text(300, 306, "load", "small", "middle"), text(210, 411, "neutral", "small", "middle"),
        '<path d="M153 300 L265 300" class="arrow"/>', text(209, 282, "ℓmain", "small", "middle"), text(209, 330, "stored orientation only", "tiny", "middle"),
        '<path d="M143 325 L185 380" class="arrow"/>', text(158, 370, "ℓtap", "small", "middle"),
        text(58, 455, "Yᴺij is a labelled block map", "body"),
        text(58, 485, "i,j ∈ B; it is not yet an array position", "small"),
        text(492, 176, "κB(source)=1", "body"), text(492, 206, "κB(load)=2", "body"), text(492, 236, "κB(neutral)=3", "body"),
        '<path d="M650 270 L650 370" class="arrow"/>',
        text(650, 310, "κB", "head", "middle"),
        '<rect x="535" y="390" width="230" height="65" rx="9" class="coord"/>',
        text(650, 418, "row/column positions", "body", "middle"), text(650, 442, "1, 2, 3", "small", "middle"),
        text(926, 176, "[Yᴺ]κ(i),κ(j)", "head"),
        '<rect x="1000" y="205" width="170" height="170" class="matrix"/>',
        '<path d="M1056 205 V375 M1113 205 V375 M1000 262 H1170 M1000 319 H1170" class="grid"/>',
        text(1028, 240, "Yss", "small", "middle"), text(1085, 240, "Ysl", "small", "middle"), text(1142, 240, "Ysn", "small", "middle"),
        text(1028, 297, "Yls", "small", "middle"), text(1085, 297, "Yll", "small", "middle"), text(1142, 297, "Yln", "small", "middle"),
        text(1028, 354, "Yns", "small", "middle"), text(1085, 354, "Ynl", "small", "middle"), text(1142, 354, "Ynn", "small", "middle"),
        text(926, 420, "Reordering the array changes positions", "body"), text(926, 450, "but not buses, lines, or equations.", "small"),
        '<rect x="34" y="530" width="1233" height="70" rx="12" class="coord"/>',
        text(58, 560, "Do not infer semantics from storage", "head"),
        text(390, 560, "The integer matrix is a coordinate realization. The labelled relation, terminal maps, and factor fibres carry the meaning.", "body"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    svg = OUT / "label-coordinate-bridge.svg"
    png = OUT / "label-coordinate-bridge.png"
    svg.write_text(render())
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise SystemExit("rsvg-convert is required to create the PNG companion")
    subprocess.run([converter, "-o", str(png), str(svg)], check=True)
    print(f"wrote {svg}")
    print(f"wrote {png}")


if __name__ == "__main__":
    main()
