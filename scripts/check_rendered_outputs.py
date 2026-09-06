#!/usr/bin/env python3
"""Smoke-test the rendered HTML/PDF products and their deliberate TOC policy.

This is intentionally a structural check, not a visual or mathematical review.
It catches stale/empty builds, missing HTML metadata, PDF compilation remnants,
and accidental changes to the compact reading-route TOC.
"""

from __future__ import annotations

import html
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_ROOT = ROOT / "docs/build"
PDF = ROOT / "docs/latex_build/GraphModelsForPowerSystems.pdf"
PDF_LOG = ROOT / "docs/latex_build/Power-SystemModellingforComputation.log"

EXPECTED_HTML = [
    "index.html",
    "cases/building-and-changing-models.html",
    "start/one-network-many-graphs.html",
    "foundations/formal-representation-frameworks.html",
    "cases/four-wire-parallel-ac-decision.html",
    "literature/review-protocol-and-evidence-status.html",
    "literature/search-runs/2026-08-14-seed-batch.html",
    "reference/knowledge-base-index.html",
]

TOC_PAGES = [
    "The parallel-member lesson",
    "Building and changing a model you can check",
    "Computational case guide",
    "Study workbook",
]


def command_text(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def fail(message: str) -> None:
    raise SystemExit(f"rendered-output check failed: {message}")


def resolve_html(relative: str) -> Path:
    """Resolve an expected page under either Documenter URL convention.

    `prettyurls` defaults to on in CI and off for local builds
    (docs/make.jl mirrors that via `ENV["CI"]`), so `page.html` becomes
    `page/index.html` in CI while local builds keep the flat filename.
    """
    literal = HTML_ROOT / relative
    if literal.is_file():
        return literal
    return HTML_ROOT / relative[: -len(".html")] / "index.html"


if not HTML_ROOT.is_dir():
    fail(f"HTML build directory is missing: {HTML_ROOT}")
if not PDF.is_file() or PDF.stat().st_size < 100_000:
    fail("PDF is missing or implausibly small")

for relative in EXPECTED_HTML:
    path = resolve_html(relative)
    if not path.is_file() or path.stat().st_size < 500:
        fail(f"expected HTML page is missing or empty: {relative}")

html_files = list(HTML_ROOT.rglob("*.html"))
if len(html_files) < 60:
    fail(f"HTML build contains only {len(html_files)} pages")

image_count = 0
for path in html_files:
    source = path.read_text(errors="replace")
    if not re.search(r"<title>\s*[^<]+\s*</title>", source, re.I):
        fail(f"HTML page has no nonempty title: {path.relative_to(HTML_ROOT)}")
    for tag in re.findall(r"<img\b[^>]*>", source, re.I):
        image_count += 1
        match = re.search(r"\balt\s*=\s*([\"'])(.*?)\1", tag, re.I | re.S)
        if match is None or not html.unescape(match.group(2)).strip():
            fail(f"HTML image has no nonempty alt text: {path.relative_to(HTML_ROOT)}")
    for href in re.findall(r"\bhref\s*=\s*([\"'])(.*?)\1", source, re.I | re.S):
        if not html.unescape(href[1]).strip():
            fail(f"HTML page contains an empty href: {path.relative_to(HTML_ROOT)}")

if shutil.which("pdfinfo") is None or shutil.which("pdftotext") is None:
    fail("pdfinfo and pdftotext are required for the rendered-output check")
info = command_text("pdfinfo", str(PDF))
page_match = re.search(r"^Pages:\s*(\d+)", info, re.M)
if page_match is None or int(page_match.group(1)) < 20:
    fail("PDF page count is missing or unexpectedly small")

with tempfile.TemporaryDirectory(prefix="multi-graph-book-pdf-") as temporary:
    body_text = command_text("pdftotext", "-layout", str(PDF), "-")
    # Contents end before the first main-text chapter. Restrict assertions to
    # those pages so a body heading cannot masquerade as a contents entry.
    pages = body_text.split("\f")
    contents_start = next((i for i, page in enumerate(pages) if re.search(r"^Contents\s*$", page, re.M)), None)
    main_start = next((i for i, page in enumerate(pages) if re.search(r"^Chapter 1\s*$", page, re.M)), None)
    if contents_start is None or main_start is None or main_start <= contents_start:
        fail("could not identify the contents and first chapter")
    toc_text = "\n".join(pages[contents_start:main_start])
    if main_start - contents_start > 3:
        fail("reading-route contents exceed three pages")
    for heading in TOC_PAGES:
        if heading not in toc_text:
            fail(f"selected teaching page is absent from the TOC: {heading}")
    for heading in ("Predict before calculating", "Repair the aggregate", "Run the calculation"):
        if heading in toc_text or heading not in body_text:
            fail(f"internal heading must appear in the text, outside the compact TOC: {heading}")
    for heading in ("From equipment to equations", "Conductors, connections, and ground", "Graphs for different computations", "Transformations and recovery", "Constraints and decisions", "Evidence for a computation", "An end-to-end modelling study", "References"):
        if heading not in toc_text:
            fail(f"expected core part is absent from the PDF TOC: {heading}")
    for heading in ("Page status: generated search-run record.", "Page status: generated reference navigation and evidence-gap summary.", "Page status: generated knowledge-base"):
        if heading in body_text:
            fail(f"reference-library content unexpectedly included in core PDF: {heading}")
    for heading in ("Change one assumption", "Check your reasoning", "Why I wrote this book"):
        if heading not in body_text:
            fail(f"new teaching content is missing from the PDF: {heading}")

    if shutil.which("pdftoppm") is not None:
        output = Path(temporary) / "page"
        subprocess.run(
            ["pdftoppm", "-f", "1", "-l", "1", "-png", "-singlefile", str(PDF), str(output)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        rendered = output.with_suffix(".png")
        if not rendered.is_file() or rendered.stat().st_size < 10_000:
            fail("cover-page raster smoke test produced no usable image")

if PDF_LOG.is_file():
    log = PDF_LOG.read_text(errors="replace")
    for marker in ("Emergency stop", "Runaway argument", "Undefined control sequence"):
        if marker in log:
            fail(f"PDF compiler log contains {marker!r}")

print(
    f"rendered outputs: {len(html_files)} HTML pages, {image_count} image tags, "
    f"{page_match.group(1)} PDF pages; selective TOC and raster smoke tests pass"
)
