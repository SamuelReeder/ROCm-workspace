---
description: Comprehensive code review of a branch's changes against its upstream merge base
argument-hint: [project] [worktree] [base-branch] [--branch <branch>] [--single-agent|--multi-agent|--auto]
allowed-tools: [Bash, Read, Glob, Grep, Write]
---

# Code Review

Perform a comprehensive code review of a branch's changes against its clean merge base.

**Arguments:** $ARGUMENTS

## Process

### 1. Resolve project, worktree, and optional target branch

- Parse `$ARGUMENTS` as optional positional arguments plus optional flags: `[project] [worktree] [base-branch] [--branch <branch>] [--single-agent|--multi-agent|--auto]`
- Support `--branch <branch>` to review a fetched remote branch directly, even when it is not checked out locally
- Strip the mode flag before positional parsing
- Strip the `--branch <branch>` pair before positional parsing
- If `--branch` is present without a value, stop with a short error
- If more than one mode flag is present, stop with a short error
- Resolve project as `repos/<project>`; project names are immediate repository directory names
- Resolve a worktree by inspecting `worktrees/<project>/` or `git -C repos/<project> worktree list`
- If 2 arguments are given, treat the 2nd as a worktree directory only if it exists; otherwise treat it as a base branch
- If 3 arguments are given: arg1=project, arg2=worktree, arg3=base branch
- If no arguments: check in-progress tasks (`source "$HOME/.cargo/env" && br list --json`) or infer from conversation context
- Default worktree to the current checkout or the repository's main checkout
- Default review mode to `auto`
- If `--branch` is provided without a worktree, use `repos/<project>` as the git context root
### 2. Resolve current branch, upstream, and explicit branch target

- Determine the current branch:
  ```bash
  CURRENT_BRANCH=$(git -C <path> branch --show-current)
  ```
- Resolve the configured upstream, if any:
  ```bash
  UPSTREAM=$(git -C <path> rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null || true)
  ```
- If `--branch <branch>` was provided, set:
  ```bash
  EXPLICIT_BRANCH=<branch>
  ```

### 3. Resolve base branch

- From argument (2nd or 3rd positional), or detect:
  ```bash
  git -C <path> symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||'
  ```
- Fallback: `main`

### 4. Refresh remote refs and find clean merge base

Always fetch the latest base branch before review. Also fetch the latest version of the branch under review, either from `--branch` or from the configured upstream, so the review is not based on stale refs.

```bash
git -C <path> fetch origin <base-branch> --quiet 2>/dev/null
if [ -n "$EXPLICIT_BRANCH" ]; then
  git -C <path> fetch origin "$EXPLICIT_BRANCH" --quiet 2>/dev/null
  TARGET="origin/$EXPLICIT_BRANCH"
elif [ -n "$UPSTREAM" ]; then
  REMOTE=${UPSTREAM%%/*}
  REMOTE_BRANCH=${UPSTREAM#*/}
  git -C <path> fetch "$REMOTE" "$REMOTE_BRANCH" --quiet 2>/dev/null
  TARGET="$UPSTREAM"
else
  TARGET=HEAD
fi
MERGE_BASE=$(git -C <path> merge-base origin/<base-branch> "$TARGET")
```

This ensures the diff only contains the branch's own changes — no upstream noise.
If `--branch` is used, review the fetched remote branch tip directly.
If `UPSTREAM` exists and differs from local `HEAD`, review the fetched upstream tip by default and note that the local branch was stale or diverged.

### 5. Early exit check

If `git diff <merge-base>..<target>` produces no output, report "No changes found between the review target and merge base" and stop without writing a file.

### 6. Gather data

Run these commands against the resolved worktree path:

```bash
# Current branch
git -C <path> branch --show-current

# Upstream and target
git -C <path> rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null || true
printf '%s\n' "$EXPLICIT_BRANCH"

# Commit stack
git -C <path> log --oneline $MERGE_BASE..$TARGET

# Full diff
git -C <path> diff $MERGE_BASE..$TARGET

# Stats
git -C <path> diff --stat $MERGE_BASE..$TARGET
git -C <path> diff --shortstat $MERGE_BASE..$TARGET

# Changed files list
git -C <path> diff --name-only $MERGE_BASE..$TARGET

# Dirty worktree check
git -C <path> status --short
```

### 7. Read changed files in full

For each file in the changed files list:
- If `TARGET` is checked out in the selected worktree, read the full file from the filesystem for complete context
- If reviewing an explicit remote branch that is not checked out locally, read file content from git objects, for example:
  ```bash
  git -C <path> show $TARGET:path/to/file
  ```
- For files >1000 lines, focus on the change regions (use the diff hunks to identify relevant line ranges) and read those regions plus surrounding context

### 8. Resolve review mode and decide whether to use subagents

Support three modes:

- `--single-agent`: force the simpler legacy flow with one reviewer and no subagent orchestration
- `--multi-agent`: force orchestrated multi-agent review when subagents are available
- `--auto`: choose based on diff size and scope

Decision rules:

- If mode is `single-agent`, use one reviewer even if the diff is large
- If mode is `multi-agent`, use subagents unless the runtime does not support them; if unavailable, note the fallback and continue single-agent
- If mode is `auto`, stay single-agent for roughly `< 8` changed files or `< 400` changed lines unless the risk is unusually high
- If mode is `auto`, prefer subagents when the diff spans multiple top-level components, mixes code with build/config changes, or has clear subsystem boundaries

When using subagents:

- Keep the orchestrator responsible for final conclusions and the written review
- Partition by disjoint scope instead of having several agents review the full diff
- Good partitions include component/directory splits, API/interface changes, tests/coverage, and build or CI changes

Each subagent should return:

- Evidence-backed findings with file and line references
- A short subsystem summary describing the dominant risks in its scope
- Notes on uncertainty where the evidence is incomplete

### 9. Explore related context

This step is intentionally open-ended. Use Grep, Glob, and Read to:
- Check how changed functions/classes are used elsewhere in the codebase
- Read related headers, interfaces, or type definitions
- Look at existing tests for the changed code
- Understand patterns in surrounding code for consistency checks
- Check for callers that might be affected by API changes
- If reviewing an explicit remote branch, prefer `git grep`, `git show`, and diff hunk context when filesystem reads would reflect a different checkout than the review target

Spend appropriate effort here — deeper exploration for larger or riskier changes.

### 10. Consolidate and analyze for issues

If subagents were used, consolidate their output before finalizing findings:

- De-duplicate overlapping findings
- Merge multiple narrow comments into a single stronger issue when they point to the same root cause
- Identify any cross-cutting or high-level issues that only become obvious after combining scopes, such as partial migrations, inconsistent contracts, repeated missing validation, or systematic test gaps
- Do not invent high-level issues unless they are supported by concrete evidence from the underlying findings

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
- **Suggestion** — Concrete actionable improvement (refactor, rename, missing test). Must be a real suggestion, not a positive comment or observation.

Do not note positive findings or compliment the code. Only report problems and actionable suggestions.

Include file path and line number references for every finding.

### 11. False-positive scrub

Before writing the report, do a dedicated verification pass over the findings:

- Re-read each finding against the exact diff hunk and surrounding file context
- Check related callers, tests, and guards for evidence that the issue is already handled
- Remove speculative or weakly-supported findings
- Downgrade severity where the concern is real but the original severity was too strong
- Re-check any synthesized high-level issue against the concrete supporting findings

The goal is to minimize false positives and keep the report high-signal.

### 12. Write review file

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

**Date:** YYYY-MM-DD | **Branch:** <branch> | **Base:** origin/<base-branch> | **Merge Base:** <sha> | **Files:** <n> | **Lines:** +N / -N

## Summary

<2-4 sentences: what the branch does, scope, approach. Note review mode, stale/dirty worktree, and any cross-cutting issues.>

## Issues

### Critical
1. `path/to/file:N` — <concise description>

### Warnings
1. `path/to/file:N` — <concise description>

### Suggestions
1. `path/to/file:N` — <concise description>

## Overall Assessment

**Risk:** Low / Medium / High — <one sentence on merge readiness and key actions>
```

### 13. Report results

After writing the file, output:
- Path to the review file
- Count of findings by severity (Critical / Warning / Suggestion)
- Overall risk level
