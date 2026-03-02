# Planning Instructions

These are instructions for you (the orchestrator) to create an implementation plan. Follow them directly — do NOT spawn a subagent for planning.

## Context

- **Worktree**: {{worktree_path}}
- **Branch**: {{branch}}
- **Project**: {{project_name}}
- **Jira Key**: {{jira_key}}
- **Beads Task**: {{beads_id}}

## Jira Description

{{jira_description}}

## Acceptance Criteria

{{acceptance_criteria}}

## Instructions

1. **Read the project CLAUDE.md** at `{{worktree_path}}/CLAUDE.md` (if it exists) to understand project-specific conventions, build instructions, and patterns.

2. **Explore code areas relevant to the task.** Use Grep, Glob, and Read to understand the codebase around the areas that will need modification. Look at:
   - Code directly related to the Jira description and acceptance criteria
   - Adjacent modules, utilities, and shared infrastructure
   - Existing tests for the areas you'll modify

3. **Identify files that need modification** and explain why each one needs changes.

4. **Note existing patterns, utilities, and conventions** that the implementation should follow. Look for:
   - Naming conventions (functions, variables, files)
   - Error handling patterns
   - Logging conventions
   - Test structure and patterns
   - Build system conventions

5. **Identify risks, dependencies, or areas needing clarification** — anything that could block or complicate the implementation.

6. **Produce a structured plan** in this exact format:

```
## Approach

<High-level strategy: 2-3 sentences describing the overall approach>

## Files to Modify

- `<path>` — <what changes and why>
- ...

## Files to Create

- `<path>` — <purpose>
- ... (or "None")

## Key Patterns to Follow

- <convention or pattern observed in the codebase that the implementation should match>
- ...

## Build/Test Strategy

- <how to build and verify the changes>
- <specific test commands or test files to run>

## Risks

- <anything that could go wrong, edge cases, or areas needing clarification>
- ... (or "None identified")
```

## Rules

- Use absolute paths for all file references.
- Be specific — name exact files, functions, and line ranges when possible.
- Keep the plan actionable. Each item should be concrete enough that an implementation agent can follow it without additional exploration.
