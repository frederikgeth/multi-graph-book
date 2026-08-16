#!/usr/bin/env python3
"""Render the special-semantics companion to the equipment visual-language plate."""

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
.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.asset{fill:#d9eef8;stroke:#245b7a;stroke-width:2}
.factor{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.aux{fill:#e4f4e7;stroke:#477a55;stroke-width:2}
.wire{stroke:#245b7a;stroke-width:3;fill:none}.bundle{stroke:#245b7a;stroke-width:2;fill:none}
.factorline{stroke:#8a4f13;stroke-width:2.5;stroke-dasharray:7 5;fill:none}
.control{stroke:#477a55;stroke-width:2.5;stroke-dasharray:3 5;fill:none;marker-end:url(#controlarrow)}
.warn{fill:#f4e5e5;stroke:#8a3030;stroke-width:2}.earth{stroke:#17212b;stroke-width:2;fill:none}
</style>
"""


def rect(x, y, w, h, cls="panel", r=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" class="{cls}"/>'


def panel(x, y, w, h, title, subtitle):
    return [rect(x, y, w, h), text(x + 22, y + 34, title, "head"), text(x + 22, y + 58, subtitle, "small")]


def ground(x, y):
    return [
        f'<path d="M{x} {y} L{x} {y + 18}" class="earth"/>',
        f'<path d="M{x - 18} {y + 18} L{x + 18} {y + 18}" class="earth"/>',
        f'<path d="M{x - 12} {y + 24} L{x + 12} {y + 24}" class="earth"/>',
        f'<path d="M{x - 6} {y + 30} L{x + 6} {y + 30}" class="earth"/>',
    ]


def render():
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1200" viewBox="0 0 1600 1200">',
        '<title>Special semantics in power-network visual language</title>',
        '<desc>Neutral grounding, nominal-pi shunts, phase-selective switching, and an n-winding leakage-factor graph are shown with explicit identity and edge provenance warnings.</desc>',
        '<defs><marker id="controlarrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#477a55"/></marker></defs>',
        '<rect width="100%" height="100%" fill="white"/>', STYLE,
        text(36, 42, "Special semantics that a compressed diagram can hide", "title"),
        text(36, 70, "Keep grounding, shunts, per-pole states, and factor provenance explicit before lowering.", "sub"),
    ]

    # A: neutral grounding
    lines += panel(36, 95, 748, 470, "A. Neutral grounding is an explicit factor", "A ground symbol is not merely a datum: it may carry impedance, current, ownership, and a limit")
    lines += [text(70, 190, "single-line badge", "head"), text(70, 220, "L1  4-wire", "body"), '<path d="M190 215 L340 215" class="wire"/>', rect(340, 190, 92, 50, "asset", 8), text(386, 222, "GND?", "body", "middle")]
    lines += [text(70, 300, "multi-line expansion", "head")]
    for idx, lab in enumerate(("a", "b", "c", "n")):
        y = 345 + idx * 34
        lines += [text(90, y + 5, lab, "body"), f'<path d="M120 {y} L310 {y}" class="bundle"/>']
    lines += [f'<path d="M310 447 L390 447" class="wire"/>', rect(390, 420, 110, 54, "factor", 8), text(445, 453, "Z_g", "body", "middle")]
    lines += ground(540, 447)
    lines += [text(585, 442, "I_n <= I_n_max", "body"), text(585, 470, "neutral limit retained", "small"), rect(70, 505, 650, 38, "warn", 7), text(88, 530, "If neutral is eliminated, keep its recovery map and feasible current limit.", "small")]

    # B: nominal-pi shunts
    lines += panel(816, 95, 748, 470, "B. Nominal-pi shunts remain terminal semantics", "Do not silently absorb endpoint shunts into a line or transformer when direction and ownership matter")
    lines += [text(850, 190, "bus i", "head"), text(1490, 190, "bus j", "head")]
    lines += ['<path d="M900 225 L1060 225" class="wire"/>', rect(1060, 195, 150, 60, "factor", 8), text(1135, 232, "Z_l", "head", "middle"), '<path d="M1210 225 L1470 225" class="wire"/>']
    lines += [f'<path d="M990 225 L990 330" class="wire"/>', rect(930, 330, 120, 52, "factor", 8), text(990, 362, "Y_from", "body", "middle")]
    lines += [f'<path d="M1310 225 L1310 330" class="wire"/>', rect(1250, 330, 120, 52, "factor", 8), text(1310, 362, "Y_to", "body", "middle")]
    lines += ground(990, 382) + ground(1310, 382)
    lines += [text(850, 455, "terminal current", "small"), text(985, 455, "I_i = I_series + Y_from V_i", "body"), text(850, 485, "terminal power", "small"), text(985, 485, "S_i includes shunt absorption", "body"), rect(850, 505, 670, 38, "warn", 7), text(868, 530, "A line-only edge cannot represent these shunts without a declared target and loss ledger.", "small")]

    # C: phase-selective switching
    lines += panel(36, 595, 748, 520, "C. Phase-selective switching has a vector state", "A single switch identity can own several pole states; a radial orientation is not a substitute for this record")
    lines += [text(70, 690, "S1", "head"), text(125, 690, "pole", "small"), text(235, 690, "state", "small"), text(390, 690, "electrical consequence", "small")]
    states = [("a", "closed", "phase a connected"), ("b", "open", "phase b islanded"), ("c", "closed", "phase c connected"), ("n", "open", "neutral path open")]
    for idx, (lab, state, consequence) in enumerate(states):
        y = 735 + idx * 54
        lines += [text(125, y + 5, lab, "body"), rect(215, y - 22, 120, 34, "asset" if state == "closed" else "warn", 7), text(275, y + 1, state, "body", "middle"), text(390, y + 5, consequence, "body")]
        lines += [f'<path d="M90 {y} L110 {y}" class="wire"/>', f'<path d="M140 {y} L205 {y}" class="bundle"/>']
    lines += [text(70, 985, "state scope", "head"), text(205, 985, "sigma_S = (sigma_a, sigma_b, sigma_c, sigma_n)", "body"), text(70, 1020, "map type", "head"), text(205, 1020, "state-conditioned quotient / surgery", "body"), rect(70, 1045, 650, 42, "warn", 7), text(88, 1072, "Never collapse pole states to one scalar open/closed flag without a guard.", "small")]

    # D: n-winding factor graph
    lines += panel(816, 595, 748, 520, "D. N-winding leakage graphs are factor decompositions", "Pairwise leakage edges are computational factors with provenance, not independent physical assets")
    lines += [text(850, 690, "one transformer asset", "head"), rect(850, 710, 270, 260, "asset", 14), text(985, 745, "X1", "head", "middle"), text(985, 770, "n winding ports", "small", "middle")]
    nodes = {"W1": (915, 835), "W2": (1050, 835), "W3": (915, 915), "W4": (1050, 915)}
    pairs = [("W1", "W2", "lambda_12"), ("W1", "W3", "lambda_13"), ("W1", "W4", "lambda_14"), ("W2", "W3", "lambda_23"), ("W2", "W4", "lambda_24"), ("W3", "W4", "lambda_34")]
    for left, right, label in pairs:
        x1, y1 = nodes[left]
        x2, y2 = nodes[right]
        lines += [f'<path d="M{x1} {y1} L{x2} {y2}" class="factorline"/>', text((x1 + x2) / 2 + 5, (y1 + y2) / 2 - 4, label, "tiny", "middle")]
    for label, (x, y) in nodes.items():
        lines += [f'<circle cx="{x}" cy="{y}" r="24" class="factor"/>', text(x, y + 5, label, "body", "middle")]
    lines += [text(1170, 700, "edge provenance", "head"), text(1170, 735, "lambda_ij = leakage factor", "body"), text(1170, 770, "not a conductor", "body"), text(1170, 805, "not an outage/ownership asset", "body"), rect(1160, 850, 350, 120, "warn", 9), text(1180, 885, "Do not infer", "head"), text(1180, 918, "factor graph = physical graph", "body"), text(1180, 947, "or cycle = physical loop", "body")]
    lines += [text(850, 1030, "Compilation target", "head"), text(1025, 1030, "port-factor incidence, MNA, or guarded edge realization", "small"), text(850, 1065, "reverse map", "head"), text(1025, 1065, "retain X1 and lambda_ij provenance", "small")]
    lines += [text(36, 1160, "Every caption must state state scope, edge provenance, omitted semantics, and whether reverse recovery is available.", "small"), '</svg>']
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    svg = OUT / "visual-language-special-semantics.svg"
    png = OUT / "visual-language-special-semantics.png"
    svg.write_text(render())
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise SystemExit("rsvg-convert is required to create the PNG companion")
    subprocess.run([converter, "-o", str(png), str(svg)], check=True)
    print(f"wrote {svg}")
    print(f"wrote {png}")


if __name__ == "__main__":
    main()
