#!/bin/bash
# Build and test all hipdnn dnn-providers standalone.
# Run from the root of a rocm-libraries worktree, e.g.:
#   cd /home/AMD/sareeder/worktrees/rocmlibs-plugin-sdk-flatbuffers
#   /home/AMD/sareeder/ROCm-workspace/scripts/build_and_test_providers.sh
#
# Usage: build_and_test_providers.sh [--build-only]

set -euo pipefail

WORKTREE_ROOT="$(pwd)"
HIPDNN_BUILD_DIR="${WORKTREE_ROOT}/projects/hipdnn/build"
LOCAL_INSTALL="${HIPDNN_BUILD_DIR}/local_install"
PROVIDERS_DIR="${WORKTREE_ROOT}/dnn-providers"
BUILD_ONLY="${1:-}"

if [[ ! -d "${HIPDNN_BUILD_DIR}" ]]; then
    echo "ERROR: hipdnn build dir not found at ${HIPDNN_BUILD_DIR}"
    echo "Make sure you're running from the root of a rocm-libraries worktree with a configured hipdnn build."
    exit 1
fi

CMAKE_SDK_FLAGS=(
    "-Dhipdnn_plugin_sdk_DIR=${LOCAL_INSTALL}/lib/cmake/hipdnn_plugin_sdk"
    "-Dhipdnn_data_sdk_DIR=${LOCAL_INSTALL}/lib/cmake/hipdnn_data_sdk"
    "-Dhipdnn_flatbuffers_sdk_DIR=${LOCAL_INSTALL}/lib/cmake/hipdnn_flatbuffers_sdk"
    "-DCMAKE_PREFIX_PATH=/opt/rocm"
    "-DCMAKE_BUILD_TYPE=Release"
)

PROVIDERS=(hip-kernel-provider miopen-provider hipblaslt-provider fusilli-provider)
declare -A RESULTS

build_and_test_provider() {
    local name="$1"
    local src="${PROVIDERS_DIR}/${name}"
    local bld="${src}/build"

    echo ""
    echo "========================================"
    echo " ${name}"
    echo "========================================"

    if [[ ! -d "${src}" ]]; then
        echo "SKIP: source directory not found"
        RESULTS[$name]="SKIP (no source)"
        return
    fi

    # Configure
    echo "[cmake] Configuring..."
    if ! cmake -S "${src}" -B "${bld}" -G Ninja \
        "${CMAKE_SDK_FLAGS[@]}" \
        -DCMAKE_INSTALL_PREFIX="${bld}/install" \
        2>&1; then
        echo "SKIP: cmake configure failed (likely missing dependencies)"
        RESULTS[$name]="SKIP (configure failed)"
        return
    fi

    # Build
    echo "[ninja] Building..."
    if ! ninja -C "${bld}" 2>&1; then
        echo "FAIL: build failed"
        RESULTS[$name]="FAIL (build)"
        return
    fi

    if [[ "${BUILD_ONLY}" == "--build-only" ]]; then
        RESULTS[$name]="BUILD OK (tests skipped)"
        return
    fi

    # Test
    echo "[ninja] Running tests..."
    if ninja -C "${bld}" check 2>&1; then
        RESULTS[$name]="PASS"
    else
        RESULTS[$name]="FAIL (tests)"
    fi
}

for provider in "${PROVIDERS[@]}"; do
    build_and_test_provider "${provider}"
done

echo ""
echo "========================================"
echo " Summary"
echo "========================================"
for provider in "${PROVIDERS[@]}"; do
    printf "  %-30s %s\n" "${provider}" "${RESULTS[$provider]}"
done
echo ""
