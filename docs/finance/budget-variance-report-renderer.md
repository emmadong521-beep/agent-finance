# Budget Variance Report Renderer

## v1.4 Goal

v1.4 adds a rule-based Chinese Markdown renderer for the Budget Variance & Business Insight Agent. It converts a `BudgetVarianceSummary` from the v1.3 analyzer into a management-readable budget execution variance report.

## Input

The renderer accepts:

```python
BudgetVarianceSummary
```

This summary includes periods, totals, material variance counts, major items, department/category summaries, and insight flags.

## Output

The renderer returns a Chinese Markdown report string.

## Report Sections

The output structure is fixed:

- 预算执行差异分析报告
- 报告期间
- 总体结论
- 收入预算执行情况
- 成本费用预算执行情况
- 重大偏差项目
- 异常归因
- 对利润和现金流的影响
- 管理建议
- 下月关注事项
- 人工复核提示

## Rendering Rules

- Amounts are formatted with two decimal places.
- Variance rates are formatted as percentages.
- Major variance table shows the first 10 `summary.major_items`.
- Abnormal attribution uses only existing `business_driver` and `remark` fields.
- Management recommendations are derived from rule-based insight flags and major item categories.
- Cash flow and profit impact language is conservative and does not forecast cash flow.

## Boundaries

- 规则型生成，不调用 LLM
- 不接 ERP
- 不生成审计意见
- 不提供税务判断
- 不替代人工财务判断
- 只基于 `BudgetVarianceSummary` 生成中文 Markdown 管理报告

## Demo

Run from the repository root:

```bash
python3 finance/agents/budget_variance/demo_render_budget_report.py
```

The demo reads `finance/examples/budget_actual_sample.csv`, runs the v1.3 analyzer, and prints the rendered Markdown report.
