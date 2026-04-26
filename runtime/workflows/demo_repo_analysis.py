"""Demo: run the v0.8 RepoAnalysisWorkflow with GitHub RepoContext.

Usage:
    python3 runtime/workflows/demo_repo_analysis.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

# Ensure project root is importable when running this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from runtime.executors.mock_executor import MockExecutor
from runtime.memory.init_db import init_db
from runtime.memory.memory_service import MemoryService
from runtime.repo.github_fetcher import GitHubRepoFetcher
from runtime.reflection.darwin_reflector import DarwinReflector
from runtime.workflows.repo_analysis import RepoAnalysisInput, RepoAnalysisWorkflow
from runtime.workflows.standard_task import StandardTaskWorkflow


def main() -> None:
    init_db()
    memory_service = MemoryService()
    standard_workflow = StandardTaskWorkflow(
        memory_service=memory_service,
        executor=MockExecutor(),
        reflector=DarwinReflector(),
    )
    workflow = RepoAnalysisWorkflow(standard_workflow=standard_workflow)
    repo_context = GitHubRepoFetcher().fetch(
        "https://github.com/emmadong521-beep/agent-os"
    )

    input_data = RepoAnalysisInput(
        repo_url="https://github.com/emmadong521-beep/agent-os",
        repo_name="agent-os",
        project_name="agent-os",
        repo_context=repo_context,
    )

    result = workflow.run(input_data)
    memory_service.close()

    print(json.dumps(asdict(result), indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
