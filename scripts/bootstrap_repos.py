#!/usr/bin/env python3
"""Manage workspace-local repositories and branch-derived git worktrees.

Repositories are discovered from immediate directories under ``repos/``.  The
repository directory name is the project key; no workspace registry is needed.
Worktrees are created under ``worktrees/<project>/<branch-suffix>/`` using the
suffix after the required ``users/sareeder/`` branch prefix.
"""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPOS_DIR = WORKSPACE_ROOT / "repos"
DEFAULT_WORKTREES_DIR = WORKSPACE_ROOT / "worktrees"
SAFE_WORKTREE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
BRANCH_PREFIX = "users/sareeder/"


@dataclass(frozen=True)
class Project:
    """A repository discovered under the workspace repos directory."""

    key: str
    path: Path


class BootstrapError(RuntimeError):
    """A user-correctable bootstrap failure."""


class CommandError(BootstrapError):
    def __init__(self, command: Sequence[str], returncode: int, stdout: str, stderr: str) -> None:
        rendered = render_command(command)
        detail = stderr.strip() or stdout.strip() or f"exit status {returncode}"
        super().__init__(f"Command failed ({returncode}): {rendered}\n{detail}")
        self.command = tuple(command)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def render_command(command: Sequence[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in command)


def run(command: Sequence[str], *, dry_run: bool, capture: bool = False) -> str:
    print("+ " + render_command(command))
    if dry_run:
        return ""
    if capture:
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        result = subprocess.run(command, text=True)
    if result.returncode != 0:
        raise CommandError(
            command,
            result.returncode,
            result.stdout or "",
            result.stderr or "",
        )
    return (result.stdout or "").strip() if capture else ""


def ensure_dir(path: Path, *, dry_run: bool) -> None:
    if dry_run:
        print("+ mkdir -p " + shlex.quote(str(path)))
        return
    path.mkdir(parents=True, exist_ok=True)


def is_git_worktree(path: Path, *, dry_run: bool) -> bool:
    if dry_run:
        return path.exists()
    if not path.exists():
        return False
    try:
        top_level = run(["git", "-C", str(path), "rev-parse", "--show-toplevel"], dry_run=False, capture=True)
    except CommandError:
        return False
    try:
        return Path(top_level).resolve() == path.resolve()
    except OSError:
        return False


def discover_projects(repos_dir: Path, *, dry_run: bool = False) -> dict[str, Project]:
    """Discover immediate git repository directories under ``repos_dir``."""
    if not repos_dir.exists():
        return {}
    projects: dict[str, Project] = {}
    for candidate in sorted(repos_dir.iterdir(), key=lambda item: item.name.lower()):
        if candidate.is_dir() and is_git_worktree(candidate, dry_run=dry_run):
            projects[candidate.name] = Project(key=candidate.name, path=candidate)
    return projects


def resolve_project(projects: Mapping[str, Project], selector: str) -> Project:
    needle = selector.strip().lower()
    for project in projects.values():
        if needle == project.key.lower():
            return project
    known = ", ".join(sorted(projects)) or "none"
    raise BootstrapError(f"Unknown repository '{selector}'. Repositories under repos/: {known}")


def select_projects(projects: Mapping[str, Project], selectors: Iterable[str]) -> list[Project]:
    selected: dict[str, Project] = {}
    for selector in selectors:
        project = resolve_project(projects, selector)
        selected[project.key] = project
    return list(selected.values())


def branch_to_worktree_name(branch: str) -> str:
    """Return the canonical suffix directory name for a user branch.

    Workspace branches always use ``users/sareeder/``.  The prefix is omitted
    from the worktree directory; remaining path separators become ``--``.
    """
    value = branch.strip()
    for prefix in ("refs/heads/", "refs/remotes/"):
        if value.startswith(prefix):
            value = value[len(prefix) :]
            break
    if value.startswith("origin/"):
        value = value[len("origin/") :]
    if not value.startswith(BRANCH_PREFIX):
        raise BootstrapError(f"Branch must use the '{BRANCH_PREFIX}' prefix: {branch!r}")
    suffix = value[len(BRANCH_PREFIX) :]
    if not suffix:
        raise BootstrapError(f"Branch must include a name after '{BRANCH_PREFIX}'")
    name = suffix.replace("/", "--")
    name = re.sub(r"[^A-Za-z0-9._-]", "-", name)
    name = name.strip(".-")
    if not name:
        raise BootstrapError(f"Branch '{branch}' does not produce a valid worktree name")
    if not name[0].isalnum():
        name = "branch-" + name
    if not SAFE_WORKTREE_NAME.fullmatch(name):
        raise BootstrapError(f"Branch '{branch}' produces invalid worktree name '{name}'")
    return name




def worktree_path(worktrees_dir: Path, project: Project, branch: str) -> Path:
    return worktrees_dir / project.key / branch_to_worktree_name(branch)


def ensure_repo(project: Project, *, dry_run: bool) -> Path:
    if not is_git_worktree(project.path, dry_run=dry_run):
        raise BootstrapError(f"{project.path} is not a git checkout")
    return project.path


def ensure_worktree(
    project: Project,
    branch: str,
    worktrees_dir: Path,
    *,
    dry_run: bool,
    fetch: bool,
    main_repo: Path | None = None,
) -> Path:
    if main_repo is None:
        main_repo = ensure_repo(project, dry_run=dry_run)
    destination = worktree_path(worktrees_dir, project, branch)
    ensure_dir(destination.parent, dry_run=dry_run)

    if destination.exists():
        if is_git_worktree(destination, dry_run=dry_run):
            print(f"= {destination} already exists as a git worktree")
            return destination
        raise BootstrapError(f"{destination} exists but is not a git worktree")

    if fetch:
        run(["git", "-C", str(main_repo), "fetch", "--all", "--prune", "--tags"], dry_run=dry_run)
    run(["git", "-C", str(main_repo), "worktree", "add", str(destination), branch], dry_run=dry_run)
    return destination


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover repositories under repos/ and create branch-derived worktrees."
    )
    parser.add_argument(
        "--repos-dir",
        type=Path,
        default=DEFAULT_REPOS_DIR,
        help=f"repository directory (default: {DEFAULT_REPOS_DIR})",
    )
    parser.add_argument(
        "--worktrees-dir",
        type=Path,
        default=DEFAULT_WORKTREES_DIR,
        help=f"worktree destination root (default: {DEFAULT_WORKTREES_DIR})",
    )
    parser.add_argument(
        "--project",
        action="append",
        default=[],
        help="repository directory name to use; repeatable. Defaults to all repositories.",
    )
    parser.add_argument(
        "--worktree",
        nargs=2,
        action="append",
        metavar=("PROJECT", "BRANCH"),
        default=[],
        help="create a branch-derived worktree for PROJECT and BRANCH; repeatable",
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="fetch selected repositories before processing",
    )
    parser.add_argument(
        "--submodules",
        action="store_true",
        help="initialize and update selected repositories' submodules recursively",
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="do not fetch before creating requested worktrees",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print git commands without changing directories or worktrees",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.fetch and args.no_fetch:
        raise BootstrapError("Use either --fetch or --no-fetch, not both")

    repos_dir = args.repos_dir.resolve()
    worktrees_dir = args.worktrees_dir.resolve()
    projects = discover_projects(repos_dir, dry_run=args.dry_run)
    if not projects:
        raise BootstrapError(f"No git repositories found under {repos_dir}")

    requested = list(args.project)
    for project_name, _branch in args.worktree:
        requested.append(project_name)
    selected = select_projects(projects, requested) if requested else list(projects.values())
    selected_by_key = {project.key: project for project in selected}

    print(f"Workspace:  {WORKSPACE_ROOT}")
    print(f"Worktrees:  {worktrees_dir}")
    print("Repositories:")
    for project in selected:
        print(f"  {project.key}: {project.path}")

    for project in selected:
        if args.fetch:
            run(["git", "-C", str(project.path), "fetch", "--all", "--prune", "--tags"], dry_run=args.dry_run)
        if args.submodules:
            run(["git", "-C", str(project.path), "submodule", "update", "--init", "--recursive"], dry_run=args.dry_run)

    created_worktrees: list[Path] = []
    for project_name, branch in args.worktree:
        project = selected_by_key[resolve_project(projects, project_name).key]
        created_worktrees.append(
            ensure_worktree(
                project,
                branch,
                worktrees_dir,
                dry_run=args.dry_run,
                fetch=not args.no_fetch and not args.fetch,
                main_repo=project.path,
            )
        )

    print("\nBootstrap summary")
    print(f"  repositories: {len(selected)}")
    print(f"  requested worktrees: {len(created_worktrees)}")
    for path in created_worktrees:
        print(f"    {path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BootstrapError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
