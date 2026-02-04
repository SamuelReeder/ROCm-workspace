# ROCm Workspace Hub

Centralized dispatch workspace for ROCm development projects.

## Projects

| Project | Path | Type |
|---------|------|------|
| TheRock | ~/TheRock | CMake superbuild |
| rocm-libraries | ~/full/rocm-libraries | CMake superbuild |
| mlse-tools | ~/mlse-tools-internal | Python scripts |
| dnn-benchmarking | ~/dnn-benchmarking | Python package |

## TheRock Worktrees

| Name | Path | Branch |
|------|------|--------|
| main | ~/TheRock | users/sareeder/install-latest-rocm |
| consumption | ~/therock-consumption | users/sareeder/hipdnn-consumption-tests |
| miopen-plugin | ~/therock-miopen-plugin-move | users/sareeder/miopen-plugin-move |

## rocm-libraries Worktrees

| Name | Path | Branch |
|------|------|--------|
| main | ~/full/rocm-libraries | users/sareeder/detail-migration |

**To create a new rocm-libraries worktree for parallel work:**
```bash
cd ~/full/rocm-libraries
git worktree add ~/rocmlibs-<name> <branch>
# Example: git worktree add ~/rocmlibs-feature users/sareeder/new-feature
```

Each worktree is fully isolated with its own:
- `projects/hipdnn/build/` - hipDNN build artifacts
- `dnn-providers/*/build/` - Provider build artifacts
- Working directory state

## Navigation

- `/goto <project> [worktree]` - Navigate to project and load its context
- `/status` - Show git status across all projects
- `/worktrees [project]` - List/manage worktrees

## Project Detection

Mention project names, library names (hipDNN, MIOpen, rocBLAS), or worktree names in your prompt - the workspace will automatically detect and use the correct project context.

## Key Rules

1. **Worktree Isolation**: Each worktree has its own build/ and .venv - never cross-contaminate
2. **Absolute Paths**: Always use full paths to the correct worktree
3. **Project CLAUDE.md**: Each project has detailed instructions in its own CLAUDE.md
