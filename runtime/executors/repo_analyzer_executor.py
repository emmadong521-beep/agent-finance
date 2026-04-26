"""Rule-based repository analyzer executor.

v0.9 scope: generate a structured Markdown report from RepoContext-enriched
task descriptions without cloning repositories or calling external tools.
"""

from __future__ import annotations

import ast
from typing import Any

from runtime.executors.base_executor import (
    BaseExecutor,
    ExecutionContext,
    ExecutionResult,
    Task,
)


class RepoAnalyzerExecutor(BaseExecutor):
    """Analyze repository context using deterministic rules."""

    def name(self) -> str:
        return "repo-analyzer"

    def is_available(self) -> bool:
        return True

    def execute(self, task: Task, context: ExecutionContext) -> ExecutionResult:
        repo_name = str(task.metadata.get("repo_name") or task.project_name or "unknown")
        repo_url = task.metadata.get("repo_url")
        repo_context_used = bool(task.metadata.get("repo_context_used"))

        parsed = self._parse_description(task.description)
        report = self._build_report(
            repo_name=repo_name,
            repo_url=repo_url if isinstance(repo_url, str) else None,
            repo_context_used=repo_context_used,
            parsed=parsed,
        )

        return ExecutionResult(
            task_id=task.task_id,
            executor_name=self.name(),
            status="completed",
            summary=f"已完成 {repo_name} 的规则型仓库分析",
            output=report,
            metadata={
                "repo_name": repo_name,
                "repo_url": repo_url,
                "repo_context_used": repo_context_used,
                "analyzer_type": "rule_based",
            },
        )

    def _parse_description(self, description: str) -> dict[str, Any]:
        lines = description.splitlines()
        parsed: dict[str, Any] = {
            "default_branch": self._line_value(lines, "Default branch:"),
            "metadata": self._parse_metadata(self._line_value(lines, "Repository metadata:")),
            "readme_excerpt": self._section_text(
                lines,
                "README excerpt:",
                "Root file tree first 50 entries:",
            ),
            "file_tree": self._section_lines(
                lines,
                "Root file tree first 50 entries:",
                "Key files:",
            ),
            "key_files": self._parse_key_files(lines),
            "key_file_excerpts": self._parse_key_file_excerpts(lines),
        }
        return parsed

    def _build_report(
        self,
        repo_name: str,
        repo_url: str | None,
        repo_context_used: bool,
        parsed: dict[str, Any],
    ) -> str:
        file_tree = parsed["file_tree"]
        key_files = parsed["key_files"]
        key_file_excerpts = parsed["key_file_excerpts"]
        metadata = parsed["metadata"]
        readme_excerpt = parsed["readme_excerpt"]
        default_branch = parsed["default_branch"] or "unknown"

        sections = [
            "## 概览",
            self._overview(repo_name, repo_url, repo_context_used, metadata, readme_excerpt),
            "## 架构线索",
            self._architecture_signals(file_tree, key_files),
            "## 模块线索",
            self._modules(file_tree),
            "## 数据流判断",
            self._data_flow(key_files, key_file_excerpts),
            "## 系统设计位置",
            self._system_design(repo_name, default_branch, repo_context_used),
            "## 工程备注",
            self._engineering_notes(metadata, file_tree, key_files),
            "## 限制",
            (
                "这是规则型分析结果。当前不会递归扫描源码，不会调用 LLM，"
                "不会 clone 仓库，也不会调用 Codex、Hermes、Claude Code 或 Paperclip。"
            ),
        ]
        return "\n\n".join(sections)

    def _overview(
        self,
        repo_name: str,
        repo_url: str | None,
        repo_context_used: bool,
        metadata: dict[str, Any],
        readme_excerpt: str,
    ) -> str:
        description = metadata.get("description") or "未发现仓库描述信息"
        language = metadata.get("language") or "未知"
        readme_signal = (
            f"已读取 README 摘要，长度约 {len(readme_excerpt)} 字符。"
            if readme_excerpt
            else "未读取到 README 摘要。"
        )
        return (
            f"`{repo_name}`（{repo_url or '未提供 URL'}）已基于 RepoContext 进行分析。"
            f"repo_context_used={repo_context_used}。仓库描述：{description}。"
            f"GitHub 语言元数据：{language}。\n\nREADME 线索：{readme_signal}"
        )

    def _architecture_signals(
        self,
        file_tree: list[str],
        key_files: list[str],
    ) -> str:
        signals: list[str] = []
        lower_files = {item.lower() for item in file_tree + key_files}

        if "package.json" in lower_files:
            signals.append("发现 `package.json`，项目可能包含 Node.js / TypeScript / JavaScript 工程。")
        if "pyproject.toml" in lower_files or "requirements.txt" in lower_files:
            signals.append("发现 Python 构建或依赖文件，项目可能包含 Python 工程。")
        if "dockerfile" in lower_files:
            signals.append("发现 `Dockerfile`，存在容器化部署线索。")
        if "readme.md" in lower_files:
            signals.append("发现 `README.md`，可作为产品目标和架构入口说明。")

        if not signals:
            signals.append("根目录未发现高信号的包管理或部署文件。")

        signals.append(f"已观察到的根目录条目：{file_tree[:30]}。")
        signals.append(f"已读取的关键文件：{key_files or '无'}。")
        return "\n".join(f"- {signal}" for signal in signals)

    def _modules(self, file_tree: list[str]) -> str:
        module_hints = {
            ".openclaw": "OpenClaw 配置、提示词和技能相关目录",
            "docs": "文档与设计说明",
            "client": "前端或客户端应用目录",
            "server": "后端或服务端应用目录",
            "src": "主要源码目录",
            "runtime": "运行时代码目录",
            "contracts": "JSON Schema 或接口契约目录",
            "memory": "SQLite memory 相关资产",
            "workspace": "任务工作区",
        }
        found = []
        lower_entries = {item.lower(): item for item in file_tree}
        for key, meaning in module_hints.items():
            if key in lower_entries:
                found.append(f"`{lower_entries[key]}`：{meaning}")

        if not found:
            return "暂未从根目录文件树中识别出已知模块，需要进一步扫描源码确认职责。"
        return "\n".join(f"- {item}" for item in found)

    def _data_flow(
        self,
        key_files: list[str],
        key_file_excerpts: dict[str, str],
    ) -> str:
        available = "、".join(key_files) if key_files else "无关键文件"
        excerpt_signal = ""
        if key_file_excerpts:
            excerpt_signal = " 已读取部分关键文件片段，但这些仍不足以支持源码级数据流判断。"
        return (
            f"当前只检查了 README、根目录文件树和 {available}。"
            "没有递归扫描源码，因此不能推断完整运行时数据流。"
            f"{excerpt_signal}"
        )

    def _system_design(
        self,
        repo_name: str,
        default_branch: str,
        repo_context_used: bool,
    ) -> str:
        return (
            f"`{repo_name}` 基于默认分支 `{default_branch}` 的 RepoContext 进入分析流程。"
            "RepoAnalysisWorkflow 将 RepoContext 写入 Task.description，随后由 "
            "StandardTaskWorkflow 调用本 executor、Darwin 反思和 memory 写回。"
            f"repo_context_used={repo_context_used}。"
        )

    def _engineering_notes(
        self,
        metadata: dict[str, Any],
        file_tree: list[str],
        key_files: list[str],
    ) -> str:
        notes = [
            f"根目录条目数量：{len(file_tree)}。",
            f"关键文件：{key_files or '无'}。",
        ]
        labels = {
            "stars": "stars",
            "forks": "forks",
            "open_issues": "open issues",
            "license": "license",
        }
        for key, label in labels.items():
            if key in metadata:
                notes.append(f"{label}：{metadata[key]}。")
        return "\n".join(f"- {note}" for note in notes)

    def _line_value(self, lines: list[str], prefix: str) -> str:
        for line in lines:
            if line.startswith(prefix):
                return line.removeprefix(prefix).strip()
        return ""

    def _section_lines(
        self,
        lines: list[str],
        start_marker: str,
        end_marker: str,
    ) -> list[str]:
        text = self._section_text(lines, start_marker, end_marker)
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _section_text(
        self,
        lines: list[str],
        start_marker: str,
        end_marker: str,
    ) -> str:
        try:
            start = lines.index(start_marker) + 1
        except ValueError:
            return ""

        end = len(lines)
        for idx in range(start, len(lines)):
            if lines[idx].startswith(end_marker):
                end = idx
                break
        return "\n".join(lines[start:end]).strip()

    def _parse_metadata(self, raw_metadata: str) -> dict[str, Any]:
        if not raw_metadata:
            return {}
        try:
            value = ast.literal_eval(raw_metadata)
        except (SyntaxError, ValueError):
            return {"raw": raw_metadata}
        if isinstance(value, dict):
            return value
        return {"raw": raw_metadata}

    def _parse_key_files(self, lines: list[str]) -> list[str]:
        raw_key_files = self._line_value(lines, "Key files:")
        if not raw_key_files:
            return []
        try:
            value = ast.literal_eval(raw_key_files)
        except (SyntaxError, ValueError):
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        return []

    def _parse_key_file_excerpts(self, lines: list[str]) -> dict[str, str]:
        excerpts: dict[str, str] = {}
        current_name: str | None = None
        current_lines: list[str] = []

        for line in lines:
            if line.startswith("Key file excerpt:"):
                if current_name is not None:
                    excerpts[current_name] = "\n".join(current_lines).strip()
                current_name = line.removeprefix("Key file excerpt:").strip()
                current_lines = []
            elif current_name is not None:
                current_lines.append(line)

        if current_name is not None:
            excerpts[current_name] = "\n".join(current_lines).strip()
        return excerpts

    def _compact(self, value: str, limit: int) -> str:
        return " ".join(value.split())[:limit]
