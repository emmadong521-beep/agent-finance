"""Demo: verify the v0.2 SQLite Memory Backbone end-to-end.

Simulates:
1. Initialize database
2. Create a session
3. Write messages
4. Write a pattern memory item (Darwin reflection)
5. Search memory
6. Print prefetch result

Usage:
    python runtime/memory/demo_memory.py
"""

import json
import sys
from pathlib import Path

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from runtime.memory.init_db import init_db
from runtime.memory.memory_service import MemoryService

DB_PATH = PROJECT_ROOT / "memory" / "memory.db"


def main() -> None:
    # ── 1. Initialize database ──────────────────────────────────────
    print("=" * 60)
    print("Step 1: Initialize database")
    print("=" * 60)
    init_db()

    # ── 2. Create a session ────────────────────────────────────────
    print()
    print("=" * 60)
    print("Step 2: Create a session")
    print("=" * 60)
    mem = MemoryService()

    session_id = mem.create_session(
        task_title="Analyze GitHub repo architecture",
        project_name="agent-os",
        agent_name="main-agent",
    )
    print(f"  session_id = {session_id}")

    # ── 3. Write messages ──────────────────────────────────────────
    print()
    print("=" * 60)
    print("Step 3: Write messages")
    print("=" * 60)
    mem.add_message(session_id, "user", "Analyze the architecture of this repo.")
    mem.add_message(
        session_id,
        "assistant",
        "The repo follows a layered architecture with 6 layers...",
    )
    mem.add_message(
        session_id,
        "reflection",
        "Loading project context before analysis was effective.",
    )
    print("  ✅ 3 messages written")

    # ── 4. Write a pattern (Darwin reflection) ─────────────────────
    print()
    print("=" * 60)
    print("Step 4: Write a pattern memory item (Darwin reflection)")
    print("=" * 60)
    mem.add_memory_item(
        memory_type="pattern",
        title="Read project context before execution",
        content="Before every non-trivial task, load project context and relevant patterns from memory.",
        importance=4,
        scope="project",
        project_name="agent-os",
        agent_name="main-agent",
        source_session_id=session_id,
    )
    print("  ✅ Pattern written")

    # Also write a project context and an anti-pattern for richer demo
    mem.add_memory_item(
        memory_type="project_context",
        title="Agent OS tech stack",
        content="Python 3.11+, SQLite, OpenClaw, FTS5 for search. No external vector DB.",
        importance=5,
        scope="project",
        project_name="agent-os",
    )
    mem.add_memory_item(
        memory_type="anti_pattern",
        title="Skipping memory prefetch",
        content="Tasks that skip reading memory tend to repeat mistakes and miss relevant context.",
        importance=4,
        scope="project",
        project_name="agent-os",
    )
    print("  ✅ Project context + anti-pattern written")

    # ── 5. Search memory ───────────────────────────────────────────
    print()
    print("=" * 60)
    print("Step 5: Search memory for 'project context'")
    print("=" * 60)
    results = mem.search_memory("project context", project_name="agent-os")
    for r in results:
        print(f"  [{r['memory_type']}] {r['title']}")
        print(f"    {r['content'][:80]}...")
        print()

    # ── 6. Prefetch for task ───────────────────────────────────────
    print("=" * 60)
    print("Step 6: Prefetch memory for next task")
    print("=" * 60)
    prefetch = mem.prefetch_for_task(
        project_name="agent-os",
        task_keywords="execution memory",
    )
    print(json.dumps(prefetch, indent=2, default=str))

    # ── Cleanup ────────────────────────────────────────────────────
    mem.end_session(session_id, status="completed", summary="Demo completed successfully.")
    mem.close()

    print()
    print("=" * 60)
    print("✅ v0.2 Memory Backbone demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
