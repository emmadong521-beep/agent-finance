"""Base executor contract for Agent OS.

v0.3 scope: define a stable execution interface that workflows can call
without binding directly to Hermes, Claude Code, Codex, or any future runner.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Task:
    """A unit of work to be executed by an executor."""

    task_id: str
    title: str
    description: str
    project_name: str | None = None
    workflow_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExecutionContext:
    """Context supplied to an executor before a task starts."""

    session_id: int | None = None
    agent_name: str | None = None
    workspace_path: str | None = None
    memory_prefetch: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExecutionResult:
    """Normalized result returned by every executor."""

    task_id: str
    executor_name: str
    status: str
    summary: str
    output: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseExecutor(ABC):
    """Abstract interface shared by all execution backends."""

    @abstractmethod
    def name(self) -> str:
        """Return the stable executor name."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether this executor can run in the current environment."""

    @abstractmethod
    def execute(self, task: Task, context: ExecutionContext) -> ExecutionResult:
        """Execute a task and return a normalized result."""
