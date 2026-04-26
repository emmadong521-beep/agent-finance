# Architecture Overview

## Layers

1. **Interaction Layer**
2. **Agent OS Layer** (OpenClaw)
3. **Skill Layer** (Harness, Darwin)
4. **Execution Layer** (Hermes / Claude Code)
5. **Memory Layer** (SQLite)
6. **Workflow Layer** (Task / Research)

## Design Principles

- **Modular** — each layer is independent and replaceable
- **Replaceable execution layer** — swap Hermes, Claude Code, or any other executor
- **Persistent memory** — knowledge survives across sessions
- **Self-improving behavior** — agents learn from outcomes
- **Future multi-agent compatibility** — designed for orchestration from day one

## Future Integration

**Paperclip** will act as a control plane on top of this system.
