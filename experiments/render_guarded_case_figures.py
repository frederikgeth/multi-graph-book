#!/usr/bin/env python3
"""Render the evidence plates for the guarded-case section.

The plates are deliberately small, deterministic summaries of the checked JSON
artifacts.  They expose the claim, guards, residual, cross-check, and open item
without pretending that a figure is a substitute for the certificate.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/src/assets"


def esc(value: object) -> str:
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: float, y: float, value: object, cls: str = "body", anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


STYLE = """
<style>
text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:27px;font-weight:bold}.sub{font-size:15px;fill:#5f6b76}
.head{font-size:18px;font-weight:bold}.body{font-size:15px}.small{font-size:13px;fill:#46525d}.tiny{font-size:12px;fill:#46525d}
.panel{fill:#fbfcfd;stroke:#17212b;stroke-width:2}.good{fill:#e4f4e7;stroke:#477a55;stroke-width:2}.warn{fill:#fff3dc;stroke:#a36516;stroke-width:2}.bad{fill:#f4e5e5;stroke:#8a3232;stroke-width:2}.ink{stroke:#17212b;stroke-width:2}.ok{fill:#2f6b3b}.red{fill:#8a3232}.amber{fill:#a36516}
</style>
"""


def shell(title: str, subtitle: str, width: int = 1400, height: int = 820) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<title>{esc(title)}</title>', f'<desc>{esc(subtitle)}</desc>',
        '<rect width="100%" height="100%" fill="white"/>', STYLE,
        text(35, 40, title, "title"), text(35, 68, subtitle, "sub"),
    ]


def finish(lines: list[str]) -> str:
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def rect(x: float, y: float, w: float, h: float, cls: str = "panel", r: int = 10) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" class="{cls}"/>'


def line(x1: float, y1: float, x2: float, y2: float, cls: str = "ink", width: int = 2, dash: str = "") -> str:
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}" stroke-width="{width}"{extra}/>'


def wrap(value: object, n: int = 67) -> list[str]:
    words = str(value).split()
    rows: list[str] = []
    current = ""
    for word in words:
        if current and len(current) + len(word) + 1 > n:
            rows.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        rows.append(current)
    return rows


def field(lines: list[str], x: float, y: float, label: str, value: object, value_cls: str = "small") -> None:
    lines.append(text(x, y, label, "tiny"))
    rows = wrap(value)
    for i, row in enumerate(rows[:2]):
        lines.append(text(x, y + 19 + i * 16, row, value_cls))


def result_plate(title: str, subtitle: str, claim: str, classification: str, source_scope: str,
                guards: list[str], residual: str, crosscheck: str, open_item: str,
                status: str = "AUDITED SUMMARY") -> str:
    lines = shell(title, subtitle, 1400, 760)
    lines += [rect(40, 105, 1320, 100, "good"), text(70, 140, claim, "head"), text(70, 171, classification, "body"), text(1325, 142, status, "head", "end")]
    lines += [rect(40, 230, 640, 220, "panel"), rect(720, 230, 640, 220, "panel")]
    lines += [text(70, 268, "source scope", "head"), text(70, 299, wrap(source_scope, 64)[0], "small")]
    for i, row in enumerate(wrap(source_scope, 64)[1:3]):
        lines.append(text(70, 318 + i * 17, row, "small"))
    lines += [text(70, 374, "guards discharged", "head")]
    for i, guard in enumerate(guards[:3]):
        y = 405 + i * 18
        lines += [text(70, y, "✓", "ok"), text(92, y, guard, "small")]
    lines += [text(750, 268, "verification", "head"), text(750, 307, "residual", "tiny"), text(750, 329, residual, "body"), text(750, 374, "cross-check", "tiny")]
    for i, row in enumerate(wrap(crosscheck, 62)[:2]):
        lines.append(text(750, 396 + i * 18, row, "small"))
    lines += [rect(40, 485, 1320, 105, "warn"), text(70, 522, "OPEN ITEM", "head"), text(70, 555, wrap(open_item, 125)[0], "body")]
    if len(wrap(open_item, 125)) > 1:
        lines.append(text(70, 575, wrap(open_item, 125)[1], "small"))
    lines += [rect(40, 630, 1320, 55, "panel"), text(70, 664, "Generated from the checked artifact; read the chapter and certificate for the full contract.", "small")]
    return finish(lines)


def ladder() -> str:
    data = json.loads((ROOT / "experiments/generated/four-wire-impedance-model-ladder.json").read_text())
    path = data["transformation_path"]
    lines = shell("Every edge can be defensible while the path is not", "The composed ladder retains the weakest exactness label and the union of unresolved guards.", 1500, 920)
    x0, y0, w, h, gap = 55, 150, 188, 290, 18
    for i, edge in enumerate(path):
        x = x0 + i * (w + gap)
        cls = "good" if edge["exactness"] in ("guarded-exact", "exact-coordinate") else "warn"
        lines += [rect(x, y0, w, h, cls), text(x + w / 2, y0 + 32, edge["rule"], "head", "middle"), text(x + w / 2, y0 + 58, edge["exactness"], "tiny", "middle")]
        lines += [text(x + 15, y0 + 95, "source", "tiny")]
        for j, row in enumerate(wrap(edge["source"], 22)[:2]):
            lines.append(text(x + 15, y0 + 114 + j * 15, row, "tiny"))
        lines += [text(x + 15, y0 + 151, "target", "tiny")]
        for j, row in enumerate(wrap(edge["target"], 22)[:2]):
            lines.append(text(x + 15, y0 + 170 + j * 15, row, "tiny"))
        lines += [text(x + 15, y0 + 210, "✓ edge guards", "small")]
        for j, row in enumerate(wrap(edge["guards"][0], 22)[:2]):
            lines.append(text(x + 15, y0 + 231 + j * 14, row, "tiny"))
        lines += [text(x + 15, y0 + 270, "preserves:", "tiny")]
        for j, row in enumerate(wrap(edge["preserves"][0], 22)[:1]):
            lines.append(text(x + 15, y0 + 285 + j * 14, row, "tiny"))
        if i < len(path) - 1:
            lines.append(line(x + w, y0 + 145, x + w + gap - 4, y0 + 145, "ink", 3))
            lines.append(text(x + w + gap / 2 - 2, y0 + 132, "→", "head", "middle"))
    endx = x0 + (len(path) - 1) * (w + gap)
    lines += [rect(endx - 3, y0 + h + 35, w + 6, 95, "bad"), text(endx + w / 2, y0 + h + 68, "⚑ endpoint", "head", "middle"), text(endx + w / 2, y0 + h + 94, "positive-sequence decision", "small", "middle")]
    lines += [rect(55, 570, 1390, 180, "panel"), text(80, 608, "accumulated unresolved guards", "head")]
    unresolved = ["neutral limits recovered", "shunt/common-mode effects excluded or mapped", "sequence coupling negligible or excluded", "balanced boundary data and sequence-compatible decisions"]
    for i, value in enumerate(unresolved):
        x = 80 + (i % 2) * 680
        y = 650 + (i // 2) * 38
        lines += [text(x, y, "!", "red"), text(x + 20, y, value, "body")]
    lines += [text(60, 805, "Green ticks certify individual edges; they do not certify their composition for a richer decision query.", "small")]
    return finish(lines)


def carson() -> str:
    data = json.loads((ROOT / "experiments/generated/australian-carson-reproduction.json").read_text())
    probe = data["cases"]["overhead"]["reference_case"]["frequency_probe"]
    lines = shell("Carson reconciliation: two knobs explain the overhead mismatch", "The same lifted construction is probed at two frequencies and conductor orders; the source matrix is never used as model input.", 1500, 900)
    lines += [rect(45, 120, 410, 560, "panel"), rect(485, 120, 410, 560, "panel"), rect(925, 120, 510, 560, "good")]
    lines += [text(70, 160, "lifted construction", "head"), text(70, 192, "50 Hz · source order [1,2,3,4]", "body"), text(70, 250, "max error", "tiny"), text(70, 280, f"{probe[0]['source_order_max_series_error_ohm_per_km']:.3f} Ω/km", "head"), text(70, 345, "reference", "tiny"), text(70, 370, "Australian_overhead Z_abcn", "small"), text(70, 430, "input", "tiny"), text(70, 455, "Carson primitive from construction fields", "small")]
    lines += [text(510, 160, "probe", "head"), text(510, 192, "60 Hz · order [4,1,2,3]", "body"), text(510, 250, "max error", "tiny"), text(510, 280, f"{probe[1]['permuted_max_series_error_ohm_per_km']:.2e} Ω/km", "head"), text(510, 345, "knobs", "tiny"), text(510, 370, "frequency + conductor permutation", "small"), text(510, 430, "diagnosis", "tiny"), text(510, 455, "reference convention was undeclared", "small")]
    lines += [text(950, 160, "resolved comparison", "head"), text(950, 200, "R and X align after both knobs", "body"), text(950, 270, "50 Hz / order [4,1,2,3]", "tiny"), text(950, 293, f"{probe[0]['permuted_max_series_error_ohm_per_km']:.3f} Ω/km", "small"), text(950, 345, "60 Hz / order [4,1,2,3]", "tiny"), text(950, 370, f"{probe[1]['permuted_max_series_error_ohm_per_km']:.2e} Ω/km", "head"), text(950, 445, "cross-check", "tiny"), text(950, 470, "OpenDSSDirect circuit solve + independent", "small"), text(950, 490, "LinearAlgebra solve agree on voltage/loss rows", "small")]
    lines += [rect(45, 720, 1390, 105, "warn"), text(70, 758, "CREDIBILITY BOUNDARY", "head"), text(70, 789, "The overhead case is reconciled; the companion CS1035 case remains open because its raw construction mapping is unavailable.", "body")]
    return finish(lines)


def cs1035_gap() -> str:
    data = json.loads((ROOT / "experiments/generated/australian-carson-reproduction.json").read_text())
    probe = data["cases"]["underground"]["reference_case"]["frequency_probe"]
    lines = shell("CS1035: an explicit unresolved reproduction", "A failed probe is evidence too: changing frequency does not close the construction-to-matrix gap.", 1400, 720)
    lines += [rect(50, 130, 390, 390, "panel"), rect(505, 130, 390, 390, "warn"), rect(960, 130, 390, 390, "bad")]
    lines += [text(75, 170, "available", "head"), text(75, 210, "UGHV fixture fields", "body"), text(75, 250, "diameter, resistance, positions", "small"), text(75, 278, "50 Hz Carson primitive", "small"), text(75, 340, "independent reference", "tiny"), text(75, 365, "CS1035 Z_abcn matrix", "small")]
    lines += [text(530, 170, "frequency probe", "head"), text(530, 220, "50 Hz", "body"), text(530, 250, f"error {probe[0]['permuted_max_series_error_ohm_per_km']:.3f} Ω/km", "small"), text(530, 315, "60 Hz", "body"), text(530, 345, f"error {probe[1]['permuted_max_series_error_ohm_per_km']:.3f} Ω/km", "small"), text(530, 420, "frequency is not sufficient", "head")]
    lines += [text(985, 170, "missing", "head"), text(985, 220, "raw CS1035 construction mapping", "body"), text(985, 275, "conductor / screen geometry", "small"), text(985, 302, "earth-return convention", "small"), text(985, 329, "source frequency and ordering", "small"), text(985, 410, "OPEN DATA TASK", "head")]
    lines += [rect(50, 565, 1300, 75, "panel"), text(75, 610, "Do not relabel this as a successful reproduction: retain the matrix as an independent comparison and preserve the missing provenance in the evidence ledger.", "body")]
    return finish(lines)


def tap_decision() -> str:
    network = json.loads((ROOT / "experiments/generated/transformer-tap-ac-decision-certificate.json").read_text())
    local = json.loads((ROOT / "experiments/generated/transformer-tap-decision-certificate.json").read_text())
    ev = network["evidence"]
    local_tap = local["evidence"]["decision_witness"]["source_optimal_tap"]
    net_tap = ev["source_optimum"]["tap_value"]
    net_alpha = ev["source_optimum"]["objective_served_fraction"]
    frozen_gap = ev["frozen_start_objective_gap"]
    independent_gap = json.loads((ROOT / "experiments/generated/transformer-tap-ac-independent-certificate.json").read_text())["evidence"]["ipopt_comparison"]["maximum_absolute_served_fraction_difference"]
    lines = shell("The optimal tap belongs to the decision problem, not the transformer", "Same device and finite tap domain; different boundary/objective embeddings select different decisions.", 1500, 850)
    lines += [rect(45, 120, 420, 510, "panel"), rect(510, 120, 420, 510, "good"), rect(975, 120, 460, 510, "warn")]
    lines += [text(70, 160, "local fixed-boundary metric", "head"), text(70, 200, "tap domain {0.95, 1.00, 1.05}", "body"), text(70, 270, "selected tap", "tiny"), text(70, 305, f"{local_tap:.2f}", "head"), text(70, 370, "what is optimized", "tiny"), text(70, 398, "transformer-local leakage metric", "small"), text(70, 465, "boundary", "tiny"), text(70, 493, "prescribed voltage", "small")]
    lines += [text(535, 160, "network AC embedding", "head"), text(535, 200, "tap domain {0.95, 1.00, 1.05}", "body"), text(535, 270, "selected tap", "tiny"), text(535, 305, f"{net_tap:.2f}", "head"), text(535, 370, "served fraction", "tiny"), text(535, 398, f"{net_alpha:.7f}", "head"), text(535, 465, "what is optimized", "tiny"), text(535, 493, "network served load with AC limits", "small")]
    lines += [text(1000, 160, "same device ≠ same decision", "head"), text(1000, 210, "The network map is pointwise exact", "body"), text(1000, 250, "at all three taps; the embedding changes", "small"), text(1000, 270, "which objective and boundary are active.", "small"), text(1000, 350, "freeze at 1.00", "tiny"), text(1000, 382, f"served-fraction loss {frozen_gap:.7f}", "head"), text(1000, 435, "independent reproduction", "tiny"), text(1000, 462, f"max objective difference {independent_gap:.2e}", "small"), text(1000, 530, "lesson", "tiny"), text(1000, 557, "preserve the decision map, not", "small"), text(1000, 576, "just the device equation", "small")]
    lines += [rect(45, 685, 1390, 85, "panel"), text(70, 725, "The 1.05 and 0.95 choices are complementary witnesses, not contradictory recommendations.", "body"), text(70, 750, "A tap value has semantics only relative to the declared objective, boundary variables, constraints, and state domain.", "small")]
    return finish(lines)


def parallel_decision() -> str:
    data = json.loads((ROOT / "experiments/generated/pi-four-wire-parallel-ac-certificate.json").read_text())
    ev = data["evidence"]
    exact = ev["exact_pruned_solution"]["objective_served_fraction"]
    naive = ev["naive_aggregate_solution"]["objective_served_fraction"]
    gap = ev["naive_objective_gap"]
    cert_gap = ev["pruned_objective_gap"]
    independent = ev["independent_source_objective_gap"]
    lines = shell("Parallel-member limits: aggregation is not a decision certificate", "The same terminal relation can be aggregated, while member constraints require a recovered exact pruning map.", 1450, 820)
    lines += [rect(45, 125, 410, 470, "panel"), rect(505, 125, 410, 470, "bad"), rect(965, 125, 440, 470, "good")]
    lines += [text(70, 165, "source / exact pruning", "head"), text(70, 210, "member identities retained", "body"), text(70, 270, "served fraction", "tiny"), text(70, 305, f"{exact:.7f}", "head"), text(70, 370, "recovery relation", "tiny"), text(70, 400, "full Pi terminal-current map", "small"), text(70, 465, "independent gap", "tiny"), text(70, 493, f"{independent:.2e}", "small")]
    lines += [text(530, 165, "naive aggregate", "head"), text(530, 210, "one summed member limit", "body"), text(530, 270, "served fraction", "tiny"), text(530, 305, f"{naive:.7f}", "head"), text(530, 370, "outer-relaxation gap", "tiny"), text(530, 402, f"{gap:.7f}", "head"), text(530, 465, "forgotten", "tiny"), text(530, 493, "member-specific terminal constraints", "small")]
    lines += [text(990, 165, "certificate", "head"), text(990, 210, "TR-PAR-007", "body"), text(990, 270, "exact pruning residual", "tiny"), text(990, 302, f"{cert_gap:.2e}", "head"), text(990, 365, "guards", "tiny"), text(990, 394, "nonsingular maps; fixed state", "small"), text(990, 420, "and voltage domain; full recovery", "small"), text(990, 490, "lesson", "tiny"), text(990, 518, "aggregate admittance ≠ aggregate", "small"), text(990, 540, "ampacity unless the implication is proved", "small")]
    lines += [rect(45, 650, 1360, 80, "panel"), text(70, 690, "The exact target keeps one member's limits only because the certificate proves they imply the other member's limits under the declared map.", "body")]
    return finish(lines)


def bim_signature() -> str:
    lines = shell("Variable signatures determine which BIM/BFM questions are expressible", "A shared bus-pair variable and member-indexed variables describe different relaxation spaces.", 1400, 780)
    rows = [
        ("member current limit", "✗", "✓"),
        ("independent outage/state", "✗", "✓"),
        ("recovered branch current", "✗", "✓"),
        ("member measurement", "✗", "✓"),
        ("common voltage-drop consistency", "implicit", "explicit"),
    ]
    lines += [rect(55, 125, 1290, 520, "panel"), text(85, 170, "question", "head"), text(720, 170, "shared W_ij", "head", "middle"), text(1080, 170, "member-indexed W_lij / S_lij", "head", "middle")]
    for i, (question, left, right) in enumerate(rows):
        y = 220 + i * 78
        lines += [line(80, y - 25, 1310, y - 25, "ink", 1), text(85, y, question, "body"), text(720, y, left, "head", "middle"), text(1080, y, right, "head", "middle")]
    lines += [rect(85, 545, 1210, 62, "warn"), text(105, 582, "Missing relation: Z_l* S_lij = Z_k* S_kij. Aggregate balance can pass while no common voltage drop exists.", "body")]
    lines += [text(65, 705, "Notation capability plate, not a new numerical certificate: the chapter's equations define the scope boundary.", "small")]
    return finish(lines)


def main() -> None:
    outputs = {
        "guarded-result-plate.svg": result_plate(
            "A guarded result plate: Carson overhead case", "A compact, artifact-derived audit summary for a case chapter.",
            "AUSTRALIAN-CARSON-001", "source-backed reproduction · comparison diagnostic", "lifted overhead construction + independent Australian Z_abcn reference", ["construction fields are source-backed", "reference matrix is not used as model input", "60 Hz/order probe is labelled an inference"], "4.3×10⁻⁵ Ω/km", "OpenDSSDirect and independent LinearAlgebra solve agree on voltage/loss rows", "CS1035 raw construction mapping remains unavailable."),
        "four-wire-impedance-ladder.svg": ladder(),
        "australian-carson-reconciliation.svg": carson(),
        "australian-cs1035-gap.svg": cs1035_gap(),
        "transformer-tap-decision-plate.svg": tap_decision(),
        "parallel-member-decision-plate.svg": parallel_decision(),
        "bim-bfm-signature-capability.svg": bim_signature(),
    }
    for name, content in outputs.items():
        (OUT / name).write_text(content)
        print(f"wrote {OUT / name}")


if __name__ == "__main__":
    main()
