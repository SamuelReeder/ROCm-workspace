## Environment
Controller host: HPE (`hpe-sjc2-43`) when deployed. Verify the current host with
`hostname` before assuming local paths.

Use the workspace filesystem to resolve project context. Immediate git
directories under `repos/` are projects; verify paths with `test -d` and git
metadata before accessing them.

## Execution routing
- Teams harness agents run locally on the controller host/container by default.
- Ordinary code reading, editing, review, planning, and research should use the workspace-local checkout/state.
- Workspace checkout roots `/app/workspace/repos` and `/app/workspace/worktrees` are durable Docker volumes, not temporary scratch space.
- This workspace does not provide SSH wrappers or remote-execution CLIs. If a deployment provides remote execution, follow the runtime instructions injected by that deployment instead of looking for scripts in this repo.

## Projects

Discover projects with:

```bash
for repo in repos/*; do
  test -d "$repo/.git" && basename "$repo"
done
```

Resolve a worktree from a repository's git worktree list:

```bash
git -C repos/<project> worktree list --verbose
```

## Jira

Use `.claude/skills/orchestrate/jira-mapping.json` for Jira project keys and
base branches. Confirm the mapped repository exists under `repos/` before
starting work.
