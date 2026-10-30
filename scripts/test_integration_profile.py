#!/usr/bin/env python3
"""Reject unreproducible package identities and exercise discovery provenance."""

import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from integration_profile import PROFILE, digest, load_profile, validate_checkout


class IntegrationProfileTests(unittest.TestCase):
    def test_committed_profile_and_tampered_environment(self):
        profile = load_profile()
        self.assertEqual(len(profile["revision"]), 40)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("profile.json", "Project.toml", "Manifest.toml"):
                shutil.copy2(PROFILE.parent / name, root / name)
            lock = root / "profile.json"
            with (root / "Manifest.toml").open("a") as stream:
                stream.write("\n# changed environment\n")
            with self.assertRaisesRegex(ValueError, "Manifest.toml hash"):
                load_profile(lock)
            changed = copy.deepcopy(profile)
            changed["environment_sha256"]["Manifest.toml"] = digest(root / "Manifest.toml")
            changed["revision"] = "main"
            lock.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "immutable Git SHA"):
                load_profile(lock)
            changed["revision"] = "0" * 40
            lock.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "Project does not select"):
                load_profile(lock)

    def test_local_path_dependency_is_not_a_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("profile.json", "Project.toml", "Manifest.toml"):
                shutil.copy2(PROFILE.parent / name, root / name)
            manifest = root / "Manifest.toml"
            manifest.write_text(manifest.read_text().replace("[[deps.PowerIO]]", '[[deps.PowerIO]]\npath = "/tmp/local-powerio"'))
            profile = load_profile()
            profile["environment_sha256"]["Manifest.toml"] = digest(manifest)
            (root / "profile.json").write_text(json.dumps(profile))
            with self.assertRaisesRegex(ValueError, "local path dependencies"):
                load_profile(root / "profile.json")

    def test_checkout_refuses_wrong_revision_tree_and_dirty_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(["git", "-C", str(root), *args], text=True,
                                               stderr=subprocess.PIPE).strip()
            git("init", "--quiet")
            (root / "source.txt").write_text("reviewed\n")
            git("add", "source.txt")
            git("-c", "user.name=Integration test", "-c", "user.email=test@example.invalid",
                "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "fixture")
            profile = {"revision": git("rev-parse", "HEAD"), "git_tree_sha1": git("rev-parse", "HEAD^{tree}")}
            validate_checkout(root, profile)
            with self.assertRaisesRegex(ValueError, "revision differs"):
                validate_checkout(root, {**profile, "revision": "0" * 40})
            with self.assertRaisesRegex(ValueError, "tree differs"):
                validate_checkout(root, {**profile, "git_tree_sha1": "0" * 40})
            (root / "source.txt").write_text("unreviewed\n")
            with self.assertRaisesRegex(ValueError, "dirty"):
                validate_checkout(root, profile)
            (root / "source.txt").write_text("reviewed\n")
            (root / "extra.txt").write_text("untracked\n")
            with self.assertRaisesRegex(ValueError, "dirty"):
                validate_checkout(root, profile)

    def test_service_exposes_one_identity_and_rejects_packet_identity_drift(self):
        from llm_service import BookLLMService, validate_context_packet
        from mcp_llm_server import MANIFEST_URI, handle_request
        service = BookLLMService()
        identity = service.health()["source_identity"]
        self.assertEqual(identity["bmopftools_revision"], load_profile()["revision"])
        self.assertEqual(identity["executable_evidence"], "pinned_export_only_no_runtime_inspected")
        answer = service.response("Do loads belong in Ybus?")
        self.assertEqual(answer["packet"]["source_identity"], identity)
        self.assertIn(identity["pair_sha256"], answer["markdown"])
        self.assertEqual(service.search("Ybus")["source_identity"], identity)
        resource = handle_request(service, {"jsonrpc": "2.0", "id": 1, "method": "resources/read",
                                            "params": {"uri": MANIFEST_URI}})
        self.assertEqual(json.loads(resource["result"]["contents"][0]["text"])["source_identity"], identity)
        answer["packet"]["source_identity"]["bmopftools_revision"] = "0" * 40
        self.assertTrue(any("source/pair identity" in error for error in validate_context_packet(service.index, answer["packet"])))
        self.assertEqual(service.health()["source_identity"], identity)


if __name__ == "__main__":
    unittest.main()
