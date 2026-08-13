#!/usr/bin/env python3
"""Render nonlinear source/aggregate KKT sparsity and ordering fill."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "experiments/generated/nonlinear-kkt-witness.json"
OUTPUT = ROOT / "docs/src/assets/nonlinear-kkt-witness.svg"


def matrix_pattern(rows: int, cols: int, entries: set[tuple[int, int]], x: int, y: int, size: int, color: str) -> list[str]:
    cell = size / max(rows, cols)
    width, height = cell * cols, cell * rows
    lines = [f'<rect x="{x}" y="{y}" width="{width:.2f}" height="{height:.2f}" fill="#f8fafc" stroke="#9aa7b2"/>']
    for i in range(rows + 1):
        yy = y + i * cell
        lines.append(f'<line x1="{x}" y1="{yy:.2f}" x2="{x+width:.2f}" y2="{yy:.2f}" stroke="#dce2e8" stroke-width="0.5"/>')
    for j in range(cols + 1):
        xx = x + j * cell
        lines.append(f'<line x1="{xx:.2f}" y1="{y}" x2="{xx:.2f}" y2="{y+height:.2f}" stroke="#dce2e8" stroke-width="0.5"/>')
    for row, col in entries:
        lines.append(f'<rect x="{x+(col-1)*cell:.2f}" y="{y+(row-1)*cell:.2f}" width="{cell:.2f}" height="{cell:.2f}" fill="{color}"/>')
    return lines


def pattern_from_witness(model: dict) -> set[tuple[int, int]]:
    """Use the exact thresholded KKT entries emitted by the Julia witness."""
    return {(entry["row"], entry["col"]) for entry in model["kkt"]["entries"]}


def main() -> None:
    data = json.loads(INPUT.read_text())
    source, aggregate = data["source"], data["aggregate"]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650" viewBox="0 0 1200 650">',
        '<rect width="1200" height="650" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:23px;font-weight:bold}.sub{font-size:15px}.metric{font-size:14px;fill:#5f6b76}</style>',
        '<text x="35" y="38" class="title">Nonlinear AC decision Jacobian and KKT fill witness</text>',
        '<text x="35" y="64" class="sub">Finite-difference residual Jacobians; symbolic KKT fill under two explicit elimination orders.</text>',
        '<text x="55" y="105" class="title">Source: two members</text>',
        '<text x="660" y="105" class="title">Aggregate: one recovered current</text>',
    ]
    lines += matrix_pattern(source["kkt"]["dimension"], source["kkt"]["dimension"], pattern_from_witness(source), 55, 130, 430, "#3d78b5")
    lines += matrix_pattern(aggregate["kkt"]["dimension"], aggregate["kkt"]["dimension"], pattern_from_witness(aggregate), 660, 130, 430, "#7856a8")
    lines += [
        f'<text x="55" y="600" class="metric">J: {source["jacobian"]["rows"]}×{source["jacobian"]["cols"]}, {source["jacobian"]["nnz_atol"]} nonzeros · KKT: {source["kkt"]["dimension"]}×{source["kkt"]["dimension"]}</text>',
        f'<text x="55" y="622" class="metric">natural fill {source["kkt"]["orders"]["natural"]["fill_edges"]}; constraints-first fill {source["kkt"]["orders"]["constraints_first"]["fill_edges"]}</text>',
        f'<text x="660" y="600" class="metric">J: {aggregate["jacobian"]["rows"]}×{aggregate["jacobian"]["cols"]}, {aggregate["jacobian"]["nnz_atol"]} nonzeros · KKT: {aggregate["kkt"]["dimension"]}×{aggregate["kkt"]["dimension"]}</text>',
        f'<text x="660" y="622" class="metric">natural fill {aggregate["kkt"]["orders"]["natural"]["fill_edges"]}; constraints-first fill {aggregate["kkt"]["orders"]["constraints_first"]["fill_edges"]}</text>',
        '</svg>',
    ]
    OUTPUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
