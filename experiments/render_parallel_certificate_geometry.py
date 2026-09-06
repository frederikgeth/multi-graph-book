#!/usr/bin/env python3
"""Render the maintained geometry and decision-gap plate for parallel cases."""

from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/src/assets"


def esc(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x: float, y: float, value: object, cls: str = "body", anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


STYLE = """
<style>
text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:28px;font-weight:bold}
.sub{font-size:16px;fill:#5f6b76}.head{font-size:19px;font-weight:bold}
.body{font-size:15px}.small{font-size:13px;fill:#5f6b76}.tiny{font-size:12px;fill:#5f6b76}
.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.grid{stroke:#c7d0d8;stroke-width:1;stroke-dasharray:4 4}
.axis{stroke:#17212b;stroke-width:2}.retained{fill:#d9eef8;stroke:#245b7a;stroke-width:3}
.candidate{fill:none;stroke:#8a3232;stroke-width:3;stroke-dasharray:8 5}.map{stroke:#477a55;stroke-width:3;fill:none;marker-end:url(#arrow)}
.exact{fill:#477a55}.naive{fill:#8a3232}.limit{stroke:#8a3232;stroke-width:2;stroke-dasharray:6 5}
</style>
"""


def main() -> None:
    four = json.loads((ROOT / 'experiments/generated/four-wire-parallel-ac-certificate.json').read_text())['evidence']
    multi = json.loads((ROOT / 'experiments/generated/multiconductor-parallel-ac-certificate.json').read_text())['evidence']
    phase_a = next(c for c in four['redundancy']['checks'] if c['conductor'] == 'a')
    bound, rating = phase_a['exact_worst_case_magnitude'], phase_a['candidate_limit']
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="820" viewBox="0 0 1400 820">',
        '<title>Parallel redundancy certificate geometry and decision gap</title>',
        '<desc>Left: the phase-a candidate-current bound and rating use one current scale, read from the four-wire certificate. Right: exact and naive served fractions for two multiconductor parallel cases.</desc>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#477a55"/></marker></defs>',
        '<rect width="100%" height="100%" fill="white"/>', STYLE,
        t(35, 40, "A certificate has geometry—and a decision consequence", "title"),
        t(35, 68, "The row-norm bound is the bridge from retained member limits to a safe deletion; the bar chart shows what goes wrong when that bridge is replaced by a summed limit.", "sub"),
        '<rect x="35" y="105" width="650" height="620" rx="14" class="panel"/>',
        '<rect x="715" y="105" width="650" height="620" rx="14" class="panel"/>',
        t(65, 142, "A. Candidate current: certified disc", "head"),
        t(745, 142, "B. Served-fraction consequence", "head"),
    ]
    # One current plane and one scale; the inner disc bounds candidate current.
    cx, cy, scale = 300, 420, 250
    lines += [f'<line x1="{cx-scale}" y1="{cy}" x2="{cx+scale}" y2="{cy}" class="axis"/>',
              f'<line x1="{cx}" y1="{cy-185}" x2="{cx}" y2="{cy+scale}" class="axis"/>',
              f'<circle cx="{cx}" cy="{cy}" r="{rating*scale:.1f}" class="candidate"/>',
              f'<circle cx="{cx}" cy="{cy}" r="{bound*scale:.1f}" class="retained"/>',
              t(65, 185, f"Phase a: rating {rating:.2f} p.u. (dashed)", "body"),
              t(65, 215, f"Recovered current bound {bound:.4f} p.u. (solid)", "body"),
              t(cx + 10, cy - scale + 95, "Im I₂a [p.u.]", "small"), t(cx + scale - 20, cy + 28, "Re I₂a [p.u.]", "small", "end"),
              '<rect x="75" y="605" width="560" height="78" rx="10" fill="#e5f1e7" stroke="#477a55" stroke-width="2"/>',
              t(95, 632, f"Phase-a implication: {bound:.4f} < {rating:.2f}", "head"),
              t(95, 658, "The certificate checks every row under the fixed map.", "small")]
    # Bar chart.
    x0, y0, w, h = 815, 210, 500, 390
    maxv = 2.0
    for v in (0, 0.5, 1.0, 1.5, 2.0):
        y = y0 + h - v/maxv*h
        lines += [f'<line x1="{x0}" y1="{y:.1f}" x2="{x0+w}" y2="{y:.1f}" class="grid"/>', t(x0-10, y+4, f"{v:g}", "tiny", "end")]
    lines += [f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+h}" class="axis"/>',
              f'<line x1="{x0}" y1="{y0+h}" x2="{x0+w}" y2="{y0+h}" class="axis"/>',
              t(x0+w/2, y0+h+42, "served fraction alpha", "small", "middle"),
              t(x0+4, y0-15, "load served", "small")]
    rows = [(name, ev["exact_pruned_solution"]["objective_served_fraction"], ev["naive_aggregate_solution"]["objective_served_fraction"]) for name, ev in [("multiconductor", multi), ("four-wire", four)]]
    for idx, (label, exact, naive) in enumerate(rows):
        gx = x0 + 80 + idx*220
        for off, val, cls, name in ((-27, exact, "exact", "exact"), (27, naive, "naive", "naive sum")):
            bh = val/maxv*h
            lines += [f'<rect x="{gx+off-18}" y="{y0+h-bh:.1f}" width="36" height="{bh:.1f}" class="{cls}"/>',
                      t(gx+off, y0+h-bh-8, f"{val:.4f}", "tiny", "middle"),
                      t(gx+off, y0+h+20, name, "tiny", "middle")]
        lines += [t(gx, y0+h+72, label, "body", "middle")]
    lines += ['<rect x="745" y="738" width="590" height="70" rx="10" fill="#f8e1c4" stroke="#8a4f13" stroke-width="2"/>',
              t(765, 767, "The naive sum enlarges the feasible set", "head"),
              t(765, 792, "by replacing member limits with an uncertified sum.", "small"),
              '</svg>']
    svg = OUT / "parallel-redundancy-certificate.svg"
    png = OUT / "parallel-redundancy-certificate.png"
    svg.write_text("\n".join(lines) + "\n")
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise SystemExit("rsvg-convert is required to create PNG companions")
    subprocess.run([converter, "-o", str(png), str(svg)], check=True)
    print(f"wrote {svg}")
    print(f"wrote {png}")


if __name__ == "__main__":
    main()
