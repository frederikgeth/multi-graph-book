#!/usr/bin/env python3
"""Render the first standards-aware equipment visual-language plate."""

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/src/assets"


def esc(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: float, y: float, value: object, cls: str = "body", anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


STYLE = """
<style>
text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:29px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}
.head{font-size:19px;font-weight:bold}.body{font-size:15px}.small{font-size:13px;fill:#46525d}.tiny{font-size:12px;fill:#46525d}
.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.asset{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.bus{fill:white;stroke:#17212b;stroke-width:2}
.factor{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.aux{fill:#e4f4e7;stroke:#477a55;stroke-width:2}
.ink{stroke:#17212b;stroke-width:2;fill:none}.wire{stroke:#245b7a;stroke-width:4;fill:none}
.bundle{stroke:#245b7a;stroke-width:2;fill:none}.map{stroke:#7856a8;stroke-width:2.5;stroke-dasharray:8 5;fill:none;marker-end:url(#maparrow)}
.control{stroke:#477a55;stroke-width:2.5;stroke-dasharray:3 5;fill:none;marker-end:url(#controlarrow)}
.orientation{stroke:#17212b;stroke-width:2.5;fill:none;marker-end:url(#orientationarrow)}
.warn{fill:#f4e5e5;stroke:#8a3030;stroke-width:2}
</style>
"""


def rect(x, y, w, h, cls="panel", r=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" class="{cls}"/>'


def circle(x, y, r, label, cls="asset"):
    return f'<circle cx="{x}" cy="{y}" r="{r}" class="{cls}"/>' + text(x, y + 5, label, "head", "middle")


def panel(x, y, w, h, title, subtitle):
    return [rect(x, y, w, h), text(x + 22, y + 34, title, "head"), text(x + 22, y + 58, subtitle, "small")]


def render():
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1100" viewBox="0 0 1600 1100">',
        '<title>Standards-aware visual language for power-network equipment</title>',
        '<desc>Line, three-winding transformer, regulator, and switch are shown as single-line assets, multi-line terminal expansions, and typed factor or compiled views. Persistent identities and omitted semantics are explicit.</desc>',
        '<defs><marker id="maparrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#7856a8"/></marker><marker id="controlarrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#477a55"/></marker><marker id="orientationarrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        '<rect width="100%" height="100%" fill="white"/>', STYLE,
        text(36, 42, "One equipment family, several declared views", "title"),
        text(36, 70, "IEC-style symbols are the visual vocabulary; identity fibres and map labels carry the power-system semantics.", "sub"),
    ]

    # Asset single-line row: buses are vertices; equipment is drawn on branches.
    lines += panel(36, 105, 1528, 240, "A. Single-line asset view", "Buses/terminals are vertices; lines, transformers, regulators, and switches are branches or multi-terminal equipment")
    lines += [
        rect(72, 192, 105, 52, "bus", 5), rect(253, 192, 105, 52, "bus", 5),
        text(124, 224, "B_i", "head", "middle"), text(305, 224, "B_j", "head", "middle"),
        '<path d="M177 218 L253 218" class="wire"/>', text(215, 198, "L1", "head", "middle"),
        '<path d="M194 218 L235 218" class="orientation"/>', text(215, 180, "stored orientation", "tiny", "middle"), text(72, 270, "line branch", "small"),
        rect(490, 192, 82, 52, "bus", 5), rect(690, 192, 82, 52, "bus", 5), rect(590, 270, 82, 42, "bus", 5),
        text(531, 224, "B_1", "body", "middle"), text(731, 224, "B_2", "body", "middle"), text(631, 298, "B_3", "body", "middle"),
        '<path d="M572 218 L610 238 M690 218 L650 238 M631 270 L631 244" class="wire"/>',
        '<circle cx="631" cy="238" r="23" class="asset"/><path d="M617 238 Q631 215 645 238 Q631 261 617 238" class="ink"/>',
        text(631, 242, "X1", "body", "middle"), text(631, 335, "three-winding transformer", "small", "middle"),
        rect(900, 192, 82, 52, "bus", 5), rect(1125, 192, 82, 52, "bus", 5),
        text(941, 224, "B_k", "body", "middle"), text(1166, 224, "B_l", "body", "middle"),
        '<path d="M982 218 L1030 218" class="wire"/><path d="M1070 218 L1125 218" class="wire"/>',
        '<circle cx="1048" cy="218" r="19" class="asset"/><circle cx="1063" cy="218" r="19" class="asset"/>',
        '<path d="M1040 178 L1065 164" class="control"/>', text(1055, 150, "R1 tap", "small", "middle"), text(1055, 270, "regulator branch", "small", "middle"),
        rect(1310, 192, 82, 52, "bus", 5), rect(1485, 192, 60, 52, "bus", 5),
        text(1351, 224, "B_m", "body", "middle"), text(1515, 224, "B_n", "body", "middle"),
        '<path d="M1392 218 L1440 218 M1470 218 L1485 218" class="wire"/><path d="M1438 218 L1462 202" class="ink"/>',
        text(1450, 270, "S1 open contact", "small", "middle"),
        text(72, 320, "Persistent IDs: L1, X1, R1, S1. The equipment is not a bus; its terminals attach to buses.", "small"),
    ]

    # Multi-line row.
    lines += panel(36, 375, 1528, 300, "B. Multi-line terminal view", "Conductors, winding connections, poles, neutral, and control ownership become visible")
    # line expansion
    lines += [text(80, 464, "L1", "head"), text(80, 484, "four-wire line", "small")]
    for idx, lab in enumerate(("a", "b", "c", "n")):
        y = 490 + idx * 34
        lines += [text(120, y + 5, lab, "body"), f'<path d="M150 {y} L335 {y}" class="bundle"/>']
    # transformer expansion
    lines += [text(420, 464, "X1", "head"), text(420, 484, "winding ports", "small")]
    for idx, lab in enumerate(("W1  a,b,c,n", "W2  a,b,c,n", "W3  a,b,c")):
        y = 495 + idx * 52
        lines += [rect(500, y - 22, 180, 36, "asset", 8), text(590, y + 2, lab, "body", "middle")]
    lines += [text(720, 464, "R1", "head"), text(720, 484, "tap/control relation", "small")]
    for idx, lab in enumerate(("a", "b", "c")):
        y = 500 + idx * 45
        lines += [text(750, y + 5, lab, "body"), f'<path d="M780 {y} L900 {y}" class="bundle"/>', rect(830, y - 18, 46, 32, "aux", 6), text(853, y + 4, "t", "body", "middle")]
    lines += [text(1000, 464, "S1", "head"), text(1000, 484, "pole-wise contacts", "small")]
    for idx, lab in enumerate(("a", "b", "c", "n")):
        y = 490 + idx * 34
        lines += [text(1035, y + 5, lab, "body"), f'<path d="M1060 {y} L1120 {y}" class="bundle"/>']
        if lab == "n":
            lines += [f'<path d="M1165 {y} L1220 {y}" class="bundle"/>', f'<path d="M1120 {y} L1158 {y - 16}" class="ink"/>']
        else:
            lines += [f'<path d="M1160 {y} L1220 {y}" class="bundle"/>', rect(1120, y - 10, 40, 20, "asset", 4)]
    lines += [
        text(1280, 505, "solid conductors", "small"), text(1280, 535, "explicit neutral/earth", "small"), text(1280, 565, "n pole shown open", "small"),
        text(720, 630, "R1 is phase-only here; its neutral is not a tap port.", "small"),
        text(36, 650, "The multi-line view is still not the complete equation model: internal leakage, excitation, and grounding may remain factor-level objects.", "small"),
    ]

    # Factor/compiled row.
    lines += panel(36, 705, 1528, 305, "C. Factor and compiled views", "Sibling factors are listed side by side; no map is implied")
    # line factor
    lines += [rect(75, 770, 315, 150, "factor"), text(98, 805, "L1 factor", "head"), text(98, 837, "Z_l, Y_l_from, Y_l_to", "body"), text(98, 870, "limits + conductor order", "small"), text(98, 900, "compiled: block edge / MNA rows", "tiny")]
    # transformer factor
    lines += [rect(445, 755, 370, 180, "factor"), text(470, 790, "X1 factor", "head"), text(470, 823, "Tₓ  ·  leakage  ·  excitation", "body"), text(470, 852, "grounding  ·  tap/control", "body"), text(470, 887, "three winding fibres retained", "small"), text(470, 915, "compiled: port incidence or guarded edge target", "tiny")]
    # regulator/switch
    lines += [rect(870, 770, 280, 150, "aux"), text(895, 805, "R1 / S1", "head"), text(895, 838, "T_r(t)  ·  sigma_s", "body"), text(895, 870, "control/state, not extra line", "small"), text(895, 900, "compiled: decision-aware equations", "tiny")]
    # warning
    lines += [rect(1205, 770, 315, 150, "warn"), text(1230, 805, "Do not infer", "head"), text(1230, 838, "factor edge = physical asset", "body"), text(1230, 870, "single-line = scalar model", "body"), text(1230, 902, "arrow = power-flow direction", "body")]
    lines += [
        text(36, 975, "Legend", "head"), '<path d="M120 970 L210 970" class="wire"/>', text(225, 975, "declared electrical attachment", "small"), '<path d="M470 970 L560 970" class="map"/>', text(575, 975, "view/lowering map", "small"), '<path d="M790 970 L880 970" class="control"/>', text(895, 975, "state/control relation", "small"),
        text(36, 1040, "A caption must identify object level, identity fibre, omitted semantics, map type, and reverse-map status.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    svg = OUT / "visual-language-equipment-plate.svg"
    png = OUT / "visual-language-equipment-plate.png"
    svg.write_text(render())
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise SystemExit("rsvg-convert is required to create the PNG companion")
    subprocess.run([converter, "-o", str(png), str(svg)], check=True)
    print(f"wrote {svg}")
    print(f"wrote {png}")


if __name__ == "__main__":
    main()
