---
description: Prepare a pull request with commit analysis and suggested description
argument-hint: [project] [base-branch]
allowed-tools: [Bash, Read]
---

# PR Preparation

Analyze commits and prepare a pull request description.

**Arguments:** $ARGUMENTS

## Process

1. **Resolve project:**
   - First argument = project key or alias (resolve via `/home/AMD/sareeder/ROCm-workspace/.claude/registry/projects.json`)
   - If not provided, check in-progress tasks (`source "$HOME/.cargo/env" && br list --json`) or infer from conversation
   - Determine the project path (and worktree path if applicable)

2. **Resolve base branch:**
   - Second argument = base branch (default: `main`)
   - For TheRock: typically `develop` or `main`
   - For rocm-libraries: typically `develop` or `main`

3. **Show commit stack:**
   ```bash
   git -C <path> log --oneline <base>..HEAD
   ```

4. **Show diff stats:**
   ```bash
   git -C <path> diff --stat <base>..HEAD
   ```

5. **Show current branch:**
   ```bash
   git -C <path> branch --show-current
   ```

6. **Check remote status:**
   ```bash
   git -C <path> status -sb
   ```

7. **Suggest PR content:**
   - Suggest a concise PR title (under 70 characters)
   - Draft a PR summary with:
     - What changed and why
     - Key files modified
     - Testing notes (if test files changed)
   - If there are WIP commits, suggest squashing first (reference `/squash-prep`)

8. **Stop and wait** for user direction before creating the PR.

## Output Format

```
## Branch: <branch-name>
## Base: <base-branch>
## Commits: <count>

### Commit Stack
<commit list>

### Diff Stats
<diff stats>

### Suggested PR
**Title:** <title>
**Summary:**
<summary>

### Next Steps
- Review the suggested PR content
- Run `/squash-prep` if WIP commits need squashing
- Confirm to create the PR with `gh pr create`
```
