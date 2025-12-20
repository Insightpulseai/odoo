#!/usr/bin/env python3
"""
Mirror Gold Tables to Supabase
==============================

Syncs Delta Lake gold tables to Supabase for fast API queries.
Runs incrementally based on lookback window.

Usage:
    python scripts/lakehouse/mirror_gold_to_supabase.py

Environment variables:
    TRINO_HOST          - Trino host (default: localhost)
    TRINO_PORT          - Trino port (default: 8082)
    SUPABASE_URL        - Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY - Service role key for writes
"""

from __future__ import annotations
import os
import sys
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    import requests
except ImportError:
    print("ERROR: requests required: pip install requests")
    sys.exit(1)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.lakehouse.config import load_pipeline_config
except ImportError:
    load_pipeline_config = None  # type: ignore


class TrinoClient:
    """Simple Trino HTTP client."""

    def __init__(self, host: str = "localhost", port: int = 8082, user: str = "lakehouse"):
        self.base_url = f"http://{host}:{port}/v1/statement"
        self.user = user

    def query(self, sql: str, timeout: int = 120) -> list[dict]:
        """Execute SQL and return results as list of dicts."""
        response = requests.post(
            self.base_url,
            headers={"X-Trino-User": self.user},
            data=sql.encode("utf-8"),
            timeout=timeout,
        )
        response.raise_for_status()

        data = response.json()
        columns = [c["name"] for c in data.get("columns", [])]
        rows = [dict(zip(columns, row)) for row in data.get("data", [])]

        # Follow pagination
        next_uri = data.get("nextUri")
        while next_uri:
            resp = requests.get(next_uri, timeout=timeout)
            resp.raise_for_status()
            payload = resp.json()
            if payload.get("data") and columns:
                rows.extend(dict(zip(columns, row)) for row in payload["data"])
            next_uri = payload.get("nextUri")

        return rows


class SupabaseClient:
    """Simple Supabase REST client."""

    def __init__(self, url: str, service_role_key: str):
        self.url = url.rstrip("/")
        self.headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        }

    def upsert(self, table: str, rows: list[dict], on_conflict: str) -> int:
        """Upsert rows into table."""
        if not rows:
            return 0

        # Convert arrays/objects for JSON
        for row in rows:
            for key, val in row.items():
                if isinstance(val, (list, dict)):
                    row[key] = json.dumps(val)

        response = requests.post(
            f"{self.url}/rest/v1/{table}",
            headers=self.headers,
            params={"on_conflict": on_conflict},
            data=json.dumps(rows),
            timeout=60,
        )
        response.raise_for_status()
        return len(rows)


def mirror_chunks(trino: TrinoClient, supabase: SupabaseClient,
                  lookback_days: int = 7, batch_size: int = 1000) -> int:
    """Mirror gold.chunks to rag.chunks."""
    print(f"Mirroring gold.chunks (lookback={lookback_days} days)...")

    rows = trino.query(f"""
        SELECT
            tenant_id,
            chunk_id as id,
            document_id,
            document_version_id,
            ord,
            heading,
            content,
            tokens,
            created_at
        FROM delta.gold.chunks
        WHERE chunk_date >= current_date - INTERVAL '{lookback_days}' DAY
        ORDER BY created_at DESC
        LIMIT {batch_size}
    """)

    if rows:
        # Note: Supabase table is rag.chunks but REST uses just "chunks" with schema prefix
        # Adjust based on your Supabase schema setup
        count = supabase.upsert("chunks", rows, on_conflict="id")
        print(f"  Upserted {count} chunks")
        return count

    print("  No new chunks to mirror")
    return 0


def mirror_embeddings(trino: TrinoClient, supabase: SupabaseClient,
                      lookback_days: int = 7, batch_size: int = 1000) -> int:
    """Mirror gold.embeddings to rag.embeddings."""
    print(f"Mirroring gold.embeddings (lookback={lookback_days} days)...")

    rows = trino.query(f"""
        SELECT
            tenant_id,
            embedding_id as id,
            chunk_id,
            model,
            dims,
            v as embedding,
            created_at
        FROM delta.gold.embeddings
        WHERE embed_date >= current_date - INTERVAL '{lookback_days}' DAY
        ORDER BY created_at DESC
        LIMIT {batch_size}
    """)

    if rows:
        count = supabase.upsert("embeddings", rows, on_conflict="id")
        print(f"  Upserted {count} embeddings")
        return count

    print("  No new embeddings to mirror")
    return 0


def main() -> int:
    print("=" * 50)
    print("Lakehouse Mirror: Gold → Supabase")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print("=" * 50)

    # Load config
    lookback_days = 7
    batch_size = 1000

    if load_pipeline_config:
        try:
            config = load_pipeline_config()
            if not config.mirror_enabled:
                print("Mirroring disabled in config")
                return 0
            lookback_days = config.mirror_lookback_days
            batch_size = config.mirror_batch_size
        except Exception as e:
            print(f"WARN: Could not load config: {e}")

    # Get connection params from env
    trino_host = os.getenv("TRINO_HOST", "localhost")
    trino_port = int(os.getenv("TRINO_PORT", "8082"))
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
        return 1

    # Initialize clients
    trino = TrinoClient(host=trino_host, port=trino_port)
    supabase = SupabaseClient(url=supabase_url, service_role_key=supabase_key)

    # Mirror tables
    total = 0
    try:
        total += mirror_chunks(trino, supabase, lookback_days, batch_size)
        total += mirror_embeddings(trino, supabase, lookback_days, batch_size)
    except Exception as e:
        print(f"ERROR: Mirror failed: {e}")
        return 1

    print("=" * 50)
    print(f"Total rows mirrored: {total}")
    print("Done")

    return 0


if __name__ == "__main__":
    sys.exit(main())
