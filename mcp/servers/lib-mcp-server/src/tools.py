"""
LIB MCP Tools - Tool definitions and handlers

Provides 5 MCP tools:
1. lib_search_files - Search by extension, path pattern, or metadata
2. lib_get_file_info - Get detailed metadata for specific file
3. lib_scan_directory - Trigger manual scan of directory
4. lib_query_runs - Get scan run history
5. lib_fts_search - Full-text search across content
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import aiosqlite

# Add scripts/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts" / "lib"))

from lib_db import get_file_by_path, search_files, fts_search
from lib_scan import scan_repository
from .config import settings


async def get_lib_db():
    """Get database connection"""
    return aiosqlite.connect(str(settings.lib_db_path))


async def handle_search_files(
    query: Optional[str] = None,
    ext: Optional[str] = None,
    mime: Optional[str] = None,
    repo_root: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Search files by metadata

    Args:
        query: Path pattern (LIKE query)
        ext: File extension filter (e.g., '.py')
        mime: MIME type filter (e.g., 'text/x-python')
        repo_root: Repository root filter
        limit: Maximum results (default 100)

    Returns:
        Search results with file metadata
    """
    async with get_lib_db() as db:
        results = await search_files(db, query, ext, mime, repo_root, limit)

    return {
        "results": results,
        "count": len(results),
        "limit": limit
    }


async def handle_get_file_info(path: str) -> Dict[str, Any]:
    """
    Get detailed metadata for specific file

    Args:
        path: Absolute file path

    Returns:
        File metadata or error
    """
    async with get_lib_db() as db:
        file_info = await get_file_by_path(db, path)

    if not file_info:
        return {
            "error": "File not found",
            "path": path
        }

    return file_info


async def handle_scan_directory(path: str) -> Dict[str, Any]:
    """
    Trigger manual scan of directory

    Args:
        path: Directory path to scan

    Returns:
        Scan statistics
    """
    scan_path = Path(path)

    if not scan_path.exists():
        return {
            "error": "Path does not exist",
            "path": path
        }

    if not scan_path.is_dir():
        return {
            "error": "Path is not a directory",
            "path": path
        }

    stats = await scan_repository([scan_path], settings.lib_db_path, verbose=False)

    return {
        "path": path,
        "stats": stats
    }


async def handle_query_runs(limit: int = 10) -> Dict[str, Any]:
    """
    Get scan run history

    Args:
        limit: Maximum runs to return (default 10)

    Returns:
        List of scan runs
    """
    async with get_lib_db() as db:
        cursor = await db.execute(
            """
            SELECT id, started_at, finished_at, scan_roots, files_scanned,
                   files_new, files_updated, files_deleted, status, duration_sec
            FROM lib_runs
            ORDER BY started_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = await cursor.fetchall()

    runs = [
        {
            "id": row[0],
            "started_at": row[1],
            "finished_at": row[2],
            "scan_roots": row[3],
            "files_scanned": row[4],
            "files_new": row[5],
            "files_updated": row[6],
            "files_deleted": row[7],
            "status": row[8],
            "duration_sec": row[9]
        }
        for row in rows
    ]

    return {
        "runs": runs,
        "count": len(runs)
    }


async def handle_fts_search(query: str, limit: int = 50) -> Dict[str, Any]:
    """
    Full-text search across file content

    Args:
        query: FTS5 query string
        limit: Maximum results (default 50)

    Returns:
        Search results with content snippets
    """
    if not settings.fts5_enabled:
        return {
            "error": "FTS5 search is disabled",
            "query": query
        }

    async with get_lib_db() as db:
        results = await fts_search(db, query, limit)

    return {
        "results": results,
        "count": len(results),
        "query": query
    }


# Tool definitions for MCP registration
TOOLS = [
    {
        "name": "lib_search_files",
        "description": "Search LIB file registry by extension, path pattern, or metadata",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Path pattern (LIKE query)"
                },
                "ext": {
                    "type": "string",
                    "description": "File extension filter (e.g., '.py')"
                },
                "mime": {
                    "type": "string",
                    "description": "MIME type filter (e.g., 'text/x-python')"
                },
                "repo_root": {
                    "type": "string",
                    "description": "Repository root filter"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results (default 100)",
                    "default": 100
                }
            }
        },
        "handler": handle_search_files
    },
    {
        "name": "lib_get_file_info",
        "description": "Get detailed metadata for specific file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute file path",
                    "required": True
                }
            },
            "required": ["path"]
        },
        "handler": handle_get_file_info
    },
    {
        "name": "lib_scan_directory",
        "description": "Trigger manual scan of directory",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to scan",
                    "required": True
                }
            },
            "required": ["path"]
        },
        "handler": handle_scan_directory
    },
    {
        "name": "lib_query_runs",
        "description": "Get scan run history",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum runs to return (default 10)",
                    "default": 10
                }
            }
        },
        "handler": handle_query_runs
    },
    {
        "name": "lib_fts_search",
        "description": "Full-text search across file content (FTS5)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "FTS5 query string",
                    "required": True
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results (default 50)",
                    "default": 50
                }
            },
            "required": ["query"]
        },
        "handler": handle_fts_search
    }
]
