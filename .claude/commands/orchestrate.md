---
description: Orchestrate Jira tasks through implementation, review, and PR creation
argument-hint: <JIRA-KEY> [JIRA-KEY ...] [additional instructions]
allowed-tools: [Bash, Read, Glob, Grep, Write, Edit, Task, ToolSearch, AskUserQuestion, TaskCreate, TaskUpdate, TaskList, TaskGet]
---

# Jira-to-PR Orchestration

Automate the full lifecycle: Jira intake → beads task → worktree → plan → implement → review → draft PR → Jira transition.

**You are the orchestrator AND the planner.** You coordinate subagents for execution tasks (worktree creation, implementation, review, finalization) but do the planning yourself using your own tools.

**Arguments:** $ARGUMENTS

Process each Jira key sequentially. Each task fully resolves before the next starts.

---

## Phase 1 — Jira Intake

For each Jira key in `$ARGUMENTS`:

1. Call `jira_get_issue` with the Jira key to fetch:
   - Summary, description, components, labels
   - Project key, priority
   - Acceptance criteria (check description and custom fields)
2. Store the extracted data for use in subsequent phases.

If the Jira key is invalid or inaccessible, report the error and skip to the next key.

---

## Phase 2 — Project Mapping

Read the mapping config:
```
Read: .claude/skills/orchestrate/jira-mapping.json
```

Read the project registry:
```
Read: .claude/registry/projects.json
```

Match the Jira task to a ROCm project using this priority:
1. **Jira components** → match against `projects.json` `components` and `subprojects` lists
2. **Jira labels** → match against project keys and `aliases` in `projects.json`
3. **Jira project key** → look up in `jira-mapping.json` `project_key_map`
4. **Ambiguous** → use `AskUserQuestion` to let the user pick the target project

Also determine the base branch from `jira-mapping.json` `base_branches`.

---

## Phase 3 — Beads Task Creation

Create a beads task:

```bash
source "$HOME/.cargo/env"
br create "<Jira summary>" --label <project-key> --label orchestrated
br update <id> --external-ref "<JIRA-KEY>"
```

Set acceptance criteria and design notes:
```bash
br comments add <id> "Acceptance criteria: <criteria from Jira>"
br comments add <id> "Jira description: <description summary>"
```

Store the beads task ID for subsequent phases.

---

## Phase 4 — Worktree Creation (Subagent)

1. **Fetch latest** from the base branch:
   ```bash
   git -C <main-repo-path> fetch origin <base-branch>
   ```

2. **Derive branch name**:
   - Format: `users/sareeder/<jira-key-lowercase>/<short-feature-summary>`
   - Feature summary: derived from Jira title, kebab-cased, max ~40 chars
   - Example: `users/sareeder/almiopen-123/add-convolution-descriptor-cache`

3. **Create branch** from the latest base:
   ```bash
   git -C <main-repo-path> branch <branch-name> origin/<base-branch>
   ```

4. **Spawn worktree subagent** using a `general-purpose` haiku agent with worktree-setup instructions:
   ```
   1. Read .claude/agents/worktree-setup.md
   2. Extract the body (everything after the YAML frontmatter closing ---)
   3. Append task details: "Create a <project> worktree for branch <branch-name> at path /home/AMD/sareeder/worktrees/<prefix>-<jira-key-lowercase>"
   4. Task(subagent_type="general-purpose", prompt=<agent body + task details>, model="haiku", mode="bypassPermissions")
   ```
   The worktree path uses `~/worktrees/` to keep orchestrated worktrees separate.

5. **Update projects.json** with the new worktree entry.

6. **Update beads task**:
   ```bash
   source "$HOME/.cargo/env"
   br comments add <id> "Worktree: <path>, Branch: <branch>"
   br update <id> --status in_progress
   ```

---

## Phase 5 — Planning (Orchestrator — You)

**You do the planning yourself.** Do NOT spawn a Plan subagent. Use your own Glob, Grep, and Read tools to explore the codebase and create the plan.

Read the planning instructions:
```
Read: .claude/skills/orchestrate/plan-template.md
```

Follow those instructions directly, substituting the context values:
- `{{worktree_path}}` — full worktree path
- `{{branch}}` — branch name
- `{{project_name}}` — project name
- `{{jira_key}}` — Jira key
- `{{jira_description}}` — Jira description text
- `{{acceptance_criteria}}` — acceptance criteria
- `{{beads_id}}` — beads task ID

Your planning work:
1. Read the project CLAUDE.md at `<worktree_path>/CLAUDE.md`
2. Explore code areas relevant to the task using Glob, Grep, Read
3. Identify files to modify, patterns to follow, and risks
4. Produce the structured plan output format from the template

After creating the plan:

1. **Record the plan in beads**:
   ```bash
   source "$HOME/.cargo/env" && br comments add <id> "PLAN: <one-line plan summary>"
   ```

2. **Present the plan to the user** via `AskUserQuestion`:
   - Show the full plan text
   - Options:
     - **Approve** — "Approve this plan and proceed to implementation"
     - **Revise** — "I have feedback on this plan" (user provides feedback)
     - **Abort** — "Cancel this task"

3. **Handle the response**:
   - **Approve** → store the plan text for Phase 6 and continue
   - **Revise** → revise the plan yourself based on user feedback. Do additional exploration if needed. Then re-present via `AskUserQuestion`. (Loop until approved or aborted.)
   - **Abort** → update beads:
     ```bash
     source "$HOME/.cargo/env"
     br comments add <id> "ABORTED: User cancelled during planning"
     br update <id> --status open
     ```
     Skip remaining phases for this task.

---

## Phase 6 — Implementation (Subagent)

Read the implementation template:
```
Read: .claude/skills/orchestrate/impl-template.md
```

Replace all `{{placeholders}}` with actual values:
- `{{worktree_path}}` — full worktree path
- `{{branch}}` — branch name
- `{{project_name}}` — project name
- `{{jira_key}}` — Jira key
- `{{jira_description}}` — Jira description text
- `{{acceptance_criteria}}` — acceptance criteria
- `{{beads_id}}` — beads task ID
- `{{implementation_plan}}` — the approved plan text from Phase 5

Spawn a `general-purpose` subagent with the filled template:
```
Task(subagent_type="general-purpose", prompt=<filled template>, mode="bypassPermissions")
```

**Store the returned `agentId`** — this will be used to resume the same agent for build fixes and review findings, preserving its full context.

The implementation agent will:
- Follow the approved plan (skipping broad exploration — the plan provides context)
- Implement and commit changes
- Update beads task with progress

### Build/Test Verification

After the implementation agent returns, extract the **Build/Test Strategy** section from the approved plan (Phase 5). This contains the exact build and test commands.

Spawn a `general-purpose` haiku agent to build and test:

```
Task(subagent_type="general-purpose", model="haiku", mode="bypassPermissions", prompt="
You are a build/test runner. Run the following commands in {{worktree_path}} and report results.

## Build/Test Commands

<paste the Build/Test Strategy section from the approved plan>

Run each command. Report results as: BUILD: PASS|FAIL, TEST: PASS|FAIL|SKIPPED, with any error output verbatim.
")
```

**If build/test fails**: resume the **original implementation agent** with the build errors to fix:

```
Task(subagent_type="general-purpose", resume=<impl_agent_id>, mode="bypassPermissions", prompt="
## Build/Test Failure to Fix

<paste the build/test error output>

Fix the build or test failure. Before committing, run pre-commit on staged files:
  cd {{worktree_path}} && git add <files> && pre-commit run
If pre-commit modifies files, re-stage and commit. If it reports errors, fix them and re-run until it passes.
Make a separate commit for the fix.
Do NOT build or test — the orchestrator will re-verify.
")
```

The resumed agent already has full context from implementation — no need to re-explain the codebase or plan.

Then re-run the build/test haiku agent. Loop up to **3 times**. If still failing after 3 attempts, escalate to the user via `AskUserQuestion`.

---

## Phase 7 — Review (Subagent)

Read the review template:
```
Read: .claude/skills/orchestrate/review-template.md
```

Replace all `{{placeholders}}` with actual values (same as Phase 6, plus `{{base_branch}}`).

Spawn a `general-purpose` subagent with the filled template:
```
Task(subagent_type="general-purpose", prompt=<filled template>, mode="bypassPermissions")
```

The review agent will:
- Find the merge base
- Gather diff and commit stack
- Read all changed files
- Explore related context
- Analyze for issues
- Check acceptance criteria
- Return a structured verdict: **PASS** or **FAIL** with classified findings

---

## Phase 8 — Address Review Findings

Parse the review agent's verdict:

- **If PASS** → proceed to Phase 9
- **If FAIL** → **resume the original implementation agent** to address findings:
  ```
  Task(subagent_type="general-purpose", resume=<impl_agent_id>, mode="bypassPermissions", prompt="
  ## Review Findings to Address

  <paste the review verdict with all findings>

  Address each Critical and Warning finding. Before each commit, run pre-commit on staged files:
    cd {{worktree_path}} && git add <files> && pre-commit run
  If pre-commit modifies files, re-stage and commit. If it reports errors, fix them and re-run until it passes.
  Make a separate commit per fix.
  ")
  ```

  The resumed agent already has the full implementation context — all files it read, the plan, and its understanding of the codebase. No need to re-explain anything; just provide the findings.

  **Fallback**: If resuming fails (e.g., context limit reached), spawn a fresh `general-purpose` sonnet agent with the original impl template plus the review findings.

  Then re-run build/test verification (Phase 6 haiku build agent).

Record the review result in beads:
```bash
source "$HOME/.cargo/env" && br comments add <id> "REVIEW: <PASS|FAIL> - <summary>"
```

---

## Phase 9 — Finalize (Subagent)

Read the finalize template:
```
Read: .claude/skills/orchestrate/finalize-template.md
```

Replace all `{{placeholders}}` with actual values:
- `{{worktree_path}}` — full worktree path
- `{{branch}}` — branch name
- `{{base_branch}}` — base branch (e.g. develop, main)
- `{{project_name}}` — project name
- `{{jira_key}}` — Jira key
- `{{jira_summary}}` — Jira issue summary/title
- `{{beads_id}}` — beads task ID
- `{{implementation_summary}}` — summary of what was implemented (from Phase 6 agent output)
- `{{test_results}}` — build/test results summary (from Phase 6 verification)
- `{{review_iterations}}` — number of review iterations
- `{{remote_repo}}` — remote repo in `owner/repo` format (e.g. `ROCm/rocm-libraries`)

Spawn a `general-purpose` subagent with the filled template:
```
Task(subagent_type="general-purpose", prompt=<filled template>, mode="bypassPermissions")
```

The finalize agent will:
- Push the branch
- Create a **draft** PR
- Update beads task and close it
- Transition the Jira ticket (if applicable)
- Add a Jira comment with the PR link
- Return the PR URL and completion report

After the finalize agent returns, output the completion report to the user.

---

## Error Handling

- **Jira MCP unavailable**: Report error, ask user if they want to proceed with manual Jira key info
- **Worktree creation fails**: Report git error, stop processing this task
- **Build/test failures in implementation**: Implementation agent handles retries internally
- **Push fails**: Report error with the git message, ask user to resolve
- **PR creation fails**: Report error, provide the manual `gh` command for the user

---

## Beads Update Protocol

| Event | Command |
|-------|---------|
| Task claimed | `br update <id> --status in_progress` |
| Progress | `br comments add <id> "<note>"` |
| Blocker | `br comments add <id> "BLOCKED: <detail>"` |
| Review result | `br comments add <id> "REVIEW [N/3]: PASS/FAIL - <summary>"` |
| PR created | `br update <id> --external-ref "<JIRA-KEY> \| <pr-url>"` |
| Task done | `br close <id>` with design field set to full synopsis |
