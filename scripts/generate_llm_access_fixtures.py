#!/usr/bin/env python3
"""Generate and check canonical JSON answer fixtures for the access routes."""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

from llm_service import BookLLMService

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "llm/access-fixtures.toml"
OUTPUT = ROOT / "llm/generated/access-fixtures.jsonl"


def render() -> str:
    service = BookLLMService()
    fixtures = tomllib.loads(INPUT.read_text()).get("fixture", [])
    records = []
    seen = set()
    for fixture in fixtures:
        fixture_id = fixture["fixture_id"]
        if fixture_id in seen:
            raise ValueError(f"duplicate fixture ID: {fixture_id}")
        seen.add(fixture_id)
        response = service.response(fixture["query"], fixture["audience"])
        packet = response["packet"]
        route_ids = [item["misconception_id"] for item in packet["retrieval"]["detected_misconceptions"]]
        if packet["status"] != fixture["expected_status"]:
            raise ValueError(f"{fixture_id}: expected status {fixture['expected_status']}, got {packet['status']}")
        expected_route = fixture.get("expected_misconception_id", "")
        if expected_route and expected_route not in route_ids:
            raise ValueError(f"{fixture_id}: expected route {expected_route} not detected")
        if not expected_route and route_ids:
            raise ValueError(f"{fixture_id}: unexpected qualification route {route_ids}")
        markdown = response["markdown"]
        missing = [heading for heading in fixture["required_markdown_headings"] if f"## {heading}" not in markdown]
        if missing:
            raise ValueError(f"{fixture_id}: Markdown headings missing: {missing}")
        records.append({"fixture": fixture, "response": response})
    return "\n".join(json.dumps(record, sort_keys=True, ensure_ascii=False) for record in records) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        expected = render()
    except (OSError, ValueError, KeyError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        print(f"LLM access fixture generation failed: {error}")
        return 1
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(expected)
    elif not OUTPUT.is_file() or OUTPUT.read_text() != expected:
        print(f"stale access fixtures: {OUTPUT.relative_to(ROOT)}")
        print("run: python3 scripts/generate_llm_access_fixtures.py --write")
        return 1
    print(f"LLM access fixtures: {expected.count(chr(10))} deterministic records pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
