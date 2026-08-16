#!/usr/bin/env python3
"""Lint the maintained Markdown math for a few high-cost notation slips."""

from __future__ import annotations

import re
import sys
from pathlib import Path


INLINE = re.compile(r"``([^`\n]*)``")
BARE_ELL = re.compile(r"(?<!\\)\bell\b")
BARE_PI = re.compile(r"(?<!\\)\bPi\b")
# A bold command must be followed by an argument.  This deliberately checks
# only unmistakable omissions, leaving TeX package-specific syntax alone.
ORPHAN_BOLD = re.compile(r"\\mathbf\s*(?:$|[,.;:)\]])")
DOUBLE_BACKSLASH = re.compile(r"\\\\")


def find_math_hygiene_findings(root: Path) -> list[str]:
    findings: list[str] = []
    for document in sorted((root / "docs/src").rglob("*.md")):
        in_fence = False
        inline_open = False
        inline_buffer: list[str] = []
        inline_start = 0
        for line_number, line in enumerate(document.read_text().splitlines(), 1):
            stripped = line.lstrip()
            if in_fence:
                if stripped.startswith("```"):
                    in_fence = False
                else:
                    _check_segment(findings, document, line_number, line, check_double=False)
                continue
            if stripped.startswith("```math"):
                in_fence = True
                continue
            if stripped.startswith("```"):
                continue
            remainder = line
            while True:
                marker = remainder.find("``")
                if not inline_open:
                    if marker < 0:
                        break
                    inline_open = True
                    inline_start = line_number
                    inline_buffer = []
                    remainder = remainder[marker + 2 :]
                else:
                    if marker < 0:
                        inline_buffer.append(remainder)
                        break
                    inline_buffer.append(remainder[:marker])
                    _check_segment(findings, document, inline_start, "\n".join(inline_buffer), check_double=True)
                    inline_open = False
                    inline_buffer = []
                    remainder = remainder[marker + 2 :]
        if inline_open:
            findings.append(f"{document.relative_to(root)}:{inline_start}: unbalanced inline math delimiters")
    return findings


def _check_segment(findings: list[str], document: Path, line_number: int, segment: str, *, check_double: bool) -> None:
    location = f"{document.relative_to(document.parents[1])}:{line_number}"
    if BARE_ELL.search(segment):
        findings.append(f"{location}: use \\ell rather than bare ell in math")
    if BARE_PI.search(segment):
        findings.append(f"{location}: use \\Pi rather than bare Pi in math")
    if ORPHAN_BOLD.search(segment):
        findings.append(f"{location}: \\mathbf has no visible argument")
    if check_double and DOUBLE_BACKSLASH.search(segment):
        findings.append(f"{location}: doubled backslash in inline/display math; use a single TeX command escape")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    findings = find_math_hygiene_findings(root)
    if findings:
        print("math hygiene failed:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1
    print("math hygiene: no bare ell/Pi, orphan \\mathbf commands, or unbalanced inline delimiters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
