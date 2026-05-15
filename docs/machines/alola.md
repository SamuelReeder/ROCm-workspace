# Alola Cluster

All Alola login nodes (ctr2-alola-login-03, -04, etc.) share the same NFS home directory, project paths, and environment.

## First Steps

Always run the environment detection script first:

```bash
bash scripts/ssh/detect-env.sh
```

This tells you: GPU type, whether you're inside an enroot container, available containers, ROCm version, and accessible project paths.

## Enroot Containers

Builds and tests must run inside an enroot container — the login node itself lacks the ROCm stack.

```bash
# List available containers
enroot list

# Start an existing container (interactive shell)
enroot start sareeder-latest

# If already inside enroot (IN_ENROOT=yes from detect-env.sh), skip this step
```

The `sareeder-latest` container has the ROCm toolchain, compilers, and libraries needed to build and test.

## Building Inside the Container

Once inside the container:

```bash
# TheRock
cd /home/AMD/sareeder/TheRock
python3 fetch_sources.py
cmake -B build -G Ninja -DTHEROCK_AMDGPU_TARGETS="gfx90a"
ninja -C build

# rocm-libraries (hipDNN example)
cd /home/AMD/sareeder/full/rocm-libraries
cmake -B build -G Ninja
ninja -C build hipdnn
ctest --test-dir build -R hipdnn
```

Adjust `THEROCK_AMDGPU_TARGETS` based on the GPU detected by `detect-env.sh` (e.g., `gfx90a`, `gfx942`).

## Running Tests

```bash
# From inside the container, in the build directory
ctest --test-dir build -R <test-pattern> --output-on-failure
```

## SSH from WSL

When working remotely from WSL via the Teams bot:

```bash
# Run a single command
scripts/ssh/ssh-alola.sh 03 "command here"

# Run detect-env remotely
scripts/ssh/ssh-alola.sh 03 "bash ~/ROCm-workspace/scripts/ssh/detect-env.sh"

# Run inside enroot remotely
scripts/ssh/ssh-alola.sh 03 "enroot start sareeder-latest -- bash -c 'cd /home/AMD/sareeder/TheRock && ninja -C build'"
```

## Key Paths

All the same as WSL (`/home/AMD/sareeder/...`), accessed via NFS:

| Path | Project |
|------|---------|
| `/home/AMD/sareeder/TheRock` | TheRock superbuild |
| `/home/AMD/sareeder/full/rocm-libraries` | rocm-libraries |
| `/home/AMD/sareeder/mlse-tools-internal` | mlse-tools |
| `/home/AMD/sareeder/dnn-benchmarking` | dnn-benchmarking |

## Notes

- The login node is for scheduling and light work — heavy builds go in enroot
- GPU resources may be shared with other users — check `rocm-smi` before launching large jobs
- The container shares the home directory mount, so file changes persist outside the container
