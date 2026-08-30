#!/usr/bin/env python3
"""Run the release gates and validate an internal release-candidate manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "review/release-candidate-manifest.json"
PYTHON = sys.executable

CHECKS: list[tuple[str, list[str]]] = [
    ("bibliography", ["julia", "--startup-file=no", "scripts/check_bibliography.jl"]),
    ("claims", ["julia", "--startup-file=no", "scripts/check_claims.jl"]),
    ("claim mentions", [PYTHON, "scripts/check_claim_mentions.py"]),
    ("evidence summary", [PYTHON, "scripts/check_evidence_summary.py"]),
    ("review snapshot", [PYTHON, "scripts/check_review_snapshot.py"]),
    ("evidence matrix", [PYTHON, "scripts/check_evidence_matrix.py"]),
    ("development log", [PYTHON, "scripts/check_development_log.py"]),
    ("agent benchmark", [PYTHON, "scripts/check_agent_benchmark.py", "--check"]),
    ("figures", [PYTHON, "scripts/check_figures.py"]),
    ("vocabulary", [PYTHON, "scripts/check_vocabulary.py"]),
    ("LLM accessibility", [PYTHON, "scripts/check_llm_accessibility.py"]),
    ("LLM retrieval", [PYTHON, "scripts/evaluate_llm_retrieval.py", "--check"]),
    ("LLM neural benchmark", [PYTHON, "scripts/check_neural_benchmark.py"]),
    ("LLM access routes", [PYTHON, "scripts/check_llm_routes.py"]),
    ("LLM answer contract", [PYTHON, "scripts/check_llm_answer_contract.py"]),
    ("LLM access fixtures", [PYTHON, "scripts/generate_llm_access_fixtures.py", "--check"]),
    ("LLM adversarial evaluation", [PYTHON, "scripts/evaluate_llm_adversarial.py", "--check"]),
    ("prose numbers", [PYTHON, "scripts/check_prose_numbers.py"]),
    ("math hygiene", [PYTHON, "scripts/check_math_hygiene.py"]),
    ("callouts", [PYTHON, "scripts/check_callouts.py"]),
    ("page anchors", [PYTHON, "scripts/check_page_ids.py"]),
    ("paper tracks", [PYTHON, "scripts/check_paper_tracks.py"]),
    ("generated artifact manifest", [PYTHON, "scripts/generate_artifact_manifest.py", "--check"]),
    ("artifacts", [PYTHON, "scripts/check_artifacts.py"]),
    ("rendered outputs", [PYTHON, "scripts/check_rendered_outputs.py"]),
    ("PDF references", [PYTHON, "scripts/check_pdf_refs.py"]),
    ("experiment suite", ["julia", "--startup-file=no", "--project=experiments", "experiments/test/runtests.jl"]),
    ("git diff", ["git", "diff", "--check"]),
]

EXCLUDED_PARTS = {".git", "__pycache__"}
HASH_ROOTS = (
    "README.md",
    "ARCHITECTURE.md",
    "BOOK_PLAN.md",
    "CONTRIBUTING.md",
    "OPEN_TRANCHES.md",
    "QUALITY_CONTROL.md",
    "ROADMAP.md",
    "benchmarks",
    "claims",
    "docs/src",
    "docs/make.jl",
    "docs/build",
    "docs/latex_build",
    "experiments",
    "package",
    "schemas",
    "scripts",
    "review",
    "llm",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def release_files() -> list[Path]:
    paths: set[Path] = set()
    for root_name in HASH_ROOTS:
        root = ROOT / root_name
        if root.is_file():
            paths.add(root)
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(ROOT)
            if any(part in EXCLUDED_PARTS for part in relative.parts):
                continue
            if path == MANIFEST:
                continue
            if relative.parts[:2] == ("docs", "latex_build") and path.suffix != ".pdf":
                continue
            paths.add(path)
    return sorted(paths, key=lambda path: path.relative_to(ROOT).as_posix())


def run_checks() -> tuple[dict[str, str], list[str]]:
    outputs: dict[str, str] = {}
    failures: list[str] = []
    environment = os.environ.copy()
    writable_depot = "/private/tmp/mgb-julia-depot"
    depot_parts = [writable_depot]
    existing_depot = environment.get("JULIA_DEPOT_PATH", "")
    if existing_depot:
        depot_parts.extend(part for part in existing_depot.split(os.pathsep) if part)
    home_depot = str(Path.home() / ".julia")
    if home_depot not in depot_parts:
        depot_parts.append(home_depot)
    environment["JULIA_DEPOT_PATH"] = os.pathsep.join(depot_parts)
    for name, command in CHECKS:
        print(f"[release] {name}: {' '.join(command)}")
        result = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        outputs[name] = result.stdout
        if result.returncode:
            failures.append(f"{name} exited with status {result.returncode}\n{result.stdout}")
            print(result.stdout, end="")
        else:
            last_line = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else "passed"
            print(f"  {last_line}")
    return outputs, failures


def first_int(pattern: str, text: str, label: str) -> int:
    match = re.search(pattern, text)
    if match is None:
        raise ValueError(f"could not parse {label} from validator output")
    return int(match.group(1))


def first_tenths_percent(pattern: str, text: str, label: str) -> int:
    match = re.search(pattern, text)
    if match is None:
        raise ValueError(f"could not parse {label} from validator output")
    return int(match.group(1)) * 10 + int(match.group(2))


def observed_counts(outputs: dict[str, str]) -> dict[str, int]:
    claims = first_int(r"claims ledger: (\d+) unique claims", outputs["claims"], "claims")
    bibliography = outputs["bibliography"]
    rendered = outputs["rendered outputs"]
    artifacts = outputs["artifacts"]
    llm = outputs["LLM accessibility"]
    llm_retrieval = outputs["LLM retrieval"]
    return {
        "claims": claims,
        "bibliography_records": first_int(r"bibliography audit: (\d+) records", bibliography, "bibliography records"),
        "bibliography_unique_doi_fields": first_int(r"records covered; (\d+) unique DOI", bibliography, "unique DOI fields"),
        "html_pages": first_int(r"rendered outputs: (\d+) HTML pages", rendered, "HTML pages"),
        "image_tags": first_int(r"HTML pages, (\d+) image tags", rendered, "image tags"),
        "pdf_pages": first_int(r"image tags, (\d+) PDF pages", rendered, "PDF pages"),
        "required_artifacts": first_int(r"artifacts: (\d+) required files", artifacts, "required artifacts"),
        "certificates": first_int(r"required files, (\d+) certificates", artifacts, "certificates"),
        "source_objects": first_int(r"transformer contracts, (\d+) source objects", artifacts, "source objects"),
        "view_maps": first_int(r"source objects, (\d+) view maps", artifacts, "view maps"),
        "local_links": first_int(r"view maps, and (\d+) local links", artifacts, "local links"),
        "llm_corpus_records": first_int(r"LLM accessibility: (\d+) records", llm, "LLM corpus records"),
        "llm_section_records": first_int(r"records: (\d+) sections", llm, "LLM section records"),
        "llm_claim_bundles": first_int(r"sections, (\d+) claim bundles", llm, "LLM claim bundles"),
        "llm_concept_bundles": first_int(r"claim bundles, (\d+) concept bundles", llm, "LLM concept bundles"),
        "llm_misconception_contracts": first_int(r", (\d+) misconception contracts", llm, "LLM misconception contracts"),
        "llm_evaluation_cases": first_int(r"and (\d+) evaluation cases pass", llm, "LLM evaluation cases"),
        "llm_retrieval_cases": first_int(r"LLM retrieval: (\d+) cases", llm_retrieval, "LLM retrieval cases"),
        "llm_heldout_cases": first_int(r"heldout=(\d+)", llm_retrieval, "LLM held-out cases"),
        "llm_route_top1_percent": first_int(r"route_top1=(\d+)\.\d+%", llm_retrieval, "LLM route top-1 percent"),
        "llm_lexical_complete_at_10_tenths_percent": first_tenths_percent(
            r"lexical_complete_at_10=(\d+)\.(\d)%", llm_retrieval, "LLM lexical complete at 10"
        ),
        "llm_contract_complete_percent": first_int(
            r"contract_complete=(\d+)\.\d+%", llm_retrieval, "LLM contract complete percent"
        ),
        "llm_heldout_hybrid_recall_at_10_tenths_percent": first_tenths_percent(
            r"heldout_hybrid_recall_at_10=(\d+)\.(\d)%",
            llm_retrieval,
            "LLM held-out hybrid recall at 10",
        ),
        "llm_heldout_router_fired_tenths_percent": first_tenths_percent(
            r"heldout_router_fired=(\d+)\.(\d)%",
            llm_retrieval,
            "LLM held-out router firing",
        ),
        "llm_heldout_hybrid_zero_recall_at_10_cases": first_int(
            r"heldout_hybrid_zero_recall_at_10=(\d+)/\d+",
            llm_retrieval,
            "LLM held-out hybrid zero-recall cases",
        ),
    }


def manifest_payload(outputs: dict[str, str]) -> dict:
    portable_checks = []
    for name, command in CHECKS:
        recorded_command = ["python3" if command[0] == PYTHON else command[0], *command[1:]]
        portable_checks.append({"name": name, "command": recorded_command})
    return {
        "schema_version": 1,
        "release_candidate_id": "mgb-2026-08-17-internal-rc",
        "generated_on": date.today().isoformat(),
        "status": "internally_validated_not_externally_reviewed",
        "external_reviewed_claims": 0,
        "independent_human_double_coding": False,
        "observed_counts": observed_counts(outputs),
        "checks": portable_checks,
        "files": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
            for path in release_files()
        ],
    }


def compare_manifest(expected: dict, actual: dict) -> list[str]:
    errors: list[str] = []
    for field in ("schema_version", "release_candidate_id", "status", "external_reviewed_claims", "independent_human_double_coding"):
        if actual.get(field) != expected.get(field):
            errors.append(f"manifest field differs: {field}")
    if actual.get("observed_counts") != expected.get("observed_counts"):
        errors.append(f"manifest counts differ: expected {expected.get('observed_counts')}, recorded {actual.get('observed_counts')}")
    recorded = {entry["path"]: entry["sha256"] for entry in actual.get("files", [])}
    current = {entry["path"]: entry["sha256"] for entry in expected.get("files", [])}
    if set(recorded) != set(current):
        errors.append("manifest file list differs from the current release inputs")
    for path in sorted(set(recorded) & set(current)):
        if recorded[path] != current[path]:
            errors.append(f"manifest hash changed: {path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write or refresh the release-candidate manifest after all checks pass")
    parser.add_argument("--check", action="store_true", help="check the existing manifest; this is the default")
    args = parser.parse_args()
    if args.write and args.check:
        parser.error("use either --write or --check, not both")

    outputs, failures = run_checks()
    if failures:
        print("release candidate validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    expected = manifest_payload(outputs)
    if args.write:
        MANIFEST.write_text(json.dumps(expected, indent=2) + "\n")
        print(f"release candidate manifest written: {MANIFEST.relative_to(ROOT)}")
        print(f"release candidate counts: {expected['observed_counts']}")
        return 0

    if not MANIFEST.is_file():
        print(f"release candidate validation failed: missing {MANIFEST.relative_to(ROOT)}")
        print("run with --write after rebuilding the HTML and PDF outputs")
        return 1
    actual = json.loads(MANIFEST.read_text())
    errors = compare_manifest(expected, actual)
    if errors:
        print("release candidate manifest validation failed:")
        for error in errors:
            print(f"- {error}")
        print("run with --write only after deliberately updating the release candidate")
        return 1
    print(f"release candidate: {actual['release_candidate_id']} is internally validated and unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
