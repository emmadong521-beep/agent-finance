# Flexible CSV Mapping

## Why Field Mapping Is Needed

Enterprise budget actual exports often use Chinese headers, department-specific labels, or business aliases instead of the internal English field names used by Agent Finance. v1.8 adds a flexible CSV field mapping layer so the Budget Variance Agent can load real-world CSV exports more easily while keeping the internal data model stable.

## Standard Fields

Internally, the loader maps every CSV into these standard fields:

- `period`
- `department`
- `account`
- `budget_amount`
- `actual_amount`
- `variance_amount`
- `variance_rate`
- `business_driver`
- `remark`

## Supported Chinese Aliases

| Standard Field | Supported Aliases |
| --- | --- |
| `period` | `period`, `期间`, `月份`, `报告期间`, `会计期间` |
| `department` | `department`, `部门`, `责任部门`, `业务部门`, `所属部门` |
| `account` | `account`, `科目`, `预算科目`, `项目`, `费用项目`, `预算项目` |
| `budget_amount` | `budget_amount`, `预算金额`, `预算数`, `预算`, `预算额` |
| `actual_amount` | `actual_amount`, `实际金额`, `实际数`, `实际`, `发生额`, `实际发生额` |
| `variance_amount` | `variance_amount`, `差异金额`, `差异额`, `预算差异`, `偏差金额` |
| `variance_rate` | `variance_rate`, `差异率`, `偏差率`, `预算偏差率`, `差异比例` |
| `business_driver` | `business_driver`, `业务原因`, `原因`, `主要原因`, `驱动因素`, `业务驱动` |
| `remark` | `remark`, `备注`, `说明`, `补充说明`, `备注说明` |

## Chinese CSV Example

```csv
期间,部门,科目,预算金额,实际金额,差异金额,差异率,业务原因,备注
2026-03,销售部,销售收入,5000000,4300000,-700000,-14.00%,重点客户订单延期,销售收入低于预算且部分客户回款延迟
```

Full sample:

```text
finance/examples/budget_actual_cn_sample.csv
```

## CLI Usage

English sample:

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --mode rule --format markdown
```

Chinese sample:

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_cn_sample.csv --mode rule --format markdown
```

## UI Usage

Run the local UI:

```bash
python -m streamlit run apps/budget_variance_ui.py
```

The upload control accepts CSV files with English standard fields, Chinese fields, or supported aliases.

## Current Boundaries

- 仍要求每一行代表一个预算实际项目
- 不自动识别合并单元格
- 不处理多表头 Excel
- 不读取 xlsx，只支持 CSV
