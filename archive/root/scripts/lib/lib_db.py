#!/usr/bin/env python3
"""
LIB Database Layer - SQLite schema and operations for Local Intelligence Brain

Core responsibilities:
- Database initialization with WAL mode
- Schema creation (lib_files, lib_runs, FTS5)
- Query helpers for file operations
- Soft delete support
"""

import asyncio
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
import sys

try:
    import aiosqlite
    HAS_AIOSQLITE = True
    Connection = aiosqlite.Connection
except ImportError:
    HAS_AIOSQLITE = False
    Connection = Any  # Fallback type


SCHEMA_SQL = """
-- Core file registry (with soft delete support)
CREATE TABLE IF NOT EXISTS lib_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    bytes INTEGER NOT NULL,
    mtime_unix INTEGER NOT NULL,
    kind TEXT NOT NULL CHECK(kind IN ('file', 'dir', 'symlink')),
    ext TEXT,
    mime TEXT,
    repo_root TEXT,
    content TEXT,
    deleted_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_files_sha256_path ON lib_files(sha256, path);
CREATE INDEX IF NOT EXISTS idx_files_mtime ON lib_files(mtime_unix);
CREATE INDEX IF NOT EXISTS idx_files_ext ON lib_files(ext);
CREATE INDEX IF NOT EXISTS idx_files_kind ON lib_files(kind);
CREATE INDEX IF NOT EXISTS idx_files_repo_root ON lib_files(repo_root);
CREATE INDEX IF NOT EXISTS idx_files_deleted ON lib_files(deleted_at);

-- Scan run metadata
CREATE TABLE IF NOT EXISTS lib_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at TEXT,
    scan_roots TEXT NOT NULL,
    files_scanned INTEGER DEFAULT 0,
    files_new INTEGER DEFAULT 0,
    files_updated INTEGER DEFAULT 0,
    files_deleted INTEGER DEFAULT 0,
    status TEXT NOT NULL CHECK(status IN ('running', 'completed', 'failed')),
    notes TEXT,
    duration_sec REAL
);

-- FTS5 virtual table with content
CREATE VIRTUAL TABLE IF NOT EXISTS lib_files_fts USING fts5(
    path,
    ext,
    mime,
    content,
    content='lib_files',
    content_rowid='id'
);

-- FTS5 sync triggers
CREATE TRIGGER IF NOT EXISTS lib_files_fts_insert AFTER INSERT ON lib_files BEGIN
    INSERT INTO lib_files_fts(rowid, path, ext, mime, content)
    VALUES (new.id, new.path, new.ext, new.mime, new.content);
END;

CREATE TRIGGER IF NOT EXISTS lib_files_fts_update AFTER UPDATE ON lib_files BEGIN
    UPDATE lib_files_fts
    SET path = new.path, ext = new.ext, mime = new.mime, content = new.content
    WHERE rowid = new.id;
END;

CREATE TRIGGER IF NOT EXISTS lib_files_fts_delete AFTER DELETE ON lib_files BEGIN
    DELETE FROM lib_files_fts WHERE rowid = old.id;
END;
"""


async def init_database(db_path: Path) -> None:
    """
    Initialize LIB database with schema and pragmas

    Args:
        db_path: Path to SQLite database file
    """
    if not HAS_AIOSQLITE:
        raise ImportError("aiosqlite is required for async operations")

    db_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(str(db_path)) as db:
        # Set WAL mode and performance pragmas
        await db.execute("PRAGMA journal_mode = WAL")
        await db.execute("PRAGMA synchronous = NORMAL")
        await db.execute("PRAGMA busy_timeout = 5000")
        await db.execute("PRAGMA cache_size = -64000")  # 64MB

        # Create schema
        await db.executescript(SCHEMA_SQL)
        await db.commit()


async def get_file_by_path(db: Connection, path: str) -> Optional[Dict[str, Any]]:
    """
    Get file metadata by path

    Args:
        db: Database connection
        path: File path

    Returns:
        File metadata dict or None if not found
    """
    cursor = await db.execute(
        """
        SELECT id, path, sha256, bytes, mtime_unix, kind, ext, mime,
               repo_root, content, deleted_at, created_at, updated_at
        FROM lib_files
        WHERE path = ? AND deleted_at IS NULL
        """,
        (path,)
    )
    row = await cursor.fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "path": row[1],
        "sha256": row[2],
        "bytes": row[3],
        "mtime_unix": row[4],
        "kind": row[5],
        "ext": row[6],
        "mime": row[7],
        "repo_root": row[8],
        "content": row[9],
        "deleted_at": row[10],
        "created_at": row[11],
        "updated_at": row[12]
    }


async def search_files(
    db: Connection,
    query: Optional[str] = None,
    ext: Optional[str] = None,
    mime: Optional[str] = None,
    repo_root: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Search files by metadata

    Args:
        db: Database connection
        query: Path pattern (LIKE query)
        ext: File extension filter
        mime: MIME type filter
        repo_root: Repository root filter
        limit: Maximum results

    Returns:
        List of file metadata dicts
    """
    conditions = ["deleted_at IS NULL"]
    params = []

    if query:
        conditions.append("path LIKE ?")
        params.append(f"%{query}%")

    if ext:
        conditions.append("ext = ?")
        params.append(ext)

    if mime:
        conditions.append("mime = ?")
        params.append(mime)

    if repo_root:
        conditions.append("repo_root = ?")
        params.append(repo_root)

    params.append(limit)

    sql = f"""
        SELECT id, path, sha256, bytes, mtime_unix, kind, ext, mime, repo_root
        FROM lib_files
        WHERE {' AND '.join(conditions)}
        ORDER BY path
        LIMIT ?
    """

    cursor = await db.execute(sql, params)
    rows = await cursor.fetchall()

    return [
        {
            "id": row[0],
            "path": row[1],
            "sha256": row[2],
            "bytes": row[3],
            "mtime_unix": row[4],
            "kind": row[5],
            "ext": row[6],
            "mime": row[7],
            "repo_root": row[8]
        }
        for row in rows
    ]


async def fts_search(
    db: Connection,
    query: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Full-text search across file content

    Args:
        db: Database connection
        query: FTS5 query string
        limit: Maximum results

    Returns:
        List of search results with snippets
    """
    cursor = await db.execute(
        """
        SELECT f.path, f.bytes, f.mtime_unix, f.ext, f.mime,
               snippet(lib_files_fts, 3, '<mark>', '</mark>', '...', 32) as snippet,
               rank
        FROM lib_files_fts fts
        JOIN lib_files f ON f.id = fts.rowid
        WHERE lib_files_fts MATCH ? AND f.deleted_at IS NULL
        ORDER BY rank
        LIMIT ?
        """,
        (query, limit)
    )
    rows = await cursor.fetchall()

    return [
        {
            "path": row[0],
            "bytes": row[1],
            "mtime_unix": row[2],
            "ext": row[3],
            "mime": row[4],
            "snippet": row[5],
            "rank": row[6]
        }
        for row in rows
    ]


async def create_scan_run(db: Connection, scan_roots: List[str]) -> int:
    """
    Create a new scan run record

    Args:
        db: Database connection
        scan_roots: List of root paths being scanned

    Returns:
        Run ID
    """
    cursor = await db.execute(
        """
        INSERT INTO lib_runs (scan_roots, status)
        VALUES (?, 'running')
        """,
        (",".join(scan_roots),)
    )
    await db.commit()
    return cursor.lastrowid


async def update_scan_run(
    db: Connection,
    run_id: int,
    stats: Dict[str, int],
    status: str = "completed",
    notes: Optional[str] = None
) -> None:
    """
    Update scan run with final statistics

    Args:
        db: Database connection
        run_id: Run ID to update
        stats: Statistics dict with scanned/new/updated/deleted counts
        status: Final status
        notes: Optional notes
    """
    finished_at = datetime.now().isoformat()

    # Calculate duration
    cursor = await db.execute(
        "SELECT started_at FROM lib_runs WHERE id = ?",
        (run_id,)
    )
    row = await cursor.fetchone()
    if row:
        started = datetime.fromisoformat(row[0])
        duration = (datetime.now() - started).total_seconds()
    else:
        duration = 0

    await db.execute(
        """
        UPDATE lib_runs
        SET finished_at = ?,
            files_scanned = ?,
            files_new = ?,
            files_updated = ?,
            files_deleted = ?,
            status = ?,
            notes = ?,
            duration_sec = ?
        WHERE id = ?
        """,
        (
            finished_at,
            stats.get("scanned", 0),
            stats.get("new", 0),
            stats.get("updated", 0),
            stats.get("deleted", 0),
            status,
            notes,
            duration,
            run_id
        )
    )
    await db.commit()


def init_database_sync(db_path: Path) -> None:
    """Synchronous database initialization for CLI usage"""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))

    # Set WAL mode and performance pragmas
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA cache_size = -64000")

    # Create schema
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: lib_db.py init --db-path <path>")
        sys.exit(1)

    if sys.argv[1] == "init":
        db_path = Path(sys.argv[3] if len(sys.argv) > 3 else ".lib/lib.db")
        print(f"Initializing LIB database at {db_path}...")
        init_database_sync(db_path)
        print(f"✅ Database initialized")
        print(f"   Schema: lib_files, lib_runs, lib_files_fts")
        print(f"   Mode: WAL with NORMAL synchronous")


if __name__ == "__main__":
    main()
