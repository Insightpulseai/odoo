#!/usr/bin/env python3
"""
LIB Scanner - Filesystem scanning and indexing for Local Intelligence Brain

Core responsibilities:
- Filesystem traversal with gitignore-style filtering
- Content extraction for FTS5 indexing
- SHA256 computation and change detection
- Soft delete for removed files
- Multi-repository support
"""

import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import List, Set, Dict, Optional, Any
import asyncio
import sys

try:
    import aiosqlite
    HAS_AIOSQLITE = True
    Connection = aiosqlite.Connection
except ImportError:
    HAS_AIOSQLITE = False
    Connection = Any

from lib_db import create_scan_run, update_scan_run


# Text file extensions for content extraction
TEXT_EXTENSIONS = {
    '.py', '.js', '.ts', '.tsx', '.jsx', '.md', '.txt', '.json',
    '.sql', '.yaml', '.yml', '.sh', '.bash', '.toml', '.ini',
    '.conf', '.xml', '.html', '.css', '.scss', '.vue', '.svelte'
}

# Ignore patterns (gitignore-style)
IGNORE_PARTS = {
    'node_modules', '__pycache__', '.git', 'build', 'dist',
    '.venv', 'venv', '.cache', '.next', 'target', '.turbo',
    '.vercel', '.nuxt', '.output', 'coverage', '.pytest_cache',
    '.mypy_cache', '.ruff_cache', '__pypackages__', '.egg-info'
}


def should_ignore(path: Path) -> bool:
    """
    Check if path should be ignored (gitignore patterns)

    Args:
        path: Path to check

    Returns:
        True if path should be ignored
    """
    return any(part in path.parts for part in IGNORE_PARTS)


def compute_sha256(path: Path) -> str:
    """
    Compute SHA256 hash of file

    Args:
        path: File path

    Returns:
        SHA256 hex digest
    """
    sha256 = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (PermissionError, OSError):
        return ""


def extract_content(path: Path, max_size_kb: int = 50) -> Optional[str]:
    """
    Extract text content for FTS5 indexing

    Args:
        path: File path
        max_size_kb: Maximum file size to read (KB)

    Returns:
        Extracted content or None
    """
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return None

    try:
        # Check file size
        if path.stat().st_size > max_size_kb * 1024:
            return None

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read(max_size_kb * 1024)
            return content
    except (UnicodeDecodeError, PermissionError, OSError):
        return None


async def process_file(
    db: Connection,
    path: Path,
    repo_root: Path,
    stats: Dict[str, int]
) -> None:
    """
    Process single file - extract metadata and content

    Args:
        db: Database connection
        path: File path
        repo_root: Repository root path
        stats: Statistics dict to update
    """
    # Get file metadata
    try:
        stat = path.stat()
    except (PermissionError, OSError):
        return

    mtime_unix = int(stat.st_mtime)
    file_size = stat.st_size

    # Check if file exists in DB
    cursor = await db.execute(
        "SELECT id, mtime_unix, sha256, deleted_at FROM lib_files WHERE path = ?",
        (str(path),)
    )
    row = await cursor.fetchone()

    if row:
        file_id, old_mtime, old_sha, deleted_at = row

        # Undelete if previously deleted
        if deleted_at:
            await db.execute(
                "UPDATE lib_files SET deleted_at = NULL, updated_at = ? WHERE id = ?",
                (datetime.now().isoformat(), file_id)
            )

        # Skip if unchanged
        if mtime_unix == old_mtime:
            return

        # File changed, update
        sha256 = compute_sha256(path)
        if not sha256:
            return

        content = extract_content(path)

        await db.execute(
            """
            UPDATE lib_files
            SET sha256 = ?, bytes = ?, mtime_unix = ?, content = ?,
                updated_at = ?, deleted_at = NULL
            WHERE id = ?
            """,
            (sha256, file_size, mtime_unix, content, datetime.now().isoformat(), file_id)
        )
        stats["updated"] += 1
    else:
        # New file, insert
        sha256 = compute_sha256(path)
        if not sha256:
            return

        ext = path.suffix.lower()
        mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        content = extract_content(path)

        await db.execute(
            """
            INSERT INTO lib_files
            (path, sha256, bytes, mtime_unix, kind, ext, mime, repo_root, content)
            VALUES (?, ?, ?, ?, 'file', ?, ?, ?, ?)
            """,
            (str(path), sha256, file_size, mtime_unix, ext, mime, str(repo_root), content)
        )
        stats["new"] += 1


async def mark_deleted_files(
    db: Connection,
    scan_roots: List[Path],
    scanned_paths: Set[str],
    stats: Dict[str, int]
) -> None:
    """
    Soft delete files that exist in DB but not in filesystem

    Args:
        db: Database connection
        scan_roots: List of scanned root paths
        scanned_paths: Set of paths found during scan
        stats: Statistics dict to update
    """
    for root in scan_roots:
        cursor = await db.execute(
            """
            SELECT path FROM lib_files
            WHERE repo_root = ? AND deleted_at IS NULL
            """,
            (str(root),)
        )
        rows = await cursor.fetchall()

        for (path,) in rows:
            if path not in scanned_paths:
                await db.execute(
                    "UPDATE lib_files SET deleted_at = ? WHERE path = ?",
                    (datetime.now().isoformat(), path)
                )
                stats["deleted"] += 1


async def scan_repository(
    scan_roots: List[Path],
    db_path: Path,
    verbose: bool = False
) -> Dict[str, int]:
    """
    Scan filesystem and update lib.db

    Args:
        scan_roots: List of root paths to scan
        db_path: Path to SQLite database
        verbose: Print progress

    Returns:
        Statistics dict with scan results
    """
    if not HAS_AIOSQLITE:
        raise ImportError("aiosqlite is required for async scanner operations. Install with: pip install aiosqlite")

    async with aiosqlite.connect(str(db_path)) as db:
        # Create scan run
        run_id = await create_scan_run(db, [str(r) for r in scan_roots])
        stats = {"scanned": 0, "new": 0, "updated": 0, "deleted": 0}

        # Track all scanned paths
        scanned_paths = set()

        for root in scan_roots:
            if verbose:
                print(f"Scanning {root}...")

            # Walk filesystem
            for path in root.rglob("*"):
                if should_ignore(path):
                    continue

                if path.is_file():
                    scanned_paths.add(str(path))
                    await process_file(db, path, root, stats)
                    stats["scanned"] += 1

                    if verbose and stats["scanned"] % 100 == 0:
                        print(f"  Scanned {stats['scanned']} files...")

        # Soft delete files not found in scan
        if verbose:
            print("Checking for deleted files...")
        await mark_deleted_files(db, scan_roots, scanned_paths, stats)

        # Finalize run
        await update_scan_run(db, run_id, stats)
        await db.commit()

        if verbose:
            print(f"✅ Scan complete:")
            print(f"   Files scanned: {stats['scanned']}")
            print(f"   New: {stats['new']}")
            print(f"   Updated: {stats['updated']}")
            print(f"   Deleted: {stats['deleted']}")

        return stats


async def main():
    """CLI entry point"""
    if len(sys.argv) < 3:
        print("Usage: lib_scan.py --scan-root <path> --db-path <path> [--verbose]")
        sys.exit(1)

    scan_root = None
    db_path = None
    verbose = "--verbose" in sys.argv

    for i, arg in enumerate(sys.argv):
        if arg == "--scan-root" and i + 1 < len(sys.argv):
            scan_root = Path(sys.argv[i + 1])
        if arg == "--db-path" and i + 1 < len(sys.argv):
            db_path = Path(sys.argv[i + 1])

    if not scan_root or not db_path:
        print("Error: --scan-root and --db-path are required")
        sys.exit(1)

    await scan_repository([scan_root], db_path, verbose=verbose)


if __name__ == "__main__":
    asyncio.run(main())
