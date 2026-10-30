#!/usr/bin/env python3
"""Measure contract-router scope gates on the router-scope paraphrase set.

Reports, per case set, in-scope routing (correct, abstained, or misrouted to
a different contract) and forbidden routing (a contract answers a question its
packet cannot support). The regression set (RSCOPE-*) gates: any forbidden hit
fails `--check`. The independent set (RBLIND-*) is measurement only: it was
written without the gate patterns and must not be used to tune them, so its
results are reported but never gate. A stale report always fails, so any
routing change surfaces as a reviewed diff.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from llm_retrieval import CorpusIndex, MISCONCEPTIONS  # noqa: E402

CASES = ROOT / "llm/router-scope-paraphrases.toml"
# case-ID prefix -> (set name, whether forbidden hits fail the check)
CASE_SETS = {"RSCOPE": ("regression", True), "RBLIND": ("independent", False)}
OUTPUT = ROOT / "llm/generated/router-scope-evaluation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate() -> dict:
    index = CorpusIndex()
    known = {item["id"] for item in index.misconceptions}
    cases = tomllib.loads(CASES.read_text()).get("case", [])
    rows, seen = [], set()
    for case in cases:
        case_id = case["case_id"]
        if case_id in seen:
            raise ValueError(f"duplicate router-scope case ID: {case_id}")
        seen.add(case_id)
        prefix = case_id.split("-", 1)[0]
        if prefix not in CASE_SETS:
            raise ValueError(f"{case_id}: unknown case-set prefix {prefix}")
        expected = case.get("expected_route", "")
        forbidden = case.get("forbidden_routes", [])
        if not expected and not forbidden:
            raise ValueError(f"{case_id}: needs expected_route or forbidden_routes")
        unknown = ({expected} | set(forbidden)) - known - {""}
        if unknown:
            raise ValueError(f"{case_id}: unknown routes {sorted(unknown)}")
        if expected in forbidden:
            raise ValueError(f"{case_id}: expected route is also forbidden")
        routes = index.route_misconceptions(case["question"])
        top1 = routes[0]["misconception_id"] if routes else ""
        rows.append({
            "case_id": case_id,
            "case_set": CASE_SETS[prefix][0],
            "question": case["question"],
            "expected_route": expected,
            "forbidden_routes": forbidden,
            "route_top1": top1,
            "in_scope_hit": bool(expected) and top1 == expected,
            "misrouted": bool(expected) and bool(top1) and top1 != expected,
            "forbidden_hit": top1 in forbidden,
        })
    summary = {}
    for name, _ in CASE_SETS.values():
        members = [row for row in rows if row["case_set"] == name]
        in_scope = [row for row in members if row["expected_route"]]
        summary[name] = {
            "cases": len(members),
            "in_scope_cases": len(in_scope),
            "in_scope_correct": sum(row["in_scope_hit"] for row in in_scope),
            "in_scope_abstained": sum(not row["route_top1"] for row in in_scope),
            "in_scope_misrouted": sum(row["misrouted"] for row in in_scope),
            "guarded_cases": sum(bool(row["forbidden_routes"]) for row in members),
            "forbidden_hits": sum(row["forbidden_hit"] for row in members),
        }
    return {
        "schema_version": "0.2.0",
        "purpose": "Router scope-gate measurement on synthetic paraphrases; not a deployment error-rate estimate.",
        "inputs": {
            "cases": {"path": str(CASES.relative_to(ROOT)), "sha256": sha256(CASES)},
            "misconceptions": {"path": str(MISCONCEPTIONS.relative_to(ROOT)), "sha256": sha256(MISCONCEPTIONS)},
        },
        "summary": summary,
        "cases": rows,
    }


def render(result: dict) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = evaluate()
    text = render(result)
    if args.write:
        OUTPUT.write_text(text)
    for row in result["cases"]:
        if row["forbidden_hit"] or (row["expected_route"] and not row["in_scope_hit"]):
            kind = "FORBIDDEN" if row["forbidden_hit"] else ("misroute" if row["misrouted"] else "abstain")
            print(f"{kind}: {row['case_id']} -> {row['route_top1'] or '(no route)'}")
    for name, item in result["summary"].items():
        print(f"router scope [{name}]: {item['in_scope_correct']}/{item['in_scope_cases']} in-scope correct, "
              f"{item['in_scope_abstained']} abstained, {item['in_scope_misrouted']} misrouted; "
              f"{item['forbidden_hits']} forbidden hit(s) in {item['guarded_cases']} guarded case(s)")
    if args.check:
        gated = {name for name, gate in CASE_SETS.values() if gate}
        if any(result["summary"][name]["forbidden_hits"] for name in gated):
            print("router scope check failed: a scoped contract answered an out-of-scope regression question")
            return 1
        if not OUTPUT.is_file() or OUTPUT.read_text() != text:
            print("router scope check failed: generated report is stale; rerun with --write and review the diff")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
