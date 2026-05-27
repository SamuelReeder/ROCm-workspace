---
description: List and manage git worktrees across ROCm projects
argument-hint: [project] [add|remove] [name] [branch]
allowed-tools: [Bash, Read, Write]
---

# Worktree Management

List, create, or remove workspace-local ROCm project worktrees.

**Arguments:** $ARGUMENTS

## Layout

Use the workspace-local bootstrap layout for new machines and new worktrees:

```text
repos/<project>/                  # canonical clone for the project
worktrees/<project>/<name>/       # feature/debug worktrees
```

Both directories are gitignored. The project registry (`.claude/registry/projects.json`) remains the source of truth for project names and remotes.

## Bootstrap Missing Repositories

Before creating worktrees, ensure the source clone exists:

```bash
python3 scripts/bootstrap_repos.py --project <project>
```

To clone every registry project:

```bash
python3 scripts/bootstrap_repos.py
```

Use `--dry-run` first when you want to inspect the git commands without changing disk. The bootstrap script clones shallow default-branch repositories and reuses an existing registry checkout as a Git object reference when one is present; add `--full-history` for complete history and `--submodules` for recursive submodule initialization.

## Actions

### No Arguments - List All Workspace Worktrees

Show worktrees for local workspace clones that exist:

```bash
for repo in repos/*; do
  test -d "$repo/.git" || continue
  git -C "$repo" worktree list --verbose
done
```

### `<project>` - List Project Worktrees

Show worktrees for one project:

```bash
git -C repos/<project> worktree list --verbose
```

If `repos/<project>` does not exist yet, run:

```bash
python3 scripts/bootstrap_repos.py --project <project>
```

### `<project> add <name> <branch>` - Create New Worktree

Create a workspace-local worktree under `worktrees/<project>/<name>`:

```bash
python3 scripts/bootstrap_repos.py \
  --project <project> \
  --worktree <project> <name> <branch>
```

The bootstrap script fetches before creating requested worktrees unless `--no-fetch` is passed. Worktree names must be simple path components: letters, numbers, dots, underscores, and dashes only.

### `<project> remove <name>` - Remove Worktree

Before removing, inspect for uncommitted changes:

```bash
git -C worktrees/<project>/<name> status --short
```

Then remove through the source clone:

```bash
git -C repos/<project> worktree remove worktrees/<project>/<name>
```

Use `--force` only after confirming no work should be preserved.

## Registry Updates

Do not update `.claude/registry/projects.json` for temporary workspace-local worktrees. Add registry entries only for long-lived, shared worktrees that other agents should discover by name.
