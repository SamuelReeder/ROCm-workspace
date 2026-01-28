---
description: Show git status overview of all managed ROCm projects
allowed-tools: [Bash, Read]
---

# ROCm Projects Status

Show git branch and status for all managed projects and worktrees.

## Process

1. Read project registry from `/home/AMD/sareeder/ROCm-workspace/.claude/registry/projects.json`

2. For each project, run:
   ```bash
   git -C <path> branch --show-current
   git -C <path> status --short | head -5
   ```

3. For projects with worktrees (TheRock), also check each worktree

## Output Format

```
TheRock
  main (~/TheRock): users/sareeder/install-latest-rocm
    [status: clean | N modified | N untracked]
  consumption (~/therock-consumption): users/sareeder/hipdnn-consumption-tests
    [status]
  miopen-plugin (~/therock-miopen-plugin-move): users/sareeder/miopen-plugin-move
    [status]

rocm-libraries (~/full/rocm-libraries): <branch>
  [status]

mlse-tools-internal (~/mlse-tools-internal): <branch>
  [status]

dnn-benchmarking (~/dnn-benchmarking): <branch>
  [status]
```

## Commands to Run

```bash
# TheRock main
git -C /home/AMD/sareeder/TheRock branch --show-current
git -C /home/AMD/sareeder/TheRock status --short | head -5

# TheRock consumption
git -C /home/AMD/sareeder/therock-consumption branch --show-current
git -C /home/AMD/sareeder/therock-consumption status --short | head -5

# TheRock miopen-plugin
git -C /home/AMD/sareeder/therock-miopen-plugin-move branch --show-current
git -C /home/AMD/sareeder/therock-miopen-plugin-move status --short | head -5

# rocm-libraries
git -C /home/AMD/sareeder/full/rocm-libraries branch --show-current
git -C /home/AMD/sareeder/full/rocm-libraries status --short | head -5

# mlse-tools-internal
git -C /home/AMD/sareeder/mlse-tools-internal branch --show-current
git -C /home/AMD/sareeder/mlse-tools-internal status --short | head -5

# dnn-benchmarking
git -C /home/AMD/sareeder/dnn-benchmarking branch --show-current
git -C /home/AMD/sareeder/dnn-benchmarking status --short | head -5
```
