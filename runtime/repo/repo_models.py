"""Repository context models for Agent OS."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RepoContext:
    """Basic context fetched from a public repository."""

    repo_name: str
    repo_url: str
    default_branch: str | None = None
    readme: str | None = None
    file_tree: list[str] = field(default_factory=list)
    key_files: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
