---
name: worktree-guard
description: Prevent cross-contamination between worktrees by validating build and git operations target the correct worktree
event: PreToolUse
tools: [Bash]
---

# Worktree Guard Hook

Validates that build commands and git operations target the correct worktree.

## Check Patterns

### Build Path Validation

When seeing `ninja -C <path>` or `cmake -B <path>`, verify:
1. Path matches a known worktree's build directory
2. Path is consistent with current conversation context

Known build directories:
- `/home/AMD/sareeder/TheRock/build`
- `/home/AMD/sareeder/therock-consumption/build`
- `/home/AMD/sareeder/therock-miopen-plugin-move/build`
- `/home/AMD/sareeder/full/rocm-libraries/build`

### Git Path Validation

When seeing `git -C <path>`, verify:
1. Path matches a known project or worktree
2. Operations don't accidentally target wrong worktree

### File Operation Validation

When editing files, verify:
1. File path is within the current working context
2. Not accidentally editing files in a different worktree

## Warning (Non-Blocking)

If a potential cross-contamination is detected, emit a warning:

```
**[Worktree Guard]** Build path '/home/AMD/sareeder/TheRock/build' may not match
the current context (therock-consumption). Verify you're targeting the correct worktree.
```

## Known Worktree Mappings

| Context | Expected Build Path |
|---------|---------------------|
| TheRock (main) | /home/AMD/sareeder/TheRock/build |
| therock-consumption | /home/AMD/sareeder/therock-consumption/build |
| therock-miopen-plugin | /home/AMD/sareeder/therock-miopen-plugin-move/build |
| rocm-libraries | /home/AMD/sareeder/full/rocm-libraries/build |

## Implementation Note

This hook provides advisory warnings. It does not block operations, as there may be legitimate reasons to reference other worktrees (e.g., comparing builds).
