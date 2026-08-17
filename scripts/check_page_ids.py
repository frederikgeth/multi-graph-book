#!/usr/bin/env python3
"""Require stable @id anchors on every HTML-routed page."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAKE = ROOT / "docs/make.jl"
PAGE = re.compile(r'=>\s*"([^"]+\.md)"')
TITLE = re.compile(r"^#\s+(?:\[[^]]+\]\(@id\s+([A-Za-z][A-Za-z0-9_-]*)\)|.+)$", re.MULTILINE)


def html_pages() -> list[Path]:
    source = MAKE.read_text()
    start = source.index("const PAGES_HTML = [")
    end = source.index("\n]\n\nconst PAGES_PDF", start)
    return [ROOT / "docs/src" / path for path in PAGE.findall(source[start:end])]


def main() -> int:
    errors: list[str] = []
    pages = html_pages()
    anchors: dict[str, str] = {}
    for page in pages:
        if not page.is_file():
            errors.append(f"HTML route names missing page {page.relative_to(ROOT)}")
            continue
        match = TITLE.search(page.read_text())
        if match is None or match.group(1) is None:
            errors.append(f"{page.relative_to(ROOT)} has no stable H1 @id anchor")
            continue
        anchor = match.group(1)
        if anchor in anchors:
            errors.append(f"duplicate page @id {anchor}: {anchors[anchor]} and {page.relative_to(ROOT)}")
        anchors[anchor] = page.relative_to(ROOT).as_posix()
    if errors:
        print("HTML page-anchor audit failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"page anchors: {len(pages)} HTML-routed pages have unique stable H1 @id anchors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
