"""Rule-based repository analyzer executor.

v0.9 scope: generate a structured Markdown report from RepoContext-enriched
task descriptions without cloning repositories or calling external tools.
"""

from __future__ import annotations

import ast
from typing import Any

from runtime.executors.base_executor import (
    BaseExecutor,
    ExecutionContext,
    ExecutionResult,
    Task,
)


class RepoAnalyzerExecutor(BaseExecutor):
    """Analyze repository context using deterministic rules."""

    def name(self) -> str:
        return "repo-analyzer"

    def is_available(self) -> bool:
        return True

    def execute(self, task: Task, context: ExecutionContext) -> ExecutionResult:
        repo_name = str(task.metadata.get("repo_name") or task.project_name or "unknown")
        repo_url = task.metadata.get("repo_url")
        repo_context_used = bool(task.metadata.get("repo_context_used"))

        parsed = self._parse_description(task.description)
        report = self._build_report(
            repo_name=repo_name,
            repo_url=repo_url if isinstance(repo_url, str) else None,
            repo_context_used=repo_context_used,
            parsed=parsed,
        )

        return ExecutionResult(
            task_id=task.task_id,
            executor_name=self.name(),
            status="completed",
            summary=f"Rule-based repo analysis completed for {repo_name}",
            output=report,
            metadata={
                "repo_name": repo_name,
                "repo_url": repo_url,
                "repo_context_used": repo_context_used,
                "analyzer_type": "rule_based",
            },
        )

    def _parse_description(self, description: str) -> dict[str, Any]:
        lines = description.splitlines()
        parsed: dict[str, Any] = {
            "default_branch": self._line_value(lines, "Default branch:"),
            "metadata": self._parse_metadata(self._line_value(lines, "Repository metadata:")),
            "readme_excerpt": self._section_text(
                lines,
                "README excerpt:",
                "Root file tree first 50 entries:",
            ),
            "file_tree": self._section_lines(
                lines,
                "Root file tree first 50 entries:",
                "Key files:",
            ),
            "key_files": self._parse_key_files(lines),
            "key_file_excerpts": self._parse_key_file_excerpts(lines),
        }
        return parsed

    def _build_report(
        self,
        repo_name: str,
        repo_url: str | None,
        repo_context_used: bool,
        parsed: dict[str, Any],
    ) -> str:
        file_tree = parsed["file_tree"]
        key_files = parsed["key_files"]
        key_file_excerpts = parsed["key_file_excerpts"]
        metadata = parsed["metadata"]
        readme_excerpt = parsed["readme_excerpt"]
        default_branch = parsed["default_branch"] or "unknown"

        sections = [
            "## Overview",
            self._overview(repo_name, repo_url, repo_context_used, metadata, readme_excerpt),
            "## Architecture Signals",
            self._architecture_signals(file_tree, key_files),
            "## Modules",
            self._modules(file_tree),
            "## Data Flow",
            self._data_flow(key_files, key_file_excerpts),
            "## System Design",
            self._system_design(repo_name, default_branch, repo_context_used),
            "## Engineering Notes",
            self._engineering_notes(metadata, file_tree, key_files),
            "## Limitations",
            (
                "This is rule-based analysis only. It does not recursively scan source "
                "files, does not call an LLM, does not clone the repository, and does "
                "not invoke Codex, Hermes, Claude Code, or Paperclip."
            ),
        ]
        return "\n\n".join(sections)

    def _overview(
        self,
        repo_name: str,
        repo_url: str | None,
        repo_context_used: bool,
        metadata: dict[str, Any],
        readme_excerpt: str,
    ) -> str:
        description = metadata.get("description") or "No description metadata found."
        language = metadata.get("language") or "unknown"
        readme_signal = self._compact(readme_excerpt, 320) or "No README excerpt found."
        return (
            f"Repository `{repo_name}` ({repo_url or 'no URL'}) was analyzed with "
            f"repo_context_used={repo_context_used}. Description: {description}. "
            f"Primary language metadata: {language}.\n\nREADME signal: {readme_signal}"
        )

    def _architecture_signals(
        self,
        file_tree: list[str],
        key_files: list[str],
    ) -> str:
        signals: list[str] = []
        lower_files = {item.lower() for item in file_tree + key_files}

        if "package.json" in lower_files:
            signals.append("`package.json` suggests a Node/TypeScript/JavaScript project.")
        if "pyproject.toml" in lower_files or "requirements.txt" in lower_files:
            signals.append("Python packaging files suggest a Python project.")
        if "dockerfile" in lower_files:
            signals.append("`Dockerfile` suggests containerization support.")
        if "readme.md" in lower_files:
            signals.append("`README.md` provides first-pass product and architecture context.")

        if not signals:
            signals.append("No high-signal package or deployment files were found at root.")

        signals.append(f"Root entries observed: {file_tree[:30]}.")
        signals.append(f"Key files fetched: {key_files or 'none'}.")
        return "\n".join(f"- {signal}" for signal in signals)

    def _modules(self, file_tree: list[str]) -> str:
        module_hints = {
            "docs": "documentation and design notes",
            "client": "frontend/client application",
            "server": "backend/server application",
            "src": "primary source tree",
            "runtime": "runtime implementation layer",
            "contracts": "JSON schemas or interface contracts",
            "memory": "memory persistence assets",
        }
        found = []
        lower_entries = {item.lower(): item for item in file_tree}
        for key, meaning in module_hints.items():
            if key in lower_entries:
                found.append(f"`{lower_entries[key]}`: {meaning}")

        if not found:
            return "No known module directory hints were found in the root file tree."
        return "\n".join(f"- {item}" for item in found)

    def _data_flow(
        self,
        key_files: list[str],
        key_file_excerpts: dict[str, str],
    ) -> str:
        available = ", ".join(key_files) if key_files else "no key files"
        excerpt_signal = ""
        if key_file_excerpts:
            excerpt_signal = (
                " Key file excerpts were available, but they are root-level snippets "
                "and not enough for source-level data-flow claims."
            )
        return (
            f"Only README, root file tree, and {available} were inspected. "
            "The executor cannot infer complete runtime data flow without recursive "
            f"source inspection.{excerpt_signal}"
        )

    def _system_design(
        self,
        repo_name: str,
        default_branch: str,
        repo_context_used: bool,
    ) -> str:
        return (
            f"`{repo_name}` was analyzed from default_branch `{default_branch}`. "
            "RepoAnalysisWorkflow injected RepoContext into Task.description, then "
            "StandardTaskWorkflow ran this executor, Darwin reflection, and memory "
            f"writeback. repo_context_used={repo_context_used}."
        )

    def _engineering_notes(
        self,
        metadata: dict[str, Any],
        file_tree: list[str],
        key_files: list[str],
    ) -> str:
        notes = [
            f"Root file count inspected: {len(file_tree)}.",
            f"Key files inspected: {key_files or 'none'}.",
        ]
        for key in ("stars", "forks", "open_issues", "license"):
            if key in metadata:
                notes.append(f"{key}: {metadata[key]}.")
        return "\n".join(f"- {note}" for note in notes)

    def _line_value(self, lines: list[str], prefix: str) -> str:
        for line in lines:
            if line.startswith(prefix):
                return line.removeprefix(prefix).strip()
        return ""

    def _section_lines(
        self,
        lines: list[str],
        start_marker: str,
        end_marker: str,
    ) -> list[str]:
        text = self._section_text(lines, start_marker, end_marker)
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _section_text(
        self,
        lines: list[str],
        start_marker: str,
        end_marker: str,
    ) -> str:
        try:
            start = lines.index(start_marker) + 1
        except ValueError:
            return ""

        end = len(lines)
        for idx in range(start, len(lines)):
            if lines[idx].startswith(end_marker):
                end = idx
                break
        return "\n".join(lines[start:end]).strip()

    def _parse_metadata(self, raw_metadata: str) -> dict[str, Any]:
        if not raw_metadata:
            return {}
        try:
            value = ast.literal_eval(raw_metadata)
        except (SyntaxError, ValueError):
            return {"raw": raw_metadata}
        if isinstance(value, dict):
            return value
        return {"raw": raw_metadata}

    def _parse_key_files(self, lines: list[str]) -> list[str]:
        raw_key_files = self._line_value(lines, "Key files:")
        if not raw_key_files:
            return []
        try:
            value = ast.literal_eval(raw_key_files)
        except (SyntaxError, ValueError):
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        return []

    def _parse_key_file_excerpts(self, lines: list[str]) -> dict[str, str]:
        excerpts: dict[str, str] = {}
        current_name: str | None = None
        current_lines: list[str] = []

        for line in lines:
            if line.startswith("Key file excerpt:"):
                if current_name is not None:
                    excerpts[current_name] = "\n".join(current_lines).strip()
                current_name = line.removeprefix("Key file excerpt:").strip()
                current_lines = []
            elif current_name is not None:
                current_lines.append(line)

        if current_name is not None:
            excerpts[current_name] = "\n".join(current_lines).strip()
        return excerpts

    def _compact(self, value: str, limit: int) -> str:
        return " ".join(value.split())[:limit]
