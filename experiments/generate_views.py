#!/usr/bin/env python3
"""Render six deliberately non-isomorphic views of the running network."""

import json
import hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data" / "running-network" / "v0.1.0.json"
OUTPUT = ROOT / "docs" / "src" / "assets" / "running-network-views.png"
SOURCE_MAP = ROOT / "experiments" / "generated" / "view-source-maps.json"
W, H, PW, PH = 2400, 1600, 800, 800
INK, MUTED, GRID = "#17212b", "#5f6b76", "#dce2e8"
BUS, LINE, XFMR, DEVICE, GROUND = "#d9eef8", "#3d78b5", "#d8892b", "#7856a8", "#477a55"


def getfont(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


TITLE, SUB, LABEL, SMALL, TINY = (
    getfont(34, True), getfont(21), getfont(22, True), getfont(18), getfont(15)
)


def panel(draw, col, row, title, subtitle):
    x0, y0 = col * PW, row * PH
    draw.rectangle((x0+12, y0+12, x0+PW-12, y0+PH-12), fill="white", outline=GRID, width=3)
    draw.text((x0+34, y0+28), title, fill=INK, font=TITLE)
    draw.text((x0+34, y0+72), subtitle, fill=MUTED, font=SUB)
    return x0, y0


def circle(draw, point, radius, text, fill=BUS, font=SMALL):
    x, y = point
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=fill, outline=INK, width=3)
    bounds = draw.textbbox((0, 0), text, font=font)
    draw.text((x-(bounds[2]-bounds[0])/2, y-(bounds[3]-bounds[1])/2-1), text, fill=INK, font=font)


def box(draw, point, size, text, fill="white", font=SMALL):
    x, y = point; w, h = size
    draw.rounded_rectangle((x-w/2, y-h/2, x+w/2, y+h/2), radius=10,
                           fill=fill, outline=INK, width=3)
    bounds = draw.textbbox((0, 0), text, font=font)
    draw.text((x-(bounds[2]-bounds[0])/2, y-(bounds[3]-bounds[1])/2-1), text, fill=INK, font=font)


def edge(draw, a, b, color=LINE, width=5):
    draw.line((*a, *b), fill=color, width=width)


def asset(draw, x0, y0):
    buses={"i0":(x0+70,y0+280),"i1":(x0+200,y0+280),"i2":(x0+390,y0+280),
           "i3":(x0+560,y0+280),"i4":(x0+710,y0+280),
           "i5":(x0+330,y0+540),"i6":(x0+560,y0+540)}
    assets={"w0":(x0+135,y0+280),"l1":(x0+295,y0+240),"l2":(x0+295,y0+320),
            "l3":(x0+475,y0+280),"l4":(x0+635,y0+280),"x1":(x0+435,y0+430),
            "d3":(x0+330,y0+640),"g1":(x0+560,y0+640)}
    pairs=[("i0","w0"),("w0","i1"),("i1","l1"),("l1","i2"),("i1","l2"),
           ("l2","i2"),("i2","l3"),("l3","i3"),("i3","l4"),("l4","i4"),
           ("i1","x1"),("x1","i5"),("x1","i6"),("i5","d3"),("i6","g1")]
    points={**buses,**assets}
    for a,b in pairs:
        if (a,b) == ('i1','x1'):
            # Route around l2: crossing its asset box falsely suggests attachment.
            elbow=(points[a][0], y0+405)
            edge(draw,points[a],elbow,MUTED,3); edge(draw,elbow,points[b],MUTED,3)
        else:
            edge(draw,points[a],points[b],MUTED,3)
    for ident,point in buses.items(): circle(draw,point,28,ident)
    for ident,point in assets.items():
        color="#f8e1c4" if ident=="x1" else "#eadff4" if ident in ("w0","g1") else "#e7f0fa"
        box(draw,point,(58,38),ident,fill=color,font=TINY)
    draw.text((x0+125,y0+710),"Lines and devices are vertices with stable identity.",fill=MUTED,font=SMALL)


def physical(draw, x0, y0, compact=False):
    p = {"i0": (x0+80,y0+280), "i1": (x0+205,y0+280), "i2": (x0+370,y0+280),
         "i3": (x0+535,y0+280), "i4": (x0+695,y0+280),
         "i5": (x0+340,y0+535), "i6": (x0+560,y0+535)}
    edge(draw,p["i0"],p["i1"],DEVICE)
    edge(draw,(p["i1"][0],p["i1"][1]-9),(p["i2"][0],p["i2"][1]-9))
    edge(draw,(p["i1"][0],p["i1"][1]+9),(p["i2"][0],p["i2"][1]+9))
    edge(draw,p["i2"],p["i3"]); edge(draw,p["i3"],p["i4"])
    for target in (p["i1"],p["i5"],p["i6"]): edge(draw,(x0+435,y0+435),target,XFMR)
    if not compact:
        box(draw,(x0+435,y0+435),(66,52),"x1",fill="#f8e1c4")
    for ident, point in p.items(): circle(draw,point,30,ident)
    draw.text((x0+270,y0+225),"l1",fill=LINE,font=SMALL)
    draw.text((x0+300,y0+300),"l2",fill=LINE,font=SMALL)
    draw.text((x0+460,y0+225),"l3",fill=LINE,font=SMALL)
    draw.text((x0+620,y0+225),"l4",fill=LINE,font=SMALL)
    if compact:
        box(draw,(x0+435,y0+435),(112,48),"x1*",fill="#f8e1c4",font=TINY)
        draw.text((x0+300,y0+620),"x1* = compiled star view; not a physical line",fill=INK,font=TINY)
    if not compact:
        box(draw,(x0+143,y0+245),(58,34),"w0",fill="#eadff4",font=TINY)
        box(draw,(x0+340,y0+625),(62,36),"d3",fill="#f1eafa",font=TINY)
        box(draw,(x0+560,y0+625),(62,36),"g1",fill="#eadff4",font=TINY)
        draw.text((x0+125,y0+690),"Stable physical identities own lifecycle facts.",fill=MUTED,font=SMALL)
    else:
        draw.text((x0+160,y0+680),"Parallel identity survives; conductor detail does not.",fill=MUTED,font=SMALL)


def terminal(draw, x0, y0):
    box(draw,(x0+190,y0+300),(260,170),"i3",fill=BUS,font=LABEL)
    box(draw,(x0+610,y0+300),(260,170),"i4",fill=BUS,font=LABEL)
    left={"a":(x0+300,y0+250),"c":(x0+300,y0+300),"n":(x0+300,y0+350)}
    right={"a":(x0+500,y0+250),"c":(x0+500,y0+300),"n":(x0+500,y0+350)}
    for name,point in left.items(): circle(draw,point,18,name,fill="white",font=TINY)
    for name,point in right.items(): circle(draw,point,18,name,fill="white",font=TINY)
    edge(draw,left["a"],right["c"],LINE,4); edge(draw,left["c"],right["a"],LINE,4)
    edge(draw,left["n"],right["n"],GROUND,4)
    draw.text((x0+370,y0+205),"l4",fill=LINE,font=LABEL)
    draw.text((x0+300,y0+430),"N_l4,i3 = [a,c,n]",fill=INK,font=SMALL)
    draw.text((x0+300,y0+470),"N_l4,i4 = [c,a,n]",fill=INK,font=SMALL)
    draw.text((x0+160,y0+580),"The crossing is data, not a drawing accident.",fill=MUTED,font=SMALL)


def factor(draw, x0, y0):
    js={"J_i1":(x0+120,y0+300),"J_i2":(x0+400,y0+300),"J_i3":(x0+680,y0+300),
        "J_i5":(x0+260,y0+590),"J_i6":(x0+540,y0+590)}
    fs={"Phi_l1":(x0+260,y0+245),"Phi_l2":(x0+260,y0+355),
        "Phi_l3":(x0+540,y0+300),"Phi_x1":(x0+400,y0+470)}
    for name in ("Phi_l1","Phi_l2"):
        edge(draw,js["J_i1"],fs[name],MUTED,3); edge(draw,fs[name],js["J_i2"],MUTED,3)
    edge(draw,js["J_i2"],fs["Phi_l3"],MUTED,3); edge(draw,fs["Phi_l3"],js["J_i3"],MUTED,3)
    for name in ("J_i1","J_i5","J_i6"):
        if name == 'J_i1':
            elbow=(js[name][0], y0+460)
            edge(draw,fs['Phi_x1'],elbow,XFMR,4); edge(draw,elbow,js[name],XFMR,4)
        else:
            edge(draw,fs['Phi_x1'],js[name],XFMR,4)
    for name,point in js.items(): circle(draw,point,37,name,fill="#e4f4e7",font=TINY)
    for name,point in fs.items(): box(draw,point,(110,52),name,fill="#f8e1c4",font=TINY)
    draw.text((x0+230,y0+680),"Factor arity is not forced to two.",fill=MUTED,font=SMALL)


def opf(draw, x0, y0):
    variables=[(x0+110,y0+250,"U_i"),(x0+110,y0+370,"I_lij"),(x0+110,y0+490,"P_g,Q_g")]
    constraints=[(x0+400,y0+220,"KCL"),(x0+400,y0+330,"device laws"),
                 (x0+400,y0+440,"limits"),(x0+400,y0+550,"state maps")]
    for vx,vy,_ in variables:
        for cx,cy,_ in constraints:
            if abs(vy-cy)<=150: edge(draw,(vx+48,vy),(cx-80,cy),MUTED,3)
    for cx,cy,_ in constraints: edge(draw,(cx+80,cy),(x0+600,y0+375),MUTED,3)
    for x,y,text in variables: circle(draw,(x,y),48,text,font=TINY)
    for x,y,text in constraints: box(draw,(x,y),(160,60),text,fill="#e9d5b5",font=TINY)
    box(draw,(x0+675,y0+375),(150,90),"min f(z)",fill="#eadff4",font=LABEL)
    draw.text((x0+130,y0+680),"Vertices may be variables and constraints, not assets.",fill=MUTED,font=SMALL)


def sparsity(draw, x0, y0):
    origin=(x0+170,y0+190); cell=34; n=13; groups=[0,3,6,9,11,13]
    for i in range(n+1):
        width=3 if i in groups else 1; color=MUTED if i in groups else GRID
        draw.line((origin[0],origin[1]+i*cell,origin[0]+n*cell,origin[1]+i*cell),fill=color,width=width)
        draw.line((origin[0]+i*cell,origin[1],origin[0]+i*cell,origin[1]+n*cell),fill=color,width=width)
    pattern={(i,i) for i in range(n)}
    for a,b in [(0,3),(1,4),(2,5),(3,6),(4,7),(5,8),(0,9),(1,9),(2,10),
                (6,9),(7,9),(8,10),(9,11),(9,12),(10,11),(10,12)]:
        pattern.update(((a,b),(b,a)))
    for row,col in pattern:
        cx=origin[0]+col*cell+cell/2; cy=origin[1]+row*cell+cell/2
        draw.ellipse((cx-7,cy-7,cx+7,cy+7),fill=LINE)
    for pos,text in [(1.5,"U"),(4.5,"I"),(7.5,"S"),(10,"x"),(12,"u")]:
        draw.text((origin[0]+pos*cell-8,origin[1]-35),text,fill=INK,font=SMALL)
        draw.text((origin[0]-34,origin[1]+pos*cell-10),text,fill=INK,font=SMALL)
    draw.text((x0+170,y0+680),"Nonzeros encode algebraic coupling only.",fill=MUTED,font=SMALL)


def source_objects(network):
    """Return canonical source IDs for every object represented by the fixture."""
    objects = []
    for family in ("bus", "line", "switch", "shunt", "load", "generator", "voltage_source"):
        objects.extend(f"{family}/{identifier}" for identifier in sorted(network.get(family, {})))
    for family, devices in sorted(network.get("transformer", {}).items()):
        objects.extend(f"transformer/{family}/{identifier}" for identifier in sorted(devices))
    return objects


def source_maps(network):
    """Define reviewable provenance for each generated representation."""
    objects = source_objects(network)
    buses = [f"bus/{identifier}" for identifier in sorted(network["bus"])]
    branch_objects = [f"line/{identifier}" for identifier in sorted(network["line"])]
    branch_objects += [f"switch/{identifier}" for identifier in sorted(network["switch"])]
    transformer_objects = [
        f"transformer/{family}/{identifier}"
        for family, devices in sorted(network["transformer"].items())
        for identifier in sorted(devices)
    ]
    simple_edge_sources = {}
    for family in ("line", "switch"):
        for identifier, device in sorted(network.get(family, {}).items()):
            endpoints = tuple(sorted((device["bus_from"], device["bus_to"])))
            simple_edge_sources.setdefault(endpoints, []).append(f"{family}/{identifier}")
    device_objects = [source for source in objects if not source.startswith("bus/")]
    terminal_objects = [
        {
            "generated_id": f"terminal::{bus_id}::{terminal}",
            "sources": [f"bus/{bus_id}"],
            "source_field": f"bus/{bus_id}/terminal_names/{position}",
        }
        for bus_id, bus in sorted(network["bus"].items())
        for position, terminal in enumerate(bus["terminal_names"])
    ]
    attachment_objects = []
    for family in ("line", "switch"):
        for identifier, device in sorted(network.get(family, {}).items()):
            attachment_objects.append({
                "generated_id": f"attachment::{family}/{identifier}::from",
                "sources": [f"{family}/{identifier}", f"bus/{device['bus_from']}"],
                "source_field": f"{family}/{identifier}/terminal_map_from",
            })
            attachment_objects.append({
                "generated_id": f"attachment::{family}/{identifier}::to",
                "sources": [f"{family}/{identifier}", f"bus/{device['bus_to']}"],
                "source_field": f"{family}/{identifier}/terminal_map_to",
            })
    for family in ("shunt", "load", "generator", "voltage_source"):
        for identifier, device in sorted(network.get(family, {}).items()):
            attachment_objects.append({
                "generated_id": f"attachment::{family}/{identifier}",
                "sources": [f"{family}/{identifier}", f"bus/{device['bus']}"],
                "source_field": f"{family}/{identifier}/terminal_map",
            })
    for family, devices in sorted(network["transformer"].items()):
        for identifier, device in sorted(devices.items()):
            source = f"transformer/{family}/{identifier}"
            for position, winding in enumerate(device["windings"], start=1):
                attachment_objects.append({
                    "generated_id": f"attachment::{source}::winding-{position}",
                    "sources": [source, f"bus/{winding['bus']}"],
                    "source_field": f"{source}/windings/{position}/terminal_map",
                })

    return {
        "asset_property": {
            "generated_objects": [
                {"generated_id": f"asset::{source}", "sources": [source]}
                for source in objects
            ],
            "retains": ["stable source identity", "device family", "asset membership"],
            "omits": ["equations", "numerical sparsity"],
        },
        "terminal_connectivity": {
            "generated_objects": terminal_objects + attachment_objects,
            "retains": ["ordered terminal identity", "attachment map", "grounding attachment"],
            "omits": ["constitutive equations", "objective"],
        },
        "bus_branch_multigraph": {
            "generated_objects": [
                {"generated_id": f"vertex::{source}", "sources": [source]} for source in buses
            ] + [
                {"generated_id": f"edge::{source}", "sources": [source]} for source in branch_objects
            ] + [
                {"generated_id": f"multiterminal::{source}", "sources": [source]}
                for source in transformer_objects
            ],
            "retains": ["parallel member identity", "bus incidence", "multi-terminal device identity"],
            "omits": ["ordered conductor coordinates", "constitutive equations"],
        },
        "simple_topology": {
            "generated_objects": [
                {"generated_id": f"vertex::{source}", "sources": [source]} for source in buses
            ] + [
                {
                    "generated_id": f"edge::{endpoint_a}--{endpoint_b}",
                    "sources": sources,
                }
                for (endpoint_a, endpoint_b), sources in sorted(simple_edge_sources.items())
            ],
            "retains": ["bus adjacency", "connected components of the two-terminal subnetwork"],
            "omits": [
                "parallel member identity",
                "ordered conductor coordinates",
                "multi-terminal devices pending compilation",
                "constitutive equations",
            ],
        },
        "port_factor": {
            "generated_objects": [
                {"generated_id": f"junction::{source}", "sources": [source]} for source in buses
            ] + [
                {"generated_id": f"factor::{source}", "sources": [source]} for source in device_objects
            ],
            "retains": ["factor arity", "device identity", "typed attachment"],
            "omits": ["solver-specific variable ordering"],
        },
        "opf_equation": {
            "generated_objects": [
                {"generated_id": f"equation-block::{source}", "sources": [source]}
                for source in objects
            ],
            "retains": ["variables", "constraints", "limits", "objective participation"],
            "omits": ["asset lifecycle facts not consumed by the formulation"],
        },
        "sparsity": {
            "generated_objects": [
                {"generated_id": f"nonzero-block::{source}", "sources": [source]}
                for source in objects
            ],
            "retains": ["numerical dependency blocks", "variable ordering groups"],
            "omits": ["physical edge meaning", "most stable asset identity in a solver matrix"],
        },
    }


def main():
    with FIXTURE.open() as stream: network=json.load(stream)
    assert set(network["line"])=={"l1","l2","l3","l4"}
    assert set(network["bus"])=={f"i{k}" for k in range(7)}
    assert len(network["transformer"]["n_winding"]["x1"]["windings"])==3
    image=Image.new("RGB",(W,H),"#f7f9fb"); draw=ImageDraw.Draw(image)
    definitions=[
        (0,0,"1. Asset/property","Objects answer identity questions",asset),
        (1,0,"2. Terminal connectivity","Ordered conductor attachment maps",terminal),
        (2,0,"3. Bus-branch multigraph","Study topology; x1 shown as compiled star",lambda d,x,y:physical(d,x,y,True)),
        (0,1,"4. Port-factor","Arbitrary-arity behavioral relations",factor),
        (1,1,"5. OPF/equation","Variables, constraints and decisions",opf),
        (2,1,"6. Sparsity","Numerical dependency structure",sparsity),
    ]
    for col,row,title,subtitle,painter in definitions:
        x0,y0=panel(draw,col,row,title,subtitle); painter(draw,x0,y0)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    image.save(OUTPUT,optimize=True)
    source_map = {
        "schema_version": 1,
        "fixture": str(FIXTURE.relative_to(ROOT)),
        "fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
        "figure": str(OUTPUT.relative_to(ROOT)),
        "figure_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        "views": source_maps(network),
    }
    SOURCE_MAP.parent.mkdir(parents=True, exist_ok=True)
    SOURCE_MAP.write_text(json.dumps(source_map, indent=2, sort_keys=True) + "\n")
    print(OUTPUT.relative_to(ROOT))
    print(SOURCE_MAP.relative_to(ROOT))


if __name__=="__main__": main()
