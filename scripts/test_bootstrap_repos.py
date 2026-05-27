#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

SCRIPT = Path(__file__).with_name("bootstrap_repos.py")
SPEC = importlib.util.spec_from_file_location("bootstrap_repos", SCRIPT)
assert SPEC and SPEC.loader
bootstrap_repos = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bootstrap_repos
SPEC.loader.exec_module(bootstrap_repos)


class BootstrapReposTest(unittest.TestCase):
    def write_registry(self, root: Path) -> Path:
        registry = root / ".claude" / "registry" / "projects.json"
        registry.parent.mkdir(parents=True)
        registry.write_text(json.dumps({
            "projects": {
                "rocm-libraries": {
                    "name": "rocm-libraries",
                    "remote": "git@github.com:ROCm/rocm-libraries.git",
                    "aliases": ["libs", "rocmlibs"],
                },
                "therock": {
                    "name": "TheRock",
                    "remote": "git@github.com:ROCm/TheRock.git",
                    "aliases": ["rock"],
                },
                "missing-remote": {
                    "name": "Missing Remote"
                },
            }
        }))
        return registry

    def test_load_projects_uses_only_entries_with_remotes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            registry = self.write_registry(Path(tmp))
            projects = bootstrap_repos.load_projects(registry)

        self.assertEqual(set(projects), {"rocm-libraries", "therock"})
        self.assertEqual(projects["rocm-libraries"].remote, "git@github.com:ROCm/rocm-libraries.git")

    def test_resolve_project_accepts_key_name_and_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            registry = self.write_registry(Path(tmp))
            projects = bootstrap_repos.load_projects(registry)

        self.assertEqual(bootstrap_repos.resolve_project(projects, "rocm-libraries").key, "rocm-libraries")
        self.assertEqual(bootstrap_repos.resolve_project(projects, "TheRock").key, "therock")
        self.assertEqual(bootstrap_repos.resolve_project(projects, "libs").key, "rocm-libraries")

    def test_worktree_path_rejects_path_traversal(self) -> None:
        project = bootstrap_repos.Project(
            key="rocm-libraries",
            name="rocm-libraries",
            remote="git@github.com:ROCm/rocm-libraries.git",
            path=None,
            aliases=(),
        )
        base = Path("/tmp/worktrees")
        self.assertEqual(
            bootstrap_repos.worktree_path(base, project, "feature_1.2-3"),
            base / "rocm-libraries" / "feature_1.2-3",
        )
        with self.assertRaises(bootstrap_repos.BootstrapError):
            bootstrap_repos.worktree_path(base, project, "../escape")

    def test_dry_run_prints_clone_and_worktree_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = self.write_registry(root)
            stdout = StringIO()
            with redirect_stdout(stdout):
                rc = bootstrap_repos.main([
                    "--registry", str(registry),
                    "--repos-dir", str(root / "repos"),
                    "--worktrees-dir", str(root / "worktrees"),
                    "--project", "libs",
                    "--worktree", "libs", "feature-x", "origin/develop",
                    "--dry-run",
                ])
            output = stdout.getvalue()

        self.assertEqual(rc, 0)
        self.assertIn("git clone git@github.com:ROCm/rocm-libraries.git", output)
        self.assertIn("worktree add", output)
        self.assertIn("worktrees/rocm-libraries/feature-x", output)


if __name__ == "__main__":
    unittest.main()
