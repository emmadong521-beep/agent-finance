# SQLite Memory Backbone — Design Document

## Why SQLite?

- **Zero infrastructure** — no server, no Docker, no external dependency
- **Embedded & fast** — reads/writes happen locally with minimal latency
- **FTS5 built-in** — full-text search without additional tooling
- **Portable** — a single `.db` file can be backed up, copied, or versioned
- **Sufficient for v0.2** — we don't need vector search or distributed storage yet

When Agent OS eventually needs semantic/vector search, we can add a sidecar
(e.g. ChromaDB, Qdrant) without changing the SQLite layer — it stays as the
canonical store for structured data and FTS.

## Table Responsibilities

| Table | Purpose |
|---|---|
| `sessions` | Tracks a single task execution from start to end |
| `messages` | Conversation / execution trace within a session |
| `tool_calls` | Records of tool invocations (what, args, success/fail) |
| `memory_items` | Long-term structured memory (patterns, decisions, failures, etc.) |
| `memory_links` | Graph-like relationships between memory items |
| `active_memory_items` | View over `memory_items` where `is_active = 1` |

### Memory Types

- `project_context` — static knowledge about a project
- `pattern` — approaches that consistently work
- `anti_pattern` — approaches that consistently fail
- `decision` — important choices and their rationale
- `failure` — what went wrong and how to prevent it
- `note` — general observations worth keeping

## Memory Write Flow

```
Task completes
    │
    ▼
Darwin Reflection
    │
    ├─► add_memory_item(pattern, ...)
    ├─► add_memory_item(anti_pattern, ...)
    ├─► add_memory_item(decision, ...)
    └─► add_memory_item(failure, ...)
    │
    ▼
SQLite (memory_items + FTS5 index)
```

## Memory Prefetch Flow

```
New task arrives
    │
    ▼
prefetch_for_task(project_name, keywords)
    │
    ├─► get_project_context(project_name)
    ├─► get_patterns(project_name)
    ├─► get_anti_patterns(project_name)
    └─► search_memory(keywords, project_name)
    │
    ▼
Agent receives context before execution
```

## MemoryService API

| Method | Description |
|---|---|
| `create_session()` | Start a new task session |
| `end_session()` | Mark session completed/failed |
| `add_message()` | Record a conversation message |
| `add_tool_call()` | Record a tool invocation |
| `add_memory_item()` | Write a long-term memory item |
| `search_memory()` | FTS5 keyword search |
| `get_project_context()` | Load project context |
| `get_patterns()` | Load known patterns |
| `get_anti_patterns()` | Load known anti-patterns |
| `prefetch_for_task()` | One-call memory load before execution |

## Future: Paperclip Compatibility

When Paperclip is integrated as the multi-agent control plane:

- Each agent gets its own `agent_name` scope in `memory_items`
- Paperclip can query cross-agent memory via `scope = 'global'`
- Memory links can represent inter-agent knowledge transfer
- Access control is enforced at the application layer, not in SQLite

## Scope Boundaries (v0.2)

v0.2 **does not** include:

- Vector / semantic search
- Graph-based memory reasoning
- Paperclip integration
- Hermes deep integration
- Auto-generated SKILL.md
- Multi-agent memory permission isolation

v0.2 only does one thing: **stable SQLite memory read/write**.
