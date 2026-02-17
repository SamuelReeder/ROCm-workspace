# ROCm Workspace Hub

Centralized dispatch workspace for ROCm development projects.

## Projects

| Project | Path | Type |
|---------|------|------|
| TheRock | ~/TheRock | CMake superbuild |
| rocm-libraries | ~/full/rocm-libraries | CMake superbuild |
| mlse-tools | ~/mlse-tools-internal | Python scripts |
| dnn-benchmarking | ~/tmp/dnn-benchmarking | Python package |

## TheRock Worktrees

| Name | Path | Branch |
|------|------|--------|
| main | ~/TheRock | users/sareeder/install-latest-rocm |
| consumption | ~/therock-consumption | users/sareeder/hipdnn-consumption-tests |
| miopen-plugin | ~/therock-miopen-plugin-move | users/sareeder/miopen-plugin-move |

## rocm-libraries Worktrees

| Name | Path | Branch |
|------|------|--------|
| main | ~/full/rocm-libraries | users/sareeder/detail-migration |

**To create a new rocm-libraries worktree for parallel work:**
```bash
cd ~/full/rocm-libraries
git worktree add ~/rocmlibs-<name> <branch>
# Example: git worktree add ~/rocmlibs-feature users/sareeder/new-feature
```

Each worktree is fully isolated with its own:
- `projects/hipdnn/build/` - hipDNN build artifacts
- `dnn-providers/*/build/` - Provider build artifacts
- Working directory state

## Navigation

- `/goto <project> [worktree]` - Navigate to project and load its context
- `/status` - Show git status across all projects
- `/worktrees [project]` - List/manage worktrees
- `/task <list|ready|create|show|close|update|q>` - Issue tracker (beads_rust)
- `/wip [description]` - Quick WIP commit in current project
- `/prep-pr [project] [base]` - Prepare PR with commit analysis

## Project Detection

Mention project names, library names (hipDNN, MIOpen, rocBLAS), or worktree names in your prompt - the workspace will automatically detect and use the correct project context.

## New Branch / Worktree Setup

When starting work on a new branch, use the `worktree-setup` agent to create a worktree. It validates the project/branch, creates the worktree with the correct naming convention, sets up the environment, and reports the result back.

## Key Rules

1. **Worktree Isolation**: Each worktree has its own build/ and .venv - never cross-contaminate
2. **Absolute Paths**: Always use full paths to the correct worktree
3. **Project CLAUDE.md**: Each project has detailed instructions in its own CLAUDE.md

## Issue Tracking (beads_rust)

Tasks tracked with `br` in `.beads/` (local-only, not committed to git).
- `br list` or `/task list` — see all tasks
- `br ready` or `/task ready` — actionable tasks
- Labels map to projects (`therock`, `rocm-libraries`, etc.) and worktrees (`wt:main`, `wt:consumption`)
