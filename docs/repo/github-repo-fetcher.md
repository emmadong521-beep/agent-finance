# GitHub Repo Fetcher

## Why Agent OS Needs a Repo Fetcher

Repo analysis needs real repository context before an executor can produce a
useful answer. v0.6 proved that repo analysis can flow through the standard
task loop. v0.7 adds a lightweight fetcher that collects public GitHub context
without adding infrastructure or cloning repositories.

`GitHubRepoFetcher` gives future workflows a structured `RepoContext` with
metadata, README text, root files, and selected key files.

## RepoContext Fields

- `repo_name`: repository name parsed from the GitHub URL.
- `repo_url`: original public GitHub URL.
- `default_branch`: default branch from the GitHub REST API.
- `readme`: README content when a supported README file is available.
- `file_tree`: root directory file names only.
- `key_files`: content for known high-signal files that were found.
- `metadata`: GitHub metadata such as owner, description, stars, language,
  forks, open issues, license, and HTML URL.

## v0.7 Boundaries

v0.7 uses only Python standard library `urllib.request`. It does not introduce
external dependencies.

It does not do authentication, private repository access, recursive tree walks,
git clone, real LLM analysis, real Hermes/Claude Code/Codex execution, or
Paperclip orchestration.

Network errors are raised as clear runtime exceptions. Missing README or key
files are skipped instead of failing the whole fetch.

## Future Integrations

`RepoAnalysisWorkflow` can accept `RepoContext` and include README, root tree,
and key files in its generated task description.

Codex or Hermes can use the fetched context as a lightweight first pass before
deeper repository inspection.

Paperclip can coordinate multiple fetch and analysis workers, fan out by module
or file type, and merge their results into a repository-level report.
