#!/usr/bin/env python3
"""Build, verify and unpack a local source handoff; never publish or repin it."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REF = "refs/heads/review-snapshot"
FILES = {"book.bundle", "BMOPFTools.bundle", "Project.toml", "Manifest.toml",
         "review.pdf", "html.zip", "review-request.md", "README.md", "review_handoff.py"}


def run(*args, cwd=None):
    return subprocess.check_output([str(a) for a in args], cwd=cwd,
                                   stderr=subprocess.PIPE).decode().strip()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git_text(root, revision, path):
    return run("git", "-C", root, "show", f"{revision}:{path}")


def revision_id(root, revision):
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("select an immutable full Git revision")
    actual = run("git", "-C", root, "rev-parse", f"{revision}^{{commit}}")
    if actual != revision:
        raise ValueError("Git revision mismatch")
    return {"revision": actual,
            "tree": run("git", "-C", root, "rev-parse", f"{actual}^{{tree}}")}


def rebind_environment(environment, package):
    project = (environment / "Project.toml").read_bytes()
    original = (environment / "Manifest.toml").read_text()
    before = tomllib.loads(original)
    paths = [(name, entry) for name, entries in before["deps"].items()
             for entry in entries if "path" in entry]
    if len(paths) != 1 or paths[0][0] != "BMOPFTools":
        raise ValueError("only one BMOPFTools path dependency can be relocated")
    old_path = Path(paths[0][1]["path"])
    resolved = old_path if old_path.is_absolute() else environment / old_path
    if resolved.resolve() != package.resolve():
        raise ValueError("locked environment selects a different package checkout")
    rebound, count = re.subn(r'^path = "[^"\n]*"$',
                            'path = "../BMOPFTools.jl"', original, flags=re.M)
    expected = copy.deepcopy(before)
    expected["deps"]["BMOPFTools"][0]["path"] = "../BMOPFTools.jl"
    if count != 1 or tomllib.loads(rebound) != expected:
        raise ValueError("relocation changed more than the package path")
    return project, rebound, {name: digest(environment / name)
                              for name in ("Project.toml", "Manifest.toml")}


def make_bundle(source, revision, output):
    # Temporary refs belong to an expendable bare clone, never the source repo.
    with tempfile.TemporaryDirectory(prefix="mgb-handoff-git-") as temporary:
        bare = Path(temporary) / "snapshot.git"
        run("git", "clone", "--bare", "--shared", source, bare)
        run("git", "-C", bare, "update-ref", REF, revision)
        run("git", "-C", bare, "bundle", "create", output.resolve(), REF)


def build(book, revision, package, environment, pdf, html_root, request, output):
    if output.exists():
        raise ValueError("handoff output already exists")
    book_id = revision_id(book, revision)
    profile = json.loads(git_text(book, revision,
                                 "experiments/integration/linear-audit-candidate.json"))
    package_id = revision_id(package, profile["revision"])
    if package_id["tree"] != profile["git_tree_sha1"]:
        raise ValueError("candidate tree differs from the book profile")
    if run("git", "-C", package, "rev-parse", "HEAD") != package_id["revision"]:
        raise ValueError("candidate checkout is not at the selected revision")
    if run("git", "-C", package, "status", "--porcelain"):
        raise ValueError("candidate checkout must be clean")
    evidence = json.loads(git_text(book, revision,
                                  "review/checkpoint-teaching-evidence-2026-10-26.json"))
    if digest(pdf) != evidence["rendering"]["pdf_sha256"]:
        raise ValueError("PDF differs from the frozen teaching evidence")
    if digest(html_root / "GraphModelsForPowerSystems.pdf") != digest(pdf):
        raise ValueError("HTML download differs from the frozen PDF")
    html_files = sorted(path for path in html_root.rglob("*") if path.is_file())
    if any(path.is_symlink() for path in html_root.rglob("*")):
        raise ValueError("rendered HTML must contain regular files, not symlinks")
    for path, expected in evidence["source_sha256"].items():
        # git show text strips final newlines; hash the bytes without that helper.
        content = subprocess.check_output(["git", "-C", str(book), "show", f"{revision}:{path}"])
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError(f"frozen source evidence mismatch: {path}")
    project, manifest, original_hashes = rebind_environment(environment, package)
    published = json.loads(git_text(book, revision, "experiments/integration/profile.json"))
    output.mkdir(parents=True)
    make_bundle(book, revision, output / "book.bundle")
    make_bundle(package, package_id["revision"], output / "BMOPFTools.bundle")
    (output / "Project.toml").write_bytes(project)
    (output / "Manifest.toml").write_text(manifest)
    shutil.copyfile(pdf, output / "review.pdf")
    with zipfile.ZipFile(output / "html.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in html_files:
            archive.write(path, path.relative_to(html_root).as_posix())
    shutil.copyfile(request, output / "review-request.md")
    shutil.copyfile(__file__, output / "review_handoff.py")
    (output / "README.md").write_text("""# Local author/domain review handoff

This is a frozen source handoff, not a release or an externally reviewed result.
The book and candidate revisions and SHA-256 hashes are in handoff-manifest.json.
Git history is included; Julia, its package cache and binary artifacts are not.
Dependencies may require network access on first installation.

Verify, then unpack into a NEW directory (Python 3.11+ and Git required):

```sh
python3 review_handoff.py verify .
python3 review_handoff.py unpack . --output /path/to/new/review
```

From that new directory, read review-request.md and review.pdf; open html/index.html
for the complete rendered reference library. Book-only checks:

```sh
cd book
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_llm_reproducibility.py
```

For candidate execution, use the Julia version in handoff-manifest.json. From
the unpacked directory, instantiate without resolving or editing the lock:

```sh
julia --startup-file=no --project=environment -e 'using Pkg; Pkg.instantiate()'
julia --startup-file=no --project=environment book/experiments/lessons/verify_linear_coverage.jl coverage.json
```

The companion requires a new output file and the exact clean candidate. Its
result is a fresh run, not a replay of a historical solver trajectory. The
environment differs from the author environment only in the local package path;
transitive dependency declarations are unchanged. New environment/output hashes
are expected and must be recorded. Hash checks establish integrity against this
manifest, not authorship or physical-model adequacy. Do not promote a package
pin, PSK status or external-review claim merely because these commands pass.
""")
    payload = {
        "schema_version": "1.0.0", "kind": "local_review_handoff_not_release",
        "book": book_id, "candidate": package_id,
        "published_package_revision_unchanged": published["revision"],
        "julia_version": published["julia_version"],
        "original_environment_sha256": original_hashes,
        "environment_change": "deps.BMOPFTools[0].path only; ../BMOPFTools.jl",
        "pdf": evidence["rendering"],
        "html_file_count": len(html_files),
        "files": {name: digest(output / name) for name in sorted(FILES)},
        "external_review_or_publication_claimed": False,
    }
    (output / "handoff-manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    verify(output)
    return payload


def verify(root):
    payload = json.loads((root / "handoff-manifest.json").read_text())
    if payload.get("kind") != "local_review_handoff_not_release" or payload.get("schema_version") != "1.0.0":
        raise ValueError("unsupported handoff manifest")
    if set(payload.get("files", {})) != FILES:
        raise ValueError("unexpected or missing handoff files")
    for name, expected in payload["files"].items():
        if (root / name).is_symlink() or digest(root / name) != expected:
            raise ValueError(f"handoff checksum mismatch: {name}")
    with tempfile.TemporaryDirectory(prefix="mgb-handoff-verify-") as temporary:
        run("git", "init", "-q", temporary)
        for filename, key in (("book.bundle", "book"), ("BMOPFTools.bundle", "candidate")):
            bundle = (root / filename).resolve()
            run("git", "-C", temporary, "bundle", "verify", bundle)
            if run("git", "bundle", "list-heads", bundle) != f'{payload[key]["revision"]} {REF}':
                raise ValueError(f"unexpected bundle identity: {filename}")
    return payload


def unpack(root, output):
    payload = verify(root)
    if output.exists():
        raise ValueError("unpack destination must be new")
    output.mkdir(parents=True)
    for filename, folder, key in (("book.bundle", "book", "book"),
                                  ("BMOPFTools.bundle", "BMOPFTools.jl", "candidate")):
        target = output / folder
        run("git", "clone", "--branch", "review-snapshot", "--single-branch", (root / filename).resolve(), target)
        if revision_id(target, payload[key]["revision"]) != payload[key]:
            raise ValueError("unpacked repository identity mismatch")
        if run("git", "-C", target, "status", "--porcelain"):
            raise ValueError("unpacked repository is not clean")
    environment = output / "environment"
    environment.mkdir()
    for name in ("Project.toml", "Manifest.toml"):
        shutil.copyfile(root / name, environment / name)
    for name in ("README.md", "review-request.md", "handoff-manifest.json", "review.pdf"):
        shutil.copyfile(root / name, output / name)
    with zipfile.ZipFile(root / "html.zip") as archive:
        for entry in archive.infolist():
            name = PurePosixPath(entry.filename)
            mode = entry.external_attr >> 16
            if name.is_absolute() or ".." in name.parts or "\\" in entry.filename or (mode & 0o170000) == 0o120000:
                raise ValueError("unsafe HTML archive entry")
        archive.extractall(output / "html")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("build")
    create.add_argument("--book-root", type=Path, default=ROOT)
    create.add_argument("--book-revision", required=True)
    for name in ("package", "environment", "pdf", "html", "request", "output"):
        create.add_argument("--" + name, type=Path, required=True)
    check = commands.add_parser("verify")
    check.add_argument("root", type=Path)
    extract = commands.add_parser("unpack")
    extract.add_argument("root", type=Path)
    extract.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "build":
            result = build(args.book_root, args.book_revision, args.package,
                           args.environment, args.pdf, args.html, args.request, args.output)
        elif args.command == "verify":
            result = verify(args.root)
        else:
            result = unpack(args.root, args.output)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"review handoff failed: {error}\n")
    print(f'review handoff {args.command}: book {result["book"]["revision"]}; candidate {result["candidate"]["revision"]}')


if __name__ == "__main__":
    main()
