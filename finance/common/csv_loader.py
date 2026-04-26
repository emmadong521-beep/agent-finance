from __future__ import annotations

import csv
from pathlib import Path

from finance.common.finance_models import BudgetActualRecord, FinanceDataset


REQUIRED_FIELDS = [
    "period",
    "department",
    "account",
    "budget_amount",
    "actual_amount",
    "variance_amount",
    "variance_rate",
    "business_driver",
    "remark",
]


def load_budget_actual_csv(path: str) -> FinanceDataset:
    source_path = str(Path(path))
    records: list[BudgetActualRecord] = []

    with open(path, newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        _validate_required_fields(reader.fieldnames)

        for row_number, row in enumerate(reader, start=2):
            budget_amount = _parse_float(row, "budget_amount", row_number)
            actual_amount = _parse_float(row, "actual_amount", row_number)

            variance_amount_value = _clean_value(row.get("variance_amount"))
            if variance_amount_value == "":
                variance_amount = actual_amount - budget_amount
            else:
                variance_amount = _parse_float(row, "variance_amount", row_number)

            variance_rate_value = _clean_value(row.get("variance_rate"))
            if variance_rate_value == "":
                variance_rate = _calculate_variance_rate(
                    variance_amount=variance_amount,
                    budget_amount=budget_amount,
                )
            else:
                variance_rate = _parse_variance_rate(row, row_number)

            records.append(
                BudgetActualRecord(
                    period=_clean_value(row.get("period")),
                    department=_clean_value(row.get("department")),
                    account=_clean_value(row.get("account")),
                    budget_amount=budget_amount,
                    actual_amount=actual_amount,
                    variance_amount=variance_amount,
                    variance_rate=variance_rate,
                    business_driver=_clean_value(row.get("business_driver")),
                    remark=_clean_value(row.get("remark")),
                )
            )

    return FinanceDataset(records=records, source_path=source_path)


def _validate_required_fields(fieldnames: list[str] | None) -> None:
    if fieldnames is None:
        raise ValueError("CSV header is missing required fields: " + ", ".join(REQUIRED_FIELDS))

    missing_fields = [field for field in REQUIRED_FIELDS if field not in fieldnames]
    if missing_fields:
        raise ValueError("CSV header is missing required fields: " + ", ".join(missing_fields))


def _clean_value(value: str | None) -> str:
    return "" if value is None else value.strip()


def _parse_float(row: dict[str, str], field_name: str, row_number: int) -> float:
    value = _clean_value(row.get(field_name))
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(
            f"Failed to parse numeric value at row {row_number}, field '{field_name}'."
        ) from exc


def _parse_variance_rate(row: dict[str, str], row_number: int) -> float:
    field_name = "variance_rate"
    value = _clean_value(row.get(field_name))

    if value.endswith("%"):
        numeric_value = value[:-1].strip()
        try:
            return round(float(numeric_value) / 100, 10)
        except ValueError as exc:
            raise ValueError(
                f"Failed to parse numeric value at row {row_number}, field '{field_name}'."
            ) from exc

    try:
        return round(float(value), 10)
    except ValueError as exc:
        raise ValueError(
            f"Failed to parse numeric value at row {row_number}, field '{field_name}'."
        ) from exc


def _calculate_variance_rate(variance_amount: float, budget_amount: float) -> float:
    if budget_amount == 0:
        return 0.0
    return round(variance_amount / budget_amount, 10)
