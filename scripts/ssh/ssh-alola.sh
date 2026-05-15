#!/bin/bash
# Run a command on any alola login node via SSH
# Usage: ./ssh-alola.sh <node> "<command>"
#   e.g. ./ssh-alola.sh 03 "hostname"
#   e.g. ./ssh-alola.sh 04 "rocm-smi"
# Or without a command to get an interactive shell:
#   ./ssh-alola.sh 03

NODE="${1:?Usage: ssh-alola.sh <node-number> [command...]}"
shift
source ~/.bashrc 2>/dev/null
sshpass -p "Idiomswerelit1!" ssh -o StrictHostKeyChecking=no "sareeder@ctr2-alola-login-${NODE}" "$@"
