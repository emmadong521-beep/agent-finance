"""Workflow result models for Agent OS."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WorkflowResult:
    """Normalized result returned by a workflow run."""

    task_id: str
    workflow_name: str
    status: str
    execution_summary: str
    reflection_summary: str
    written_memory_ids: list[int]
    output: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
