---
description: Create a draft PR and close the associated beads task
argument-hint: (typically invoked by finalize agents, not directly)
allowed-tools: [Bash, Read]
---

# Create PR

Push the branch, create a draft PR, update the beads task, and report completion.

## PR Conventions

- Title format: `[hipDNN] <descriptive title>` — no Jira ticket ID anywhere in the PR (title, body, or branch name)
- PR is always created as a **draft**
- Assignee: `SamuelReeder`
- No "Generated with Claude Code" footer
- Use markdown formatting for code symbols, file names, function names, flags, etc. (e.g. `MyClass`, `--flag`, `file.cpp`)

## PR Body Template

```
## Motivation

<Why this change is needed and what it achieves>

## Technical Details

<Plain unified summary of the approach and changes. Describe what was added or modified and why, using `code formatting` for symbols, files, and flags. Do not list files mechanically or reference review feedback — just explain the implementation.>

## Test Plan

- [ ] <test 1>
- [x] <test 2 — mark completed tests with [x], pending with [ ]>

## Submission Checklist

- [ ] Look over the contributing guidelines at https://github.com/ROCm/ROCm/blob/develop/CONTRIBUTING.md#pull-requests.
```

## Steps

### 1. Push the branch

```bash
git -C <worktree_path> push -u origin <branch>
```

If push fails, report the error verbatim and stop.

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

## Technical Details

<technical_details>

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
br update <beads_id> --design "<synopsis of what was implemented and how>"
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
