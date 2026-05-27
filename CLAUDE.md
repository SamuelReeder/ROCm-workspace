# ROCm Workspace Hub

Central dispatch workspace for ROCm development projects. Agents normally run on the HPE controller host/container; ROCm build, test, benchmark, and GPU runtime work is routed through durable Alola sessions.

## Source of Truth

- Projects, aliases, and long-lived worktrees → `.claude/registry/projects.json`
- Workspace-local clone/worktree bootstrap → `scripts/bootstrap_repos.py`
- Commands → `.claude/commands/*.md`
- Agents → `.shared/agents/*.md` (symlinked into `.claude/agents/` and `.codex/agents/`)
- Skills → `.shared/skills/*/` (symlinked into `.claude/skills/` and `.codex/skills/`)
- Task tracking → beads_rust (`br`) in `.beads/`
- Alola details → `docs/machines/alola.md`

## Default Agent Execution

- Stay local to the HPE/controller host for orchestration, editing, git, GitHub, and Teams replies.
- Do not run ROCm builds/tests/benchmarks directly on HPE.
- For ROCm build/test/runtime work, run commands through:

```bash
workspace/scripts/alola-session run -- <command>
```

- The default Alola target is login node `03`, ASIC `gfx90a`, in the login enroot container `sareeder-latest_container`.
- Explicit GPU targets allocate a compute node through SLURM, for example:

```bash
workspace/scripts/alola-session run --target gfx942 -- <command>
```

This uses the configured `MARKHAM&GFX942` constraint and `/cluster/images/hipdnn/hipdnn_latest_gfx942.sqsh`.

## Workspace Setup

- New-machine clones live under gitignored `repos/<project>/`.
- Temporary/local worktrees live under gitignored `worktrees/<project>/<name>/`.
- Bootstrap clones top-level repositories by default; use `--submodules` only when recursive submodule checkout is needed.
- Bootstrap all registry repos:

```bash
python3 scripts/bootstrap_repos.py
```

- Create a workspace-local worktree:

```bash
python3 scripts/bootstrap_repos.py --project rocm-libraries --worktree rocm-libraries <name> <branch>
```

## Workflow Principles

1. Plan first for non-trivial tasks.
2. Use subagents liberally for independent implementation/review work.
3. Track persistent work in beads when appropriate.
4. Verify before done with a build, test, or focused review.
5. Attempt autonomous bug fixing before escalating.

## Key Rules

1. Use absolute paths when operating inside project clones/worktrees.
2. Do not rely on `/goto`; read the registry and project docs directly when context is needed.
3. Each worktree keeps its own `build/` and `.venv`.
4. Before creating a fresh worktree from a moving base branch, fetch the source clone first.
5. Beads commands require `source "$HOME/.cargo/env"` first.
6. No Jira/project IDs in commit messages, PR titles, PR bodies, or branch names.
