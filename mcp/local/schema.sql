-- ============================================================================
-- Local MCP SQLite Schema
-- Purpose: Development sandbox with Claude memory + commit embeddings
-- ============================================================================

-- Skills Registry (local development)
CREATE TABLE IF NOT EXISTS skills (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT,
    status TEXT CHECK(status IN ('dev', 'testing', 'stable', 'approved')) DEFAULT 'dev',
    metadata JSON,
    file_path TEXT,  -- Path to skill YAML/JSON in repo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_skills_status ON skills(status);
CREATE INDEX idx_skills_name ON skills(name);

-- RAG Embeddings (local corpora for development)
CREATE TABLE IF NOT EXISTS rag_embeddings (
    id TEXT PRIMARY KEY,
    corpus TEXT NOT NULL,  -- 'odoo-docs', 'oca-modules', 'custom-addons'
    chunk_text TEXT NOT NULL,
    embedding BLOB NOT NULL,  -- Serialized vector (sentence-transformers)
    metadata JSON,
    source_file TEXT,
    chunk_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rag_corpus ON rag_embeddings(corpus);
CREATE INDEX idx_rag_source ON rag_embeddings(source_file);

-- Conversation Memory (Claude memory - local only, never synced)
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_id TEXT,
    messages JSON NOT NULL,  -- Array of message objects
    context JSON,  -- Session context (project, files, intent)
    summary TEXT,  -- Auto-generated summary
    embedding BLOB,  -- Conversation embedding for similarity search
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived BOOLEAN DEFAULT 0
);

CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);

-- Commit Embeddings (extensible like CLAUDE.md but embedded)
CREATE TABLE IF NOT EXISTS commit_embeddings (
    id TEXT PRIMARY KEY,
    commit_hash TEXT UNIQUE NOT NULL,
    author TEXT,
    commit_message TEXT NOT NULL,
    files_changed JSON,  -- Array of file paths
    additions INTEGER,
    deletions INTEGER,
    commit_date TIMESTAMP,
    embedding BLOB NOT NULL,  -- Embedding of commit message + diff summary
    metadata JSON,  -- Additional context (branch, tags, related issues)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_commits_hash ON commit_embeddings(commit_hash);
CREATE INDEX idx_commits_author ON commit_embeddings(author);
CREATE INDEX idx_commits_date ON commit_embeddings(commit_date DESC);

-- Memory Context Links (links conversations to commits, files, skills)
CREATE TABLE IF NOT EXISTS memory_context_links (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    link_type TEXT CHECK(link_type IN ('commit', 'file', 'skill', 'odoo_record', 'external_doc')),
    link_target TEXT NOT NULL,  -- commit_hash, file_path, skill_id, etc.
    relevance_score REAL,  -- 0.0-1.0 similarity score
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_memory_links_conversation ON memory_context_links(conversation_id);
CREATE INDEX idx_memory_links_type ON memory_context_links(link_type);
CREATE INDEX idx_memory_links_target ON memory_context_links(link_target);

-- Session Context (current working context - like .vscode/settings.json but dynamic)
CREATE TABLE IF NOT EXISTS session_context (
    id TEXT PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    workspace_root TEXT,
    active_files JSON,  -- Recently opened files
    active_skills JSON,  -- Currently loaded skills
    odoo_instance TEXT,  -- 'odoo_lab' or 'odoo_erp'
    user_preferences JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_session_context_session ON session_context(session_id);

-- MCP Tool Usage Metrics (local analytics)
CREATE TABLE IF NOT EXISTS tool_usage_metrics (
    id TEXT PRIMARY KEY,
    tool_name TEXT NOT NULL,
    operation TEXT,
    latency_ms INTEGER,
    success BOOLEAN,
    error_message TEXT,
    context JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tool_usage_tool ON tool_usage_metrics(tool_name);
CREATE INDEX idx_tool_usage_created ON tool_usage_metrics(created_at DESC);

-- Views for common queries

-- Recent conversations with context
CREATE VIEW IF NOT EXISTS recent_conversations AS
SELECT
    c.id,
    c.session_id,
    c.summary,
    c.created_at,
    c.updated_at,
    COUNT(mcl.id) as linked_items,
    GROUP_CONCAT(DISTINCT mcl.link_type) as link_types
FROM conversations c
LEFT JOIN memory_context_links mcl ON c.id = mcl.conversation_id
WHERE c.archived = 0
GROUP BY c.id
ORDER BY c.updated_at DESC
LIMIT 50;

-- Skills by status
CREATE VIEW IF NOT EXISTS skills_by_status AS
SELECT
    status,
    COUNT(*) as count,
    GROUP_CONCAT(name, ', ') as skill_names
FROM skills
GROUP BY status;

-- Recent commits with high relevance
CREATE VIEW IF NOT EXISTS recent_commits AS
SELECT
    commit_hash,
    author,
    commit_message,
    commit_date,
    additions,
    deletions
FROM commit_embeddings
ORDER BY commit_date DESC
LIMIT 100;
