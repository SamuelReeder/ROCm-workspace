# ROCm Workspace

Centralized Claude Code workspace for managing multiple ROCm development projects with intelligent routing, worktree isolation, and automatic context loading.

## What is This?

This workspace acts as a dispatch hub that automatically:
- Detects which ROCm project you're working on from your prompts
- Loads project-specific build commands and development patterns
- Manages worktree isolation (separate builds, venvs)
- Routes commands to the correct project directory

## Managed Projects

| Project | Location | Type |
|---------|----------|------|
| **TheRock** | `~/TheRock` | CMake superbuild (hipDNN, MIOpen, ROCm stack) |
| **rocm-libraries** | `~/full/rocm-libraries` | CMake superbuild (23 library projects) |
| **mlse-tools-internal** | `~/mlse-tools-internal` | Python automation scripts |
| **dnn-benchmarking** | `~/dnn-benchmarking` | Python benchmarking package |

## Local Clone Bootstrap

Use the bootstrap script to clone every registry project into this workspace instead of scattering fresh clones under `$HOME`:

```bash
python3 scripts/bootstrap_repos.py --dry-run
python3 scripts/bootstrap_repos.py
```

The script reads `.claude/registry/projects.json`, clones each project remote into `repos/<project>/`, and creates `worktrees/` for workspace-local worktrees. Both directories are gitignored. New clones are shallow all-branch checkouts by default; add `--full-history` if complete history is required. If the registry path already exists, the script uses it as a Git object reference to avoid downloading duplicate objects. It does not initialize large submodules by default; add `--submodules` when a full recursive checkout is needed.

Create a workspace-local worktree with:

```bash
python3 scripts/bootstrap_repos.py \
  --project rocm-libraries \
  --worktree rocm-libraries my-feature users/sareeder/my-feature
```

That creates `worktrees/rocm-libraries/my-feature` from the local clone at `repos/rocm-libraries`. Add `--fetch` to update existing clones before use, and `--submodules` only when you need recursive submodule checkout.

### TheRock Worktrees

| Name | Path | Branch |
|------|------|--------|
| main | `~/TheRock` | users/sareeder/install-latest-rocm |
| consumption | `~/therock-consumption` | users/sareeder/hipdnn-consumption-tests |
| miopen-plugin | `~/therock-miopen-plugin-move` | users/sareeder/miopen-plugin-move |

## How to Use

### Start Claude from this workspace:
```bash
cd ~/ROCm-workspace
claude
```

### Option 1: Natural Language (Recommended)

Just mention the project, library, or worktree in your prompt:

```
"Fix the convolution bug in hipDNN"
→ Auto-routes to rocm-libraries, loads its CLAUDE.md

"Build MIOpen in the consumption worktree"
→ Routes to therock-consumption, uses correct build dir

"Add a benchmark test for batchnorm"
→ Routes to dnn-benchmarking, activates venv
```

**Detection keywords:**
- **TheRock**: therock, rock, superbuild, component names
- **consumption worktree**: consumption, hipdnn-consumption
- **miopen-plugin worktree**: miopen-plugin, plugin-move
- **rocm-libraries**: libs, hipdnn, miopen-provider, projects/
- **mlse-tools**: mlse, alola, kubernetes, promote
- **dnn-benchmarking**: benchmark, bench, --graph, perf

### Option 2: Explicit Commands

Use slash commands for direct navigation:

```bash
/goto therock              # Navigate to TheRock main
/goto therock consumption  # Navigate to consumption worktree
/goto libs                 # Navigate to rocm-libraries
/goto bench                # Navigate to dnn-benchmarking

/status                    # Show all projects and their git status
/worktrees                 # List all worktrees across projects
/worktrees therock add feature-x users/sareeder/branch-name  # Create new worktree
```

### Task Management

Issues tracked locally with [beads_rust](https://github.com/Dicklesworthstone/beads_rust) (`br`) — SQLite-backed, survives session resets:

```bash
/task create "Fix convolution dispatch"  # Create a new task
/task list                               # List all tasks with status/priority
/task ready                              # Show actionable (unblocked) tasks
/task show bd-abc                        # Show task details
/task close bd-abc                       # Mark task as done
/task q "Quick note"                     # Quick capture, prints ID only
```

Task data lives in `.beads/` (local-only, gitignored). Labels link tasks to projects (`therock`, `rocm-libraries`) and worktrees (`wt:main`, `wt:consumption`).

### PR Workflow

```bash
/wip "fix convolution dispatch"   # Quick WIP commit in current project
/squash-prep therock              # Suggest squash strategy for clean history
```

Use the `pr-summary` skill to draft or revise PR titles and descriptions.

## Features

### Automatic Context Loading
Each project has detailed instructions in its own `CLAUDE.md`. The workspace loads only the relevant context when you mention a project.

### Worktree Isolation
Each worktree maintains:
- Separate `build/` directory
- Separate `.venv` (for Python projects)
- Independent git working tree

The workspace prevents accidental cross-contamination with path validation.

### Build Pattern Intelligence

**TheRock:**
```bash
ninja -j 128 -C ~/therock-consumption/build hipDNN+build  # Incremental build
ninja -j 128 -C ~/TheRock/build miopen+expunge            # Clean rebuild
```

**rocm-libraries:**
```bash
ninja -j 128 -C ~/full/rocm-libraries/build check         # Run tests
ninja -j 128 -C ~/full/rocm-libraries/build format        # Format code
```

### Automatic Worktree Setup

When you create a new worktree, the workspace automatically:
1. Creates the worktree at `~/<project>-<name>`
2. Sets up `.venv` and installs requirements (for Python projects)
3. Copies `CLAUDE.md` from main repo
4. Updates the project registry

## Example Workflows

### Start work on a feature branch
```
You: "I need to work on the hipDNN consumption tests"

Claude: [Detects therock-consumption worktree]
        [Loads TheRock CLAUDE.md]
        Ready to work in ~/therock-consumption
        Branch: users/sareeder/hipdnn-consumption-tests
```

### Create a new worktree
```
You: "/worktrees therock add ck-integration users/sareeder/ck-integration"

Claude: [Creates worktree at ~/therock-ck-integration]
        [Sets up .venv automatically]
        [Installs requirements.txt]
        Ready for development
```

### Build with automatic context
```
You: "Build the composable_kernel component"

Claude: [Detects TheRock from component name]
        ninja -j 128 -C ~/TheRock/build composable_kernel
        [Build succeeds]
```

### Multi-project status
```
You: "/status"

Claude:
TheRock
  main: users/sareeder/install-latest-rocm [2 modified]
  consumption: users/sareeder/hipdnn-consumption-tests [clean]
  miopen-plugin: users/sareeder/miopen-plugin-move [1 modified]

rocm-libraries: main [clean]
mlse-tools-internal: main [clean]
dnn-benchmarking: main [clean]
```

## Architecture

```
ROCm-workspace/
├── CLAUDE.md                    # Hub instructions (minimal, ~335 tokens)
├── .claude/
│   ├── commands/                # /goto, /status, /worktrees, /task, /wip, /squash-prep
│   ├── skills/                  # Auto-triggered skills and workflow templates
│   │   ├── pr-summary, review-pr -> ../../.shared/skills/*
│   │   ├── hipdnn-* -> ../../.shared/skills/hipdnn-*
│   │   └── descriptor-* / orchestrate templates
│   ├── hooks/
│   │   └── worktree-guard.md    # Prevent cross-contamination
│   └── registry/
│       └── projects.json        # Project metadata and paths
├── .beads/                      # Local issue tracker (gitignored)
│   ├── beads.db                 # SQLite database
│   ├── issues.jsonl             # JSONL export
│   └── config.yaml              # beads_rust config
├── docs/                        # Reference documentation (tier 4)
│   ├── README.md
│   └── python-style-guide.md    # Python coding standards
├── workflows/                   # Repeatable procedures (tier 4)
│   ├── README.md
│   └── debugging-tips.md        # CMake, ROCm, Python debugging
└── README.md                    # This file
```

## Skills (Automatic)

Skills activate automatically based on conversation context:

| Skill | Activates When |
|-------|----------------|
| `pr-summary` | You draft, revise, or create PR text |
| `review-pr` | You review a branch or pull request |
| `hipdnn-review` | You review hipDNN changes |
| `hipdnn-superbuild` | You build hipDNN through the superbuild |
| `hipdnn-superbuild-test` | You test an existing hipDNN superbuild |

## Commands

| Command | Description |
|---------|-------------|
| `/goto <project> [worktree]` | Navigate to project and load its context |
| `/status` | Show git status across all projects |
| `/worktrees [project]` | List/manage worktrees |
| `/task <list\|ready\|create\|show\|close\|update\|q>` | Issue tracker (beads_rust) |
| `/wip [description]` | Quick WIP commit in current project |
| `/squash-prep [project] [base]` | Suggest squash strategy for clean history |

## Context Management

The workspace uses tiered context loading to minimize token usage:

1. **Hub CLAUDE.md** (~335 tokens) - Always loaded
2. **Project CLAUDE.md** (~1500 tokens) - Loaded when project detected
3. **Skills** (~500 tokens each) - Loaded by conversation triggers
4. **Deep docs** (`docs/`, `workflows/`) - Read on demand, never auto-loaded

## Requirements

- Claude Code CLI
- `git` with access to each registry remote
- Optional existing project paths from `registry/projects.json`; on a new machine, run `python3 scripts/bootstrap_repos.py` to populate workspace-local `repos/` and `worktrees/`.

## Customization

Edit `.claude/registry/projects.json` to:
- Add new projects
- Update worktree paths
- Add project aliases for detection
- Modify build/venv patterns

## License

This workspace configuration is part of ROCm development workflow.
