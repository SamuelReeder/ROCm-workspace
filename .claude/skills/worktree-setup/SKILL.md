---
name: worktree-setup
description: Use this skill when entering a new worktree that lacks setup, creating a new worktree, or when a worktree is missing its .venv or build directory. Activates when detecting worktree paths without expected infrastructure.
version: 1.0.0
---

# Automatic Worktree Setup

Automatically set up worktrees with proper isolation when detected.

## Detection Triggers

1. Entering a worktree path that exists but lacks `.venv` (for Python projects)
2. Creating a new worktree via `/worktrees add`
3. User mentions a worktree that needs setup

## Setup Process

### For Python Projects (TheRock worktrees, dnn-benchmarking)

When detecting a worktree without `.venv`:

```bash
# Check if .venv exists
ls <worktree-path>/.venv 2>/dev/null || {
  echo "Setting up venv for worktree..."
  cd <worktree-path>
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  pip install -r requirements-dev.txt 2>/dev/null || true
}
```

### For CMake Projects

Build directory is created on first build, but verify prerequisites:

```bash
# Check for CMakeLists.txt
ls <worktree-path>/CMakeLists.txt || echo "Warning: No CMakeLists.txt found"

# Build directory will be created by cmake -B build
```

## Post-Setup Actions

1. **Update project registry** if this is a new worktree:
   - Add entry to `/home/AMD/sareeder/ROCm-workspace/.claude/registry/projects.json`

2. **Copy CLAUDE.md** from main repo if worktree doesn't have one:
   ```bash
   cp /home/AMD/sareeder/TheRock/CLAUDE.md /home/AMD/sareeder/therock-newworktree/CLAUDE.md
   ```

3. **Report setup status** to user:
   - Venv location
   - Python version
   - Installed packages count
   - Ready for development

## Worktree Naming Convention

New worktrees follow pattern: `/home/AMD/sareeder/{project}-{name}`

Examples:
- TheRock worktree "feature-x" → `/home/AMD/sareeder/therock-feature-x`
- rocm-libraries worktree "bugfix" → `/home/AMD/sareeder/rocm-libraries-bugfix`

## Requirements Files

| Project | Requirements |
|---------|--------------|
| TheRock | requirements.txt, requirements-test.txt |
| dnn-benchmarking | requirements.txt, requirements-dev.txt |

## Silent Operation

This skill operates automatically without prompting the user. Report results after completion, not before.
