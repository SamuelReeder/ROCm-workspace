#!/usr/bin/env python3
"""Bootstrap ROCm workspace repositories and local worktree roots.

The workspace registry remains the source of truth for project names and remotes.
This script clones those remotes into ignored workspace-local directories:

  repos/<project-key>/
  worktrees/<project-key>/<worktree-name>/

It intentionally does not rewrite registry paths. Existing machines may still use
pre-existing absolute checkouts; this is a portable bootstrap path for new hosts.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = WORKSPACE_ROOT / ".claude" / "registry" / "projects.json"
DEFAULT_REPOS_DIR = WORKSPACE_ROOT / "repos"
DEFAULT_WORKTREES_DIR = WORKSPACE_ROOT / "worktrees"
DEFAULT_CLONE_DEPTH = "1"
SAFE_WORKTREE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True)
class Project:
    key: str
    name: str
    remote: str
    path: Path | None
    aliases: tuple[str, ...]


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


def load_projects(registry_path: Path) -> dict[str, Project]:
    try:
        data = json.loads(registry_path.read_text())
    except FileNotFoundError as exc:
        raise BootstrapError(f"Registry not found: {registry_path}") from exc
    except json.JSONDecodeError as exc:
        raise BootstrapError(f"Invalid registry JSON in {registry_path}: {exc}") from exc

    raw_projects = data.get("projects")
    if not isinstance(raw_projects, dict):
        raise BootstrapError(f"Registry {registry_path} does not contain a projects object")

    projects: dict[str, Project] = {}
    for key, raw in raw_projects.items():
        if not isinstance(raw, dict):
            continue
        remote = str(raw.get("remote") or "").strip()
        if not remote:
            continue
        aliases = tuple(str(alias).lower() for alias in raw.get("aliases", []) if str(alias).strip())
        source_path = Path(str(raw.get("path")).replace("~", str(Path.home()), 1)).expanduser() if raw.get("path") else None
        projects[key] = Project(
            key=key,
            name=str(raw.get("name") or key),
            remote=remote,
            path=source_path,
            aliases=aliases,
        )
    if not projects:
        raise BootstrapError(f"Registry {registry_path} contains no projects with remotes")
    return projects


def resolve_project(projects: Mapping[str, Project], selector: str) -> Project:
    needle = selector.strip().lower()
    for project in projects.values():
        if needle in {project.key.lower(), project.name.lower(), *project.aliases}:
            return project
    known = ", ".join(sorted(projects))
    raise BootstrapError(f"Unknown project '{selector}'. Known projects: {known}")


def select_projects(projects: Mapping[str, Project], selectors: Iterable[str]) -> list[Project]:
    selected: dict[str, Project] = {}
    for selector in selectors:
        project = resolve_project(projects, selector)
        selected[project.key] = project
    return list(selected.values())


def repo_path(repos_dir: Path, project: Project) -> Path:
    return repos_dir / project.key


def worktree_path(worktrees_dir: Path, project: Project, name: str) -> Path:
    if not SAFE_WORKTREE_NAME.fullmatch(name):
        raise BootstrapError(
            f"Invalid worktree name '{name}'. Use only letters, numbers, dots, underscores, and dashes; do not include slashes."
        )
    return worktrees_dir / project.key / name


def clone_command(project: Project, destination: Path, *, full_history: bool) -> list[str]:
    command = ["git", "clone"]
    if not full_history:
        command.extend(["--depth", DEFAULT_CLONE_DEPTH])
    if project.path and project.path.resolve() != destination.resolve() and project.path.exists():
        command.extend(["--reference-if-able", str(project.path)])
    command.extend([project.remote, str(destination)])
    return command

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


def ensure_project_clone(
    project: Project,
    repos_dir: Path,
    *,
    dry_run: bool,
    fetch: bool,
    submodules: bool,
    full_history: bool,
) -> Path:
    destination = repo_path(repos_dir, project)
    ensure_dir(repos_dir, dry_run=dry_run)

    if not destination.exists():
        run(clone_command(project, destination, full_history=full_history), dry_run=dry_run)
        if submodules:
            run(["git", "-C", str(destination), "submodule", "update", "--init", "--recursive"], dry_run=dry_run)
        return destination

    if not is_git_worktree(destination, dry_run=dry_run):
        raise BootstrapError(f"{destination} exists but is not a git checkout")

    if not dry_run:
        origin = run(["git", "-C", str(destination), "remote", "get-url", "origin"], dry_run=False, capture=True)
        if origin != project.remote:
            raise BootstrapError(
                f"{destination} origin is {origin!r}, expected {project.remote!r}. Move it aside or fix the remote before bootstrapping."
            )

    if fetch:
        run(["git", "-C", str(destination), "fetch", "--all", "--prune", "--tags"], dry_run=dry_run)
        if submodules:
            run(["git", "-C", str(destination), "submodule", "update", "--init", "--recursive"], dry_run=dry_run)
    else:
        print(f"= {destination} already exists; skipping fetch")
    return destination


def ensure_worktree(
    project: Project,
    name: str,
    branch: str,
    repos_dir: Path,
    worktrees_dir: Path,
    *,
    dry_run: bool,
    fetch: bool,
    main_repo: Path | None = None,
) -> Path:
    if main_repo is None:
        main_repo = ensure_project_clone(project, repos_dir, dry_run=dry_run, fetch=fetch, submodules=False, full_history=False)
    destination = worktree_path(worktrees_dir, project, name)
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
        description="Clone registry projects into workspace/repos and create workspace-local worktrees."
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        help=f"project registry JSON (default: {DEFAULT_REGISTRY})",
    )
    parser.add_argument(
        "--repos-dir",
        type=Path,
        default=DEFAULT_REPOS_DIR,
        help=f"clone destination root (default: {DEFAULT_REPOS_DIR})",
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
        help="project key/name/alias to clone; repeatable. Defaults to all registry projects unless only --worktree is used.",
    )
    parser.add_argument(
        "--worktree",
        nargs=3,
        action="append",
        metavar=("PROJECT", "NAME", "BRANCH"),
        default=[],
        help="create worktrees/<project>/<name> from BRANCH; repeatable",
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="fetch existing clones. Worktree creation fetches unless --no-fetch is set.",
    )
    parser.add_argument(
        "--submodules",
        action="store_true",
        help="after cloning/fetching a repo, initialize and update its submodules recursively",
    )
    parser.add_argument(
        "--full-history",
        action="store_true",
        help="clone complete history instead of the default shallow all-branch clone",
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="do not fetch before creating requested worktrees",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the git commands without creating directories or cloning",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.fetch and args.no_fetch:
        raise BootstrapError("Use either --fetch or --no-fetch, not both")

    registry = args.registry.resolve()
    repos_dir = args.repos_dir.resolve()
    worktrees_dir = args.worktrees_dir.resolve()
    projects = load_projects(registry)

    requested = list(args.project)
    for project_name, _name, _branch in args.worktree:
        requested.append(project_name)

    clone_targets = select_projects(projects, requested) if requested else list(projects.values())
    fetch_existing_clones = bool(args.fetch)
    worktree_fetch = not args.no_fetch

    print(f"Workspace: {WORKSPACE_ROOT}")
    print(f"Registry:  {registry}")
    print(f"Repos:     {repos_dir}")
    print(f"Worktrees: {worktrees_dir}")

    cloned: list[Path] = []
    prepared_repos: dict[str, Path] = {}
    for project in clone_targets:
        cloned_path = ensure_project_clone(project, repos_dir, dry_run=args.dry_run, fetch=fetch_existing_clones, submodules=args.submodules, full_history=args.full_history)
        cloned.append(cloned_path)
        prepared_repos[project.key] = cloned_path

    created_worktrees: list[Path] = []
    for project_name, name, branch in args.worktree:
        project = resolve_project(projects, project_name)
        created_worktrees.append(
            ensure_worktree(
                project,
                name,
                branch,
                repos_dir,
                worktrees_dir,
                dry_run=args.dry_run,
                fetch=worktree_fetch,
                main_repo=prepared_repos.get(project.key),
            )
        )

    print("\nBootstrap summary")
    print(f"  clone targets: {len(cloned)}")
    for path in cloned:
        print(f"    {path}")
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
