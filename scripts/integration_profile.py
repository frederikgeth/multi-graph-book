"""Validate the immutable package locator and its separate Julia environment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "experiments/integration/profile.json"
REPOSITORY = "frederikgeth/BMOPFTools.jl"
URL = f"https://github.com/{REPOSITORY}.git"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_profile(path: Path = PROFILE) -> dict:
    profile = json.loads(path.read_text())
    if profile.get("schema_version") != "1.0.0" or profile.get("repository") != REPOSITORY:
        raise ValueError("unsupported integration profile schema or repository")
    revision = profile.get("revision", "")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("integration revision must be a full immutable Git SHA")
    for name in ("Project.toml", "Manifest.toml"):
        if digest(path.parent / name) != profile["environment_sha256"][name]:
            raise ValueError(f"integration {name} hash differs from the profile")
    project = tomllib.loads((path.parent / "Project.toml").read_text())
    manifest = tomllib.loads((path.parent / "Manifest.toml").read_text())
    if project.get("sources", {}).get("BMOPFTools") != {"url": URL, "rev": revision}:
        raise ValueError("integration Project does not select the pinned package URL and revision")
    package = manifest["deps"]["BMOPFTools"][0]
    if package.get("repo-url") != URL or package.get("repo-rev") != revision:
        raise ValueError("integration Manifest does not select the pinned package URL and revision")
    if not re.fullmatch(r"[0-9a-f]{40}", package.get("git-tree-sha1", "")):
        raise ValueError("integration Manifest lacks an immutable package tree")
    if package["git-tree-sha1"] != profile.get("git_tree_sha1"):
        raise ValueError("integration package tree differs from the profile")
    if any("path" in entry for entries in manifest["deps"].values() for entry in entries):
        raise ValueError("integration Manifest must not contain local path dependencies")
    if manifest.get("julia_version") != profile.get("julia_version"):
        raise ValueError("integration Julia version differs from the lockfile")
    return profile


def validate_checkout(root: Path, profile: dict) -> None:
    def git(*args: str) -> str:
        try:
            return subprocess.check_output(["git", "-C", str(root), *args], text=True,
                                           stderr=subprocess.PIPE).strip()
        except subprocess.CalledProcessError as error:
            raise ValueError(f"cannot inspect integration checkout: {error.stderr.strip()}") from error

    if Path(git("rev-parse", "--show-toplevel")).resolve() != root.resolve():
        raise ValueError("BMOPFTools root must be the package Git checkout root")
    if git("rev-parse", "HEAD") != profile["revision"]:
        raise ValueError("BMOPFTools checkout revision differs from the integration pin")
    if git("status", "--porcelain", "--untracked-files=normal"):
        raise ValueError("BMOPFTools integration checkout is dirty; commit and deliberately repin first")
    if git("rev-parse", "HEAD^{tree}") != profile["git_tree_sha1"]:
        raise ValueError("BMOPFTools checkout tree differs from the integration lockfile")
