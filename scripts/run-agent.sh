#!/bin/bash
# Run a Claude agent inside an enroot container
# Usage: echo "prompt" | ./run-agent.sh <container> <session-id> [--resume] [extra claude args...]
#
# The prompt is read from stdin to avoid shell quoting issues.
# The routing context and workspace are already available via git pull.
#
# Examples:
#   echo "build hipDNN" | ./run-agent.sh claude-abc12345 abc-uuid --model opus
#   echo "now run tests" | ./run-agent.sh claude-abc12345 abc-uuid --resume

set -e

CONTAINER="$1"
SESSION_ID="$2"
shift 2

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONTEXT_FILE="$SCRIPT_DIR/.claude/routing-context.md"

# Read prompt from stdin
PROMPT="$(cat)"

if [ -z "$CONTAINER" ] || [ -z "$SESSION_ID" ] || [ -z "$PROMPT" ]; then
    echo "Usage: echo 'prompt' | $0 <container> <session-id> [--resume] [extra args...]" >&2
    exit 1
fi

# Source Claude environment (API keys, proxy config)
ENV_FILE="$HOME/.config/claude-code/env.sh"
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi

# Ensure we're in the workspace
cd "$SCRIPT_DIR"

# Build claude args
CLAUDE_ARGS=(--print --dangerously-skip-permissions)

# Check for --resume flag
RESUME=false
EXTRA_ARGS=()
for arg in "$@"; do
    if [ "$arg" = "--resume" ]; then
        RESUME=true
    else
        EXTRA_ARGS+=("$arg")
    fi
done

if [ "$RESUME" = true ]; then
    CLAUDE_ARGS+=(--resume "$SESSION_ID")
else
    CLAUDE_ARGS+=(--session-id "$SESSION_ID")
    if [ -f "$CONTEXT_FILE" ]; then
        CLAUDE_ARGS+=(--append-system-prompt-file "$CONTEXT_FILE")
    fi
fi

CLAUDE_ARGS+=("${EXTRA_ARGS[@]}")
CLAUDE_ARGS+=(-p "$PROMPT")

# Run inside enroot container
# Pass Claude env vars into the container since enroot starts a fresh shell
enroot start --rw --mount "$HOME:$HOME" "$CONTAINER" -- \
    bash -c "source '$ENV_FILE' 2>/dev/null; cd ~/ROCm-workspace && claude $(printf '%q ' "${CLAUDE_ARGS[@]}")"
