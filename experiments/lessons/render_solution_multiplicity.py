#!/usr/bin/env python3
"""Render the three mathematical mechanisms. Optional dependency: matplotlib==3.10.8.

Run the dependency-free solution_multiplicity.py --check first. Plot curves are
visual aids; the exact artifact, not sampled pixels, establishes the finite results.
"""
import json
from fractions import Fraction
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from solution_multiplicity import build, OUTPUT, ROOT


def main():
    exact=build()
    if json.loads(OUTPUT.read_text())!=exact:
        raise SystemExit('exact artifact is stale')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
        'svg.fonttype':'none','svg.hashsalt':'solution-multiplicity-v1',
        'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,3,figsize=(15,5.4))
    fig.subplots_adjust(left=.055,right=.985,bottom=.28,top=.78,wspace=.34)
    fig.suptitle('Three different reasons for multiple solutions',x=.055,ha='left',fontsize=20,fontweight='bold',y=.97)
    fig.text(.055,.88,'Same equations, changed limits  •  Lost current selection  •  Lost physical equation',fontsize=12)
    b=exact['inputs']['branch']; e,r,p,nom,lim=(float(Fraction(b[k])) for k in
        ('source_voltage','resistance','load_power','nominal_voltage','current_limit'))
    v=np.linspace(.01,e,500); ax=axes[0]
    ax.plot(v,(e-v)/r,color='#17212b',label='Ohm law',lw=2)
    ax.plot(v,p/v,color='#245b7a',label='Constant-power load',lw=2,ls='--')
    ax.axhline(lim,color='#17212b',ls=':',lw=2,label='Current cap')
    ax.plot(v,np.minimum(nom*lim/e,nom*lim/v),color='#696969',ls='-.',label='Both-end power caps')
    ax.axhspan(lim,nom*lim/e,facecolor='#eeeeee',edgecolor='#aaaaaa',hatch='///',linewidth=0,zorder=0)
    ax.scatter([.2],[.6],marker='x',s=90,color='#17212b',zorder=4)
    ax.scatter([.6],[.2],marker='o',s=65,facecolors='white',edgecolors='#17212b',zorder=4)
    ax.annotate('MVA only',(.2,.6),(.25,.72),fontsize=10,arrowprops={'arrowstyle':'-','color':'#555555'})
    ax.annotate('Both limits',(.6,.2),(.40,.06),fontsize=10,arrowprops={'arrowstyle':'-','color':'#555555'})
    ax.set(xlim=(0,.8),ylim=(0,.85),xlabel='Receiving voltage (p.u.)',ylabel='Current (p.u.)',title='A. Two roots; one current-admissible')
    ax.legend(loc='upper right',bbox_to_anchor=(1,-.24),ncol=2,fontsize=8,frameon=False)
    ax=axes[1]
    ax.axhline(0,color='#777777',lw=1)
    ax.annotate('',xy=(15,0),xytext=(-3,0),arrowprops={'arrowstyle':'<->','color':'#17212b','lw':1.5})
    ax.plot([2,7],[0,0],color='#245b7a',lw=9,solid_capstyle='butt')
    ax.plot([2,2],[-.11,.11],color='#17212b');ax.plot([7,7],[-.11,.11],color='#17212b')
    ax.text(4.5,-.24,'Current-admissible interval [2, 7]',ha='center',fontsize=10)
    for a,label,y,marker in [(4,'Finite ratio 2:1',.7,'v'),(6,'Minimum norm',.4,'*'),(8,'Finite ratio 1:2',1.,'^')]:
        ax.plot([a,a],[0,y-.08],color='#777777',ls=':',lw=1)
        ax.scatter([a],[y],color='#17212b',marker=marker,s=75)
        ax.text(a+.45,y,label,va='center',fontsize=9)
    ax.text(5.8,-.65,'Power caps allow every real α.\nCurrent caps bound it; they do not select it.',ha='center',fontsize=10)
    ax.set(xlim=(-3,15),ylim=(-.8,1.2),xlabel='First neutral-path current α (A)',title='B. A continuum of current splits')
    ax.set_yticks([]);ax.spines['left'].set_visible(False)
    ax=axes[2];v=np.linspace(0,1.4,400)
    ax.plot(v,v-1,color='#245b7a',ls='--',lw=2,label='Original current residual')
    ax.plot(v,v*(v-1),color='#17212b',lw=2,label='Power-product residual')
    ax.axhline(0,color='#888888',lw=1)
    ax.scatter([0],[0],color='#17212b',marker='x',s=85,zorder=5,clip_on=False)
    ax.scatter([1],[0],facecolors='white',edgecolors='#17212b',s=65,zorder=5)
    ax.scatter([0],[-1],color='#245b7a',marker='s',s=40,clip_on=False)
    ax.annotate('Spurious root',xy=(0,0),xytext=(.08,.32),fontsize=10,arrowprops={'arrowstyle':'-','color':'#555555'})
    ax.text(.06,-.95,'Current mismatch = −1',fontsize=10)
    ax.set(xlim=(0,1.4),ylim=(-1.1,.6),xlabel='Voltage (p.u.)',ylabel='Residual (p.u.; separate equations)',title='C. A root of the wrong equation')
    ax.legend(loc='upper right',bbox_to_anchor=(1,-.24),fontsize=8,frameon=False)
    for ax in axes:
        ax.tick_params(labelsize=9)
    out=ROOT/'docs/src/assets/solution-multiplicity'
    fig.savefig(out.with_suffix('.png'),dpi=160,metadata={'Software':'matplotlib '+matplotlib.__version__})
    fig.savefig(out.with_suffix('.svg'),metadata={'Date':None})
    svg=out.with_suffix('.svg'); text=svg.read_text()
    text=re.sub(r'(<svg\b[^>]*>)',r'\1\n<title>Three mechanisms of solution multiplicity</title>\n<desc>A: two circuit roots with one violating current limits despite passing power limits. B: a neutral circulation continuum bounded but not uniquely selected by current limits. C: multiplying KCL by voltage adds a zero-voltage root with nonzero current residual.</desc>',text,count=1)
    svg.write_text("\n".join(line.rstrip() for line in text.splitlines())+"\n")
    print('Rendered SVG and PNG; inspect labels and monochrome distinctions.')


if __name__=='__main__':
    main()
