# Executor Abstraction

## Why Agent OS Needs Executors

OpenClaw workflows should not know how to call a specific runtime. A workflow
needs to submit a task, pass context, and receive a normalized result. The
executor layer provides that boundary so Hermes, Claude Code, Codex, and future
runners can be swapped without changing workflow logic.

The abstraction also gives Agent OS one place to enforce execution contracts:
availability checks, task shape, result shape, metadata, and future audit hooks.

## Core Contracts

### `Task`

`Task` describes the work to run. It includes a stable `task_id`, a human-readable
`title`, a detailed `description`, optional `project_name` and `workflow_name`
fields, and arbitrary `metadata`.

### `ExecutionContext`

`ExecutionContext` carries runtime context into an executor. In v0.3 it includes
the optional `session_id`, `agent_name`, `workspace_path`, `memory_prefetch`, and
extra `metadata`. This is where the v0.2 SQLite Memory Backbone connects to the
execution layer.

### `ExecutionResult`

`ExecutionResult` is the normalized response from every executor. It records the
`task_id`, `executor_name`, `status`, `summary`, optional `output`, optional
`error`, and arbitrary `metadata`.

### `BaseExecutor`

`BaseExecutor` defines the shared interface:

```python
name() -> str
is_available() -> bool
execute(task: Task, context: ExecutionContext) -> ExecutionResult
```

Workflows should depend on this interface instead of concrete runner
implementations.

## v0.3 Scope

v0.3 only establishes the execution boundary:

- `MockExecutor` validates the interface locally and returns a completed result.
- `HermesExecutor`, `ClaudeCodeExecutor`, and `CodexExecutor` are placeholders.
- Placeholder executors check command availability with `shutil.which`.
- Placeholder executors do not invoke external commands.
- Task and result JSON Schemas are stored under `contracts/`.

This keeps v0.3 focused on contracts and integration shape, not runtime behavior.

## Future Integrations

Hermes can become the default local execution engine by translating `Task` and
`ExecutionContext` into its CLI or API inputs, then mapping its output back into
`ExecutionResult`.

Claude Code and Codex can follow the same adapter pattern. Each executor owns
tool-specific command construction, environment checks, timeout handling, and
output parsing while preserving the same workflow-facing interface.

Paperclip can sit above this layer as a multi-agent control plane. It can choose
which executor receives a task, fan out work across agents, and aggregate
multiple `ExecutionResult` objects without coupling workflows to a specific
runner.
