# Repo Analysis Workflow

## Why Agent OS Needs Repo Analysis

Repository analysis is a common task shape for Agent OS: inspect a codebase,
summarize architecture, identify modules, and preserve reusable findings. It
should use the same memory, execution, reflection, and writeback loop as other
tasks instead of becoming a separate path.

`RepoAnalysisWorkflow` is the v0.6 facade that routes repository analysis
requests into `StandardTaskWorkflow`.

## Input and Result Models

`RepoAnalysisInput` describes the repository target and goal:

- `repo_url`
- `local_path`
- `repo_name`
- `analysis_goal`
- `project_name`
- `metadata`

`RepoAnalysisResult` returns the repository-specific view:

- repository identity fields
- status and summary
- `analysis_sections`
- nested `WorkflowResult`
- written memory ids
- metadata

The required analysis sections are `overview`, `architecture`, `modules`,
`data_flow`, `system_design`, and `engineering_notes`.

## Reusing StandardTaskWorkflow

The repo workflow converts `RepoAnalysisInput` into a normal executor `Task`.
It then creates an `ExecutionContext` with `agent_name = "repo-analysis"` and
calls `StandardTaskWorkflow.run()`.

That means repo analysis automatically gets:

- memory prefetch from SQLite
- executor execution through the v0.3 interface
- Darwin reflection
- SQLite memory writeback
- a normalized `WorkflowResult`

## v0.6 Boundaries

v0.6 does not clone repositories, fetch GitHub contents, scan local files, or
call a real LLM. The analysis sections are placeholders derived from the
workflow result and request metadata.

v0.6 also does not connect real Hermes, Claude Code, Codex, AutoResearch, or
Paperclip. It proves the workflow shape without adding infrastructure.

## Future Extensions

GitHub fetch can populate repository metadata, trees, README content, and issue
context before execution.

Codex or Hermes can replace `MockExecutor` to perform real codebase inspection
through the existing executor abstraction.

AutoResearch can add source collection, citations, and external context for
repository analysis tasks.

Paperclip can coordinate multiple repo analysis agents, split work by module,
and aggregate their `RepoAnalysisResult` objects into a higher-level report.
