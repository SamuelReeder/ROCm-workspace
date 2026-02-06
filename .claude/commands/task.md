---
description: Manage issues with beads_rust (br) local tracker
argument-hint: <list|ready|create|show|close|update|q|dep|label|search>
allowed-tools: [Bash, Read]
---

# Issue Tracking (beads_rust)

Wrapper around `br` — a local-first issue tracker with SQLite storage.
All data lives in `/home/AMD/sareeder/ROCm-workspace/.beads/` (gitignored).

**Arguments:** $ARGUMENTS

## Commands

All commands run from `/home/AMD/sareeder/ROCm-workspace` where `.beads/` lives.
Source cargo env first: `source "$HOME/.cargo/env"`

### `/task list`
```bash
source "$HOME/.cargo/env" && br list
```
Show all issues. Add `--json` for machine-readable output.

### `/task ready`
```bash
source "$HOME/.cargo/env" && br ready
```
Show actionable issues (open, unblocked, not deferred).

### `/task create <title>`
```bash
source "$HOME/.cargo/env" && br create "<title>" --type task --priority 2
```
Create a new task. After creation, add labels for project and worktree context:
- **Project labels:** `therock`, `rocm-libraries`, `mlse-tools`, `dnn-benchmarking`
- **Worktree labels:** `wt:main`, `wt:consumption`, `wt:miopen-plugin`
- **Component labels:** `hipdnn`, `miopen`, `rocblas`, `composable-kernel`

Priority mapping: 0=Critical, 1=High, 2=Normal (default), 3=Low, 4=Backlog

### `/task q <title>`
```bash
source "$HOME/.cargo/env" && br q "<title>"
```
Quick capture — creates issue, prints ID only. Good for rapid task entry.

### `/task show <id>`
```bash
source "$HOME/.cargo/env" && br show <id>
```
Show full details for an issue including labels, dependencies, and comments.

### `/task close <id>`
```bash
source "$HOME/.cargo/env" && br close <id>
```
Mark an issue as closed/completed.

### `/task update <id> [flags]`
```bash
source "$HOME/.cargo/env" && br update <id> [flags]
```
Update issue fields. Common flags:
- `--status <open|in_progress|closed>` — change status
- `--priority <0-4>` — change priority
- `--description "<text>"` — set/update description
- `--title "<text>"` — change title

### `/task dep <id> <blocking-id>`
```bash
source "$HOME/.cargo/env" && br dep add <id> <blocking-id>
```
Add a dependency: `<blocking-id>` blocks `<id>`.

### `/task label <id> <labels...>`
```bash
source "$HOME/.cargo/env" && br label add <id> <labels...>
```
Add labels to an issue for project/worktree/component tagging.

### `/task search <query>`
```bash
source "$HOME/.cargo/env" && br search "<query>"
```
Full-text search across issues.

## Programmatic Access

For AI/script integration, append `--json` to any command:
```bash
source "$HOME/.cargo/env" && br list --json
source "$HOME/.cargo/env" && br show <id> --json
```

## Notes
- Data stored in `.beads/` (SQLite + JSONL) — local-only, never committed
- Use labels to link issues to projects and worktrees
- `br stats` shows project-level overview
- `br blocked` shows issues waiting on dependencies
