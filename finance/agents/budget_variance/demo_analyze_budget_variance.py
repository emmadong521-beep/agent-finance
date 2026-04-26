from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from finance.agents.budget_variance.analyzer import analyze_budget_variance
from finance.common.csv_loader import load_budget_actual_csv


DEFAULT_SAMPLE_PATH = REPO_ROOT / "finance" / "examples" / "budget_actual_sample.csv"


def main() -> None:
    dataset = load_budget_actual_csv(str(DEFAULT_SAMPLE_PATH))
    analysis = analyze_budget_variance(dataset)

    summary = {
        "periods": analysis.periods,
        "total_budget": analysis.total_budget,
        "total_actual": analysis.total_actual,
        "total_variance": analysis.total_variance,
        "total_variance_rate": analysis.total_variance_rate,
        "material_variance_count": analysis.material_variance_count,
        "unfavorable_variance_count": analysis.unfavorable_variance_count,
        "favorable_variance_count": analysis.favorable_variance_count,
        "insight_flags": analysis.insight_flags,
        "major_items": [asdict(item) for item in analysis.major_items[:10]],
        "department_summary": analysis.department_summary,
        "category_summary": analysis.category_summary,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
