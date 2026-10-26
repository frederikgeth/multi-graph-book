#!/usr/bin/env python3
"""Validate the selective PDF route and its links into the full HTML library."""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAKE = ROOT / "docs/make.jl"
REF = re.compile(r"@ref\s+([A-Za-z][A-Za-z0-9_-]*)")
ANCHOR = re.compile(r"@id\s+([A-Za-z][A-Za-z0-9_-]*)")
PAGE = re.compile(r'=>\s*"([^"]+\.md)"')

# Public section ids moved out of the selective PDF in review repair R3.
# Keep canonical reference destinations and old browser-fragment entry points.
AUDIT_REFERENCE = "reference/numerical-audit-reference.md"
AUDIT_LEGACY = "foundations/numerical-consequences.md"
AUDIT_ANCHORS = (
    "generator-voltage-audit", "fixed-transformer-audit", "winding-list-audit",
    "multiphase-winding-audit", "delta-winding-audit", "winding-rating-metadata",
    "phase-neutral-voltage-audit", "neutral-earth-voltage-audit", "phase-phase-voltage-audit",
    "bus-angle-voltage-audit", "sequence-voltage-audit", "branch-angle-voltage-audit",
    "generator-cost-scope-audit", "delta-generator-injection-audit", "source-price-reference-audit",
    "source-pq-limit-audit", "ibr-injection-audit", "ibr-price-scope-audit",
)


def route(kind):
    source = MAKE.read_text()
    start = source.index(f"const PAGES_{kind} = [")
    end = source.index("\n]\n", start)
    return [ROOT / "docs/src" / path for path in PAGE.findall(source[start:end])]


def pdf_pages():
    return route("PDF")


def find_pdf_reference_errors():
    pages, html = pdf_pages(), route("HTML")
    errors = []
    if len(pages) != len(set(pages)):
        errors.append("duplicate PDF page")
    if len(html) != len(set(html)):
        errors.append("duplicate HTML page")
    if not set(pages) < set(html):
        errors.append("PDF must be a strict subset of the complete HTML route")
    omitted_from_html = set((ROOT / "docs/src").rglob("*.md")) - set(html)
    for page in sorted(omitted_from_html):
        errors.append(f"canonical page lost from HTML route: {page.relative_to(ROOT)}")
    anchors = {anchor: page for page in html if page.is_file() for anchor in ANCHOR.findall(page.read_text())}
    audit_reference = ROOT / "docs/src" / AUDIT_REFERENCE
    legacy_text = (ROOT / "docs/src" / AUDIT_LEGACY).read_text()
    if audit_reference in pages:
        errors.append("exhaustive audit reference must remain in HTML, outside the core PDF")
    for anchor in AUDIT_ANCHORS:
        if anchors.get(anchor) != audit_reference:
            errors.append(f"audit section lost its canonical reference destination: {anchor}")
        marker = f'<a id="{anchor}" data-reference-page="{AUDIT_REFERENCE}"></a>'
        if marker not in legacy_text or f"@ref {anchor})" not in legacy_text:
            errors.append(f"audit section lost its legacy fragment/continuation link: {anchor}")
    source = MAKE.read_text()
    if "PDF_REFERENCE_FALLBACK" not in source or "link::Documenter.PageLink" not in source:
        errors.append("PDF-to-HTML reference rendering is missing")
    if 'const REFERENCE_BASE_URL = "https://frederikgeth.github.io/multi-graph-book/dev/"' not in source:
        errors.append("PDF reference library base URL is missing or changed")
    for page in pages:
        if not page.is_file():
            errors.append(f"PDF route names missing page {page.relative_to(ROOT)}")
            continue
        path = page.relative_to(ROOT / "docs/src").as_posix()
        if path.startswith("literature/") or path in {
            "reference/knowledge-base-index.md", "reference/chapter-status.md",
            "reference/vocabulary-indexes.md", "reference/federated-knowledge-trace.md",
            "start/chatgpt-access.md", "start/claude-access.md",
        }:
            errors.append(f"reference-only content in core PDF: {path}")
        for target in REF.findall(page.read_text()):
            if target not in anchors:
                errors.append(f"{page.relative_to(ROOT)} references unknown @ref {target}")
    if pages[:2] != [ROOT / "docs/src/start/preface.md", ROOT / "docs/src/start/first-failure-parallel-branches.md"]:
        errors.append("the opening lesson must immediately follow the author preface")
    return errors


def main():
    errors = find_pdf_reference_errors()
    if errors:
        print("PDF reference audit failed:\n" + "\n".join(f"- {error}" for error in errors))
        return 1
    print(f"PDF reference audit: {len(pdf_pages())} selected pages; all targets resolve within the PDF or full HTML library")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
