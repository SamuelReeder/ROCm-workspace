---
description: List and manage git worktrees across repositories discovered in repos/
argument-hint: [project] [add|remove] [branch]
allowed-tools: [Bash, Read, Write]
---

# Worktree Management

List, create, or remove workspace-local worktrees. Repository projects are the
immediate git directories under `repos/`; no registry file is used.

**Arguments:** $ARGUMENTS

## Layout

```text
repos/<project>/                         # canonical local clone
worktrees/<project>/<branch-suffix>/       # feature/debug worktree
```

The branch prefix is always `users/sareeder/` and is omitted from the
worktree directory name. Slashes in the remaining suffix become `--`.
For example, `users/sareeder/fix-layout` maps to
`worktrees/rocm-libraries/fix-layout`.

## Bootstrap Missing Repositories

Clone a repository into `repos/<project>/` manually. Then inspect discovered
repositories or create worktrees:

```bash
python3 scripts/bootstrap_repos.py
python3 scripts/bootstrap_repos.py --project <project>
```

Use `--dry-run` to inspect commands. Add `--fetch` to refresh selected clones,
`--no-fetch` to skip the fetch done for worktree creation, and `--submodules`
for recursive submodule initialization.

## Actions

### No Arguments — List All Workspace Worktrees

```bash
for repo in repos/*; do
  test -d "$repo/.git" || continue
  git -C "$repo" worktree list --verbose
done
```

### `<project>` — List Project Worktrees

```bash
git -C repos/<project> worktree list --verbose
```

### `<project> add <branch>` — Create New Worktree

The destination is the suffix after `users/sareeder/`; do not invent a
separate name:

```bash
python3 scripts/bootstrap_repos.py \
  --project <project> \
  --worktree <project> <branch>
```

For `users/sareeder/fix-layout`, this creates
`worktrees/<project>/fix-layout`.

### `<project> remove <branch>` — Remove Worktree

Derive the destination using the same branch mapping, inspect changes, then
remove through the source clone:

```bash
name=$(python3 -c 'from scripts.bootstrap_repos import branch_to_worktree_name; import sys; print(branch_to_worktree_name(sys.argv[1]))' '<branch>')
git -C worktrees/<project>/$name status --short
git -C repos/<project> worktree remove worktrees/<project>/$name
```

Use `--force` only after confirming no work should be preserved.
