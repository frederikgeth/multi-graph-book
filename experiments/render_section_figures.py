#!/usr/bin/env python3
"""Render the structural figures for the formal-framework section.

The coordinate plate is derived from the checked four-wire impedance fixture;
the other two figures are declarative visual grammars, not numerical claims.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/src/assets"


def esc(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, value, cls="body", anchor="start"):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


def rect(x, y, w, h, cls="panel", rx=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>'


def line(x1, y1, x2, y2, cls="wire", width=None):
    extra = f' stroke-width="{width}"' if width else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"{extra}/>'


STYLE = """
<style>
text{font-family:Arial,sans-serif;fill:#17212b}
.title{font-size:28px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}
.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:19px;font-weight:bold}
.body{font-size:15px}.small{font-size:13px;fill:#5f6b76}.tiny{font-size:12px;fill:#5f6b76}
.bus{fill:#d9eef8;stroke:#245b7a;stroke-width:3}.factor{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}
.asset{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.port{fill:white;stroke:#8a4f13;stroke-width:2}
.jmap{stroke:#245b7a;stroke-width:3;marker-end:url(#arrowBlue)}.fmap{stroke:#8a4f13;stroke-width:3;marker-end:url(#arrowOrange)}
.lambda{stroke:#477a55;stroke-width:2.5;stroke-dasharray:8 6;marker-end:url(#arrowGreen)}
.wire{stroke:#3d78b5;stroke-width:4}.dashed{stroke:#8a3232;stroke-width:3;stroke-dasharray:8 6}
.matrix{fill:#eee8f8;stroke:#7856a8;stroke-width:2}.good{fill:#e4f4e7;stroke:#477a55;stroke-width:2}
.warn{fill:#f4e5e5;stroke:#8a3232;stroke-width:2}.card{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}
</style>
"""


def shell(title, subtitle, width=1400, height=800):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<title>{esc(title)}</title>', f'<desc>{esc(subtitle)}</desc>',
        '<defs><marker id="arrowBlue" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#245b7a"/></marker><marker id="arrowOrange" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#8a4f13"/></marker><marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#477a55"/></marker></defs>',
        '<rect width="100%" height="100%" fill="white"/>', STYLE,
        t(35, 40, title, "title"), t(35, 68, subtitle, "sub"),
    ]


def finish(lines):
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def canonical_port_factor():
    lines = shell(
        "The canonical source object is a port–factor model",
        "Ports are the typed interface: j attaches a port to a junction, f assigns it to a factor, and Λ links electrical objects to assets.",
        1400,
        820,
    )
    lines += [rect(35, 105, 860, 600), rect(935, 105, 430, 600), t(65, 145, "electrical source model 𝔓", "head"), t(965, 145, "asset / electrical relation Λ", "head")]
    # Junction bars and factor boxes.
    junctions = {"J_i": (130, 260), "J_j": (130, 470), "J_n": (130, 615)}
    for label, (x, y) in junctions.items():
        lines += [line(x, y - 45, x, y + 45, "wire", 7), t(x - 18, y + 6, label, "body", "end")]
    factors = [(430, 235, 240, 100, "factor l1", ["q1i", "q1j"]), (430, 430, 240, 125, "factor x1 (three-winding)", ["q1", "q2", "q3"]), (430, 610, 240, 70, "factor hn", ["qn"])]
    for x, y, w, h, label, ports in factors:
        lines += [rect(x, y, w, h, "factor"), t(x + w / 2, y + 27, label, "head", "middle")]
        for idx, port in enumerate(ports):
            px = x + 45 + idx * ((w - 90) / max(len(ports) - 1, 1))
            py = y + h - 18
            lines += [f'<circle cx="{px}" cy="{py}" r="8" class="port"/>', t(px, py + 25, port, "tiny", "middle")]
    # j and f maps are intentionally distinct arrow families.
    for x1, y1, x2, y2 in [(475, 317, 130, 260), (625, 317, 130, 470), (475, 537, 130, 260), (570, 537, 130, 470), (665, 537, 130, 615), (550, 662, 130, 615)]:
        lines.append(f'<path d="M{x1} {y1} L{x2} {y2}" class="jmap" fill="none"/>')
    for x1, y1, x2, y2 in [(475, 317, 430, 317), (625, 317, 670, 317), (475, 537, 430, 537), (570, 537, 550, 537), (665, 537, 670, 537), (550, 662, 550, 662)]:
        lines.append(f'<path d="M{x1} {y1} L{x2} {y2}" class="fmap" fill="none"/>')
    lines += [t(245, 205, "j: Q → J", "body"), t(720, 205, "f: Q → Φ", "body"), line(170, 215, 220, 215, "jmap"), line(650, 215, 700, 215, "fmap")]
    lines += [rect(80, 735, 790, 50, "card"), t(100, 766, "The circles are ports; the bars are junctions; the boxes are behavioural factors.", "body")]
    # Asset side with containment and many-to-many Λ links.
    lines += [rect(980, 205, 325, 190, "asset"), t(1142, 240, "asset hierarchy 𝔄", "head", "middle"), rect(1020, 270, 120, 75, "panel"), rect(1170, 270, 105, 75, "panel"), t(1080, 305, "corridor", "body", "middle"), t(1222, 305, "x₁ asset", "body", "middle"), t(1142, 370, "containment / ownership", "small", "middle")]
    for y, label in [(475, "line ℓ₁"), (535, "winding q₁"), (595, "ground hₙ")]:
        lines += [rect(1010, y - 24, 250, 48, "panel"), t(1135, y + 5, label, "body", "middle")]
    for y1, y2 in [(305, 475), (305, 535), (305, 595), (305, 535)]:
        lines.append(f'<path d="M1170 {y1} L1135 {y2}" class="lambda" fill="none"/>')
    lines += [t(965, 670, "Λ is relational, not necessarily one asset per factor.", "body"), t(965, 694, "It is the provenance bridge that a projection cannot invent later.", "small")]
    return finish(lines)


def parse_matrix(raw):
    return [[complex(item["re"], item["im"]) for item in row] for row in raw]


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def transpose(a):
    return [list(row) for row in zip(*a)]


def add(a, b, sign=1):
    return [[a[i][j] + sign * b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def format_z(z):
    real, imag = z.real, z.imag
    sign = "+" if imag >= 0 else "−"
    return f"{real:.2f} {sign} j{abs(imag):.2f}"


def matrix_block(lines, x, y, title, matrix, cls="matrix", cell_w=88, cell_h=33):
    rows, cols = len(matrix), len(matrix[0])
    width, height = cols * cell_w + 20, rows * cell_h + 65
    lines += [rect(x, y, width, height, cls), t(x + width / 2, y + 25, title, "head", "middle")]
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            lines.append(t(x + 18 + j * cell_w, y + 56 + i * cell_h, format_z(value), "tiny"))
    return lines


def coordinate_three_by_three():
    witness = json.loads((ROOT / "experiments/generated/four-wire-impedance-model-ladder.json").read_text())
    source = parse_matrix(witness["models"]["Pi_abcn"]["series"])
    tmap = [[1, 0, 0, -1], [0, 1, 0, -1], [0, 0, 1, -1]]
    zpn = matmul(matmul(tmap, source), transpose(tmap))
    zabc = [row[:3] for row in source[:3]]
    zpn_block = [[source[i][3]] for i in range(3)]
    znp_block = [source[3][:3]]
    znn = source[3][3]
    zkron = add(zabc, [[zpn_block[i][0] * znp_block[0][j] / znn for j in range(3)] for i in range(3)], sign=-1)
    pmap = [[1, -1, 0], [0, 1, -1]]
    zpp = matmul(matmul(pmap, zabc), transpose(pmap))
    lines = shell(
        "One 4×4 source, three different 3×3 views",
        "The numbers differ because the routes differ: coordinate congruence, neutral Schur elimination, and neutral-deleted phase block.",
        1400,
        850,
    )
    lines += [rect(35, 105, 1330, 80, "card"), t(60, 138, "source", "head"), t(160, 138, "Pi_abcn series primitive from the checked four-wire fixture", "body"), t(60, 166, "same entries", "head"), t(180, 166, "different maps / assumptions → different 3×3 matrices", "body")]
    matrix_block(lines, 55, 230, "Zᵃᵇᶜ  (delete neutral coordinate)", zabc)
    matrix_block(lines, 490, 230, "Zᵖⁿ = T Z Tᵀ  (phase-to-neutral)", zpn)
    matrix_block(lines, 925, 230, "Zᴷʳᵒⁿ  (neutral Schur complement)", zkron)
    lines += [rect(55, 535, 590, 110, "warn"), t(75, 570, "not interchangeable", "head"), t(75, 598, "Zᵖⁿ is a coordinate map; Zᴷʳᵒⁿ eliminates a variable; Zᵃᵇᶜ simply drops the neutral block.", "small")]
    lines += [rect(700, 535, 645, 110, "good"), t(720, 570, "actual phase-to-phase quotient", "head"), t(720, 598, "P Zᵃᵇᶜ Pᵀ is 2×2, not 3×3: the quotient removes the common mode.", "small"), t(720, 622, f"P Zᵃᵇᶜ Pᵀ = [[{format_z(zpp[0][0])}, {format_z(zpp[0][1])}], [{format_z(zpp[1][0])}, {format_z(zpp[1][1])}]]", "tiny")]
    lines += [t(60, 700, "The correct question is not ‘which matrix is the impedance matrix?’ but ‘which coordinates, eliminated variables, and grounding contract produced it?’", "body"), t(60, 730, "All values are generated from IMPEDANCE-LADDER-001; the plate is a distinction aid, not a new certificate.", "small")]
    return finish(lines)


def size_inversion():
    lines = shell(
        "Four operations can all make a model ‘smaller’—but not in the same sense",
        "Projection, normalization, compilation, and behavioural reduction change different dimensions of a model space.",
        1400,
        820,
    )
    lines += [rect(45, 230, 250, 180, "card"), t(170, 270, "one typed source", "head", "middle"), t(170, 315, "4 nodes / 6 edges", "body", "middle"), t(170, 350, "assets + ports + factors", "small", "middle"), t(170, 385, "structure and provenance", "small", "middle")]
    cards = [(350, "projection", "4 → 4 nodes", "6 → 3 edges", "forgets identity", "warn"), (610, "normalization", "4 → 4 nodes", "6 → 6 edges", "same class", "good"), (870, "compilation", "3 → 5 nodes", "1 → 6 edges", "adds virtual objects", "card"), (1130, "behavioural reduction", "4 → 3 nodes", "4 → 5 edges", "denser fill / fewer vars", "matrix")]
    for x, title, nodes, edges, detail, cls in cards:
        lines += [line(295, 320, x, 320, "wire", 4), rect(x, 190, 235, 260, cls), t(x + 117, 235, title, "head", "middle"), t(x + 117, 290, nodes, "body", "middle"), t(x + 117, 325, edges, "body", "middle"), t(x + 117, 375, detail, "small", "middle")]
    lines += [rect(45, 520, 1320, 105, "card"), t(70, 556, "size is not semantics", "head"), t(70, 586, "Compilation can grow a graph while simplifying the device vocabulary; elimination can remove vertices while adding fill edges; projection can shrink while losing identities.", "body"), t(70, 610, "The transformation type and preservation contract—not node count—decide what survived.", "small")]
    lines += [t(55, 700, "Counts are schematic teaching examples; the arrows classify operation types, not one single running-network instance.", "small")]
    return finish(lines)


def main():
    outputs = {
        "canonical-port-factor-model.svg": canonical_port_factor(),
        "coordinate-three-by-three-plate.svg": coordinate_three_by_three(),
        "transformation-size-inversion.svg": size_inversion(),
    }
    for name, content in outputs.items():
        (OUT / name).write_text(content)
        print(f"wrote {OUT / name}")


if __name__ == "__main__":
    main()
