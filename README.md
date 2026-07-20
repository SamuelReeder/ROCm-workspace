# ROCm Workspace

Centralized workspace for managing ROCm repositories and isolated git worktrees.

## Repository and Worktree Layout

The filesystem is the source of truth:

```text
repos/<project>/                         # existing canonical git clone
worktrees/<project>/<branch-suffix>/       # workspace-local worktree
```

Every immediate git repository directory under `repos/` is a project. There is
no project registry or project metadata file to maintain. Both directories are
gitignored.

Worktree directory names use only the suffix after the required
`users/sareeder/` branch prefix. Slashes in that suffix become `--`, so
`users/sareeder/fix-layout` becomes
`worktrees/rocm-libraries/fix-layout`. The prefix is implicit and must be
present on every workspace worktree branch.

## Repository Discovery and Worktrees

Clone repositories into `repos/` manually, then use the bootstrap script:

```bash
python3 scripts/bootstrap_repos.py                  # list discovered repos
python3 scripts/bootstrap_repos.py --fetch          # fetch all discovered repos
python3 scripts/bootstrap_repos.py --dry-run        # inspect worktree commands
```

Create a worktree from an existing repository clone:

```bash
python3 scripts/bootstrap_repos.py \
  --project rocm-libraries \
  --worktree rocm-libraries users/sareeder/fix-layout
```

This creates `worktrees/rocm-libraries/fix-layout`. Add `--no-fetch` to skip
fetching before worktree creation and `--submodules` when recursive submodule
initialization is required.

List all worktrees:

```bash
for repo in repos/*; do
  test -d "$repo/.git" || continue
  git -C "$repo" worktree list --verbose
done
```

List one project's worktrees:

```bash
git -C repos/rocm-libraries worktree list --verbose
```

## How to Use

Start Claude from this workspace:

```bash
cd ~/ROCm-workspace
claude
```

Available slash commands:

```text
/worktrees                         # list all discovered repositories/worktrees
/worktrees rocm-libraries          # list one repository's worktrees
/orchestrate ALMIOPEN-1234         # Jira-to-PR orchestration workflow
/review-pr rocm-libraries          # review a branch or worktree
/squash-prep rocm-libraries        # suggest squash strategy
```

Mention a project or component in a prompt to route work. Project resolution is
based on repository directory names and the current git worktree; aliases are
not maintained in this workspace.

## Worktree Isolation

Each worktree maintains its own:

- `build/` directory
- `.venv` for Python projects
- independent git working tree

The workspace prevents accidental cross-contamination with path validation.

## Build Examples

Use the checked-out hipDNN docs for standalone prerequisites and targets:
`repos/rocm-libraries/projects/hipdnn/docs/Building.md` and
`repos/rocm-libraries/projects/hipdnn/docs/Superbuild.md`. The repository root
`CMakePresets.json` defines `hipdnn-providers` as the provider-enabled preset;
`hipdnn` is hipDNN-only.

**Standalone hipDNN:**

```bash
cmake -S <worktree>/projects/hipdnn \
      -B <worktree>/projects/hipdnn/build \
      -G Ninja
cmake --build <worktree>/projects/hipdnn/build --target check
```

**hipDNN with supported provider plugins:**

```bash
cd <worktree>
cmake --preset hipdnn-providers
cmake --build build
cmake --build build --target hipdnn-check miopen-provider-check hipblaslt-provider-check
```

The `hipdnn-providers` preset builds hipDNN, MIOpen Provider, hipBLASLt
Provider, and integration tests together. Use
`scripts/build_and_test_providers.sh` for the same workflow. Do not use the
old standalone provider loop or an unqualified root
`check` target; superbuild test targets are component-prefixed.

## Architecture

```text
ROCm-workspace/
├── CLAUDE.md                    # hub instructions
├── .claude/
│   ├── commands/                # /worktrees, /orchestrate, /review-pr, /squash-prep
│   ├── skills/                  # auto-triggered skills and workflow templates
│   └── hooks/                   # workspace safety guidance
├── repos/                       # gitignored repository clones
├── worktrees/                   # gitignored branch-derived worktrees
├── scripts/
│   ├── bootstrap_repos.py       # discovery and worktree setup
│   └── test_bootstrap_repos.py  # focused bootstrap tests
├── docs/                        # reference documentation
└── README.md
```

## Requirements

- Claude Code CLI
- `git`
- network access only when cloning or fetching a repository

This workspace configuration is part of ROCm development workflow.
