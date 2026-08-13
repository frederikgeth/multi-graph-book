#!/usr/bin/env python3
"""Render the earth/neutral model-class ladder for the foundations chapter."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/src/assets/earth-return-ladder.svg"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x: int, y: int, value: str, cls: str = "body") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}">{esc(value)}</text>'


def main() -> None:
    classes = [
        ("E₀", "ideal reference", "gauge only", "no earth current", "PF/OPF under declared balance", "#f7f9fb"),
        ("E₁", "reduced earth return", "embedded impedance/shunt", "return effects, no asset path", "feeder PF and planning", "#e8f0fa"),
        ("E₂", "explicit earth conductor", "voltage/current port", "coupling and conductor limits", "four-wire and protection studies", "#e4f4e7"),
        ("E₃", "asset-aware grounding", "electrical + asset relations", "electrode/grid identity and state", "outage, switching, and maintenance", "#f8e1c4"),
    ]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="530" viewBox="0 0 1200 530">',
        '<title>Earth and neutral model classes</title>',
        '<desc>A ladder from an ideal reference to an asset-aware grounding model, with explicit limits on the questions each class can answer.</desc>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:27px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}.head{font-size:18px;font-weight:bold}.body{font-size:15px}.small{font-size:14px;fill:#5f6b76}.box{stroke:#17212b;stroke-width:2}.arrow{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        t(35, 38, "Earth / neutral model-class ladder", "title"),
        t(35, 66, "More detail is not automatically better: choose the class from the observations and decisions to preserve.", "sub"),
        t(40, 112, "Class", "head"), t(135, 112, "Electrical object", "head"), t(385, 112, "Retained return meaning", "head"), t(700, 112, "Typical study boundary", "head"),
    ]
    y = 135
    for index, (code, name, electrical, retained, study, fill) in enumerate(classes):
        lines.append(f'<rect x="35" y="{y}" width="1130" height="72" rx="10" class="box" fill="{fill}"/>')
        lines += [t(55, y + 30, code, "head"), t(135, y + 27, name, "body"), t(385, y + 27, electrical, "body"), t(385, y + 51, retained, "small"), t(700, y + 38, study, "body")]
        if index < len(classes) - 1:
            lines.append(f'<path d="M600 {y + 78} L600 {y + 92}" class="arrow"/>')
        y += 85
    lines += [
        t(35, 500, "The arrows indicate added modelling commitments, not a universal accuracy ranking.", "small"),
        t(35, 520, "A reduction is admissible only when its omitted return, protection, and asset observations are outside the contract or recoverable.", "small"),
        '</svg>',
    ]
    OUTPUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
