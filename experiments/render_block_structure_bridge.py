#!/usr/bin/env python3
"""Render the four views of one four-wire linear factor.

The SVG is intentionally declarative: labels and panel boundaries carry the
meaning, while colour is only a secondary cue.  A PNG companion is produced
with rsvg-convert for PDF-safe inclusion.
"""

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/src/assets"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, value, cls="body", anchor="start"):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


STYLE = """
<style>
text{font-family:Arial,sans-serif;fill:#17212b}
.title{font-size:28px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}
.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:19px;font-weight:bold}
.body{font-size:15px}.small{font-size:13px;fill:#5f6b76}.tiny{font-size:12px;fill:#5f6b76}
.bus{fill:#d9eef8;stroke:#245b7a;stroke-width:3}.port{fill:#fff;stroke:#245b7a;stroke-width:2}
.factor{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.wire{stroke:#245b7a;stroke-width:4;fill:none}
.wire2{stroke:#7856a8;stroke-width:2;fill:none}.grid{stroke:#17212b;stroke-width:1.5}
.block{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.block2{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}
.support{stroke:#477a55;stroke-width:2;fill:none}.dashed{stroke:#17212b;stroke-width:2;stroke-dasharray:7 5;fill:none}
</style>
"""


def circle(x, y, r, label, cls="bus"):
    return f'<circle cx="{x}" cy="{y}" r="{r}" class="{cls}"/>' + t(x, y + 5, label, "head", "middle")


def panel(x, y, w, h, title, subtitle):
    return [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" class="panel"/>',
            t(x + 22, y + 34, title, "head"), t(x + 22, y + 58, subtitle, "small")]


def render():
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="930" viewBox="0 0 1400 930">',
        '<title>One four-wire factor across four graph and equation views</title>',
        '<desc>A two-bus four-wire factor is shown as a vector edge, a port-factor incidence object, a block nodal operator, and a scalar or realified support pattern. These are views of one declared factor, not interchangeable graph semantics.</desc>',
        '<rect width="100%" height="100%" fill="white"/>', STYLE,
        t(36, 42, "One four-wire factor, four useful views", "title"),
        t(36, 70, "Lowering changes coordinates and visible structure; it must not silently invent assets or erase factor identity.", "sub"),
    ]
    # A: high-level vector edge.
    lines += panel(36, 105, 650, 350, "A. High-level vector edge", "A two-terminal engineering object with ordered conductor coordinates")
    lines += [circle(150, 285, 48, "i"), circle(570, 285, 48, "j"),
              '<path d="M198 285 L522 285" class="wire"/>',
              t(360, 265, "ℓᵢⱼ", "head", "middle"),
              t(360, 310, "Vᵢ − Vⱼ ∈ ℂ⁴", "body", "middle"),
              t(150, 370, "(a,b,c,n)", "small", "middle"), t(570, 370, "(a,b,c,n)", "small", "middle"),
              t(360, 418, "Zℓ, Iℓ, limits, and identity travel with the edge", "small", "middle")]
    # B: port-factor incidence.
    lines += panel(714, 105, 650, 350, "B. Port–factor incidence", "The canonical electrical view keeps ports, factor identity, and terminal maps explicit")
    lines += [circle(800, 285, 40, "i"), circle(1278, 285, 40, "j"),
              '<rect x="976" y="210" width="126" height="150" rx="10" class="factor"/>',
              t(1039, 255, "φℓ", "head", "middle"), t(1039, 285, "factor", "body", "middle"), t(1039, 315, "4-port", "small", "middle")]
    for idx, lab in enumerate(("a", "b", "c", "n")):
        y = 225 + idx * 40
        lines += [f'<circle cx="875" cy="{y}" r="7" class="port"/>', f'<circle cx="1203" cy="{y}" r="7" class="port"/>',
                  f'<path d="M840 285 L875 {y} L976 {y}" class="wire2"/>', f'<path d="M1102 {y} L1203 {y} L1240 285" class="wire2"/>',
                  t(875, y - 12, lab, "tiny", "middle"), t(1203, y - 12, lab, "tiny", "middle")]
    lines += [t(1039, 418, "source fibre: {ℓ}  ·  terminal maps: Tᵢ, Tⱼ", "small", "middle")]
    # C: block nodal operator.
    lines += panel(36, 485, 650, 350, "C. Block nodal operator", "Assembly exposes a 2×2 matrix of 4×4 conductor blocks")
    x0, y0, cw, ch = 225, 580, 170, 75
    for r in range(2):
        for c in range(2):
            cls = "block" if r == c else "block2"
            lines.append(f'<rect x="{x0+c*cw}" y="{y0+r*ch}" width="{cw}" height="{ch}" class="{cls}"/>')
            label = [["Yᵢᵢ", "Yᵢⱼ"], ["Yⱼᵢ", "Yⱼⱼ"]][r][c]
            lines += [t(x0 + c*cw + cw/2, y0 + r*ch + 43, label, "head", "middle"), t(x0 + c*cw + cw/2, y0 + r*ch + 70, "ℂ⁴ˣ⁴", "small", "middle")]
    lines += [t(180, 620, "i", "head", "middle"), t(180, 695, "j", "head", "middle"),
              t(310, 560, "i", "head", "middle"), t(480, 560, "j", "head", "middle"),
              t(310, 750, "Y = [ Yᵢᵢ  Yᵢⱼ ; Yⱼᵢ  Yⱼⱼ ]", "body", "middle"),
              t(360, 798, "block support is simple; stamp identity remains separate provenance", "small", "middle")]
    # D: scalar support and realification.
    lines += panel(714, 485, 650, 350, "D. Scalar support and realification", "Expanding coordinates can reveal dense support without creating new physical members")
    nodes = [(800, 610, "ia"), (800, 700, "ib"), (890, 610, "ja"), (890, 700, "jb")]
    # four representative coordinates, with dense cross-coupling and a legend.
    for a in nodes[:2]:
        for b in nodes[2:]:
            lines.append(f'<path d="M{a[0]+18} {a[1]} L{b[0]-18} {b[1]}" class="support"/>')
    for x, y, lab in nodes:
        lines.append(circle(x, y, 18, lab, "bus"))
    lines += [t(1035, 630, "complex support", "head", "middle"), t(1035, 657, "dense block → scalar clique", "small", "middle"),
              '<path d="M960 700 L1100 700" class="dashed"/>',
              t(1035, 715, "realification", "head", "middle"), t(1035, 743, "R(Y) = [ G  −B ; B  G ]", "body", "middle"),
              t(1035, 773, "twice the coordinates, same declared assets", "small", "middle"),
              t(760, 818, "support answers an algebraic question; factor fibres answer an identity question", "small")]
    lines += [f'<rect x="36" y="865" width="1328" height="42" rx="10" class="factor"/>',
              t(55, 892, "Reading rule", "head"), t(190, 892, "Use A/B for assets and ports, C for matrix equations, and D for coordinate support or realified numerics. Never infer a physical cycle or new asset from D alone.", "body")]
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    svg = OUT / "block-structure-bridge.svg"
    png = OUT / "block-structure-bridge.png"
    svg.write_text(render())
    converter = shutil.which("rsvg-convert")
    if converter:
        subprocess.run([converter, "-o", str(png), str(svg)], check=True)
    else:
        raise SystemExit("rsvg-convert is required to create the PNG companion")
    print(f"wrote {svg}")
    print(f"wrote {png}")


if __name__ == "__main__":
    main()
