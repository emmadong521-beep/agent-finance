from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from finance.common.csv_loader import load_budget_actual_csv


DEFAULT_SAMPLE_PATH = REPO_ROOT / "finance" / "examples" / "budget_actual_sample.csv"


def main() -> None:
    dataset = load_budget_actual_csv(str(DEFAULT_SAMPLE_PATH))
    material_variances = dataset.material_variances()

    summary = {
        "source_path": dataset.source_path,
        "periods": dataset.periods(),
        "departments": dataset.departments(),
        "accounts": dataset.accounts(),
        "record_count": len(dataset.records),
        "total_budget": dataset.total_budget(),
        "total_actual": dataset.total_actual(),
        "total_variance": dataset.total_variance(),
        "material_variance_count": len(material_variances),
        "material_variances": [asdict(record) for record in material_variances[:5]],
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
