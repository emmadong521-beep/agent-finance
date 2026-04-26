# Darwin — Self-Improvement Loop

## Description

Darwin is the evolution engine of Agent OS. It monitors task execution, extracts patterns, and evolves skills over time.

## When to Use

- After task reflection to trigger skill evolution
- Periodically to review and improve existing skills
- When a repeated failure pattern is detected

## Evolution Cycle

### 1. Observe

- Read recent session data (sessions, messages, tool_calls)
- Read recent memory items (patterns, failures, decisions)
- Identify recurring themes and gaps

### 2. Analyze

- Detect patterns: what approaches consistently work?
- Detect anti-patterns: what approaches consistently fail?
- Identify skill gaps: tasks that lacked a matching skill
- Find upgrade opportunities: existing skills that could be improved

### 3. Evolve

- **FIX**: Patch a broken skill based on failure data
- **DERIVE**: Create a new skill from observed patterns
- **CAPTURE**: Codify an ad-hoc approach into a formal skill
- **DEPRECATE**: Mark an outdated skill as inactive

### 4. Validate

- Test evolved skills against historical task data
- Verify no regressions in existing skill behavior
- Record evolution provenance (parent skill, change summary)

## Memory Integration

Darwin reads from and writes to the following memory types:

- **Reads**: `pattern`, `anti_pattern`, `failure`, `decision`
- **Writes**: `pattern` (new patterns discovered), `note` (evolution log)

## Skill Output

Evolved skills are saved to `.openclaw/skills/` with metadata:

- `origin`: `FIX` | `DERIVE` | `CAPTURE` | `DEPRECATE`
- `parent_skill_ids`: lineage tracking
- `change_summary`: what changed and why

## Configuration

```json
{
  "auto_evolve": true,
  "evolution_interval_hours": 24,
  "min_observations": 5,
  "max_skills_per_cycle": 3
}
```

## Future

- Integration with Paperclip for multi-agent skill sharing
- A/B testing of evolved skills
- Confidence scoring for skill recommendations
