#!/usr/bin/env python3
"""Run the pinned book/package integration in its own locked Julia environment."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from integration_profile import PROFILE, ROOT, digest, load_profile, validate_checkout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bmopf-root", type=Path, default=ROOT.parent / "BMOPFTools.jl")
    parser.add_argument("--output", type=Path, help="new results directory outside the repository")
    parser.add_argument("--check-profile", action="store_true", help="check the committed lock without Julia or a package checkout")
    args = parser.parse_args()
    profile = load_profile()
    if args.check_profile:
        print("Integration revision and environment locks agree; no runtime check claimed.")
        return 0
    package = args.bmopf_root.resolve()
    validate_checkout(package, profile)
    if args.output:
        output = args.output.resolve()
        if output.is_relative_to(ROOT):
            parser.error("choose an integration output directory outside the repository")
        output.mkdir(parents=True, exist_ok=False)
    else:
        output = Path(tempfile.mkdtemp(prefix="book-bmopf-integration-"))
    print(f"Integration output: {output}", flush=True)
    environment = PROFILE.parent
    # Package-owned recipe tests launch Julia with --project=<package-root>.
    # Keep those subprocesses on this same lock, even when a sibling checkout
    # contains an ignored, stale developer Manifest. Exclude the default global
    # environment as well. This variable is inherited by recipe subprocesses.
    runtime_env = dict(os.environ, JULIA_LOAD_PATH=f"{environment}{os.pathsep}@stdlib")
    book_revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    book_dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    record = {
        "status": "running", "started_at": datetime.now(timezone.utc).isoformat(),
        "integration_profile_sha256": digest(PROFILE), "profile": profile,
        "book_revision": book_revision, "book_dirty": book_dirty,
        "pair_sha256": json.loads((ROOT / "generated/federated-knowledge-pair-manifest.json").read_text())["pair_sha256"],
        "book_source_sha256": {name: digest(ROOT / name) for name in (
            "scripts/check_bmopf_integration.py", "scripts/integration_profile.py",
            "scripts/check_federated_knowledge.py", "experiments/running_network.jl",
            "experiments/lessons/verify_running_network.jl", "experiments/lessons/transformer_ports.jl",
            "experiments/lessons/parameter_reuse.jl", "experiments/lessons/parameter_reuse.py")},
        "scope": "package-owned export, contract, property, execution and MCP tests; scoped running-network verification; parameter reuse and failure-state lesson",
        "julia_load_path": runtime_env["JULIA_LOAD_PATH"],
        "not_established": ["full package test suite", "independent all-device feasibility", "global optimality", "physical model adequacy"],
        "commands": [],
    }

    def save() -> None:
        (output / "run.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")

    def run(command: list[str], cwd: Path = ROOT) -> None:
        record["commands"].append({"argv": command, "cwd": str(cwd)})
        save()
        with (output / "execution.log").open("a") as log:
            log.write("\nCOMMAND " + repr(command) + "\n")
            log.flush()
            subprocess.run(command, cwd=cwd, env=runtime_env, stdout=log, stderr=subprocess.STDOUT, check=True)

    save()
    try:
        version = subprocess.check_output(["julia", "--startup-file=no", "-e", "print(VERSION)"], text=True)
        if version != profile["julia_version"]:
            raise ValueError(f"integration requires Julia {profile['julia_version']}; found {version}")
        run([sys.executable, "scripts/generate_executable_knowledge.py", "--check"], package)
        run([sys.executable, "scripts/generate_finding_registry.py", "--check"], package)
        run([sys.executable, "scripts/check_federated_knowledge.py", "--check", "--bmopf-root", str(package)])
        julia = ["julia", "--startup-file=no", f"--project={environment}"]
        run(julia + ["-e", "using Pkg; Pkg.instantiate(; allow_autoprecomp=false)"])
        load_profile()  # Pkg may not silently rewrite the recorded environment.
        test_code = '''using Test, BMOPFTools, LinearAlgebra, Pkg
            expected_tree = ARGS[2]
            @assert string(Pkg.dependencies()[Base.PkgId(BMOPFTools).uuid].tree_hash) == expected_tree
            for name in ("scientific_contract_tests.jl", "property_based_contract_tests.jl",
                         "executable_knowledge_tests.jl", "execution_interface_tests.jl", "mcp_execution_tests.jl")
                include(joinpath(ARGS[1], "test", name))
            end'''
        run(julia + ["-e", test_code, str(package), profile["git_tree_sha1"]])
        run(julia + ["experiments/lessons/verify_running_network.jl", str(output / "verification.json")])
        run(julia + ["experiments/lessons/transformer_ports.jl", str(output / "transformer-ports.json")])
        run(julia + ["experiments/lessons/parameter_reuse.jl", str(output / "parameter-reuse.json")])
        load_profile()
        validate_checkout(package, profile)
        record["status"] = "passed"
    except Exception as error:
        record["status"] = "failed"
        record["error"] = str(error)
        raise
    finally:
        record["finished_at"] = datetime.now(timezone.utc).isoformat()
        save()
    print(f"Pinned integration passed; evidence and logs: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
