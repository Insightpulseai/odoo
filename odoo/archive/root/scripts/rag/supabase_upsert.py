#!/usr/bin/env python3
"""Upsert corpus files into Supabase rag.documents + rag.chunks.

Reads ssot/knowledge/corpus_registry.yaml, discovers matching files,
chunks them, and upserts into Supabase via PostgREST.

Usage:
    python scripts/rag/supabase_upsert.py                 # upsert all corpora
    python scripts/rag/supabase_upsert.py --corpus spec_bundles  # single corpus
    python scripts/rag/supabase_upsert.py --dry-run        # preview only
    python scripts/rag/supabase_upsert.py --with-embeddings # generate embeddings (requires OPENAI_API_KEY)

Environment:
    SUPABASE_URL          - Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY - Service role key (bypasses RLS)
    OPENAI_API_KEY        - (optional) For embedding generation
    RAG_TENANT_ID         - (optional) Tenant UUID, defaults to 00000000-0000-0000-0000-000000000001

Exit codes:
    0 = success
    1 = error
"""
from __future__ import annotations

import argparse
import fnmatch
import glob
import hashlib
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Any

import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
REGISTRY_PATH = os.path.join(REPO_ROOT, "ssot", "knowledge", "corpus_registry.yaml")

DEFAULT_TENANT_ID = os.environ.get(
    "RAG_TENANT_ID", "00000000-0000-0000-0000-000000000001"
)


def load_registry() -> dict:
    """Load corpus registry YAML."""
    with open(REGISTRY_PATH) as f:
        return yaml.safe_load(f)


def discover_files(corpus: dict) -> list[str]:
    """Discover files matching corpus glob patterns relative to repo root."""
    matched: set[str] = set()
    include = corpus.get("include_patterns", [])
    exclude = corpus.get("exclude_patterns", [])
    patterns = include if include else [corpus["path"]]

    for pattern in patterns:
        full_pattern = os.path.join(REPO_ROOT, pattern)
        for fpath in glob.glob(full_pattern, recursive=True):
            if os.path.isfile(fpath):
                rel = os.path.relpath(fpath, REPO_ROOT)
                excluded = any(fnmatch.fnmatch(rel, exc) for exc in exclude)
                if not excluded:
                    matched.add(rel)

    return sorted(matched)


def chunk_file(
    file_path: str,
    max_tokens: int = 512,
    overlap_tokens: int = 64,
) -> list[dict[str, Any]]:
    """Split a file into overlapping chunks.

    Uses a simple word-based tokenizer (1 token ~ 1 word for English text).
    Each chunk includes section_path derived from markdown headers.
    """
    abs_path = os.path.join(REPO_ROOT, file_path)
    try:
        with open(abs_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return []

    if not content.strip():
        return []

    words = content.split()
    chunks: list[dict[str, Any]] = []
    section_path = file_path  # default

    i = 0
    while i < len(words):
        end = min(i + max_tokens, len(words))
        chunk_words = words[i:end]
        chunk_text = " ".join(chunk_words)

        # Extract section path from markdown headers in chunk
        for line in chunk_text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                header = stripped.lstrip("#").strip()
                if header:
                    section_path = f"{file_path}#{header}"

        chunks.append(
            {
                "content": chunk_text,
                "section_path": section_path,
                "metadata": {
                    "file_path": file_path,
                    "chunk_index": len(chunks),
                    "word_offset": i,
                },
            }
        )

        if end >= len(words):
            break
        i = end - overlap_tokens

    return chunks


def content_checksum(text: str) -> str:
    """SHA-256 hex digest of text content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_commit_sha() -> str | None:
    """Get current HEAD commit SHA."""
    try:
        import subprocess

        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except FileNotFoundError:
        return None


def generate_embeddings(texts: list[str]) -> list[list[float]] | None:
    """Generate embeddings via OpenAI API. Returns None if API key missing."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        import urllib.request

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        # Batch in groups of 100
        all_embeddings: list[list[float]] = []
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            body = json.dumps(
                {"model": "text-embedding-3-small", "input": batch}
            ).encode("utf-8")

            req = urllib.request.Request(
                "https://api.openai.com/v1/embeddings",
                data=body,
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
                for item in sorted(data["data"], key=lambda x: x["index"]):
                    all_embeddings.append(item["embedding"])

        return all_embeddings
    except Exception as e:
        print(f"  WARNING: Embedding generation failed: {e}", file=sys.stderr)
        return None


def supabase_upsert(
    table: str,
    rows: list[dict],
    on_conflict: str,
    *,
    supabase_url: str,
    service_key: str,
) -> dict:
    """Upsert rows to Supabase via SQL through the Management API.

    The rag schema is not exposed via PostgREST by default, so we use
    the Supabase Management API to execute INSERT ... ON CONFLICT directly.
    Falls back to PostgREST for public schema tables.
    """
    import urllib.request

    # For rag schema tables, use Management API SQL endpoint
    if table.startswith("rag."):
        return _sql_upsert(table, rows, on_conflict)

    # For public schema tables, use PostgREST
    url = f"{supabase_url}/rest/v1/{table}"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }

    body = json.dumps(rows).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"status": resp.status, "count": len(rows)}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return {"status": e.code, "error": error_body, "count": 0}


def _sql_upsert(table: str, rows: list[dict], on_conflict: str) -> dict:
    """Upsert rows via Supabase Management API SQL endpoint.

    Builds INSERT ... ON CONFLICT (on_conflict) DO UPDATE SET ...
    """
    import urllib.request

    access_token = os.environ.get("SUPABASE_ACCESS_TOKEN")
    project_ref = os.environ.get("SUPABASE_PROJECT_REF")

    if not access_token or not project_ref:
        # Derive project_ref from SUPABASE_URL if not set
        supabase_url = os.environ.get("SUPABASE_URL", "")
        if not project_ref and supabase_url:
            # https://<ref>.supabase.co -> <ref>
            project_ref = supabase_url.split("//")[1].split(".")[0]

    if not access_token:
        return {"status": "error", "error": "SUPABASE_ACCESS_TOKEN required for rag schema upserts", "count": 0}

    if not rows:
        return {"status": 200, "count": 0}

    columns = list(rows[0].keys())
    update_cols = [c for c in columns if c != on_conflict]

    # Build VALUES list with proper escaping
    values_parts = []
    for row in rows:
        vals = []
        for col in columns:
            v = row.get(col)
            if v is None:
                vals.append("NULL")
            elif isinstance(v, (int, float)):
                vals.append(str(v))
            elif isinstance(v, list):
                vals.append(f"'{json.dumps(v)}'::jsonb")
            elif isinstance(v, dict):
                vals.append(f"'{json.dumps(v)}'::jsonb")
            else:
                # Escape single quotes
                escaped = str(v).replace("'", "''")
                vals.append(f"'{escaped}'")
        values_parts.append(f"({', '.join(vals)})")

    update_clause = ", ".join(
        f"{c} = EXCLUDED.{c}" for c in update_cols
    )

    sql = f"""INSERT INTO {table} ({', '.join(columns)})
VALUES {', '.join(values_parts)}
ON CONFLICT ({on_conflict}) DO UPDATE SET {update_clause};"""

    url = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "User-Agent": "supabase-rag-upsert/1.0",
    }

    body = json.dumps({"query": sql}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return {"status": resp.status, "count": len(rows)}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return {"status": e.code, "error": error_body[:500], "count": 0}
    except Exception as e:
        return {"status": "error", "error": str(e)[:500], "count": 0}


def process_corpus(
    corpus: dict,
    *,
    dry_run: bool = False,
    with_embeddings: bool = False,
    supabase_url: str | None = None,
    service_key: str | None = None,
) -> dict[str, Any]:
    """Process a single corpus: discover files, chunk, upsert."""
    corpus_id = corpus["id"]
    chunk_params = corpus.get("chunk_params", {})
    max_tokens = chunk_params.get("max_chunk_tokens", 512)
    overlap = chunk_params.get("overlap_tokens", 64)

    files = discover_files(corpus)
    commit_sha = get_commit_sha()

    total_chunks = 0
    doc_rows: list[dict] = []
    chunk_rows: list[dict] = []

    for file_path in files:
        abs_path = os.path.join(REPO_ROOT, file_path)
        try:
            with open(abs_path, encoding="utf-8", errors="replace") as f:
                raw_content = f.read()
        except (OSError, UnicodeDecodeError):
            continue

        checksum = content_checksum(raw_content)
        doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"ipai://{file_path}"))

        doc_rows.append(
            {
                "id": doc_id,
                "tenant_id": DEFAULT_TENANT_ID,
                "source_type": corpus_id,
                "source_url": file_path,
                "title": os.path.basename(file_path),
                "corpus_id": corpus_id,
                "repo_path": file_path,
                "content_checksum": checksum,
                "commit_sha": commit_sha,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        chunks = chunk_file(file_path, max_tokens=max_tokens, overlap_tokens=overlap)
        for chunk in chunks:
            chunk_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"ipai://{file_path}#chunk{chunk['metadata']['chunk_index']}",
                )
            )
            chunk_rows.append(
                {
                    "id": chunk_id,
                    "tenant_id": DEFAULT_TENANT_ID,
                    "document_id": doc_id,
                    "content": chunk["content"],
                    "section_path": chunk["section_path"][:500],
                    "metadata": json.dumps(chunk["metadata"]),
                }
            )
            total_chunks += 1

    result = {
        "corpus_id": corpus_id,
        "files_discovered": len(files),
        "documents": len(doc_rows),
        "chunks": total_chunks,
        "dry_run": dry_run,
    }

    if dry_run:
        print(f"  [DRY-RUN] {corpus_id}: {len(files)} files → {total_chunks} chunks")
        return result

    if not supabase_url or not service_key:
        print(f"  [SKIP] {corpus_id}: No SUPABASE_URL/SERVICE_ROLE_KEY set")
        result["skipped"] = True
        return result

    # Generate embeddings if requested
    if with_embeddings and chunk_rows:
        print(f"  Generating embeddings for {len(chunk_rows)} chunks...")
        texts = [c["content"] for c in chunk_rows]
        embeddings = generate_embeddings(texts)
        if embeddings and len(embeddings) == len(chunk_rows):
            for i, emb in enumerate(embeddings):
                chunk_rows[i]["embedding"] = emb
            print(f"  Embedded {len(embeddings)} chunks")
        else:
            print("  WARNING: Embeddings skipped (API unavailable or mismatch)")

    # Upsert documents first
    print(f"  Upserting {len(doc_rows)} documents...")
    doc_result = supabase_upsert(
        "rag.documents",
        doc_rows,
        "id",
        supabase_url=supabase_url,
        service_key=service_key,
    )
    result["doc_upsert"] = doc_result

    # Upsert chunks (in batches of 100 to stay under API size limits)
    batch_size = 100
    chunk_results = []
    for i in range(0, len(chunk_rows), batch_size):
        batch = chunk_rows[i : i + batch_size]
        print(f"  Upserting chunks {i+1}-{i+len(batch)} of {len(chunk_rows)}...")
        cr = supabase_upsert(
            "rag.chunks",
            batch,
            "id",
            supabase_url=supabase_url,
            service_key=service_key,
        )
        chunk_results.append(cr)
    result["chunk_upserts"] = chunk_results

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Upsert corpus files into Supabase RAG tables"
    )
    parser.add_argument(
        "--corpus",
        type=str,
        default=None,
        help="Process only this corpus_id (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Discover and chunk files without upserting",
    )
    parser.add_argument(
        "--with-embeddings",
        action="store_true",
        help="Generate OpenAI embeddings (requires OPENAI_API_KEY)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Write results JSON to this path",
    )
    args = parser.parse_args()

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not args.dry_run and (not supabase_url or not service_key):
        print(
            "WARNING: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set. "
            "Running in dry-run mode.",
            file=sys.stderr,
        )
        args.dry_run = True

    registry = load_registry()
    corpora = registry.get("corpora", [])

    if args.corpus:
        corpora = [c for c in corpora if c["id"] == args.corpus]
        if not corpora:
            print(f"ERROR: corpus '{args.corpus}' not found in registry")
            return 1

    print(f"Processing {len(corpora)} corpora...")
    results = []

    for corpus in corpora:
        print(f"\n── {corpus['id']} ──")
        result = process_corpus(
            corpus,
            dry_run=args.dry_run,
            with_embeddings=args.with_embeddings,
            supabase_url=supabase_url,
            service_key=service_key,
        )
        results.append(result)

    # Summary
    total_files = sum(r["files_discovered"] for r in results)
    total_chunks = sum(r["chunks"] for r in results)
    print(f"\n{'='*60}")
    print(f"Total: {total_files} files → {total_chunks} chunks across {len(results)} corpora")

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "mode": "dry_run" if args.dry_run else "upsert",
                    "corpora_processed": len(results),
                    "total_files": total_files,
                    "total_chunks": total_chunks,
                    "results": results,
                },
                f,
                indent=2,
            )
        print(f"Results written to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
