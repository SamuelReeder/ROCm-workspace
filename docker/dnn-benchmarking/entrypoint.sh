#!/usr/bin/env bash
# Activate the setup.sh-created venv (which sources activate.local to export
# ROCM_PATH and prepend the bundled ROCm libs to LD_LIBRARY_PATH), then exec the
# requested command from the dnn-benchmarking directory. Default command runs the
# pytest suite; override by passing any command, e.g. `docker run ... bash`.
set -euo pipefail

# shellcheck disable=SC1091
source /workspace/.venv/bin/activate
cd /opt/rocm-libraries/projects/hipdnn/tools/dnn-benchmarking

exec "$@"
