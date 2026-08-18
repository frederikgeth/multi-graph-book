#!/usr/bin/env python3
"""Render the first argument-carrying diagrams for the preservation chapters."""

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs/src/assets"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x: int, y: int, value: str, cls: str = "body", anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


def exactness_classes() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="850" viewBox="0 0 1200 850">',
        '<title>Four exactness classes as observed-set containment</title>',
        '<desc>Four panels compare source and target observed feasible sets: exact equality, inner conservative containment, outer relaxed containment, and scenario agreement only inside a declared sample region.</desc>',
        '<rect width="1200" height="850" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:28px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:19px;font-weight:bold}.body{font-size:15px}.small{font-size:14px;fill:#5f6b76}.source{fill:#d9eef8;fill-opacity:.9;stroke:#245b7a;stroke-width:3}.target{fill:#f8e1c4;fill-opacity:.9;stroke:#8a4f13;stroke-width:3;stroke-dasharray:9 6}.sample{fill:none;stroke:#17212b;stroke-width:2;stroke-dasharray:4 5}.witness{fill:#17212b}.arrow{stroke:#17212b;stroke-width:2;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 44, "Exactness is a relation between observed feasible sets", "title"),
        txt(40, 72, "The same source and target models can be exact for one observation family and approximate for another.", "sub"),
    ]
    panels = [(40, 110), (620, 110), (40, 470), (620, 470)]
    for x, y in panels:
        lines.append(f'<rect x="{x}" y="{y}" width="540" height="300" rx="14" class="panel"/>')
    # Exact: coincident outlines, offset labels make the equality legible.
    lines += [
        txt(65, 145, "exact", "head"),
        txt(65, 170, "observed sets coincide", "small"),
        '<ellipse cx="310" cy="270" rx="145" ry="82" class="source"/>',
        '<ellipse cx="310" cy="270" rx="145" ry="82" class="target"/>',
        txt(310, 270, "h(𝓕_M) = ĥ(𝓕_M̂)", "body", "middle"),
        txt(310, 324, "solid = source   dashed = target", "small", "middle"),
        # Inner: target sits inside source.
        txt(645, 145, "inner / conservative", "head"),
        txt(645, 170, "valid target points lift; some source points are excluded", "small"),
        '<ellipse cx="890" cy="270" rx="175" ry="96" class="source"/>',
        '<ellipse cx="890" cy="270" rx="108" ry="58" class="target"/>',
        txt(890, 270, "target ⊂ source", "body", "middle"),
        txt(890, 324, "no admitted nonphysical point", "small", "middle"),
        # Outer: source sits inside target, with the scalar witness in the gap.
        txt(65, 505, "outer / relaxed", "head"),
        txt(65, 530, "all source points are retained; extra target points may be nonphysical", "small"),
        '<ellipse cx="310" cy="630" rx="108" ry="58" class="source"/>',
        '<ellipse cx="310" cy="630" rx="175" ry="96" class="target"/>',
        '<circle cx="433" cy="620" r="6" class="witness"/>',
        '<path d="M438 616 L490 585" class="arrow"/>',
        txt(495, 582, "15 V witness", "small"),
        txt(310, 684, "source ⊂ target", "body", "middle"),
        # Scenario: agreement inside sample region, divergence outside.
        txt(645, 505, "scenario approximate", "head"),
        txt(645, 530, "agreement is certified only on the declared sample region", "small"),
        '<ellipse cx="890" cy="635" rx="150" ry="82" class="source"/>',
        '<ellipse cx="930" cy="635" rx="150" ry="82" class="target"/>',
        '<rect x="760" y="575" width="190" height="120" rx="8" class="sample"/>',
        txt(855, 615, "sampled", "body", "middle"),
        txt(855, 638, "region", "body", "middle"),
        txt(890, 690, "overlap here; divergence outside", "small", "middle"),
        txt(40, 820, "Source set: h(𝓕_M)   ·   target set: ĥ(𝓕_M̂)   ·   every panel assumes the observation map is declared first.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def recovery_map() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720">',
        '<title>Recovery map mechanism for exact lifted decisions</title>',
        '<desc>Two panels show a reduction from a source model to a target model. With a recovery map, source constraints can be checked and the observed feasible sets agree; without recovery, the target can become an outer relaxation.</desc>',
        '<rect width="1200" height="720" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:28px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:19px;font-weight:bold}.body{font-size:15px}.small{font-size:14px;fill:#5f6b76}.source{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.target{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.constraint{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.bad{fill:#f4e5e5;stroke:#8a3232;stroke-width:2}.solid{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}.dashed{stroke:#8a3232;stroke-width:3;stroke-dasharray:9 7;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 44, "Recovery is the positive mechanism behind exact lifted decisions", "title"),
        txt(40, 72, "Elimination alone gives a target relation; recovery lets the source constraints be evaluated again.", "sub"),
        '<rect x="40" y="105" width="535" height="555" rx="14" class="panel"/>',
        '<rect x="625" y="105" width="535" height="555" rx="14" class="panel"/>',
        txt(65, 140, "with recovery map", "head"),
        txt(650, 140, "without recovery map", "head"),
        # Exact panel.
        '<rect x="75" y="200" width="165" height="95" rx="12" class="source"/>',
        '<rect x="375" y="200" width="165" height="95" rx="12" class="target"/>',
        txt(157, 238, "source M", "head", "middle"),
        txt(157, 263, "member laws + limits", "small", "middle"),
        txt(457, 238, "target M̂", "head", "middle"),
        txt(457, 263, "reduced relation", "small", "middle"),
        '<path d="M245 247 L365 247" class="solid"/>',
        txt(305, 230, "reduce", "small", "middle"),
        '<rect x="75" y="390" width="165" height="95" rx="12" class="constraint"/>',
        '<rect x="375" y="390" width="165" height="95" rx="12" class="constraint"/>',
        txt(157, 428, "recover z", "head", "middle"),
        txt(157, 453, "z = R(x̂)", "small", "middle"),
        txt(457, 428, "check source limits", "head", "middle"),
        txt(457, 453, "g(x̂,R(x̂)) ≤ 0", "small", "middle"),
        '<path d="M457 302 L457 380" class="solid"/>',
        txt(480, 344, "target solution", "small"),
        '<path d="M375 438 L250 438" class="solid"/>',
        txt(312, 420, "recovery", "small", "middle"),
        txt(307, 548, "observed feasible sets coincide", "body", "middle"),
        txt(307, 575, "because every target point has a checked source lift", "small", "middle"),
        # No recovery panel.
        '<rect x="660" y="200" width="165" height="95" rx="12" class="source"/>',
        '<rect x="960" y="200" width="165" height="95" rx="12" class="target"/>',
        txt(742, 238, "source M", "head", "middle"),
        txt(742, 263, "member limits hidden", "small", "middle"),
        txt(1042, 238, "target M̂", "head", "middle"),
        txt(1042, 263, "reduced relation", "small", "middle"),
        '<path d="M830 247 L950 247" class="solid"/>',
        txt(890, 230, "reduce", "small", "middle"),
        '<rect x="810" y="390" width="165" height="95" rx="12" class="bad"/>',
        txt(892, 428, "uncheckable", "head", "middle"),
        txt(892, 453, "source limits", "small", "middle"),
        '<path d="M1042 302 L975 380" class="dashed"/>',
        txt(1055, 345, "no lift", "small"),
        txt(892, 548, "target feasible set can inflate", "body", "middle"),
        txt(892, 575, "a boundary match is not a decision certificate", "small", "middle"),
        txt(40, 700, "Recovery may be algebraic, constructive, or solver-backed; the certificate must state its domain and the quantities it reconstructs.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def argument_spine() -> str:
    steps = [
        ("1", "graph is ambiguous", "scope + translation traps"),
        ("2", "views answer different questions", "taxonomy + frameworks"),
        ("3", "there is no universal ladder", "maps + query factorization"),
        ("4", "a transformation needs a contract", "preservation + recovery"),
        ("5", "exactness is observation-relative", "exact / inner / outer / scenario"),
        ("6", "equations can survive while decisions break", "parallel-line counterexample"),
        ("7", "guards make rules checkable", "certificates + refusals"),
        ("8", "legitimate collapses have conditions", "positive sequence + reductions"),
        ("9", "representation has numerical cost", "conditioning + fill + margins"),
    ]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="760" viewBox="0 0 1400 760">',
        '<title>The argument spine of the book</title>',
        '<desc>Nine linked claims guide the reader from graph ambiguity through query-relative transformations, decision counterexamples, guarded rules, legitimate collapses, and numerical consequences.</desc>',
        '<rect width="1400" height="760" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.step{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.step.alt{fill:#f8e1c4;stroke:#8a4f13}.step.final{fill:#e4f4e7;stroke:#477a55}.num{font-size:18px;font-weight:bold}.head{font-size:17px;font-weight:bold}.small{font-size:14px;fill:#5f6b76}.arrow{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 46, "The argument spine", "title"),
        txt(40, 76, "Read 1–5 left to right, then 6–9 right to left; each step adds to one cumulative argument.", "sub"),
    ]
    # Five boxes on the first row and four on the second row, with a serpentine
    # reading order so the complete spine remains legible in print.
    positions = [(50 + 265 * i, 145) for i in range(5)] + [(1110 - 265 * i, 455) for i in range(4)]
    heading_lines = {
        "1": ["graph is", "ambiguous"],
        "2": ["views answer", "different questions"],
        "3": ["there is no", "universal ladder"],
        "4": ["a transformation", "needs a contract"],
        "5": ["exactness is", "observation-relative"],
        "6": ["equations can survive", "while decisions break"],
        "7": ["guards make rules", "checkable"],
        "8": ["legitimate collapses", "have conditions"],
        "9": ["representation has", "numerical cost"],
    }
    for index, ((number, heading, detail), (x, y)) in enumerate(zip(steps, positions)):
        cls = "step final" if number == "9" else ("step alt" if int(number) % 2 == 0 else "step")
        lines.append(f'<rect x="{x}" y="{y}" width="220" height="150" rx="14" class="{cls}"/>')
        lines.append(txt(x + 18, y + 30, number, "num"))
        for offset, heading_line in enumerate(heading_lines[number]):
            lines.append(txt(x + 18, y + 65 + 20 * offset, heading_line, "head"))
        # Split the reader-facing detail into two short lines where possible.
        if " + " in detail:
            first, second = detail.split(" + ", 1)
            lines.append(txt(x + 18, y + 117, first + " +", "small"))
            lines.append(txt(x + 18, y + 137, second, "small"))
        else:
            lines.append(txt(x + 18, y + 127, detail, "small"))
    for i in range(4):
        x = positions[i][0] + 220
        lines.append(f'<path d="M{x} 220 L{x + 45} 220" class="arrow"/>')
    # Step 5 turns directly down into step 6. Sending this connector across the
    # empty left margin makes the layout look as if a tenth box is missing.
    lines.append('<path d="M1220 295 L1220 455" class="arrow"/>')
    for i in range(3):
        x = positions[5 + i][0]
        lines.append(f'<path d="M{x} 530 L{x - 45} 530" class="arrow"/>')
    lines += [
        txt(50, 685, "The spine is a navigation device, not a claim hierarchy: later chapters can refine or qualify an earlier link.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def query_partial_orders() -> str:
    nodes = [
        ("asset/dependency", 0),
        ("port–factor", 1),
        ("multigraph", 2),
        ("simple graph", 3),
        ("equation/sparsity", 4),
    ]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="820" viewBox="0 0 1400 820">',
        '<title>Partial orders change with the query family</title>',
        '<desc>The same five representation nodes are shown under two query families. Electrical boundary queries order port-factor, multigraph, and simple views, while asset and outage queries privilege the asset/dependency view; incomparable relations are marked explicitly.</desc>',
        '<rect width="1400" height="820" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:29px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:20px;font-weight:bold}.node{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.asset{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.eq{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.body{font-size:15px}.small{font-size:14px;fill:#5f6b76}.arrow{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}.dashed{stroke:#8a4f13;stroke-width:2;stroke-dasharray:8 6;fill:none}.cross{stroke:#8a3232;stroke-width:3}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 45, "A representation order depends on the question", "title"),
        txt(40, 75, "Arrows mean “sufficient for this query family through a declared map”, not universal abstraction.", "sub"),
        '<rect x="40" y="115" width="635" height="590" rx="14" class="panel"/>',
        '<rect x="725" y="115" width="635" height="590" rx="14" class="panel"/>',
        txt(70, 155, "boundary power-flow queries", "head"),
        txt(755, 155, "asset, outage, and maintenance queries", "head"),
    ]
    # Electrical panel: a clear chain plus side views.
    boxes_left = {"asset/dependency": (75, 265), "port–factor": (265, 205), "multigraph": (455, 265), "simple graph": (455, 475), "equation/sparsity": (265, 475)}
    boxes_right = {"asset/dependency": (760, 265), "port–factor": (950, 205), "multigraph": (1140, 265), "simple graph": (1140, 475), "equation/sparsity": (950, 475)}
    for label, (x, y) in boxes_left.items():
        cls = "asset" if label.startswith("asset") else ("eq" if label.startswith("equation") else "node")
        lines.append(f'<rect x="{x}" y="{y}" width="170" height="70" rx="12" class="{cls}"/>')
        lines.append(txt(x + 85, y + 42, label, "body", "middle"))
    for label, (x, y) in boxes_right.items():
        cls = "asset" if label.startswith("asset") else ("eq" if label.startswith("equation") else "node")
        lines.append(f'<rect x="{x}" y="{y}" width="170" height="70" rx="12" class="{cls}"/>')
        lines.append(txt(x + 85, y + 42, label, "body", "middle"))
    # Electrical arrows.
    lines += [
        '<path d="M435 240 L445 275" class="arrow"/>',
        '<path d="M540 345 L540 465" class="arrow"/>',
        '<path d="M455 510 L445 510" class="arrow"/>',
        '<path d="M350 275 L350 465" class="arrow"/>',
        txt(80, 610, "asset view is incomparable here", "small"),
        '<path d="M235 300 L420 300" class="dashed"/>',
        txt(350, 290, "Λ + study map required", "small", "middle"),
        # Asset/outage arrows privilege the asset view and retain the warning.
        '<path d="M930 265 C980 180 1080 180 1140 265" class="dashed" marker-end="url(#arrow)"/>',
        txt(1035, 190, "Λ + state map", "small", "middle"),
        '<path d="M1225 345 L1225 465" class="arrow"/>',
        '<path d="M1035 275 L1035 465" class="dashed"/>',
        txt(1035, 455, "not automatic", "small", "middle"),
        txt(765, 610, "equation/sparsity view is not an asset system", "small"),
        '<path d="M1080 580 L1190 580" class="cross"/>',
        '<path d="M1190 580 L1080 580" class="cross"/>',
        txt(1135, 635, "incomparable unless a query map is declared", "small", "middle"),
        txt(40, 770, "The edges change when Q changes. This is why “more detailed” is not a universal claim across the four frameworks.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def case_escalation() -> str:
    parallel_rows = [
        ("scalar DC", ["—", "—", "—", "—", "—", "analytic"]),
        ("scalar AC π", ["—", "—", "—", "yes", "one-end", "analytic"]),
        ("proportional multiconductor", ["yes", "no", "explicit", "—", "one-end", "certificate"]),
        ("non-proportional four-wire", ["yes", "yes", "explicit", "—", "two-end", "independent"]),
        ("four-wire nominal-π", ["yes", "yes", "explicit", "yes", "two-end", "independent"]),
    ]
    transformer_rows = [
        ("leakage relation", ["pairwise", "fixed", "—", "—"]),
        ("reference compilation", ["all windings", "fixed", "recovery", "round-trip"]),
        ("terminal assembly", ["WYE/DELTA", "fixed", "ground", "certificate"]),
        ("factor completion", ["multi-port", "fixed", "auxiliary", "cross-check"]),
        ("tap decisions", ["multi-port", "discrete", "controls", "solver-backed"]),
    ]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1060" viewBox="0 0 1400 1060">',
        '<title>Escalation grid for the worked cases</title>',
        '<desc>Two grids show how the parallel-line and transformer cases escalate coupling, conductor detail, shunts, controls, and independent checks rather than repeating one example.</desc>',
        '<rect width="1400" height="1060" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.head{font-size:19px;font-weight:bold}.label{font-size:14px;font-weight:bold}.cell{font-size:13px}.grid{stroke:#17212b;stroke-width:1}.headfill{fill:#e8f0fa}.yes{fill:#e4f4e7}.partial{fill:#f8e1c4}.none{fill:#fbfcfd}.foot{font-size:14px;fill:#5f6b76}</style>',
        txt(40, 46, "The worked cases are an escalation, not repetition", "title"),
        txt(40, 76, "Each row adds a modelling distinction or a stronger evidence obligation.", "sub"),
        txt(40, 125, "Parallel-member decision cases", "head"),
    ]
    x0, y0, row_h, label_w, col_w = 40, 155, 52, 260, 175
    cols = ["coupling", "non-proportionality", "neutral", "shunts", "end structure", "check"]
    lines.append(f'<rect x="{x0}" y="{y0}" width="label_w" height="{row_h}" class="headfill"/>'.replace("label_w", str(label_w)))
    lines.append(txt(x0 + 12, y0 + 32, "case", "label"))
    for j, col in enumerate(cols):
        x = x0 + label_w + col_w * j
        lines.append(f'<rect x="{x}" y="{y0}" width="{col_w}" height="{row_h}" class="headfill"/>')
        lines.append(txt(x + col_w / 2, y0 + 32, col, "label", "middle"))
    for i, (name, values) in enumerate(parallel_rows, start=1):
        y = y0 + row_h * i
        lines.append(f'<rect x="{x0}" y="{y}" width="{label_w}" height="{row_h}" class="none"/>')
        lines.append(txt(x0 + 12, y + 32, name, "cell"))
        for j, value in enumerate(values):
            x = x0 + label_w + col_w * j
            cls = "yes" if value in {"yes", "explicit", "certificate", "independent"} else ("partial" if value in {"one-end", "two-end", "analytic"} else "none")
            lines.append(f'<rect x="{x}" y="{y}" width="{col_w}" height="{row_h}" class="{cls}"/>')
            lines.append(txt(x + col_w / 2, y + 32, value, "cell", "middle"))
    # Transformer grid.
    y2 = 500
    lines.append(txt(40, y2, "Transformer compilation and control cases", "head"))
    x0, y0, row_h, label_w, col_w = 40, y2 + 30, 62, 300, 255
    cols2 = ["electrical scope", "control domain", "forgotten/auxiliary detail", "evidence"]
    lines.append(f'<rect x="{x0}" y="{y0}" width="{label_w}" height="{row_h}" class="headfill"/>')
    lines.append(txt(x0 + 12, y0 + 38, "case", "label"))
    for j, col in enumerate(cols2):
        x = x0 + label_w + col_w * j
        lines.append(f'<rect x="{x}" y="{y0}" width="{col_w}" height="{row_h}" class="headfill"/>')
        lines.append(txt(x + col_w / 2, y0 + 38, col, "label", "middle"))
    for i, (name, values) in enumerate(transformer_rows, start=1):
        y = y0 + row_h * i
        lines.append(f'<rect x="{x0}" y="{y}" width="{label_w}" height="{row_h}" class="none"/>')
        lines.append(txt(x0 + 12, y + 38, name, "cell"))
        for j, value in enumerate(values):
            x = x0 + label_w + col_w * j
            cls = "yes" if value in {"recovery", "ground", "auxiliary", "round-trip", "certificate", "cross-check", "solver-backed", "controls"} else ("partial" if value in {"pairwise", "all windings", "multi-port", "WYE/DELTA", "fixed", "discrete"} else "none")
            lines.append(f'<rect x="{x}" y="{y}" width="{col_w}" height="{row_h}" class="{cls}"/>')
            lines.append(txt(x + col_w / 2, y + 38, value, "cell", "middle"))
    lines += [
        txt(40, 930, "The progression makes the research programme visible: conductor coupling and decision observations grow together with the guard and reproduction burden.", "foot"),
        txt(40, 960, "yes/explicit = present; partial = scoped or one-end; — = deliberately absent in that case.", "foot"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def vocabulary_bridge() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="980" viewBox="0 0 1400 980">',
        '<title>One network, five languages</title>',
        '<desc>Five rows show community language entering the book\'s typed bridge. A dashed bypass marked if untranslated leads directly to an unsafe inference; the bridge blocks that inference.</desc>',
        '<rect width="1400" height="980" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.head{font-size:18px;font-weight:bold}.body{font-size:15px}.small{font-size:13px;fill:#5f6b76}.community{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.bridge{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.warning{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.row{fill:#fbfcfd;stroke:#17212b;stroke-width:1.5}.arrow{stroke:#17212b;stroke-width:2;fill:none;marker-end:url(#arrow)}.bypass{stroke:#8a4f13;stroke-width:2;stroke-dasharray:8 6;fill:none;marker-end:url(#warnArrow)}.tag{fill:#eee8f8;stroke:#7856a8;stroke-width:1.5}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker><marker id="warnArrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#8a4f13"/></marker></defs>',
        txt(40, 46, "One network, five languages", "title"),
        txt(40, 76, "Translate the object and query—not only the word. Each community sees a useful view and carries a characteristic risk.", "sub"),
        '<rect x="40" y="105" width="1320" height="82" rx="14" class="tag"/>',
        txt(700, 137, "source model / shared semantic anchor", "head", "middle"),
        txt(700, 164, "identified assets · ordered ports · junctions · factors · states · limits · provenance", "body", "middle"),
        txt(55, 225, "community language", "head"),
        txt(470, 225, "bridge / qualified statement", "head"),
        txt(1010, 225, "if untranslated → unsafe inference", "head"),
    ]
    rows = [
        (
            "power engineering",
            "bus · feeder · line · radial · power flow",
            "name graph, active state, terminal quantity",
            "one edge carries one conserved flow",
        ),
        (
            "software and network data",
            "equipment · terminal · connectivity node · status",
            "name source/generated object and provenance map",
            "record = compiled bus = physical asset",
        ),
        (
            "mathematical modelling",
            "variable · constraint · feasible set · relaxation",
            "name observation, decision, and recovery maps",
            "equal equations imply equal decisions",
        ),
        (
            "mathematical graph theory",
            "vertex · edge/arc · cycle · quotient · minor",
            "name object types, incidence, graph, and morphism",
            "topology alone fixes electrical meaning",
        ),
        (
            "graph machine learning",
            "node/edge feature · message · pooling · hidden state",
            "name compiled message graph and retained semantics",
            "pooling preserves identity and limits",
        ),
    ]
    for idx, (community, terms, bridge, warning) in enumerate(rows):
        y = 250 + idx * 128
        lines += [
            f'<rect x="40" y="{y}" width="1320" height="108" rx="12" class="row"/>',
            f'<rect x="55" y="{y + 14}" width="325" height="80" rx="10" class="community"/>',
            f'<rect x="460" y="{y + 42}" width="430" height="52" rx="10" class="bridge"/>',
            f'<rect x="1010" y="{y + 14}" width="330" height="80" rx="10" class="warning"/>',
            txt(217, y + 43, community, "head", "middle"),
            txt(217, y + 70, terms, "small", "middle"),
            txt(675, y + 73, bridge, "body", "middle"),
            txt(1175, y + 58, warning, "body", "middle"),
            f'<path d="M380 {y + 70} L450 {y + 70}" class="arrow"/>',
            f'<path d="M380 {y + 34} C520 {y + 2} 900 {y + 2} 1000 {y + 34}" class="bypass"/>',
        ]
    lines += [
        '<rect x="40" y="905" width="1320" height="50" rx="12" class="tag"/>',
        txt(700, 930, "solid arrow: qualify through the bridge · dashed arrow: unsafe bypass if untranslated", "head", "middle"),
        txt(700, 949, "house rule: preferred term · accepted qualified shorthand · unsafe unqualified term", "small", "middle"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def audience_routes() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="800" viewBox="0 0 1400 800">',
        '<title>Audience routes through the HTML and PDF book</title>',
        '<desc>A central argument spine is shared by HTML and PDF. Five community routes branch to power engineering, software and data, mathematical modelling, graph theory, and graph machine learning chapters.</desc>',
        '<rect width="1400" height="800" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.head{font-size:17px;font-weight:bold}.node{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.aud1{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.aud2{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.aud3{fill:#f4e5e5;stroke:#8a3232;stroke-width:2}.aud4{fill:#eee8f8;stroke:#7856a8;stroke-width:2}.aud5{fill:#f7f7f7;stroke:#17212b;stroke-width:2}.small{font-size:13px;fill:#5f6b76}.body{font-size:15px}.line{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}.branch{stroke:#5f6b76;stroke-width:2;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 46, "Reading routes through one argument", "title"),
        txt(40, 76, "HTML is the full knowledge base; the PDF is a shorter, argument-shaped serialization of the same sources.", "sub"),
        txt(40, 130, "shared spine", "head"),
    ]
    spine = [(100, "scope"), (340, "representations"), (580, "contracts"), (820, "counterexamples"), (1060, "consequences")]
    for i, (x, label) in enumerate(spine):
        lines.append(f'<rect x="{x}" y="155" width="190" height="70" rx="12" class="node"/>')
        lines.append(txt(x + 95, 197, label, "body", "middle"))
        if i < len(spine) - 1:
            lines.append(f'<path d="M{x + 190} 190 L{x + 230} 190" class="line"/>')
    audiences = [
        ("power engineer", "physical meaning · terminals · decisions", "aud1", 45, 420, 100),
        ("software / data expert", "identity · topology · provenance", "aud2", 315, 490, 340),
        ("mathematical modeller", "feasible sets · maps · certificates", "aud3", 585, 420, 580),
        ("graph theorist", "typed incidence · cycles · quotients", "aud4", 855, 490, 820),
        ("graph ML expert", "message graph · pooling · recovery", "aud5", 1125, 420, 1060),
    ]
    for title, detail, cls, x, y, anchor_x in audiences:
        lines.append(f'<rect x="{x}" y="{y}" width="230" height="145" rx="12" class="{cls}"/>')
        lines.append(txt(x + 115, y + 38, title, "head", "middle"))
        parts = detail.split(" · ")
        for j, part in enumerate(parts):
            lines.append(txt(x + 115, y + 70 + 19 * j, part, "small", "middle"))
        branch_start_x = anchor_x + 95
        lines.append(f'<path d="M{branch_start_x} 225 C{branch_start_x} 330 {x + 115} {y - 50} {x + 115} {y}" class="branch"/>')
    lines += [
        txt(40, 700, "Each route re-enters the same contract language; audience emphasis changes, but preservation claims do not.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def sequence_subspace() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="760" viewBox="0 0 1400 760">',
        '<title>Positive-sequence invariant subspace and sequence mixing</title>',
        '<desc>Two projected sequence-space panels show a circulant factor preserving the positive-sequence axis and a non-circulant perturbation producing an off-axis residual.</desc>',
        '<rect width="1400" height="760" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:20px;font-weight:bold}.body{font-size:16px}.small{font-size:14px;fill:#5f6b76}.axis{stroke:#17212b;stroke-width:2}.invariant{stroke:#245b7a;stroke-width:5;fill:none;marker-end:url(#arrow)}.mix{stroke:#8a3232;stroke-width:5;fill:none;marker-end:url(#arrow)}.residual{stroke:#8a3232;stroke-width:3;stroke-dasharray:8 6}.state{fill:#17212b}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 46, "Sequence subspace geometry", "title"),
        txt(40, 76, "A balanced state stays on the positive-sequence axis only when the factor preserves that invariant subspace.", "sub"),
        '<rect x="40" y="120" width="635" height="540" rx="14" class="panel"/>',
        '<rect x="725" y="120" width="635" height="540" rx="14" class="panel"/>',
        txt(70, 160, "circulant factor", "head"),
        txt(755, 160, "non-circulant perturbation", "head"),
    ]
    for ox in (40, 725):
        cx = ox + 315
        cy = 430
        lines += [
            f'<line x1="{ox + 100}" y1="{cy}" x2="{ox + 555}" y2="{cy}" class="axis"/>',
            f'<line x1="{cx}" y1="{cy + 145}" x2="{cx}" y2="{cy - 180}" class="axis"/>',
            txt(ox + 555, cy + 28, "positive-sequence direction", "small", "end"),
            txt(cx + 12, cy - 180, "mixing direction", "small"),
        ]
    lines += [
        '<circle cx="220" cy="430" r="8" class="state"/>',
        '<path d="M220 430 L500 430" class="invariant"/>',
        txt(220, 470, "balanced state", "small", "middle"),
        txt(500, 405, "Y𝒱₊ ⊂ 𝒱₊", "body", "middle"),
        txt(355, 575, "sequence residual = 0", "small", "middle"),
        '<circle cx="905" cy="430" r="8" class="state"/>',
        '<path d="M905 430 L1150 315" class="mix"/>',
        '<path d="M905 430 L1150 430" class="residual"/>',
        txt(905, 470, "balanced input", "small", "middle"),
        txt(1150, 295, "Yv", "body", "middle"),
        txt(1035, 455, "projection onto 𝒱₊", "small", "middle"),
        txt(1035, 540, "ρ₊(v) = ‖v − E₊C₊v‖", "body", "middle"),
        txt(1035, 575, "coordinate residual, not yet a decision bound", "small", "middle"),
        txt(40, 710, "The positive-sequence model is exact for the restricted observation family only when the factor, grounding, decisions, and observations close under the restriction.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def bus_overlay() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900">',
        '<title>What does bus mean? Four representation overlays</title>',
        '<desc>One substation drawing is shown as a physical busbar section, connectivity node, state-resolved topological node, and compiled bus-branch node.</desc>',
        '<rect width="1400" height="900" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:19px;font-weight:bold}.body{font-size:15px}.small{font-size:14px;fill:#5f6b76}.bar{stroke:#17212b;stroke-width:8}.wire{stroke:#245b7a;stroke-width:4}.open{stroke:#8a3232;stroke-width:4;stroke-dasharray:8 6}.node{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.topo{fill:#e4f4e7;stroke:#477a55;stroke-width:3}.compiled{fill:#f8e1c4;stroke:#8a4f13;stroke-width:3}.switch{fill:#f4e5e5;stroke:#8a3232;stroke-width:2}</style>',
        txt(40, 46, "One substation, four meanings of “bus”", "title"),
        txt(40, 76, "The geometry is held constant; the retained objects and admissible queries change with the representation.", "sub"),
    ]
    panels = [(40, 120), (725, 120), (40, 500), (725, 500)]
    titles = ["physical busbar section", "connectivity node", "topological node under σ", "compiled bus–branch node"]
    for (x, y), title in zip(panels, titles):
        lines.append(f'<rect x="{x}" y="{y}" width="635" height="300" rx="14" class="panel"/>')
        lines.append(txt(x + 25, y + 38, title, "head"))
    def common(x: int, y: int, mode: str) -> list[str]:
        cy = y + 180
        result = [f'<line x1="{x + 115}" y1="{cy}" x2="{x + 500}" y2="{cy}" class="bar"/>']
        result += [f'<line x1="{x + 135}" y1="{cy - 75}" x2="{x + 135}" y2="{cy}" class="wire"/>', f'<line x1="{x + 300}" y1="{cy}" x2="{x + 300}" y2="{cy + 75}" class="wire"/>', f'<line x1="{x + 465}" y1="{cy - 75}" x2="{x + 465}" y2="{cy}" class="wire"/>']
        result += [txt(x + 135, cy - 90, "t₁", "small", "middle"), txt(x + 300, cy + 100, "t₂", "small", "middle"), txt(x + 465, cy - 90, "t₃", "small", "middle")]
        if mode == "physical":
            result += [txt(x + 300, cy + 145, "section identity and hardware retained", "small", "middle")]
        elif mode == "connectivity":
            for px in (x + 135, x + 300, x + 465):
                result.append(f'<circle cx="{px}" cy="{cy}" r="10" class="node"/>')
            result += [txt(x + 300, cy + 145, "κ maps terminals to a connectivity node", "small", "middle")]
        elif mode == "topological":
            result += [f'<ellipse cx="{x + 300}" cy="{cy}" rx="205" ry="42" class="topo"/>', txt(x + 300, cy + 145, "closed switches merge a component for state σ", "small", "middle")]
            result += [f'<line x1="{x + 300}" y1="{cy - 42}" x2="{x + 300}" y2="{cy - 80}" class="open"/>']
        else:
            result += [f'<rect x="{x + 205}" y="{cy - 38}" width="190" height="76" rx="12" class="compiled"/>', txt(x + 300, cy + 6, "bus bσ", "body", "middle"), txt(x + 300, cy + 145, "πσ(κ(t)) + provenance", "small", "middle")]
        return result
    lines += common(40, 120, "physical") + common(725, 120, "connectivity") + common(40, 500, "topological") + common(725, 500, "compiled")
    lines += [txt(40, 850, "A compiled bus count is therefore a state- and purpose-relative result, not a replacement for equipment identity or switch decisions.", "small"), '</svg>']
    return "\n".join(lines) + "\n"


def certificate_composition() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="760" viewBox="0 0 1400 760">',
        '<title>Forward and reverse order of certificate composition</title>',
        '<desc>Two transformations compose left to right for constraints and right to left for recovery, with an explicit interface compatibility gate.</desc>',
        '<rect width="1400" height="760" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.node{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.cert{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.recovery{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.gate{fill:#eee8f8;stroke:#7856a8;stroke-width:2}.head{font-size:19px;font-weight:bold}.body{font-size:16px}.small{font-size:14px;fill:#5f6b76}.arrow{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}.reverse{stroke:#477a55;stroke-width:3;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 46, "Certificate composition has an order", "title"),
        txt(40, 76, "Constraints travel forward; recovery travels backward through the same intermediate identity.", "sub"),
        '<rect x="55" y="150" width="230" height="90" rx="12" class="node"/>',
        '<rect x="585" y="150" width="230" height="90" rx="12" class="node"/>',
        '<rect x="1115" y="150" width="230" height="90" rx="12" class="node"/>',
        txt(170, 205, "M₀ source", "head", "middle"), txt(700, 205, "M₁ intermediate", "head", "middle"), txt(1230, 205, "M₂ target", "head", "middle"),
        '<path d="M295 195 L575 195" class="arrow"/><path d="M825 195 L1105 195" class="arrow"/>',
        '<rect x="355" y="110" width="170" height="55" rx="10" class="cert"/>',
        '<rect x="885" y="110" width="170" height="55" rx="10" class="cert"/>',
        txt(440, 144, "C₁₀", "body", "middle"), txt(970, 144, "C₂₁", "body", "middle"),
        txt(700, 285, "forward: C₂₀ = C₂₁ ∘ C₁₀", "head", "middle"),
        '<rect x="480" y="330" width="440" height="90" rx="12" class="gate"/>',
        txt(700, 368, "interface compatibility gate", "head", "middle"),
        txt(700, 395, "T₂ consumes the object generated by T₁", "small", "middle"),
        '<path d="M700 240 L700 320" class="arrow"/>',
        '<path d="M1105 525 L825 525" class="reverse"/><path d="M575 525 L295 525" class="reverse"/>',
        '<rect x="885" y="545" width="170" height="55" rx="10" class="recovery"/>',
        '<rect x="355" y="545" width="170" height="55" rx="10" class="recovery"/>',
        txt(970, 579, "R₁₂", "body", "middle"), txt(440, 579, "R₀₁", "body", "middle"),
        txt(700, 475, "reverse: R₀₂ = R₀₁ ∘ R₁₂", "head", "middle"),
        txt(40, 700, "The current implementation records both component certificates and the intermediate object identity; richer order-theoretic composition remains open.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def guarded_rule_gate() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="820" viewBox="0 0 1400 820">',
        '<title>Guarded transformation rule as a gate</title>',
        '<desc>An input candidate passes a sequence of structural, physical, state, and observation guards, producing either a certificate-backed rewrite or a structured rejection naming the failed guard.</desc>',
        '<rect width="1400" height="820" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.input{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.guard{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.pass{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.reject{fill:#f4e5e5;stroke:#8a3232;stroke-width:2}.head{font-size:19px;font-weight:bold}.body{font-size:15px}.small{font-size:14px;fill:#5f6b76}.arrow{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}.rejectline{stroke:#8a3232;stroke-width:3;stroke-dasharray:9 6;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 46, "A rule is a gate, not a guess", "title"),
        txt(40, 76, "The normalizer returns a certificate-backed target or a structured rejection naming the failed condition.", "sub"),
        '<rect x="55" y="170" width="220" height="100" rx="12" class="input"/>',
        txt(165, 212, "candidate match", "head", "middle"), txt(165, 240, "e.g. degree-two series", "small", "middle"),
        '<path d="M285 220 L385 220" class="arrow"/>',
    ]
    guards = [(400, "identity", "same coordinate/type"), (590, "state", "fixed admissible state"), (780, "physics", "no shunt/ground/control"), (970, "observation", "recovery + limits"),]
    for x, title, detail in guards:
        lines.append(f'<rect x="{x}" y="170" width="165" height="100" rx="12" class="guard"/>')
        lines.append(txt(x + 82, 208, title, "head", "middle"))
        lines.append(txt(x + 82, 238, detail, "small", "middle"))
        if x < 970:
            lines.append(f'<path d="M{x + 170} 220 L{x + 185} 220" class="arrow"/>')
    lines += [
        '<path d="M1135 220 L1220 220" class="arrow"/>',
        '<rect x="1215" y="160" width="145" height="120" rx="12" class="pass"/>',
        txt(1287, 205, "target +", "head", "middle"), txt(1287, 230, "certificate", "head", "middle"), txt(1287, 255, "rewrite", "small", "middle"),
        '<path d="M675 275 L675 425" class="rejectline"/>',
        '<rect x="490" y="440" width="370" height="110" rx="12" class="reject"/>',
        txt(675, 480, "structured rejection", "head", "middle"),
        txt(675, 510, "junction_has_shunt_or_grounding", "small", "middle"),
        txt(675, 590, "Failed guards remain data, not silent approximations.", "body", "middle"),
        txt(40, 720, "A later rule may choose a different target class, but it must declare a new contract rather than passing an inapplicable rewrite.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def spine_band() -> str:
    stages = [
        ("1", "scope"), ("2", "views"), ("3", "maps"),
        ("4", "contracts"), ("5", "exactness"), ("6", "decisions"),
        ("7", "guards"), ("8", "collapses"), ("9", "numerics"),
    ]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="250" viewBox="0 0 1400 250">',
        '<title>Chapter-header argument spine with guarded rules highlighted</title>',
        '<desc>A thin nine-stage chapter route highlights the guarded-rules stage and places it between decision counterexamples and legitimate collapses.</desc>',
        '<rect width="1400" height="250" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:22px;font-weight:bold}.sub{font-size:14px;fill:#5f6b76}.stage{fill:#f4f6f8;stroke:#8a959f;stroke-width:2}.active{fill:#e4f4e7;stroke:#477a55;stroke-width:3}.num{font-size:13px;font-weight:bold}.label{font-size:14px;font-weight:bold}.arrow{stroke:#8a959f;stroke-width:2;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0,0 L7,4 L0,8 z" fill="#8a959f"/></marker></defs>',
        txt(40, 36, "Chapter route · current spine stage: guarded rules", "title"),
        txt(40, 60, "Use the band as a local orientation cue; it is a route, not a hierarchy of claims.", "sub"),
    ]
    start_x, y, width, gap = 40, 105, 132, 18
    for idx, (num, label) in enumerate(stages):
        x = start_x + idx * (width + gap)
        cls = "active" if num == "7" else "stage"
        lines.append(f'<rect x="{x}" y="{y}" width="{width}" height="72" rx="11" class="{cls}"/>')
        lines.append(txt(x + 14, y + 24, num, "num"))
        lines.append(txt(x + width / 2, y + 48, label, "label", "middle"))
        if idx < len(stages) - 1:
            lines.append(f'<path d="M{x + width + 4} {y + 36} L{x + width + gap - 4} {y + 36}" class="arrow"/>')
    lines += [txt(40, 222, "The highlighted stage supplies the local premise for this chapter; neighbouring stages remain available for navigation.", "sub"), '</svg>']
    return "\n".join(lines) + "\n"


def orientation_power() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="760" viewBox="0 0 1400 760">',
        '<title>Stored orientation is not operating power direction</title>',
        '<desc>Two panels distinguish an arbitrary reference orientation and terminal current signs from the operating-point complex power transfer, which may reverse without changing the stored arc.</desc>',
        '<rect width="1400" height="760" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:20px;font-weight:bold}.body{font-size:16px}.small{font-size:14px;fill:#5f6b76}.wire{stroke:#17212b;stroke-width:8}.ref{stroke:#245b7a;stroke-width:4;fill:none;marker-end:url(#arrow)}.power{stroke:#8a4f13;stroke-width:5;fill:none;marker-end:url(#arrow)}.reverse{stroke:#8a3232;stroke-width:5;fill:none;marker-end:url(#arrow);stroke-dasharray:10 7}.bus{fill:#d9eef8;stroke:#245b7a;stroke-width:2}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 46, "An oriented arc is a coordinate choice, not a flow measurement", "title"),
        txt(40, 76, "Keep the stored triple ℓij, terminal signs, and operating-point power transfer as separate records.", "sub"),
        '<rect x="40" y="120" width="635" height="520" rx="14" class="panel"/>',
        '<rect x="725" y="120" width="635" height="520" rx="14" class="panel"/>',
        txt(70, 160, "reference orientation and terminal signs", "head"),
        txt(755, 160, "operating-point power transfer", "head"),
        '<rect x="95" y="330" width="120" height="78" rx="12" class="bus"/>',
        '<rect x="500" y="330" width="120" height="78" rx="12" class="bus"/>',
        txt(155, 375, "i", "head", "middle"), txt(560, 375, "j", "head", "middle"),
        '<line x1="215" y1="369" x2="500" y2="369" class="wire"/>',
        '<path d="M240 300 L455 300" class="ref"/>',
        txt(350, 286, "stored orientation ℓij", "body", "middle"),
        '<path d="M270 445 L470 445" class="ref"/>',
        txt(370, 475, "Iℓij enters at i; −Iℓij enters at j", "small", "middle"),
        txt(350, 545, "reversing the reference swaps signs and endpoint records", "small", "middle"),
        '<rect x="780" y="330" width="120" height="78" rx="12" class="bus"/>',
        '<rect x="1185" y="330" width="120" height="78" rx="12" class="bus"/>',
        txt(840, 375, "i", "head", "middle"), txt(1245, 375, "j", "head", "middle"),
        '<line x1="900" y1="369" x2="1185" y2="369" class="wire"/>',
        '<path d="M920 300 L1135 300" class="power"/>',
        txt(1027, 286, "Pij + 𝗂Qij > 0", "body", "middle"),
        '<path d="M1135 445 L920 445" class="reverse"/>',
        txt(1027, 475, "Pij + 𝗂Qij < 0 can occur", "body", "middle"),
        txt(1027, 545, "the same stored ℓij can carry either sign at another state", "small", "middle"),
        txt(40, 700, "A directed drawing may encode incidence, a reference sign, a causal relation, or a measured transfer. Name which one is intended before interpreting an arrow.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def cycles_radial() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="820" viewBox="0 0 1400 820">',
        '<title>Cycles, parallel fibres, and radial tails depend on the graph</title>',
        '<desc>Three panels show a simple cycle, a two-edge line-identity cycle hidden by a simple projection, and a radial tail ending at a leaf.</desc>',
        '<rect width="1400" height="820" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:20px;font-weight:bold}.body{font-size:16px}.small{font-size:14px;fill:#5f6b76}.edge{stroke:#17212b;stroke-width:5;fill:none}.parallel{stroke:#245b7a;stroke-width:5;fill:none}.tail{stroke:#477a55;stroke-width:5;fill:none}.node{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.leaf{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.dashed{stroke:#8a4f13;stroke-width:3;stroke-dasharray:8 6;fill:none}</style>',
        txt(40, 46, "Cycles and radiality are representation-scoped predicates", "title"),
        txt(40, 76, "State the vertex/edge set first: a simple projection can hide line identity, while an active state can open a tail.", "sub"),
        '<rect x="40" y="120" width="415" height="560" rx="14" class="panel"/>',
        '<rect x="492" y="120" width="415" height="560" rx="14" class="panel"/>',
        '<rect x="945" y="120" width="415" height="560" rx="14" class="panel"/>',
        txt(65, 160, "simple cycle", "head"), txt(517, 160, "parallel fibre", "head"), txt(970, 160, "radial tail", "head"),
        # Triangle/simple cycle.
        '<path d="M150 430 L285 280 L405 430 Z" class="edge"/>',
        '<circle cx="150" cy="430" r="12" class="node"/><circle cx="285" cy="280" r="12" class="node"/><circle cx="405" cy="430" r="12" class="node"/>',
        txt(275, 520, "one simple cycle: dim ker A = 1", "body", "middle"),
        txt(275, 555, "endpoints and edges are already identified", "small", "middle"),
        # Parallel line-identity cycle.
        '<path d="M585 430 C640 370 760 370 815 430" class="parallel"/>',
        '<path d="M585 430 C640 490 760 490 815 430" class="parallel"/>',
        '<circle cx="585" cy="430" r="12" class="node"/><circle cx="815" cy="430" r="12" class="node"/>',
        txt(700, 300, "ℓ₁", "body", "middle"), txt(700, 565, "ℓ₂", "body", "middle"),
        '<path d="M585 430 L815 430" class="dashed"/>',
        txt(700, 620, "simple projection: one edge", "small", "middle"),
        txt(700, 645, "identified multigraph: a two-edge cycle", "small", "middle"),
        # Radial tail.
        '<path d="M1030 350 L1130 350 L1230 430 L1300 530" class="tail"/>',
        '<circle cx="1030" cy="350" r="12" class="node"/><circle cx="1130" cy="350" r="12" class="node"/><circle cx="1230" cy="430" r="12" class="node"/><circle cx="1300" cy="530" r="12" class="leaf"/>',
        txt(1300, 575, "leaf", "body", "middle"),
        txt(1165, 640, "maximal bridge path ending at a leaf", "small", "middle"),
        txt(40, 740, "Thus “radial” may mean a forest in the simple graph, a forest in the identified multigraph, or an active-state forest after switches/outages are applied.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def map_of_maps() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="820" viewBox="0 0 1400 820">',
        '<title>Map of maps from one source architecture</title>',
        '<desc>A typed source architecture feeds multigraph, simple topology, port-factor, OPF, and sparsity views through distinct maps, each annotated with the query it supports.</desc>',
        '<rect width="1400" height="820" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.source{fill:#eee8f8;stroke:#7856a8;stroke-width:3}.view{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.query{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.arrow{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}.dashed{stroke:#8a4f13;stroke-width:2;stroke-dasharray:8 6;fill:none;marker-end:url(#arrow)}.head{font-size:19px;font-weight:bold}.body{font-size:15px}.small{font-size:14px;fill:#5f6b76}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 46, "One source architecture, several typed maps", "title"),
        txt(40, 76, "A view is useful because a declared map supports a query—not because it sits higher or lower in a universal hierarchy.", "sub"),
        '<rect x="55" y="285" width="290" height="150" rx="14" class="source"/>',
        txt(200, 335, "hierarchical source", "head", "middle"), txt(200, 365, "assets · ports · factors", "body", "middle"), txt(200, 392, "states · limits · provenance", "small", "middle"),
    ]
    views = [
        (470, 145, "bus–branch multigraph", "Cₘ", "PF/OPF incidence", "parallel identity retained"),
        (840, 145, "simple topology", "πₛ", "islands/partitioning", "parallel fibre forgotten"),
        (470, 430, "port–factor", "Cₚ", "multiconductor equations", "terminal maps retained"),
        (840, 430, "OPF equation view", "Cₒ", "decisions and limits", "constraint rows explicit"),
        (470, 650, "sparsity/Jacobian", "δ", "ordering and fill", "dependency graph"),
    ]
    for x, y, title, mapname, query, detail in views:
        lines += [f'<rect x="{x}" y="{y}" width="280" height="105" rx="12" class="view"/>', txt(x + 140, y + 30, title, "head", "middle"), txt(x + 140, y + 56, mapname + " · " + query, "body", "middle"), txt(x + 140, y + 82, detail, "small", "middle")]
        lines.append(f'<path d="M345 360 C390 {y + 50} 420 {y + 50} {x - 15} {y + 50}" class="arrow"/>')
    lines += [
        '<rect x="1050" y="650" width="280" height="105" rx="12" class="query"/>',
        txt(1190, 682, "preservation contract", "head", "middle"),
        txt(1190, 710, "observation + recovery", "body", "middle"),
        txt(1190, 735, "scope and refusal", "small", "middle"),
        '<path d="M750 702 L1035 702" class="dashed"/>',
        txt(890, 685, "every view needs a contract", "small", "middle"),
        txt(55, 790, "Maps may be quotients, compilers, coordinate changes, or eliminations; the source and target object sets must be named.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def kron_fill_in() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="760" viewBox="0 0 1400 760">',
        '<title>Kron reduction creates a boundary fill edge</title>',
        '<desc>Two panels show a boundary-internal partition before and after Schur elimination. Eliminating the internal junction creates a dense boundary coupling that is exact for the retained linear relation but not a physical asset.</desc>',
        '<rect width="1400" height="760" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:20px;font-weight:bold}.small{font-size:14px;fill:#5f6b76}.boundary{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.internal{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.edge{stroke:#3979b8;stroke-width:5}.fill{stroke:#c97126;stroke-width:5;stroke-dasharray:10 7}.arrow{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 46, "Kron reduction: exact boundary relation, new computational coupling", "title"),
        txt(40, 76, "The Schur complement eliminates internal variables; the dashed edge is a reduced coefficient, not a newly discovered line.", "sub"),
        '<rect x="40" y="120" width="610" height="520" rx="14" class="panel"/>',
        '<rect x="750" y="120" width="610" height="520" rx="14" class="panel"/>',
        txt(70, 160, "partitioned source relation", "head"), txt(780, 160, "reduced boundary relation", "head"),
        '<circle cx="160" cy="380" r="34" class="boundary"/><circle cx="520" cy="380" r="34" class="boundary"/><circle cx="340" cy="300" r="34" class="internal"/>',
        txt(160, 386, "b₁", "head", "middle"), txt(520, 386, "b₂", "head", "middle"), txt(340, 306, "i", "head", "middle"),
        '<line x1="190" y1="365" x2="310" y2="315" class="edge"/><line x1="370" y1="315" x2="490" y2="365" class="edge"/><line x1="160" y1="414" x2="520" y2="414" class="edge"/>',
        txt(340, 505, "Y = [YBB  YBI; YIB  YII]", "body", "middle"), txt(340, 540, "internal block YII invertible", "small", "middle"),
        '<circle cx="870" cy="380" r="34" class="boundary"/><circle cx="1240" cy="380" r="34" class="boundary"/>',
        txt(870, 386, "b₁", "head", "middle"), txt(1240, 386, "b₂", "head", "middle"),
        '<line x1="905" y1="380" x2="1205" y2="380" class="fill"/>',
        txt(1055, 345, "−YBI YII⁻¹ YIB", "body", "middle"), txt(1055, 430, "Yᵏ = YBB − YBI YII⁻¹ YIB", "body", "middle"),
        txt(1055, 505, "exact for the retained boundary relation", "small", "middle"), txt(1055, 540, "internal assets, currents, and limits require recovery", "small", "middle"),
        '<path d="M650 380 L735 380" class="arrow"/>', txt(692, 360, "Schur", "small", "middle"),
        txt(40, 700, "Kron is an elimination map. Realizing the reduced relation as permitted equipment is a separate compilation and certificate problem.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def provenance_lineage() -> str:
    nodes = [(60, "asset x₁", "stable identity"), (330, "ports q₁…q₃", "typed terminals"), (600, "factor Φₓ₁", "multi-terminal law"), (870, "compiled star", "virtual objects"), (1140, "view object", "query target")]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="540" viewBox="0 0 1400 540">',
        '<title>Provenance lineage survives compilation</title>',
        '<desc>A transformer asset is mapped to typed ports, one factor, compiled virtual star objects, and a target view. Each arrow records a map while the source asset identity remains recoverable.</desc>',
        '<rect width="1400" height="540" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.node{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.virtual{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.source{fill:#eee8f8;stroke:#7856a8;stroke-width:3}.contract{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.head{font-size:18px;font-weight:bold}.small{font-size:14px;fill:#5f6b76}.arrow{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}.lineage{stroke:#7856a8;stroke-width:3;stroke-dasharray:8 6;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 46, "Compilation changes objects, not provenance", "title"),
        txt(40, 76, "Virtual objects can support a target view while every target quantity remains traceable to source asset x₁.", "sub"),
    ]
    for idx, (x, title, detail) in enumerate(nodes):
        cls = "source" if idx == 0 else ("virtual" if idx == 3 else "node")
        lines += [f'<rect x="{x}" y="190" width="190" height="95" rx="12" class="{cls}"/>', txt(x + 95, 228, title, "head", "middle"), txt(x + 95, 255, detail, "small", "middle")]
        if idx < len(nodes) - 1:
            lines.append(f'<path d="M{x + 200} 237 L{x + 260} 237" class="arrow"/>')
    lines += [
        '<path d="M155 300 C155 390 1040 390 1235 300" class="lineage"/>',
        '<rect x="420" y="370" width="560" height="75" rx="12" class="contract"/>',
        txt(700, 402, "provenance: source = x₁; map = Cₓ₁; recovery = Rₓ₁", "head", "middle"),
        txt(700, 427, "compiled star is not a replacement asset identity", "small", "middle"),
        txt(40, 500, "The dashed return path is the recovery/provenance obligation used by decisions, outages, maintenance, and limit checks.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def active_radiality() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="760" viewBox="0 0 1400 760">',
        '<title>Inventory and active-state radiality differ</title>',
        '<desc>Two panels compare an inventory with a parallel pair and an active state in which one member is open. The simple projection is radial in both panels, while member-radiality changes only after the outage.</desc>',
        '<rect width="1400" height="760" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:30px;font-weight:bold}.sub{font-size:17px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.node{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.edge{stroke:#3979b8;stroke-width:5;fill:none}.open{stroke:#8a3232;stroke-width:5;stroke-dasharray:10 7;fill:none}.good{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.warn{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.head{font-size:20px;font-weight:bold}.body{font-size:16px}.small{font-size:14px;fill:#5f6b76}</style>',
        txt(40, 46, "Radiality depends on the active member graph", "title"),
        txt(40, 76, "An inventory can hide a line-identity cycle; the active switching state decides whether that cycle is present now.", "sub"),
        '<rect x="40" y="120" width="635" height="500" rx="14" class="panel"/><rect x="725" y="120" width="635" height="500" rx="14" class="panel"/>',
        txt(70, 160, "inventory: two parallel members", "head"), txt(755, 160, "active state σ: one member open", "head"),
        '<circle cx="180" cy="360" r="28" class="node"/><circle cx="535" cy="360" r="28" class="node"/>',
        '<path d="M205 340 C280 280 435 280 510 340" class="edge"/><path d="M205 380 C280 440 435 440 510 380" class="edge"/>',
        txt(355, 280, "ℓ₁", "body", "middle"), txt(355, 470, "ℓ₂", "body", "middle"), txt(355, 535, "simple projection: forest", "small", "middle"), txt(355, 565, "member graph: cycle → not radial", "body", "middle"),
        '<circle cx="865" cy="360" r="28" class="node"/><circle cx="1220" cy="360" r="28" class="node"/>',
        '<path d="M890 340 C965 280 1120 280 1195 340" class="edge"/><path d="M890 380 C965 440 1120 440 1195 380" class="open"/>',
        txt(1040, 280, "ℓ₁ active", "body", "middle"), txt(1040, 470, "ℓ₂ open", "body", "middle"), txt(1040, 535, "simple projection: forest", "small", "middle"), txt(1040, 565, "active member graph: tree → radial", "body", "middle"),
        '<rect x="500" y="650" width="400" height="55" rx="12" class="good"/>', txt(700, 684, "report both predicates and the state σ", "body", "middle"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def topology_projection_layers() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="790" viewBox="0 0 1400 790">',
        '<title>Two topology levels and one nodal-admittance projection</title>',
        '<desc>Three panels trace two parallel multiconductor line objects from an identified equipment-level multigraph, through explicit ports, conductor-terminal junctions, and separate factors, into one block edge in the support graph of the assembled nodal admittance matrix.</desc>',
        '<rect width="1400" height="790" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:29px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:19px;font-weight:bold}.body{font-size:15px}.small{font-size:13px;fill:#5f6b76}.bus{fill:#d9eef8;stroke:#245b7a;stroke-width:3}.factor{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.port{fill:white;stroke:#8a4f13;stroke-width:2}.algebra{fill:#eee8f8;stroke:#7856a8;stroke-width:2}.physical{stroke:#245b7a;stroke-width:5;fill:none}.wire{stroke:#8a4f13;stroke-width:2.5;fill:none}.support{stroke:#7856a8;stroke-width:6;fill:none}.arrow{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}.lost{stroke:#5f6b76;stroke-width:2;stroke-dasharray:8 6;fill:none}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 44, "One network, two topology levels, one algebraic projection", "title"),
        txt(40, 72, "Equipment identity and conductor incidence are source structure; matrix support is a derived computational view.", "sub"),
        '<rect x="35" y="110" width="405" height="590" rx="14" class="panel"/>',
        '<rect x="495" y="110" width="405" height="590" rx="14" class="panel"/>',
        '<rect x="955" y="110" width="405" height="590" rx="14" class="panel"/>',
        txt(60, 150, "1  identified equipment topology", "head"),
        txt(520, 150, "2  conductor / port–factor topology", "head"),
        txt(980, 150, "3  block support of Yᴺ", "head"),
        # High-level identified multigraph.
        '<circle cx="125" cy="350" r="34" class="bus"/><circle cx="350" cy="350" r="34" class="bus"/>',
        txt(125, 357, "i", "head", "middle"), txt(350, 357, "j", "head", "middle"),
        '<path d="M157 335 C210 275 270 275 318 335" class="physical"/>',
        '<path d="M157 365 C210 425 270 425 318 365" class="physical"/>',
        txt(238, 272, "ℓ₁", "body", "middle"), txt(238, 454, "ℓ₂", "body", "middle"),
        txt(237, 525, "same buses; distinct assets", "body", "middle"),
        txt(237, 552, "ratings, states, owners retained", "small", "middle"),
        txt(237, 620, "parallel fibre {ℓ₁, ℓ₂}", "small", "middle"),
        # Low-level terminal junctions and line factors. Two factors attach to the same junctions.
        '<circle cx="555" cy="260" r="20" class="bus"/><circle cx="555" cy="445" r="20" class="bus"/>',
        '<circle cx="840" cy="260" r="20" class="bus"/><circle cx="840" cy="445" r="20" class="bus"/>',
        txt(555, 266, "i/a", "small", "middle"), txt(555, 451, "i/n", "small", "middle"),
        txt(840, 266, "j/a", "small", "middle"), txt(840, 451, "j/n", "small", "middle"),
        '<rect x="650" y="215" width="95" height="90" rx="12" class="factor"/>',
        '<rect x="650" y="400" width="95" height="90" rx="12" class="factor"/>',
        txt(697, 252, "factor ℓ₁", "body", "middle"), txt(697, 276, "full Y(ℓ₁)", "small", "middle"),
        txt(697, 437, "factor ℓ₂", "body", "middle"), txt(697, 461, "full Y(ℓ₂)", "small", "middle"),
        '<path d="M575 260 L650 235 M575 445 L650 285 M745 235 L820 260 M745 285 L820 445" class="wire"/>',
        '<path d="M575 260 L650 420 M575 445 L650 470 M745 420 L820 260 M745 470 L820 445" class="wire"/>',
        '<circle cx="650" cy="235" r="6" class="port"/><circle cx="650" cy="285" r="6" class="port"/><circle cx="745" cy="235" r="6" class="port"/><circle cx="745" cy="285" r="6" class="port"/>',
        '<circle cx="650" cy="420" r="6" class="port"/><circle cx="650" cy="470" r="6" class="port"/><circle cx="745" cy="420" r="6" class="port"/><circle cx="745" cy="470" r="6" class="port"/>',
        txt(697, 545, "ports may share a junction", "body", "middle"),
        txt(697, 570, "factor decomposition remains explicit", "small", "middle"),
        txt(697, 600, "open circles = factor ports", "small", "middle"),
        txt(697, 625, "shared attachment is not aggregation", "small", "middle"),
        '<path d="M520 665 L575 665" class="wire"/><text x="585" y="670" class="small" text-anchor="start">j: port → junction</text>',
        '<path d="M720 665 L775 665" class="wire"/><text x="785" y="670" class="small" text-anchor="start">f: port → factor</text>',
        # Algebraic block support and summed off-diagonal block.
        '<rect x="1010" y="235" width="120" height="120" rx="12" class="algebra"/>',
        '<rect x="1185" y="235" width="120" height="120" rx="12" class="algebra"/>',
        txt(1070, 282, "node block i", "body", "middle"), txt(1070, 312, "[a,n]", "small", "middle"),
        txt(1245, 282, "node block j", "body", "middle"), txt(1245, 312, "[a,n]", "small", "middle"),
        '<path d="M1132 295 L1183 295" class="support"/>',
        txt(1157, 215, "one support edge", "small", "middle"),
        '<rect x="1015" y="420" width="285" height="90" rx="12" class="algebra"/>',
        txt(1157, 455, "Yᴺ[i,j] = Y(ℓ₁)[i,j] + Y(ℓ₂)[i,j]", "body", "middle"),
        txt(1157, 482, "a dense conductor block is possible", "small", "middle"),
        '<path d="M1015 565 L1300 565" class="lost"/>',
        txt(1157, 603, "support retains coupling", "body", "middle"),
        txt(1157, 630, "but not the decomposition into ℓ₁ and ℓ₂", "small", "middle"),
        # Cross-panel maps.
        '<path d="M442 390 L482 390" class="arrow"/>', txt(462, 370, "lift", "small", "middle"),
        '<path d="M902 390 L942 390" class="arrow"/>', txt(922, 370, "stamp", "small", "middle"),
        txt(40, 755, "The last map is many-to-one: different asset/factor decompositions can assemble to the same nodal operator.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def radial_clique_projection() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="760" viewBox="0 0 1400 760">',
        '<title>A radial asset graph can have a cyclic conductor-expanded support graph</title>',
        '<desc>The left panel is a three-bus tree with two multiconductor lines. The right panel expands each bus into two conductor nodes and shows the clique support induced by dense line stamps. Cycles on the right are algebraic coupling cycles, not additional physical line routes.</desc>',
        '<rect width="1400" height="760" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:29px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:20px;font-weight:bold}.body{font-size:15px}.small{font-size:13px;fill:#5f6b76}.bus{fill:#d9eef8;stroke:#245b7a;stroke-width:3}.macro{stroke:#245b7a;stroke-width:6;fill:none}.scalar{stroke:#7856a8;stroke-width:2.5;fill:none}.shared{stroke:#8a4f13;stroke-width:4;fill:none}.guide{stroke:#8a4f13;stroke-width:2;stroke-dasharray:6 5;fill:none}.arrow{stroke:#17212b;stroke-width:3;fill:none;marker-end:url(#arrow)}.note{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 44, "Radial at the macro level can be cyclic after conductor expansion", "title"),
        txt(40, 72, "With dense multiconductor stamps, each physical line can induce a clique in scalar matrix support.", "sub"),
        '<rect x="40" y="115" width="500" height="535" rx="14" class="panel"/>',
        '<rect x="650" y="115" width="710" height="535" rx="14" class="panel"/>',
        txt(70, 155, "equipment / bus-level topology", "head"), txt(680, 155, "conductor-expanded matrix support", "head"),
        # Macro tree.
        '<circle cx="145" cy="370" r="35" class="bus"/><circle cx="290" cy="270" r="35" class="bus"/><circle cx="435" cy="370" r="35" class="bus"/>',
        '<line x1="174" y1="350" x2="261" y2="290" class="macro"/><line x1="319" y1="290" x2="406" y2="350" class="macro"/>',
        txt(145, 377, "i", "head", "middle"), txt(290, 277, "j", "head", "middle"), txt(435, 377, "k", "head", "middle"),
        txt(215, 300, "ℓ₁", "body", "middle"), txt(365, 300, "ℓ₂", "body", "middle"),
        txt(290, 455, "tree: μ = 0", "body", "middle"),
        txt(290, 490, "one path between each bus pair", "small", "middle"),
        # Expanded two-conductor nodes, laid out as bus columns.
        '<circle cx="750" cy="280" r="24" class="bus"/><circle cx="750" cy="465" r="24" class="bus"/>',
        '<circle cx="1005" cy="280" r="24" class="bus"/><circle cx="1005" cy="465" r="24" class="bus"/>',
        '<circle cx="1260" cy="280" r="24" class="bus"/><circle cx="1260" cy="465" r="24" class="bus"/>',
        txt(750, 286, "i/a", "small", "middle"), txt(750, 471, "i/n", "small", "middle"),
        txt(1005, 286, "j/a", "small", "middle"), txt(1005, 471, "j/n", "small", "middle"),
        txt(1260, 286, "k/a", "small", "middle"), txt(1260, 471, "k/n", "small", "middle"),
        # K4 support for each dense two-conductor line stamp. Shared j-column edge is highlighted.
        '<line x1="774" y1="280" x2="981" y2="280" class="scalar"/><line x1="774" y1="465" x2="981" y2="465" class="scalar"/>',
        '<line x1="770" y1="299" x2="985" y2="446" class="scalar"/><line x1="770" y1="446" x2="985" y2="299" class="scalar"/>',
        '<line x1="750" y1="304" x2="750" y2="441" class="scalar"/><line x1="1005" y1="304" x2="1005" y2="441" class="shared"/>',
        '<line x1="1029" y1="280" x2="1236" y2="280" class="scalar"/><line x1="1029" y1="465" x2="1236" y2="465" class="scalar"/>',
        '<line x1="1025" y1="299" x2="1240" y2="446" class="scalar"/><line x1="1025" y1="446" x2="1240" y2="299" class="scalar"/>',
        '<line x1="1260" y1="304" x2="1260" y2="441" class="scalar"/>',
        txt(878, 225, "clique from ℓ₁", "small", "middle"), txt(1132, 225, "clique from ℓ₂", "small", "middle"),
        txt(1005, 188, "separator {j/a, j/n}", "small", "middle"), '<path d="M1005 195 L1005 250" class="guide"/>',
        txt(1005, 525, "perfect order: all i → all k → all j coordinates; zero fill", "small", "middle"),
        '<rect x="775" y="545" width="460" height="70" rx="12" class="note"/>',
        txt(1005, 575, "matrix cycles ≠ additional physical routes", "body", "middle"),
        txt(1005, 598, "cliques meet on a bus-coordinate separator", "small", "middle"),
        '<path d="M542 370 L635 370" class="arrow"/>', txt(589, 345, "expand + stamp", "small", "middle"),
        txt(40, 710, "The clique claim is conditional on the nonzero pattern of the primitive stamp; absent coupling removes scalar support edges.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def source_views_surgery() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="820" viewBox="0 0 1400 820">',
        '<title>One source graph, four views, and three state-conditioned surgeries</title>',
        '<desc>A canonical source graph with identified equipment and ports maps to single-line, port-factor, lowered-edge, and nodal-support views. Three surgery outputs show open-switch zones, a phase-only state, and an unknown-state family.</desc>',
        '<rect width="1400" height="820" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:28px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:18px;font-weight:bold}.body{font-size:14px}.small{font-size:13px;fill:#5f6b76}.source{fill:#d9eef8;stroke:#245b7a;stroke-width:3}.view{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.lower{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.surgery{fill:#f4e5e5;stroke:#8a3232;stroke-width:2}.arrow{stroke:#17212b;stroke-width:2.5;fill:none;marker-end:url(#arrow)}.dashed{stroke:#8a3232;stroke-width:2.5;stroke-dasharray:8 6;fill:none;marker-end:url(#arrow)}.edge{stroke:#245b7a;stroke-width:4}.thin{stroke:#477a55;stroke-width:2}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 42, "One source graph, four views, and three surgeries", "title"),
        txt(40, 70, "Each arrow is typed: it records what survives, what is forgotten, and which state selects the output.", "sub"),
        '<rect x="40" y="105" width="350" height="300" rx="14" class="panel"/>',
        txt(65, 140, "canonical source", "head"),
        '<circle cx="120" cy="240" r="30" class="source"/><circle cx="250" cy="180" r="30" class="source"/><circle cx="250" cy="300" r="30" class="source"/>',
        '<line x1="145" y1="225" x2="225" y2="195" class="edge"/><line x1="145" y1="255" x2="225" y2="285" class="edge"/>',
        txt(120, 246, "B_i", "head", "middle"), txt(250, 186, "B_j", "head", "middle"), txt(250, 306, "B_k", "head", "middle"),
        txt(185, 202, "X1", "small", "middle"), txt(185, 288, "S1", "small", "middle"),
        txt(65, 352, "identities + ordered ports + states", "body"),
        txt(65, 376, "source fibres remain available", "small"),
        '<rect x="450" y="105" width="870" height="300" rx="14" class="panel"/>',
        txt(475, 140, "typed views", "head"),
        '<rect x="490" y="185" width="170" height="120" rx="12" class="view"/><rect x="700" y="185" width="170" height="120" rx="12" class="view"/><rect x="910" y="185" width="170" height="120" rx="12" class="lower"/><rect x="1120" y="185" width="155" height="120" rx="12" class="view"/>',
        txt(575, 220, "single-line", "head", "middle"), txt(575, 247, "quotient", "small", "middle"), txt(575, 270, "partial reverse map", "small", "middle"), txt(575, 292, "exactness: target-relative", "small", "middle"),
        txt(785, 220, "port–factor", "head", "middle"), txt(785, 247, "canonical", "small", "middle"), txt(785, 270, "identity retained", "small", "middle"), txt(785, 292, "exactness: source model", "small", "middle"),
        txt(995, 220, "lowered edges", "head", "middle"), txt(995, 247, "algorithm target", "small", "middle"), txt(995, 270, "fibre required", "small", "middle"), txt(995, 292, "exactness: guarded", "small", "middle"),
        txt(1197, 220, "nodal support", "head", "middle"), txt(1197, 247, "many-to-one", "small", "middle"), txt(1197, 270, "no identity recovery", "small", "middle"), txt(1197, 292, "no feasible-set claim", "small", "middle"),
        '<path d="M392 170 C445 170 485 180 575 180" class="arrow"/><path d="M392 210 C470 210 535 180 785 180" class="arrow"/><path d="M392 250 C480 250 590 180 995 180" class="arrow"/><path d="M392 290 C500 290 650 180 1197 180" class="arrow"/>',
        '<rect x="490" y="325" width="785" height="45" rx="10" class="view"/>',
        '<path d="M575 305 L575 325" class="dashed"/><path d="M785 305 L785 325" class="dashed"/><path d="M995 305 L995 325" class="dashed"/><path d="M1197 305 L1197 325" class="dashed"/>',
        txt(882, 353, "reverse-map status is recorded here; recovery is not implied", "small", "middle"),
        '<rect x="40" y="455" width="1280" height="315" rx="14" class="panel"/>',
        txt(65, 490, "state-conditioned surgery outputs", "head"),
        '<rect x="90" y="535" width="330" height="170" rx="12" class="surgery"/><rect x="535" y="535" width="330" height="170" rx="12" class="surgery"/><rect x="980" y="535" width="290" height="170" rx="12" class="surgery"/>',
        txt(255, 570, "open_all_switches", "head", "middle"), txt(255, 600, "galvanic zones", "body", "middle"), txt(255, 628, "two components", "small", "middle"), txt(255, 665, "state σ = open", "small", "middle"),
        txt(700, 570, "phase-only switch", "head", "middle"), txt(700, 600, "coordinate query", "body", "middle"), txt(700, 628, "phase changes; neutral stays", "small", "middle"), txt(700, 665, "member radiality ≠ bus radiality", "small", "middle"),
        txt(1125, 570, "unknown switch", "head", "middle"), txt(1125, 600, "family return", "body", "middle"), txt(1125, 628, "open and closed cases", "small", "middle"), txt(1125, 665, "diagnostic, not a guess", "small", "middle"),
        '<path d="M210 405 L210 525" class="arrow"/><path d="M700 405 L700 525" class="arrow"/><path d="M1170 405 L1170 525" class="arrow"/>',
        txt(225, 470, "source state", "small"), txt(715, 470, "port state", "small"), txt(1185, 470, "support query", "small"),
        txt(40, 805, "The source object is the semantic anchor; views and surgeries are typed, state-indexed projections with provenance.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def transformer_graph_views() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="860" viewBox="0 0 1400 860">',
        '<title>One multiwinding transformer has several associated graphs</title>',
        '<desc>A three-winding transformer is shown as one identified asset and three-port factor, a pair-test triangle, a generated star with an internal virtual node, and a terminal clique after elimination. A final guard explains that an arbitrary n-winding model is not generally a diagonal star.</desc>',
        '<rect width="1400" height="860" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:29px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:19px;font-weight:bold}.body{font-size:15px}.small{font-size:13px;fill:#5f6b76}.port{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.factor{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.virtual{fill:#eee8f8;stroke:#7856a8;stroke-width:2;stroke-dasharray:7 5}.guard{fill:#f4e5e5;stroke:#8a3232;stroke-width:2}.edge{stroke:#245b7a;stroke-width:3;fill:none}.generated{stroke:#7856a8;stroke-width:3;fill:none;stroke-dasharray:8 5}.arrow{stroke:#17212b;stroke-width:2.5;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 44, "One transformer, several graphs", "title"),
        txt(40, 72, "The object and arrow labels—not the visual shape—state what each construction means.", "sub"),
    ]
    xs = [35, 370, 705, 1040]
    for x in xs:
        lines.append(f'<rect x="{x}" y="115" width="300" height="480" rx="14" class="panel"/>')
    lines += [
        txt(60, 155, "1  source and canonical factor", "head"),
        '<rect x="115" y="245" width="140" height="130" rx="14" class="factor"/>',
        txt(185, 287, "asset x₁", "head", "middle"), txt(185, 315, "one factor", "body", "middle"), txt(185, 342, "arity 3", "small", "middle"),
        '<circle cx="75" cy="235" r="24" class="port"/><circle cx="75" cy="405" r="24" class="port"/><circle cx="295" cy="320" r="24" class="port"/>',
        txt(75, 241, "k1", "small", "middle"), txt(75, 411, "k2", "small", "middle"), txt(295, 326, "k3", "small", "middle"),
        '<line x1="98" y1="247" x2="115" y2="270" class="edge"/><line x1="98" y1="393" x2="115" y2="350" class="edge"/><line x1="255" y1="315" x2="271" y2="318" class="edge"/>',
        txt(185, 490, "identity + winding interfaces", "body", "middle"), txt(185, 520, "limits, state, taps, grounding", "small", "middle"),
        txt(395, 155, "2  pair-test data graph", "head"),
        '<circle cx="440" cy="400" r="25" class="port"/><circle cx="520" cy="245" r="25" class="port"/><circle cx="620" cy="400" r="25" class="port"/>',
        '<line x1="452" y1="378" x2="508" y2="267" class="edge"/><line x1="545" y1="263" x2="605" y2="380" class="edge"/><line x1="465" y1="400" x2="595" y2="400" class="edge"/>',
        txt(440, 406, "1", "body", "middle"), txt(520, 251, "2", "body", "middle"), txt(620, 406, "3", "body", "middle"),
        txt(480, 320, "z₁₂ˢᶜ", "small", "middle"), txt(572, 320, "z₂₃ˢᶜ", "small", "middle"), txt(530, 425, "z₁₃ˢᶜ", "small", "middle"),
        txt(520, 490, "edges index tests", "body", "middle"), txt(520, 520, "not independent transformers", "small", "middle"),
        txt(730, 155, "3  generated star / T", "head"),
        '<circle cx="765" cy="270" r="25" class="port"/><circle cx="765" cy="455" r="25" class="port"/><circle cx="965" cy="360" r="25" class="port"/><circle cx="865" cy="360" r="28" class="virtual"/>',
        '<line x1="789" y1="281" x2="840" y2="338" class="generated"/><line x1="789" y1="444" x2="840" y2="382" class="generated"/><line x1="893" y1="360" x2="940" y2="360" class="generated"/>',
        txt(765, 276, "k1", "small", "middle"), txt(765, 461, "k2", "small", "middle"), txt(965, 366, "k3", "small", "middle"), txt(865, 366, "νₓ₁", "body", "middle"),
        txt(865, 490, "local cycle rank 0", "body", "middle"), txt(865, 520, "virtual node and arms", "small", "middle"),
        txt(1065, 155, "4  terminal clique", "head"),
        '<circle cx="1095" cy="405" r="25" class="port"/><circle cx="1190" cy="245" r="25" class="port"/><circle cx="1290" cy="405" r="25" class="port"/>',
        '<line x1="1108" y1="383" x2="1177" y2="267" class="generated"/><line x1="1214" y1="264" x2="1276" y2="383" class="generated"/><line x1="1120" y1="405" x2="1265" y2="405" class="generated"/>',
        txt(1095, 411, "k1", "small", "middle"), txt(1190, 251, "k2", "small", "middle"), txt(1290, 411, "k3", "small", "middle"),
        txt(1190, 490, "local cycle rank 1", "body", "middle"), txt(1190, 520, "after internal elimination", "small", "middle"),
        '<path d="M337 350 L360 350" class="arrow"/><path d="M672 350 L695 350" class="arrow"/><path d="M1007 350 L1030 350" class="arrow"/>',
        '<rect x="80" y="650" width="1240" height="140" rx="14" class="guard"/>',
        txt(110, 690, "n-winding guard", "head"),
        txt(110, 725, "For n = 3 the full reference relation has the familiar star/T coordinates. For general n, the exact (n−1)×(n−1) reference impedance is generally full.", "body"),
        txt(110, 755, "A diagonal n-arm star, a complete edge graph, and the terminal support graph are therefore guarded target views—not the source transformer.", "body"),
        txt(40, 835, "A tree can become a clique under exact elimination without creating a new physical power-system loop.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def five_bus_transformer_lowering() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="900" viewBox="0 0 1500 900">',
        '<title>The five-bus topology kernel becomes a transformer-lowering laboratory</title>',
        '<desc>Four panels retain the same five buses and line identities while adding a three-port transformer at buses j, l, and m. The panels compare the source n-port factor, a generated star, and a terminal clique, with representation-scoped cycle ranks and a loss ledger.</desc>',
        '<rect width="1500" height="900" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:29px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.head{font-size:19px;font-weight:bold}.body{font-size:14px}.small{font-size:12px;fill:#5f6b76}.bus{fill:white;stroke:#17212b;stroke-width:2}.line{stroke:#3979b8;stroke-width:3;fill:none}.parallel{stroke:#3979b8;stroke-width:3;fill:none}.factor{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.generated{stroke:#7856a8;stroke-width:3;stroke-dasharray:7 5;fill:none}.virtual{fill:#eee8f8;stroke:#7856a8;stroke-width:2;stroke-dasharray:5 4}.warn{fill:#f4e5e5;stroke:#8a3232;stroke-width:2}.arrow{stroke:#17212b;stroke-width:2.5;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 44, "Five buses through a three-port lowering", "title"),
        txt(40, 72, "The line graph Gᴸ remains fixed; the transformer extension branches into several declared target structures.", "sub"),
    ]
    panel_x = [35, 400, 765, 1130]
    titles = ["1  line topology kernel Gᴸ", "2  one three-port factor", "3  optional compiled star", "4  eliminated terminal clique"]
    for x, title in zip(panel_x, titles):
        lines += [f'<rect x="{x}" y="115" width="335" height="570" rx="14" class="panel"/>', txt(x + 22, 153, title, "head")]
    def base(x):
        return [
            f'<circle cx="{x+55}" cy="330" r="20" class="bus"/><circle cx="{x+145}" cy="235" r="20" class="bus"/><circle cx="{x+145}" cy="425" r="20" class="bus"/><circle cx="{x+245}" cy="330" r="20" class="bus"/><circle cx="{x+300}" cy="425" r="20" class="bus"/>',
            f'<path d="M{x+72} 315 C{x+94} 278 {x+113} 265 {x+132} 249" class="parallel"/><path d="M{x+76} 323 C{x+101} 290 {x+119} 276 {x+136} 253" class="parallel"/><path d="M{x+72} 341 C{x+95} 380 {x+115} 390 {x+132} 409" class="parallel"/>',
            f'<line x1="{x+145}" y1="255" x2="{x+145}" y2="405" class="line"/><line x1="{x+164}" y1="242" x2="{x+227}" y2="318" class="line"/><line x1="{x+164}" y1="418" x2="{x+227}" y2="342" class="line"/><line x1="{x+265}" y1="348" x2="{x+288}" y2="407" class="line"/>',
            txt(x+55,336,"i","body","middle"),txt(x+145,241,"j","body","middle"),txt(x+145,431,"k","body","middle"),txt(x+245,336,"l","body","middle"),txt(x+300,431,"m","body","middle"),
        ]
    for x in panel_x: lines += base(x)
    lines += [
        txt(202, 545, "identified lines q,r,s,t,u,v,w", "small", "middle"), txt(202, 575, "member μ = 3; simple μ = 2", "body", "middle"),
        '<rect x="610" y="475" width="72" height="52" rx="10" class="factor"/>', txt(646, 507, "x₁", "head", "middle"),
        '<line x1="610" y1="485" x2="560" y2="250" class="generated"/><line x1="610" y1="500" x2="645" y2="345" class="generated"/><line x1="682" y1="510" x2="695" y2="445" class="generated"/>',
        txt(567, 545, "source asset: one x₁", "body", "middle"), txt(567, 575, "factor incidence μ = 5", "small", "middle"), txt(567, 600, "no ordinary source edge for x₁", "small", "middle"),
        '<circle cx="1030" cy="500" r="22" class="virtual"/>', txt(1030,506,"νₓ₁","small","middle"),
        '<line x1="1030" y1="478" x2="925" y2="250" class="generated"/><line x1="1010" y1="500" x2="1010" y2="345" class="generated"/><line x1="1048" y1="513" x2="1055" y2="443" class="generated"/>',
        txt(932, 555, "generated node + three arms", "body", "middle"), txt(932, 582, "embedded member μ = 5", "small", "middle"), txt(932, 607, "local star μ = 0", "small", "middle"),
        '<line x1="1290" y1="250" x2="1360" y2="315" class="generated"/><line x1="1290" y1="250" x2="1417" y2="410" class="generated"/><line x1="1390" y1="345" x2="1417" y2="410" class="generated"/>',
        txt(1297, 555, "same terminal relation under guards", "body", "middle"), txt(1297, 582, "embedded member μ = 6", "small", "middle"), txt(1297, 607, "local clique μ = 1", "small", "middle"),
        '<path d="M372 400 L390 400" class="arrow"/><path d="M737 400 L755 400" class="arrow"/><path d="M1102 400 L1120 400" class="arrow"/>',
        '<rect x="80" y="735" width="1340" height="105" rx="14" class="warn"/>',
        txt(105, 770, "Loss ledger", "head"),
        txt(250, 770, "generated arms are not lines", "body"), txt(500, 770, "clique edges are not assets", "body"), txt(770, 770, "winding currents need recovery", "body"), txt(1055, 770, "support cycles are not power-flow loops", "body"),
        txt(105, 810, "Retain x₁ identity, winding-to-target fibres, connection/tap/grounding semantics, source limits, and the domain of every exactness claim.", "small"),
        txt(40, 875, "Cycle rank is reported only after the graph construction is named; the source n-port object has no privileged ordinary-edge expansion.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def layer_lens_matrix() -> str:
    rows = [
        ("source asset/property", "asset and winding IDs", "terminal attachments", "nameplate + construction", "states, ratings, ownership", "source schema"),
        ("canonical port–factor", "factor + port ownership", "typed junction incidence", "multi-port relation", "limits, controls, observations", "factor API / IR"),
        ("optional edge realization", "generated source fibres", "virtual nodes + edges", "guarded equivalent", "lifted source constraints", "edge-algorithm adapter"),
        ("equation / operator", "constraint ownership map", "variable incidence", "residuals or Y/MNA/tableau", "feasible set + objective", "solver formulation"),
        ("support / algorithm graph", "external metadata only", "nonzero adjacency", "coupling pattern only", "not native", "sparse / graph / GNN"),
    ]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="900" viewBox="0 0 1500 900">',
        '<title>Construction stages and semantic lenses form a matrix, not a ladder</title>',
        '<desc>Five construction stages are rows and five question lenses are columns. Typed transformations cross rows, while each row can be inspected through identity, connectivity, electrical, decision, and computational lenses.</desc>',
        '<rect width="1500" height="900" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:29px;font-weight:bold}.sub{font-size:16px;fill:#5f6b76}.head{font-size:16px;font-weight:bold}.body{font-size:13px}.small{font-size:12px;fill:#5f6b76}.row{fill:#d9eef8;stroke:#245b7a;stroke-width:2}.cell{fill:#fbfcfd;stroke:#9aa5ad;stroke-width:1.5}.branch{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.warn{fill:#f4e5e5;stroke:#8a3232;stroke-width:2}.arrow{stroke:#17212b;stroke-width:2.5;fill:none;marker-end:url(#arrow)}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#17212b"/></marker></defs>',
        txt(40, 44, "Construction stage × semantic lens", "title"),
        txt(40, 72, "Rows say how the model was constructed; columns say which question is being asked. Software can span several rows.", "sub"),
    ]
    x0, y0, roww, cellw, rowh = 40, 160, 250, 230, 105
    heads = ["identity / provenance", "connectivity", "electrical behaviour", "decisions / constraints", "software / computation"]
    for j, head in enumerate(heads):
        lines += [f'<rect x="{x0+roww+j*cellw}" y="105" width="{cellw}" height="55" class="branch"/>', txt(x0+roww+j*cellw+cellw/2, 138, head, "head", "middle")]
    for i, row in enumerate(rows):
        y = y0 + i * rowh
        lines += [f'<rect x="{x0}" y="{y}" width="{roww}" height="{rowh}" class="row"/>', txt(x0+18, y+43, row[0], "head"), txt(x0+18, y+72, f"stage L{i}", "small")]
        for j, value in enumerate(row[1:]):
            x = x0 + roww + j * cellw
            lines += [f'<rect x="{x}" y="{y}" width="{cellw}" height="{rowh}" class="cell"/>']
            words = value.split(" ")
            if len(words) > 3:
                cut = len(words)//2
                lines += [txt(x+cellw/2, y+45, " ".join(words[:cut]), "body", "middle"), txt(x+cellw/2, y+67, " ".join(words[cut:]), "body", "middle")]
            else:
                lines.append(txt(x+cellw/2, y+56, value, "body", "middle"))
    lines += [
        '<path d="M265 250 L265 280" class="arrow"/><path d="M265 355 L265 385" class="arrow"/><path d="M265 460 L265 490" class="arrow"/><path d="M265 565 L265 595" class="arrow"/>',
        txt(245, 273, "canonicalize", "small", "end"), txt(245, 378, "optional compile", "small", "end"), txt(245, 483, "assemble", "small", "end"), txt(245, 588, "project support", "small", "end"),
        '<rect x="40" y="720" width="1420" height="110" rx="14" class="warn"/>',
        txt(65, 755, "Transformations are typed arrows, not extra layers", "head"),
        txt(65, 785, "Projection, normalization, compilation, elimination, behavioural reduction, approximation, and graph surgery may branch at different rows.", "body"),
        txt(65, 810, "Every branch declares its interface, generated objects, preservation dimensions, omissions, provenance, and recovery status.", "small"),
        txt(40, 875, "No cell is universally ‘more expressive’: sufficiency is relative to the query family and declared transformation contract.", "small"),
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    outputs = {
        "exactness-classes": exactness_classes(),
        "recovery-map-loop": recovery_map(),
        "argument-spine": argument_spine(),
        "query-partial-orders": query_partial_orders(),
        "case-escalation-grid": case_escalation(),
        "vocabulary-bridge-five-languages": vocabulary_bridge(),
        "audience-routes": audience_routes(),
        "sequence-subspace": sequence_subspace(),
        "bus-meaning-overlays": bus_overlay(),
        "certificate-composition": certificate_composition(),
        "guarded-rule-gate": guarded_rule_gate(),
        "spine-band": spine_band(),
        "orientation-power-transfer": orientation_power(),
        "cycles-parallelism-radial-tail": cycles_radial(),
        "map-of-maps": map_of_maps(),
        "kron-fill-in": kron_fill_in(),
        "provenance-lineage": provenance_lineage(),
        "active-radiality": active_radiality(),
        "topology-projection-layers": topology_projection_layers(),
        "radial-clique-projection": radial_clique_projection(),
        "source-views-surgery": source_views_surgery(),
        "transformer-graph-views": transformer_graph_views(),
        "five-bus-transformer-lowering": five_bus_transformer_lowering(),
        "layer-lens-matrix": layer_lens_matrix(),
    }
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise SystemExit("rsvg-convert is required to create PNG companions")
    for stem, content in outputs.items():
        svg = ASSETS / f"{stem}.svg"
        png = ASSETS / f"{stem}.png"
        svg.write_text(content)
        subprocess.run([converter, "-o", str(png), str(svg)], check=True)
    print("rendered " + ", ".join(outputs))


if __name__ == "__main__":
    main()
