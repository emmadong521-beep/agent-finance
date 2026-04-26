# Budget Variance Data Loader

## v1.2 Goal

v1.2 adds the first runnable capability for the Budget Variance & Business Insight Agent: read a budget actual CSV file, validate required fields, parse numeric values, and convert rows into structured finance data objects.

This stage only loads and structures data. It does not perform budget analysis or generate management conclusions.

## Input Fields

The loader expects a CSV file with these headers:

- `period`
- `department`
- `account`
- `budget_amount`
- `actual_amount`
- `variance_amount`
- `variance_rate`
- `business_driver`
- `remark`

## Loader Validation Rules

- Uses Python standard library `csv`.
- Requires all input headers listed above.
- Raises `ValueError` if any required field is missing, including the missing field names.
- Parses `budget_amount`, `actual_amount`, and `variance_amount` as `float`.
- Parses `variance_rate` as a decimal `float`.
- Raises `ValueError` with row number and field name when numeric parsing fails.

## Automatic Calculation Rules

If `variance_amount` is blank, the loader calculates:

```text
variance_amount = actual_amount - budget_amount
```

If `variance_rate` is blank, the loader calculates:

```text
variance_rate = variance_amount / budget_amount
```

If `budget_amount` is `0`, the calculated `variance_rate` is `0.0`.

`variance_rate` supports both formats:

- `12.5%` is parsed as `0.125`
- `0.125` is parsed as `0.125`

## Demo

Run from the repository root:

```bash
python3 finance/agents/budget_variance/demo_load_budget_data.py
```

The demo reads:

```text
finance/examples/budget_actual_sample.csv
```

It outputs a JSON summary with source path, periods, departments, accounts, record count, totals, material variance count, and the first five material variance records.

## Current Boundaries

- 不接真实 ERP
- 不接 Excel
- 不做预算分析逻辑
- 只做 CSV 读取、字段校验、数值解析和结构化数据转换
