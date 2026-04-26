from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from finance.agents.budget_variance.analyzer import analyze_budget_variance
from finance.agents.budget_variance.llm_reporter import generate_llm_budget_variance_report
from finance.agents.budget_variance.report_renderer import render_budget_variance_report
from finance.common.csv_loader import load_budget_actual_csv


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        dataset = load_budget_actual_csv(args.input_csv)
        summary = analyze_budget_variance(
            dataset,
            materiality_rate=args.materiality_rate,
            materiality_amount=args.materiality_amount,
        )
        output = _format_output(summary, args.format, args.mode)

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output, encoding="utf-8")
            print(f"已写入: {args.output}")
        else:
            print(output)

        return 0
    except FileNotFoundError:
        print(f"文件不存在: {args.input_csv}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"数据处理失败: {error}", file=sys.stderr)
        return 1
    except RuntimeError as error:
        print(f"数据处理失败: {error}", file=sys.stderr)
        return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Budget Variance & Business Insight Agent on a budget actual CSV.",
    )
    parser.add_argument("input_csv", help="预算实际 CSV 文件路径")
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="输出格式，默认 markdown",
    )
    parser.add_argument(
        "--mode",
        choices=["rule", "llm"],
        default="rule",
        help="报告生成模式，默认 rule；json 输出不会调用 LLM",
    )
    parser.add_argument(
        "--materiality-rate",
        type=float,
        default=0.1,
        help="重大偏差比例阈值，默认 0.1",
    )
    parser.add_argument(
        "--materiality-amount",
        type=float,
        default=50000,
        help="重大偏差金额阈值，默认 50000",
    )
    parser.add_argument("--output", help="输出文件路径")
    return parser


def _format_output(summary, output_format: str, mode: str) -> str:
    if output_format == "json":
        return json.dumps(asdict(summary), ensure_ascii=False, indent=2)
    if mode == "llm":
        return generate_llm_budget_variance_report(summary)
    return render_budget_variance_report(summary)


if __name__ == "__main__":
    raise SystemExit(main())
