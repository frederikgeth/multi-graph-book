#!/usr/bin/env python3
"""Validate the lightweight development research and decision log."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "docs/src/literature/development-decision-log.md"

ENTRY = re.compile(r"^## (DLOG-[0-9]{4}) — (.+)$", re.MULTILINE)
METADATA = re.compile(r"^- \*\*(Date|Status|Scope):\*\*\s+(.+)$", re.MULTILINE)
REQUIRED_SECTIONS = (
    "Question",
    "Options considered",
    "Decision",
    "Reason",
    "Evidence",
    "Known downside",
    "Conditions for revisiting",
)
ALLOWED_STATUSES = {"accepted", "rejected", "superseded"}


def entry_blocks(source: str) -> list[tuple[str, str, str]]:
    matches = list(ENTRY.finditer(source))
    return [
        (
            match.group(1),
            match.group(2).strip(),
            source[match.end() : matches[index + 1].start() if index + 1 < len(matches) else len(source)],
        )
        for index, match in enumerate(matches)
    ]


def section_body(block: str, section: str) -> str | None:
    pattern = re.compile(
        rf"^### {re.escape(section)}\s*$\n(?P<body>.*?)(?=^### |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(block)
    return match.group("body").strip() if match else None


def main() -> int:
    errors: list[str] = []
    if not LOG.is_file():
        print(f"development log check failed:\n- missing {LOG.relative_to(ROOT)}")
        return 1

    source = LOG.read_text()
    blocks = entry_blocks(source)
    if not blocks:
        errors.append("no DLOG entries found")

    ids = [entry_id for entry_id, _, _ in blocks]
    if len(ids) != len(set(ids)):
        errors.append("DLOG entry IDs must be unique")
    if ids != sorted(ids):
        errors.append("DLOG entries must be ordered by ID")

    for entry_id, title, block in blocks:
        if not title:
            errors.append(f"{entry_id} has an empty title")
        metadata_items = METADATA.findall(block)
        metadata = {key.lower(): value.strip() for key, value in metadata_items}
        if len(metadata_items) != 3 or set(metadata) != {"date", "status", "scope"}:
            errors.append(f"{entry_id} must declare Date, Status, and Scope exactly once")
        else:
            try:
                recorded_date = date.fromisoformat(metadata["date"])
                if recorded_date > date.today():
                    errors.append(f"{entry_id} date is in the future: {metadata['date']}")
            except ValueError:
                errors.append(f"{entry_id} has an invalid ISO date: {metadata['date']}")
            if metadata["status"] not in ALLOWED_STATUSES:
                errors.append(
                    f"{entry_id} status must be one of {sorted(ALLOWED_STATUSES)}; got {metadata['status']}"
                )
            if not metadata["scope"]:
                errors.append(f"{entry_id} has an empty scope")

        for section in REQUIRED_SECTIONS:
            body = section_body(block, section)
            if body is None:
                errors.append(f"{entry_id} is missing section: {section}")
            elif not body:
                errors.append(f"{entry_id} has an empty section: {section}")

    if "claims ledger" not in source or "scientific claims" not in source:
        errors.append("the log must state its boundary from the scientific claims ledger")

    if errors:
        print("development log check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    status_counts = {
        status: sum(1 for _, _, block in blocks if f"- **Status:** {status}" in block)
        for status in sorted(ALLOWED_STATUSES)
    }
    counts = ", ".join(f"{status}={count}" for status, count in status_counts.items() if count)
    print(f"development log: {len(blocks)} ordered entries pass ({counts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
