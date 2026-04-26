"""Demo: fetch public GitHub repository context.

Usage:
    python3 runtime/repo/demo_github_fetcher.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

# Ensure project root is importable when running this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from runtime.repo.github_fetcher import GitHubRepoFetcher


def main() -> None:
    fetcher = GitHubRepoFetcher()
    context = fetcher.fetch("https://github.com/emmadong521-beep/agent-os")
    output = asdict(context)

    if output["readme"]:
        output["readme"] = output["readme"][:500]

    output["key_files"] = {
        name: content[:500]
        for name, content in output["key_files"].items()
    }

    print(json.dumps(output, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
