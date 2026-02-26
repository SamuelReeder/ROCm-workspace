# ROCm Workspace Hub

Centralized dispatch workspace for ROCm development projects.

## Source of Truth

- Projects, worktrees, paths, aliases → `.claude/registry/projects.json`
- Commands → `.claude/commands/*.md` (invoke with `/command-name`)
- Agents → `.claude/agents/*.md` (launched as subagents)
- Skills → `.claude/skills/*/` (invoke with `/skill-name`)
- Task tracking → beads_rust (`br`) in `.beads/` — use `/task` command
- Lessons learned → `tasks/lessons.md`

## Workflow Principles

1. **Plan first** for non-trivial tasks
2. **Use subagents liberally** — orchestrator coordinates, agents execute
3. **Track persistently** — update beads tasks with progress, status, external refs
4. **Verify before done** — build, test, or review before marking complete
5. **Self-improvement** — append lessons to `tasks/lessons.md` after corrections
6. **Autonomous bug fixing** — attempt up to 3 fix iterations before escalating

## Key Rules

1. **Worktree Isolation** — each worktree has its own `build/` and `.venv`
2. **Absolute Paths** — always use full paths to the correct worktree
3. **Project CLAUDE.md** — load with `/goto` for project-specific instructions
4. **Beads prefix** — all `br` commands require `source "$HOME/.cargo/env"` first
