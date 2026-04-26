from __future__ import annotations

from finance.agents.budget_variance.analyzer import (
    BudgetVarianceItem,
    BudgetVarianceSummary,
)


def render_budget_variance_report(summary: BudgetVarianceSummary) -> str:
    sections = [
        "# 预算执行差异分析报告",
        "## 报告期间",
        _render_periods(summary),
        "## 一、总体结论",
        _render_overall_conclusion(summary),
        "## 二、收入预算执行情况",
        _render_revenue_section(summary),
        "## 三、成本费用预算执行情况",
        _render_cost_expense_section(summary),
        "## 四、重大偏差项目",
        _render_major_items_table(summary.major_items[:10]),
        "## 五、异常归因",
        _render_attribution(summary.major_items),
        "## 六、对利润和现金流的影响",
        _render_profit_cashflow_impact(summary),
        "## 七、管理建议",
        _render_management_recommendations(summary),
        "## 八、下月关注事项",
        _render_next_month_focus(summary.major_items),
        "## 九、人工复核提示",
        (
            "本报告由 Agent Finance 基于输入数据和规则生成，仅用于管理分析辅助。"
            "重大经营判断、会计处理、审计意见、税务判断和对外披露内容必须由人工财务负责人复核确认。"
        ),
    ]

    return "\n\n".join(sections) + "\n"


def format_amount(value: float) -> str:
    return f"{value:,.2f}"


def format_rate(value: float) -> str:
    return f"{value * 100:.2f}%"


def translate_direction(direction: str) -> str:
    translations = {
        "over_budget": "超预算",
        "under_budget": "低于预算",
        "on_budget": "符合预算",
    }
    return translations.get(direction, direction)


def translate_severity(severity: str) -> str:
    translations = {
        "high": "高",
        "medium": "中",
        "low": "低",
    }
    return translations.get(severity, severity)


def get_category(
    summary: BudgetVarianceSummary,
    category: str,
) -> dict[str, float] | None:
    return summary.category_summary.get(category)


def _render_periods(summary: BudgetVarianceSummary) -> str:
    if not summary.periods:
        return "未识别报告期间。"
    return "、".join(summary.periods)


def _render_overall_conclusion(summary: BudgetVarianceSummary) -> str:
    lines = [
        (
            f"本期预算总额为 {format_amount(summary.total_budget)}，"
            f"实际发生额为 {format_amount(summary.total_actual)}，"
            f"总差异为 {format_amount(summary.total_variance)}，"
            f"总差异率为 {format_rate(summary.total_variance_rate)}。"
        ),
        (
            f"本期共识别 {summary.material_variance_count} 项重大偏差，"
            f"其中不利偏差 {summary.unfavorable_variance_count} 项，"
            f"有利偏差 {summary.favorable_variance_count} 项。"
        ),
    ]

    if summary.insight_flags:
        lines.append("总体风险提示：" + "；".join(_strip_period(flag) for flag in summary.insight_flags) + "。")
    else:
        lines.append("本期未生成明显风险提示，建议保持常规预算跟踪。")

    return "\n\n".join(lines)


def _render_revenue_section(summary: BudgetVarianceSummary) -> str:
    revenue = get_category(summary, "revenue_or_cash")
    if not revenue:
        return "本期未识别收入/回款类项目。"

    text = (
        f"收入/回款类预算为 {format_amount(revenue['budget_amount'])}，"
        f"实际为 {format_amount(revenue['actual_amount'])}，"
        f"差异为 {format_amount(revenue['variance_amount'])}。"
    )
    if revenue["variance_amount"] < 0:
        text += "收入或回款低于预算，可能影响当期利润表现和经营现金流节奏。"
    elif revenue["variance_amount"] > 0:
        text += "收入或回款高于预算，对利润和现金流形成正向支撑。"
    else:
        text += "收入或回款整体符合预算。"
    return text


def _render_cost_expense_section(summary: BudgetVarianceSummary) -> str:
    cost = get_category(summary, "cost")
    expense = get_category(summary, "expense")
    lines: list[str] = []

    if cost:
        lines.append(
            f"成本类预算为 {format_amount(cost['budget_amount'])}，"
            f"实际为 {format_amount(cost['actual_amount'])}，"
            f"差异为 {format_amount(cost['variance_amount'])}。"
        )
    if expense:
        lines.append(
            f"费用类预算为 {format_amount(expense['budget_amount'])}，"
            f"实际为 {format_amount(expense['actual_amount'])}，"
            f"差异为 {format_amount(expense['variance_amount'])}。"
        )

    if not lines:
        return "本期未识别成本/费用类项目。"

    if (cost and cost["variance_amount"] > 0) or (expense and expense["variance_amount"] > 0):
        lines.append("成本或费用超预算会压缩利润空间，需要关注审批、采购价格、资源使用和投入产出。")
    else:
        lines.append("成本费用整体未超预算，仍建议持续跟踪后续执行节奏。")

    return "\n\n".join(lines)


def _render_major_items_table(items: list[BudgetVarianceItem]) -> str:
    if not items:
        return "本期未识别 high 或 medium 级别重大偏差项目。"

    header = (
        "| 部门 | 科目 | 预算金额 | 实际金额 | 差异金额 | 差异率 | 方向 | 严重性 | 主要原因 |\n"
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |"
    )
    rows = [
        (
            f"| {item.department} | {item.account} | {format_amount(item.budget_amount)} | "
            f"{format_amount(item.actual_amount)} | {format_amount(item.variance_amount)} | "
            f"{format_rate(item.variance_rate)} | {translate_direction(item.direction)} | "
            f"{translate_severity(item.severity)} | {_escape_table_text(item.business_driver)} |"
        )
        for item in items
    ]
    return "\n".join([header, *rows])


def _render_attribution(items: list[BudgetVarianceItem]) -> str:
    focus_items = [item for item in items if item.severity in {"high", "medium"}]
    if not focus_items:
        return "- 本期未识别 high 或 medium 级别异常归因项目。"

    lines = []
    for item in focus_items[:10]:
        reason_parts = [part for part in [item.business_driver, item.remark] if part]
        reason = "；".join(reason_parts) if reason_parts else "未提供业务原因"
        lines.append(
            f"- {item.department} - {item.account}：{translate_direction(item.direction)}"
            f" {format_amount(item.variance_amount)}，主要依据：{reason}。"
        )
    return "\n".join(lines)


def _render_profit_cashflow_impact(summary: BudgetVarianceSummary) -> str:
    lines: list[str] = []

    if _has_direction(summary, "revenue_or_cash", "under_budget"):
        lines.append("收入或回款低于预算，可能影响当期利润实现和经营现金流节奏。")

    if _has_direction(summary, "cost", "over_budget") or _has_direction(summary, "expense", "over_budget"):
        lines.append("成本或费用超预算会压缩利润空间，并可能增加短期资金安排压力。")

    if not lines:
        lines.append("本期未识别明显的利润或现金流异常压力，建议持续跟踪预算执行。")

    lines.append("以上判断仅基于预算差异数据，不构成现金流预测。")
    return "\n\n".join(lines)


def _render_management_recommendations(summary: BudgetVarianceSummary) -> str:
    recommendations: list[str] = []

    if _has_direction(summary, "revenue_or_cash", "under_budget"):
        recommendations.append("收入/回款不足：建议销售、业务、财务联合跟进订单交付和回款计划。")

    if _has_direction(summary, "expense", "over_budget"):
        recommendations.append("费用超预算：建议复盘审批、预算追加和投入产出。")

    if _has_direction(summary, "cost", "over_budget"):
        recommendations.append("成本超预算：建议复核采购价格和供应链因素。")

    if any(item.severity == "high" for item in summary.major_items):
        recommendations.append("重大偏差：建议管理层对高严重性项目进行专项复盘。")

    if not recommendations and summary.insight_flags:
        recommendations.extend(summary.insight_flags)

    if not recommendations:
        recommendations.append("本期无明显异常，建议持续跟踪预算执行。")

    return "\n".join(f"- {recommendation}" for recommendation in _dedupe(recommendations))


def _render_next_month_focus(items: list[BudgetVarianceItem]) -> str:
    if not items:
        return "- 持续跟踪重点部门预算执行情况。"

    focus_lines = []
    for item in items[:6]:
        detail = item.remark or item.business_driver or "预算执行偏差"
        focus_lines.append(f"- {item.department} - {item.account}：关注{detail}。")

    return "\n".join(_dedupe(focus_lines))


def _has_direction(
    summary: BudgetVarianceSummary,
    category: str,
    direction: str,
) -> bool:
    return any(
        item.category == category and item.direction == direction
        for item in summary.major_items
    )


def _strip_period(text: str) -> str:
    return text.rstrip("。")


def _escape_table_text(text: str) -> str:
    return text.replace("|", "\\|")


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result
