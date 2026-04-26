from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import streamlit as st


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from finance.agents.budget_variance.analyzer import analyze_budget_variance
from finance.agents.budget_variance.llm_reporter import generate_llm_budget_variance_report
from finance.agents.budget_variance.report_renderer import (
    format_amount,
    format_rate,
    render_budget_variance_report,
    translate_direction,
    translate_severity,
)
from finance.common.csv_loader import load_budget_actual_csv


DEFAULT_SAMPLE_PATH = REPO_ROOT / "finance" / "examples" / "budget_actual_sample.csv"


def main() -> None:
    st.set_page_config(
        page_title="Agent Finance",
        page_icon="AF",
        layout="wide",
    )
    _inject_styles()

    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown('<p class="eyebrow">Finance AI Agent System</p>', unsafe_allow_html=True)
    st.title("Agent Finance")
    st.markdown(
        '<p class="subtitle">预算执行分析与异常归因 Agent</p>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("数据与阈值")
        uploaded_file = st.file_uploader("上传预算实际 CSV", type=["csv"])
        mode = st.radio(
            "报告生成模式",
            options=["rule", "llm"],
            index=0,
            horizontal=True,
            help="rule 使用本地规则渲染；llm 使用 FINANCE_LLM_* 配置调用 OpenAI-compatible API。",
        )
        materiality_rate = st.number_input(
            "materiality_rate",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.01,
            format="%.2f",
        )
        materiality_amount = st.number_input(
            "materiality_amount",
            min_value=0.0,
            value=50000.0,
            step=10000.0,
            format="%.2f",
        )
        st.caption("未上传文件时默认使用 finance/examples/budget_actual_sample.csv。")
        run_analysis = st.button("生成分析报告", type="primary", use_container_width=True)

    if not run_analysis:
        st.info("请上传 CSV 或使用默认样例数据，然后点击生成分析报告。")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    temp_path: str | None = None
    try:
        source_path = str(DEFAULT_SAMPLE_PATH)
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_path = temp_file.name
                source_path = temp_path

        dataset = load_budget_actual_csv(source_path)
        summary = analyze_budget_variance(
            dataset,
            materiality_rate=materiality_rate,
            materiality_amount=materiality_amount,
        )
        if mode == "llm":
            report = generate_llm_budget_variance_report(summary)
        else:
            report = render_budget_variance_report(summary)

        st.caption(f"数据来源：{uploaded_file.name if uploaded_file else DEFAULT_SAMPLE_PATH}")
        st.caption(f"报告模式：{mode}")
        _render_kpis(summary)
        _render_major_variance_table(summary)
        _render_insight_flags(summary.insight_flags)

        st.subheader("Markdown 中文报告")
        st.markdown(report)
        st.download_button(
            "下载 Markdown 报告",
            data=report,
            file_name="budget_variance_report.md",
            mime="text/markdown",
            use_container_width=True,
        )
    except (RuntimeError, ValueError) as exc:
        st.error(f"数据处理失败：{exc}")
    finally:
        if temp_path is not None:
            Path(temp_path).unlink(missing_ok=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_kpis(summary) -> None:
    kpis = [
        ("预算总额", format_amount(summary.total_budget)),
        ("实际总额", format_amount(summary.total_actual)),
        ("总差异", format_amount(summary.total_variance)),
        ("总差异率", format_rate(summary.total_variance_rate)),
        ("重大偏差数量", str(summary.material_variance_count)),
        ("不利偏差数量", str(summary.unfavorable_variance_count)),
    ]

    columns = st.columns(3)
    for index, (label, value) in enumerate(kpis):
        with columns[index % 3]:
            st.markdown(
                f"""
                <div class="metric-card">
                  <div class="metric-label">{label}</div>
                  <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_major_variance_table(summary) -> None:
    st.subheader("重大偏差项目")
    rows = [
        {
            "部门": item.department,
            "科目": item.account,
            "预算金额": format_amount(item.budget_amount),
            "实际金额": format_amount(item.actual_amount),
            "差异金额": format_amount(item.variance_amount),
            "差异率": format_rate(item.variance_rate),
            "方向": translate_direction(item.direction),
            "严重性": translate_severity(item.severity),
            "主要原因": item.business_driver,
        }
        for item in summary.major_items[:10]
    ]
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("本期未识别重大偏差项目。")


def _render_insight_flags(insight_flags: list[str]) -> None:
    st.subheader("管理关注提示")
    if not insight_flags:
        st.info("本期未生成明显管理关注提示。")
        return

    for flag in insight_flags:
        st.markdown(f'<div class="insight-card">{flag}</div>', unsafe_allow_html=True)


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: #f5fbff;
            color: #102033;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }
        .app-shell {
            color: #102033;
        }
        .eyebrow {
            color: #0891b2;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0;
            margin-bottom: 0.2rem;
            text-transform: uppercase;
        }
        .subtitle {
            color: #486173;
            font-size: 1.08rem;
            margin-top: -0.6rem;
            margin-bottom: 1.4rem;
        }
        .metric-card {
            background: linear-gradient(180deg, #ffffff 0%, #f8fdff 100%);
            border: 1px solid #d8eef4;
            border-left: 5px solid #0ea5a8;
            border-radius: 8px;
            box-shadow: 0 10px 26px rgba(21, 94, 117, 0.08);
            margin-bottom: 1rem;
            padding: 1rem 1.1rem;
        }
        .metric-label {
            color: #5b7083;
            font-size: 0.84rem;
            font-weight: 600;
            margin-bottom: 0.35rem;
        }
        .metric-value {
            color: #0f3f57;
            font-size: 1.45rem;
            font-weight: 760;
            line-height: 1.2;
        }
        .insight-card {
            background: #e8f7fb;
            border: 1px solid #b9e4ec;
            border-radius: 8px;
            color: #164e63;
            margin: 0.45rem 0;
            padding: 0.75rem 0.9rem;
        }
        [data-testid="stSidebar"] {
            background: #eef8fb;
        }
        div.stButton > button {
            background: #0e7490;
            border: 1px solid #0e7490;
            color: white;
            font-weight: 700;
        }
        div.stButton > button:hover {
            background: #0f9f9c;
            border-color: #0f9f9c;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
