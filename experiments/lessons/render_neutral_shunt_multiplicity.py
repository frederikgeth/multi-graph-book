#!/usr/bin/env python3
"""Render the declared two-conductor observation diagram, without extra dependencies."""
import json
from pathlib import Path
from neutral_shunt_multiplicity import build, OUTPUT, ROOT


def main():
    if json.loads(OUTPUT.read_text())!=build():raise SystemExit('exact witness is stale')
    s=['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="600" viewBox="0 0 1280 600">',
       '<title>Explicit neutral, coupled series element, and separately declared shunts</title>',
       '<desc>A two-conductor source at one and zero volts feeds a phase-neutral constant-power load. The coupled series resistance is one ohm on the diagonal and one half ohm off diagonal. A one tenth siemens source shunt, two sevenths siemens receiving phase-neutral shunt and one siemens neutral-earth shunt make source, series and load currents distinct. Current arrows indicate reference orientation, not actual positive flow.</desc>',
       '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#17212b"/></marker></defs>',
       '<rect width="1280" height="600" fill="white"/>',
       '<g font-family="DejaVu Sans, sans-serif" font-size="20" fill="#17212b">']
    def text(x,y,t,size=20,anchor='start'):s.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{t}</text>')
    def line(x1,y1,x2,y2,dash=False,arrow=False):s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#17212b" stroke-width="2.5"'+(' stroke-dasharray="6 5"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
    def rect(x,y,w,h):s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="#17212b" stroke-width="2.5"/>')
    def dot(x,y):s.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#17212b"/>')
    def ground(x,y):
        for dy,w in [(0,22),(7,15),(14,7)]:line(x-w,y+dy,x+w,y+dy)
    text(30,40,'Same circuit, different current observations',28)
    text(30,77,'Native series-line ratings apply between the shunt connections. Arrows define signed references.',19)
    for y in (170,390):
        line(100,y,1110,y)
        for x in (100,260,800,925,1110):dot(x,y)
    # Voltage source and its ideal earth reference.
    line(100,170,100,242);line(100,318,100,485)
    s.append('<circle cx="100" cy="280" r="38" fill="white" stroke="#17212b" stroke-width="2.5"/>')
    text(100,272,'+',24,'middle');text(100,304,'−',24,'middle');text(32,285,'1 V',19)
    ground(100,485)
    text(60,135,'f:a = 1 V');text(40,425,'f:n = 0 V')
    text(140,472,'Earth reaction is separate',17)
    # Explicit source and receiving shunts.
    for x,label in ((260,'1/10 S'),(800,'2/7 S')):
        line(x,170,x,240);rect(x-15,240,30,70);line(x,310,x,390)
        text(x+28,279,label)
    # Coupled series element; dashed link is coupling, not a third wire.
    for y in (170,390):rect(475,y-15,60,30);text(505,y+7,'1 Ω',17,'middle')
    line(505,200,505,350,dash=True)
    text(540,267,'Mutual R = 1/2 Ω',18);text(540,293,'(not another wire)',16)
    # Differential load and finite neutral-earth conductance.
    line(1110,170,1110,240);rect(1050,240,120,80);line(1110,320,1110,390)
    text(1110,271,'Coil load',18,'middle');text(1110,301,'6/35 W',18,'middle')
    line(925,390,925,450);rect(910,450,30,50);line(925,500,925,530);ground(925,530)
    text(955,480,'1 S to earth')
    text(725,135,'t:x = v_a');text(700,425,'t:n = v_n ≠ 0')
    # Three distinct current observations; return orientation remains from→to.
    line(125,150,215,150,arrow=True);text(158,128,'I_s',20)
    line(350,145,430,145,arrow=True);text(380,125,'I_a',20)
    line(350,365,430,365,arrow=True);text(380,345,'I_n',20)
    line(1200,210,1200,285,arrow=True);text(1220,255,'j',22)
    text(30,574,'Low root: |I_n| = 24/35 A > 1/2 A, while both neutral power caps pass.',21)
    s.extend(['</g>','</svg>'])
    (ROOT/'docs/src/assets/neutral-shunt-multiplicity.svg').write_text('\n'.join(s)+'\n')
if __name__=='__main__':main()
