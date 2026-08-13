#!/usr/bin/env python3
"""Render the scalar parallel-branch feasible-set counterexample."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/src/assets/parallel-feasible-set-card.svg"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: int, y: int, value: str, cls: str = "body") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}">{esc(value)}</text>'


def main() -> None:
    x0, x1 = 260, 1080
    scale = (x1 - x0) / 40.0
    axis_y = [170, 300, 430]
    rows = [
        ("source members", -10.0, 10.0, "intersection of individual limits", "#3d78b5"),
        ("naive aggregate", -200 / 11, 200 / 11, "summed rating: outer relaxation", "#d8892b"),
        ("exact lifted", -10.0, 10.0, "member constraints recovered", "#477a55"),
    ]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560" viewBox="0 0 1200 560">',
        '<title>Parallel-branch feasible-set geometry</title>',
        '<desc>The naive aggregate admits a voltage drop of 15 V even though the source member limit is 10 V; exact lifting restores the source interval.</desc>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:27px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}.head{font-size:18px;font-weight:bold}.body{font-size:15px}.small{font-size:14px;fill:#5f6b76}.axis{stroke:#17212b;stroke-width:2}.interval{stroke-width:12;stroke-linecap:round}.witness{stroke:#17212b;stroke-width:3;stroke-dasharray:8 6}</style>',
        text(35, 38, "Parallel-branch feasible-set geometry", "title"),
        text(35, 66, "Equal terminal admittance does not imply equal member-constrained feasible sets.", "sub"),
        text(260, 105, "|ΔU| (V)", "head"),
    ]
    for y, (name, low, high, note, color) in zip(axis_y, rows):
        lines += [text(35, y + 6, name, "head"), f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" class="axis"/>', f'<line x1="{x0 + (low + 20) * scale:.1f}" y1="{y}" x2="{x0 + (high + 20) * scale:.1f}" y2="{y}" stroke="{color}" class="interval"/>', text(260, y + 42, note, "small")]
        for value in (-20, -10, 0, 10, 20):
            xx = x0 + (value + 20) * scale
            lines += [f'<line x1="{xx:.1f}" y1="{y - 8}" x2="{xx:.1f}" y2="{y + 8}" class="axis"/>', text(int(xx - 12), y - 16, str(value), "small")]
    witness_x = x0 + (15 + 20) * scale
    lines += [f'<line x1="{witness_x:.1f}" y1="125" x2="{witness_x:.1f}" y2="465" class="witness"/>', text(int(witness_x - 32), 500, "ΔU = 15 V", "head"), text(35, 525, "The witness lies inside the summed-rating interval but outside both source and exact-lifted intervals.", "small"), '</svg>']
    OUTPUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
