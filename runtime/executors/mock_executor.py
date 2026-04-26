"""Mock executor for local validation of the v0.3 execution contract."""

from __future__ import annotations

from typing import Any

from runtime.executors.base_executor import (
    BaseExecutor,
    ExecutionContext,
    ExecutionResult,
    Task,
)


class MockExecutor(BaseExecutor):
    """Executor that completes tasks without invoking external tools."""

    def name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    def execute(self, task: Task, context: ExecutionContext) -> ExecutionResult:
        memory_summary = self._summarize_memory_prefetch(context.memory_prefetch)
        return ExecutionResult(
            task_id=task.task_id,
            executor_name=self.name(),
            status="completed",
            summary=f"Mock executed task: {task.title}",
            output="No external command was invoked.",
            metadata={
                "project_name": task.project_name,
                "workflow_name": task.workflow_name,
                "memory_prefetch_summary": memory_summary,
            },
        )

    def _summarize_memory_prefetch(
        self,
        memory_prefetch: dict[str, Any],
    ) -> dict[str, int | str]:
        summary: dict[str, int | str] = {}
        for key, value in memory_prefetch.items():
            if isinstance(value, list):
                summary[key] = len(value)
            elif isinstance(value, dict):
                summary[key] = len(value)
            elif value is None:
                summary[key] = 0
            else:
                summary[key] = type(value).__name__
        return summary
