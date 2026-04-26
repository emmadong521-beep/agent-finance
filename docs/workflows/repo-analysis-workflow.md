# Repo Analysis Workflow

## Why Agent OS Needs Repo Analysis

Repository analysis is a common task shape for Agent OS: inspect a codebase,
summarize architecture, identify modules, and preserve reusable findings. It
should use the same memory, execution, reflection, and writeback loop as other
tasks instead of becoming a separate path.

`RepoAnalysisWorkflow` is the facade that routes repository analysis requests
into `StandardTaskWorkflow`. As of v0.8, it can also consume `RepoContext`
created by `GitHubRepoFetcher`.

## Input and Result Models

`RepoAnalysisInput` describes the repository target and goal:

- `repo_url`
- `local_path`
- `repo_name`
- `analysis_goal`
- `project_name`
- `repo_context`
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

## RepoContext Integration

`GitHubRepoFetcher` can fetch public repository context using the GitHub REST API
and raw content endpoints. The resulting `RepoContext` contains the default
branch, README content, root file tree, key files, and repository metadata.

When `RepoAnalysisInput.repo_context` is provided, `RepoAnalysisWorkflow` uses it
to enrich the generated task description with:

- default branch
- metadata
- README excerpt
- first 50 root file tree entries
- key file names
- key file excerpts

The workflow also generates rule-based analysis sections from this context.
These sections are conservative: they explain structural clues from README, root
files, and key files without claiming a full codebase analysis.

## CLI Usage

Run repo analysis directly from a GitHub URL:

```bash
python3 runtime/workflows/run_repo_analysis.py https://github.com/emmadong521-beep/agent-os
```

The CLI defaults to the rule-based `repo-analyzer` executor.

Use a custom project name:

```bash
python3 runtime/workflows/run_repo_analysis.py https://github.com/vercel/ai --project-name vercel-ai
```

Use compact JSON output:

```bash
python3 runtime/workflows/run_repo_analysis.py https://github.com/emmadong521-beep/agent-os --compact
```

Fallback to the old mock executor:

```bash
python3 runtime/workflows/run_repo_analysis.py https://github.com/emmadong521-beep/agent-os --executor mock
```

The current `repo-analyzer` is deterministic and rule-based. It is not an LLM
and does not inspect files beyond the RepoContext supplied by `GitHubRepoFetcher`.

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

## Boundaries

v0.8 supports `RepoContext`, but still does not clone repositories, recursively
scan local files, or call a real LLM. The analysis sections are rule-based and
derived from fetched README, root file tree, key files, metadata, and workflow
result.

It also does not connect real Hermes, Claude Code, Codex, AutoResearch, or
Paperclip. It proves the context integration shape without adding execution
infrastructure.

## Future Extensions

GitHub fetch can expand beyond root-level context into recursive trees, selected
source files, issue context, and pull request context.

Codex or Hermes can replace `MockExecutor` to perform real codebase inspection
through the existing executor abstraction.

AutoResearch can add source collection, citations, and external context for
repository analysis tasks.

Paperclip can coordinate multiple repo analysis agents, split work by module,
and aggregate their `RepoAnalysisResult` objects into a higher-level report.
