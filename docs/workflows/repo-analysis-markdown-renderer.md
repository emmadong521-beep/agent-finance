# Repo Analysis Markdown Renderer

## Purpose

`render_repo_analysis_markdown()` converts a `RepoAnalysisResult` into a
human-readable Markdown report. It is a pure presentation function — it does
not modify the result or call any external service.

## Output Structure

The rendered Markdown has six fixed sections:

1. **① 项目整体介绍** — summary + overview
2. **② 架构说明** — architecture analysis
3. **③ 模块关系图** — Mermaid `graph TD`
4. **④ 数据流** — data flow description
5. **⑤ 系统设计** — system design notes
6. **⑥ 工程笔记** — engineering metadata

## Mermaid Graph Generation

The module relationship graph is derived from `analysis_sections["modules"]`:

- If the modules section contains `Root directories: ['dir1', 'dir2', ...]`,
  the renderer generates `Repo --> dir1`, `Repo --> dir2`, etc.
- If no directories can be parsed, a conservative fallback graph is emitted
  showing the generic Repository → README / Root File Tree / Key Files
  relationship.

## CLI Usage

```bash
python3 runtime/workflows/run_repo_analysis.py https://github.com/owner/repo --format markdown
```

The default output format remains JSON:
```bash
python3 runtime/workflows/run_repo_analysis.py https://github.com/owner/repo --format json
```
