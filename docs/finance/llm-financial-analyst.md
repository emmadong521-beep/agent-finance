# LLM Financial Analyst Configuration

## v1.7 Goal

Agent Finance uses a provider-neutral LLM configuration. It does not bind to a single model service provider. The default integration target is an OpenAI-compatible Chat Completions API, configured locally with an API key, base URL, and model name.

The Budget Variance Agent can use this configuration through its LLM financial analyst executor. Rule mode remains the default.

## Recommended Configuration

Use the `FINANCE_LLM_*` environment variables:

```bash
export FINANCE_LLM_API_KEY="your-key"
export FINANCE_LLM_BASE_URL="your-openai-compatible-base-url"
export FINANCE_LLM_MODEL="your-model-name"
```

## Volcengine Example

```bash
export FINANCE_LLM_BASE_URL="https://ark.cn-beijing.volces.com/api/coding/v3"
export FINANCE_LLM_MODEL="glm-5.1"
```

## CLI Usage

Generate a rule-based report:

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --mode rule --format markdown
```

Generate an LLM-assisted Markdown report:

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --mode llm --format markdown
```

JSON output never calls the LLM:

```bash
python3 finance/agents/budget_variance/run_budget_variance.py finance/examples/budget_actual_sample.csv --mode llm --format json
```

## Other OpenAI-Compatible Providers

OpenAI:

```bash
export FINANCE_LLM_API_KEY="your-key"
export FINANCE_LLM_BASE_URL="https://api.openai.com/v1"
export FINANCE_LLM_MODEL="gpt-4o-mini"
```

OpenRouter:

```bash
export FINANCE_LLM_API_KEY="your-key"
export FINANCE_LLM_BASE_URL="https://openrouter.ai/api/v1"
export FINANCE_LLM_MODEL="your-model-name"
```

## Compatibility Fallbacks

`finance/common/llm_client.py` reads environment variables in this order:

API key:

1. `FINANCE_LLM_API_KEY`
2. `ARK_API_KEY`
3. `VOLCANO_ENGINE_API_KEY`
4. `OPENAI_API_KEY`

Base URL:

1. `FINANCE_LLM_BASE_URL`
2. `ARK_BASE_URL`
3. `OPENAI_BASE_URL`
4. `https://ark.cn-beijing.volces.com/api/coding/v3`

Model:

1. `FINANCE_LLM_MODEL`
2. `ARK_MODEL`
3. `OPENAI_MODEL`
4. `glm-5.1`

## Missing API Key

If no API key is configured, the client raises:

```text
未配置 FINANCE_LLM_API_KEY。请设置环境变量 FINANCE_LLM_API_KEY，或使用 --mode rule。
```

## Security Boundary

- 不提交真实 API key
- 不打印 API key
- 不把 API key 写入日志、报告或 memory
- 仓库只提交 `.env.example`
- 本地 `.env`、`.env.local` 和 `.env.*` 文件必须被 Git 忽略
