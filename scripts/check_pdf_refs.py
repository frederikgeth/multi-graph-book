#!/usr/bin/env python3
"""Check that @ref targets used by the curated PDF are in its page route."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAKE = ROOT / "docs/make.jl"
REF = re.compile(r"@ref\s+([A-Za-z][A-Za-z0-9_-]*)")
ANCHOR = re.compile(r"@id\s+([A-Za-z][A-Za-z0-9_-]*)")
PAGE = re.compile(r'=>\s*"([^"]+\.md)"')


def pdf_pages() -> list[Path]:
    source = MAKE.read_text()
    start = source.index("const PAGES_PDF = [")
    end = source.index("\n]\n\n# Build the PDF", start)
    return [ROOT / "docs/src" / path for path in PAGE.findall(source[start:end])]


def find_pdf_reference_errors() -> list[str]:
    pages = pdf_pages()
    anchors = {
        anchor
        for page in pages
        if page.is_file()
        for anchor in ANCHOR.findall(page.read_text())
    }
    errors: list[str] = []
    for page in pages:
        if not page.is_file():
            errors.append(f"PDF route names missing page {page.relative_to(ROOT)}")
            continue
        for target in REF.findall(page.read_text()):
            if target not in anchors:
                errors.append(
                    f"{page.relative_to(ROOT)} references @ref {target}, which is absent from the PDF route"
                )
    return errors


def main() -> int:
    errors = find_pdf_reference_errors()
    if errors:
        print("PDF reference audit failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"PDF reference audit: {len(pdf_pages())} pages and all @ref targets are reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
