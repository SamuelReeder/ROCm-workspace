#!/usr/bin/env bash
# Build the dnn-benchmarking image and run its pytest suite on the GPU.
#
# The Dockerfile clones rocm-libraries from a git URL. To build an unpushed
# local branch (or to build fully offline), this script serves the local clone
# over a throwaway `git daemon` and points the build at it via build args. To
# build from GitHub instead, skip this script and run, e.g.:
#
#   docker build -t dnn-benchmarking \
#     --build-arg ROCM_LIBRARIES_REF=<branch> docker/dnn-benchmarking
#
set -euo pipefail

IMAGE="${IMAGE:-dnn-benchmarking}"
GPU_ARCH="${GPU_ARCH:-gfx90a}"
PORT="${PORT:-9418}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REPO_DIR="$WORKSPACE_ROOT/repos/rocm-libraries"

if [ ! -d "$REPO_DIR/.git" ]; then
    echo "ERROR: local rocm-libraries clone not found at $REPO_DIR" >&2
    exit 1
fi

REF="$(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD)"
echo ">> Serving $REPO_DIR (branch $REF) over git daemon on port $PORT"

# Allow partial (blob-filtered) clones from the served repo.
git -C "$REPO_DIR" config uploadpack.allowFilter true
git -C "$REPO_DIR" config uploadpack.allowAnySHA1InWant true

git daemon --reuseaddr --base-path="$WORKSPACE_ROOT/repos" --export-all \
    --enable=upload-pack --listen=0.0.0.0 --port="$PORT" --detach
cleanup() {
    # `git daemon --detach` reparents to init and execs to argv[0] "git-daemon";
    # match that name so the listener we started is reliably stopped.
    pkill -f "git-daemon .*--port=$PORT" 2>/dev/null || true
}
trap cleanup EXIT
sleep 1

echo ">> Building image $IMAGE (arch $GPU_ARCH)"
DOCKER_BUILDKIT=1 docker build --network=host -t "$IMAGE" \
    --build-arg ROCM_LIBRARIES_REPO="git://127.0.0.1:$PORT/rocm-libraries" \
    --build-arg ROCM_LIBRARIES_REF="$REF" \
    --build-arg GPU_ARCH="$GPU_ARCH" \
    "$SCRIPT_DIR"

echo ">> Running pytest suite on GPU"
docker run --rm \
    --privileged --device=/dev/kfd --device=/dev/dri \
    "$IMAGE" "$@"
