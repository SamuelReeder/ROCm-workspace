---
description: List and manage git worktrees across ROCm projects
argument-hint: [project] [add|remove] [name] [branch]
allowed-tools: [Bash, Read, Write]
---

# Worktree Management

List, create, or remove worktrees for ROCm projects.

**Arguments:** $ARGUMENTS

## Actions

### No Arguments - List All Worktrees
Show all worktrees across all projects:
```bash
git -C /home/AMD/sareeder/TheRock worktree list
git -C /home/AMD/sareeder/full/rocm-libraries worktree list
git -C /home/AMD/sareeder/mlse-tools-internal worktree list
git -C /home/AMD/sareeder/dnn-benchmarking worktree list
```

### `<project>` - List Project Worktrees
Show worktrees for specific project:
```bash
git -C <project-path> worktree list --verbose
```

### `<project> add <name> <branch>` - Create New Worktree

1. Resolve project to main repository path
2. Determine worktree path using naming pattern: `/home/AMD/sareeder/<project>-<name>`
3. Create worktree:
   ```bash
   git -C <main-repo> worktree add /home/AMD/sareeder/<project>-<name> <branch>
   ```
4. **Auto-setup for Python projects** (if project has venv):
   ```bash
   cd /home/AMD/sareeder/<project>-<name>
   python3 -m venv .venv
   source .venv/bin/activate && pip install -r requirements.txt
   ```
5. **Auto-setup for CMake projects**:
   ```bash
   # Build directory will be created on first build
   # Just verify the worktree is ready
   ```
6. Update project registry to include new worktree
7. Copy CLAUDE.md from main repo if it exists

### `<project> remove <name>` - Remove Worktree

1. Resolve worktree path: `/home/AMD/sareeder/<project>-<name>`
2. Confirm removal (warn about uncommitted changes)
3. Remove worktree:
   ```bash
   git -C <main-repo> worktree remove /home/AMD/sareeder/<project>-<name>
   ```
4. Update project registry to remove worktree entry

## Naming Convention

Worktrees are created at: `/home/AMD/sareeder/{project}-{worktree-name}`

Examples:
- `therock-ck-fix` for TheRock worktree named "ck-fix"
- `rocm-libraries-feature-x` for rocm-libraries worktree

## Registry Update

After add/remove, update `/home/AMD/sareeder/ROCm-workspace/.claude/registry/projects.json`:

```json
"worktrees": {
  "new-worktree": {
    "path": "/home/AMD/sareeder/therock-new-worktree",
    "branch": "users/sareeder/new-branch"
  }
}
```
