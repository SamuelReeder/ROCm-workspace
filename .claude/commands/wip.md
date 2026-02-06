---
description: Quick WIP commit in the current project context
argument-hint: [description]
allowed-tools: [Bash, Read]
---

# WIP Commit

Create a quick work-in-progress commit in the current project.

**Arguments:** $ARGUMENTS

## Process

1. **Determine project path:**
   - If an in-progress task exists (run `source "$HOME/.cargo/env" && br list --json` and find tasks with `status: "in_progress"`), check labels for project/worktree and resolve via `/home/AMD/sareeder/ROCm-workspace/.claude/registry/projects.json`
   - Otherwise, infer from conversation context
   - If no project can be determined, ask the user

2. **Check for changes:**
   ```bash
   git -C <project-path> status --short
   ```
   If no changes, report "Nothing to commit" and stop.

3. **Create WIP commit:**
   ```bash
   git -C <project-path> add -A
   git -C <project-path> commit -m "WIP: <description>"
   ```
   - If `$ARGUMENTS` is provided, use it as the description
   - If no description provided, generate a brief one from the changed files

4. **Show result:**
   ```bash
   git -C <project-path> log -1 --oneline
   ```

## Notes
- This is intentionally quick and loose — WIP commits will be squashed later
- Uses `git add -A` to capture everything (including untracked files)
- The commit message prefix "WIP: " makes these easy to identify for squashing
