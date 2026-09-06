#!/usr/bin/env python3
"""Reproducible teaching diagrams. Numeric geometry comes from exact lesson data.

SVG is the maintained vector source; rsvg-convert supplies the PDF-safe PNG.
Legacy renderer entry points delegate here for figures replaced by this pass.
"""
from fractions import Fraction as F
from html import escape
from pathlib import Path
import argparse
import shutil
import subprocess

from lessons.parallel_members import evaluate

ASSETS = Path(__file__).resolve().parents[1] / 'docs/src/assets'
INK, BLUE, ORANGE, RED = '#17212b', '#245b7a', '#8a4f13', '#8a3232'


class Drawing:
    def __init__(self, title, desc, height=650, width=1100):
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                      f'<title>{escape(title)}</title><desc>{escape(desc)}</desc>',
                      f'<rect width="{width}" height="{height}" fill="white"/>',
                      '<style>text{font-family:Arial,sans-serif;fill:#17212b;font-size:20px}.title{font-size:29px;font-weight:bold}.head{font-size:23px;font-weight:bold}.small{font-size:18px}.math{font-family:DejaVu Sans,Arial,sans-serif;font-size:22px}</style>',
                      '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#17212b"/></marker></defs>']
        self.text(30, 43, title, 'title')

    def text(self, x, y, value, cls='', anchor='start'):
        self.parts.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{escape(str(value))}</text>')

    def line(self, x1, y1, x2, y2, color=INK, dash=False, arrow=False, width=3):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'
                          + (' stroke-dasharray="9 6"' if dash else '')
                          + (' marker-end="url(#arrow)"' if arrow else '') + '/>')

    def box(self, x, y, w, h, fill='#f7fafc', color=INK):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{color}" stroke-width="2"/>')

    def circle(self, x, y, radius, color=BLUE, fill='white', dash=False):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" stroke="{color}" stroke-width="3"' + (' stroke-dasharray="9 6"' if dash else '') + '/>')

    def node(self, x, y, label, color=BLUE):
        self.circle(x, y, 18, color)
        self.text(x, y+7, label, anchor='middle')

    def finish(self):
        return '\n'.join(self.parts + ['</svg>']) + '\n'


def parallel_data():
    drop = F(15)
    result = evaluate(drop, F(100))
    total_g = result['aggregate_current']/drop
    return drop, result, total_g


def parallel():
    drop, r, g = parallel_data()
    d = Drawing('Same terminal law; different admissible currents',
                'Two resistive parallel members have conductances 10 S and 1 S and limits 100 A each. At a 15 V drop the total current is 165 A, but the first member carries 150 A and violates its rating.', 590)
    d.text(30, 78, 'Fixed resistive branches; no shunts. Current reference is from i to j.', 'small')
    d.text(40, 124, 'Source: retain both member limits', 'head')
    d.text(605, 124, 'Target: sum conductance and ratings', 'head')
    for y in (205, 300):
        d.line(85, 250, 85, y, BLUE)
        d.line(85, y, 485, y, BLUE)
        d.line(485, y, 485, 250, BLUE)
    d.node(85, 250, 'i'); d.node(485, 250, 'j')
    d.text(285, 188, 'ℓ₁: 10 S, limit 100 A', anchor='middle')
    d.text(285, 333, 'ℓ₂: 1 S, limit 100 A', anchor='middle')
    d.line(650, 250, 1010, 250, BLUE)
    d.node(650, 250, 'i'); d.node(1010, 250, 'j')
    d.text(830, 204, f'{g} S, summed limit {r["summed_rating"]} A', anchor='middle')
    d.text(830, 304, 'I = 11 ΔU in both models', 'math', 'middle')
    d.text(40, 387, f'At ΔU = {drop} V:', 'head')
    d.text(40, 425, f'I₁ = {r["currents"]["first"]} A > 100 A: FAIL')
    d.text(40, 458, f'I₂ = {r["currents"]["second"]} A ≤ 100 A: PASS')
    d.text(605, 425, f'I = {r["aggregate_current"]} A ≤ {r["summed_rating"]} A: PASS')
    d.text(605, 458, 'The aggregate check misses the member violation.')
    d.text(30, 530, f'Repair for this fixed member set: total-current cap {r["exact_rating"]} A; recover each member current.')
    d.text(30, 565, 'A declared-limit violation does not predict conductor temperature or melting.', 'small')
    return d.finish()


def geometry():
    drop, r, g = parallel_data()
    d = Drawing('One voltage-drop plane, two feasible regions',
                'Concentric discs in volts: retained member constraints give radius 10 V; the summed-rating target gives radius 200/11 V. The point (15,0) V lies outside the source and inside the target.', 650)
    d.text(30, 78, 'Complex ΔU; fixed scalar conductances and current-magnitude bounds.', 'small')
    cx, cy, scale = 320, 348, 11
    x, y = lambda v: cx+float(v)*scale, lambda v: cy-float(v)*scale
    source_radius, target_radius = r['drop_cap'], r['summed_rating']/g
    d.circle(cx, cy, float(target_radius)*scale, ORANGE, '#fff7ec', True)
    d.circle(cx, cy, float(source_radius)*scale, BLUE, '#e5f2f8')
    d.line(x(-22), cy, x(22), cy, arrow=True, width=1.5)
    d.line(cx, y(-21), cx, y(22), arrow=True, width=1.5)
    for v in (-20, -10, 10, 20):
        d.line(x(v), cy-5, x(v), cy+5, width=1)
        d.text(x(v), cy+27, v, 'small', 'middle')
        d.line(cx-5, y(v), cx+5, y(v), width=1)
        d.text(cx-12, y(v)+6, v, 'small', 'end')
    d.text(560, cy+55, 'Re ΔU [V]', 'small', 'end')
    d.text(cx+12, 115, 'Im ΔU [V]', 'small')
    d.circle(x(drop), y(0), 6, RED, RED)
    d.line(x(drop), cy-8, 580, 245, RED, width=1.5)
    d.text(600, 160, 'Solid boundary: source', 'head')
    d.text(600, 198, f'|ΔU| ≤ {source_radius} V', 'math')
    d.text(600, 269, f'Witness: ({drop}, 0) V', 'head')
    d.text(600, 307, 'Member 1 fails; aggregate passes.')
    d.text(600, 390, 'Dashed boundary: naive target', 'head')
    d.text(600, 428, '|ΔU| ≤ 200/11 V ≈ 18.18 V', 'math')
    d.text(30, 602, 'Both discs and the witness use the same scale. The extra annulus contains false acceptances.', 'small')
    return d.finish()


def recovery():
    d = Drawing('Recovery proves one inclusion; exactness needs both',
                'First obtain a target feasible point, recover source variables, and check source equations, constraints and matched observations. This gives target-observation inclusion. Exact observed-set equality also requires coverage of every source observation.', 625)
    d.text(30, 81, 'S and T are feasible sets; h and ĥ map them into the same joint observation space.', 'small')
    for x, head, body in [(35, '1. Target point', 'x̂ ∈ T'), (380, '2. Recover', 'z = R(x̂)'), (725, '3. Check source', 'z ∈ S; h(z) = ĥ(x̂)')]:
        d.box(x, 130, 310, 115)
        d.text(x+155, 167, head, 'head', 'middle')
        d.text(x+155, 214, body, 'math', 'middle')
    d.line(349, 187, 373, 187, arrow=True)
    d.line(694, 187, 718, 187, arrow=True)
    d.text(35, 300, 'If this succeeds for EVERY target feasible point:', 'head')
    d.text(70, 344, 'ĥ(T) ⊆ h(S)', 'math')
    d.text(330, 344, 'A conservative target may still exclude valid source observations.')
    d.text(35, 410, 'Also show coverage of EVERY source feasible observation:', 'head')
    d.text(70, 454, 'h(S) ⊆ ĥ(T)', 'math')
    d.text(330, 454, 'Together, the two inclusions give ĥ(T) = h(S).')
    d.text(35, 521, 'Checking one returned solution establishes only that point’s recovery obligations.', 'small')
    d.text(35, 555, 'Without a retained recovery relation or other evidence, source constraints may remain unassessed.', 'small')
    d.text(35, 589, 'Decision equivalence also requires the declared decision and objective mappings.', 'small')
    return d.finish()


def orientation():
    d = Drawing('Reference orientation and active-power sign are separate',
                'For a series-only scalar branch, the stored current reference runs from i to j. Active power entering the branch at terminal i may be positive or negative at different operating points. Reactive power has a separate sign; complex power is not ordered.', 560)
    d.text(30, 80, 'Scalar series-only branch: no shunts, taps or internal current injection.', 'small')
    d.text(40, 125, 'Stored current reference', 'head')
    d.text(590, 125, 'Active power at terminal i', 'head')
    for x in (80, 635):
        d.line(x, 245, x+350, 245, BLUE)
        d.node(x, 245, 'i'); d.node(x+350, 245, 'j')
    d.line(165, 210, 355, 210, arrow=True)
    d.text(260, 188, 'I: i → j', 'math', 'middle')
    d.text(40, 311, 'Currents entering the branch: I at i, −I at j.')
    d.text(40, 347, 'Reversing the reference gives I′ = −I.')
    d.text(590, 182, 'Sᵢ = Uᵢ conj(I) = Pᵢ + jQᵢ', 'math')
    d.line(710, 210, 900, 210, arrow=True)
    d.text(790, 308, 'Pᵢ > 0: active power enters at i', anchor='middle')
    d.line(900, 350, 710, 350, dash=True, arrow=True)
    d.text(790, 389, 'Pᵢ < 0: active power leaves at i', anchor='middle')
    d.text(30, 465, 'The two signs refer to different operating points. Qᵢ has its own sign; do not write Sᵢ > 0.', 'small')
    d.text(30, 504, 'With losses, powers entering at the two terminals need not be negatives of one another.', 'small')
    return d.finish()


FIGURES = {'start-here-same-ybus': parallel, 'parallel-feasible-set-card': geometry,
           'recovery-map-loop': recovery, 'orientation-power-transfer': orientation}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('names', nargs='*', choices=list(FIGURES))
    args = parser.parse_args()
    converter = shutil.which('rsvg-convert')
    if not converter:
        raise SystemExit('rsvg-convert is required')
    for name in args.names or FIGURES:
        svg = ASSETS / f'{name}.svg'
        svg.write_text(FIGURES[name]())
        subprocess.run([converter, str(svg), '-o', str(svg.with_suffix('.png'))], check=True)
        print(f'rendered {name}')


if __name__ == '__main__':
    main()
