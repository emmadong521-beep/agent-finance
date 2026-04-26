"""Demo: run the v0.5 StandardTaskWorkflow end to end.

Usage:
    python3 runtime/workflows/demo_workflow.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

# Ensure project root is importable when running this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from runtime.executors.base_executor import ExecutionContext, Task
from runtime.executors.mock_executor import MockExecutor
from runtime.memory.init_db import init_db
from runtime.memory.memory_service import MemoryService
from runtime.reflection.darwin_reflector import DarwinReflector
from runtime.workflows.standard_task import StandardTaskWorkflow


def main() -> None:
    init_db()
    memory_service = MemoryService()
    executor = MockExecutor()
    reflector = DarwinReflector()
    workflow = StandardTaskWorkflow(
        memory_service=memory_service,
        executor=executor,
        reflector=reflector,
    )

    task = Task(
        task_id="task-demo-workflow-001",
        title="Validate standard task workflow",
        description="Run memory prefetch executor reflection and writeback.",
        project_name="agent-os",
        workflow_name="standard_task",
        metadata={"stage": "v0.5"},
    )
    context = ExecutionContext(
        agent_name="workflow-demo",
        workspace_path=str(PROJECT_ROOT),
    )

    result = workflow.run(task, context)
    memory_service.close()

    print(json.dumps(asdict(result), indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
