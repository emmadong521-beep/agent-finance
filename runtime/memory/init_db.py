"""Initialize Agent OS SQLite database from schema.sql.

Usage:
    python runtime/memory/init_db.py
"""

import sqlite3
import sys
from pathlib import Path

# Resolve paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = PROJECT_ROOT / "memory" / "schema.sql"
DB_PATH = PROJECT_ROOT / "memory" / "memory.db"


def init_db(db_path: Path | None = None, schema_path: Path | None = None) -> Path:
    """Create (or reconnect to) the SQLite database and run schema.sql.

    Idempotent: running multiple times is safe because every CREATE uses
    IF NOT EXISTS.

    Returns:
        Path to the created / existing database file.
    """
    db_path = db_path or DB_PATH
    schema_path = schema_path or SCHEMA_PATH

    if not schema_path.exists():
        print(f"ERROR: schema not found at {schema_path}", file=sys.stderr)
        sys.exit(1)

    db_path.parent.mkdir(parents=True, exist_ok=True)

    schema_sql = schema_path.read_text(encoding="utf-8")

    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_sql)

    print(f"✅ Database initialized at {db_path}")
    return db_path


if __name__ == "__main__":
    init_db()
