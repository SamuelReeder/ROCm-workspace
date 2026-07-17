---
name: review-pr
description: Review a branch or PR against a clean upstream merge base, inspect changed files and related context, and write a severity-tagged markdown review report under reviews/<project>/.
---

# Review PR

Use this skill when the user wants a comprehensive review of a branch or PR, wants the repo's `review-pr` workflow, or asks for a written review report.

## Inputs

Accept up to three optional positional arguments plus optional flags:

- `[project] [worktree] [base-branch]`
- `--branch <branch>`
- `--single-agent`
- `--multi-agent`
- `--auto`

Interpret them the same way as the Claude command:

- Strip any mode flag from the argument list before positional parsing.
- Strip any `--branch <branch>` pair from the argument list before positional parsing.
- If `--branch` is provided without a value, stop with a short error.
- If more than one mode flag is provided, treat that as invalid input and stop with a short error.
- If 2 arguments are given, treat the 2nd as a worktree directory under `worktrees/<project>/` only if that directory exists; otherwise treat it as a base branch.
- If no arguments are given, infer from in-progress tasks via `source "$HOME/.cargo/env" && br list --json` or from conversation context.
- Default `worktree` to the current checkout or the repository's main checkout.
- Default review mode to `auto`.
- Support reviewing a fetched remote branch directly via `--branch <branch>` even when no local worktree exists for that branch.

## Workflow

1. Resolve the project from `repos/<project>/` and resolve a worktree by inspecting `worktrees/<project>/` or `git worktree list`.
2. Resolve the current branch, any configured upstream, and any explicit branch target:

   ```bash
   CURRENT_BRANCH=$(git -C <path> branch --show-current)
   UPSTREAM=$(git -C <path> rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null || true)
   EXPLICIT_BRANCH=<branch if --branch was provided>
   ```

3. Resolve the base branch from the explicit argument or detect it with:

   ```bash
   git -C <path> symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||'
   ```

   Fall back to `main`.
4. Refresh remote refs before reviewing. Always fetch the base branch. Also fetch the latest remote version of the review branch, either from `--branch` or from the configured upstream, so the review is not based on stale local refs:

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
   ```

5. Choose the review target:

   - If `--branch` was provided, review the fetched remote branch tip directly.
   - Otherwise, if an upstream exists, prefer reviewing the latest fetched upstream tip so the report reflects the current branch on the remote.
   - Otherwise, review local `HEAD`.
   - If local `HEAD` differs from the upstream tip, note that explicitly in the report.

6. Compute a clean merge base against the chosen target:

   ```bash
   MERGE_BASE=$(git -C <path> merge-base origin/<base-branch> "$TARGET")
   ```

7. If `git diff $MERGE_BASE..$TARGET` is empty, report that no changes were found and stop without writing a file.
8. Gather branch name, commit stack, full diff, diff stats, and changed files for `$MERGE_BASE..$TARGET`.
9. Check whether the worktree has uncommitted changes. If it does, mention that they are excluded from the review unless the user explicitly asks to include them.
10. Resolve review mode:

   - `--single-agent`: force the simpler legacy flow with one reviewer and no subagent orchestration
   - `--multi-agent`: force orchestrated multi-agent review when subagents are available
   - `--auto`: choose based on diff size and scope

11. Decide whether to use subagents:

   - If mode is `single-agent`, use one reviewer even if the diff is large.
   - If mode is `multi-agent`, use subagents unless the runtime does not support them; if subagents are unavailable, note the fallback and continue single-agent.
   - If mode is `auto`, stay single-agent for small reviews, roughly under 8 changed files or 400 changed lines, unless the risk is unusually high.
   - If mode is `auto`, prefer multi-agent review for larger diffs, multiple top-level components, mixed code and build/config changes, or changes with clear subsystem boundaries.

12. When using subagents, keep the orchestrator responsible for the final review. Do not have multiple agents review the full diff. Partition by disjoint scope such as:

   - top-level component or directory
   - API and interface changes
   - tests and validation gaps
   - build, CI, packaging, or config changes

13. Each review subagent should:

   - inspect only its assigned files plus the minimum related context needed for callers, types, and tests
   - return evidence-backed findings with file and line references
   - include a short subsystem summary describing the main risk areas in its scope
   - avoid speculative comments and note uncertainty when evidence is incomplete

14. The orchestrator should consolidate subagent output before writing the report:

   - deduplicate overlapping findings
   - merge closely related comments into one stronger finding when they describe the same underlying defect
   - identify cross-cutting or high-level issues that only become clear after combining scopes, such as inconsistent API behavior, repeated missing error handling, partial migrations, or systematic test gaps
   - avoid inventing high-level issues without concrete support from the reviewed files

15. Read every changed file for context. For files over 1000 lines, focus on changed hunks plus surrounding context.
    - If reviewing an explicit remote branch that is not checked out locally, read file contents from git objects with `git show $TARGET:path/to/file`.
16. Explore related callers, interfaces, type definitions, and tests to evaluate downstream impact and coverage.
    - If reviewing an explicit remote branch, prefer `git grep`, `git show`, and diff hunk context when filesystem reads would reflect a different checkout than the review target.
17. Record findings with severity:
   - `Critical`: likely bug, security issue, or data-loss risk
   - `Warning`: important risk, regression, or missing coverage
   - `Suggestion`: concrete actionable improvement — not a positive comment or observation
   - Do not include positive findings or compliments on the code
18. Do a false-positive scrub before writing the report:

   - Re-read each finding against the exact diff hunk and surrounding file context.
   - Check whether existing tests, callers, or guards already address the concern.
   - Remove speculative findings that are not well-supported by evidence in the code.
   - Downgrade severity when the issue is real but the initial classification was too strong.
   - Re-check any synthesized high-level issue against the underlying concrete findings so the summary does not overstate the evidence.

19. Include file paths and line numbers for every remaining finding.
20. Write the review to `/home/AMD/sareeder/ROCm-workspace/reviews/<project>/` using filename `<branch-short>-<YYYY-MM-DD>.md`.

## Review File

The report should include:

- One-line metadata: date, branch, base, merge base SHA, file count, line delta
- Summary (2-4 sentences): what the branch does, review mode, any stale/dirty worktree notes, cross-cutting issues
- Findings grouped into `Critical`, `Warnings`, and `Suggestions` — each as `path/to/file:N — description`
- Overall risk level (`Low`, `Medium`, `High`) with a single sentence on merge readiness

Strip common prefixes from the branch name when building the filename, including `users/<name>/`, `feature/`, and `bugfix/`. Replace any remaining `/` with `-`.

## Final Response

After writing the report, return:

- The review file path
- Finding counts by severity
- Overall risk level
