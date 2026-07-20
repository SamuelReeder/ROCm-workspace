#!/usr/bin/env bash
# Build and test hipDNN with the supported provider plugins through the
# rocm-libraries superbuild. Run from any directory inside a rocm-libraries
# worktree, or from its root.
#
# Usage: build_and_test_providers.sh [--build-only] [--clean]
#   --build-only  Skip the component test targets after building
#   --clean       Remove the repository-root build directory before configuring

set -euo pipefail

WORKTREE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
BUILD_DIR="${WORKTREE_ROOT}/build"
BUILD_ONLY=0
CLEAN=0

for arg in "$@"; do
    case "$arg" in
        --build-only) BUILD_ONLY=1 ;;
        --clean) CLEAN=1 ;;
        *)
            echo "ERROR: unknown option: ${arg}" >&2
            exit 2
            ;;
    esac
done

if [[ ! -f "${WORKTREE_ROOT}/CMakePresets.json" ]]; then
    echo "ERROR: ${WORKTREE_ROOT} is not a rocm-libraries checkout" >&2
    exit 1
fi

if [[ "${CLEAN}" -eq 1 ]]; then
    echo "[clean] Removing ${BUILD_DIR}..."
    rm -rf "${BUILD_DIR}"
fi

cd "${WORKTREE_ROOT}"

echo "[cmake] Configuring hipDNN and supported providers..."
cmake --preset hipdnn-providers

echo "[ninja] Building hipDNN and supported providers..."
cmake --build "${BUILD_DIR}"

if [[ "${BUILD_ONLY}" -eq 1 ]]; then
    echo "[summary] Build completed; tests skipped"
    exit 0
fi

for target in hipdnn-check miopen-provider-check hipblaslt-provider-check; do
    echo "[test] Running ${target}..."
    cmake --build "${BUILD_DIR}" --target "${target}"
done

echo "[summary] hipDNN, MIOpen Provider, and hipBLASLt Provider passed"
