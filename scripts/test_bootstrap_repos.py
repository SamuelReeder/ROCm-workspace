#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
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
    def make_repo(self, root: Path, name: str = "rocm-libraries") -> Path:
        repo = root / "repos" / name
        repo.mkdir(parents=True)
        subprocess.run(["git", "init", str(repo)], check=True, stdout=subprocess.DEVNULL)
        return repo

    def test_discover_projects_uses_repository_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self.make_repo(root)
            (root / "repos" / "not-a-repo").mkdir()

            projects = bootstrap_repos.discover_projects(root / "repos")

        self.assertEqual(set(projects), {"rocm-libraries"})
        self.assertEqual(projects["rocm-libraries"].path, repo)

    def test_resolve_project_accepts_only_directory_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(Path(tmp))
            projects = bootstrap_repos.discover_projects(repo.parent)

        self.assertEqual(bootstrap_repos.resolve_project(projects, "rocm-libraries").path, repo)
        with self.assertRaises(bootstrap_repos.BootstrapError):
            bootstrap_repos.resolve_project(projects, "libs")

    def test_branch_name_uses_users_suffix(self) -> None:
        self.assertEqual(
            bootstrap_repos.branch_to_worktree_name("users/sareeder/feature-x"),
            "feature-x",
        )
        self.assertEqual(
            bootstrap_repos.branch_to_worktree_name("origin/users/sareeder/jira/fix-layout"),
            "jira--fix-layout",
        )
        self.assertEqual(
            bootstrap_repos.branch_to_worktree_name("refs/heads/users/sareeder/feature_x"),
            "feature_x",
        )
        with self.assertRaises(bootstrap_repos.BootstrapError):
            bootstrap_repos.branch_to_worktree_name("feature-x")

    def test_worktree_path_is_derived_from_branch_suffix(self) -> None:
        project = bootstrap_repos.Project(key="rocm-libraries", path=Path("/tmp/repos/rocm-libraries"))
        self.assertEqual(
            bootstrap_repos.worktree_path(Path("/tmp/worktrees"), project, "users/sareeder/jira/fix"),
            Path("/tmp/worktrees/rocm-libraries/jira--fix"),
        )


    def test_creates_worktree_at_branch_derived_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self.make_repo(root)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "--allow-empty", "-m", "initial"], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "-C", str(repo), "branch", "users/sareeder/feature-x"], check=True)

            rc = bootstrap_repos.main([
                "--repos-dir", str(root / "repos"),
                "--worktrees-dir", str(root / "worktrees"),
                "--project", "rocm-libraries",
                "--worktree", "rocm-libraries", "users/sareeder/feature-x",
                "--no-fetch",
            ])
            destination = root / "worktrees" / "rocm-libraries" / "feature-x"

            self.assertEqual(rc, 0)
            self.assertTrue((destination / ".git").exists())
            self.assertEqual(
                subprocess.check_output(["git", "-C", str(destination), "branch", "--show-current"], text=True).strip(),
                "users/sareeder/feature-x",
            )

    def test_dry_run_discovers_repo_and_creates_branch_derived_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            stdout = StringIO()
            with redirect_stdout(stdout):
                rc = bootstrap_repos.main([
                    "--repos-dir", str(root / "repos"),
                    "--worktrees-dir", str(root / "worktrees"),
                    "--project", "rocm-libraries",
                    "--worktree", "rocm-libraries", "users/sareeder/feature-x",
                    "--no-fetch",
                    "--dry-run",
                ])
            output = stdout.getvalue()

        self.assertEqual(rc, 0)
        self.assertNotIn("Registry", output)
        self.assertIn("worktree add", output)
        self.assertIn("worktrees/rocm-libraries/feature-x", output)


if __name__ == "__main__":
    unittest.main()
