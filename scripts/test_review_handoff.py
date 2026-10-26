#!/usr/bin/env python3
"""Synthetic Git fixtures for source portability; these are not agent/review results."""
import json
from pathlib import Path
import tempfile
import tomllib
import unittest
import zipfile

import review_handoff as handoff


class ReviewHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="mgb-handoff-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.sources = self.root / "sources"
        self.package = self.sources / "package"
        self.book = self.sources / "book"
        self.environment = self.sources / "environment"
        for repo in (self.book, self.package):
            repo.mkdir(parents=True)
            handoff.run("git", "init", "-q", repo)
        (self.package / "component.jl").write_text("# synthetic package fixture\n")
        self.package_revision = self.commit(self.package)
        tree = handoff.run("git", "-C", self.package, "rev-parse", "HEAD^{tree}")
        profiles = self.book / "experiments/integration"
        profiles.mkdir(parents=True)
        (profiles / "linear-audit-candidate.json").write_text(json.dumps({
            "revision": self.package_revision, "git_tree_sha1": tree,
        }))
        (profiles / "profile.json").write_text(json.dumps({
            "revision": "b" * 40, "julia_version": "1.12.6",
        }))
        (self.book / "lesson.md").write_text("Synthetic teaching source.\n")
        self.pdf = self.sources / "recorded-pdf-bytes"
        self.pdf.write_bytes(b"synthetic frozen output; not a PDF render test")
        self.html = self.sources / "html"
        self.html.mkdir()
        (self.html / "index.html").write_text("<title>Synthetic handoff</title>")
        (self.html / "GraphModelsForPowerSystems.pdf").write_bytes(self.pdf.read_bytes())
        review = self.book / "review"
        review.mkdir()
        (review / "checkpoint-teaching-evidence-2026-10-26.json").write_text(json.dumps({
            "source_sha256": {"lesson.md": handoff.digest(self.book / "lesson.md")},
            "rendering": {"pdf_sha256": handoff.digest(self.pdf)},
        }))
        self.book_revision = self.commit(self.book)
        self.environment.mkdir()
        (self.environment / "Project.toml").write_text('[deps]\nBMOPFTools = "fixture-uuid"\n')
        (self.environment / "Manifest.toml").write_text(
            'julia_version = "1.12.6"\nmanifest_format = "2.0"\n'
            '[[deps.BMOPFTools]]\npath = ' + json.dumps(str(self.package)) + '\n'
            'uuid = "fixture-uuid"\nversion = "0.1.0"\n'
            '[[deps.TransitiveFixture]]\ngit-tree-sha1 = "unchanged-tree"\nversion = "2.3.4"\n')
        self.request = self.root / "request.md"
        self.request.write_text("Synthetic review scope. No reviewer assigned.\n")
        self.output = self.root / "handoff"

    def commit(self, repo):
        handoff.run("git", "-C", repo, "add", ".")
        handoff.run("git", "-C", repo, "-c", "user.name=handoff-fixture",
                    "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
        return handoff.run("git", "-C", repo, "rev-parse", "HEAD")

    def build(self):
        return handoff.build(self.book, self.book_revision, self.package,
                             self.environment, self.pdf, self.html, self.request, self.output)

    def test_handoff_survives_source_removal_and_relocation(self):
        old_manifest = tomllib.loads((self.environment / "Manifest.toml").read_text())
        self.build()
        moved = self.root / "elsewhere" / "handoff"
        moved.parent.mkdir()
        self.output.rename(moved)
        self.sources.rename(self.root / "unavailable-originals")
        extracted = self.root / "fresh-review"
        result = handoff.unpack(moved, extracted)
        for folder, revision in (("book", self.book_revision), ("BMOPFTools.jl", self.package_revision)):
            self.assertEqual(handoff.run("git", "-C", extracted / folder, "rev-parse", "HEAD"), revision)
            self.assertEqual(handoff.run("git", "-C", extracted / folder, "status", "--porcelain"), "")
            self.assertFalse((extracted / folder / ".git/objects/info/alternates").exists())
        old_manifest["deps"]["BMOPFTools"][0]["path"] = "../BMOPFTools.jl"
        self.assertEqual(tomllib.loads((extracted / "environment/Manifest.toml").read_text()), old_manifest)
        self.assertEqual(result["kind"], "local_review_handoff_not_release")
        self.assertEqual((extracted / "html/index.html").read_text(), "<title>Synthetic handoff</title>")

    def test_tampered_file_and_extra_manifest_path_are_rejected(self):
        self.build()
        (self.output / "review.pdf").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            handoff.verify(self.output)
        manifest = self.output / "handoff-manifest.json"
        payload = json.loads(manifest.read_text())
        payload["files"]["../outside"] = "0" * 64
        manifest.write_text(json.dumps(payload))
        with self.assertRaisesRegex(ValueError, "unexpected or missing"):
            handoff.verify(self.output)

    def test_dirty_candidate_and_wrong_pdf_are_rejected_before_writing(self):
        (self.package / "component.jl").write_text("changed\n")
        with self.assertRaisesRegex(ValueError, "must be clean"):
            self.build()
        self.assertFalse(self.output.exists())
        handoff.run("git", "-C", self.package, "restore", "component.jl")
        self.pdf.write_bytes(b"different output")
        with self.assertRaisesRegex(ValueError, "PDF differs"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_additional_path_dependency_is_not_silently_rebound(self):
        with (self.environment / "Manifest.toml").open("a") as stream:
            stream.write('[[deps.OtherLocal]]\npath = "/unrecorded/source"\n')
        with self.assertRaisesRegex(ValueError, "only one BMOPFTools"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_existing_destination_is_preserved(self):
        self.build()
        destination = self.root / "existing"
        destination.mkdir()
        (destination / "keep").write_text("original")
        with self.assertRaisesRegex(ValueError, "must be new"):
            handoff.unpack(self.output, destination)
        self.assertEqual((destination / "keep").read_text(), "original")

    def test_html_archive_cannot_escape_the_new_directory(self):
        self.build()
        with zipfile.ZipFile(self.output / "html.zip", "w") as archive:
            archive.writestr("../outside", "not allowed")
        manifest = self.output / "handoff-manifest.json"
        payload = json.loads(manifest.read_text())
        payload["files"]["html.zip"] = handoff.digest(self.output / "html.zip")
        manifest.write_text(json.dumps(payload))
        with self.assertRaisesRegex(ValueError, "unsafe HTML"):
            handoff.unpack(self.output, self.root / "bad-html")
        self.assertFalse((self.root / "outside").exists())


if __name__ == "__main__":
    unittest.main()
