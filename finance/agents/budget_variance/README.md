# Budget Variance & Business Insight Agent

The Budget Variance Agent helps finance teams analyze budget execution and generate management-ready business insight reports.

## Goals

- Compare budget vs actual data
- Attribute variances to business drivers
- Detect abnormal items and material deviations
- Generate structured management reports
- Support memory writeback in the future for recurring variance patterns, risk signals, and recommended actions

## MVP Flow

1. Ingest structured budget vs actual data.
2. Classify revenue, cost, and expense items.
3. Identify major favorable and unfavorable variances.
4. Attribute variances using business drivers and remarks.
5. Produce a Chinese management report using the report template.

## v1.2 CSV Loader

v1.2 adds a standard-library CSV loader for budget actual data. It validates required fields, parses numeric values, supports percentage or decimal variance rates, and converts rows into structured finance data objects.

Run the demo from the repository root:

```bash
python3 finance/agents/budget_variance/demo_load_budget_data.py
```

## v1.3 Rule-Based Analyzer

v1.3 adds a rule-based analyzer that classifies material variance items by direction, severity, and category, summarizes results by department and category, and emits Chinese insight flags for management review.

Run the analyzer demo from the repository root:

```bash
python3 finance/agents/budget_variance/demo_analyze_budget_variance.py
```

## v1.4 Markdown Report Renderer

v1.4 adds a rule-based Chinese Markdown renderer that converts `BudgetVarianceSummary` into a management-readable budget execution variance report.

Run the report demo from the repository root:

```bash
python3 finance/agents/budget_variance/demo_render_budget_report.py
```

## v1.5 Local Web UI and Skill

v1.5 adds a Streamlit UI for CSV upload, threshold configuration, KPI cards, major variance tables, insight flags, Markdown report display, and report download. It also adds a Budget Variance Skill definition under `finance/skills/budget_variance`.

Run the UI from the repository root:

```bash
streamlit run apps/budget_variance_ui.py
```

## v1.6 Command-Line Interface

v1.6 adds a standard CLI entrypoint that reads any budget actual CSV, runs the rule-based analyzer, and outputs either a Markdown report or JSON analysis result.

Run the CLI from the repository root:

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --format markdown
```

Save a report to file:

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --format markdown --output workspace/budget_variance_report.md
```

## v1.7 LLM Financial Analyst Executor

v1.7 adds provider-neutral LLM report generation for Markdown output. The CLI now supports `--mode rule` and `--mode llm`. Rule mode is the default. JSON output does not call the LLM.

Run an LLM-generated Markdown report:

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --mode llm --format markdown
```

Configure the LLM with `FINANCE_LLM_API_KEY`, `FINANCE_LLM_BASE_URL`, and `FINANCE_LLM_MODEL`.

## Related Files

- `scope.md`: MVP input, output, and non-goals
- `sample_output.md`: sample report output
- `../../../templates/budget_variance_report.md`: report template
- `../../../examples/budget_actual_sample.csv`: sample budget vs actual data
- `../../../common/finance_models.py`: finance data models
- `../../../common/csv_loader.py`: budget actual CSV loader
- `analyzer.py`: rule-based budget variance analyzer
- `report_renderer.py`: Chinese Markdown report renderer
- `llm_reporter.py`: LLM financial analyst report generator
- `run_budget_variance.py`: CLI entrypoint
- `../../../skills/budget_variance/SKILL.md`: Budget Variance Skill definition
