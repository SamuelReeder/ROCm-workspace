# Repository Setup

This page tells you how to bootstrap project clones and worktrees in this
workspace. Most agents do not need this page: it applies only when you set
up a new clone or worktree, not during normal task work.

## Bootstrap script

`scripts/bootstrap_repos.py` discovers and clones repositories under
`repos/`, and creates worktrees under `worktrees/<project>/<branch-suffix>/`.

Run bootstrap with no arguments to sync existing clones:

```bash
python3 scripts/bootstrap_repos.py
```

Create a worktree for a branch:

```bash
python3 scripts/bootstrap_repos.py --project rocm-libraries --worktree rocm-libraries users/sareeder/feature-x
```

## Rules

- Bootstrap discovers existing git repositories under `repos/`; clone new
  repositories there manually when needed.
- Workspace worktree branches must use the `users/sareeder/` prefix. The
  directory uses only the suffix: `users/sareeder/feature-x` becomes
  `feature-x`.
- Fetch the source clone before creating a fresh worktree from a moving base
  branch.
