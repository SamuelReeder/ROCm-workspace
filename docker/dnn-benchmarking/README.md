# Running dnn-benchmarking on a bare image

Set up `dnn-benchmarking` (hipDNN + provider plugins + ROCm PyTorch) on a clean
Ubuntu 24.04 image and run its test suite. Two equivalent paths:

- **Docker** — one build, fully reproducible (see [`Dockerfile`](./Dockerfile)).
- **Manual** — the same steps run by hand in a bare Ubuntu 24.04 shell.

Both install nothing from a system ROCm: ROCm is supplied entirely by the ROCm
PyTorch nightly wheel's bundled SDK, and `setup.sh` compiles hipDNN and the
provider plugins against it.

## Requirements

- Ubuntu 24.04 (ships Python 3.12 as `python3`).
- Network access (pulls the torch nightly + ROCm SDK wheels, ~2 GB).
- An AMD GPU with `/dev/kfd` + `/dev/dri` **to run the tests**. Build/setup needs
  no GPU.

## GPU architecture

Setup needs the GPU arch up front, because a bare image has no ROCm detection
tools (`rocm_agent_enumerator`/`rocminfo`) to discover it. Pass it via
`--gpu-arch`; `setup.sh` derives everything else (the torch nightly bucket and
the HIP `GPU_TARGETS` offload target) from it. Pick the value for your card:

| GPU | `--gpu-arch` |
|-----|--------------|
| MI200/MI210/MI250 | `gfx90a` |
| MI300X/MI300A     | `gfx942` |
| MI350             | `gfx950` |

The rest of this doc uses **gfx90a (MI210)**; substitute your value.

---

## Option A — Docker

Build, then run the suite with the GPU mounted:

```bash
# Build (override REF for a branch; defaults to the public repo)
docker build -t dnn-benchmarking \
  --build-arg GPU_ARCH=gfx90a \
  --build-arg ROCM_LIBRARIES_REF=develop \
  docker/dnn-benchmarking

# Run the ROCm test suite (unit + GPU-generic + rocm; cuda-only deselected)
docker run --rm --privileged --device=/dev/kfd --device=/dev/dri \
  dnn-benchmarking
```

Other commands run the same way (the entrypoint activates the venv and `cd`s into
the tool directory):

```bash
docker run --rm --privileged --device=/dev/kfd --device=/dev/dri \
  dnn-benchmarking pytest -m rocm -q
docker run --rm -it --privileged --device=/dev/kfd --device=/dev/dri \
  dnn-benchmarking bash
```

To build an unpushed local branch (or fully offline), use
[`build_and_test.sh`](./build_and_test.sh), which serves your local clone over a
throwaway `git daemon` and then builds + runs:

```bash
bash docker/dnn-benchmarking/build_and_test.sh                 # default suite
bash docker/dnn-benchmarking/build_and_test.sh pytest -m rocm  # any pytest args
```

---

## Option B — Manual

Run these in a bare Ubuntu 24.04 shell (as root). Each step maps 1:1 to the
Dockerfile.

```bash
# 1. Toolchain (git + Python venv/pip + a C++/HIP build toolchain)
apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv python3-dev python3-pip \
    git ca-certificates cmake ninja-build build-essential pkg-config \
    libnuma-dev libatomic1

# 2. Clone only the subtrees setup.sh builds (sparse, shallow)
cd /opt
git clone --depth 1 --filter=blob:none --sparse \
    --branch develop https://github.com/ROCm/rocm-libraries.git rocm-libraries
git -C rocm-libraries sparse-checkout set projects/hipdnn dnn-providers

# 3. Run setup: installs the ROCm torch nightly, builds hipDNN + the three
#    provider plugins + the hipDNN Python bindings against the bundled ROCm SDK.
#    --gpu-arch is the only input: setup.sh derives the HIP offload target from
#    it (no GPU_TARGETS / ROCM_SDK_TARGET_FAMILY env needed) and its torch-mode
#    probe tolerates the GPU-less `import torch` warning.
mkdir -p /workspace
cd /opt/rocm-libraries/projects/hipdnn/tools/dnn-benchmarking
bash setup.sh --workspace /workspace --gpu-arch gfx90a -y
```

Then activate and run the tests (GPU required here):

```bash
# 4. Activate the venv. activate.local (written by setup.sh) exports ROCM_PATH,
#    the libraries-prefix LD_LIBRARY_PATH, and DNN_BENCH_WORKSPACE -- no manual
#    env is needed, and the bindings preload the HIP runtime through rocm_sdk.
source /workspace/.venv/bin/activate

# 5. Run the suite (cuda-only tests deselected)
pytest -m "not cuda"
```

---

## Notes on `--gpu-arch`

`setup.sh` is normally run on a configured ROCm host, where it autodetects the
GPU and its offload arch. A bare image (and `docker build` with no GPU) has
neither the detection tools nor a GPU, so you state the arch once with
`--gpu-arch`. From it `setup.sh`:

- picks the ROCm torch nightly bucket, and
- passes the HIP offload target to the hipDNN/provider builds as `-DGPU_TARGETS`,
  so HIP does not fall back to a default target list.

Its torch-mode probe reads only the final output line, so the GPU-less
`import torch` SDK warning no longer needs suppressing (the former
`ROCM_SDK_TARGET_FAMILY` workaround is gone).

Nothing extra is needed at runtime either: the Dockerfile sets no ROCm env and
no `LD_LIBRARY_PATH`. Activating the `setup.sh`-created venv exports `ROCM_PATH`,
the libraries-prefix `LD_LIBRARY_PATH`, and `DNN_BENCH_WORKSPACE`, and the hipDNN
bindings preload the HIP runtime via `rocm_sdk`.
