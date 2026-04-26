PRAGMA foreign_keys = ON;

-- =========================
-- 1) Sessions
-- A task/session execution unit
-- =========================
CREATE TABLE IF NOT EXISTS sessions (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  session_key   TEXT NOT NULL UNIQUE,
  task_title    TEXT NOT NULL,
  project_name  TEXT,
  agent_name    TEXT,
  status        TEXT NOT NULL DEFAULT 'running'
                CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
  started_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ended_at      TEXT,
  summary       TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_project_name ON sessions(project_name);
CREATE INDEX IF NOT EXISTS idx_sessions_agent_name  ON sessions(agent_name);
CREATE INDEX IF NOT EXISTS idx_sessions_status       ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_started_at   ON sessions(started_at);

-- =========================
-- 2) Messages
-- Conversation / execution trace
-- =========================
CREATE TABLE IF NOT EXISTS messages (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id  INTEGER NOT NULL,
  role        TEXT NOT NULL
              CHECK (role IN ('system', 'user', 'assistant', 'tool', 'reflection')),
  content     TEXT NOT NULL,
  created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_session_id  ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_role        ON messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_created_at  ON messages(created_at);

-- Full-text search over messages
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
  content,
  content='messages',
  content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
  INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
END;

CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
  INSERT INTO messages_fts(messages_fts, rowid, content)
    VALUES('delete', old.id, old.content);
END;

CREATE TRIGGER IF NOT EXISTS messages_au AFTER UPDATE ON messages BEGIN
  INSERT INTO messages_fts(messages_fts, rowid, content)
    VALUES('delete', old.id, old.content);
  INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
END;

-- =========================
-- 3) Tool Calls
-- Tool usage records
-- =========================
CREATE TABLE IF NOT EXISTS tool_calls (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id      INTEGER NOT NULL,
  tool_name       TEXT NOT NULL,
  arguments_json  TEXT,
  result_summary  TEXT,
  success         INTEGER NOT NULL DEFAULT 1 CHECK (success IN (0, 1)),
  created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tool_calls_session_id  ON tool_calls(session_id);
CREATE INDEX IF NOT EXISTS idx_tool_calls_tool_name   ON tool_calls(tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_calls_success     ON tool_calls(success);
CREATE INDEX IF NOT EXISTS idx_tool_calls_created_at  ON tool_calls(created_at);

-- =========================
-- 4) Memory Items
-- Long-term structured memory
-- =========================
CREATE TABLE IF NOT EXISTS memory_items (
  id                  INTEGER PRIMARY KEY AUTOINCREMENT,
  memory_type         TEXT NOT NULL
                      CHECK (
                        memory_type IN (
                          'project_context',
                          'pattern',
                          'anti_pattern',
                          'decision',
                          'failure',
                          'note'
                        )
                      ),
  title               TEXT NOT NULL,
  content             TEXT NOT NULL,
  importance          INTEGER NOT NULL DEFAULT 3 CHECK (importance BETWEEN 1 AND 5),
  scope               TEXT NOT NULL DEFAULT 'project'
                      CHECK (scope IN ('global', 'project', 'agent')),
  project_name        TEXT,
  agent_name          TEXT,
  source_session_id   INTEGER,
  created_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at          TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  is_active           INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
  FOREIGN KEY (source_session_id) REFERENCES sessions(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_memory_items_type              ON memory_items(memory_type);
CREATE INDEX IF NOT EXISTS idx_memory_items_scope             ON memory_items(scope);
CREATE INDEX IF NOT EXISTS idx_memory_items_project_name      ON memory_items(project_name);
CREATE INDEX IF NOT EXISTS idx_memory_items_agent_name        ON memory_items(agent_name);
CREATE INDEX IF NOT EXISTS idx_memory_items_importance        ON memory_items(importance);
CREATE INDEX IF NOT EXISTS idx_memory_items_is_active         ON memory_items(is_active);
CREATE INDEX IF NOT EXISTS idx_memory_items_source_session_id ON memory_items(source_session_id);
CREATE INDEX IF NOT EXISTS idx_memory_items_updated_at        ON memory_items(updated_at);

-- Full-text search over memory content
CREATE VIRTUAL TABLE IF NOT EXISTS memory_items_fts USING fts5(
  title,
  content,
  content='memory_items',
  content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS memory_items_ai AFTER INSERT ON memory_items BEGIN
  INSERT INTO memory_items_fts(rowid, title, content)
    VALUES (new.id, new.title, new.content);
END;

CREATE TRIGGER IF NOT EXISTS memory_items_ad AFTER DELETE ON memory_items BEGIN
  INSERT INTO memory_items_fts(memory_items_fts, rowid, title, content)
    VALUES('delete', old.id, old.title, old.content);
END;

CREATE TRIGGER IF NOT EXISTS memory_items_au AFTER UPDATE ON memory_items BEGIN
  INSERT INTO memory_items_fts(memory_items_fts, rowid, title, content)
    VALUES('delete', old.id, old.title, old.content);
  INSERT INTO memory_items_fts(rowid, title, content)
    VALUES (new.id, new.title, new.content);
END;

CREATE TRIGGER IF NOT EXISTS memory_items_touch_updated_at
AFTER UPDATE OF title, content, importance, scope, project_name, agent_name, is_active
ON memory_items
BEGIN
  UPDATE memory_items
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- =========================
-- 5) Memory Links
-- Optional graph-like relationships
-- =========================
CREATE TABLE IF NOT EXISTS memory_links (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  from_memory_id  INTEGER NOT NULL,
  to_memory_id    INTEGER NOT NULL,
  link_type       TEXT NOT NULL
                  CHECK (
                    link_type IN (
                      'related_to',
                      'supports',
                      'contradicts',
                      'derived_from',
                      'applies_to',
                      'caused_by'
                    )
                  ),
  created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (from_memory_id) REFERENCES memory_items(id) ON DELETE CASCADE,
  FOREIGN KEY (to_memory_id)   REFERENCES memory_items(id) ON DELETE CASCADE,
  CHECK (from_memory_id <> to_memory_id)
);

CREATE INDEX IF NOT EXISTS idx_memory_links_from ON memory_links(from_memory_id);
CREATE INDEX IF NOT EXISTS idx_memory_links_to   ON memory_links(to_memory_id);
CREATE INDEX IF NOT EXISTS idx_memory_links_type ON memory_links(link_type);

-- Prevent duplicate links
CREATE UNIQUE INDEX IF NOT EXISTS uq_memory_links_unique
  ON memory_links(from_memory_id, to_memory_id, link_type);

-- =========================
-- 6) Optional view for active memory
-- =========================
CREATE VIEW IF NOT EXISTS active_memory_items AS
SELECT *
FROM memory_items
WHERE is_active = 1;
