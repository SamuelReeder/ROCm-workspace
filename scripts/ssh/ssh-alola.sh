#!/usr/bin/env bash
set -euo pipefail

# Run a command on an Alola login node via SSH.
# Usage: scripts/ssh/ssh-alola.sh <node-number> [command...]
# Production/HPE use is key-based:
#   ALOLA_SSH_KEY=/run/secrets/alola_ssh_key scripts/ssh/ssh-alola.sh 03 hostname

NODE="${1:?Usage: ssh-alola.sh <node-number> [command...]}"
shift || true

case "$NODE" in
  [0-9]) NODE="0${NODE}" ;;
  [0-9][0-9]) ;;
  *) echo "Invalid Alola node '$NODE'" >&2; exit 2 ;;
esac

ALOLA_USER="${ALOLA_USER:-sareeder}"
HOST="ctr2-alola-login-${NODE}"
DEFAULT_OPTIONS="-o BatchMode=yes -o StrictHostKeyChecking=yes"
# shellcheck disable=SC2206
SSH_OPTIONS=(${ALOLA_SSH_OPTIONS:-$DEFAULT_OPTIONS})
SSH_ARGS=("${SSH_OPTIONS[@]}")

if [ -n "${ALOLA_SSH_KEY:-}" ]; then
  SSH_ARGS=("-i" "$ALOLA_SSH_KEY" "${SSH_ARGS[@]}")
fi

if [ "${ALOLA_ALLOW_SSHPASS:-0}" = "1" ]; then
  if [ -z "${ALOLA_PASSWORD:-}" ]; then
    echo "ALOLA_ALLOW_SSHPASS=1 requires ALOLA_PASSWORD; hardcoded passwords are not supported" >&2
    exit 2
  fi
  exec sshpass -p "$ALOLA_PASSWORD" ssh "${SSH_ARGS[@]}" "${ALOLA_USER}@${HOST}" "$@"
fi

exec ssh "${SSH_ARGS[@]}" "${ALOLA_USER}@${HOST}" "$@"
