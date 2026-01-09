#!/usr/bin/env python3
"""
Knowledge Graph Ingestion Pipeline
Populates Supabase kg schema from graph_seed.json and external sources
"""

import json
import os
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)


def get_db_connection():
    """Get PostgreSQL connection from environment"""
    # Try Supabase connection string first
    postgres_url = os.environ.get("POSTGRES_URL")
    if postgres_url:
        return psycopg2.connect(postgres_url)

    # Fallback to individual parameters
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "6543")),
        database=os.environ.get("POSTGRES_DB", "postgres"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD"),
    )


def compute_content_hash(content: Any) -> str:
    """Compute SHA256 hash of content for change detection"""
    content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(content_str.encode("utf-8")).hexdigest()


def load_graph_seed(seed_path: Path) -> Dict[str, Any]:
    """Load knowledge graph seed from JSON file"""
    if not seed_path.exists():
        raise FileNotFoundError(f"Graph seed not found: {seed_path}")

    with open(seed_path, "r", encoding="utf-8") as f:
        return json.load(f)


def upsert_nodes(conn, nodes: List[Dict[str, Any]]) -> int:
    """Upsert nodes into kg.nodes table"""
    if not nodes:
        return 0

    with conn.cursor() as cur:
        # Prepare data for execute_values
        values = [
            (
                node["id"],
                node["kind"],
                node["name"],
                json.dumps(node.get("ref", {})),
                json.dumps(node.get("props", {})),
            )
            for node in nodes
        ]

        # Use ON CONFLICT to update existing nodes
        execute_values(
            cur,
            """
            INSERT INTO kg.nodes (id, kind, name, ref, props, updated_at)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                kind = EXCLUDED.kind,
                name = EXCLUDED.name,
                ref = EXCLUDED.ref,
                props = EXCLUDED.props,
                updated_at = NOW()
            """,
            values,
            template="(%s, %s, %s, %s::jsonb, %s::jsonb, NOW())",
        )

        conn.commit()
        return len(nodes)


def upsert_edges(conn, edges: List[Dict[str, Any]]) -> int:
    """Upsert edges into kg.edges table"""
    if not edges:
        return 0

    with conn.cursor() as cur:
        # Prepare data for execute_values
        values = [
            (
                edge["src"],
                edge["rel"],
                edge["dst"],
                json.dumps(edge.get("props", {})),
            )
            for edge in edges
        ]

        # Use ON CONFLICT to update existing edges
        execute_values(
            cur,
            """
            INSERT INTO kg.edges (src, rel, dst, props)
            VALUES %s
            ON CONFLICT (src, rel, dst) DO UPDATE SET
                props = EXCLUDED.props
            """,
            values,
            template="(%s, %s, %s, %s::jsonb)",
        )

        conn.commit()
        return len(edges)


def record_source(conn, source_kind: str, source_id: str, payload: Dict[str, Any]) -> bool:
    """Record ingestion source with content hash for change detection"""
    content_hash = compute_content_hash(payload)

    with conn.cursor() as cur:
        # Check if source already exists with same content hash
        cur.execute(
            """
            SELECT content_hash FROM kg.sources
            WHERE source_kind = %s AND source_id = %s
            """,
            (source_kind, source_id),
        )
        result = cur.fetchone()

        if result and result[0] == content_hash:
            # No changes detected
            return False

        # Insert or update source record
        cur.execute(
            """
            INSERT INTO kg.sources (source_kind, source_id, content_hash, payload)
            VALUES (%s, %s, %s, %s::jsonb)
            ON CONFLICT (source_kind, source_id) DO UPDATE SET
                content_hash = EXCLUDED.content_hash,
                payload = EXCLUDED.payload,
                ingested_at = NOW()
            """,
            (source_kind, source_id, content_hash, json.dumps(payload)),
        )

        conn.commit()
        return True


def ingest_local_repo(conn, seed_path: Path) -> Dict[str, int]:
    """Ingest local repository scan from graph_seed.json"""
    print("Loading graph seed from local repository scan...")
    seed_data = load_graph_seed(seed_path)

    # Record source
    source_id = seed_data.get("generated_at", datetime.now().isoformat())
    has_changes = record_source(conn, "local_repo_scan", source_id, seed_data)

    if not has_changes:
        print("  No changes detected in local repository scan")
        return {"nodes": 0, "edges": 0}

    # Upsert nodes and edges
    nodes_count = upsert_nodes(conn, seed_data.get("nodes", []))
    edges_count = upsert_edges(conn, seed_data.get("edges", []))

    print(f"  Ingested {nodes_count} nodes and {edges_count} edges")

    return {"nodes": nodes_count, "edges": edges_count}


def ingest_github_metadata(conn) -> Dict[str, int]:
    """
    Ingest GitHub metadata via GraphQL API (repos, issues, PRs, workflows)

    NOTE: This is a placeholder for future implementation.
    Requires GitHub GraphQL API calls with GITHUB_TOKEN.
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("  Skipping GitHub metadata ingestion (no GITHUB_TOKEN)")
        return {"nodes": 0, "edges": 0}

    # TODO: Implement GitHub GraphQL API ingestion
    # - Query repositories
    # - Query issues and PRs
    # - Query workflows and runs
    # - Create nodes with stable IDs
    # - Create edges (RESOLVES, IMPLEMENTS, etc.)

    print("  GitHub metadata ingestion not yet implemented")
    return {"nodes": 0, "edges": 0}


def cleanup_orphaned_edges(conn) -> int:
    """Remove edges referencing non-existent nodes"""
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM kg.edges
            WHERE src NOT IN (SELECT id FROM kg.nodes)
               OR dst NOT IN (SELECT id FROM kg.nodes)
            """
        )
        deleted = cur.rowcount
        conn.commit()

        if deleted > 0:
            print(f"  Cleaned up {deleted} orphaned edges")

        return deleted


def generate_statistics(conn) -> Dict[str, Any]:
    """Generate ingestion statistics"""
    with conn.cursor() as cur:
        # Count nodes by kind
        cur.execute(
            """
            SELECT kind, COUNT(*) as count
            FROM kg.nodes
            GROUP BY kind
            ORDER BY count DESC
            """
        )
        nodes_by_kind = {row[0]: row[1] for row in cur.fetchall()}

        # Count edges by relationship
        cur.execute(
            """
            SELECT rel, COUNT(*) as count
            FROM kg.edges
            GROUP BY rel
            ORDER BY count DESC
            """
        )
        edges_by_rel = {row[0]: row[1] for row in cur.fetchall()}

        # Total counts
        cur.execute("SELECT COUNT(*) FROM kg.nodes")
        total_nodes = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM kg.edges")
        total_edges = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM kg.sources")
        total_sources = cur.fetchone()[0]

        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "total_sources": total_sources,
            "nodes_by_kind": nodes_by_kind,
            "edges_by_rel": edges_by_rel,
        }


def main():
    """Main ingestion pipeline"""
    repo_root = Path(__file__).parent.parent
    seed_path = repo_root / "docs" / "knowledge" / "graph_seed.json"

    print("=" * 80)
    print("Knowledge Graph Ingestion Pipeline")
    print("=" * 80)
    print()

    # Connect to database
    try:
        conn = get_db_connection()
        print("✓ Connected to PostgreSQL")
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {e}")
        sys.exit(1)

    try:
        # Ingest local repository scan
        print("\n1. Ingesting local repository scan...")
        local_stats = ingest_local_repo(conn, seed_path)

        # Ingest GitHub metadata (future)
        print("\n2. Ingesting GitHub metadata...")
        github_stats = ingest_github_metadata(conn)

        # Cleanup orphaned edges
        print("\n3. Cleaning up orphaned edges...")
        cleanup_orphaned_edges(conn)

        # Generate statistics
        print("\n4. Generating statistics...")
        stats = generate_statistics(conn)

        # Print summary
        print()
        print("=" * 80)
        print("Ingestion Summary")
        print("=" * 80)
        print(f"Total nodes: {stats['total_nodes']}")
        print(f"Total edges: {stats['total_edges']}")
        print(f"Total sources: {stats['total_sources']}")
        print()
        print("Nodes by kind:")
        for kind, count in stats["nodes_by_kind"].items():
            print(f"  {kind:20} {count:4}")
        print()
        print("Edges by relationship:")
        for rel, count in stats["edges_by_rel"].items():
            print(f"  {rel:20} {count:4}")
        print()
        print("✓ Ingestion complete")

    except Exception as e:
        print(f"\nERROR: Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
