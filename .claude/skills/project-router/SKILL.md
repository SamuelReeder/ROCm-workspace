---
name: project-router
description: Use this skill when the user mentions ROCm projects (TheRock, rocm-libraries, mlse-tools, dnn-benchmarking), library names (hipDNN, MIOpen, rocBLAS, composable_kernel, hipBLASLt), worktree names (consumption, miopen-plugin), or paths containing these projects. Also activates for ROCm/AMD GPU development, CMake superbuilds, or HIP/ROCm toolchain work.
version: 1.0.0
---

# Project Router

Automatically detect which ROCm project the user is referencing and load appropriate context.

## Project Detection Table

| Keywords | Project | Primary Path |
|----------|---------|--------------|
| TheRock, rock, superbuild, component+build, fetch_sources | therock | /home/AMD/sareeder/TheRock |
| consumption, hipdnn-consumption | therock (consumption worktree) | /home/AMD/sareeder/therock-consumption |
| miopen-plugin, plugin-move | therock (miopen-plugin worktree) | /home/AMD/sareeder/therock-miopen-plugin-move |
| rocm-libraries, libs, projects/hipdnn, projects/miopen, dnn-providers | rocm-libraries | /home/AMD/sareeder/full/rocm-libraries |
| hipDNN (outside TheRock context), hipdnn_frontend, hipdnn_backend | rocm-libraries | /home/AMD/sareeder/full/rocm-libraries |
| mlse-tools, mlse, alola, slurm, kubernetes, promote_ck, promote_miopen | mlse-tools | /home/AMD/sareeder/mlse-tools-internal |
| dnn-benchmarking, benchmark, --graph, A/B testing, perf | dnn-benchmarking | /home/AMD/sareeder/dnn-benchmarking |

## Worktree Detection Priority

When multiple matches possible, use this priority:
1. Explicit worktree name mentioned (e.g., "consumption") → that worktree
2. Recent context from conversation → maintain current worktree
3. Default to main repository

## Context Loading

When project is detected:

1. **Read project registry**: `/home/AMD/sareeder/ROCm-workspace/.claude/registry/projects.json`

2. **Read project CLAUDE.md** (if exists):
   - TheRock: `/home/AMD/sareeder/TheRock/CLAUDE.md`
   - rocm-libraries: `/home/AMD/sareeder/full/rocm-libraries/CLAUDE.md`
   - dnn-benchmarking: `/home/AMD/sareeder/dnn-benchmarking/CLAUDE.md`

3. **Set working context**:
   - All file paths should be absolute to the detected project
   - Build commands use project's build directory
   - Git operations target correct repository/worktree

## Path Patterns

Always use absolute paths:
```
/home/AMD/sareeder/TheRock/...
/home/AMD/sareeder/therock-consumption/...
/home/AMD/sareeder/therock-miopen-plugin-move/...
/home/AMD/sareeder/full/rocm-libraries/...
/home/AMD/sareeder/mlse-tools-internal/...
/home/AMD/sareeder/dnn-benchmarking/...
```

## Multi-Project Operations

If user mentions multiple projects, handle sequentially and clearly indicate which project each operation targets.
