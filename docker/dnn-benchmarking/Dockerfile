# syntax=docker/dockerfile:1

# Bare Ubuntu 24.04 ships Python 3.12 as the default `python3`. We add only the
# toolchain setup.sh needs to clone the repo and compile hipDNN + the provider
# plugins from source; ROCm itself is supplied entirely by the ROCm PyTorch
# nightly wheel's bundled SDK (no system /opt/rocm required).
FROM ubuntu:24.04

# Source selection. Defaults to the public monorepo; override REF (and REPO for
# an offline mirror) to build a specific branch. GPU_ARCH selects the ROCm torch
# nightly bucket and pins device-code offload codegen so the build needs no GPU.
ARG ROCM_LIBRARIES_REPO=https://github.com/ROCm/rocm-libraries.git
ARG ROCM_LIBRARIES_REF=develop
ARG GPU_ARCH=gfx90a

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-venv python3-dev python3-pip \
        git ca-certificates \
        cmake ninja-build build-essential pkg-config \
        libnuma-dev libatomic1 \
    && rm -rf /var/lib/apt/lists/*

# Sparse, shallow clone of only the subtrees setup.sh builds:
#   projects/hipdnn  -> hipDNN, its Python bindings, and the dnn-benchmarking tool
#   dnn-providers    -> miopen / hipblaslt / hip-kernel plugins + their shared cmake
# Everything else in the 9GB monorepo is skipped via blob filtering.
WORKDIR /opt
# Cache-bust the clone whenever the target ref advances. The instruction text of
# the `git clone` below never changes, so BuildKit would otherwise reuse a stale
# checkout after develop moves (e.g. a new merge), silently building old sources.
# This GitHub API payload changes with every new commit on ${ROCM_LIBRARIES_REF},
# so the clone layer is reused only while the ref HEAD is unchanged and re-cloned
# the moment it moves. Assumes the default GitHub repo; pass --no-cache when
# building from an overridden offline ROCM_LIBRARIES_REPO mirror.
ADD https://api.github.com/repos/ROCm/rocm-libraries/commits/${ROCM_LIBRARIES_REF} /tmp/rocm-libraries-ref.json
RUN git clone --depth 1 --filter=blob:none --sparse \
        --branch "${ROCM_LIBRARIES_REF}" "${ROCM_LIBRARIES_REPO}" rocm-libraries \
    && git -C rocm-libraries sparse-checkout set projects/hipdnn dnn-providers

# setup.sh prefers /workspace when it exists and is writable; create it so the
# venv, bytecode cache, and benchmark caches land at a stable, known path.
RUN mkdir -p /workspace

WORKDIR /opt/rocm-libraries/projects/hipdnn/tools/dnn-benchmarking

# Full ROCm PyTorch setup, driven entirely by --gpu-arch: install the ROCm torch
# nightly for GPU_ARCH, discover the bundled ROCm SDK, and build+install hipDNN,
# the three provider plugins, and the hipDNN Python bindings against it. -y skips
# the prompt.
#
# No offload env vars or GPU-discovery shims are needed on this GPU-less build
# host: setup.sh derives the HIP offload target from --gpu-arch and passes it to
# the hipDNN/provider cmake builds (-DGPU_TARGETS), and its torch-mode probe
# tolerates the GPU-less `import torch` warning. --gpu-arch is the only input.
RUN --mount=type=cache,target=/root/.cache/pip \
    bash setup.sh --workspace /workspace --gpu-arch "${GPU_ARCH}" -y

# Inlined entrypoint (keeps this a single self-contained Dockerfile): activate the
# setup.sh-created venv -- activate.local exports ROCM_PATH, the libraries-prefix
# LD_LIBRARY_PATH, and DNN_BENCH_WORKSPACE -- then exec the requested command from
# the tool dir. No runtime ROCm env is set here; the bindings preload the HIP
# runtime via rocm_sdk.
RUN printf '%s\n' \
        '#!/usr/bin/env bash' \
        'set -euo pipefail' \
        'source /workspace/.venv/bin/activate' \
        'cd /opt/rocm-libraries/projects/hipdnn/tools/dnn-benchmarking' \
        'exec "$@"' \
        > /usr/local/bin/entrypoint.sh \
    && chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
# Default: run the dnn-benchmarking suite that applies on a ROCm host
# (unit + GPU-generic + rocm-only; cuda-only tests are dropped).
CMD ["pytest", "-m", "not cuda"]
