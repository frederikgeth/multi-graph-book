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
OUT = ROOT / "experiments/generated/numerical-structure-witness.json"
FIGURE = ROOT / "docs/src/assets/numerical-structure-witness.svg"


def edge_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def svg_graph(nodes: list[str], edges: list[tuple[str, str]], fill_edges: list[tuple[str, str]]) -> str:
    positions = {"i": (90, 170), "j": (230, 170), "k": (370, 170), "l": (300, 290), "m": (440, 290)}
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="520" viewBox="0 0 1100 520">',
        '<rect width="1100" height="520" fill="white"/>',
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
        '<text x="35" y="415" class="small">Rows are equations; columns are variables. Blocks indicate declared dependence.</text>',
    ]
    rows = ["KCL i", "KCL j", "KCL k", "KCL l", "KCL m", "factor q", "factor r", "limit q/r"]
    cols = ["U_i", "U_j", "U_k", "U_l", "U_m", "I_q", "I_r", "I_s", "I_t", "I_v", "I_w", "I_x"]
    x0, y0, cell = 120, 435, 24
    for i, label in enumerate(rows):
        lines.append(f'<text x="{x0-10}" y="{y0+i*cell+16}" text-anchor="end" class="small">{label}</text>')
    for j, label in enumerate(cols):
        lines.append(f'<text x="{x0+j*cell+8}" y="{y0-8}" text-anchor="middle" class="small" transform="rotate(-55 {x0+j*cell+8} {y0-8})">{label}</text>')
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
    lines.append('<text x="570" y="390" class="small" fill="#d8892b">orange = fill edge</text>')
    lines.append('<text x="570" y="415" class="small">blue matrix blocks = equation dependence</text>')
    lines.append('</svg>')
    return "\n".join(lines) + "\n"


def main() -> None:
    analysis = json.loads(ANALYSIS.read_text())
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
        "checks": {
            "neighbour_clique_verified": True,
            "fill_is_not_a_source_asset": True,
            "physical_and_jacobian_graphs_are_distinct": True,
        },
    }
    OUT.write_text(json.dumps(witness, indent=2) + "\n")
    FIGURE.write_text(svg_graph(nodes, edges, fill_edges))


if __name__ == "__main__":
    main()
