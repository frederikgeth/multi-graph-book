#!/usr/bin/env python3
"""Render the reusable complex-plane feasible-set geometry card."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/src/assets/parallel-feasible-set-card.svg"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: int, y: int, value: str, cls: str = "body", anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


def main() -> None:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720">',
        '<title>Complex-plane feasible-set geometry for parallel limits</title>',
        '<desc>The retained member limits form a source disc in the complex voltage-drop plane, while a summed-rating aggregate admits a larger outer disc. A weighted quadratic limit is shown as an ellipse to distinguish the general geometry from the scalar witness.</desc>',
        '<rect width="1200" height="720" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:27px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}.head{font-size:18px;font-weight:bold}.body{font-size:15px}.small{font-size:14px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.axis{stroke:#17212b;stroke-width:2}.source{fill:#d9eef8;fill-opacity:.65;stroke:#245b7a;stroke-width:3}.aggregate{fill:#f8e1c4;fill-opacity:.55;stroke:#8a4f13;stroke-width:3;stroke-dasharray:9 6}.ellipse{fill:#e4f4e7;fill-opacity:.6;stroke:#477a55;stroke-width:3}.witness{stroke:#8a3232;stroke-width:3;stroke-dasharray:8 6}.dot{fill:#8a3232}</style>',
        text(35, 38, "Complex-plane feasible-set geometry", "title"),
        text(35, 66, "The scalar witness uses discs; weighted quadratic limits generalize the boundary to ellipses.", "sub"),
        '<rect x="35" y="95" width="540" height="470" rx="14" class="panel"/>',
        '<rect x="625" y="95" width="540" height="470" rx="14" class="panel"/>',
        text(60, 130, "retained member constraints", "head"),
        text(650, 130, "aggregate and weighted limits", "head"),
    ]
    cx, cy = 305, 355
    lines += [
        f'<line x1="100" y1="{cy}" x2="510" y2="{cy}" class="axis"/>',
        f'<line x1="{cx}" y1="170" x2="{cx}" y2="520" class="axis"/>',
        text(510, cy + 25, "Re z", "small", "end"),
        text(cx + 10, 170, "Im z", "small"),
        f'<circle cx="{cx}" cy="{cy}" r="125" class="source"/>',
        text(cx, cy - 137, "q limit: |z| ≤ 1", "small", "middle"),
        text(cx, cy + 155, "r limit is looser here; intersection is the q disc", "small", "middle"),
    ]
    cx2, cy2 = 895, 355
    witness_x = cx2 + 125
    lines += [
        f'<line x1="690" y1="{cy2}" x2="1100" y2="{cy2}" class="axis"/>',
        f'<line x1="{cx2}" y1="170" x2="{cx2}" y2="520" class="axis"/>',
        text(1100, cy2 + 25, "Re z", "small", "end"),
        text(cx2 + 10, 170, "Im z", "small"),
        f'<circle cx="{cx2}" cy="{cy2}" r="190" class="aggregate"/>',
        f'<ellipse cx="{cx2}" cy="{cy2}" rx="155" ry="105" class="ellipse"/>',
        text(cx2, 145, "summed rating: |z| ≤ 200/110 ≈ 1.82", "small", "middle"),
        text(cx2, cy2 + 155, "weighted quadratic limit: an ellipse", "small", "middle"),
        f'<line x1="{witness_x}" y1="175" x2="{witness_x}" y2="520" class="witness"/>',
        f'<circle cx="{witness_x}" cy="{cy2}" r="7" class="dot"/>',
        text(witness_x + 12, cy2 - 14, "15 V witness", "body"),
        text(35, 610, "The witness lies inside the aggregate disc but outside the retained member disc; recovery exposes the violated member limit.", "small"),
        text(35, 640, "For weighted or coupled limits, the same containment test becomes disc/ellipse or quadratic-form geometry.", "small"),
        '</svg>',
    ]
    OUTPUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
