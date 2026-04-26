"""Demo: validate the v0.3 executor abstraction with MockExecutor.

Usage:
    python runtime/executors/demo_executor.py
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


def main() -> None:
    task = Task(
        task_id="task-demo-executor-001",
        title="Validate executor abstraction",
        description="Run a sample task through MockExecutor.",
        project_name="agent-os",
        workflow_name="standard_task",
        metadata={"source": "demo_executor"},
    )
    context = ExecutionContext(
        session_id=1,
        agent_name="main-agent",
        workspace_path=str(PROJECT_ROOT),
        memory_prefetch={
            "project_context": [
                {
                    "title": "Agent OS executor plan",
                    "content": "Executors share a single BaseExecutor contract.",
                }
            ],
            "patterns": [
                {
                    "title": "Use adapters for external runners",
                    "content": "Keep workflow code independent of runner details.",
                }
            ],
            "anti_patterns": [],
            "relevant_memories": [
                {
                    "title": "v0.2 memory backbone",
                    "content": "Prefetch returns structured context before execution.",
                }
            ],
        },
    )

    executor = MockExecutor()
    result = executor.execute(task, context)
    print(json.dumps(asdict(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
