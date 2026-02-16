"""
SQLite database initialization and connection management
"""
import aiosqlite
from pathlib import Path
from typing import AsyncIterator
from contextlib import asynccontextmanager
from .config import settings


SCHEMA_SQL = """
-- Skills Registry (local development)
CREATE TABLE IF NOT EXISTS skills (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT,
    status TEXT CHECK(status IN ('dev', 'testing', 'stable', 'approved')) DEFAULT 'dev',
    metadata JSON,
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_skills_status ON skills(status);
CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);

-- RAG Embeddings
CREATE TABLE IF NOT EXISTS rag_embeddings (
    id TEXT PRIMARY KEY,
    corpus TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding BLOB NOT NULL,
    metadata JSON,
    source_file TEXT,
    chunk_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rag_corpus ON rag_embeddings(corpus);

-- Conversation Memory (Claude memory)
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_id TEXT,
    messages JSON NOT NULL,
    context JSON,
    summary TEXT,
    embedding BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived BOOLEAN DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);

-- Commit Embeddings
CREATE TABLE IF NOT EXISTS commit_embeddings (
    id TEXT PRIMARY KEY,
    commit_hash TEXT UNIQUE NOT NULL,
    author TEXT,
    commit_message TEXT NOT NULL,
    files_changed JSON,
    additions INTEGER,
    deletions INTEGER,
    commit_date TIMESTAMP,
    embedding BLOB NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_commits_hash ON commit_embeddings(commit_hash);

-- Memory Context Links
CREATE TABLE IF NOT EXISTS memory_context_links (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    link_type TEXT CHECK(link_type IN ('commit', 'file', 'skill', 'odoo_record', 'external_doc')),
    link_target TEXT NOT NULL,
    relevance_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_memory_links_conversation ON memory_context_links(conversation_id);

-- Session Context
CREATE TABLE IF NOT EXISTS session_context (
    id TEXT PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    workspace_root TEXT,
    active_files JSON,
    active_skills JSON,
    odoo_instance TEXT,
    user_preferences JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tool Usage Metrics
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
"""


async def init_database(db_path: Path):
    """Initialize SQLite database with schema"""
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(SCHEMA_SQL)
        await db.commit()


async def init_all_databases():
    """Initialize all SQLite databases"""
    await init_database(settings.skills_db_path)
    await init_database(settings.rag_db_path)
    await init_database(settings.memory_db_path)


@asynccontextmanager
async def get_skills_db() -> AsyncIterator[aiosqlite.Connection]:
    """Get async connection to skills database"""
    async with aiosqlite.connect(settings.skills_db_path) as db:
        db.row_factory = aiosqlite.Row
        yield db


@asynccontextmanager
async def get_rag_db() -> AsyncIterator[aiosqlite.Connection]:
    """Get async connection to RAG database"""
    async with aiosqlite.connect(settings.rag_db_path) as db:
        db.row_factory = aiosqlite.Row
        yield db


@asynccontextmanager
async def get_memory_db() -> AsyncIterator[aiosqlite.Connection]:
    """Get async connection to memory database"""
    async with aiosqlite.connect(settings.memory_db_path) as db:
        db.row_factory = aiosqlite.Row
        yield db
