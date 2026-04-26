# Agent Finance

Agent Finance is a Finance AI Agent System built around one shared Finance Agent Runtime and multiple specialized finance agents.

The project is formally repositioned from a generic Agent OS into a finance-domain agent platform. It is designed for financial analysis, budget execution, abnormal variance attribution, compliance review, accounts receivable risk analysis, reconciliation matching, and controlled finance knowledge Q&A.

## Vision

Agent Finance aims to support finance teams with AI agents that can:

- Analyze structured finance and business data
- Track budget execution and explain budget variance
- Attribute abnormal items to business drivers
- Support compliance review and controlled finance knowledge Q&A
- Identify accounts receivable risk and cash collection issues
- Assist reconciliation matching workflows
- Generate management-ready financial narratives

## Architecture

Architecture principle:

**One shared Finance Agent Runtime + multiple specialized finance agents.**

Layer responsibilities:

- **Shared Agent Runtime:** execution adapters, workflows, memory services, reflection, and contracts
- **Finance Domain Layer:** finance-specific agent scopes, report templates, examples, and shared domain conventions
- **Specialized Finance Agents:** focused agents for budget variance, compliance review, AR risk, reconciliation, and controlled finance Q&A
- **OpenClaw Compatibility Layer:** compatible entrypoint and skill layer for existing OpenClaw-style workflows; OpenClaw is not the current only runtime core

## Runtime Capabilities

The shared runtime already supports:

- SQLite memory
- Executor abstraction
- Workflow layer
- Darwin reflection/writeback
- GitHub repo fetcher
- Repo analysis CLI
- Markdown report renderer
- External executor adapter preparation

## Finance Agent Roadmap

Planned finance agents:

- **budget_variance:** Budget Variance & Business Insight Agent
- **compliance_review:** compliance and policy review assistant
- **ar_risk:** accounts receivable risk analysis agent
- **reconciliation:** reconciliation support agent
- **controlled_qa:** controlled finance knowledge Q&A agent

## First Agent: Budget Variance & Business Insight Agent

The first finance agent focuses on budget execution analysis and management insight generation.

MVP scope:

- Compare budget vs actual data
- Attribute major variances to business drivers
- Detect abnormal budget execution items
- Generate Chinese management reports
- Prepare for future memory writeback of recurring patterns, risks, and management actions

See [finance/agents/budget_variance](finance/agents/budget_variance) for the detailed scope, template, and sample output.

The Budget Variance Agent supports CSV files with English standard fields, Chinese field names, and common finance aliases. Chinese sample:

```text
finance/examples/budget_actual_cn_sample.csv
```

CLI example with Chinese headers:

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_cn_sample.csv --format markdown
```

## Local UI

Run the Budget Variance Agent local Streamlit UI:

```bash
python -m streamlit run apps/budget_variance_ui.py
```

The UI supports CSV upload, materiality threshold configuration, KPI cards, major variance tables, insight flags, rendered Chinese Markdown reports, and report download.

## CLI

Run the Budget Variance Agent from the command line:

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --format markdown
```

Use `--format json` for structured analysis output or `--output <path>` to save the result to a file.

Rule mode is the default. To use the LLM financial analyst executor for Markdown reports:

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --mode llm --format markdown
```

`--format json` always returns the structured analyzer summary and does not call an LLM.

## LLM Configuration

Agent Finance uses provider-neutral LLM configuration for OpenAI-compatible Chat Completions APIs.

Recommended local configuration:

```bash
export FINANCE_LLM_API_KEY="your-key"
export FINANCE_LLM_BASE_URL="your-openai-compatible-base-url"
export FINANCE_LLM_MODEL="your-model-or-endpoint-id"
```

Volcengine example:

```bash
export FINANCE_LLM_BASE_URL="https://ark.cn-beijing.volces.com/api/coding/v3"
export FINANCE_LLM_MODEL="your-model-or-endpoint-id"
```

Do not commit real API keys. Use `.env.example` as a template only.

## Project Structure

```text
.openclaw/    # compatible entrypoint and skill layer
apps/         # local app entrypoints
memory/       # SQLite memory + exports
runtime/      # shared executors, workflows, memory services, reflection
contracts/    # task/result/workflow/repo schemas
finance/      # finance domain layer and specialized finance agents
docs/         # architecture and decisions
workspace/    # working directory
```

## Roadmap

- **v0.1:** OpenClaw + Harness + Darwin
- **v0.2:** SQLite memory backbone
- **v0.3:** Executor abstraction
- **v0.4:** Skill evolution pipeline
- **v0.5:** Workflow system
- **v0.6:** AutoResearch integration
- **v0.7:** Paperclip integration
- **v1.0:** External executor adapter preparation
- **v1.1:** Finance MVP repositioning and Budget Variance Agent scope
- **v1.5:** Budget Variance UI and skill definition

## Status

Early-stage Finance AI Agent System. Rapid iteration expected.
