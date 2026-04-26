# Changelog

## v1.3 - Budget Variance Analyzer

- Add budget variance analysis models
- Add material variance, direction, severity, and category classification
- Add department and category summaries
- Add insight flags for management review
- Add budget variance analysis demo and documentation

## v1.2 - Finance Data Loader

- Add BudgetActualRecord and FinanceDataset models
- Add budget actual CSV loader
- Add field validation and numeric parsing
- Add budget data loading demo
- Add budget actual input schema and documentation

## v1.1 - Finance MVP Repositioning

- Reposition project from generic Agent OS to Finance AI Agent System
- Add finance domain layer
- Add Budget Variance & Business Insight Agent scope
- Add budget variance report template
- Add sample budget vs actual data

## v1.0.1 - Chinese Repo Analysis Report

- Render repo analysis Markdown reports in Chinese
- Generate Chinese architecture, module, data-flow, and system-design sections
- Localize RepoAnalyzerExecutor Markdown output
- Document Chinese Markdown report behavior

## v1.0 - External Executor Adapter Preparation

- Add ExecutorRunConfig
- Add ExternalCommandExecutor for safe command execution
- Upgrade Codex, Claude Code, and Hermes executors to external command adapters
- Add dry-run and execute controls to repo analysis CLI
- Document external executor safety model

## v0.9.1 - Repo Analysis Markdown Renderer

- Add render_repo_analysis_markdown for human-readable Markdown reports
- Add --format option to repo analysis CLI (json or markdown)
- Generate Mermaid module relationship graphs from analysis sections
- Document Markdown renderer

## v0.9 - Rule-Based Repo Analyzer Executor

- Add RepoAnalyzerExecutor for rule-based repository analysis
- Generate structured Markdown analysis from RepoContext-enriched task descriptions
- Add --executor option to repo analysis CLI
- Default repo analysis CLI to repo-analyzer
- Document repo analyzer executor

## v0.8.1 - Repo Analysis CLI

- Add command-line entrypoint for running repo analysis by GitHub URL
- Support project name and analysis goal options
- Support pretty and compact JSON output
- Document repo analysis CLI usage

## v0.8 - Repo Context Integration

- Integrate RepoContext into RepoAnalysisWorkflow
- Enrich repository analysis task descriptions with README, file tree, key files, and metadata
- Generate rule-based analysis sections from fetched repository context
- Update repo analysis demo to fetch GitHub context before workflow execution
- Document RepoContext integration

## v0.7 - GitHub Repo Fetcher

- Add RepoContext model
- Add GitHubRepoFetcher for public GitHub repositories
- Add README, root file tree, and key file collection
- Add repo context JSON schema
- Add GitHub repo fetcher documentation

## v0.6 - Repo Analysis Workflow

- Add RepoAnalysisInput and RepoAnalysisResult models
- Add RepoAnalysisWorkflow on top of StandardTaskWorkflow
- Add repo analysis demo
- Add repo analysis result JSON schema
- Add Repo Analysis Workflow documentation

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
