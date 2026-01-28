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
ninja -C ~/therock-consumption/build hipDNN+build  # Incremental build
ninja -C ~/TheRock/build miopen+expunge            # Clean rebuild
```

**rocm-libraries:**
```bash
ninja -C ~/full/rocm-libraries/build check         # Run tests
ninja -C ~/full/rocm-libraries/build format        # Format code
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
        ninja -C ~/TheRock/build composable_kernel
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
├── CLAUDE.md                    # Hub instructions (minimal)
├── .claude/
│   ├── commands/                # /goto, /status, /worktrees
│   ├── skills/                  # Auto-triggered based on context
│   │   ├── project-router/      # Detect project from conversation
│   │   ├── cmake-build/         # CMake/Ninja patterns
│   │   ├── python-dev/          # Venv/pytest patterns
│   │   └── worktree-setup/      # Auto-setup new worktrees
│   ├── hooks/
│   │   └── worktree-guard.md    # Prevent cross-contamination
│   └── registry/
│       └── projects.json        # Project metadata and paths
└── README.md                    # This file
```

## Skills (Automatic)

Skills activate automatically based on conversation context:

| Skill | Activates When |
|-------|----------------|
| `project-router` | You mention project/library/worktree names |
| `cmake-build` | You ask to build, compile, run ninja |
| `python-dev` | You mention pytest, pip, venv, Python work |
| `worktree-setup` | You create/enter worktree without setup |

## Context Management

The workspace uses tiered context loading to minimize token usage:

1. **Hub CLAUDE.md** (~300 tokens) - Always loaded
2. **Project CLAUDE.md** (~1500 tokens) - Loaded when project detected
3. **Skills** (~500 tokens each) - Loaded by conversation triggers
4. **Deep docs** - Read by agent subprocesses, not main context

## Requirements

- Claude Code CLI
- Projects must exist at the paths specified in `registry/projects.json`
- For TheRock worktrees: paths follow pattern `~/<project>-<worktree-name>`

## Customization

Edit `.claude/registry/projects.json` to:
- Add new projects
- Update worktree paths
- Add project aliases for detection
- Modify build/venv patterns

## License

This workspace configuration is part of ROCm development workflow.
