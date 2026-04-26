"""Standard task workflow for Agent OS v0.5."""

from __future__ import annotations

from runtime.executors.base_executor import BaseExecutor, ExecutionContext, Task
from runtime.memory.memory_service import MemoryService
from runtime.reflection.darwin_reflector import DarwinReflector
from runtime.workflows.workflow_models import WorkflowResult


class StandardTaskWorkflow:
    """Connect memory prefetch, execution, reflection, and memory writeback."""

    workflow_name = "standard_task"

    def __init__(
        self,
        memory_service: MemoryService,
        executor: BaseExecutor,
        reflector: DarwinReflector,
    ) -> None:
        self.memory_service = memory_service
        self.executor = executor
        self.reflector = reflector

    def run(self, task: Task, context: ExecutionContext) -> WorkflowResult:
        project_name = task.project_name or "default"
        task_keywords = self._build_task_keywords(task)
        session_id: int | None = None

        if task.project_name is None:
            task.project_name = project_name
        if task.workflow_name is None:
            task.workflow_name = self.workflow_name

        try:
            session_id = self.memory_service.create_session(
                task_title=task.title,
                project_name=project_name,
                agent_name=context.agent_name,
            )
            context.session_id = session_id

            prefetch = self.memory_service.prefetch_for_task(
                project_name=project_name,
                task_keywords=task_keywords,
            )
            context.memory_prefetch = prefetch

            execution_result = self.executor.execute(task, context)
            reflection = self.reflector.reflect(task, execution_result, context)
            written_memory_ids = self.reflector.writeback(
                reflection,
                self.memory_service,
                source_session_id=session_id,
            )

            workflow_status = (
                "completed"
                if execution_result.status == "completed"
                else execution_result.status
            )
            self.memory_service.end_session(
                session_id,
                status=workflow_status,
                summary=reflection.summary,
            )

            return WorkflowResult(
                task_id=task.task_id,
                workflow_name=self.workflow_name,
                status=workflow_status,
                execution_summary=execution_result.summary,
                reflection_summary=reflection.summary,
                written_memory_ids=written_memory_ids,
                output=execution_result.output,
                error=execution_result.error,
                metadata={
                    "project_name": project_name,
                    "session_id": session_id,
                    "executor_name": execution_result.executor_name,
                    "memory_prefetch_counts": self._count_prefetch(prefetch),
                },
            )
        except Exception as exc:
            if session_id is not None:
                self.memory_service.end_session(
                    session_id,
                    status="failed",
                    summary=f"Workflow failed: {exc}",
                )
            return WorkflowResult(
                task_id=task.task_id,
                workflow_name=self.workflow_name,
                status="failed",
                execution_summary="Workflow did not complete execution.",
                reflection_summary="Workflow failed before reflection completed.",
                written_memory_ids=[],
                error=str(exc),
                metadata={
                    "project_name": project_name,
                    "session_id": session_id,
                    "executor_name": self.executor.name(),
                },
            )

    def _count_prefetch(
        self,
        prefetch: dict[str, list[dict]],
    ) -> dict[str, int]:
        return {key: len(value) for key, value in prefetch.items()}

    def _build_task_keywords(self, task: Task) -> str:
        raw_keywords = f"{task.title} {task.description}"
        return "".join(
            char if char.isalnum() or char.isspace() else " "
            for char in raw_keywords
        )
