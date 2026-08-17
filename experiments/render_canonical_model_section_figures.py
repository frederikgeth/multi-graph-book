#!/usr/bin/env python3
"""Render the three high-value figures for the canonical-model section."""

from __future__ import annotations

import json
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
text{font-family:Arial,sans-serif;fill:#17212b}
.title{font-size:28px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}
.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:19px;font-weight:bold}
.body{font-size:15px}.small{font-size:13px;fill:#5f6b76}.tiny{font-size:12px;fill:#5f6b76}
.blue{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.orange{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}
.green{fill:#e5f1e7;stroke:#477a55;stroke-width:2}.red{fill:#f4e5e5;stroke:#8a3232;stroke-width:2}
.axis{stroke:#17212b;stroke-width:2}.grid{stroke:#c7d0d8;stroke-width:1;stroke-dasharray:4 4}
.limit{stroke:#8a3232;stroke-width:2;stroke-dasharray:7 5}.curve1{stroke:#245b7a;stroke-width:3;fill:none}
.curve2{stroke:#8a4f13;stroke-width:3;fill:none}.curve3{stroke:#477a55;stroke-width:3;fill:none}
.curve4{stroke:#7856a8;stroke-width:3;fill:none}.failed{stroke:#8a3232;stroke-width:3;fill:none;stroke-dasharray:8 5}
.arrow{stroke:#245b7a;stroke-width:3;fill:none;marker-end:url(#arrow)}
.arrowo{stroke:#8a4f13;stroke-width:3;fill:none;marker-end:url(#arrowo)}
.arrowg{stroke:#477a55;stroke-width:3;fill:none;marker-end:url(#arrowg)}
</style>
"""


def shell(title: str, subtitle: str, width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f"<title>{esc(title)}</title>", f"<desc>{esc(subtitle)}</desc>",
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#245b7a"/></marker><marker id="arrowo" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#8a4f13"/></marker><marker id="arrowg" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#477a55"/></marker></defs>',
        '<rect width="100%" height="100%" fill="white"/>', STYLE,
        text(35, 40, title, "title"), text(35, 68, subtitle, "sub"),
    ]


def finish(lines: list[str]) -> str:
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def plot_path(points: list[tuple[float, float]], x0: float, y0: float, w: float, h: float,
              xmin: float, xmax: float, ymin: float, ymax: float, cls: str) -> str:
    def px(x: float) -> float:
        return x0 + (x - xmin) / (xmax - xmin) * w

    def py(y: float) -> float:
        return y0 + h - (y - ymin) / (ymax - ymin) * h

    d = " ".join(("M" if i == 0 else "L") + f"{px(x):.1f},{py(y):.1f}" for i, (x, y) in enumerate(points))
    return f'<path d="{d}" class="{cls}"/>'


def dot(x: float, y: float, x0: float, y0: float, w: float, h: float,
        xmin: float, xmax: float, ymin: float, ymax: float, cls: str = "blue") -> str:
    px = x0 + (x - xmin) / (xmax - xmin) * w
    py = y0 + h - (y - ymin) / (ymax - ymin) * h
    return f'<circle cx="{px:.1f}" cy="{py:.1f}" r="7" class="{cls}"/>'


def axes(lines: list[str], x0: float, y0: float, w: float, h: float,
         xmin: float, xmax: float, ymin: float, ymax: float, xlabel: str, ylabel: str) -> None:
    lines += [f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" class="axis"/>',
              f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" class="axis"/>',
              text(x0 + w / 2, y0 + h + 36, xlabel, "small", "middle"),
              text(x0 + 4, y0 - 12, ylabel, "small", "start")]
    for value in (xmin, (xmin + xmax) / 2, xmax):
        x = x0 + (value - xmin) / (xmax - xmin) * w
        lines += [f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y0 + h}" class="grid"/>', text(x, y0 + h + 18, f"{value:g}", "tiny", "middle")]
    for value in (ymin, (ymin + ymax) / 2, ymax):
        y = y0 + h - (value - ymin) / (ymax - ymin) * h
        lines += [f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 + w}" y2="{y:.1f}" class="grid"/>', text(x0 - 10, y + 4, f"{value:g}", "tiny", "end")]


def load_model_divergence() -> str:
    witness = json.loads((ROOT / "experiments/generated/load-grounding-witnesses.json").read_text())
    rows = {row["family"]: row for row in witness["load_models"]["rows"]}
    continuation = witness["load_continuation"]["rows"]
    lines = shell("Same graph, different constitutive law", "The load model moves the operating point and the continuation boundary while topology, limits, and nominal demand stay fixed.", 1400, 900)
    lines += [f'<rect x="35" y="105" width="650" height="640" rx="14" class="panel"/>', f'<rect x="715" y="105" width="650" height="640" rx="14" class="panel"/>', text(65, 140, "A. Operating point at scale 1", "head"), text(745, 140, "B. Iteration-scoped continuation probe", "head")]
    x0, y0, w, h = 125, 205, 490, 365
    xmin, xmax, ymin, ymax = 0.82, 1.0, 0.75, 1.25
    axes(lines, x0, y0, w, h, xmin, xmax, ymin, ymax, "receiving voltage |Uᵣ| (p.u.)", "current magnitude |I| (p.u.)")
    # Smooth indicative curves derived from the declared scalar laws.
    s_nom = (0.9**2 + 0.25**2) ** 0.5
    curves = {"CP": "curve1", "CI": "curve2", "CZ": "curve3", "ZIP": "curve4"}
    for family, cls in curves.items():
        pts = []
        for k in range(41):
            v = xmin + (xmax - xmin) * k / 40
            ratio = v / 1.0
            if family == "CP": p, q = 0.9, 0.25
            elif family == "CI": p, q = 0.9 * ratio, 0.25 * ratio
            elif family == "CZ": p, q = 0.9 * ratio**2, 0.25 * ratio**2
            else: p, q = 0.9 * (0.4 * ratio**2 + 0.3 * ratio + 0.3), 0.25 * (0.2 * ratio**2 + 0.3 * ratio + 0.5)
            pts.append((v, (p * p + q * q) ** 0.5 / v))
        lines.append(plot_path(pts, x0, y0, w, h, xmin, xmax, ymin, ymax, cls))
    xv = x0 + (0.87 - xmin) / (xmax - xmin) * w
    yi = y0 + h - (1.0 - ymin) / (ymax - ymin) * h
    lines += [f'<line x1="{xv:.1f}" y1="{y0}" x2="{xv:.1f}" y2="{y0+h}" class="limit"/>', f'<line x1="{x0}" y1="{yi:.1f}" x2="{x0+w}" y2="{yi:.1f}" class="limit"/>', text(xv + 5, y0 + 16, "|Uᵣ| ≥ 0.87", "tiny"), text(x0 + w - 5, yi - 7, "|I| ≤ 1.00", "tiny", "end")]
    colors = {"CP": "red", "CI": "orange", "CZ": "green", "ZIP": "blue"}
    for family, row in rows.items():
        lines += [dot(row["voltage_magnitude_pu"], row["current_magnitude_pu"], x0, y0, w, h, xmin, xmax, ymin, ymax, colors[family]), text(x0 + (row["voltage_magnitude_pu"] - xmin) / (xmax - xmin) * w + 10, y0 + h - (row["current_magnitude_pu"] - ymin) / (ymax - ymin) * h - 9, family, "tiny")]
    x1, y1, w1, h1 = 805, 205, 490, 365
    xmin2, xmax2, ymin2, ymax2 = 0.2, 3.0, 0.45, 1.02
    axes(lines, x1, y1, w1, h1, xmin2, xmax2, ymin2, ymax2, "demand scale", "receiving voltage |Uᵣ| (p.u.)")
    for family, cls in curves.items():
        pts = [(r["scale"], r["voltage_magnitude_pu"]) for r in continuation if r["family"] == family]
        lines.append(plot_path(pts, x1, y1, w1, h1, xmin2, xmax2, ymin2, ymax2, cls if family != "CP" else "failed"))
    fail = next(r for r in continuation if r["family"] == "CP" and not r["converged"])
    lines += [dot(fail["scale"], fail["voltage_magnitude_pu"], x1, y1, w1, h1, xmin2, xmax2, ymin2, ymax2, "red"), text(x1 + (fail["scale"] - xmin2) / (xmax2 - xmin2) * w1 + 10, y1 + 25, "CP first failure: 1.8", "tiny")]
    for idx, (family, cls) in enumerate(curves.items()):
        lines += [f'<line x1="{70 + idx*120}" y1="665" x2="{100 + idx*120}" y2="665" class="{cls}"/>', text(108 + idx*120, 670, family, "small")]
    lines += [f'<rect x="35" y="780" width="1330" height="70" rx="10" class="orange"/>', text(55, 810, "Interpretation", "head"), text(185, 807, "The topology is unchanged. The constitutive law changes the feasible operating point and the iteration-scoped branch boundary;", "small"), text(185, 830, "this is not a universal load-model ranking or collapse theorem.", "small")]
    return finish(lines)


def source_pipeline() -> str:
    lines = shell("A source document becomes a graph only through ordered semantic gates", "The adapter publishes a canonical model, findings, and provenance before any graph quotient or solver view is derived.", 1400, 850)
    lines += [f'<rect x="35" y="105" width="1330" height="575" rx="14" class="panel"/>', text(65, 142, "semantic projection", "head"), text(65, 177, "P : D → (C, F, Π)", "body")]
    gates = [(80, 260, "1  schema", "fields and shapes", "malformed matrix"), (300, 260, "2  completeness", "required subtype data", "missing terminal map"), (520, 260, "3  domain", "plausible values", "negative rating"), (740, 260, "4  integrity", "references and dimensions", "missing bus"), (960, 260, "5  conformance", "study-specific rules", "bad grounding"), (1180, 260, "6  readiness", "well-posed decisions", "missing limit")]
    for x, y, title, detail, failure in gates:
        lines += [f'<rect x="{x}" y="{y}" width="180" height="170" rx="12" class="blue"/>', text(x + 90, y + 34, title, "head", "middle"), text(x + 90, y + 70, detail, "small", "middle"), f'<rect x="{x+18}" y="{y+102}" width="144" height="45" rx="8" class="red"/>', text(x + 90, y + 130, failure, "tiny", "middle")]
        if x < 1180:
            lines.append(f'<path d="M{x+180} {y+85} L{x+214} {y+85}" class="arrow"/>')
    lines += [f'<rect x="150" y="505" width="300" height="90" rx="12" class="green"/>', text(300, 540, "canonical typed model C", "head", "middle"), text(300, 570, "assets · terminals · factors · states", "small", "middle"), f'<rect x="550" y="505" width="300" height="90" rx="12" class="orange"/>', text(700, 540, "findings ledger F", "head", "middle"), text(700, 570, "declared · derived · inferred · unsupported", "small", "middle"), f'<rect x="950" y="505" width="300" height="90" rx="12" class="green"/>', text(1100, 540, "provenance Π", "head", "middle"), text(1100, 570, "source maps · hashes · recovery", "small", "middle")]
    lines += [f'<rect x="35" y="710" width="1330" height="70" rx="10" class="orange"/>', text(55, 740, "Ordering rule", "head"), text(185, 740, "A later graph cannot repair a semantic failure that should have been caught at an earlier gate.", "body")]
    return finish(lines)


def impedance_ladder() -> str:
    lines = shell("Impedance fidelity is a guarded transformation path", "Each arrow adds a declared approximation or coordinate change; the matrix alone is not the complete electrical factor.", 1400, 850)
    lines += [f'<rect x="35" y="105" width="1330" height="500" rx="14" class="panel"/>', text(65, 142, "physical provenance → electrical relation → decision model", "head")]
    stages = [(65, "circuit primitive", "wire data · geometry\nearth · frequency", "blue"), (330, "conductor primitive", "R, X, shunt blocks\nordered conductors", "blue"), (595, "phase view", "terminal maps\nneutral decision", "green"), (860, "sequence coordinates", "F invertible\nchannels may mix", "orange"), (1125, "restricted scalar", "D / F₁\npositive sequence", "red")]
    for x, title, detail, cls in stages:
        lines += [f'<rect x="{x}" y="245" width="210" height="150" rx="12" class="{cls}"/>', text(x + 105, 280, title, "head", "middle")]
        for idx, part in enumerate(detail.split("\n")):
            lines.append(text(x + 105, 320 + idx * 24, part, "small", "middle"))
    arrows = [(275, "K_g", "grounding / invertibility"), (540, "K_n / P_n", "neutral guard; possible loss"), (805, "F", "coordinate change"), (1070, "D / F₁", "sequence closure / restriction")]
    for x, label, guard in arrows:
        lines += [f'<path d="M{x} 320 L{x+55} 320" class="arrowo"/>', text(x + 27, 285, label, "small", "middle"), text(x + 27, 425, guard, "tiny", "middle")]
    lines += [f'<rect x="65" y="480" width="1270" height="78" rx="10" class="orange"/>', text(85, 513, "Loss ledger", "head"), text(215, 507, "neutral/common-mode coordinates, sequence coupling, phase-specific limits, shunt placement, and source geometry", "small"), text(215, 532, "are forgotten only when the guard and preservation target say so.", "small")]
    lines += [f'<rect x="35" y="655" width="1330" height="70" rx="10" class="green"/>', text(55, 685, "Reading rule", "head"), text(185, 685, "A positive-sequence edge is a derived view—not a primitive fact about the asset—and must retain its transformation path.", "body")]
    return finish(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = {
        "load-model-divergence.svg": load_model_divergence(),
        "source-canonical-pipeline.svg": source_pipeline(),
        "impedance-fidelity-ladder.svg": impedance_ladder(),
    }
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise SystemExit("rsvg-convert is required to create PNG companions")
    for name, content in outputs.items():
        svg = OUT / name
        png = OUT / name.replace(".svg", ".png")
        svg.write_text(content)
        subprocess.run([converter, "-o", str(png), str(svg)], check=True)
        print(f"wrote {svg}")
        print(f"wrote {png}")


if __name__ == "__main__":
    main()
