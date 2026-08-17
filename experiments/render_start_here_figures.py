#!/usr/bin/env python3
"""Render the first visual hooks for the Start-here section.

The figures are deliberately small, declarative SVGs.  They use the same
source identities and numerical values as the running-network and parallel-
branch witnesses, while making the reader-facing three-beat structure
explicit: belief, failure, resolution.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/src/assets"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, value, cls="body", anchor="start"):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


def rect(x, y, w, h, cls="panel", rx=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>'


def line(x1, y1, x2, y2, cls="wire", width=None):
    extra = f' stroke-width="{width}"' if width else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"{extra}/>'


def circle(x, y, r, label, cls="bus"):
    return (
        f'<circle cx="{x}" cy="{y}" r="{r}" class="{cls}"/>'
        + t(x, y + 6, label, "head", "middle")
    )


STYLE = """
<style>
text{font-family:Arial,sans-serif;fill:#17212b}
.title{font-size:28px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}
.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:19px;font-weight:bold}
.body{font-size:15px}.small{font-size:14px;fill:#5f6b76}.tiny{font-size:13px;fill:#5f6b76}
.bus{fill:#d9eef8;stroke:#245b7a;stroke-width:3}.bus2{fill:#e4f4e7;stroke:#477a55;stroke-width:3}
.wire{stroke:#3d78b5;stroke-width:5}.wire2{stroke:#7856a8;stroke-width:4}
.ground{stroke:#477a55;stroke-width:4}.accent{stroke:#8a4f13;stroke-width:4}
.dashed{stroke:#8a3232;stroke-width:3;stroke-dasharray:9 7}.card{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}
.bad{fill:#f4e5e5;stroke:#8a3232;stroke-width:2}.good{fill:#e4f4e7;stroke:#477a55;stroke-width:2}
.matrix{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.matrix2{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}
</style>
"""


def shell(title, subtitle, width=1200, height=720):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<title>{esc(title)}</title>',
        f'<desc>{esc(subtitle)}</desc>',
        '<rect width="100%" height="100%" fill="white"/>',
        STYLE,
        t(35, 40, title, "title"),
        t(35, 68, subtitle, "sub"),
    ]


def finish(lines):
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def running_network():
    lines = shell(
        "The running network: one layout to reuse",
        "Stable source identities stay visible while later figures change the question or the view.",
        1400,
        760,
    )
    lines += [rect(35, 100, 1330, 500), t(65, 140, "reference physical layout", "head")]
    p = {"i0": (150, 330), "i1": (370, 330), "i2": (610, 330), "i3": (850, 330), "i4": (1080, 330), "i5": (700, 505), "i6": (930, 505)}
    lines += [line(*p["i0"], *p["i1"], "wire2"), line(p["i1"][0], 315, p["i2"][0], 315, "wire"), line(p["i1"][0], 345, p["i2"][0], 345, "wire"), line(*p["i2"], *p["i3"], "wire"), line(*p["i3"], *p["i4"], "wire")]
    for target in ("i1", "i5", "i6"):
        lines.append(line(750, 435, *p[target], "accent"))
    for ident, point in p.items():
        lines.append(circle(*point, 32, ident))
    for x, y, label, cls in [(260, 315, "w0", "card"), (490, 295, "l1", "matrix"), (490, 365, "l2", "matrix"), (730, 300, "l3", "matrix"), (965, 300, "l4", "matrix2"), (750, 435, "x1", "card"), (700, 575, "d3", "good"), (930, 575, "g1", "good")]:
        lines.append(rect(x - 28, y - 18, 56, 36, cls, 8))
        lines.append(t(x, y + 5, label, "tiny", "middle"))
    lines += [t(110, 665, "parallel members ℓ₁, ℓ₂", "body"), t(410, 665, "coupled line ℓ₃", "body"), t(735, 665, "three-winding factor x₁", "body"), t(1080, 665, "phase-mapped lateral ℓ₄", "body", "end"), t(65, 715, "This is the reference layout.  A graph view may forget, compile, or expand these objects, but it must say which.", "small")]
    return finish(lines)


def radial_triangles():
    lines = shell(
        "Your radial feeder has triangles in it",
        "The answer is not a contradiction: the bus graph and the conductor-expanded support graph answer different questions.",
        1400,
        800,
    )
    lines += [rect(35, 105, 500, 540), rect(575, 105, 790, 540), t(65, 145, "belief: radial bus topology", "head"), t(605, 145, "failure: conductor-expanded support", "head")]
    p = {"i": (140, 365), "j": (285, 270), "k": (430, 365)}
    lines += [line(*p["i"], *p["j"], "wire2"), line(*p["j"], *p["k"], "wire2")]
    for ident, point in p.items(): lines.append(circle(*point, 30, ident))
    lines += [t(285, 490, "tree: μ = 0", "body", "middle"), t(285, 520, "no physical loop at bus level", "small", "middle")]
    q = {"ia": (700, 320), "ib": (700, 440), "ja": (930, 250), "jb": (930, 370), "ka": (1160, 320), "kb": (1160, 440)}
    for a, b in [("ia", "ja"), ("ia", "jb"), ("ib", "ja"), ("ib", "jb"), ("ja", "ka"), ("ja", "kb"), ("jb", "ka"), ("jb", "kb")]: lines.append(line(*q[a], *q[b], "wire2", 3))
    for ident, point in q.items(): lines.append(circle(*point, 22, ident, "bus2"))
    lines += [t(930, 505, "dense mutual coupling induces cliques", "body", "middle"), t(930, 535, "cycle rank of the support graph is positive", "small", "middle"), rect(35, 680, 1330, 70, "card"), t(55, 708, "resolution", "head"), t(180, 708, "which graph?  Bus-level radiality is a tree; conductor-expanded matrix support is a chordal graph with clique structure.", "body")]
    return finish(lines)


def same_ybus():
    lines = shell(
        "Same Y-bus. Different answer.",
        "A nodal admittance equality can preserve the linear terminal map while saying nothing about member limits or controls.",
        1400,
        820,
    )
    lines += [rect(35, 105, 610, 240), rect(755, 105, 610, 240), t(65, 145, "network A", "head"), t(785, 145, "network B", "head")]
    for offset, labels in [(35, ("ℓ₁", "ℓ₂")), (755, ("ℓ₁", "ℓ₂"))]:
        lines += [circle(130 + offset, 245, 28, "i"), circle(540 + offset, 245, 28, "j"), line(160 + offset, 230, 510 + offset, 230, "wire"), line(160 + offset, 260, 510 + offset, 260, "wire")]
        lines += [t(335 + offset, 220, labels[0], "small", "middle"), t(335 + offset, 285, labels[1], "small", "middle")]
    lines += [rect(470, 375, 460, 70, "good"), t(700, 404, "‖Y_A − Y_B‖∞ = 0", "head", "middle"), t(700, 430, "same unconstrained terminal current relation", "small", "middle")]
    lines += [rect(35, 480, 610, 190, "panel"), rect(755, 480, 610, 190, "panel"), t(65, 520, "decision model A", "head"), t(785, 520, "decision model B", "head")]
    lines += [t(65, 570, "member limits retained", "body"), t(65, 610, "maximum served power", "small"), t(350, 615, "110 MW", "head", "middle"), t(785, 570, "summed limit used", "body"), t(785, 610, "maximum served power", "small"), t(1070, 615, "200 MW", "head", "middle")]
    lines += [rect(35, 705, 1330, 70, "bad"), t(55, 733, "resolution", "head"), t(180, 733, "Y-bus is assembled from linear factors; limits, states, and controls live in the decision model. Your model dispatches 200 MW. Your conductor melts at 110.", "body")]
    return finish(lines)


def neutral_recovery():
    lines = shell(
        "The neutral you eliminated is still carrying current",
        "Boundary voltages can be exact after Kron reduction while a recovered neutral constraint remains decisive.",
        1400,
        800,
    )
    lines += [rect(35, 105, 600, 500), rect(765, 105, 600, 500), t(65, 145, "reduced boundary model", "head"), t(795, 145, "recovery obligation", "head")]
    p = {"i": (150, 330), "j": (500, 330), "n": (325, 470)}
    lines += [line(*p["i"], *p["j"], "wire2"), line(*p["i"], *p["n"], "dashed"), line(*p["n"], *p["j"], "dashed")]
    lines += [circle(*p["i"], 30, "i"), circle(*p["j"], 30, "j"), circle(*p["n"], 28, "n", "bad"), t(325, 535, "eliminated", "small", "middle"), t(325, 565, "from the boundary equation", "small", "middle"), t(325, 220, "phase voltages match to 10⁻¹⁵", "body", "middle")]
    lines += [t(795, 220, "recover the hidden branch current", "body"), t(795, 275, "|Iₙ| = 43.0 A", "head"), t(795, 325, "declared limit = 42.6 A", "body"), rect(795, 365, 500, 75, "bad"), t(1045, 397, "constraint violated", "head", "middle"), t(1045, 425, "if the recovery constraint is dropped, the target admits it", "tiny", "middle"), rect(795, 475, 500, 75, "good"), t(1045, 507, "resolution: preserve the recovery map", "head", "middle"), t(1045, 535, "and evaluate the neutral limit in the reduced feasible set", "tiny", "middle")]
    lines += [rect(35, 650, 1330, 70, "card"), t(55, 678, "which observation?", "head"), t(245, 678, "The reduced phase relation is exact; the decision problem is not, unless the eliminated neutral current and its rating are recovered.", "body")]
    return finish(lines)


def negative_star_arm(witness):
    arms = witness["star_arm_impedances_ohm"]
    eigenvalues = ", ".join(f"{value:.1f}" for value in witness["reactance_eigenvalues"])
    lines = shell(
        "This passive transformer contains a negative reactance",
        "The negative number belongs to a star coordinate; the positive-semidefinite matrix is the physical guard.",
        1400,
        800,
    )
    lines += [rect(35, 105, 600, 500), rect(765, 105, 600, 500), t(65, 145, "belief: every arm must be positive", "head"), t(795, 145, "failure: one compiled arm is negative", "head")]
    # Pairwise tests: all positive.
    for x, pair, value in [(150, "12", "1.0 Ω"), (320, "13", "1.0 Ω"), (490, "23", "3.0 Ω")]:
        lines += [circle(x, 300, 34, pair, "bus2"), t(x, 365, f"x{pair} = {value}", "body", "middle")]
    lines += [t(335, 445, "all source short-circuit tests are positive", "body", "middle"), t(335, 475, "and physically admissible", "small", "middle")]
    # Star arms.
    for x, arm, value, cls in [(860, "z₁", f"{arms['1']['imag']:.1f} j Ω", "bad"), (1055, "z₂", f"{arms['2']['imag']:.1f} j Ω", "good"), (1250, "z₃", f"{arms['3']['imag']:.1f} j Ω", "good")]:
        lines += [rect(x - 70, 245, 140, 100, cls), t(x, 285, arm, "head", "middle"), t(x, 320, value, "body", "middle")]
    lines += [t(1065, 405, "the first arm looks non-physical", "body", "middle"), rect(820, 450, 480, 85, "good"), t(1060, 483, f"guard passes: eigenvalues(Im Zᴮ) = [{eigenvalues}]", "body", "middle"), t(1060, 512, "positive semidefinite, so the compiled relation is admissible", "tiny", "middle")]
    lines += [rect(35, 650, 1330, 70, "card"), t(55, 678, "resolution", "head"), t(180, 678, "which coordinates?  A negative star arm can be a coordinate artifact; the matrix invariant—not componentwise arm positivity—determines admissibility.", "body")]
    return finish(lines)


def formulation_lattice():
    lines = shell(
        "Lowering is a guarded lattice, not a single arrow",
        "The equation/constraint operator is the faithful boundary; nodal admittance is one optional reduction.",
        1400,
        800,
    )
    # The horizontal spine is the faithful compilation path.
    columns = [(45, "source model", "identified ports, states,\nlimits, decisions"),
               (375, "port / factor", "typed terminal\nrelations"),
               (705, "equation operator", "F(z)=0, g(z)≤0,\nobservations, provenance"),
               (1035, "study target", "MNA / tableau\nor guarded Y")]
    for x, title, detail in columns:
        lines += [rect(x, 235, 290, 150, "panel"), t(x + 145, 275, title, "head", "middle")]
        for idx, row in enumerate(detail.split("\n")):
            lines.append(t(x + 145, 320 + idx * 25, row, "body", "middle"))
    for x1, x2 in [(335, 375), (665, 705), (995, 1035)]:
        lines += [line(x1, 310, x2, 310, "accent", 5), t((x1 + x2) / 2, 295, "compile", "tiny", "middle")]
    # Explicitly separate the two guarded target branches.
    lines += [line(850, 385, 850, 535, "wire2", 4), line(850, 535, 1160, 535, "wire2", 4), line(1160, 535, 1160, 385, "wire2", 4)]
    lines += [rect(885, 555, 250, 110, "good"), t(1010, 592, "MNA / tableau", "head", "middle"), t(1010, 625, "preserves extra variables", "small", "middle"), t(1010, 648, "and member constraints", "small", "middle")]
    lines += [rect(1165, 555, 190, 110, "bad"), t(1260, 592, "Yᴺ", "head", "middle"), t(1260, 625, "only if guards", "small", "middle"), t(1260, 648, "and query allow it", "small", "middle")]
    lines += [line(850, 385, 1260, 555, "dashed", 3), t(1080, 465, "optional Lᵧ", "tiny", "middle")]
    lines += [rect(45, 105, 1310, 80, "card"), t(70, 137, "belief", "head"), t(170, 137, "every linear network ends as a Y-bus", "body"), t(70, 165, "resolution", "head"), t(190, 165, "the faithful target carries equations, constraints, observations, and provenance; Yᴺ is a guarded view", "body")]
    lines += [rect(45, 700, 1310, 55, "bad"), t(70, 734, "blocked shortcut", "head"), t(230, 734, "ideal voltage source, switching decision, or member limit → do not silently erase the extra variable", "body")]
    return finish(lines)


def main():
    certificate = json.loads((ROOT / "experiments/generated/multiwinding-leakage-compilation-certificate.json").read_text())
    outputs = {
        "start-here-running-network.svg": running_network(),
        "start-here-radial-triangles.svg": radial_triangles(),
        "start-here-same-ybus.svg": same_ybus(),
        "start-here-neutral-recovery.svg": neutral_recovery(),
        "start-here-negative-star-arm.svg": negative_star_arm(certificate["evidence"]["negative_star_arm_witness"]),
        "formulation-lowering-lattice.svg": formulation_lattice(),
    }
    for name, content in outputs.items():
        (OUT / name).write_text(content)
        print(f"wrote {OUT / name}")


if __name__ == "__main__":
    main()
