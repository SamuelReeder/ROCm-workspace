#!/bin/bash
# Claude Code hook: runs pre-commit on staged files after any git add command
# Fires on PostToolUse for Bash, works across all projects/worktrees

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

# Only trigger after git add commands
if ! echo "$COMMAND" | grep -q "git add"; then
  exit 0
fi

# Run in the directory where Claude actually staged files
cd "$CWD" || exit 0

# Find the git repo root (handles subdirectories and worktrees)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO_ROOT"

# Only run if this repo has a pre-commit config
if [ ! -f ".pre-commit-config.yaml" ]; then
  exit 0
fi

STAGED_FILES=$(git diff --cached --name-only 2>/dev/null)
if [ -n "$STAGED_FILES" ]; then
  echo "Running pre-commit on staged files..." >&2
  pre-commit run --files $STAGED_FILES >&2
  PRE_COMMIT_EXIT=$?
  if [ $PRE_COMMIT_EXIT -ne 0 ]; then
    echo "pre-commit failed — files may have been modified. Re-stage and retry." >&2
    exit 2  # Block: tells Claude the action failed
  fi
fi

exit 0
