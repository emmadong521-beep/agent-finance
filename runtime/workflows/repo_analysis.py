"""Repository analysis workflow for Agent OS v0.6."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from runtime.executors.base_executor import ExecutionContext, Task
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
        project_name = input.project_name or input.repo_name
        task = Task(
            task_id=f"repo-analysis:{input.repo_name}",
            title=f"Analyze repository: {input.repo_name}",
            description=self._build_task_description(input),
            project_name=project_name,
            workflow_name=self.workflow_name,
            metadata={
                "repo_name": input.repo_name,
                "repo_url": input.repo_url,
                "local_path": input.local_path,
                **input.metadata,
            },
        )
        context = ExecutionContext(
            agent_name="repo-analysis",
            metadata={
                "workflow_name": self.workflow_name,
                "repo_name": input.repo_name,
            },
        )

        workflow_result = self.standard_workflow.run(task, context)
        analysis_sections = self._build_analysis_sections(input, workflow_result)

        return RepoAnalysisResult(
            repo_name=input.repo_name,
            repo_url=input.repo_url,
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
                "mock_analysis": True,
            },
        )

    def _build_task_description(self, input: RepoAnalysisInput) -> str:
        repo_url = input.repo_url or "not provided"
        local_path = input.local_path or "not provided"
        return (
            f"Repository name: {input.repo_name}\n"
            f"Repository URL: {repo_url}\n"
            f"Local path: {local_path}\n"
            f"Analysis goal: {input.analysis_goal}\n"
            "v0.6 should route this through the standard workflow without "
            "cloning or invoking a real LLM."
        )

    def _build_summary(
        self,
        input: RepoAnalysisInput,
        workflow_result: WorkflowResult,
    ) -> str:
        return (
            f"Repo analysis workflow for '{input.repo_name}' finished with "
            f"status '{workflow_result.status}'. {workflow_result.execution_summary}"
        )

    def _build_analysis_sections(
        self,
        input: RepoAnalysisInput,
        workflow_result: WorkflowResult,
    ) -> dict[str, str]:
        source = input.repo_url or input.local_path or input.repo_name
        return {
            "overview": (
                f"Placeholder overview for {input.repo_name}. Source: {source}. "
                f"Goal: {input.analysis_goal}."
            ),
            "architecture": (
                "Architecture analysis is routed through StandardTaskWorkflow. "
                "v0.6 does not inspect repository files or call an LLM."
            ),
            "modules": (
                "Module inventory is not populated in v0.6 because no clone or "
                "filesystem scan is performed."
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
                f"Workflow status: {workflow_result.status}. Written memory ids: "
                f"{workflow_result.written_memory_ids}."
            ),
        }
