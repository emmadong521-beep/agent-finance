# Harness — Structured Task Execution

## Description

Harness provides a structured workflow pattern for reliable task execution. Every task follows the UPARV loop: Understand → Plan → Act → Verify → Reflect.

## When to Use

- Any task that requires structured, reliable execution
- Tasks that benefit from planning before acting
- Tasks where verification and reflection add value

## Workflow

### 1. Understand

- Parse the task instruction
- Identify constraints, requirements, and success criteria
- Retrieve relevant memory (patterns, decisions, project context)
- Check for related prior sessions

### 2. Plan

- Break the task into ordered steps
- Identify dependencies and risks
- Select appropriate tools and skills
- Define verification criteria for each step

### 3. Act

- Execute steps in planned order
- Record all tool calls and results
- Adapt plan if unexpected issues arise
- Maintain a clear execution trace

### 4. Verify

- Check each deliverable against requirements
- Validate no side effects or regressions
- Confirm task completeness

### 5. Reflect

- Extract patterns, anti-patterns, decisions, and failures
- Write structured insights to memory
- Suggest skill improvements

## Integration

- **Memory**: Reads from `memory_items` before execution, writes after reflection
- **Darwin**: Feeds execution data into the evolution pipeline
- **Sessions**: All activity is tracked in the `sessions` and `messages` tables

## Configuration

```json
{
  "pattern": "UPARV",
  "auto_reflect": true,
  "memory_retrieval": true
}
```
