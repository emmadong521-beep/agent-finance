"""Placeholder Codex executor.

v0.3 only detects availability and returns a normalized skipped result.
It does not invoke Codex.
"""

from __future__ import annotations

import shutil

from runtime.executors.base_executor import (
    BaseExecutor,
    ExecutionContext,
    ExecutionResult,
    Task,
)


class CodexExecutor(BaseExecutor):
    """Executor adapter reserved for Codex."""

    command = "codex"

    def name(self) -> str:
        return "codex"

    def is_available(self) -> bool:
        return shutil.which(self.command) is not None

    def execute(self, task: Task, context: ExecutionContext) -> ExecutionResult:
        return ExecutionResult(
            task_id=task.task_id,
            executor_name=self.name(),
            status="not_implemented",
            summary="Codex executor is a v0.3 placeholder and did not run.",
            metadata={
                "command": self.command,
                "available": self.is_available(),
                "session_id": context.session_id,
            },
        )
