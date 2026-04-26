"""Markdown renderer for RepoAnalysisResult."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.workflows.repo_analysis import RepoAnalysisResult


def render_repo_analysis_markdown(result: RepoAnalysisResult) -> str:
    """Render a RepoAnalysisResult as human-readable Markdown."""
    sections = result.analysis_sections
    lines: list[str] = [
        f"# {result.repo_name} 项目分析",
        "",
        "## ① 项目整体介绍",
        "",
        result.summary,
        "",
        sections.get("overview", ""),
        "",
        "## ② 架构说明",
        "",
        sections.get("architecture", ""),
        "",
        "## ③ 模块关系图",
        "",
    ]

    lines.append("```mermaid")
    lines.extend(_build_mermaid_graph(sections.get("modules", "")))
    lines.append("```")

    lines.extend(
        [
            "",
            "## ④ 数据流",
            "",
            sections.get("data_flow", ""),
            "",
            "## ⑤ 系统设计",
            "",
            sections.get("system_design", ""),
            "",
            "## ⑥ 工程笔记",
            "",
            sections.get("engineering_notes", ""),
            "",
        ]
    )

    return "\n".join(lines)


def _build_mermaid_graph(modules_section: str) -> list[str]:
    """Build a Mermaid graph TD from the modules analysis section.

    If root directories can be parsed, generate Repo --> dir edges.
    Otherwise, emit a conservative fallback graph.
    """
    directories = _parse_directories(modules_section)

    if directories:
        lines = ["graph TD", "    Repo[Repository]"]
        for dir_name in directories:
            safe_id = _safe_node_id(dir_name)
            lines.append(f"    Repo --> {safe_id}[{dir_name}]")
        return lines

    return [
        "graph TD",
        "    Repo[Repository] --> README[README]",
        "    Repo --> Files[Root File Tree]",
        "    Repo --> KeyFiles[Key Files]",
        "    KeyFiles --> Analysis[Repo Analysis]",
    ]


def _parse_directories(modules_section: str) -> list[str]:
    """Extract directory names from the modules section string.

    Expected format: "Root directories: ['dir1', 'dir2', ...]."
    """
    match = re.search(r"Root directories:\s*\[([^\]]*)\]", modules_section)
    if not match:
        return []
    raw = match.group(1)
    return re.findall(r"'([^']+)'", raw)


def _safe_node_id(name: str) -> str:
    """Convert a directory name to a valid Mermaid node ID."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)
