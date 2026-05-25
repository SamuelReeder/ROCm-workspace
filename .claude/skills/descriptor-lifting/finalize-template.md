# Finalize Agent — Descriptor Lifting

You are finalizing the descriptor lifting implementation for the **{{NodePascal}}** operation — pushing the branch, creating a draft PR, and closing the beads task.

Use this PR creation flow:
1. Push `{{branch}}`.
2. Create a draft PR with `gh pr create --repo {{remote_repo}} --head {{branch}} --base {{base_branch}} --draft --assignee SamuelReeder`.
3. Update and close the beads task with the PR URL.

Use the `pr-summary` skill's title/body conventions for PR text.

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

- **Title**: `Add {{NodePascal}} descriptor lifting`
- **Motivation**: Adds descriptor-based lifting support for the {{NodePascal}} operation in hipDNN. This enables reconstructing frontend graph attributes from serialized FlatBuffer data, completing the round-trip: frontend graph → descriptor lowering → serialize → deserialize → descriptor lifting → frontend graph.
- **Technical Details**: A plain unified summary of the implementation approach derived from the implementation summary. Describe what was added (fromNode, unpacker, unpack_from_descriptor, scaffolding wiring), how the pieces fit together, and any notable decisions — using `code formatting` for symbols, files, and flags. Do not list files mechanically.

- **Test Plan**:
```
- [x] fromNode round-trip tests (lifecycle, tensor references, data fields, name preservation)
- [x] NodeFactory delegation test (verifies correct dispatch)
- [x] buildNode round-trip (fromNode → buildNode preserves all attributes)
- [x] getAttribute validation (all fields accessible after fromNode)
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
