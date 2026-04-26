# Repo Analyzer Executor

## Why This Executor Exists

`MockExecutor` validates the execution contract, but it intentionally returns a
generic response. Repo analysis needs an executor that can turn fetched
repository context into a useful first-pass report while still avoiding external
tools.

`RepoAnalyzerExecutor` fills that gap for v0.9. It is deterministic, local, and
rule-based.

## How It Differs From MockExecutor

`MockExecutor` always returns a completed placeholder result.

`RepoAnalyzerExecutor` reads the `Task.description` produced by
`RepoAnalysisWorkflow`, extracts RepoContext signals, and generates Markdown with
these sections:

- Overview
- Architecture Signals
- Modules
- Data Flow
- System Design
- Engineering Notes
- Limitations

## How It Uses RepoContext

v0.8 injects RepoContext into the task description: default branch, metadata,
README excerpt, root file tree, key file names, and key file excerpts. The
executor parses those text markers and applies conservative rules.

For example, `package.json` suggests a Node/TypeScript/JavaScript project,
`pyproject.toml` or `requirements.txt` suggests Python, and `Dockerfile`
suggests containerization. Known root directories such as `runtime`, `contracts`,
`memory`, `docs`, `client`, `server`, and `src` become module hints.

## v0.9 Boundaries

This executor does not clone repositories, recursively scan source files, call
an LLM, or invoke Codex, Hermes, Claude Code, or Paperclip. Its data-flow notes
are intentionally conservative because README, root tree, and key files are not
enough for source-level claims.

## Future Replacement

Codex, Hermes, or Claude Code can later replace this executor behind the same
`BaseExecutor` interface. Those adapters can perform deeper source inspection
and still return an `ExecutionResult` that the workflow and Darwin reflection
layers already understand.
