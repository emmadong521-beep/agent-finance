# Standard Task Workflow

## Why Agent OS Needs a Workflow Layer

The memory, executor, and reflection layers each solve a separate problem. A
workflow layer defines the order in which those pieces run for a real task. This
keeps OpenClaw from wiring every step manually and gives Agent OS one standard
task loop that can be tested and reused.

`StandardTaskWorkflow` is the v0.5 implementation of that loop.

## StandardTaskWorkflow Steps

1. Create a memory session for the task.
2. Build task keywords from the task title and description.
3. Prefetch project memory through `MemoryService.prefetch_for_task()`.
4. Attach the prefetch result to `ExecutionContext.memory_prefetch`.
5. Execute the task through a `BaseExecutor`.
6. Reflect on the `ExecutionResult` with `DarwinReflector`.
7. Write reflection memory candidates back to SQLite.
8. End the memory session.
9. Return a `WorkflowResult`.

If execution or reflection fails, the workflow marks the session as `failed` and
returns a failed `WorkflowResult`.

## Relationship to Existing Layers

The v0.2 memory layer owns sessions, prefetch, and memory writes.

The v0.3 executor layer owns the stable execution interface. The workflow only
depends on `BaseExecutor`, so it can run with `MockExecutor` today and real
Hermes, Claude Code, or Codex adapters later.

The v0.4 reflection layer owns post-execution analysis and candidate generation.
The workflow calls Darwin and persists the returned candidates.

## v0.5 Boundaries

v0.5 does not introduce a new memory schema, real external executor calls,
Paperclip orchestration, queueing, retries, or parallel execution. It only
connects the existing layers into a single standard task flow.

## Future Extensions

`repo_analysis` can become a specialized workflow that enriches task keywords,
collects repository structure, and stores project-level findings.

`autoresearch` can add source collection, citation tracking, and research memory
types while still returning a `WorkflowResult`.

Paperclip can sit above workflows as a control plane. It can choose which
workflow to run, select an executor, coordinate multiple agents, and aggregate
their results without changing the standard task contract.
