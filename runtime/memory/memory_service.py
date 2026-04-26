"""MemoryService — the core read/write interface for Agent OS long-term memory.

v0.2 scope: SQLite-backed CRUD + FTS5 search + task prefetch.
No vector search, no Paperclip, no auto-skill generation.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "memory" / "memory.db"


class MemoryService:
    """Thin wrapper around the Agent OS SQLite database."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self._conn: sqlite3.Connection | None = None

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._conn.execute("PRAGMA journal_mode = WAL")
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    def create_session(
        self,
        task_title: str,
        project_name: str | None = None,
        agent_name: str | None = None,
    ) -> int:
        """Create a new session and return its id."""
        session_key = f"session:{uuid.uuid4().hex[:12]}"
        cur = self.conn.execute(
            """INSERT INTO sessions (session_key, task_title, project_name, agent_name)
               VALUES (?, ?, ?, ?)""",
            (session_key, task_title, project_name, agent_name),
        )
        self.conn.commit()
        return cur.lastrowid  # type: ignore[return-value]

    def end_session(
        self,
        session_id: int,
        status: str = "completed",
        summary: str | None = None,
    ) -> None:
        """Mark a session as ended."""
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            """UPDATE sessions
               SET status = ?, ended_at = ?, summary = ?
               WHERE id = ?""",
            (status, now, summary, session_id),
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    def add_message(
        self,
        session_id: int,
        role: str,
        content: str,
    ) -> int:
        """Append a message to a session."""
        cur = self.conn.execute(
            """INSERT INTO messages (session_id, role, content)
               VALUES (?, ?, ?)""",
            (session_id, role, content),
        )
        self.conn.commit()
        return cur.lastrowid  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Tool calls
    # ------------------------------------------------------------------

    def add_tool_call(
        self,
        session_id: int,
        tool_name: str,
        arguments: dict | None = None,
        result_summary: str | None = None,
        success: bool = True,
    ) -> int:
        """Record a tool invocation."""
        cur = self.conn.execute(
            """INSERT INTO tool_calls
                   (session_id, tool_name, arguments_json, result_summary, success)
               VALUES (?, ?, ?, ?, ?)""",
            (
                session_id,
                tool_name,
                json.dumps(arguments) if arguments else None,
                result_summary,
                1 if success else 0,
            ),
        )
        self.conn.commit()
        return cur.lastrowid  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Memory items
    # ------------------------------------------------------------------

    def add_memory_item(
        self,
        memory_type: str,
        title: str,
        content: str,
        importance: int = 3,
        scope: str = "project",
        project_name: str | None = None,
        agent_name: str | None = None,
        source_session_id: int | None = None,
    ) -> int:
        """Insert a long-term memory item."""
        cur = self.conn.execute(
            """INSERT INTO memory_items
                   (memory_type, title, content, importance, scope,
                    project_name, agent_name, source_session_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                memory_type,
                title,
                content,
                importance,
                scope,
                project_name,
                agent_name,
                source_session_id,
            ),
        )
        self.conn.commit()
        return cur.lastrowid  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def search_memory(
        self,
        query: str,
        project_name: str | None = None,
        memory_type: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """FTS5 full-text search over memory items (active only)."""
        sql = """
            SELECT m.*
            FROM memory_items m
            JOIN memory_items_fts fts ON fts.rowid = m.id
            WHERE memory_items_fts MATCH ?
              AND m.is_active = 1
        """
        params: list[Any] = [query]

        if project_name is not None:
            sql += " AND m.project_name = ?"
            params.append(project_name)
        if memory_type is not None:
            sql += " AND m.memory_type = ?"
            params.append(memory_type)

        sql += " ORDER BY m.importance DESC, m.updated_at DESC LIMIT ?"
        params.append(limit)

        rows = self.conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def get_project_context(
        self,
        project_name: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Return project_context memory items for a given project."""
        rows = self.conn.execute(
            """SELECT * FROM memory_items
               WHERE memory_type = 'project_context'
                 AND project_name = ?
                 AND is_active = 1
               ORDER BY importance DESC, updated_at DESC
               LIMIT ?""",
            (project_name, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_patterns(
        self,
        project_name: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Return pattern memory items."""
        sql = """
            SELECT * FROM memory_items
            WHERE memory_type = 'pattern'
              AND is_active = 1
        """
        params: list[Any] = []
        if project_name is not None:
            sql += " AND project_name = ?"
            params.append(project_name)
        sql += " ORDER BY importance DESC, updated_at DESC LIMIT ?"
        params.append(limit)

        rows = self.conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def get_anti_patterns(
        self,
        project_name: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Return anti_pattern memory items."""
        sql = """
            SELECT * FROM memory_items
            WHERE memory_type = 'anti_pattern'
              AND is_active = 1
        """
        params: list[Any] = []
        if project_name is not None:
            sql += " AND project_name = ?"
            params.append(project_name)
        sql += " ORDER BY importance DESC, updated_at DESC LIMIT ?"
        params.append(limit)

        rows = self.conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Prefetch
    # ------------------------------------------------------------------

    def prefetch_for_task(
        self,
        project_name: str,
        task_keywords: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Gather relevant memory before a task starts.

        Returns a dict with keys:
            project_context, patterns, anti_patterns, relevant_memories
        """
        result: dict[str, list[dict[str, Any]]] = {
            "project_context": self.get_project_context(project_name),
            "patterns": self.get_patterns(project_name),
            "anti_patterns": self.get_anti_patterns(project_name),
            "relevant_memories": [],
        }

        if task_keywords:
            result["relevant_memories"] = self.search_memory(
                query=task_keywords,
                project_name=project_name,
                limit=10,
            )

        return result
