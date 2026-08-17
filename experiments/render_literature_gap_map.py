"""Render the current literature-attention assessment as a compact gap map."""

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/src/assets"
TOPICS = [
    ("Switch topology processing", "High", 5),
    ("Linear terminal/Kron equivalents", "High", 5),
    ("Dynamic equivalents", "High", 5),
    ("Voltage/flow feeder reduction", "Moderate", 4),
    ("Radiality and phase preservation", "Emerging", 3),
    ("Thermal-limit preservation", "Specialized", 2),
    ("Typed equipment-class closure", "Low", 1),
    ("Explicit neutral/grounding", "Low", 1),
    ("Parallel decision preservation", "Low", 1),
    ("Provenance/reversible compilation", "Low", 1),
    ("Unified certified normalization", "Very low", 0),
]


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tx(x: int, y: int, value: str, cls: str = "body", anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


STYLE = """
<style>
text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:27px;font-weight:bold}
.sub{font-size:15px;fill:#5f6b76}.body{font-size:14px}.small{font-size:12px;fill:#5f6b76}
.bar{fill:#245b7a}.axis{stroke:#17212b;stroke-width:1}.guide{stroke:#aab7c2;stroke-width:1;stroke-dasharray:4 4}
</style>
"""


def main() -> None:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="720" viewBox="0 0 1500 720">',
        '<title>Literature attention and structured gaps</title>',
        "<desc>Horizontal bars show the book's provisional literature-attention assessment for eleven topics, from high attention to very low attention. Lower attention indicates a research gap relative to the book agenda, not absence of all literature.</desc>",
        '<rect width="100%" height="100%" fill="white"/>', STYLE,
        tx(35, 42, "Literature attention is uneven across the preservation agenda", "title"),
        tx(35, 70, "Provisional synthesis of the current evidence matrix and literature map; low attention is a gap signal, not a claim of no literature.", "sub"),
        tx(360, 112, "relative attention", "small", "middle"),
        '<path d="M360 125 L1190 125" class="axis"/>',
    ]
    for level, x in zip(("Very low", "Low", "Specialized", "Emerging", "Moderate", "High"), (360, 526, 692, 858, 1024, 1190)):
        lines += [f'<path d="M{x} 120 L{x} 650" class="guide"/>', tx(x, 112, level, "small", "middle")]
    y = 155
    for topic, label, score in TOPICS:
        width = score * 166
        lines += [tx(35, y + 16, topic, "body"), f'<rect x="360" y="{y}" width="{width}" height="24" rx="4" class="bar"/>', tx(1220, y + 17, label, "body")]
        y += 43
    lines += [
        tx(35, 670, "Interpretation", "body"),
        tx(145, 670, "Established reduction and topology procedures receive substantial attention; typed closure, provenance, grounding, and decision preservation remain underdeveloped.", "small"),
        '</svg>',
    ]
    svg = OUT / "literature-gap-map.svg"
    png = OUT / "literature-gap-map.png"
    svg.write_text("\n".join(lines) + "\n")
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise SystemExit("rsvg-convert is required to create PNG companions")
    subprocess.run([converter, "-o", str(png), str(svg)], check=True)
    print(f"wrote {svg}")
    print(f"wrote {png}")


if __name__ == "__main__":
    main()
