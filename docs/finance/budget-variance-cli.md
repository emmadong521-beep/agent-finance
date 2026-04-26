# Budget Variance CLI

## CLI Goal

v1.6 adds a standard command-line entrypoint for the Budget Variance & Business Insight Agent. The CLI reads any budget actual CSV file, runs the rule-based analyzer, outputs either a Chinese Markdown report or structured JSON analysis, and can save the output to a file.

The CLI uses Python standard library `argparse` and does not introduce new dependencies.

## Command Format

```bash
python3 finance/agents/budget_variance/run_budget_variance.py <input_csv>
```

## Parameters

- `input_csv`: required CSV path.
- `--format`: optional output format, `markdown` or `json`. Defaults to `markdown`.
- `--mode`: optional report mode, `rule` or `llm`. Defaults to `rule`. JSON output never calls the LLM.
- `--materiality-rate`: optional float threshold. Defaults to `0.1`.
- `--materiality-amount`: optional float threshold. Defaults to `50000`.
- `--output`: optional output file path. When provided, the CLI writes UTF-8 content to the file and prints a confirmation line.

## Markdown Output Example

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --format markdown
```

The output is a Chinese Markdown report with sections for overall conclusion, revenue execution, cost and expense execution, major variance items, attribution, profit and cash flow impact, management recommendations, next-month focus, and human review notice.

LLM Markdown mode:

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --mode llm --format markdown
```

## JSON Output Example

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --format json
```

The output is a JSON serialization of `BudgetVarianceSummary`. It does not call the LLM, even if `--mode llm` is provided. It includes:

- `periods`
- `total_budget`
- `total_actual`
- `total_variance`
- `total_variance_rate`
- `material_variance_count`
- `unfavorable_variance_count`
- `favorable_variance_count`
- `major_items`
- `department_summary`
- `category_summary`
- `insight_flags`

## Save To File Example

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --format markdown --output workspace/budget_variance_report.md
```

Expected stdout:

```text
已写入: workspace/budget_variance_report.md
```

## Current Boundaries

- 规则型分析，不调用 LLM
- LLM mode only affects Markdown report generation
- 不接真实 ERP
- 不接真实银行流水
- 不生成审计意见
- 不提供税务判断
- 不替代人工财务判断
