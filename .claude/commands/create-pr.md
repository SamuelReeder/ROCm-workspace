---
description: Create a draft PR and close the associated beads task
argument-hint: (typically invoked by finalize agents, not directly)
allowed-tools: [Bash, Read]
---

# Create PR

Push the branch, create a draft PR, update the beads task, and report completion.

## PR Conventions

- Title: `[hipDNN] <descriptive title>` — no Jira ticket IDs anywhere (title, body, branch)
- Always draft
- Assignee: `SamuelReeder`
- No "Generated with Claude Code" footer
- Backtick-format symbols, files, and flags (e.g. `MyClass`, `--flag`, `file.cpp`)

## PR Body

Keep the description high-level — the diff covers implementation details. Focus on *why* and *what changed conceptually*, not *how*.

```
## Motivation

<Why this change is needed and what problem it solves>

## Changes

<High-level summary of what changed. No file lists or line-level detail.>

## Risk Assessment

<Potential failure modes, regressions, or areas of concern. Note which are mitigated and which remain. If low-risk, say so briefly and why.>

## Test Plan

- [ ] <test 1>
- [x] <completed test>

## Submission Checklist

- [ ] Look over the contributing guidelines at https://github.com/ROCm/ROCm/blob/develop/CONTRIBUTING.md#pull-requests.
```

## Steps

### 1. Push the branch

```bash
git -C <worktree_path> push -u origin <branch>
```

Stop and report verbatim if push fails.

### 2. Create draft PR

```bash
cd <worktree_path> && gh pr create --repo <remote_repo> \
  --head <branch> \
  --base <base_branch> \
  --draft \
  --assignee SamuelReeder \
  --title "[hipDNN] <title>" \
  --body "$(cat <<'EOF'
## Motivation

<motivation>

## Changes

<changes>

## Risk Assessment

<risk_assessment>

## Test Plan

<test_plan_checklist>

## Submission Checklist

- [ ] Look over the contributing guidelines at https://github.com/ROCm/ROCm/blob/develop/CONTRIBUTING.md#pull-requests.
EOF
)"
```

Store the PR URL from the output.

### 3. Update beads task

```bash
source "$HOME/.cargo/env"
br update <beads_id> --external-ref "<jira_key> | <pr-url>"
br update <beads_id> --design "<synopsis of what was implemented>"
br close <beads_id>
```

### 4. Report completion

```
## Completion Report

| Field | Value |
|-------|-------|
| **PR** | <pr-url> (DRAFT) |
| **Beads Task** | <beads_id> (closed) |
| **Branch** | <branch> |
| **Worktree** | <worktree_path> |
```
