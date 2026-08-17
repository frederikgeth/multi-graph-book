#!/usr/bin/env python3
"""Render the four principal representation levels and orthogonal projections."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/src/assets"


def esc(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: float, y: float, value: object, cls: str = "body", anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


STYLE = """
<style>
text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:28px;font-weight:bold}
.sub{font-size:16px;fill:#5f6b76}.head{font-size:18px;font-weight:bold}.body{font-size:14px}
.small{font-size:12px;fill:#5f6b76}.level{fill:#d9eef8;stroke:#245b7a;stroke-width:2}
.special{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.asset{fill:#e5f1e7;stroke:#477a55;stroke-width:2}
.compute{fill:#f4e5e5;stroke:#8a3232;stroke-width:2}.arrow{stroke:#245b7a;stroke-width:3;fill:none;marker-end:url(#arrow)}
.dashed{stroke:#477a55;stroke-width:2;fill:none;stroke-dasharray:8 5;marker-end:url(#arrowg)}
</style>
"""


def main() -> None:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="880" viewBox="0 0 1500 880">',
        '<title>Representation taxonomy: four principal levels and orthogonal projections</title>',
        '<desc>Four principal levels run from simple topology through bus-branch and port-factor representations, with an orthogonal asset relation model and computational equation and sparsity projections attached sideways.</desc>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#245b7a"/></marker><marker id="arrowg" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#477a55"/></marker></defs>',
        '<rect width="100%" height="100%" fill="white"/>', STYLE,
        text(35, 42, "Four principal levels, with specialisations—not one universal ladder", "title"),
        text(35, 70, "The central boxes answer different electrical or identity questions. Sideways companions and computational projections retain incomparable information.", "sub"),
    ]
    boxes = [
        (70, 170, 290, 150, "1  Simple graph", "connectivity · islands · partitioning", "forgets parallel identity and terminals"),
        (420, 170, 290, 150, "2  Oriented multigraph", "bus–branch PF/OPF · asset identities", "retains two-terminal members"),
        (770, 170, 290, 150, "3  Port–factor incidence", "multiconductor · n-port · coupled", "canonical electrical source model"),
        (1120, 170, 290, 150, "4  Asset/dependency", "ownership · protection · maintenance", "orthogonal companion source model"),
    ]
    for x, y, w, h, title, detail, note in boxes:
        cls = "asset" if title.startswith("4") else "level"
        lines += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" class="{cls}"/>',
                  text(x+w/2, y+38, title, "head", "middle"), text(x+w/2, y+78, detail, "body", "middle"), text(x+w/2, y+114, note, "small", "middle")]
    for x in (360, 710):
        lines.append(f'<path d="M{x} 245 L{x+55} 245" class="arrow"/>')
    lines += [f'<path d="M1060 245 L1115 245" class="dashed"/>', text(1088, 220, "linked, not nested", "small", "middle")]
    # Specialisations attach to the first three electrical levels.
    lines += [
        '<rect x="105" y="385" width="470" height="120" rx="12" class="special"/>',
        text(340, 418, "Attached specialisations", "head", "middle"),
        text(340, 450, "node–breaker / bus–breaker / bus–branch", "body", "middle"),
        text(340, 478, "terminal and state-resolved views", "small", "middle"),
        '<path d="M215 320 L215 385" class="dashed"/>', '<path d="M565 320 L565 385" class="dashed"/>',
        '<path d="M915 320 L565 385" class="dashed"/>',
        '<rect x="650" y="385" width="700" height="120" rx="12" class="compute"/>',
        text(1000, 418, "Computational projections", "head", "middle"),
        text(1000, 450, "equation · incidence · nodal support · Jacobian · KKT · sparsity", "body", "middle"),
        text(1000, 478, "vertices and edges mean algebraic dependence, not automatically physical assets", "small", "middle"),
        '<path d="M915 320 L915 385" class="dashed"/>',
        '<rect x="70" y="585" width="1330" height="190" rx="14" fill="#fbfcfd" stroke="#17212b" stroke-width="2"/>',
        text(95, 622, "Reading rule", "head"),
        text(95, 657, "The boxes are analytical levels, not a total ordering by detail or graph size.", "body"),
        text(95, 692, "A simple graph may be perfect for islands; a port–factor graph may be necessary for a three-winding transformer;", "body"),
        text(95, 720, "an equation graph may be the right object for sparse ordering; the asset model answers a different question.", "body"),
        text(95, 752, "Every arrow therefore needs a declared map, purpose, loss ledger, and recovery/provenance contract.", "small"),
    ]
    lines.append('</svg>')
    svg = OUT / "representation-principal-levels.svg"
    png = OUT / "representation-principal-levels.png"
    svg.write_text("\n".join(lines) + "\n")
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise SystemExit("rsvg-convert is required to create PNG companions")
    subprocess.run([converter, "-o", str(png), str(svg)], check=True)
    print(f"wrote {svg}")
    print(f"wrote {png}")


if __name__ == "__main__":
    main()
