from __future__ import annotations

import csv
from pathlib import Path

from finance.common.field_mapping import build_field_mapping
from finance.common.finance_models import BudgetActualRecord, FinanceDataset


def load_budget_actual_csv(path: str) -> FinanceDataset:
    source_path = str(Path(path))
    records: list[BudgetActualRecord] = []

    with open(path, newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("CSV header is missing required budget fields.")
        field_mapping = build_field_mapping(reader.fieldnames)

        for row_number, row in enumerate(reader, start=2):
            budget_amount = _parse_float(row, field_mapping, "budget_amount", row_number)
            actual_amount = _parse_float(row, field_mapping, "actual_amount", row_number)

            variance_amount_value = _get_value(row, field_mapping, "variance_amount")
            if variance_amount_value == "":
                variance_amount = actual_amount - budget_amount
            else:
                variance_amount = _parse_float(
                    row,
                    field_mapping,
                    "variance_amount",
                    row_number,
                )

            variance_rate_value = _get_value(row, field_mapping, "variance_rate")
            if variance_rate_value == "":
                variance_rate = _calculate_variance_rate(
                    variance_amount=variance_amount,
                    budget_amount=budget_amount,
                )
            else:
                variance_rate = _parse_variance_rate(row, field_mapping, row_number)

            records.append(
                BudgetActualRecord(
                    period=_get_value(row, field_mapping, "period"),
                    department=_get_value(row, field_mapping, "department"),
                    account=_get_value(row, field_mapping, "account"),
                    budget_amount=budget_amount,
                    actual_amount=actual_amount,
                    variance_amount=variance_amount,
                    variance_rate=variance_rate,
                    business_driver=_get_value(row, field_mapping, "business_driver"),
                    remark=_get_value(row, field_mapping, "remark"),
                )
            )

    return FinanceDataset(records=records, source_path=source_path)


def _clean_value(value: str | None) -> str:
    return "" if value is None else value.strip()


def _get_value(
    row: dict[str, str],
    field_mapping: dict[str, str],
    standard_field_name: str,
) -> str:
    return _clean_value(row.get(field_mapping[standard_field_name]))


def _parse_float(
    row: dict[str, str],
    field_mapping: dict[str, str],
    standard_field_name: str,
    row_number: int,
) -> float:
    original_field_name = field_mapping[standard_field_name]
    value = _clean_value(row.get(original_field_name))
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(
            "Failed to parse numeric value at "
            f"row {row_number}, field '{original_field_name}' "
            f"(standard field '{standard_field_name}')."
        ) from exc


def _parse_variance_rate(
    row: dict[str, str],
    field_mapping: dict[str, str],
    row_number: int,
) -> float:
    standard_field_name = "variance_rate"
    original_field_name = field_mapping[standard_field_name]
    value = _clean_value(row.get(original_field_name))

    if value.endswith("%"):
        numeric_value = value[:-1].strip()
        try:
            return round(float(numeric_value) / 100, 10)
        except ValueError as exc:
            raise ValueError(
                "Failed to parse numeric value at "
                f"row {row_number}, field '{original_field_name}' "
                f"(standard field '{standard_field_name}')."
            ) from exc

    try:
        return round(float(value), 10)
    except ValueError as exc:
        raise ValueError(
            "Failed to parse numeric value at "
            f"row {row_number}, field '{original_field_name}' "
            f"(standard field '{standard_field_name}')."
        ) from exc


def _calculate_variance_rate(variance_amount: float, budget_amount: float) -> float:
    if budget_amount == 0:
        return 0.0
    return round(variance_amount / budget_amount, 10)
