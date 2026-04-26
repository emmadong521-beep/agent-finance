# Reflection Prompt

After every task completion, perform a structured reflection:

## Task Summary

- What was the task?
- What was the outcome?

## Analysis

- **Patterns**: What recurring patterns did this task reveal?
- **Anti-patterns**: What should be avoided in the future?
- **Decisions**: What key decisions were made and why?
- **Failures**: What went wrong? How could it be prevented?

## Memory Updates

Based on this reflection, should any memory items be:

- **Created** — new patterns, decisions, or context to remember
- **Updated** — existing knowledge that needs revision
- **Deprecated** — outdated information to mark inactive

## Skill Evolution

- Did this task expose a gap in existing skills?
- Should any skill be updated or a new one derived?
- Any suggestions for the Darwin evolution pipeline?

## Output

Write structured reflections to the `memory_items` table with appropriate `memory_type`:

- `pattern` — reusable approaches that worked
- `anti_pattern` — approaches that failed
- `decision` — important choices and rationale
- `failure` — what went wrong and how to prevent it
- `note` — general observations worth keeping
