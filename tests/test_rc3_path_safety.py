"""Filesystem regressions use only temporary synthetic files, never real secrets."""
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from rc2_support import ROOT
import bootstrap
import keychain_store


class PathSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="bwb-path-safety-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.raw = b"SYNTHETIC-DOWNLOAD"
        self.spec = {"url": "https://example.invalid/fixture",
                     "sha256": hashlib.sha256(self.raw).hexdigest()}

    def credential_config(self, path):
        return {"credential": {"provider": "env_file", "path": str(path)},
                "allow_legacy_env_file": True}

    def credential_file(self):
        path = self.root / "synthetic.env"
        path.write_text("CONTROL_PLANE_API_KEY=fixture-only\n")
        path.chmod(0o600)
        return path

    def test_partial_hardlink_refused_without_touching_victim(self):
        target = self.root / "archive"
        victim = self.root / "unrelated"
        victim.write_bytes(b"ORIGINAL")
        os.link(victim, target.with_suffix(".partial"))
        with patch.object(bootstrap.urllib.request, "urlopen") as request:
            with self.assertRaises(ValueError):
                bootstrap.download(self.spec, target)
            request.assert_not_called()
        self.assertEqual(victim.read_bytes(), b"ORIGINAL")
        self.assertFalse(target.exists())

    def test_legacy_regular_partial_is_preserved(self):
        target = self.root / "archive"
        partial = target.with_suffix(".partial")
        partial.write_bytes(b"OLD-PARTIAL")
        with patch.object(bootstrap.urllib.request, "urlopen", return_value=io.BytesIO(self.raw)):
            bootstrap.download(self.spec, target)
        self.assertEqual(partial.read_bytes(), b"OLD-PARTIAL")
        self.assertEqual(target.read_bytes(), self.raw)
        self.assertEqual(target.stat().st_nlink, 1)

    def test_destination_created_during_download_is_not_overwritten(self):
        target = self.root / "archive"
        def response(*args, **kwargs):
            target.write_bytes(b"NEW-USER-DATA")
            return io.BytesIO(self.raw)
        with patch.object(bootstrap.urllib.request, "urlopen", side_effect=response):
            with self.assertRaises(RuntimeError):
                bootstrap.download(self.spec, target)
        self.assertEqual(target.read_bytes(), b"NEW-USER-DATA")
        self.assertEqual(list(self.root.glob(".archive-*")), [])

    def test_cached_hardlink_refused(self):
        victim = self.root / "unrelated"
        victim.write_bytes(self.raw)
        target = self.root / "archive"
        os.link(victim, target)
        with patch.object(bootstrap.urllib.request, "urlopen") as request:
            with self.assertRaises(ValueError):
                bootstrap.download(self.spec, target)
            request.assert_not_called()
        self.assertEqual(victim.read_bytes(), self.raw)

    def test_network_failure_cleans_only_owned_temporary(self):
        target = self.root / "archive"
        with patch.object(bootstrap.urllib.request, "urlopen", side_effect=OSError("synthetic failure")):
            with self.assertRaises(OSError):
                bootstrap.download(self.spec, target)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_runtime_symlink_fails_before_mutating_either_tree(self):
        outside = self.root / "unrelated"
        outside.mkdir(mode=0o755)
        runtime = self.root / "runtime"
        runtime.symlink_to(outside, target_is_directory=True)
        state = self.root / "state"
        with patch.object(bootstrap, "RUNTIME", runtime), patch.object(bootstrap, "STATE", state), \
                patch.object(bootstrap.platform, "system", return_value="Darwin"), \
                patch.object(bootstrap, "download") as download:
            with self.assertRaises(ValueError):
                bootstrap._prepare_runtime()
            download.assert_not_called()
        self.assertEqual(outside.stat().st_mode & 0o777, 0o755)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse(state.exists())

    def test_state_parent_symlink_fails_before_creating_runtime(self):
        outside = self.root / "unrelated"
        outside.mkdir()
        link = self.root / "alias"
        link.symlink_to(outside, target_is_directory=True)
        runtime = self.root / "runtime"
        with patch.object(bootstrap, "RUNTIME", runtime), patch.object(bootstrap, "STATE", link / "state"), \
                patch.object(bootstrap.platform, "system", return_value="Darwin"):
            with self.assertRaises(ValueError):
                bootstrap._prepare_runtime()
        self.assertFalse(runtime.exists())
        self.assertEqual(list(outside.iterdir()), [])

    def test_existing_runtime_permissions_not_changed(self):
        runtime = self.root / "runtime"
        runtime.mkdir(mode=0o755)
        with patch.object(bootstrap, "RUNTIME", runtime), patch.object(bootstrap, "STATE", self.root / "state"), \
                patch.object(bootstrap.platform, "system", return_value="Darwin"), \
                patch.object(bootstrap.platform, "machine", return_value="arm64"), \
                patch.object(bootstrap, "download", side_effect=RuntimeError("stop before network")):
            with self.assertRaises(RuntimeError):
                bootstrap._prepare_runtime()
        self.assertEqual(runtime.stat().st_mode & 0o777, 0o755)

    def test_nested_runtime_symlink_fails_before_other_writes(self):
        runtime = self.root / "runtime"
        runtime.mkdir()
        outside = self.root / "unrelated"
        outside.mkdir()
        (runtime / "downloads").symlink_to(outside, target_is_directory=True)
        state = self.root / "state"
        with patch.object(bootstrap, "RUNTIME", runtime), patch.object(bootstrap, "STATE", state), \
                patch.object(bootstrap.platform, "system", return_value="Darwin"):
            with self.assertRaises(ValueError):
                bootstrap._prepare_runtime()
        self.assertFalse(state.exists())
        self.assertEqual(list(outside.iterdir()), [])

    def test_credential_parent_symlink_refused(self):
        path = self.credential_file()
        alias = self.root / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            keychain_store.load_credential(self.credential_config(alias / path.name))

    def test_credential_hardlink_refused(self):
        path = self.credential_file()
        alias = self.root / "alias"
        os.link(path, alias)
        with self.assertRaises(RuntimeError):
            keychain_store.load_credential(self.credential_config(alias))
        self.assertIn("fixture-only", path.read_text())

    def test_credential_fifo_refused_without_blocking(self):
        path = self.root / "fifo"
        os.mkfifo(path, 0o600)
        with self.assertRaises(RuntimeError):
            keychain_store.load_credential(self.credential_config(path))

    def test_private_regular_credential_still_supported(self):
        path = self.credential_file()
        self.assertEqual(keychain_store.load_credential(self.credential_config(path)), "fixture-only")

    def test_credential_size_limit(self):
        path = self.credential_file()
        path.write_text("X" * 65537)
        with self.assertRaises(RuntimeError) as result:
            keychain_store.load_credential(self.credential_config(path))
        self.assertNotIn("XXXXX", str(result.exception))

    def test_component_receipt_does_not_claim_all_dependencies_hashed(self):
        wheel = self.root / "fixture.whl"
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr("blender_mcp/bundled/addon.py", "# synthetic fixture\n")
        runtime, state = self.root / "runtime", self.root / "state"
        with patch.object(bootstrap, "RUNTIME", runtime), patch.object(bootstrap, "STATE", state), \
                patch.object(bootstrap.platform, "system", return_value="Darwin"), \
                patch.object(bootstrap.platform, "machine", return_value="arm64"), \
                patch.object(bootstrap, "download", return_value=wheel), \
                patch.object(bootstrap, "extract_file"), patch.object(bootstrap, "run"):
            self.assertTrue(bootstrap._prepare_runtime()["ok"])
        receipt = json.loads((state / "components.json").read_text())
        self.assertEqual(receipt["hash_verification"], "PRIMARY_ARTIFACTS_PASS")
        self.assertFalse(receipt["python_transitive_hashes_verified"])
        self.assertEqual(len(receipt["hash_verification_scope"]), 3)
