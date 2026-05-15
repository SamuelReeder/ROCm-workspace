# ROCm Workspace Hub

Centralized dispatch workspace for ROCm development projects.

## Source of Truth

- Projects, worktrees, paths, aliases → `.claude/registry/projects.json`
- Commands → `.claude/commands/*.md` (invoke with `/command-name`)
- Agents → `.shared/agents/*.md` (symlinked into `.claude/agents/` and `.codex/agents/`; sync Codex config with `scripts/sync_codex_agents.py`)
- Skills → `.shared/skills/*/` (symlinked into `.claude/skills/` and `.codex/skills/`)
- Task tracking → beads_rust (`br`) in `.beads/` — use `/task` command
- Lessons learned → `tasks/lessons.md`

## Workflow Principles

1. **Plan first** for non-trivial tasks
2. **Use subagents liberally** — orchestrator coordinates, agents execute
3. **Track persistently** — update beads tasks with progress, status, external refs
4. **Verify before done** — build, test, or review before marking complete
5. **Self-improvement** — append lessons to `tasks/lessons.md` after corrections
6. **Autonomous bug fixing** — attempt up to 3 fix iterations before escalating

## Machine Detection

Run `hostname` to determine where you are. Check `.claude/registry/machines.json` for known machines:
- If hostname matches a `hostPattern`, read the machine's `context` doc before doing anything
- Run the machine's `detectScript` to get GPU, enroot, and environment info
- If on **Alola** (`ctr2-alola-login-*`): read `docs/machines/alola.md` — builds require enroot containers

If no hostname match, check if project paths are accessible with `test -d` before assuming local.

## Key Rules

1. **Worktree Isolation** — each worktree has its own `build/` and `.venv`
2. **Absolute Paths** — always use full paths to the correct worktree
3. **Project CLAUDE.md** — load with `/goto` for project-specific instructions
4. **Beads prefix** — all `br` commands require `source "$HOME/.cargo/env"` first
5. **Fresh worktrees** — before creating a new worktree, always fetch and pull the latest default branch (e.g., `main` or `develop`) of the project so the worktree starts from the most recent upstream state

## Commit & PR Conventions

- **No ticket/project IDs** — do not include Jira ticket IDs or project keys in commit messages, PR titles, PR bodies, or branch names
- **Commits** — use the `commit` subagent (`subagent_type="commit"`) to stage, pre-commit, commit, and push in isolation; write the commit message yourself (you have context), pass it to the agent
- **PRs** — see `/create-pr` for full PR conventions
