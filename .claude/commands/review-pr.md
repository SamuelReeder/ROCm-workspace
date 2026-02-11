---
description: Comprehensive code review of a branch's changes against its upstream merge base
argument-hint: [project] [worktree] [base-branch]
allowed-tools: [Bash, Read, Glob, Grep, Write]
---

# Code Review

Perform a comprehensive code review of a branch's changes against its clean merge base.

**Arguments:** $ARGUMENTS

## Process

### 1. Resolve project and worktree

- Parse `$ARGUMENTS` positionally (all optional): `[project] [worktree] [base-branch]`
- Resolve project via registry at `/home/AMD/sareeder/ROCm-workspace/.claude/registry/projects.json`
- If 2 arguments given, disambiguate the 2nd: if it matches a worktree key in the resolved project → treat as worktree, otherwise → treat as base branch
- If 3 arguments given: arg1=project, arg2=worktree, arg3=base branch
- If no arguments: check in-progress tasks (`source "$HOME/.cargo/env" && br list --json`) or infer from conversation context
- Default worktree: `main`

### 2. Resolve base branch

- From argument (2nd or 3rd positional), or detect:
  ```bash
  git -C <path> symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||'
  ```
- Fallback: `main`

### 3. Find clean merge base

```bash
git -C <path> fetch origin <base-branch> --quiet 2>/dev/null
MERGE_BASE=$(git -C <path> merge-base origin/<base-branch> HEAD)
```

This ensures the diff only contains the branch's own changes — no upstream noise.

### 4. Early exit check

If `git diff <merge-base>..HEAD` produces no output, report "No changes found between HEAD and merge base" and stop without writing a file.

### 5. Gather data

Run these commands against the resolved worktree path:

```bash
# Current branch
git -C <path> branch --show-current

# Commit stack
git -C <path> log --oneline $MERGE_BASE..HEAD

# Full diff
git -C <path> diff $MERGE_BASE..HEAD

# Stats
git -C <path> diff --stat $MERGE_BASE..HEAD
git -C <path> diff --shortstat $MERGE_BASE..HEAD

# Changed files list
git -C <path> diff --name-only $MERGE_BASE..HEAD
```

### 6. Read changed files in full

For each file in the changed files list:
- Read the full file for complete context
- For files >1000 lines, focus on the change regions (use the diff hunks to identify relevant line ranges) and read those regions plus surrounding context

### 7. Explore related context

This step is intentionally open-ended. Use Grep, Glob, and Read to:
- Check how changed functions/classes are used elsewhere in the codebase
- Read related headers, interfaces, or type definitions
- Look at existing tests for the changed code
- Understand patterns in surrounding code for consistency checks
- Check for callers that might be affected by API changes

Spend appropriate effort here — deeper exploration for larger or riskier changes.

### 8. Analyze for issues

Review all gathered context and identify:

- **Bugs, logic errors, race conditions, resource leaks**
- **Security issues** (injection, hardcoded secrets, path traversal, input validation)
- **Error handling gaps** (unchecked returns, swallowed exceptions, missing cleanup)
- **Performance concerns** (unnecessary allocations, O(n²) patterns, missing caching)
- **Code style / consistency** with surrounding code and project conventions
- **Missing edge cases** (null/empty inputs, overflow, boundary conditions)
- **API design / breaking changes** (signature changes, removed exports, changed behavior)
- **Test coverage gaps** (untested paths, missing negative tests)

Tag each finding with severity:
- **Critical** — Likely bug, security issue, data loss risk. Must fix before merge.
- **Warning** — Potential issue, code smell, or risky pattern. Should address.
- **Suggestion** — Style improvement, minor optimization, or nice-to-have. Optional.

Include file path and line number references for every finding.

### 9. Write review file

Write the review to: `/home/AMD/sareeder/ROCm-workspace/reviews/<project>/`

Create the subdirectory if it doesn't exist (e.g. `reviews/therock/`, `reviews/rocm-libraries/`).

**Filename:** `<branch-short>-<YYYY-MM-DD>.md`
- Strip common prefixes from the branch name: remove `users/sareeder/`, `users/<any>/`, `feature/`, `bugfix/`, etc.
- Use only the meaningful suffix (e.g. `users/sareeder/miopen-plugin-move` → `miopen-plugin-move`)
- Replace any remaining `/` with `-`
- Examples:
  - `users/sareeder/detail-migration` → `reviews/rocm-libraries/detail-migration-2026-02-09.md`
  - `users/sareeder/install-latest-rocm` → `reviews/therock/install-latest-rocm-2026-02-09.md`

**File structure:**

```markdown
# Code Review: <Project> / <branch>

| Field | Value |
|-------|-------|
| Date | YYYY-MM-DD |
| Branch | <branch> |
| Base | origin/<base-branch> |
| Merge Base | <sha> |
| Commits | <n> |
| Files Changed | <n> |
| Lines | +N / -N |

## Summary

<What the branch does, the approach taken, scope of changes>

## Commit Stack

| SHA | Message |
|-----|---------|
| ... | ...     |

## Issues

Each issue references the file and line. Only files with findings appear here.

### Critical
<Numbered list or "None found.">
1. `path/to/file` Line N: <description>

### Warnings
<Numbered list or "None found.">

### Suggestions
<Numbered list or "None found.">

## Overall Assessment

**Risk Level:** Low / Medium / High

<Quality assessment, readiness for merge, and recommended actions before merging>
```

### 10. Report results

After writing the file, output:
- Path to the review file
- Count of findings by severity (Critical / Warning / Suggestion)
- Overall risk level
