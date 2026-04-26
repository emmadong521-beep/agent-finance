# Budget Variance Analyzer

## v1.3 Goal

v1.3 adds the core rule-based analysis capability for the Budget Variance & Business Insight Agent. It takes a `FinanceDataset`, identifies material budget variances, classifies direction, severity, and category, summarizes results by department and category, and emits structured insight flags for management review.

This stage does not call an LLM and does not generate a final written report.

## Analysis Rules

The analyzer reads structured records from the v1.2 CSV loader and returns a `BudgetVarianceSummary`.

It calculates:

- Total budget, actual, variance, and variance rate
- Material variance count
- Favorable and unfavorable variance counts
- Major variance items
- Department summary
- Category summary
- Chinese insight flags

## Direction Logic

- `variance_amount > 0`: `over_budget`
- `variance_amount < 0`: `under_budget`
- `variance_amount == 0`: `on_budget`

## Severity Logic

- `high`: `abs(variance_rate) >= 0.3` or `abs(variance_amount) >= 300000`
- `medium`: `abs(variance_rate) >= 0.1` or `abs(variance_amount) >= 50000`
- `low`: all other records

Major items are `high` or `medium` severity records, sorted by absolute variance amount from largest to smallest.

## Category Logic

- Account contains `收入` or `回款`: `revenue_or_cash`
- Account contains `成本` or `采购`: `cost`
- Account contains `广告`, `差旅`, `培训`, `人力`, `云服务`, `订阅`, `售后`, `手续费`, `物流`, or `服务费`: `expense`
- Otherwise: `other`

## Favorable and Unfavorable Logic

For revenue and cash records, `under_budget` is unfavorable and `over_budget` is favorable.

For cost, expense, and other records, `over_budget` is unfavorable and `under_budget` is favorable.

## Insight Flags Logic

The analyzer emits Chinese flags when material records match review patterns:

- Revenue or cash records are materially under budget: `收入或回款低于预算，需要关注订单交付和现金流。`
- Expense records are materially over budget: `费用超预算，需要复盘审批和投入产出。`
- Cost records are materially over budget: `成本超预算，需要关注采购价格或供应链因素。`
- Three or more high severity records exist: `存在多项重大偏差，建议管理层专项复盘。`

## Demo

Run from the repository root:

```bash
python3 finance/agents/budget_variance/demo_analyze_budget_variance.py
```

The demo reads:

```text
finance/examples/budget_actual_sample.csv
```

It outputs JSON with totals, variance counts, insight flags, top 10 major items, department summary, and category summary.

## Current Boundaries

- 规则型分析，不调用 LLM
- 不生成最终管理报告
- 不给审计意见
- 不给经营决策结论
- 不替代人工财务判断
