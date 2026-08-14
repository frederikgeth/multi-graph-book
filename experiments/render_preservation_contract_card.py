#!/usr/bin/env python3
"""Render the reusable preservation-contract card used by the foundations chapter."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/src/assets/preservation-contract-card.svg"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: int, y: int, value: str, cls: str = "body") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}">{esc(value)}</text>'


def card(x: int, y: int, width: int, height: int, heading: str, lines: list[str], fill: str) -> list[str]:
    output = [f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="12" class="card" fill="{fill}"/>']
    output.append(text(x + 20, y + 32, heading, "heading"))
    for index, line in enumerate(lines, start=1):
        output.append(text(x + 20, y + 32 + 25 * index, line))
    return output


def main() -> None:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720">',
        '<title>Preservation contract card</title>',
        '<desc>A transformation certificate records scope, guards, retained observations, forgotten meaning, recovery, and evidence.</desc>',
        '<rect x="0" y="0" width="1200" height="720" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:28px;font-weight:bold}.subtitle{font-size:16px;fill:#5f6b76}.heading{font-size:18px;font-weight:bold}.body{font-size:15px}.small{font-size:14px;fill:#5f6b76}.card{stroke:#17212b;stroke-width:2}.arrow{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        text(40, 42, "Preservation contract", "title"),
        text(40, 70, "A transformation is a scoped claim about observations and decisions, not a label of similarity.", "subtitle"),
    ]
    lines += card(40, 105, 350, 150, "1. Scope", ["source and target model categories", "admissible inputs, states, and decisions", "observation family H and boundary", "units, coordinates, and orientation"], "#e4f4e7")
    lines += card(425, 105, 350, 150, "2. Guards", ["rank / invertibility conditions", "grounding and terminal compatibility", "state and device-library assumptions", "applicability domain"], "#e8f0fa")
    lines += card(810, 105, 350, 150, "3. Classification", ["exact, inner, outer, or scenario", "feasible-set and objective relation", "decision map and active constraints", "error / margin if approximate"], "#f8e1c4")
    lines += ['<path d="M215 275 L215 320 L600 320 L600 350" class="arrow"/>', '<path d="M600 275 L600 350" class="arrow"/>', '<path d="M985 275 L985 320 L600 320 L600 350" class="arrow"/>']
    lines += card(275, 350, 650, 110, "4. Transformation map", ["source objects  →  generated / reduced objects", "typed relation, provenance, and target interfaces"], "#f7f9fb")
    lines += ['<path d="M600 480 L600 515 L215 515 L215 545" class="arrow"/>', '<path d="M600 480 L600 545" class="arrow"/>', '<path d="M600 480 L600 515 L985 515 L985 545" class="arrow"/>']
    lines += card(40, 545, 350, 115, "5. Retains", ["terminal behaviour and limits", "states, controls, objectives", "declared observations"], "#e8f0fa")
    lines += card(425, 545, 350, 115, "6. Forgets", ["unanswerable identities or states", "eliminated variables and constraints", "out-of-scope physical detail"], "#f4e5e5")
    lines += card(810, 545, 350, 115, "7. Recovery + evidence", ["recovery and constraint maps", "provenance and reproducible artifact", "proof, test, or external source"], "#e4f4e7")
    lines += [text(40, 700, "Colour is secondary; headings and text carry the contract in monochrome.", "small"), '</svg>']
    OUTPUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
