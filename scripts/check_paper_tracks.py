#!/usr/bin/env python3
"""Check that the three paper extraction tracks retain live claims and links."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKS = ROOT / "review/paper-extraction-tracks.md"
CLAIMS = ROOT / "claims/claims.toml"
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def main() -> int:
    text = TRACKS.read_text()
    claim_ids = {item["claim_id"] for item in tomllib.loads(CLAIMS.read_text()).get("claim", [])}
    failures: list[str] = []
    track_count = len(re.findall(r"^## Track [A-C] —", text, re.MULTILINE))
    if track_count != 3:
        failures.append(f"expected three paper tracks, found {track_count}")
    for claim_id in re.findall(r"`([A-Z]+-[0-9]{3})`", text):
        if claim_id not in claim_ids:
            failures.append(f"track references unknown claim {claim_id}")
    for target in LINK.findall(text):
        if target.startswith("http"):
            continue
        path = (TRACKS.parent / target).resolve()
        if not path.is_file():
            failures.append(f"track link does not resolve: {target}")
    for heading in ("## Shared extraction protocol", "**Boundary.**"):
        if heading not in text:
            failures.append(f"track document lacks required boundary/protocol marker {heading}")
    if failures:
        print("paper track audit failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("paper tracks: three tracks, live claim IDs, and local links validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
