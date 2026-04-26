from __future__ import annotations

from copy import deepcopy


STANDARD_BUDGET_FIELDS = [
    "period",
    "department",
    "account",
    "budget_amount",
    "actual_amount",
    "variance_amount",
    "variance_rate",
    "business_driver",
    "remark",
]


BUDGET_FIELD_ALIASES = {
    "period": ["period", "期间", "月份", "报告期间", "会计期间"],
    "department": ["department", "部门", "责任部门", "业务部门", "所属部门"],
    "account": ["account", "科目", "预算科目", "项目", "费用项目", "预算项目"],
    "budget_amount": ["budget_amount", "预算金额", "预算数", "预算", "预算额"],
    "actual_amount": ["actual_amount", "实际金额", "实际数", "实际", "发生额", "实际发生额"],
    "variance_amount": ["variance_amount", "差异金额", "差异额", "预算差异", "偏差金额"],
    "variance_rate": ["variance_rate", "差异率", "偏差率", "预算偏差率", "差异比例"],
    "business_driver": ["business_driver", "业务原因", "原因", "主要原因", "驱动因素", "业务驱动"],
    "remark": ["remark", "备注", "说明", "补充说明", "备注说明"],
}


def normalize_header(header: str) -> str:
    return header.replace("\ufeff", "").replace("\u3000", " ").strip()


def build_field_mapping(fieldnames: list[str]) -> dict[str, str]:
    normalized_headers = [
        (original_header, normalize_header(original_header))
        for original_header in fieldnames
    ]
    field_mapping: dict[str, str] = {}

    for standard_field in STANDARD_BUDGET_FIELDS:
        normalized_aliases = {
            normalize_header(alias)
            for alias in BUDGET_FIELD_ALIASES[standard_field]
        }
        for original_header, normalized_header in normalized_headers:
            if normalized_header in normalized_aliases:
                field_mapping[standard_field] = original_header
                break

    missing_fields = [
        field for field in STANDARD_BUDGET_FIELDS if field not in field_mapping
    ]
    if missing_fields:
        missing_details = [
            f"{field} (aliases: {', '.join(BUDGET_FIELD_ALIASES[field])})"
            for field in missing_fields
        ]
        raise ValueError(
            "CSV header is missing required budget fields: "
            + "; ".join(missing_details)
        )

    return field_mapping


def get_supported_field_aliases() -> dict[str, list[str]]:
    return deepcopy(BUDGET_FIELD_ALIASES)
