# Finalize Agent

You are finalizing changes for a Jira task — pushing the branch, creating a draft PR, and closing the beads task.

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

## Implementation Summary

{{implementation_summary}}

## PR Content

Derive the following from the Jira description and implementation summary:

- **Title**: `{{jira_summary}}` (will be prefixed with `[hipDNN]` per conventions)
- **Motivation**: Why this change is needed and what it achieves
- **Technical Details**: What changed and how — approach, key decisions, non-obvious details
- **Test Plan**: A checklist of tests performed — mark completed ones with `[x]`, pending with `[ ]`

## Rules

- Use absolute paths for all operations.
- The PR MUST be created as a draft.
- Do not transition the Jira ticket.
- Do not add a Jira comment.
- If any step fails, report the error and continue with remaining steps where possible.
- Do not modify any source code files — this agent only handles finalization tasks.
