"""CLI entrypoint for running RepoAnalysisWorkflow by GitHub URL.

Usage:
    python3 runtime/workflows/run_repo_analysis.py https://github.com/owner/repo
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

# Ensure project root is importable when running this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from runtime.executors.mock_executor import MockExecutor
from runtime.executors.repo_analyzer_executor import RepoAnalyzerExecutor
from runtime.memory.init_db import init_db
from runtime.memory.memory_service import MemoryService
from runtime.reflection.darwin_reflector import DarwinReflector
from runtime.repo.github_fetcher import GitHubRepoFetcher
from runtime.workflows.repo_analysis import RepoAnalysisInput, RepoAnalysisWorkflow
from runtime.workflows.standard_task import StandardTaskWorkflow


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Agent OS repo analysis for a public GitHub repository.",
    )
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument(
        "--project-name",
        help="Project name to use for memory scope. Defaults to repo_name.",
    )
    parser.add_argument(
        "--analysis-goal",
        default="Analyze repository architecture",
        help="Analysis goal to include in the workflow task.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Print pretty JSON output. Enabled by default.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Print compact JSON output.",
    )
    parser.add_argument(
        "--executor",
        default="repo-analyzer",
        choices=("mock", "repo-analyzer"),
        help="Executor to use: repo-analyzer or mock. Defaults to repo-analyzer.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    memory_service: MemoryService | None = None

    try:
        fetcher = GitHubRepoFetcher()
        _, repo_name = fetcher.parse_repo_url(args.repo_url)
        repo_context = fetcher.fetch(args.repo_url)

        init_db()
        memory_service = MemoryService()
        executor = build_executor(args.executor)
        standard_workflow = StandardTaskWorkflow(
            memory_service=memory_service,
            executor=executor,
            reflector=DarwinReflector(),
        )
        workflow = RepoAnalysisWorkflow(standard_workflow=standard_workflow)

        input_data = RepoAnalysisInput(
            repo_url=args.repo_url,
            repo_name=repo_name,
            project_name=args.project_name or repo_name,
            analysis_goal=args.analysis_goal,
            repo_context=repo_context,
        )
        result = workflow.run(input_data)

        if args.compact:
            print(json.dumps(asdict(result), separators=(",", ":"), default=str))
        else:
            print(json.dumps(asdict(result), indent=2, sort_keys=True, default=str))
        return 0
    except Exception as exc:
        print(f"ERROR: repo analysis failed: {exc}", file=sys.stderr)
        return 1
    finally:
        if memory_service is not None:
            memory_service.close()


def build_executor(name: str) -> MockExecutor | RepoAnalyzerExecutor:
    if name == "mock":
        return MockExecutor()
    if name == "repo-analyzer":
        return RepoAnalyzerExecutor()
    print(f"ERROR: unknown executor '{name}'", file=sys.stderr)
    raise SystemExit(2)


if __name__ == "__main__":
    raise SystemExit(main())
