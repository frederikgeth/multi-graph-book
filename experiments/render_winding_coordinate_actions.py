"""Render the row-versus-column winding-coordinate action figure."""

from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/src/assets"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tx(x: int, y: int, value: str, cls: str = "body", anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


STYLE = """
<style>
text{font-family:Arial,sans-serif;fill:#17212b}.title{font-size:27px;font-weight:bold}
.sub{font-size:15px;fill:#5f6b76}.head{font-size:18px;font-weight:bold}.body{font-size:14px}
.small{font-size:12px;fill:#5f6b76}.panel{fill:#f8fbfd;stroke:#245b7a;stroke-width:2}
.matrix{fill:#e5f1e7;stroke:#477a55;stroke-width:2}.vector{fill:#f8e1c4;stroke:#8a4f13;stroke-width:2}
.arrow{stroke:#245b7a;stroke-width:3;fill:none;marker-end:url(#arrow)}
</style>
"""


def main() -> None:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="720" viewBox="0 0 1500 720">',
        '<title>Winding coordinate actions: terminal columns versus coil rows</title>',
        '<desc>Two panels show the same connection-incidence matrix under distinct permutation actions. Terminal-coordinate permutations act on columns by right multiplication with the transpose, while coil-row permutations act on rows by left multiplication.</desc>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#245b7a"/></marker></defs>',
        '<rect width="100%" height="100%" fill="white"/>', STYLE,
        tx(35, 42, "One incidence matrix, two typed permutation actions", "title"),
        tx(35, 70, "The index set being permuted determines the side on which the action appears.", "sub"),
        '<rect x="45" y="110" width="680" height="500" rx="16" class="panel"/>',
        tx(385, 150, "Terminal-coordinate permutation (columns)", "head", "middle"),
        tx(385, 180, "Û = P U   ⇒   Â = A Pᵀ", "body", "middle"),
        '<rect x="110" y="250" width="150" height="150" class="matrix"/>',
        tx(185, 290, "A", "head", "middle"), tx(185, 325, "coil rows", "small", "middle"), tx(185, 350, "terminal columns", "small", "middle"),
        '<path d="M270 325 L410 325" class="arrow"/>',
        '<rect x="420" y="250" width="150" height="150" class="matrix"/>',
        tx(495, 290, "A Pᵀ", "head", "middle"), tx(495, 325, "same coil rows", "small", "middle"), tx(495, 350, "reordered columns", "small", "middle"),
        tx(385, 455, "Voltage coordinates move; coil labels and coil limits stay fixed.", "body", "middle"),
        tx(385, 485, "Dual terminal currents transform as Î = P I.", "small", "middle"),
        '<rect x="775" y="110" width="680" height="500" rx="16" class="panel"/>',
        tx(1115, 150, "Coil-row permutation (rows)", "head", "middle"),
        tx(1115, 180, "Ṽ = Q V   ⇒   Ã = Q A", "body", "middle"),
        '<rect x="840" y="250" width="150" height="150" class="matrix"/>',
        tx(915, 290, "A", "head", "middle"), tx(915, 325, "source coil rows", "small", "middle"), tx(915, 350, "terminal columns", "small", "middle"),
        '<path d="M1000 325 L1140 325" class="arrow"/>',
        '<rect x="1150" y="250" width="150" height="150" class="matrix"/>',
        tx(1225, 290, "Q A", "head", "middle"), tx(1225, 325, "common coil rows", "small", "middle"), tx(1225, 350, "same terminal columns", "small", "middle"),
        tx(1115, 455, "Coil coordinates move; terminal labels stay fixed.", "body", "middle"),
        tx(1115, 485, "Coil-current limits transform with Q (or Qᵀ in recovery).", "small", "middle"),
        '<rect x="105" y="545" width="1290" height="40" rx="10" class="vector"/>',
        tx(750, 571, "Do not reuse P_xk for both actions: P_xk is terminal-column order; Q_xk is coil-row order.", "body", "middle"),
        '</svg>',
    ]
    svg = OUT / "winding-coordinate-actions.svg"
    png = OUT / "winding-coordinate-actions.png"
    svg.write_text("\n".join(lines) + "\n")
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise SystemExit("rsvg-convert is required to create PNG companions")
    subprocess.run([converter, "-o", str(png), str(svg)], check=True)
    print(f"wrote {svg}")
    print(f"wrote {png}")


if __name__ == "__main__":
    main()
