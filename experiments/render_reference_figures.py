#!/usr/bin/env python3
"""Generate navigational figures for the reference section from the claims ledger."""

from __future__ import annotations

import tomllib
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/src/assets"
REFERENCE = ROOT / "docs/src/reference/evidence-map.md"


def esc(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x: float, y: float, value: object, cls: str = "body", anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


def rect(x: float, y: float, w: float, h: float, cls: str = "panel", r: int = 10) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" class="{cls}"/>'


STYLE = """
<style>
text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:28px;font-weight:bold}.sub{font-size:15px;fill:#5f6b76}
.head{font-size:18px;font-weight:bold}.body{font-size:15px}.small{font-size:13px;fill:#46525d}.tiny{font-size:12px;fill:#46525d}
.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.card{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}.good{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.empty{fill:#ffffff;stroke:#9aa5ad;stroke-width:2;stroke-dasharray:5 4}.ink{stroke:#17212b;stroke-width:2}.arrow{stroke:#245b7a;stroke-width:3;marker-end:url(#arrow)}
</style>
"""


def shell(title: str, subtitle: str, width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<title>{esc(title)}</title>', f'<desc>{esc(subtitle)}</desc>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#245b7a"/></marker></defs>',
        '<rect width="100%" height="100%" fill="white"/>', STYLE,
        t(35, 40, title, "title"), t(35, 68, subtitle, "sub"),
    ]


def finish(lines: list[str]) -> str:
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def anatomy() -> str:
    lines = shell("How to decode a power-network symbol", "The index grammar separates element identity, oriented attachment, relation role, and coordinate slots.", 1400, 760)
    lines += [rect(45, 115, 1310, 250, "good")]
    # Draw the slots separately rather than relying on a font's Unicode
    # superscript/subscript coverage; the printed symbol remains readable in
    # the PDF and in monochrome raster fallbacks.
    lines += [t(680, 200, "Y", "title", "middle"), t(715, 178, "sh", "head", "middle"), t(705, 218, "l", "head", "middle"), t(738, 218, "ij", "head", "middle"), t(700, 250, "element · role · orientation", "body", "middle")]
    callouts = [(90, 160, "Y", "constitutive quantity / operator"), (380, 145, "sh", "relation role: shunt, series, reference, coil, leak"), (930, 145, "ℓ", "element identity; intrinsic under reversal"), (930, 285, "ij", "oriented attachment; endpoint-specific data")]
    for x, y, slot, meaning in callouts:
        lines += [rect(x, y, 285, 70, "panel"), t(x + 18, y + 29, slot, "head"), t(x + 18, y + 52, meaning, "small")]
    lines += [t(245, 402, "The same grammar scales to symbols that are not yet in a table.", "body", "middle")]
    lines += [rect(45, 445, 625, 220, "panel"), rect(710, 445, 645, 220, "panel"), t(70, 485, "coordinate slots", "head"), t(735, 485, "orientation rule", "head")]
    for i, (slot, meaning) in enumerate([("p,q", "phase / conductor coordinates"), ("k", "winding or port label"), ("d", "decision or scenario index")]):
        y = 525 + i * 40
        lines += [t(75, y, slot, "body"), t(165, y, meaning, "small")]
    lines += [t(735, 525, "Z_l = Z_l^T is element-intrinsic", "body"), t(735, 565, "Y_lij may be end-specific", "body"), t(735, 605, "I_lij and S_lij use the oriented triple", "small")]
    lines += [t(55, 710, "The symbols are compact, but their ownership is not implicit: every index belongs to a declared set.", "small")]
    return finish(lines)


def distinction_map() -> str:
    lines = shell("Terminology is a distinction map, not only a glossary", "The diagnostic question on each edge tells the reader which apparently similar terms can be substituted—and which cannot.", 1450, 900)
    clusters = [
        (55, 130, "bus", ["busbar section", "connectivity node", "topological node", "nodal variable group", "reporting bus"], "which layer and state?"),
        (500, 130, "transformation", ["projection", "compilation", "normalization", "behavioural reduction"], "does it solve equations or add objects?"),
        (945, 130, "exactness", ["exact", "inner", "outer", "scenario-approximate"], "which containment is claimed?"),
        (275, 500, "state", ["connected", "energized", "adjacent", "coupled"], "which state and matrix?"),
        (810, 500, "flow", ["commodity flow", "series current", "terminal current", "terminal power"], "what is conserved?"),
    ]
    for x, y, title, terms, question in clusters:
        h = 260 if len(terms) > 4 else 220
        lines += [rect(x, y, 385, h, "panel"), t(x + 20, y + 38, title, "head")]
        for i, term in enumerate(terms):
            yy = y + 75 + i * 27
            lines += [t(x + 28, yy, "•", "body"), t(x + 48, yy, term, "body")]
        lines += [rect(x + 18, y + h - 55, 349, 35, "card"), t(x + 192, y + h - 32, question, "small", "middle")]
    lines += [t(725, 450, "diagnostic questions", "head", "middle"), t(725, 475, "are the edges of the map", "small", "middle")]
    return finish(lines)


def facets(claim: dict) -> set[str]:
    chapter, cid = claim["chapter"], claim["claim_id"]
    out: set[str] = set()
    if chapter.startswith("docs/src/foundations/") or cid.startswith(("ARCH-", "THESIS-")): out.add("representation")
    if "cycles" in chapter or "five-bus" in chapter or cid.startswith(("GRAPH-", "TR-PAR-")): out.add("graph/topology")
    if chapter.startswith("docs/src/transformations/") or cid.startswith("TR-"): out.add("transformations")
    if chapter.startswith("docs/src/cases/") or "decision" in chapter or cid.startswith(("TR-PAR-", "TR-XFMR-")): out.add("decision cases")
    if any(token in chapter for token in ("earth-ground", "rating", "orientation", "translation", "cycles")): out.add("physical modelling")
    if cid.startswith(("NUMERICAL-", "FIXTURE-")) or "executable" in chapter: out.add("numerical evidence")
    if cid.startswith("LIT-") or chapter.startswith("docs/src/literature/"): out.add("study/literature")
    if cid.startswith(("FIXTURE-", "DATA-", "ARCH-")) or "executable" in chapter or "crosswalk" in chapter: out.add("software/data")
    return out or {"general"}


def evidence_map(claims: list[dict]) -> str:
    columns = ["self-checked", "independently-implemented", "externally-reviewed"]
    rows = ["structure", "terminal_behavior", "phase_neutral", "limits", "decision", "state", "measurement", "provenance", "numerical_structure"]
    counts = {(row, col): 0 for row in rows for col in columns}
    for claim in claims:
        for row in claim.get("preservation_dimensions", []):
            for col in columns:
                if claim["verification"] == col: counts[(row, col)] += 1
    lines = shell("Evidence map: preservation coverage is visible only when the holes remain", "Counts are derived from explicit preservation dimensions in the claims ledger; an empty cell means no claim is coded there.", 1400, 800)
    x0, y0, cw, ch = 430, 145, 270, 42
    for j, col in enumerate(columns):
        lines += [t(x0 + j * cw + cw / 2, y0 - 20, col, "small", "middle")]
    for i, row in enumerate(rows):
        y = y0 + i * ch
        lines.append(t(x0 - 20, y + 31, row, "small", "end"))
        for j, col in enumerate(columns):
            value = counts[(row, col)]
            cls = "good" if value else "empty"
            lines += [rect(x0 + j * cw, y, cw - 12, ch - 8, cls), t(x0 + j * cw + (cw - 12) / 2, y + 30, value, "head" if value else "small", "middle")]
    lines += [rect(70, 180, 175, 310, "card"), t(157, 220, "read the map", "head", "middle"), t(90, 265, "filled cell", "body"), t(90, 290, "coded coverage", "small"), t(90, 350, "empty cell", "body"), t(90, 375, "research gap or", "small"), t(90, 395, "uncoded scope", "small")]
    lines += [rect(70, 570, 1220, 80, "panel"), t(95, 607, "External review remains empty across every dimension; dimensions describe the book's claim scope, not literature completeness.", "body"), t(95, 632, "The map is a gap analysis, not a claim that an empty cell proves the literature is empty.", "small")]
    lines += [t(75, 720, f"Generated from claims/claims.toml · {len(claims)} claims · preservation dimensions are controlled metadata.", "small")]
    return finish(lines)


def verification_summary(claims: list[dict]) -> str:
    states = ["self-checked", "independently-implemented", "externally-reviewed"]
    types = ["empirical", "theorem", "definition", "proposal", "practice"]
    counts = Counter((claim["claim_type"], claim["verification"]) for claim in claims)
    totals = Counter(claim["verification"] for claim in claims)
    lines = shell("Verification state at a glance", "The ledger currently distinguishes self-checks and independent implementations; no claim is externally reviewed.", 1400, 690)
    lines += [rect(55, 105, 1290, 90, "good"), t(80, 140, f"{len(claims)} claims", "head"), t(80, 171, " · ".join(f"{totals[s]} {s}" for s in states), "body")]
    x0, y0, cw, ch = 360, 250, 300, 58
    for j, state in enumerate(states): lines.append(t(x0 + j * cw + (cw - 15) / 2, y0 - 25, state, "small", "middle"))
    for i, typ in enumerate(types):
        y = y0 + i * ch
        lines.append(t(x0 - 25, y + 35, typ, "body", "end"))
        for j, state in enumerate(states):
            value = counts[(typ, state)]
            cls = "good" if value else "empty"
            lines += [rect(x0 + j * cw, y, cw - 15, ch - 10, cls), t(x0 + j * cw + (cw - 15) / 2, y + 34, value, "head" if value else "small", "middle")]
    lines += [rect(70, 250, 190, 280, "panel"), t(165, 290, "interpretation", "head", "middle"), t(90, 335, "self-checked", "body"), t(90, 360, "repo tests / derivations", "small"), t(90, 405, "independent", "body"), t(90, 430, "separate implementation", "small"), t(90, 475, "external", "body"), t(90, 500, "peer review", "small")]
    lines += [t(75, 620, "The summary is generated, so a future independently reviewed claim will change the figure rather than the prose promise.", "small")]
    return finish(lines)


def verification_sentence(claims: list[dict]) -> str:
    totals = Counter(claim["verification"] for claim in claims)
    return (
        "The largest named gaps in this snapshot are measurement (no coded claims at any "
        "verification state), state and numerical-structure claims without independent "
        "implementations, and external review (zero claims across all nine preservation "
        "dimensions). These are gaps in the current evidence record, not evidence that the "
        "corresponding literature or engineering practice is empty. The verification summary "
        f"reports {totals['self-checked']} self-checked, "
        f"{totals['independently-implemented']} independently implemented, and "
        f"{totals['externally-reviewed']} externally reviewed claims out of {len(claims)}; "
        "self-checking and independent implementation are useful but are not external peer review."
    )


def main() -> None:
    claims = tomllib.loads((ROOT / "claims/claims.toml").read_text()).get("claim", [])
    outputs = {
        "reference-symbol-anatomy.svg": anatomy(),
        "reference-distinction-map.svg": distinction_map(),
        "reference-evidence-map.svg": evidence_map(claims),
        "reference-verification-summary.svg": verification_summary(claims),
    }
    for name, content in outputs.items():
        (OUT / name).write_text(content)
        print(f"wrote {OUT / name}")
    REFERENCE.write_text(
        """# [Evidence map and verification summary](@id reference-evidence-map)

**Page status:** generated reference navigation and evidence-gap summary.

This page is generated from `claims/claims.toml`. It is a retrieval aid and gap analysis, not a replacement for the claims ledger or the evidence matrix. Empty cells are intentionally visible.

![Symbol anatomy for the book's index grammar.](../assets/reference-symbol-anatomy.png)

![Terminology distinction map.](../assets/reference-distinction-map.png)

![Evidence coverage by preservation dimension and verification state.](../assets/reference-evidence-map.png)

![Verification state by claim type.](../assets/reference-verification-summary.png)

<!-- generated-evidence-summary:start -->
"""
        + verification_sentence(claims)
        + "\n<!-- generated-evidence-summary:end -->\n"
    )
    print(f"wrote {REFERENCE}")


if __name__ == "__main__":
    main()
