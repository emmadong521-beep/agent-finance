"""Repository analysis workflow for Agent OS v0.8."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from runtime.executors.base_executor import ExecutionContext, Task
from runtime.repo.repo_models import RepoContext
from runtime.workflows.standard_task import StandardTaskWorkflow
from runtime.workflows.workflow_models import WorkflowResult


@dataclass(slots=True)
class RepoAnalysisInput:
    """Input for repository analysis requests."""

    repo_name: str
    repo_url: str | None = None
    local_path: str | None = None
    analysis_goal: str = "Analyze repository architecture"
    project_name: str | None = None
    repo_context: RepoContext | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RepoAnalysisResult:
    """Normalized result for repository analysis workflows."""

    repo_name: str
    repo_url: str | None
    local_path: str | None
    status: str
    summary: str
    analysis_sections: dict[str, str]
    workflow_result: WorkflowResult
    written_memory_ids: list[int]
    metadata: dict[str, Any] = field(default_factory=dict)


class RepoAnalysisWorkflow:
    """Run repository analysis through the standard Agent OS task loop."""

    workflow_name = "repo_analysis"

    def __init__(self, standard_workflow: StandardTaskWorkflow) -> None:
        self.standard_workflow = standard_workflow

    def run(self, input: RepoAnalysisInput) -> RepoAnalysisResult:
        repo_name = self._repo_name(input)
        repo_url = self._repo_url(input)
        project_name = input.project_name or repo_name
        task = Task(
            task_id=f"repo-analysis:{repo_name}",
            title=f"Analyze repository: {repo_name}",
            description=self._build_task_description(input),
            project_name=project_name,
            workflow_name=self.workflow_name,
            metadata={
                "repo_name": repo_name,
                "repo_url": repo_url,
                "local_path": input.local_path,
                "repo_context_used": input.repo_context is not None,
                **input.metadata,
            },
        )
        context = ExecutionContext(
            agent_name="repo-analysis",
            metadata={
                "workflow_name": self.workflow_name,
                "repo_name": repo_name,
            },
        )

        workflow_result = self.standard_workflow.run(task, context)
        analysis_sections = self._build_analysis_sections(input, workflow_result)

        return RepoAnalysisResult(
            repo_name=repo_name,
            repo_url=repo_url,
            local_path=input.local_path,
            status=workflow_result.status,
            summary=self._build_summary(input, workflow_result),
            analysis_sections=analysis_sections,
            workflow_result=workflow_result,
            written_memory_ids=workflow_result.written_memory_ids,
            metadata={
                "project_name": project_name,
                "workflow_name": self.workflow_name,
                "source_workflow_name": workflow_result.workflow_name,
                "repo_context_used": input.repo_context is not None,
                "default_branch": self._default_branch(input),
                "file_tree_count": len(self._file_tree(input)),
                "key_files": list(self._key_files(input).keys()),
                "mock_analysis": input.repo_context is None,
            },
        )

    def _build_task_description(self, input: RepoAnalysisInput) -> str:
        repo_name = self._repo_name(input)
        repo_url = self._repo_url(input) or "not provided"
        local_path = input.local_path or "not provided"
        lines = [
            f"Repository name: {repo_name}",
            f"Repository URL: {repo_url}",
            f"Local path: {local_path}",
            f"Analysis goal: {input.analysis_goal}",
        ]

        if input.repo_context is None:
            lines.append(
                "No RepoContext was provided. Preserve v0.6 behavior without "
                "cloning or invoking a real LLM."
            )
            return "\n".join(lines)

        metadata = self._metadata(input)
        file_tree = self._file_tree(input)
        key_files = self._key_files(input)
        readme = input.repo_context.readme or ""

        lines.extend(
            [
                f"Default branch: {self._default_branch(input) or 'unknown'}",
                f"Repository metadata: {metadata}",
                "README excerpt:",
                self._truncate(readme, 1200) or "not available",
                "Root file tree first 50 entries:",
                "\n".join(file_tree[:50]) or "not available",
                f"Key files: {list(key_files.keys())}",
            ]
        )

        for name, content in key_files.items():
            lines.extend(
                [
                    f"Key file excerpt: {name}",
                    self._truncate(content, 800),
                ]
            )

        return "\n".join(lines)

    def _build_summary(
        self,
        input: RepoAnalysisInput,
        workflow_result: WorkflowResult,
    ) -> str:
        repo_name = self._repo_name(input)
        return (
            f"Repo analysis workflow for '{repo_name}' finished with "
            f"status '{workflow_result.status}'. {workflow_result.execution_summary}"
        )

    def _build_analysis_sections(
        self,
        input: RepoAnalysisInput,
        workflow_result: WorkflowResult,
    ) -> dict[str, str]:
        repo_context_used = input.repo_context is not None
        repo_name = self._repo_name(input)
        source = self._repo_url(input) or input.local_path or repo_name
        metadata = self._metadata(input)
        file_tree = self._file_tree(input)
        key_files = self._key_files(input)
        readme_summary = (
            self._truncate(input.repo_context.readme, 500)
            if input.repo_context
            else ""
        )

        if not repo_context_used:
            return {
                "overview": (
                    f"Placeholder overview for {repo_name}. Source: {source}. "
                    f"Goal: {input.analysis_goal}."
                ),
                "architecture": (
                    "Architecture analysis is routed through StandardTaskWorkflow. "
                    "No RepoContext was provided, so v0.6 placeholder behavior is preserved."
                ),
                "modules": (
                    "Module inventory is not populated because no RepoContext, clone, "
                    "or filesystem scan is available."
                ),
                "data_flow": (
                    "Data flow is represented by the Agent OS loop: memory prefetch, "
                    "executor execution, Darwin reflection, and memory writeback."
                ),
                "system_design": (
                    "RepoAnalysisWorkflow is a specialized workflow facade on top of "
                    "StandardTaskWorkflow."
                ),
                "engineering_notes": (
                    "repo_context_used=False; default_branch=None; file_tree_count=0; "
                    f"key_files=[]; written_memory_ids={workflow_result.written_memory_ids}."
                ),
            }

        directories = [item for item in file_tree if "." not in item]
        files = [item for item in file_tree if "." in item]
        return {
            "overview": (
                f"Rule-based overview for {repo_name}. Source: {source}. "
                f"Metadata: {metadata}. README signal: {readme_summary or 'not available'}"
            ),
            "architecture": (
                "Architecture clues come from the root file tree and key files. "
                f"Root entries include {file_tree[:20]}. Key files available: "
                f"{list(key_files.keys())}."
            ),
            "modules": (
                f"Root directories: {directories or 'none detected'}. "
                f"Root files: {files or 'none detected'}."
            ),
            "data_flow": (
                "Data flow cannot be fully determined from README, root file tree, "
                "and key files alone. v0.8 reports only conservative structural "
                "signals without recursive scanning or LLM analysis."
            ),
            "system_design": (
                "RepoAnalysisWorkflow converts RepoContext into a Task description, "
                "then enters StandardTaskWorkflow for memory prefetch, executor "
                "execution, Darwin reflection, and memory writeback."
            ),
            "engineering_notes": (
                f"repo_context_used=True; default_branch={self._default_branch(input)}; "
                f"file_tree_count={len(file_tree)}; key_files={list(key_files.keys())}; "
                f"written_memory_ids={workflow_result.written_memory_ids}."
            ),
        }

    def _repo_name(self, input: RepoAnalysisInput) -> str:
        if input.repo_context is not None:
            return input.repo_context.repo_name
        return input.repo_name

    def _repo_url(self, input: RepoAnalysisInput) -> str | None:
        if input.repo_context is not None:
            return input.repo_context.repo_url
        return input.repo_url

    def _default_branch(self, input: RepoAnalysisInput) -> str | None:
        if input.repo_context is not None:
            return input.repo_context.default_branch
        return None

    def _metadata(self, input: RepoAnalysisInput) -> dict[str, Any]:
        if input.repo_context is not None:
            return input.repo_context.metadata
        return {}

    def _file_tree(self, input: RepoAnalysisInput) -> list[str]:
        if input.repo_context is not None:
            return input.repo_context.file_tree
        return []

    def _key_files(self, input: RepoAnalysisInput) -> dict[str, str]:
        if input.repo_context is not None:
            return input.repo_context.key_files
        return {}

    def _truncate(self, value: str | None, limit: int) -> str:
        if not value:
            return ""
        return value[:limit]
