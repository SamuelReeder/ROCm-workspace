---
description: Navigate to a ROCm project or worktree and load its context
argument-hint: <project> [worktree]
allowed-tools: [Read, Bash, Glob]
---

# Navigate to Project

Navigate to the specified ROCm project and load its CLAUDE.md context.

**Arguments:** $ARGUMENTS

## Project Registry

Read the project registry at `/home/AMD/sareeder/ROCm-workspace/.claude/registry/projects.json`

## Process

1. Parse project identifier from first argument
2. Parse optional worktree from second argument (default: "main" for TheRock, or root for others)
3. Resolve project alias to canonical name using the registry's `aliases` field
4. Determine target path:
   - If project has worktrees and worktree specified: use `worktrees[name].path`
   - Otherwise: use project's main `path`
5. Verify path exists with `ls <path>`
6. Read the target project's CLAUDE.md: `<path>/CLAUDE.md`
7. Get current git status:
   ```bash
   git -C <path> branch --show-current
   git -C <path> status --short | head -10
   ```
8. Report to user:
   - Project name and full path
   - Current branch
   - Worktree indicator if applicable
   - Build directory: `<path>/<buildDir>`
   - Venv path if applicable: `<path>/<venv>`
   - Summary of key CLAUDE.md instructions

## Alias Resolution Examples

| Input | Resolves To | Path |
|-------|-------------|------|
| therock | TheRock (main) | ~/TheRock |
| rock consumption | TheRock (consumption) | ~/therock-consumption |
| libs | rocm-libraries | ~/full/rocm-libraries |
| hipdnn | rocm-libraries | ~/full/rocm-libraries |
| bench | dnn-benchmarking | ~/dnn-benchmarking |
| mlse | mlse-tools-internal | ~/mlse-tools-internal |

## Context Setting

After navigation, all subsequent file operations and commands should target the resolved path. Use absolute paths in all operations.
