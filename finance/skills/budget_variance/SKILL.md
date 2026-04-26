---
name: budget-variance
description: 使用 Budget Variance & Business Insight Agent 分析预算实际 CSV，识别重大偏差、异常归因、管理关注提示，并生成中文预算执行差异分析报告。
---

# Budget Variance Skill

## Purpose

用于预算执行分析和异常归因。基于标准预算实际 CSV，读取数据、校验字段、执行规则型差异分析，并生成中文管理层可读的 Markdown 报告。

## When To Use

- 需要比较 budget vs actual 数据
- 需要识别重大预算偏差、超预算或低于预算项目
- 需要按部门、科目或类别查看预算执行情况
- 需要生成预算执行差异分析报告草稿
- 需要为管理层复盘准备结构化输入

## Required Inputs

CSV 必须包含以下字段：

- `period`
- `department`
- `account`
- `budget_amount`
- `actual_amount`
- `variance_amount`
- `variance_rate`
- `business_driver`
- `remark`

`variance_amount` 和 `variance_rate` 可为空；loader 会基于预算和实际金额自动计算。

## Execution Steps

1. 使用 `load_budget_actual_csv(path)` 读取并校验 CSV。
2. 使用 `analyze_budget_variance(dataset)` 生成 `BudgetVarianceSummary`。
3. 查看 `major_items`、`department_summary`、`category_summary` 和 `insight_flags`。
4. 使用 `render_budget_variance_report(summary)` 生成中文 Markdown 报告。
5. 如需 LLM 报告草稿，配置 `FINANCE_LLM_API_KEY`、`FINANCE_LLM_BASE_URL`、`FINANCE_LLM_MODEL` 后使用 `--mode llm`。
6. 如需本地交互界面，运行 Streamlit UI。

## Output Format

- JSON summary：用于程序化查看指标、重大偏差和分类汇总
- Markdown report：用于管理层阅读和人工复核
- LLM Markdown draft：基于结构化分析结果生成的中文报告草稿
- UI view：展示 KPI 卡片、重大偏差表、管理关注提示和报告下载

## Human Review Boundary

本 Skill 只提供管理分析辅助。重大经营判断、会计处理、审计意见、税务判断、合规结论和对外披露内容必须由人工财务负责人复核确认。

## Non-Goals

- 不接真实 ERP
- 不接真实银行流水
- 不把 API key 写入日志、报告或 memory
- 不做审计意见
- 不替代人工财务判断
- 不处理登录、权限或审批流

## Example Command

```bash
streamlit run apps/budget_variance_ui.py
```

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --format markdown
```

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --mode llm --format markdown
```
