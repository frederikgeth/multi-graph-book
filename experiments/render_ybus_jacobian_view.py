#!/usr/bin/env python3
"""Render the pinned BMOPFTools Ybus and realified-current-Jacobian patterns."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "experiments/generated/ybus-jacobian-witness.json"
OUTPUT = ROOT / "docs/src/assets/ybus-jacobian-witness.svg"


def pattern(entries: list[dict], rows: int, cols: int, x: int, y: int, width: int, height: int, color: str) -> list[str]:
    cell = min(width / cols, height / rows)
    lines = [f'<rect x="{x}" y="{y}" width="{cell*cols:.2f}" height="{cell*rows:.2f}" fill="#f8fafc" stroke="#9aa7b2"/>']
    for row in range(rows + 1):
        yy = y + row * cell
        lines.append(f'<line x1="{x}" y1="{yy:.2f}" x2="{x + cell*cols:.2f}" y2="{yy:.2f}" stroke="#dce2e8" stroke-width="0.5"/>')
    for col in range(cols + 1):
        xx = x + col * cell
        lines.append(f'<line x1="{xx:.2f}" y1="{y}" x2="{xx:.2f}" y2="{y + cell*rows:.2f}" stroke="#dce2e8" stroke-width="0.5"/>')
    for entry in entries:
        xx = x + (entry["col"] - 1) * cell
        yy = y + (entry["row"] - 1) * cell
        lines.append(f'<rect x="{xx:.2f}" y="{yy:.2f}" width="{cell:.2f}" height="{cell:.2f}" fill="{color}"/>')
    return lines


def main() -> None:
    data = json.loads(INPUT.read_text())
    passive = data["passive_ybus"]
    jac = data["realified_current_jacobian"]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="680" viewBox="0 0 1200 680">',
        '<rect width="1200" height="680" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:24px;font-weight:bold}.sub{font-size:15px}.metric{font-size:14px;fill:#5f6b76}</style>',
        '<text x="35" y="38" class="title">BMOPFTools running-network numerical structure</text>',
        '<text x="35" y="65" class="sub">Passive Ybus pattern and its realified current-voltage map; entries are generated, not hand-drawn.</text>',
        '<text x="55" y="105" class="title">Passive Ybus (20 × 20)</text>',
        '<text x="55" y="128" class="metric">166 nonzeros · complex-symmetric residual 1.8×10⁻¹⁵</text>',
        '<text x="660" y="105" class="title">Realified current Jacobian (40 × 40)</text>',
        '<text x="660" y="128" class="metric">664 nonzeros · J = [Re(Y) −Im(Y); Im(Y) Re(Y)]</text>',
    ]
    lines += pattern(passive["entries"], passive["rows"], passive["cols"], 55, 150, 450, 450, "#3d78b5")
    lines += pattern(jac["entries"], jac["rows"], jac["cols"], 660, 150, 450, 450, "#7856a8")
    lines += [
        '<text x="55" y="640" class="metric">Condition estimate is norm- and scaling-dependent; this witness reports it explicitly.</text>',
        f'<text x="660" y="640" class="metric">κ₂(Y) ≈ {passive["condition_2"]:.3e}; rank at tolerance = {passive["rank_atol"]}/{passive["rows"]}</text>',
        '</svg>',
    ]
    OUTPUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
