# Alola Cluster

Alola login nodes (`ctr2-alola-login-03`, `ctr2-alola-login-04`) share the same NFS home directory and project paths. Teams agents are hosted on HPE by default; Alola is the durable execution backend for ROCm builds, tests, benchmarks, GPU runtime checks, and provider verification.

## Controller model

- The Teams harness process stays local to the HPE controller (`hpe-sjc2-43`).
- Agents use `workspace/scripts/alola-session` to run commands through persistent remote tmux sessions.
- The persistence boundary is the Alola login-node tmux session, not the HPE process/container.
- If an HPE bot/container restarts, the session manager can rediscover an existing tmux session or reacquire a GPU allocation.

## Default targets

- Plain build/test/runtime work should use the default login-node enroot target: node `03`, ASIC `gfx90a`, container `sareeder-latest_container`.
- A named ASIC such as `gfx942` or `gfx950` requests a non-exclusive SLURM GPU allocation.
- GPU image names follow `/cluster/images/hipdnn/hipdnn_latest_<asic>.sqsh`.
- GPU constraints default to `MARKHAM&<ASIC_UPPER>` so work lands on Markham nodes with the expected `/home/AMD/sareeder/...` worktrees.

## Session CLI

Run from the workspace checkout on HPE:

```bash
# Default login-node enroot session (node 03, gfx90a)
workspace/scripts/alola-session run -- hostname

# Specific login node
workspace/scripts/alola-session run --target 04 -- 'hostname && pwd'

# Non-exclusive GPU allocation by ASIC
workspace/scripts/alola-session run --target gfx942 -- 'rocminfo | grep -m1 gfx942'

# Force compute-node allocation for gfx90a
workspace/scripts/alola-session run --target gpu:gfx90a -- 'rocminfo | grep -m1 gfx90a'

# Start/status/stop without running a command
workspace/scripts/alola-session start --target gfx942
workspace/scripts/alola-session status --target gfx942
workspace/scripts/alola-session stop --target gfx942

# Print a human attach command
workspace/scripts/alola-session attach --target gfx942
```

Commands are written to `~/.teams-agent/commands/<id>.sh` and then invoked through `tmux send-keys`; arbitrary command text is not quoted directly into `send-keys`.

## SSH authentication

Production/HPE use is key-based. Mount or provide a key and use batch-mode SSH:

```bash
export ALOLA_USER=sareeder
export ALOLA_SSH_KEY=/run/secrets/alola_ssh_key
export ALOLA_SSH_OPTIONS='-o BatchMode=yes -o StrictHostKeyChecking=yes'
workspace/scripts/ssh/ssh-alola.sh 03 hostname
```

The helper does not contain a password fallback. `sshpass` can only be enabled explicitly with `ALOLA_ALLOW_SSHPASS=1` and `ALOLA_PASSWORD` for temporary local compatibility.

## First steps inside a session

```bash
bash ~/ROCm-workspace/scripts/ssh/detect-env.sh
hostname
pwd
command -v hipcc
```

The detect script reports GPU type, whether the shell is inside enroot, available containers, ROCm version, and accessible project paths.

## Build/test examples

```bash
# rocm-libraries / hipDNN on default login-node enroot session
workspace/scripts/alola-session run -- \
  'cd /home/AMD/sareeder/full/rocm-libraries && cmake -B build -G Ninja && ninja -C build hipdnn && ctest --test-dir build -R hipdnn --output-on-failure'

# TheRock for a specific ASIC allocation
workspace/scripts/alola-session run --target gfx942 -- \
  'cd /home/AMD/sareeder/TheRock && python3 fetch_sources.py && cmake -B build -G Ninja -DTHEROCK_AMDGPU_TARGETS=gfx942 && ninja -C build'
```

## Key paths

| Path | Project |
|------|---------|
| `/home/AMD/sareeder/TheRock` | TheRock superbuild |
| `/home/AMD/sareeder/full/rocm-libraries` | rocm-libraries |
| `/home/AMD/sareeder/mlse-tools-internal` | mlse-tools |
| `/home/AMD/sareeder/dnn-benchmarking` | dnn-benchmarking |

## Cleanup

```bash
# Stop a managed session and release matching SLURM jobs
workspace/scripts/alola-session stop --target gfx942

# Manual emergency cleanup on a login node
ssh ctr2-alola-login-03 'tmux list-sessions'
ssh ctr2-alola-login-03 'tmux kill-session -t <session>'
ssh ctr2-alola-login-03 'scancel -u sareeder -n <session>'
```

Login-node sessions are cheap to keep around. GPU sessions rely on SLURM `--time` for hard timeout and are reacquired automatically by the next command using the same target if the allocation expired.
