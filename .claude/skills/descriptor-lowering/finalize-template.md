# Finalize Agent — Descriptor Lowering

You are finalizing the descriptor lowering implementation for the **{{NodePascal}}** operation — pushing the branch, creating a draft PR, and closing the beads task.

Follow the PR creation process defined in `/home/AMD/sareeder/ROCm-workspace/.claude/commands/create-pr.md`.

## Context

- **Worktree**: {{worktree_path}}
- **Branch**: {{branch}}
- **Base Branch**: {{base_branch}}
- **Jira Key**: {{jira_key}}
- **Jira Summary**: {{jira_summary}}
- **Beads Task**: {{beads_id}}
- **Remote Repo**: {{remote_repo}}
- **Review Iterations**: {{review_iterations}}
- **Node Type**: {{NodePascal}}

## Implementation Summary

{{implementation_summary}}

## PR Content

- **Title**: `Add {{NodePascal}} descriptor lowering`
- **Motivation**: Adds descriptor-based lowering support for the {{NodePascal}} operation in hipDNN. This enables the {{node_snake}} operation to be lowered through the descriptor API path (`HIPDNN_USE_DESCRIPTOR_API=1`), creating backend operation descriptors that serialize to FlatBuffer graphs.
- **Technical Details**: A plain unified summary of the implementation approach derived from the implementation summary. Describe what was added, how the pieces fit together, and any notable decisions — using `code formatting` for symbols, files, and flags. Do not list files mechanically.

- **Test Plan**:
```
- [x] Backend unit tests (descriptor lifecycle, finalize validation, attribute set/get, buildNode)
- [x] Backend graph tests (serialization round-trip)
- [x] Frontend integration tests (full pipeline: frontend graph → descriptor lowering → serialize → deserialize → verify)
- [x] Standard tests pass: `ctest --output-on-failure`
- [x] Descriptor API tests pass: `HIPDNN_USE_DESCRIPTOR_API=1 ctest --output-on-failure`
```

## Rules

- Use absolute paths for all operations.
- The PR MUST be created as a draft.
- Do not transition the Jira ticket.
- Do not add a Jira comment.
- If any step fails, report the error and continue with remaining steps where possible.
- Do not modify any source code files — this agent only handles finalization tasks.
