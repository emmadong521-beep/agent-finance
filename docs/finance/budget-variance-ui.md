# Budget Variance UI

## UI Goal

v1.5 adds a local Streamlit Web UI for the Budget Variance & Business Insight Agent. The UI lets finance users upload budget actual CSV files, configure materiality thresholds, run rule-based analysis, inspect major variance items, review insight flags, and download a Markdown report.

## Page Features

- Page title: `Agent Finance`
- Subtitle: `预算执行分析与异常归因 Agent`
- CSV upload
- Rule / LLM report mode selection
- Default sample data from `finance/examples/budget_actual_sample.csv`
- Configurable `materiality_rate`
- Configurable `materiality_amount`
- KPI cards for budget, actual, variance, variance rate, material variance count, and unfavorable variance count
- Major variance table with the top 10 items
- Chinese `insight_flags`
- Rendered Markdown budget variance report
- Markdown report download button

## Usage

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the local UI:

```bash
streamlit run apps/budget_variance_ui.py
```

If no CSV is uploaded, the UI uses:

```text
finance/examples/budget_actual_sample.csv
```

## CSV Format

The uploaded CSV must include:

- `period`
- `department`
- `account`
- `budget_amount`
- `actual_amount`
- `variance_amount`
- `variance_rate`
- `business_driver`
- `remark`

`variance_rate` supports percentage strings such as `12.5%` and decimal strings such as `0.125`.

## Current Boundaries

- Rule mode 不调用 LLM
- LLM mode 只使用 `FINANCE_LLM_*` 或兼容 fallback 环境变量调用 OpenAI-compatible Chat Completions API
- 不接真实 ERP
- 不接真实银行流水
- 不做登录权限
- 不生成审计意见
- 不替代人工财务判断
- 只基于 CSV 和规则型分析生成本地 UI 输出

## Future Extensions

- Excel upload support
- Department filters and period filters
- Report export to PDF or DOCX
- Configurable variance rules
- Memory writeback for recurring variance patterns
- Controlled finance knowledge Q&A integration
