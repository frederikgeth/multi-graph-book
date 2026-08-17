#!/usr/bin/env python3
"""Render the two onboarding routes for the graph/transmission reading guide."""

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/src/assets"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, value, cls="body", anchor="middle"):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


STYLE = """
<style>
text{font-family:Arial,sans-serif;fill:#17212b}
.title{font-size:28px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}
.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:19px;font-weight:bold}
.body{font-size:15px}.small{font-size:13px;fill:#5f6b76}.tiny{font-size:12px;fill:#5f6b76}
.graph{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.trans{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}
.shared{fill:#e5f1e7;stroke:#477a55;stroke-width:2}.route{stroke:#245b7a;stroke-width:3;fill:none;marker-end:url(#arrow)}
.route2{stroke:#8a4f13;stroke-width:3;fill:none;marker-end:url(#arrow2)}
.merge{stroke:#477a55;stroke-width:3;fill:none;marker-end:url(#arrow3)}
.dash{stroke:#17212b;stroke-width:2;stroke-dasharray:7 5;fill:none}
</style>
"""


def box(x, y, w, h, label, cls, detail):
    return [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" class="{cls}"/>',
        text(x + w / 2, y + 31, label, "head"),
        text(x + w / 2, y + 57, detail, "small"),
    ]


def render() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="820" viewBox="0 0 1400 820">',
        '<title>Two routes into multiconductor power-network graph models</title>',
        '<desc>Simple graph theory and balanced transmission modelling take distinct routes through progressively richer representations and converge on preservation contracts.</desc>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#245b7a"/></marker><marker id="arrow2" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#8a4f13"/></marker><marker id="arrow3" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#477a55"/></marker></defs>',
        '<rect width="100%" height="100%" fill="white"/>', STYLE,
        text(38, 44, "Two routes into one preservation language", "title", "start"),
        text(38, 72, "Use the route that matches your background; the convergent target is a decision-aware model, not a single graph drawing.", "sub", "start"),
        '<rect x="38" y="102" width="1324" height="620" rx="14" class="panel"/>',
        text(700, 138, "Start here", "head"),
        *box(90, 175, 270, 74, "Simple graph theory", "graph", "vertices · edges · cycles"),
        *box(1040, 175, 270, 74, "Transmission modelling", "trans", "bus–branch · positive sequence"),
        *box(90, 300, 270, 74, "Multigraph identity", "graph", "parallel members stay distinct"),
        *box(1040, 300, 270, 74, "Phase/neutral expansion", "trans", "coupling · shunts · grounding"),
        *box(90, 425, 270, 74, "Terminal/factor view", "graph", "ports · n-port devices"),
        *box(1040, 425, 270, 74, "Matrix-valued edge", "trans", "block equations · limits"),
        *box(515, 555, 370, 78, "First decision counterexample", "shared", "same terminal Y, different feasible set"),
        *box(515, 655, 370, 48, "Preservation contracts", "shared", "what survives, what is recovered"),
        '<path d="M225 249 L225 300" class="route"/>',
        '<path d="M225 374 L225 425" class="route"/>',
        '<path d="M1175 249 L1175 300" class="route2"/>',
        '<path d="M1175 374 L1175 425" class="route2"/>',
        '<path d="M360 462 C470 462 465 565 515 585" class="merge"/>',
        '<path d="M1040 462 C930 462 935 565 885 585" class="merge"/>',
        '<path d="M700 633 L700 655" class="merge"/>',
        text(700, 192, "qualify the graph", "tiny"),
        text(700, 252, "", "tiny"),
        text(700, 742, "The route map is pedagogical: each arrow adds structure or makes a preservation obligation explicit.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    svg = OUT / "reading-routes-graph-transmission.svg"
    png = OUT / "reading-routes-graph-transmission.png"
    svg.write_text(render())
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise SystemExit("rsvg-convert is required to create the PNG companion")
    subprocess.run([converter, "-o", str(png), str(svg)], check=True)
    print(f"wrote {svg}")
    print(f"wrote {png}")


if __name__ == "__main__":
    main()
