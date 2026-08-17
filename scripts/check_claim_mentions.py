#!/usr/bin/env python3
"""Check that each ledger claim is substantively mentioned in its chapter."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "claims/claims.toml"
STOPWORDS = set("the a an and or of to in for with from is are was were this that as by on its their each every not only than into can may has have be do does it".split())


def content_words(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z][a-z0-9-]+", text.lower()) if len(word) > 4 and word not in STOPWORDS}


def main() -> int:
    claims = tomllib.loads(CLAIMS.read_text()).get("claim", [])
    failures: list[str] = []
    for claim in claims:
        chapter = ROOT / claim["chapter"]
        if not chapter.is_file():
            failures.append(f"{claim['claim_id']}: missing chapter {claim['chapter']}")
            continue
        text = chapter.read_text()
        claim_words = content_words(claim["claim_text"])
        chapter_words = content_words(text)
        overlap = len(claim_words & chapter_words) / max(1, len(claim_words))
        if claim["claim_id"] not in text and overlap < 0.45:
            failures.append(f"{claim['claim_id']}: only {overlap:.0%} lexical coverage in {claim['chapter']}")
    if failures:
        print("claim mention audit failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print(f"claim mention audit: {len(claims)} claims have reader-facing chapter coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
