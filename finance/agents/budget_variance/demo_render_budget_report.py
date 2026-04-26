from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from finance.agents.budget_variance.analyzer import analyze_budget_variance
from finance.agents.budget_variance.report_renderer import render_budget_variance_report
from finance.common.csv_loader import load_budget_actual_csv


DEFAULT_SAMPLE_PATH = REPO_ROOT / "finance" / "examples" / "budget_actual_sample.csv"


def main() -> None:
    dataset = load_budget_actual_csv(str(DEFAULT_SAMPLE_PATH))
    summary = analyze_budget_variance(dataset)
    report = render_budget_variance_report(summary)
    print(report)


if __name__ == "__main__":
    main()
