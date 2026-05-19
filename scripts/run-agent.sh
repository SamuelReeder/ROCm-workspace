#!/bin/bash
# Run a harness agent inside an enroot container
# Usage: echo "prompt" | ./run-agent.sh <container> <session-id> [--resume] [extra harness args...]
#
# The prompt is read from stdin to avoid shell quoting issues.
# The routing context and workspace are already available via git pull.
#
# Examples:
#   echo "build hipDNN" | ./run-agent.sh harness-abc12345 abc-uuid --model opus
#   echo "now run tests" | ./run-agent.sh harness-abc12345 abc-uuid --resume

set -e

resolve_harness_bin() {
    local candidate
    local resolved
    local home="${HOME:-$(eval echo ~)}"

    for candidate in "${HARNESS_BIN}" "${OH_MY_PI_BIN}" "$home/.local/bin/oh-my-pi" \
                      "$home/.bun/bin/oh-my-pi" "$home/.bun/bin/omp" \
                      "$home/.local/bin/omp" "$home/.local/bin/claude" \
                      "oh-my-pi" "omp" "claude"; do
        [ -z "$candidate" ] && continue
        case "$candidate" in
            ~*) candidate="$home/${candidate#~}" ;;
        esac
        if [[ "$candidate" = /* ]]; then
            if [ -x "$candidate" ]; then
                resolved="$candidate"
                break
            fi
        else
            if command -v "$candidate" >/dev/null 2>&1; then
                resolved="$candidate"
                break
            fi
        fi
    done

    if [ -z "$resolved" ]; then
        echo "Harness binary not found. Set HARNESS_BIN." >&2
        exit 1
    fi

    echo "$resolved"
}

CONTAINER="$1"
SESSION_ID="$2"
shift 2 || true

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONTEXT_FILE="$SCRIPT_DIR/.claude/routing-context.md"

PROMPT="$(cat)"

if [ -z "$CONTAINER" ] || [ -z "$SESSION_ID" ] || [ -z "$PROMPT" ]; then
    echo "Usage: echo 'prompt' | $0 <container> <session-id> [--resume] [extra args...]" >&2
    exit 1
fi

resolve_env_file() {
    local candidate
    local home="${HOME:-$(eval echo ~)}"
    for candidate in "${HARNESS_ENV_FILE}" "$home/.config/oh-my-pi/env.sh" "$home/.config/claude-code/env.sh"; do
        [ -z "$candidate" ] && continue
        case "$candidate" in
            ~*) candidate="$home/${candidate#~}" ;;
        esac
        if [ -f "$candidate" ]; then
            echo "$candidate"
            return
        fi
    done
}

ENV_FILE="$(resolve_env_file)"

if [ -n "$ENV_FILE" ] && [ -f "$ENV_FILE" ]; then
    # Source harness environment (API keys, proxy config)
    # shellcheck disable=SC1090
    source "$ENV_FILE"
fi

HARNESS_BIN_RESOLVED="$(resolve_harness_bin)"
HARNESS_BIN="$HARNESS_BIN_RESOLVED"

cd "$SCRIPT_DIR"

HARNESS_BASE="${HARNESS_BASE_ARGS:-}"
if [ -n "$HARNESS_BASE" ]; then
    read -r -a HARNESS_ARGS <<< "$HARNESS_BASE"
else
    HARNESS_ARGS=(--print)
fi

env_default() {
    local name="$1"
    local default_value="$2"
    if [ "${!name+x}" ]; then
        printf '%s\n' "${!name}"
    else
        printf '%s\n' "$default_value"
    fi
}

PROMPT_FLAG="$(env_default HARNESS_PROMPT_FLAG "-p")"
SESSION_FLAG="$(env_default HARNESS_SESSION_FLAG "--session-id")"
RESUME_FLAG="$(env_default HARNESS_RESUME_FLAG "--resume")"
SYSTEM_PROMPT_FLAG="$(env_default HARNESS_SYSTEM_PROMPT_FLAG "--append-system-prompt")"
SYSTEM_PROMPT_FILE_FLAG="$(env_default HARNESS_SYSTEM_PROMPT_FILE_FLAG "--append-system-prompt-file")"
SKIP_FLAG="$(env_default HARNESS_SKIP_PERMISSIONS_FLAG "--dangerously-skip-permissions")"

skip_permissions=true
case "${HARNESS_SKIP_PERMISSIONS:-1}" in
    0|false|False|no|No|off|Off) skip_permissions=false ;;
esac

append_system_prompt=true
case "${HARNESS_APPEND_SYSTEM_PROMPT:-1}" in
    0|false|False|no|No|off|Off) append_system_prompt=false ;;
esac

RESUME=false
EXTRA_ARGS=()
for arg in "$@"; do
    if [ "$arg" = "--resume" ]; then
        RESUME=true
    else
        EXTRA_ARGS+=("$arg")
    fi
done

if [ "$skip_permissions" = true ] && [ -n "$SKIP_FLAG" ]; then
    HARNESS_ARGS+=("$SKIP_FLAG")
fi

if [ "$RESUME" = true ]; then
    if [ -n "$RESUME_FLAG" ]; then
        HARNESS_ARGS+=("$RESUME_FLAG" "$SESSION_ID")
    fi
else
    if [ -n "$SESSION_FLAG" ]; then
        HARNESS_ARGS+=("$SESSION_FLAG" "$SESSION_ID")
    fi
    if [ "$append_system_prompt" = true ] && [ -f "$CONTEXT_FILE" ]; then
        if [ -n "$SYSTEM_PROMPT_FILE_FLAG" ]; then
            HARNESS_ARGS+=("$SYSTEM_PROMPT_FILE_FLAG" "$CONTEXT_FILE")
        elif [ -n "$SYSTEM_PROMPT_FLAG" ]; then
            HARNESS_ARGS+=("$SYSTEM_PROMPT_FLAG" "$(cat "$CONTEXT_FILE")")
        fi
    fi
fi

HARNESS_ARGS+=("${EXTRA_ARGS[@]}")
if [ -n "$PROMPT_FLAG" ]; then
    HARNESS_ARGS+=("$PROMPT_FLAG" "$PROMPT")
else
    HARNESS_ARGS+=("$PROMPT")
fi

HARNESS_CMD=$(printf '%q ' "$HARNESS_BIN" "${HARNESS_ARGS[@]}")
HARNESS_CMD=${HARNESS_CMD% }

SOURCE_SNIPPET=""
if [ -n "$ENV_FILE" ] && [ -f "$ENV_FILE" ]; then
    ENV_FILE_QUOTED=$(printf '%q' "$ENV_FILE")
    SOURCE_SNIPPET="source ${ENV_FILE_QUOTED} 2>/dev/null;"
fi

enroot start --rw --mount "$HOME:$HOME" "$CONTAINER" -- \
    bash -c "${SOURCE_SNIPPET} cd ~/ROCm-workspace && ${HARNESS_CMD}"
