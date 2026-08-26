# ROCm Workspace Hub

Central dispatch workspace for ROCm development projects. This repo owns project/worktree discovery and local workspace conventions.

## Source of Truth

- Repository projects → immediate git directories under `repos/<project>/`, gitignored.
- Workspace-local worktrees → `worktrees/<project>/<branch-suffix>/`, gitignored.
- Worktree branches must use the `users/sareeder/` prefix; the directory uses only the suffix (`users/sareeder/feature-x` → `feature-x`).
- Bootstrap and clone setup → `docs/repo-setup.md`
- Commands → `.claude/commands/*.md`
- Agents → `.shared/agents/*.md` (symlinked into `.claude/agents/` and `.codex/agents/`)
- Skills → `.shared/skills/*/` (symlinked into `.claude/skills/` and `.codex/skills/`)

Repository names and worktrees are discovered from the filesystem; do not add project metadata files.

## Default Agent Execution

- Stay local to the controller host/container for orchestration, editing, git, GitHub, and Teams replies.
- Use this workspace for source checkout discovery and local file operations only.
- Do not rely on workspace-owned SSH wrappers or remote-execution scripts. Follow the deployment-provided routing instructions for remote or specialized-runtime execution and verification.

## Workflow Principles

1. Plan first for non-trivial tasks.
2. Use subagents liberally for independent implementation/review work.
3. Verify before done with a build, test, or focused review.
4. Attempt autonomous bug fixing before escalating.

### Design and Escalation

- Use `docs/design-and-escalation.md` as the full policy record.
- Triage work before planning. Use GREEN for established, locally verifiable changes. Use Design mode for open decisions.
- Do not draft a plan while an architectural decision remains open.
- Workers must return `STOP: <violated invariant>` with evidence and one alternative. They must not work around the issue.
- Stop all affected implementation dispatches after a `STOP:` result or contradicted assumption.
- Escalate decisions with structured options. Resume with a fresh agent after sign-off.
- Treat a documented halt with evidence as a successful dispatch result.

### Open-Ended Work

Principle 1 covers tasks that have a groove. When there isn't one — a new subsystem, a new representation or protocol, an ownership boundary between components, or a rewrite — the codebase does not supply the missing decisions, and an agent asked to implement settles them silently while writing code. The review then lands on a coherent implementation of a design nobody chose.

For that work, read the `design-first` skill and keep the modes separate: orient → investigate → debate → decide → plan → implement → verify → checkpoint. Recommendations, not gates; the point is that implementation stays behind the last decision actually validated.

- State the mode before shifting: "gather context and concur or challenge", "do not turn this into a task yet", "implement this milestone and stop".
- Separate required properties from candidate mechanisms, so a pivot reads as progress rather than failure.
- Do not plan while the design is open. A plan containing "choose an appropriate representation" still hides design work inside implementation.
- Bound each milestone: exact outcome, out-of-scope list, acceptance evidence, and the event that stops the agent.
- Build a local correctness oracle before end-to-end runs — fixtures, dumps, invariant checks. `X violates invariant Y` beats "the run looked wrong".
- Stop a bad path by naming the violated invariant, not by restating the request more forcefully.
- Record fixed point, decisions, rejected alternatives, invariants, and open questions in the project's design docs. It is the part that survives a pivot.

Spikes are expected to be thrown away: one narrow question, a hard stop, hard-coded values allowed only while the spike stays disposable. Keep the evidence, discard the structure.

## Key Rules

1. Use absolute paths when operating inside project clones/worktrees.
2. Each worktree keeps its own `build/` and `.venv`.

## ASD-STE100 Writing Standard

All agents SHOULD generally use ASD-STE100 Simplified Technical English for all communication, including comments, plans, task descriptions, summaries, reports, and other prose.

- Use short, direct sentences. Use one main action in each sentence.
- Use the active voice. Name the actor when the actor is not clear.
- Use the imperative mood for instructions. Start each instruction with a verb.
- Use the present tense for facts. Use the future tense only for planned results.
- Use common, approved words and one term for each concept. Define each abbreviation at first use.
- Use specific terms. Do not use vague words, idioms, slang, metaphors, or unnecessary qualifiers.
- Avoid nominalizations, noun strings, and hidden verbs. Use a direct verb for each action.
- Do not use `and/or`, `etc.`, or ambiguous pronouns.
- Keep each sentence to 25 words or fewer when practical.
- Use numbered steps for procedures. State a condition before the action when the condition controls the action.
- State the action, reason, or result in each comment and plan. Do not add filler text.
- Keep command names, paths, identifiers, and required syntax unchanged.
