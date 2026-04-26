"""Chinese Markdown renderer for RepoAnalysisResult."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from runtime.workflows.repo_analysis import RepoAnalysisResult


MODULE_DESCRIPTIONS = {
    ".openclaw": "OpenClaw 配置、提示词和技能相关目录",
    "docs": "文档与设计说明",
    "runtime": "运行时代码，包含 executor、workflow、memory、reflection 等实现",
    "contracts": "JSON Schema / 接口契约",
    "memory": "SQLite memory 相关资产",
    "workspace": "任务工作区",
    "client": "前端或客户端应用目录",
    "server": "后端或服务端应用目录",
    "src": "主要源码目录",
    "scripts": "脚本与自动化辅助工具",
    "shared": "前后端或多模块共享代码",
    "library": "库代码或可复用能力集合",
    "orchestrator": "编排、调度或流程控制相关目录",
    "generators": "生成器或代码/内容生成相关目录",
    "output": "输出产物目录",
}


def render_repo_analysis_markdown(result: RepoAnalysisResult) -> str:
    """Render a RepoAnalysisResult as a Chinese Markdown report."""
    modules = _extract_module_names(result.analysis_sections.get("modules", ""))
    metadata = result.metadata
    workflow_metadata = result.workflow_result.metadata
    execution_metadata = workflow_metadata.get("execution_metadata", {})
    key_files = _as_list(metadata.get("key_files"))

    parts = [
        f"# {result.repo_name} 项目分析",
        "## ① 项目整体介绍",
        _render_overview(result, metadata, workflow_metadata),
        "## ② 架构说明",
        _render_architecture(metadata, modules, key_files),
        "## ③ 模块关系图",
        _render_mermaid_graph(modules),
        "## ④ 模块说明",
        _render_modules(modules),
        "## ⑤ 数据流说明",
        _render_data_flow(),
        "## ⑥ 系统设计说明",
        _render_system_design(),
        "## ⑦ 工程备注",
        _render_engineering_notes(result, metadata, execution_metadata),
    ]

    executor_report = result.workflow_result.output
    if executor_report:
        parts.extend(
            [
                "## ⑧ Executor 规则型分析摘要",
                executor_report,
            ]
        )

    return "\n\n".join(parts)


def _render_overview(
    result: RepoAnalysisResult,
    metadata: dict[str, Any],
    workflow_metadata: dict[str, Any],
) -> str:
    repo_context_used = metadata.get("repo_context_used")
    source_info = [
        "README 摘要",
        "根目录文件树",
        "关键文件列表",
        "GitHub 仓库元数据",
    ]
    if not repo_context_used:
        source_info = ["用户提供的仓库名称和 URL"]

    return "\n".join(
        [
            f"- 仓库名称：`{result.repo_name}`",
            f"- GitHub 地址：{result.repo_url or '未提供'}",
            f"- 当前状态：`{result.status}`",
            f"- 执行器：`{workflow_metadata.get('executor_name', 'unknown')}`",
            f"- 分析依据：{', '.join(source_info)}",
            "- 分析性质：这是基于规则的初步分析，用于快速理解仓库结构线索；不是完整源码审计。",
        ]
    )


def _render_architecture(
    metadata: dict[str, Any],
    modules: list[str],
    key_files: list[str],
) -> str:
    lines = [
        f"- 默认分支：`{metadata.get('default_branch') or '未知'}`",
        f"- 根目录条目数量：{metadata.get('file_tree_count', '未知')}",
    ]

    lower_key_files = {name.lower() for name in key_files}
    if "package.json" in lower_key_files:
        lines.append("- 发现 `package.json`，仓库可能包含 Node.js / TypeScript / JavaScript 工程。")
    if "pyproject.toml" in lower_key_files or "requirements.txt" in lower_key_files:
        lines.append("- 发现 Python 依赖或构建文件，仓库可能包含 Python 工程。")
    if "dockerfile" in lower_key_files:
        lines.append("- 发现 `Dockerfile`，存在容器化部署线索。")
    if "README.md" in key_files:
        lines.append("- 发现 `README.md`，当前分析会优先依赖 README 中的项目说明。")

    if modules:
        lines.append(f"- 根目录模块线索包括：{', '.join(f'`{name}`' for name in modules)}。")
    else:
        lines.append("- 暂未从根目录信息中解析出明确模块，需要进一步源码扫描才能细化架构。")

    lines.append("- 当前架构判断只来自仓库上下文摘要，不能替代递归源码分析。")
    return "\n".join(lines)


def _render_mermaid_graph(modules: list[str]) -> str:
    if not modules:
        return """```mermaid
graph TD
    Repo[Repository] --> README[README]
    Repo --> Files[Root File Tree]
    Repo --> KeyFiles[Key Files]
    KeyFiles --> Analysis[Repo Analysis]
```"""

    lines = [
        "```mermaid",
        "graph TD",
        "    Repo[Repository] --> Analysis[Repo Analysis]",
    ]
    for module in modules[:12]:
        node_id = _mermaid_node_id(module)
        label = module.replace('"', "'")
        lines.append(f'    Repo --> {node_id}["{label}"]')
        lines.append(f"    {node_id} --> Analysis")
    lines.append("```")
    return "\n".join(lines)


def _render_modules(modules: list[str]) -> str:
    if not modules:
        return "暂未能从根目录信息中解析出明确模块。"

    lines = []
    for module in modules:
        description = MODULE_DESCRIPTIONS.get(module, "根目录中的项目组成部分，需进一步扫描源码确认职责")
        lines.append(f"- `{module}`：{description}")
    return "\n".join(lines)


def _render_data_flow() -> str:
    return "\n".join(
        [
            "- 当前仅读取 README、根目录文件树和关键文件。",
            "- 当前没有递归扫描源码，也没有执行真实 LLM 分析。",
            "- 因此不能断言完整业务数据流，只能说明仓库入口信息与模块线索。",
            "- 若需要完整数据流，需要后续接入源码遍历、调用图分析或真实代码执行器。",
        ]
    )


def _render_system_design() -> str:
    return """GitHub 仓库分析在 Agent OS 中的处理链路如下：

```mermaid
graph TD
    URL[GitHub URL] --> Fetcher[GitHubRepoFetcher]
    Fetcher --> Context[RepoContext]
    Context --> Workflow[RepoAnalysisWorkflow]
    Workflow --> Executor[RepoAnalyzerExecutor]
    Executor --> Reflection[DarwinReflector]
    Reflection --> Memory[SQLite Memory]
```"""


def _render_engineering_notes(
    result: RepoAnalysisResult,
    metadata: dict[str, Any],
    execution_metadata: Any,
) -> str:
    lines = [
        f"- repo_context_used：{metadata.get('repo_context_used')}",
        f"- default_branch：{metadata.get('default_branch')}",
        f"- file_tree_count：{metadata.get('file_tree_count')}",
        f"- key_files：{metadata.get('key_files')}",
        f"- written_memory_ids：{result.written_memory_ids}",
    ]
    if isinstance(execution_metadata, dict) and execution_metadata:
        lines.append(f"- execution_metadata：{execution_metadata}")
    return "\n".join(lines)


def _extract_module_names(modules_text: str) -> list[str]:
    quoted = re.findall(r"`([^`]+)`", modules_text)
    if quoted:
        return _filter_module_names(_dedupe(quoted))

    root_dirs_match = re.search(r"Root directories:\s*(.+?)\.", modules_text)
    if root_dirs_match:
        candidates = re.findall(r"'([^']+)'", root_dirs_match.group(1))
        return _filter_module_names(_dedupe(candidates))

    return []


def _mermaid_node_id(name: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z_]", "_", name)
    if not cleaned:
        return "Module"
    if cleaned[0].isdigit():
        cleaned = f"Module_{cleaned}"
    return cleaned


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _filter_module_names(values: list[str]) -> list[str]:
    common_root_files = {
        "LICENSE",
        "README",
        "README.md",
        "README_EN.md",
        "CHANGELOG.md",
        "package.json",
        "package-lock.json",
        "pyproject.toml",
        "requirements.txt",
        "Dockerfile",
        "Makefile",
    }
    return [
        value
        for value in values
        if value not in common_root_files and (value.startswith(".") or "." not in value)
    ]


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []
