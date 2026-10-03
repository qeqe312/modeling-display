import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import deploy


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="geo3d-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.repo, self.target = self.base / "repo", self.base / "target"
        self.repo.mkdir()

    def install(self, files, prune=False):
        plan = deploy.plan_deployment(self.repo, self.target, files, prune)
        deploy.apply_plan(plan)
        return plan

    def test_extra_files_preserved_and_stale_requires_opt_in(self):
        self.install({"SKILL.md": b"old", "old.md": b"managed"})
        (self.target / "notes.txt").write_bytes(b"user")
        self.install({"SKILL.md": b"new"})
        self.assertTrue((self.target / "old.md").exists())
        self.install({"SKILL.md": b"new"}, prune=True)
        self.assertFalse((self.target / "old.md").exists())
        self.assertEqual((self.target / "notes.txt").read_bytes(), b"user")
        backups = list((self.target / ".modeling-display-backups").rglob("old.md"))
        self.assertEqual(backups[0].read_bytes(), b"managed")

    def test_modified_stale_file_blocks_prune_before_writes(self):
        self.install({"SKILL.md": b"v1", "old.md": b"original"})
        (self.target / "old.md").write_bytes(b"user edit")
        with self.assertRaises(ValueError):
            self.install({"SKILL.md": b"v2"}, prune=True)
        self.assertEqual((self.target / "SKILL.md").read_bytes(), b"v1")

    def test_manifest_cannot_delete_git_or_escape_root(self):
        self.target.mkdir()
        for rel in ("../outside.txt", ".git", "nested/.git/config", "nested/.GIT/config", "C:/file", "nested\\file"):
            (self.target / deploy.MANIFEST).write_text(json.dumps({"schema": 1, "files": {rel: "0" * 64}}))
            with self.assertRaises(ValueError):
                deploy.plan_deployment(self.repo, self.target, {}, True)

    def test_invalid_manifest_schema_refused(self):
        self.target.mkdir()
        for value in ([], {'schema': 2, 'files': {}}, {'schema': 1, 'files': {'x': 'bad'}}):
            (self.target / deploy.MANIFEST).write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                deploy.plan_deployment(self.repo, self.target, {'SKILL.md': b'new'})
        self.assertFalse((self.target / 'SKILL.md').exists())

    def test_source_destination_overlap_and_git_checkout_rejected(self):
        for target in (self.repo, self.repo / "child", self.base):
            with self.assertRaises(ValueError):
                deploy.validate_root(target, self.repo)
        self.target.mkdir()
        (self.target / ".git").write_text("gitdir: example")
        with self.assertRaises(ValueError):
            deploy.validate_root(self.target, self.repo)

    def test_symbolic_link_rejected(self):
        outside = self.base / "outside"
        outside.mkdir()
        try:
            self.target.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("OS does not permit symlink creation")
        with self.assertRaises(ValueError):
            deploy.plan_deployment(self.repo, self.target, {"SKILL.md": b"new"})
        self.assertFalse((outside / "SKILL.md").exists())

    def test_backup_and_binary_identity(self):
        self.install({"data.bin": b"\x00\xff\r\n"})
        self.install({"data.bin": b"\x01\xff\r\n"})
        self.assertEqual((self.target / "data.bin").read_bytes(), b"\x01\xff\r\n")
        backup = next((self.target / ".modeling-display-backups").rglob("data.bin"))
        self.assertEqual(backup.read_bytes(), b"\x00\xff\r\n")
        plan = deploy.plan_deployment(self.repo, self.target, {"data.bin": b"\x01\xff\r\n"})
        self.assertFalse(plan[1] or plan[2] or plan[4])

    @unittest.skipUnless(os.name == 'nt', 'Windows junction regression')
    def test_windows_junction_rejected(self):
        outside = self.base / 'outside'
        outside.mkdir()
        environment = dict(os.environ, GEO3D_LINK=str(self.target), GEO3D_DEST=str(outside))
        subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                        'New-Item -ItemType Junction -Path $env:GEO3D_LINK -Target $env:GEO3D_DEST | Out-Null'],
                       env=environment, check=True, capture_output=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            with self.assertRaises(ValueError):
                deploy.plan_deployment(self.repo, self.target, {'SKILL.md': b'new'})
            self.assertFalse((outside / 'SKILL.md').exists())
        finally:
            # Remove only the junction itself, never recursively traverse its target.
            self.target.rmdir()

    def test_check_is_readonly_and_installs_license(self):
        home = self.base / "home"
        result = deploy.main(["--home", str(home), "--target", "codex", "--check"])
        self.assertEqual(result, 1)
        self.assertFalse(home.exists())
        self.assertEqual(deploy.main(["--home", str(home), "--target", "codex"]), 0)
        self.assertEqual(deploy.main(["--home", str(home), "--target", "codex", "--check"]), 0)
        self.assertTrue((home / ".codex/skills/modeling-display/LICENSE").exists())
        self.assertTrue((home / ".codex/skills/modeling-display/assets/vendor/THREE-LICENSE.txt").exists())

    def test_invalid_arguments_have_no_effect(self):
        for arguments in (["--target"], ["--target", "typo"], ["--unknown"]):
            with self.assertRaises(SystemExit) as error:
                deploy.main(arguments)
            self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
