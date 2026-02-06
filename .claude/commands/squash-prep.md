---
description: Analyze commits and suggest a squash strategy for clean PR history
argument-hint: [project] [base-branch]
allowed-tools: [Bash, Read]
---

# Squash Preparation

Analyze the commit stack and suggest a squash strategy for a clean PR.

**Arguments:** $ARGUMENTS

## Process

1. **Resolve project:**
   - First argument = project key or alias (resolve via `/home/AMD/sareeder/ROCm-workspace/.claude/registry/projects.json`)
   - If not provided, check in-progress tasks (`source "$HOME/.cargo/env" && br list --json`) or infer from conversation
   - Determine the project path (and worktree path if applicable)

2. **Resolve base branch:**
   - Second argument = base branch (default: `main`)

3. **Analyze commits:**
   ```bash
   git -C <path> log <base>..HEAD --oneline
   git -C <path> log <base>..HEAD --format="%h %s" --reverse
   ```

4. **Show overall diff:**
   ```bash
   git -C <path> diff <base> --stat
   ```

5. **Categorize commits:**
   - WIP commits (prefixed with "WIP:")
   - Fix commits (fixing previous commits in the stack)
   - Feature commits (actual meaningful changes)
   - Merge commits

6. **Suggest strategy:**
   - If all WIP: suggest single squash with a clean message
   - If mixed: suggest grouping related commits, squashing WIP into their feature commits
   - If already clean: report "commits look good, no squash needed"

7. **Draft squash commit message:**
   - Based on the overall diff, suggest a clean commit message
   - Follow conventional commit style if the repo uses it
   - Include scope if changes are focused on one component

8. **Provide squash command:**
   ```bash
   # Soft reset to base and recommit:
   git -C <path> reset --soft <base>
   git -C <path> commit -m "<suggested message>"
   ```

9. **Stop and wait** for user confirmation before executing any git commands.

## Notes
- This command ONLY analyzes and suggests — it never modifies git history automatically
- Always show the suggested commands and wait for explicit user approval
- Warn if the branch has been pushed to remote (force-push will be needed after squash)
