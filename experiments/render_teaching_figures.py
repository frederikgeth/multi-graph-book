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


def outage():
    from lessons.practical_model_checks import Star, compile_star, source_currents, wrong_delete_triangle_edges, matrix_currents
    old, new = Star((1, 1, 1)), Star((1, 1, 0))
    base, rebuilt = compile_star(old), compile_star(new)
    wrong = wrong_delete_triangle_edges(base)
    volts = (1, 0, 0)
    d = Drawing('Opening this star arm changes the remaining equivalent',
                'An equal 1 S star reduces to a triangle with 1/3 S edges. Opening source arm c and rebuilding gives 1/2 S between a and b, with c isolated. Deleting triangle edges instead leaves the wrong 1/3 S. At boundary voltages (1,0,0) V, the correct current at a is 1/2 A, not 1/3 A.', 830)
    d.text(30, 79, 'Three boundary terminals; a zero-injection center; no shunts. Conductances in siemens.', 'small')
    d.text(40, 127, '1. Source: all three arms are 1 S', 'head')
    d.text(605, 127, '2. Eliminate the center', 'head')

    def network(x, y, reduced=False, opened=False):
        a, b, c, n = (x-160,y), (x+160,y), (x,y+150), (x,y+62)
        if reduced:
            d.line(*a,*b, BLUE)
            if not opened:
                d.line(*a,*c,BLUE);d.line(*b,*c,BLUE)
            g = -rebuilt.matrix_S[0][1] if opened else -base.matrix_S[0][1]
            d.text(x,y-17,f'{g} S',anchor='middle')
            if not opened:
                d.text(x-143,y+110,f'{g} S',anchor='middle')
                d.text(x+143,y+110,f'{g} S',anchor='middle')
        else:
            d.line(*a,*n,BLUE);d.line(*b,*n,BLUE)
            if opened:
                d.line(n[0],n[1]+18,n[0],n[1]+35,BLUE)
                d.line(c[0],c[1]-18,c[0],c[1]-45,BLUE)
                d.line(n[0],n[1]+35,n[0]+25,n[1]+50,INK)
                d.text(x+40,y+115,'open', 'small')
            else:
                d.line(*n,*c,BLUE)
            d.node(*n,'n',ORANGE)
        for point, label in [(a,'a'),(b,'b'),(c,'c')]:d.node(*point,label)
        if reduced and opened:d.text(x+35,y+157,'isolated', 'small')
    network(245,180)
    network(835,180,True)
    d.line(466,257,595,257,arrow=True)
    d.text(40,395,'3. Open source arm n–c', 'head')
    d.text(605,395,'4. Rebuild from the edited source', 'head')
    network(245,452,opened=True)
    network(835,452,True,True)
    d.line(466,524,595,524,arrow=True)
    d.text(40,665,'Tempting edit: delete triangle edges a–c and b–c.', 'head')
    d.text(40,703,f'It leaves a–b at {-wrong.matrix_S[0][1]} S. Symmetry and zero row sums still hold.')
    d.text(40,754,f'At (U_a,U_b,U_c) = (1,0,0) V: rebuilt I_a = {source_currents(new,volts)[0]} A;', 'math')
    d.text(40,792,f'wrong deletion I_a = {matrix_currents(wrong,volts)[0]} A. Recover source currents to distinguish them.', 'math')
    return d.finish()


def stamping():
    from lessons.assemble_network import assemble, BRANCHES
    order, permuted = ('s','m','t'), ('t','s','m')
    local = assemble(('s','m'), load=F(0), load_node='s', branches=BRANCHES[:1])
    y, yp = assemble(order), assemble(permuted)
    d = Drawing('One branch stamp, two array orderings',
                'Branch e1 joins s to m with conductance 2 S and local stamp [[2,-2],[-2,2]]. With e2 of 1 S and a shunt load of 1/2 S at t, the assembled matrix is shown in orders (s,m,t) and (t,s,m). Highlighted cells receive the e1 contribution; their final values include other stamps.', 775)
    d.text(30,80,'Fixed resistive lesson. Labels identify nodes; array positions follow the declared order.', 'small')
    d.text(40,123,'Equipment and terminal order', 'head')
    d.line(75,206,415,206,BLUE)
    for x,n in [(75,'s'),(245,'m'),(415,'t')]:d.node(x,206,n)
    d.text(160,180,'e1: 2 S',anchor='middle');d.text(330,180,'e2: 1 S',anchor='middle')
    d.text(75,250,'U_s = 12 V', 'small', 'middle')
    d.line(415,225,415,258,BLUE)
    d.box(404,258,22,32,'white',BLUE)
    d.line(415,290,415,316,BLUE)
    for i,w in enumerate([36,24,12]):d.line(415-w/2,316+6*i,415+w/2,316+6*i)
    d.text(382,282,'1/2 S', 'small', 'end')
    d.text(40,349,'The load shunt attaches to t and the reference.', 'small')

    def matrix(x,y,values,labels,highlight=()):
        size=54
        for j,n in enumerate(labels):d.text(x+j*size+size/2,y-12,n,anchor='middle')
        for i,(label,row) in enumerate(zip(labels,values)):
            d.text(x-16,y+i*size+35,label,anchor='end')
            for j,value in enumerate(row):
                fill='#e5f2f8' if (i,j) in highlight else 'white'
                d.box(x+j*size,y+i*size,size,size,fill,'#a5afb8')
                d.text(x+j*size+size/2,y+i*size+35,str(value),'math','middle')
        if highlight:
            lo_i, hi_i = min(i for i,j in highlight), max(i for i,j in highlight)
            lo_j, hi_j = min(j for i,j in highlight), max(j for i,j in highlight)
            d.parts.append(f'<rect x="{x+lo_j*size}" y="{y+lo_i*size}" width="{(hi_j-lo_j+1)*size}" height="{(hi_i-lo_i+1)*size}" fill="none" stroke="{INK}" stroke-width="3"/>')
    d.text(610,123,'Local stamp of e1 [S]', 'head')
    matrix(698,168,local,('s','m'))
    d.text(600,314,'+2 on its two diagonal positions;', 'small')
    d.text(600,344,'−2 on its two off-diagonal positions.', 'small')
    d.line(30,379,1060,379,width=1)
    d.text(40,423,'Y [S] in order (s, m, t)', 'head')
    d.text(615,423,'Y′ [S] in order (t, s, m)', 'head')
    matrix(157,468,y,order,tuple((i,j) for i in [0,1] for j in [0,1]))
    matrix(728,468,yp,permuted,tuple((i,j) for i in [1,2] for j in [1,2]))
    d.line(382,550,648,550,arrow=True)
    d.text(515,521,'Y′ = P Y Pᵀ','math','middle')
    d.text(515,589,'U′ = P U','math','middle')
    d.text(40,688,'Outlined, shaded cells receive the e1 stamp. Displayed entries are the assembled totals.', 'small')
    d.text(40,727,'The m diagonal is 3 S because e1 contributes 2 S and e2 contributes 1 S.', 'small')
    return d.finish()


def multipliers():
    from lessons.practical_model_checks import dispatch, duplicate_kkt
    import math
    d = Drawing('Same dispatch; scaled or nonunique multipliers',
                'Left: for c=50, d=10, beta=1, raw multipliers are 50/alpha, while mapped physical demand sensitivity remains 50. Right: duplicating the unscaled constraint gives all nonnegative multiplier pairs summing to 50, including (0,50), (20,30) and (50,0).', 710)
    d.text(30,80,'min βcp subject to α(d−p) ≤ 0; c = 50, d = 10, α > 0. Here β = 1.', 'math')
    d.text(40,128,'Constraint scaling', 'head')
    d.text(620,128,'Duplicate the unscaled constraint', 'head')
    left,right,top,bottom = 90,460,212,495
    xx=lambda a:left+math.log10(float(a))*(right-left)/2
    yy=lambda v:bottom-float(v)*(bottom-top)/50
    d.line(left,bottom,right+24,bottom,arrow=True,width=1.5)
    d.line(left,bottom,left,top-25,arrow=True,width=1.5)
    for v in [0,25,50]:
        d.line(left-5,yy(v),left,yy(v),width=1)
        d.text(left-12,yy(v)+6,v,'small','end')
    d.text(40,175,'Numerical value in these conventions', 'small')
    # The plotted curve is evaluated by the analytical lesson, not a freehand spline.
    samples=[F(str(10**(2*i/80))) for i in range(81)]
    for a,b in zip(samples,samples[1:]):
        d.line(xx(a), yy(dispatch(50,10,alpha=a)['raw_multiplier']), xx(b), yy(dispatch(50,10,alpha=b)['raw_multiplier']), BLUE, width=2.5)
    d.line(left,yy(50),right,yy(50),ORANGE,dash=True)
    for a in [1,10,100]:
        r=dispatch(50,10,alpha=a)
        d.circle(xx(a),yy(r['raw_multiplier']),5,BLUE,BLUE)
        d.text(xx(a),bottom+28,a,'small','middle')
    d.text(280,yy(5)-17,'λ′ = 5 at α = 10','small','middle')
    d.text(460,yy(F(1,2))-24,'λ′ = 1/2','small','middle')
    d.text(265,yy(50)-17,'αλ′ = 50','math','middle')
    d.text(270,550,'α (log scale)', 'small','middle')
    d.text(40,597,'Solid: raw λ′. Dashed: mapped sensitivity.', 'small')
    d.text(40,630,'For β ≠ 1, map back using (α/β)λ′.', 'small')
    x0,y0,s=675,495,5.5
    x=lambda v:x0+float(v)*s
    y=lambda v:y0-float(v)*s
    d.line(x0,y0,x(57),y0,arrow=True,width=1.5)
    d.line(x0,y0,x0,y(57),arrow=True,width=1.5)
    d.line(x(0),y(50),x(50),y(0),BLUE,width=3)
    for v in [0,25,50]:
        d.line(x(v),y0,x(v),y0+5,width=1);d.text(x(v),y0+28,v,'small','middle')
        if v:d.text(x0-12,y(v)+6,v,'small','end')
    for a,b,tx,ty in [(0,50,712,225),(20,30,798,310),(50,0,958,470)]:
        assert duplicate_kkt(50,10,10,(a,b))
        d.circle(x(a),y(b),5,BLUE,BLUE);d.text(tx,ty,f'({a},{b})','small')
    d.text(x0+12,175,'λ₂','math')
    d.text(995,532,'λ₁','math')
    d.text(815,565,'λ₁ + λ₂ = 50; λ ≥ 0','math','middle')
    d.text(620,597,'Each point satisfies KKT at p = 10.', 'small')
    d.text(620,630,'Common demand sensitivity is the sum.', 'small')
    d.text(30, 679, 'p,d in MW; c and the mapped demand sensitivity in currency/MWh; objective in currency/hour.', 'small')
    return d.finish()


FIGURES = {'start-here-same-ybus': parallel, 'parallel-feasible-set-card': geometry,
           'recovery-map-loop': recovery, 'orientation-power-transfer': orientation,
           'practical-outage-reduction': outage, 'equipment-matrix-stamp': stamping,
           'practical-multiplier-maps': multipliers}


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
