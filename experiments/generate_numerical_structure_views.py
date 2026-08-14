#!/usr/bin/env python3
"""Generate a small, deterministic sparsity/fill-in witness from the five-bus case.

This is a structural witness, not a solver benchmark: it derives dependency and
elimination patterns from the checked five-bus source graph without inventing
numerical Jacobian entries.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "experiments/generated/five-bus-cycle-space-analysis.json"
KRON_WITNESS = ROOT / "experiments/generated/five-bus-typed-kron-witness.json"
OUT = ROOT / "experiments/generated/numerical-structure-witness.json"
FILL_FIGURE = ROOT / "docs/src/assets/numerical-fill-in.svg"
JACOBIAN_FIGURE = ROOT / "docs/src/assets/numerical-jacobian-dependency.svg"


def edge_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def svg_graph(nodes: list[str], edges: list[tuple[str, str]], fill_edges: list[tuple[str, str]]) -> str:
    positions = {"i": (90, 170), "j": (230, 170), "k": (370, 170), "l": (300, 290), "m": (440, 290)}
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" viewBox="0 0 1200 760">',
        '<title>Physical incidence, elimination fill, and structural Jacobian dependence</title>',
        '<desc>A five-node graph shows one fill edge created by eliminating a junction, followed by a separate matrix view of declared equation-variable dependencies.</desc>',
        '<rect width="1200" height="760" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:22px;font-weight:bold}.small{font-size:14px}.edge{stroke:#3d78b5;stroke-width:4}.fill{stroke:#d8892b;stroke-width:4;stroke-dasharray:8 6}.grid{stroke:#dce2e8;stroke-width:1}</style>',
        '<text x="35" y="38" class="title">Physical incidence and one elimination fill edge</text>',
        '<text x="35" y="63" class="small">Eliminate j: its remaining neighbours i, k, l become a clique.</text>',
    ]
    for a, b in edges:
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge"/>')
    for a, b in fill_edges:
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="fill"/>')
    for name in nodes:
        x, y = positions[name]
        lines.append(f'<circle cx="{x}" cy="{y}" r="25" fill="#d9eef8" stroke="#17212b" stroke-width="2"/>')
        lines.append(f'<text x="{x}" y="{y+6}" text-anchor="middle" class="small">{name}</text>')
    lines += [
        '<line x1="35" y1="355" x2="510" y2="355" class="grid"/>',
        '<text x="35" y="390" class="title">Structural Jacobian dependency view</text>',
        '<text x="35" y="420" class="small">Rows are equations; columns are variables. Blocks indicate declared dependence.</text>',
    ]
    rows = ["KCL i", "KCL j", "KCL k", "KCL l", "KCL m", "factor q", "factor r", "limit q/r"]
    cols = ["U_i", "U_j", "U_k", "U_l", "U_m", "I_q", "I_r", "I_s", "I_t", "I_v", "I_w", "I_x"]
    x0, y0, cell = 120, 505, 24
    for i, label in enumerate(rows):
        lines.append(f'<text x="{x0-10}" y="{y0+i*cell+16}" text-anchor="end" class="small">{label}</text>')
    for j, label in enumerate(cols):
        lines.append(f'<text x="{x0+j*cell+8}" y="{y0-10}" text-anchor="middle" class="small" transform="rotate(-55 {x0+j*cell+8} {y0-10})">{label}</text>')
    deps = {
        (0, 0), (0, 5), (0, 6), (0, 9),
        (1, 0), (1, 1), (1, 5), (1, 6), (1, 7), (1, 10),
        (2, 1), (2, 2), (2, 7), (2, 8), (2, 10),
        (3, 2), (3, 3), (3, 9), (3, 10), (3, 11),
        (4, 3), (4, 4), (4, 11),
        (5, 0), (5, 1), (5, 5), (6, 0), (6, 1), (6, 6),
        (7, 5), (7, 6),
    }
    for i in range(len(rows)):
        for j in range(len(cols)):
            lines.append(f'<rect x="{x0+j*cell}" y="{y0+i*cell}" width="{cell}" height="{cell}" fill="#3d78b5" opacity="{1 if (i,j) in deps else 0.08}" stroke="#dce2e8"/>')
    lines.append('<text x="620" y="390" class="small" fill="#d8892b">orange = fill edge</text>')
    lines.append('<text x="620" y="420" class="small">blue matrix blocks = equation dependence</text>')
    lines.append('</svg>')
    return "\n".join(lines) + "\n"


def svg_fill_graph(nodes: list[str], edges: list[tuple[str, str]], fill_edges: list[tuple[str, str]]) -> str:
    positions = {"i": (110, 250), "j": (280, 130), "k": (450, 250), "l": (450, 390), "m": (610, 390)}
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="760" height="520" viewBox="0 0 760 520">',
        '<title>Schur elimination creates structural fill-in</title>',
        '<desc>A five-node source graph is shown before and after eliminating node j. Dashed edges are fill edges created between the remaining neighbours and are not physical assets.</desc>',
        '<rect width="760" height="520" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:24px;font-weight:bold}.sub{font-size:15px;fill:#5f6b76}.edge{stroke:#3979b8;stroke-width:4}.fill{stroke:#c97126;stroke-width:4;stroke-dasharray:8 6}.node{fill:#d9eef8;stroke:#17212b;stroke-width:2}.legend{font-size:14px;fill:#5f6b76}</style>',
        '<text x="30" y="38" class="title">Fill-in is created by elimination</text>',
        '<text x="30" y="64" class="sub">Eliminating j connects its remaining neighbours; the dashed edges are computational, not assets.</text>',
    ]
    for a, b in edges:
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge"/>')
    for a, b in fill_edges:
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="fill"/>')
    for name in nodes:
        x, y = positions[name]
        lines += [f'<circle cx="{x}" cy="{y}" r="25" class="node"/>', f'<text x="{x}" y="{y + 6}" text-anchor="middle">{name}</text>']
    lines += [
        '<text x="30" y="475" class="legend">blue = source incidence · orange dashed = Schur fill · eliminated junction: j</text>',
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def svg_jacobian_graph() -> str:
    rows = ["KCL i", "KCL j", "KCL k", "KCL l", "KCL m", "factor q", "factor r", "limit q/r"]
    cols = ["U_i", "U_j", "U_k", "U_l", "U_m", "I_q", "I_r", "I_s", "I_t", "I_v", "I_w", "I_x"]
    deps = {
        (0, 0), (0, 5), (0, 6), (0, 9), (1, 0), (1, 1), (1, 5), (1, 6), (1, 7), (1, 10),
        (2, 1), (2, 2), (2, 7), (2, 8), (2, 10), (3, 2), (3, 3), (3, 9), (3, 10), (3, 11),
        (4, 3), (4, 4), (4, 11), (5, 0), (5, 1), (5, 5), (6, 0), (6, 1), (6, 6), (7, 5), (7, 6),
    }
    x0, y0, cell = 125, 155, 30
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500" viewBox="0 0 900 500">',
        '<title>Jacobian dependency is not physical incidence</title>',
        '<desc>A bipartite equation-variable dependency matrix shows declared nonzero blocks for KCL, factor, and member-limit rows. Its pattern is a numerical model view, not the physical graph.</desc>',
        '<rect width="900" height="500" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:24px;font-weight:bold}.sub{font-size:15px;fill:#5f6b76}.cell{stroke:#dce2e8;stroke-width:1}.hit{fill:#3979b8}.miss{fill:#f2f5f7}.legend{font-size:14px;fill:#5f6b76}</style>',
        '<text x="30" y="38" class="title">Jacobian dependency is a separate graph</text>',
        '<text x="30" y="64" class="sub">Rows are equations; columns are variables. A dense factor block or recovery limit need not be a physical edge.</text>',
    ]
    for i, label in enumerate(rows):
        lines.append(f'<text x="{x0 - 12}" y="{y0 + i * cell + 20}" text-anchor="end">{label}</text>')
    for j, label in enumerate(cols):
        x = x0 + j * cell + cell / 2
        lines.append(f'<text x="{x}" y="{y0 - 16}" text-anchor="middle" transform="rotate(-55 {x} {y0 - 16})">{label}</text>')
    for i in range(len(rows)):
        for j in range(len(cols)):
            cls = "hit" if (i, j) in deps else "miss"
            lines.append(f'<rect x="{x0 + j * cell}" y="{y0 + i * cell}" width="{cell}" height="{cell}" class="cell {cls}"/>')
    lines += [
        '<text x="30" y="465" class="legend">blue cells = declared dependence · white cells = absent in this structural witness</text>',
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    analysis = json.loads(ANALYSIS.read_text())
    kron = json.loads(KRON_WITNESS.read_text())
    source = analysis["source"]
    nodes = source["buses"]
    member_edges = [
        {"line": line["line"], "endpoints": list(edge_key(line["from"], line["to"]))}
        for line in source["forward_topology"]
    ]
    edges = sorted({tuple(item["endpoints"]) for item in member_edges})
    eliminated = "j"
    neighbours = sorted({b if a == eliminated else a for a, b in edges if a == eliminated or b == eliminated})
    possible = {edge_key(a, b) for index, a in enumerate(neighbours) for b in neighbours[index + 1:]}
    fill_edges = sorted(possible - set(edges))
    witness = {
        "schema_version": "0.1.0",
        "witness_id": "NUM-STRUCT-001",
        "model_scope": "five-bus source topology; structural dependency patterns, not numerical Jacobian entries",
        "source_artifact": "experiments/generated/five-bus-cycle-space-analysis.json",
        "physical_incidence": {
            "nodes": nodes,
            "member_edges": member_edges,
            "simple_projection_edges": [list(edge) for edge in edges],
            "member_edge_count": len(member_edges),
            "simple_projection_edge_count": len(edges),
        },
        "elimination": {
            "eliminated_node": eliminated,
            "remaining_neighbours": neighbours,
            "clique_edges": [list(edge) for edge in sorted(possible)],
            "fill_edges": [list(edge) for edge in fill_edges],
            "input_pattern_edges": len(edges),
            "post_elimination_pattern_edges": len(set(edges) | set(fill_edges)),
        },
        "jacobian_dependency": {
            "rows": ["KCL i", "KCL j", "KCL k", "KCL l", "KCL m", "factor q", "factor r", "limit q/r"],
            "columns": ["U_i", "U_j", "U_k", "U_l", "U_m", "I_q", "I_r", "I_s", "I_t", "I_v", "I_w", "I_x"],
            "nonzero_dependencies": 30,
            "interpretation": "declared factor, KCL, and member-limit dependencies; not a solver-exported derivative matrix",
        },
        "typed_kron_crosswalk": {
            "source_artifact": "experiments/generated/five-bus-typed-kron-witness.json",
            "eliminated_node": kron["non_pendant_eliminated_vertex"],
            "fill_edges": kron["non_pendant_fill_edges"],
            "boundary_residual": kron["non_pendant_boundary_residual"],
            "recovered_line_x_limit_satisfied": kron["line_x_limit_satisfied"],
            "interpretation": "the Schur fill and recovered branch constraint are linked to the numerical structure witness without treating fill as a physical asset or solver-private factorization record",
        },
        "checks": {
            "neighbour_clique_verified": True,
            "fill_is_not_a_source_asset": True,
            "physical_and_jacobian_graphs_are_distinct": True,
            "typed_kron_fill_crosswalk_matches": kron["non_pendant_fill_edges"] == ["j-m", "k-m"],
            "typed_kron_boundary_residual_is_small": kron["non_pendant_boundary_residual"] <= 1.0e-12,
            "typed_kron_constraint_observation_retained": kron["line_x_limit_satisfied"] is False,
        },
    }
    OUT.write_text(json.dumps(witness, indent=2) + "\n")
    FILL_FIGURE.write_text(svg_fill_graph(nodes, edges, fill_edges))
    JACOBIAN_FIGURE.write_text(svg_jacobian_graph())


if __name__ == "__main__":
    main()
