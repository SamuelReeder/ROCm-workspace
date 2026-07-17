# ROCm Workspace Hub

Central dispatch workspace for ROCm development projects. This repo owns project/worktree discovery and local workspace conventions; deployment-specific remote execution routing lives outside this repo.

## Source of Truth

- Repository projects → immediate git directories under `repos/<project>/`
- Workspace-local worktrees → `worktrees/<project>/<branch-suffix>/`
- Workspace-local clone/worktree bootstrap → `scripts/bootstrap_repos.py`
- Commands → `.claude/commands/*.md`
- Agents → `.shared/agents/*.md` (symlinked into `.claude/agents/` and `.codex/agents/`)
- Skills → `.shared/skills/*/` (symlinked into `.claude/skills/` and `.codex/skills/`)
- Task tracking → beads_rust (`br`) in `.beads/`

Repository names and worktrees are discovered from the filesystem; do not add project metadata files.

## Default Agent Execution

- Stay local to the controller host/container for orchestration, editing, git, GitHub, and Teams replies.
- Use this workspace for source checkout discovery and local file operations only.
- Do not rely on workspace-owned SSH wrappers or remote-execution scripts; if a deployment provides remote execution, follow the runtime instructions injected by that deployment.

## Workspace Setup

- Existing clones live under gitignored `repos/<project>/`.
- Workspace-local worktrees live under gitignored `worktrees/<project>/<branch-suffix>/`.
- In container deployments, `/app/workspace/repos` and `/app/workspace/worktrees` are durable Docker volumes, not temporary scratch paths.
- Bootstrap discovers existing git repositories under `repos/`; clone repositories there manually when needed.
- Workspace worktree branches must use the `users/sareeder/` prefix. The directory uses only the suffix: `users/sareeder/feature-x` becomes `feature-x`.

```bash
python3 scripts/bootstrap_repos.py
python3 scripts/bootstrap_repos.py --project rocm-libraries --worktree rocm-libraries users/sareeder/feature-x

```
- When verification requires a remote or specialized runtime, use the deployment-provided routing instructions rather than workspace-local scripts.

## Workflow Principles

1. Plan first for non-trivial tasks.
2. Use subagents liberally for independent implementation/review work.
3. Track persistent work in beads when appropriate.
4. Verify before done with a build, test, or focused review.
5. Attempt autonomous bug fixing before escalating.

## Key Rules

1. Use absolute paths when operating inside project clones/worktrees.
2. Discover projects from `repos/` rather than maintaining a project registry.
3. Each worktree keeps its own `build/` and `.venv`.
4. Before creating a fresh worktree from a moving base branch, fetch the source clone first.
5. Beads commands require `source "$HOME/.cargo/env"` first.
