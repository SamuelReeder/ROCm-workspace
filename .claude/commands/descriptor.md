---
description: Orchestrate adding descriptor lowering or lifting for a hipDNN node (Jira → worktree → codegen skill → PR)
argument-hint: <JIRA-KEY> [additional instructions]
allowed-tools: [Bash, Read, Write, Task, AskUserQuestion]
---

# Descriptor Orchestrator

Coordinates adding descriptor-based lowering **or** lifting for a hipDNN operation node.
The orchestrator's job is **dispatch only** — gather info from Jira, set up the worktree,
hand off to the codegen skill agent, then confirm the PR with the user before posting.

Do not investigate the codebase, check prerequisites, or make technical judgements yourself.
Delegate all technical work to agents.

**Arguments:** $ARGUMENTS

---

## Phase 1 — Jira Intake

1. Extract the Jira key from `$ARGUMENTS`. Store anything after it as `additional_instructions`.
2. Call `jira_get_issue` to fetch summary, description, and acceptance criteria.
3. **Determine mode** from the ticket text:
   - Contains "lifting" or "lift" → `lift-only`
   - Otherwise → `backend`
   - If genuinely ambiguous, use `AskUserQuestion` to ask the user.
4. **Derive the operation name** from the Jira summary/description — e.g. `matmul`, `sdpa`, `batch_norm`. If ambiguous, ask the user.

---

## Phase 2 — Worktree Setup

1. Read `.claude/registry/projects.json` for the `rocm-libraries` main repo path.
2. Derive branch name:
   - Lowering: `users/sareeder/<jira-key-lowercase>/add-<node>-descriptor`
   - Lifting:   `users/sareeder/<jira-key-lowercase>/add-<node>-lifting`
3. Spawn a worktree-setup agent:
   - Read `.claude/agents/worktree-setup.md`, extract body after YAML frontmatter
   - Pass it to a haiku subagent in `bypassPermissions` mode with these specifics:
     - Main repo path (from registry)
     - Branch name (derived above)
     - Worktree path: `/home/AMD/sareeder/worktrees/rocm-libs-<jira-key-lowercase>`
     - Base: `origin/develop`
4. Once the agent confirms success, update `projects.json` with the new worktree entry.

---

## Phase 3 — Read the Codegen Skill

Read the skill file directly from the worktree (it is now merged into `develop`):

```bash
cat <worktree_path>/projects/hipdnn/tools/DescriptorGenerator/.claude/skills/hipdnn-codegen/SKILL.md
```

Store the full SKILL.md content for use in Phase 4.

---

## Phase 4 — Implementation (Subagent)

Prepend a context block to the SKILL.md content and spawn a `general-purpose` subagent using **opus** in `bypassPermissions` mode:

```
## Task Context

- **Jira Key**: <jira_key>
- **Summary**: <jira_summary>
- **Mode**: <mode>  (backend | lift-only)
- **Operation**: <node_snake>  (use as the $ARGUMENTS operation name for the skill)
- **Worktree**: <worktree_path>
- **Acceptance Criteria**:
<acceptance_criteria>

## Jira Description

<jira_description>

## Additional Instructions

<additional_instructions>

---

The hipDNN project root for all file operations is: <worktree_path>/projects/hipdnn/
The codegen tool is at: <worktree_path>/projects/hipdnn/tools/DescriptorGenerator/
Use the worktree above for all reads, writes, builds, and tests.
Run with mode "<mode>" and operation name "<node_snake>".

---

[full SKILL.md content]
```

Spawn with:
```
Task(subagent_type="general-purpose", prompt=<context + SKILL.md>, mode="bypassPermissions", model="opus")
```

The skill handles everything: codegen, file placement, fragment insertion, wiring, build, and tests.
If the agent reports an unresolvable failure, surface the error to the user and stop.

**Notes for the impl agent** (include verbatim in the context block):
- Use the `commit` subagent (`subagent_type="commit"`) for all commits — write the message yourself and pass it to the agent
- For `lift-only` mode: the integration lifting test (`Integration<Op>DescriptorLifting.cpp`) must include an `AutoAssignedUidsPreservedInRoundTrip` test case (see `IntegrationConvFpropDescriptorLowering.cpp` for reference)
- For `lift-only` mode: add one test case to `$HIPDNN_SRC/frontend/tests/TestOperationUnpacker.cpp` for the new node type

---

## Phase 5 — PR Review & Post

Before creating the PR, draft the title and body, then **ask the user to confirm**:

Draft:
- **Title**: a concise description of the change derived from the Jira summary (no ticket ID, prefixed with `[hipDNN]`)
- **Motivation**: why this change is needed
- **Technical details**: what the impl agent reported — what was added and how the pieces fit
- **Test plan**: what was built and tested, as a checklist

Use `AskUserQuestion` to present the draft and ask the user to approve or provide edits before proceeding.

Once approved:
- Use the `pr-summary` skill conventions for the confirmed title and body.
- Push the branch with `git -C <worktree_path> push -u origin <branch>`.
- Create a draft PR with `gh pr create --repo <remote_repo> --head <branch> --base develop --draft --assignee SamuelReeder`, passing the confirmed title and body.
- Update the beads task with the PR URL and close it, sourcing `"$HOME/.cargo/env"` before running `br`.

Output the PR URL to the user.

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Jira unavailable | Ask user for info manually |
| Mode or operation ambiguous | Ask user |
| Worktree agent fails | Surface error, stop |
| Codegen branch or SKILL.md missing | Report and stop |
| Impl agent reports unresolvable failure | Surface error to user, stop |
| Push fails | Report error verbatim, stop |
| PR creation fails | Report error, give manual `gh` command |
