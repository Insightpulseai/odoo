#!/usr/bin/env python3
"""
Ingest documentation into Supabase knowledge schema for RAG.

This script chunks markdown files and generates embeddings for semantic search.
Similar to Kapa.ai's doc brain, but under your direct control.

Usage:
    python3 scripts/ingest_docs_to_supabase.py [--source SLUG] [--path PATH]

Environment:
    SUPABASE_DB_URL: PostgreSQL connection string
    OPENAI_API_KEY: OpenAI API key for embeddings
    EMBED_MODEL: OpenAI embedding model (default: text-embedding-3-large)

Examples:
    # Ingest all docs
    python3 scripts/ingest_docs_to_supabase.py

    # Ingest specific source
    python3 scripts/ingest_docs_to_supabase.py --source supabase-docs --path docs/supabase/

    # Dry run
    python3 scripts/ingest_docs_to_supabase.py --dry-run
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any

# Check for required packages
try:
    import psycopg2
    import tiktoken
except ImportError as e:
    print(f"Missing required package: {e.name}")
    print("Install with: pip install psycopg2-binary tiktoken")
    sys.exit(1)

# Optional OpenAI for embeddings
try:
    import openai

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("Warning: openai package not installed. Embeddings will be skipped.")

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

DEFAULT_EMBED_MODEL = "text-embedding-3-large"
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50

KNOWN_SOURCES = {
    "supabase-docs": {
        "kind": "docs",
        "base_url": "https://supabase.com/docs",
        "paths": ["docs/supabase/", "docs/architecture/supabase/"],
    },
    "odoo-oca-18": {
        "kind": "docs",
        "base_url": "https://odoo-community.org/",
        "paths": ["docs/odoo/", "docs/OCA/"],
    },
    "mailgun-docs": {
        "kind": "docs",
        "base_url": "https://documentation.mailgun.com/",
        "paths": ["docs/mailgun/"],
    },
    "ipai-specs": {
        "kind": "spec",
        "base_url": None,
        "paths": ["spec/"],
    },
    "ipai-prds": {
        "kind": "prd",
        "base_url": None,
        "paths": ["docs/prd/"],
    },
    "ipai-internal": {
        "kind": "internal",
        "base_url": None,
        "paths": ["CLAUDE.md", "docs/architecture/"],
    },
}

# -----------------------------------------------------------------------------
# Database Functions
# -----------------------------------------------------------------------------


def get_db_connection() -> "psycopg2.connection":
    """Get PostgreSQL connection from environment."""
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        raise ValueError("SUPABASE_DB_URL environment variable not set")
    return psycopg2.connect(db_url)


def upsert_source(
    conn: "psycopg2.connection",
    slug: str,
    kind: str,
    base_url: Optional[str] = None,
    meta: Optional[Dict] = None,
) -> str:
    """Upsert a knowledge source and return its ID."""
    meta = meta or {}
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO knowledge.sources (slug, kind, base_url, meta)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (slug) DO UPDATE SET
                kind = EXCLUDED.kind,
                base_url = EXCLUDED.base_url,
                meta = EXCLUDED.meta,
                updated_at = NOW()
            RETURNING id;
        """,
            (slug, kind, base_url, json.dumps(meta)),
        )
        row = cur.fetchone()
        conn.commit()
        return str(row[0])


def get_existing_chunks(conn: "psycopg2.connection", source_id: str) -> set:
    """Get existing external_ids for a source."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT external_id FROM knowledge.chunks
            WHERE source_id = %s AND external_id IS NOT NULL;
        """,
            (source_id,),
        )
        return {row[0] for row in cur.fetchall()}


def insert_chunk(
    conn: "psycopg2.connection",
    source_id: str,
    external_id: str,
    content: str,
    metadata: Dict,
    embedding: Optional[List[float]] = None,
) -> str:
    """Insert a chunk and return its ID."""
    with conn.cursor() as cur:
        if embedding:
            cur.execute(
                """
                INSERT INTO knowledge.chunks (source_id, external_id, content, metadata, embedding)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """,
                (source_id, external_id, content, json.dumps(metadata), embedding),
            )
        else:
            cur.execute(
                """
                INSERT INTO knowledge.chunks (source_id, external_id, content, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """,
                (source_id, external_id, content, json.dumps(metadata)),
            )
        row = cur.fetchone()
        conn.commit()
        return str(row[0])


def delete_chunks_by_external_id(
    conn: "psycopg2.connection", source_id: str, external_ids: List[str]
) -> int:
    """Delete chunks by external_id."""
    if not external_ids:
        return 0
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM knowledge.chunks
            WHERE source_id = %s AND external_id = ANY(%s);
        """,
            (source_id, external_ids),
        )
        deleted = cur.rowcount
        conn.commit()
        return deleted


# -----------------------------------------------------------------------------
# Chunking Functions
# -----------------------------------------------------------------------------


def get_tokenizer():
    """Get tiktoken tokenizer for chunk sizing."""
    return tiktoken.get_encoding("cl100k_base")


def chunk_text(
    text: str,
    max_tokens: int = DEFAULT_CHUNK_SIZE,
    overlap_tokens: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Chunk text into smaller pieces with overlap.

    Args:
        text: Text to chunk
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Number of overlapping tokens between chunks

    Returns:
        List of text chunks
    """
    enc = get_tokenizer()
    tokens = enc.encode(text)

    if len(tokens) <= max_tokens:
        return [text]

    chunks = []
    start = 0

    while start < len(tokens):
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)

        # Move start with overlap
        start = end - overlap_tokens

    return chunks


def compute_file_hash(path: Path) -> str:
    """Compute MD5 hash of file content for change detection."""
    content = path.read_text(encoding="utf-8")
    return hashlib.md5(content.encode()).hexdigest()


# -----------------------------------------------------------------------------
# Embedding Functions
# -----------------------------------------------------------------------------


def get_openai_client():
    """Get OpenAI client if available."""
    if not HAS_OPENAI:
        return None
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not set. Embeddings will be skipped.")
        return None
    return openai.OpenAI(api_key=api_key)


def embed_batch(client, texts: List[str], model: str) -> List[List[float]]:
    """
    Generate embeddings for a batch of texts.

    Args:
        client: OpenAI client
        texts: List of texts to embed
        model: Embedding model name

    Returns:
        List of embedding vectors
    """
    if not client:
        return [[] for _ in texts]

    try:
        response = client.embeddings.create(
            model=model,
            input=texts,
        )
        return [d.embedding for d in response.data]
    except Exception as e:
        print(f"Embedding error: {e}")
        return [[] for _ in texts]


# -----------------------------------------------------------------------------
# File Discovery
# -----------------------------------------------------------------------------


def discover_markdown_files(paths: List[str], base_dir: Path) -> List[Path]:
    """
    Discover markdown files from paths.

    Args:
        paths: List of paths (files or directories)
        base_dir: Base directory for relative paths

    Returns:
        List of markdown file paths
    """
    files = []
    for p in paths:
        path = base_dir / p if not os.path.isabs(p) else Path(p)

        if path.is_file() and path.suffix.lower() in (".md", ".mdx"):
            files.append(path)
        elif path.is_dir():
            files.extend(path.rglob("*.md"))
            files.extend(path.rglob("*.mdx"))

    return sorted(set(files))


# -----------------------------------------------------------------------------
# Main Ingestion
# -----------------------------------------------------------------------------


def ingest_source(
    conn: "psycopg2.connection",
    source_slug: str,
    source_config: Dict[str, Any],
    base_dir: Path,
    openai_client,
    embed_model: str,
    dry_run: bool = False,
    verbose: bool = False,
) -> Dict[str, int]:
    """
    Ingest a single source into the knowledge schema.

    Args:
        conn: Database connection
        source_slug: Source identifier
        source_config: Source configuration
        base_dir: Base directory
        openai_client: OpenAI client for embeddings
        embed_model: Embedding model name
        dry_run: If True, don't write to database
        verbose: If True, print verbose output

    Returns:
        Statistics dict
    """
    stats = {"files": 0, "chunks": 0, "skipped": 0, "errors": 0}

    kind = source_config.get("kind", "docs")
    base_url = source_config.get("base_url")
    paths = source_config.get("paths", [])

    if verbose:
        print(f"\n--- Ingesting source: {source_slug} ({kind}) ---")

    # Discover files
    files = discover_markdown_files(paths, base_dir)
    if not files:
        print(f"No markdown files found for source: {source_slug}")
        return stats

    stats["files"] = len(files)
    if verbose:
        print(f"Found {len(files)} markdown files")

    if dry_run:
        for f in files:
            print(f"  Would ingest: {f.relative_to(base_dir)}")
        return stats

    # Upsert source
    source_id = upsert_source(conn, source_slug, kind, base_url, {"paths": paths})

    # Get existing chunks for incremental update
    existing_ids = get_existing_chunks(conn, source_id)
    processed_ids = set()

    # Process files
    for file_path in files:
        try:
            rel_path = str(file_path.relative_to(base_dir))
            file_hash = compute_file_hash(file_path)

            # Read content
            content = file_path.read_text(encoding="utf-8")
            if not content.strip():
                stats["skipped"] += 1
                continue

            # Chunk content
            chunks = chunk_text(content)

            # Generate embeddings if client available
            embeddings = (
                embed_batch(openai_client, chunks, embed_model)
                if openai_client
                else None
            )

            # Insert chunks
            for i, chunk_content in enumerate(chunks):
                external_id = f"{rel_path}#chunk-{i}"
                processed_ids.add(external_id)

                # Skip if unchanged
                if external_id in existing_ids:
                    stats["skipped"] += 1
                    continue

                embedding = embeddings[i] if embeddings else None
                metadata = {
                    "file": rel_path,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "file_hash": file_hash,
                }

                insert_chunk(
                    conn, source_id, external_id, chunk_content, metadata, embedding
                )
                stats["chunks"] += 1

            if verbose:
                print(f"  {rel_path}: {len(chunks)} chunks")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            stats["errors"] += 1

    # Clean up stale chunks
    stale_ids = existing_ids - processed_ids
    if stale_ids:
        deleted = delete_chunks_by_external_id(conn, source_id, list(stale_ids))
        if verbose:
            print(f"  Deleted {deleted} stale chunks")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Ingest documentation into Supabase knowledge schema"
    )
    parser.add_argument("--source", "-s", help="Specific source slug to ingest")
    parser.add_argument("--path", "-p", help="Custom path for source")
    parser.add_argument(
        "--dry-run", "-n", action="store_true", help="Show what would be done"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--model", default=DEFAULT_EMBED_MODEL, help="Embedding model")
    args = parser.parse_args()

    # Find base directory
    script_path = Path(__file__).resolve()
    base_dir = script_path.parent.parent  # odoo-ce/

    if args.verbose:
        print(f"Base directory: {base_dir}")

    # Check database connection
    if not args.dry_run:
        try:
            conn = get_db_connection()
            if args.verbose:
                print("Database connection established")
        except Exception as e:
            print(f"Database connection failed: {e}")
            print("Set SUPABASE_DB_URL environment variable")
            sys.exit(1)
    else:
        conn = None

    # Initialize OpenAI client
    openai_client = get_openai_client() if not args.dry_run else None

    # Build sources to process
    if args.source:
        if args.source in KNOWN_SOURCES:
            sources = {args.source: KNOWN_SOURCES[args.source]}
        else:
            # Custom source
            if not args.path:
                print(f"Unknown source: {args.source}. Use --path to specify path.")
                sys.exit(1)
            sources = {
                args.source: {
                    "kind": "docs",
                    "base_url": None,
                    "paths": [args.path],
                }
            }
    else:
        sources = KNOWN_SOURCES

    # Process sources
    total_stats = {"files": 0, "chunks": 0, "skipped": 0, "errors": 0}

    for slug, config in sources.items():
        stats = ingest_source(
            conn,
            slug,
            config,
            base_dir,
            openai_client,
            args.model,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )

        for key in total_stats:
            total_stats[key] += stats.get(key, 0)

    # Print summary
    print("\n=== Ingestion Summary ===")
    print(f"Files processed: {total_stats['files']}")
    print(f"Chunks inserted: {total_stats['chunks']}")
    print(f"Chunks skipped: {total_stats['skipped']}")
    print(f"Errors: {total_stats['errors']}")

    if conn:
        conn.close()


if __name__ == "__main__":
    main()
