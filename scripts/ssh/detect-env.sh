#!/bin/bash
# Detect the current machine environment
# Outputs key=value pairs for agent consumption
# Run directly on the machine (not via SSH)

echo "HOSTNAME=$(hostname)"
echo "USER=$USER"
echo "HOME=$HOME"
DEFAULT_LOGIN_CONTAINER="${ALOLA_DEFAULT_LOGIN_CONTAINER:-sareeder-latest_container}"
echo "ENROOT_DEFAULT_LOGIN_CONTAINER=$DEFAULT_LOGIN_CONTAINER"
echo "ENROOT_CONTAINER_SCOPE=node-local_rootfs"
echo "ENROOT_SHARED_IMAGE_DIR=/cluster/images/hipdnn"

# Enroot container rootfses listed by `enroot list` are node-local under
# /var/tmp/<uid>/enroot-data. Shared images live under /cluster/images/hipdnn
# and can be used to recreate a missing node-local rootfs.
if [ -f /etc/enroot ]; then
  echo "IN_ENROOT=yes"
  echo "ENROOT_NAME=$(cat /etc/enroot 2>/dev/null || echo unknown)"
else
  echo "IN_ENROOT=no"
  CONTAINERS=$(enroot list 2>/dev/null | tr '\n' ',' | sed 's/,$//')
  echo "ENROOT_CONTAINERS=${CONTAINERS:-none}"
fi

# GPU detection
GPU=$(rocm-smi --showproductname 2>/dev/null | grep -oP 'gfx\w+' | head -1)
if [ -n "$GPU" ]; then
  echo "GPU=$GPU"
  echo "GPU_COUNT=$(rocm-smi -l 2>/dev/null | grep -c 'GPU')"
else
  echo "GPU=none"
  echo "GPU_COUNT=0"
fi

# ROCm version
if command -v rocminfo &>/dev/null; then
  ROCM_VER=$(rocminfo 2>/dev/null | grep -oP 'HSA Runtime Version:\s+\K[\d.]+' | head -1)
  echo "ROCM_VERSION=${ROCM_VER:-unknown}"
fi

# Check common paths
echo "HAS_THEROCK=$(test -d /home/AMD/$USER/TheRock && echo yes || echo no)"
echo "HAS_ROCMLIBS=$(test -d /home/AMD/$USER/full/rocm-libraries && echo yes || echo no)"
