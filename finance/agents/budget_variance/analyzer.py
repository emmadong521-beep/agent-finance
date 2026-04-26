from __future__ import annotations

from dataclasses import dataclass

from finance.common.finance_models import BudgetActualRecord, FinanceDataset


@dataclass(frozen=True)
class BudgetVarianceItem:
    period: str
    department: str
    account: str
    budget_amount: float
    actual_amount: float
    variance_amount: float
    variance_rate: float
    direction: str
    severity: str
    category: str
    business_driver: str
    remark: str


@dataclass(frozen=True)
class BudgetVarianceSummary:
    periods: list[str]
    total_budget: float
    total_actual: float
    total_variance: float
    total_variance_rate: float
    record_count: int
    material_variance_count: int
    unfavorable_variance_count: int
    favorable_variance_count: int
    major_items: list[BudgetVarianceItem]
    department_summary: dict[str, dict[str, float]]
    category_summary: dict[str, dict[str, float]]
    insight_flags: list[str]


def analyze_budget_variance(
    dataset: FinanceDataset,
    materiality_rate: float = 0.1,
    materiality_amount: float = 50000,
) -> BudgetVarianceSummary:
    items = [_build_item(record) for record in dataset.records]
    major_items = sorted(
        [item for item in items if item.severity in {"high", "medium"}],
        key=lambda item: abs(item.variance_amount),
        reverse=True,
    )

    total_budget = dataset.total_budget()
    total_actual = dataset.total_actual()
    total_variance = dataset.total_variance()
    total_variance_rate = _calculate_rate(total_variance, total_budget)

    material_items = [
        item
        for item in items
        if _is_material(item, materiality_rate, materiality_amount)
    ]
    unfavorable_variance_count = sum(1 for item in items if _is_unfavorable(item))
    favorable_variance_count = sum(1 for item in items if _is_favorable(item))

    return BudgetVarianceSummary(
        periods=dataset.periods(),
        total_budget=total_budget,
        total_actual=total_actual,
        total_variance=total_variance,
        total_variance_rate=total_variance_rate,
        record_count=len(dataset.records),
        material_variance_count=len(material_items),
        unfavorable_variance_count=unfavorable_variance_count,
        favorable_variance_count=favorable_variance_count,
        major_items=major_items,
        department_summary=_summarize_by(items, key_name="department"),
        category_summary=_summarize_by(items, key_name="category"),
        insight_flags=_build_insight_flags(
            items=items,
            major_items=major_items,
            materiality_rate=materiality_rate,
            materiality_amount=materiality_amount,
        ),
    )


def _build_item(record: BudgetActualRecord) -> BudgetVarianceItem:
    return BudgetVarianceItem(
        period=record.period,
        department=record.department,
        account=record.account,
        budget_amount=record.budget_amount,
        actual_amount=record.actual_amount,
        variance_amount=record.variance_amount,
        variance_rate=record.variance_rate,
        direction=_classify_direction(record.variance_amount),
        severity=_classify_severity(record.variance_amount, record.variance_rate),
        category=_classify_category(record.account),
        business_driver=record.business_driver,
        remark=record.remark,
    )


def _classify_direction(variance_amount: float) -> str:
    if variance_amount > 0:
        return "over_budget"
    if variance_amount < 0:
        return "under_budget"
    return "on_budget"


def _classify_severity(variance_amount: float, variance_rate: float) -> str:
    if abs(variance_rate) >= 0.3 or abs(variance_amount) >= 300000:
        return "high"
    if abs(variance_rate) >= 0.1 or abs(variance_amount) >= 50000:
        return "medium"
    return "low"


def _classify_category(account: str) -> str:
    if "收入" in account or "回款" in account:
        return "revenue_or_cash"
    if "成本" in account or "采购" in account:
        return "cost"

    expense_keywords = [
        "广告",
        "差旅",
        "培训",
        "人力",
        "云服务",
        "订阅",
        "售后",
        "手续费",
        "物流",
        "服务费",
    ]
    if any(keyword in account for keyword in expense_keywords):
        return "expense"

    return "other"


def _summarize_by(
    items: list[BudgetVarianceItem],
    key_name: str,
) -> dict[str, dict[str, float]]:
    summary: dict[str, dict[str, float]] = {}

    for item in items:
        key = getattr(item, key_name)
        if key not in summary:
            summary[key] = {
                "budget_amount": 0.0,
                "actual_amount": 0.0,
                "variance_amount": 0.0,
                "record_count": 0.0,
            }

        summary[key]["budget_amount"] += item.budget_amount
        summary[key]["actual_amount"] += item.actual_amount
        summary[key]["variance_amount"] += item.variance_amount
        summary[key]["record_count"] += 1.0

    return summary


def _build_insight_flags(
    items: list[BudgetVarianceItem],
    major_items: list[BudgetVarianceItem],
    materiality_rate: float,
    materiality_amount: float,
) -> list[str]:
    flags: list[str] = []

    if any(
        item.category == "revenue_or_cash"
        and item.direction == "under_budget"
        and _is_material(item, materiality_rate, materiality_amount)
        for item in items
    ):
        flags.append("收入或回款低于预算，需要关注订单交付和现金流。")

    if any(
        item.category == "expense"
        and item.direction == "over_budget"
        and _is_material(item, materiality_rate, materiality_amount)
        for item in items
    ):
        flags.append("费用超预算，需要复盘审批和投入产出。")

    if any(
        item.category == "cost"
        and item.direction == "over_budget"
        and _is_material(item, materiality_rate, materiality_amount)
        for item in items
    ):
        flags.append("成本超预算，需要关注采购价格或供应链因素。")

    high_severity_count = sum(1 for item in major_items if item.severity == "high")
    if high_severity_count >= 3:
        flags.append("存在多项重大偏差，建议管理层专项复盘。")

    return flags


def _is_material(
    item: BudgetVarianceItem,
    materiality_rate: float,
    materiality_amount: float,
) -> bool:
    return (
        abs(item.variance_rate) >= materiality_rate
        or abs(item.variance_amount) >= materiality_amount
    )


def _is_unfavorable(item: BudgetVarianceItem) -> bool:
    if item.direction == "on_budget":
        return False
    if item.category == "revenue_or_cash":
        return item.direction == "under_budget"
    return item.direction == "over_budget"


def _is_favorable(item: BudgetVarianceItem) -> bool:
    if item.direction == "on_budget":
        return False
    return not _is_unfavorable(item)


def _calculate_rate(variance_amount: float, budget_amount: float) -> float:
    if budget_amount == 0:
        return 0.0
    return round(variance_amount / budget_amount, 10)
