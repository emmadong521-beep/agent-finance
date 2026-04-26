from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from finance.agents.budget_variance.analyzer import BudgetVarianceSummary
from finance.common.llm_client import chat_completion


def generate_llm_budget_variance_report(summary: BudgetVarianceSummary) -> str:
    response = chat_completion(
        messages=[
            {
                "role": "system",
                "content": (
                    "你是 Agent Finance 的财务分析报告助手。"
                    "请基于输入的结构化预算差异分析结果生成中文 Markdown 管理报告。"
                    "不要编造输入中不存在的事实、原因、金额、合同、客户或预测。"
                    "不要给审计意见、税务判断、会计处理结论或对外披露建议。"
                    "报告必须保守表达，并明确人工复核边界。"
                ),
            },
            {
                "role": "user",
                "content": _build_user_prompt(summary),
            },
        ],
        temperature=0.2,
    )
    return _extract_content(response)


def _build_user_prompt(summary: BudgetVarianceSummary) -> str:
    summary_json = json.dumps(asdict(summary), ensure_ascii=False, indent=2)
    return (
        "请将以下 BudgetVarianceSummary 渲染为中文 Markdown 预算执行差异分析报告。\n\n"
        "固定章节：\n"
        "# 预算执行差异分析报告\n"
        "## 报告期间\n"
        "## 一、总体结论\n"
        "## 二、收入预算执行情况\n"
        "## 三、成本费用预算执行情况\n"
        "## 四、重大偏差项目\n"
        "## 五、异常归因\n"
        "## 六、对利润和现金流的影响\n"
        "## 七、管理建议\n"
        "## 八、下月关注事项\n"
        "## 九、人工复核提示\n\n"
        "约束：\n"
        "- 只使用输入 JSON 中的字段和事实。\n"
        "- 重大偏差项目用 Markdown 表格展示，优先展示 major_items 前 10 条。\n"
        "- 金额保留两位小数，差异率显示为百分比。\n"
        "- 人工复核提示必须包含：本报告由 Agent Finance 基于输入数据和规则生成，仅用于管理分析辅助。\n"
        "- 不要输出 API key、环境变量值、日志或调试信息。\n\n"
        "BudgetVarianceSummary JSON:\n"
        f"```json\n{summary_json}\n```"
    )


def _extract_content(response: dict[str, Any]) -> str:
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("LLM API response missing choices[0].message.content") from exc

    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("LLM API response content is empty")
    return content.strip() + "\n"
