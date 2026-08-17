#!/usr/bin/env python3
"""Render a labelled three-winding port--factor anatomy card."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/src/assets/transformer-anatomy.svg"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: int, y: int, value: str, cls: str = "body") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}">{esc(value)}</text>'


def main() -> None:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700">',
        '<title>Three-winding transformer port-factor anatomy</title>',
        '<desc>A three-winding transformer is one factor with terminal bundles, internal leakage, excitation, grounding, recovered currents, and limits.</desc>',
        '<rect x="0" y="0" width="1200" height="700" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:27px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}.head{font-size:18px;font-weight:bold}.body{font-size:15px}.small{font-size:14px;fill:#5f6b76}.port{stroke:#17212b;stroke-width:2}.flow{stroke:#3d78b5;stroke-width:3;fill:none;marker-end:url(#arrow)}.aux{stroke:#7856a8;stroke-width:3;fill:none;marker-end:url(#arrow)}.ground{stroke:#477a55;stroke-width:3;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        text(35, 38, "Three-winding transformer as one port–factor", "title"),
        text(35, 66, "The factor retains winding bundles and internal relations; a compiled star is a target view, not the source device.", "sub"),
        '<rect x="430" y="155" width="340" height="330" rx="18" class="port" fill="#f8e1c4"/>',
        text(515, 205, "factor x₁", "head"), text(485, 238, "Yₓᶜᵒⁱˡ, Tₓ, Aₓ", "body"), text(472, 285, "leakage relation", "body"), text(472, 312, "excitation relation", "body"), text(472, 339, "internal grounding", "body"), text(472, 366, "tap / control identity", "body"), text(472, 420, "one factor; three winding ports", "small"),
        '<rect x="55" y="135" width="285" height="115" rx="14" class="port" fill="#e8f0fa"/>', '<rect x="55" y="292" width="285" height="115" rx="14" class="port" fill="#e8f0fa"/>', '<rect x="55" y="449" width="285" height="115" rx="14" class="port" fill="#e8f0fa"/>',
        text(78, 169, "winding 1  •  port bundle", "head"), text(78, 198, "Uₓ₁, Iₓ₁  ·  WYE", "body"), text(78, 226, "ordered terminals and limits", "small"),
        text(78, 326, "winding 2  •  port bundle", "head"), text(78, 355, "Uₓ₂, Iₓ₂  ·  WYE", "body"), text(78, 383, "excitation placement declared", "small"),
        text(78, 483, "winding 3  •  port bundle", "head"), text(78, 512, "Uₓ₃, Iₓ₃  ·  DELTA", "body"), text(78, 540, "gauge and terminal order retained", "small"),
        '<path d="M340 192 L430 230" class="flow"/><path d="M340 349 L430 320" class="flow"/><path d="M340 506 L430 400" class="flow"/>',
        '<rect x="855" y="140" width="300" height="125" rx="14" class="port" fill="#e4f4e7"/>', '<rect x="855" y="300" width="300" height="125" rx="14" class="port" fill="#e8f0fa"/>', '<rect x="855" y="460" width="300" height="125" rx="14" class="port" fill="#f4e5e5"/>',
        text(878, 175, "recovered quantities", "head"), text(878, 204, "leakage-coil and winding currents", "body"), text(878, 232, "terminal current / power maps", "small"),
        text(878, 335, "declared constraints", "head"), text(878, 364, "per-coil, winding, and terminal limits", "body"), text(878, 392, "state and decision ownership", "small"),
        text(878, 495, "explicit auxiliary factors", "head"), text(878, 524, "excitation, internal ground, controls", "body"), text(878, 552, "not silently folded into an asset", "small"),
        '<path d="M770 255 L855 200" class="flow"/><path d="M770 335 L855 360" class="flow"/><path d="M770 415 L855 520" class="aux"/>', '<path d="M430 390 L385 610 L490 610" class="ground"/>',
        text(500, 618, "grounding scope is explicit", "small"), text(35, 650, "A two-terminal compilation may introduce virtual objects, but its certificate must preserve source identity, terminal relations, limits, and recovery.", "small"), '</svg>',
    ]
    OUTPUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
