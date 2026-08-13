#!/usr/bin/env python3
"""Render a pedagogical figure set from the verified five-bus analysis.

The graph data, line orientations, spanning tree, chords, cycle ranks, and
parallel-limit witness come from the Julia-generated JSON artifact. Layout and
visual semantics live here. The three committed PNGs are therefore views of
one executable source rather than independently maintained drawings.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "experiments" / "generated" / "five-bus-cycle-space-analysis.json"
ASSETS = ROOT / "docs" / "src" / "assets"
MANIFEST = ROOT / "experiments" / "generated" / "five-bus-figure-manifest.json"
OUTPUTS = {
    "cycle_basis": ASSETS / "five-bus-cycle-basis.png",
    "transformation_map": ASSETS / "five-bus-transformation-map.png",
    "feasible_sets": ASSETS / "five-bus-feasible-sets.png",
}

INK = "#17212b"
MUTED = "#5f6b76"
GRID = "#d8e0e7"
PAPER = "#f6f8fa"
WHITE = "#ffffff"
BLUE = "#3979b8"
ORANGE = "#c97126"
GREEN = "#35805a"
RED = "#bd3f3f"
PURPLE = "#7758a6"
FADED = "#cbd3da"
PALE_BLUE = "#edf5fb"
PALE_ORANGE = "#fff3e5"
PALE_GREEN = "#eaf5ee"
PALE_RED = "#fbecec"
PALE_PURPLE = "#f1ecf8"


def getfont(size: int, bold: bool = False):
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


TITLE = getfont(48, True)
PANEL = getfont(31, True)
HEADING = getfont(27, True)
LABEL = getfont(23, True)
BODY = getfont(22)
SMALL = getfont(19)
TINY = getfont(17)


def load_analysis():
    with ANALYSIS.open() as stream:
        return json.load(stream)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def center_text(draw, point, text, font=BODY, fill=INK):
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(
        (point[0] - (box[2] - box[0]) / 2, point[1] - (box[3] - box[1]) / 2),
        text,
        font=font,
        fill=fill,
    )


def text_block(draw, xy, lines, font=BODY, fill=INK, spacing=8):
    if isinstance(lines, str):
        lines = [lines]
    y = xy[1]
    for line in lines:
        draw.text((xy[0], y), line, font=font, fill=fill)
        box = draw.textbbox((0, 0), line, font=font)
        y += box[3] - box[1] + spacing
    return y


def card(draw, box, fill=WHITE, outline=GRID, radius=20, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def badge(draw, xy, text, fill, foreground=INK):
    box = draw.textbbox((0, 0), text, font=SMALL)
    w, h = box[2] - box[0] + 24, box[3] - box[1] + 15
    draw.rounded_rectangle((xy[0], xy[1], xy[0] + w, xy[1] + h), radius=13, fill=fill)
    center_text(draw, (xy[0] + w / 2, xy[1] + h / 2 - 1), text, SMALL, foreground)
    return w, h


def graph_points(box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    return {
        "i": (x0 + 0.10 * w, y0 + 0.50 * h),
        "j": (x0 + 0.38 * w, y0 + 0.18 * h),
        "k": (x0 + 0.38 * w, y0 + 0.82 * h),
        "l": (x0 + 0.72 * w, y0 + 0.50 * h),
        "m": (x0 + 0.94 * w, y0 + 0.50 * h),
    }


def edge_path(edge_id, points):
    i, j, k, l, m = (points[name] for name in ("i", "j", "k", "l", "m"))
    if edge_id == "q":
        return [j, ((i[0] + j[0]) / 2 - 25, j[1] + 45), i]
    if edge_id == "r":
        return [i, ((i[0] + j[0]) / 2 + 35, i[1] - 20), j]
    return {
        "s": [j, k],
        "t": [k, i],
        "v": [l, j],
        "w": [k, l],
        "x": [l, m],
    }[edge_id]


def point_on_polyline(points, fraction):
    lengths = [math.dist(a, b) for a, b in zip(points[:-1], points[1:])]
    target = sum(lengths) * fraction
    for a, b, length in zip(points[:-1], points[1:], lengths):
        if target <= length:
            ratio = target / length if length else 0
            point = (a[0] + ratio * (b[0] - a[0]), a[1] + ratio * (b[1] - a[1]))
            return point, math.atan2(b[1] - a[1], b[0] - a[0])
        target -= length
    a, b = points[-2:]
    return b, math.atan2(b[1] - a[1], b[0] - a[0])


def draw_dashed_segment(draw, a, b, fill, width=7, dash=18, gap=12):
    length = math.dist(a, b)
    if not length:
        return
    dx, dy = b[0] - a[0], b[1] - a[1]
    offset = 0.0
    while offset < length:
        end = min(offset + dash, length)
        draw.line(
            (
                a[0] + dx * offset / length,
                a[1] + dy * offset / length,
                a[0] + dx * end / length,
                a[1] + dy * end / length,
            ),
            fill=fill,
            width=width,
        )
        offset += dash + gap


def draw_polyline(draw, points, fill, width=7, dashed=False):
    for a, b in zip(points[:-1], points[1:]):
        if dashed:
            draw_dashed_segment(draw, a, b, fill, width)
        else:
            draw.line((*a, *b), fill=fill, width=width)


def arrowhead(draw, points, fill):
    (x, y), angle = point_on_polyline(points, 0.64)
    size = 13
    tip = (x + size * math.cos(angle), y + size * math.sin(angle))
    left = (x + size * math.cos(angle + 2.45), y + size * math.sin(angle + 2.45))
    right = (x + size * math.cos(angle - 2.45), y + size * math.sin(angle - 2.45))
    draw.polygon([tip, left, right], fill=fill)


def edge_label(draw, point, text, fill=INK):
    box = draw.textbbox((0, 0), text, font=TINY)
    pad = 5
    card(
        draw,
        (
            point[0] - (box[2] - box[0]) / 2 - pad,
            point[1] - (box[3] - box[1]) / 2 - pad,
            point[0] + (box[2] - box[0]) / 2 + pad,
            point[1] + (box[3] - box[1]) / 2 + pad,
        ),
        fill=WHITE,
        outline=WHITE,
        radius=6,
        width=1,
    )
    center_text(draw, point, text, TINY, fill)


def edge_label_point(edge_id, path):
    point, _ = point_on_polyline(path, 0.50)
    offsets = {
        "q": (-6, -22), "r": (18, 18), "s": (20, 0), "t": (-10, 22),
        "v": (5, -18), "w": (12, 20), "x": (0, -20),
    }
    dx, dy = offsets[edge_id]
    return point[0] + dx, point[1] + dy


def node(draw, point, name, role=None, role_offset=(0, 43)):
    radius = 25
    draw.ellipse(
        (point[0] - radius, point[1] - radius, point[0] + radius, point[1] + radius),
        fill=WHITE,
        outline=INK,
        width=4,
    )
    center_text(draw, (point[0], point[1] - 2), name, LABEL)
    if role:
        center_text(draw, (point[0] + role_offset[0], point[1] + role_offset[1]), role, TINY, MUTED)


def edge_records(analysis):
    return {edge["line"]: edge for edge in analysis["source"]["forward_topology"]}


def draw_graph(
    draw,
    analysis,
    box,
    *,
    selected: Iterable[str] | None = None,
    tree: Iterable[str] | None = None,
    chords: Iterable[str] | None = None,
    collapsed_parallel=False,
    show_directions=False,
    show_roles=False,
    show_labels=True,
):
    points = graph_points(box)
    selected = set(selected) if selected is not None else None
    tree, chords = set(tree or []), set(chords or [])
    records = edge_records(analysis)

    draw_ids = ["q", "r", "s", "t", "v", "w", "x"]
    if collapsed_parallel:
        draw_ids = ["e_ij", "s", "t", "v", "w", "x"]

    for edge_id in draw_ids:
        source_id = "r" if edge_id == "e_ij" else edge_id
        path = [points["i"], points["j"]] if edge_id == "e_ij" else edge_path(edge_id, points)
        if selected is not None:
            color = BLUE if source_id in selected or edge_id in selected else FADED
            width = 8 if source_id in selected or edge_id in selected else 4
        elif edge_id in chords:
            color, width = ORANGE, 7
        elif edge_id in tree:
            color, width = BLUE, 8
        elif edge_id == "e_ij":
            color, width = GREEN, 10
        else:
            color, width = BLUE, 7
        draw_polyline(draw, path, color, width, dashed=edge_id in chords)
        if show_directions and edge_id != "e_ij":
            arrowhead(draw, path, color)
        if show_labels:
            label = "e_ij" if edge_id == "e_ij" else records[edge_id]["line"]
            edge_label(draw, edge_label_point(source_id, path), label, color if color != FADED else MUTED)

    roles = {
        "i": ("source", (0, 43)),
        "j": ("load d1", (58, 8)),
        "k": ("load d2", (0, 43)),
    } if show_roles else {}
    for name, point in points.items():
        role, offset = roles.get(name, (None, (0, 43)))
        node(draw, point, name, role, offset)
    return points


def title_block(draw, title, subtitle):
    draw.text((65, 42), title, font=TITLE, fill=INK)
    draw.text((65, 102), subtitle, font=BODY, fill=MUTED)


def render_cycle_basis(analysis):
    image = Image.new("RGB", (2400, 1180), PAPER)
    draw = ImageDraw.Draw(image)
    title_block(
        draw,
        "The missing cycle is only visible when lines keep their names",
        "A vertex-only description collapses q and r; the source multigraph has three independent line cycles.",
    )

    card(draw, (45, 165, 875, 1095))
    draw.text((80, 195), "Source multigraph", font=PANEL, fill=INK)
    badge(draw, (80, 245), "7 lines - 5 buses + 1 = 3 cycles", PALE_BLUE, BLUE)
    draw_graph(draw, analysis, (80, 330, 835, 900), show_directions=True, show_roles=True)
    text_block(
        draw,
        (80, 960),
        ["q and r share endpoints but remain different assets.", "x is the only bridge; it belongs to no cycle."],
        SMALL,
        MUTED,
        6,
    )

    cycle_cards = [
        ("C_q", ["q", "r"], "parallel two-edge cycle", BLUE),
        ("C_t", ["r", "s", "t"], "left triangle", ORANGE),
        ("C_v", ["s", "v", "w"], "right triangle", GREEN),
    ]
    for index, (name, members, description, color) in enumerate(cycle_cards):
        x0 = 925 + index * 475
        card(draw, (x0, 165, x0 + 430, 1095))
        draw.text((x0 + 28, 195), name, font=PANEL, fill=color)
        draw.text((x0 + 28, 240), description, font=SMALL, fill=MUTED)
        draw_graph(draw, analysis, (x0 + 15, 320, x0 + 415, 690), selected=members)
        card(draw, (x0 + 25, 760, x0 + 405, 890), fill={BLUE: PALE_BLUE, ORANGE: PALE_ORANGE, GREEN: PALE_GREEN}[color], outline=WHITE)
        center_text(draw, (x0 + 215, 800), " + ".join(members), LABEL, color)
        center_text(draw, (x0 + 215, 845), "signed columns sum to zero", SMALL, MUTED)
        center_text(draw, (x0 + 215, 955), "A c_{} = 0".format(name[-1]), LABEL, INK)
        center_text(draw, (x0 + 215, 1010), "line-indexed, not vertex-only", SMALL, MUTED)

    OUTPUTS["cycle_basis"].parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUTS["cycle_basis"], optimize=True)


def connector(draw, start, end, color=INK, label=None):
    draw.line((*start, *end), fill=color, width=5)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    size = 15
    left = (end[0] + size * math.cos(angle + 2.5), end[1] + size * math.sin(angle + 2.5))
    right = (end[0] + size * math.cos(angle - 2.5), end[1] + size * math.sin(angle - 2.5))
    draw.polygon([end, left, right], fill=color)
    if label:
        midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 - 18)
        edge_label(draw, midpoint, label, color)


def mini_semantic_card(draw, analysis, box, title, badge_text, badge_fill, badge_color, kind):
    x0, y0, x1, y1 = box
    card(draw, box)
    draw.text((x0 + 28, y0 + 24), title, font=HEADING, fill=INK)
    badge(draw, (x0 + 28, y0 + 70), badge_text, badge_fill, badge_color)
    graph_box = (x0 + 20, y0 + 125, x1 - 20, y0 + 465)
    if kind in ("projection", "aggregate"):
        draw_graph(draw, analysis, graph_box, collapsed_parallel=True, show_labels=True)
    elif kind == "coordinates":
        draw_graph(
            draw,
            analysis,
            graph_box,
            tree=analysis["cycle_space"]["spanning_tree_lines"],
            chords=analysis["cycle_space"]["chord_lines"],
            show_labels=True,
        )
    lines = {
        "projection": ["cycle rank: 2", "q/r identity and states are forgotten"],
        "aggregate": ["same scalar Ybus", "q/r currents and limits stay lifted"],
        "coordinates": ["cycle rank: 3", "tree is solid; q,t,v remain as chords"],
    }[kind]
    text_block(draw, (x0 + 32, y1 - 105), lines, SMALL, MUTED, 7)


def render_transformation_map(analysis):
    image = Image.new("RGB", (2400, 1600), PAPER)
    draw = ImageDraw.Draw(image)
    title_block(
        draw,
        "One drawing can hide three incompatible meanings",
        "The operation label - not the visual shape - determines what is preserved and what has changed.",
    )

    card(draw, (775, 165, 1625, 560), fill=WHITE)
    draw.text((815, 195), "Identified source multigraph", font=PANEL, fill=INK)
    badge(draw, (815, 245), "physical members q,r,s,t,v,w,x", PALE_BLUE, BLUE)
    draw_graph(draw, analysis, (820, 300, 1580, 525), show_directions=True, show_labels=True)

    left_box = (55, 735, 755, 1345)
    middle_box = (850, 735, 1550, 1345)
    right_box = (1645, 735, 2345, 1345)
    connector(draw, (915, 560), (405, 735), ORANGE, "forget identity")
    connector(draw, (1200, 560), (1200, 735), GREEN, "sum primitives")
    connector(draw, (1485, 560), (1995, 735), PURPLE, "choose coordinates")

    mini_semantic_card(draw, analysis, left_box, "Simple topology", "lossy projection", PALE_ORANGE, ORANGE, "projection")
    mini_semantic_card(draw, analysis, middle_box, "Electrical factor", "exact terminal relation", PALE_GREEN, GREEN, "aggregate")
    mini_semantic_card(draw, analysis, right_box, "Tree plus chords", "coordinate view", PALE_PURPLE, PURPLE, "coordinates")

    card(draw, (1645, 1380, 2345, 1555), fill=PALE_RED, outline=RED, radius=16, width=3)
    draw.text((1675, 1403), "Deleting q, t, or v is different", font=LABEL, fill=RED)
    draw.text((1675, 1448), "It is a state change or topology decision,", font=SMALL, fill=INK)
    draw.text((1675, 1485), "not a spanning-tree coordinate choice.", font=SMALL, fill=INK)

    OUTPUTS["transformation_map"].parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUTS["transformation_map"], optimize=True)


def interval_x(value, minimum, maximum, x0, x1):
    return x0 + (value - minimum) / (maximum - minimum) * (x1 - x0)


def draw_interval(draw, y, lower, upper, axis_min, axis_max, x0, x1, color, label, detail):
    draw.text((90, y - 18), label, font=LABEL, fill=INK)
    left = interval_x(lower, axis_min, axis_max, x0, x1)
    right = interval_x(upper, axis_min, axis_max, x0, x1)
    draw.line((x0, y + 30, x1, y + 30), fill=FADED, width=5)
    draw.line((left, y + 30, right, y + 30), fill=color, width=18)
    draw.ellipse((left - 9, y + 21, left + 9, y + 39), fill=color)
    draw.ellipse((right - 9, y + 21, right + 9, y + 39), fill=color)
    draw.text((90, y + 54), detail, font=SMALL, fill=MUTED)


def render_feasible_sets(analysis):
    witness = analysis["electrical_check"]["parallel_decision_witness"]
    source_limit = witness["source_voltage_limit_V"]
    aggregate_limit = witness["aggregate_voltage_limit_V"]
    test_voltage = witness["voltage_difference_V"]

    image = Image.new("RGB", (2200, 1120), PAPER)
    draw = ImageDraw.Draw(image)
    title_block(
        draw,
        "Same nodal admittance. Different feasible decisions.",
        "Electrical equality does not imply equality of the member-constrained feasible set.",
    )

    card(draw, (55, 165, 2145, 310), fill=PALE_BLUE, outline=WHITE)
    center_text(draw, (1100, 215), "Ybus(source) = Ybus(aggregate)", PANEL, BLUE)
    center_text(draw, (1100, 265), "The current-voltage law agrees exactly before limits are applied.", BODY, MUTED)

    axis_min, axis_max = -20.0, 20.0
    x0, x1 = 560, 2070
    axis_y = 450
    draw.line((x0, axis_y, x1, axis_y), fill=INK, width=4)
    for value in (-20, -15, -10, -5, 0, 5, 10, 15, 20):
        x = interval_x(value, axis_min, axis_max, x0, x1)
        draw.line((x, axis_y - 10, x, axis_y + 10), fill=INK, width=3)
        center_text(draw, (x, axis_y + 38), str(value), SMALL, MUTED)
    draw.text((1965, axis_y - 50), "Delta U (V)", font=LABEL, fill=INK)

    draw_interval(
        draw, 535, -source_limit, source_limit, axis_min, axis_max, x0, x1, GREEN,
        "Source model", "intersection of q and r limits: |Delta U| <= 10 V",
    )
    draw_interval(
        draw, 690, -aggregate_limit, aggregate_limit, axis_min, axis_max, x0, x1, ORANGE,
        "Naive aggregate", "summed rating: |Delta U| <= 200/11 = 18.18 V",
    )

    witness_x = interval_x(test_voltage, axis_min, axis_max, x0, x1)
    draw.line((witness_x, axis_y - 25, witness_x, 835), fill=RED, width=5)
    draw.ellipse((witness_x - 13, axis_y - 13, witness_x + 13, axis_y + 13), fill=RED)
    edge_label(draw, (witness_x, 410), "witness: 15 V", RED)

    cards = [
        (65, "q member", "150 A > 100 A", PALE_RED, RED, "violated"),
        (775, "r member", "15 A <= 100 A", PALE_GREEN, GREEN, "satisfied"),
        (1485, "summed check", "165 A <= 200 A", PALE_GREEN, GREEN, "passes"),
    ]
    for x, title, value, fill, color, verdict in cards:
        card(draw, (x, 870, x + 650, 1060), fill=fill, outline=WHITE)
        draw.text((x + 28, 892), title, font=LABEL, fill=INK)
        draw.text((x + 28, 940), value, font=PANEL, fill=color)
        badge(draw, (x + 500, 895), verdict, WHITE, color)
        if title == "summed check":
            draw.text((x + 28, 1000), "The wrong model accepts the point.", font=SMALL, fill=MUTED)
        elif title == "q member":
            draw.text((x + 28, 1000), "The source model rejects the point.", font=SMALL, fill=MUTED)

    OUTPUTS["feasible_sets"].parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUTS["feasible_sets"], optimize=True)


def write_manifest():
    manifest = {
        "schema_version": "1.0.0",
        "source_analysis": str(ANALYSIS.relative_to(ROOT)),
        "source_analysis_sha256": sha256(ANALYSIS),
        "generator": str(Path(__file__).resolve().relative_to(ROOT)),
        "figures": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": sha256(path),
            }
            for name, path in OUTPUTS.items()
        },
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w") as stream:
        json.dump(manifest, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main():
    analysis = load_analysis()
    render_cycle_basis(analysis)
    render_transformation_map(analysis)
    render_feasible_sets(analysis)
    write_manifest()
    for path in (*OUTPUTS.values(), MANIFEST):
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
