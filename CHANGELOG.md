# Changelog

## v0.5 - Standard Task Workflow

- Add WorkflowResult model
- Add StandardTaskWorkflow to connect memory prefetch, executor execution, Darwin reflection, and memory writeback
- Add end-to-end workflow demo
- Add workflow result JSON schema
- Add Standard Task Workflow documentation

## v0.4 - Darwin Memory Writeback

- Add ReflectionResult and MemoryCandidate models
- Add DarwinReflector for rule-based post-execution reflection
- Add SQLite memory writeback from reflection candidates
- Add end-to-end reflection demo
- Add Darwin memory writeback documentation

## v0.3 - Executor Abstraction

- Add BaseExecutor interface
- Add Task, ExecutionContext, and ExecutionResult contracts
- Add MockExecutor for local validation
- Add placeholder Hermes, Claude Code, and Codex executors
- Add task/result JSON schemas
- Add executor abstraction documentation

## v0.2 - SQLite Memory Backbone

- Add SQLite database initialization script
- Add MemoryService for sessions, messages, tool calls, and memory items
- Add FTS5-based memory search
- Add task prefetch flow for project context, patterns, anti-patterns, and relevant memories
- Add memory demo script
- Add SQLite memory backbone documentation
- Finalize v0.2 formatting and SQLite memory configuration

## v0.1 (Initial)

- Initialize project structure
- Add OpenClaw configuration
- Add Harness skill
- Add Darwin skill
- Add system prompt and task execution template
- Define architecture and roadmap
