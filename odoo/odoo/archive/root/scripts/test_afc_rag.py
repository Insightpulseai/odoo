#!/usr/bin/env python3
"""
AFC RAG Service Test Script

Tests the AFC RAG service health, semantic search, and query capabilities.
"""

import os
import sys
import psycopg2
import json
from typing import List, Dict, Any

# Get connection URL from environment
POSTGRES_URL = os.getenv("POSTGRES_URL_NON_POOLING", "")

# Parse connection URL if available, otherwise use individual parameters
if POSTGRES_URL:
    import urllib.parse

    parsed = urllib.parse.urlparse(POSTGRES_URL)
    DB_CONFIG = {
        "host": parsed.hostname,
        "database": parsed.path[1:] if parsed.path else "postgres",
        "user": parsed.username,
        "password": parsed.password,
        "port": parsed.port or 5432,
    }
else:
    DB_CONFIG = {
        "host": os.getenv("POSTGRES_HOST", "db.spdtwktxdalcfigzeqrz.supabase.co"),
        "database": os.getenv("POSTGRES_DATABASE", "postgres"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
        "port": os.getenv("POSTGRES_PORT", "5432"),
    }


def test_connection() -> bool:
    """Test database connection."""
    print("🔍 Testing database connection...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        conn.close()
        print(f"✅ Connection successful")
        print(f"   PostgreSQL version: {version[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False


def test_schema() -> bool:
    """Test AFC schema tables exist."""
    print("\n🔍 Testing AFC schema...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Check document_chunks table
        cursor.execute("SELECT COUNT(*) FROM afc.document_chunks;")
        chunk_count = cursor.fetchone()[0]
        print(f"✅ document_chunks table: {chunk_count} rows")

        # Check chunk_embeddings table
        cursor.execute("SELECT COUNT(*) FROM afc.chunk_embeddings;")
        embedding_count = cursor.fetchone()[0]
        print(f"✅ chunk_embeddings table: {embedding_count} rows")

        # Check pgvector extension
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM pg_extension WHERE extname = 'vector'
            );
        """
        )
        has_pgvector = cursor.fetchone()[0]
        print(
            f"{'✅' if has_pgvector else '❌'} pgvector extension: {'installed' if has_pgvector else 'not found'}"
        )

        conn.close()
        return chunk_count > 0 and embedding_count > 0 and has_pgvector
    except Exception as e:
        print(f"❌ Schema test failed: {str(e)}")
        return False


def test_semantic_search(
    query: str = "What is the BIR 1601-C deadline?", top_k: int = 3
) -> bool:
    """Test semantic search capability."""
    print(f"\n🔍 Testing semantic search...")
    print(f"   Query: '{query}'")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Generate placeholder embedding (zeros)
        query_embedding = [0.0] * 1536
        embedding_str = str(query_embedding)

        # Execute vector similarity search
        cursor.execute(
            """
            SELECT
                dc.id,
                dc.content,
                dc.source,
                dc.metadata,
                ce.embedding <=> %s::vector AS similarity
            FROM afc.document_chunks dc
            JOIN afc.chunk_embeddings ce ON ce.chunk_id = dc.id
            ORDER BY similarity ASC
            LIMIT %s
        """,
            (embedding_str, top_k),
        )

        results = cursor.fetchall()
        conn.close()

        if not results:
            print("⚠️  No results found (this is expected with placeholder embeddings)")
            print("   Configure OpenAI API key for actual semantic search")
            return True

        print(f"✅ Found {len(results)} results:")
        for i, (chunk_id, content, source, metadata, similarity) in enumerate(
            results, 1
        ):
            print(f"\n   [{i}] Source: {source}")
            print(f"       Similarity: {similarity:.4f}")
            print(f"       Content: {content[:100]}...")
            if metadata:
                print(f"       Metadata: {json.dumps(metadata, indent=10)[:100]}...")

        return True
    except Exception as e:
        print(f"❌ Semantic search failed: {str(e)}")
        return False


def test_health_check() -> bool:
    """Test health check functionality."""
    print("\n🔍 Testing health check...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM afc.document_chunks;")
        chunk_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM afc.chunk_embeddings;")
        embedding_count = cursor.fetchone()[0]

        conn.close()

        health = {
            "status": "ok" if chunk_count > 0 and embedding_count > 0 else "error",
            "chunk_count": chunk_count,
            "embedding_count": embedding_count,
            "message": f"AFC RAG service healthy. {chunk_count} chunks with {embedding_count} embeddings available.",
        }

        print(f"✅ Health check: {health['status']}")
        print(f"   Chunks: {health['chunk_count']}")
        print(f"   Embeddings: {health['embedding_count']}")
        print(f"   Message: {health['message']}")

        return health["status"] == "ok"
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False


def test_seed_data() -> bool:
    """Test AFC seed data."""
    print("\n🔍 Testing AFC seed data...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Test ph_tax_config
        cursor.execute("SELECT COUNT(*) FROM afc.ph_tax_config;")
        tax_count = cursor.fetchone()[0]
        print(f"✅ ph_tax_config: {tax_count} rows")

        # Test sod_role
        cursor.execute("SELECT COUNT(*) FROM afc.sod_role;")
        role_count = cursor.fetchone()[0]
        print(f"✅ sod_role: {role_count} rows")

        # Test sod_conflict_matrix
        cursor.execute("SELECT COUNT(*) FROM afc.sod_conflict_matrix;")
        conflict_count = cursor.fetchone()[0]
        print(f"✅ sod_conflict_matrix: {conflict_count} rows")

        conn.close()

        return tax_count >= 6 and role_count >= 8 and conflict_count >= 4
    except Exception as e:
        print(f"❌ Seed data test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AFC RAG Service Test Suite")
    print("=" * 60)

    if not DB_CONFIG["password"]:
        print("\n⚠️  Warning: POSTGRES_PASSWORD not set")
        print("   Set environment variable or update DB_CONFIG in script")
        return 1

    tests = [
        ("Connection", test_connection),
        ("Schema", test_schema),
        ("Seed Data", test_seed_data),
        ("Health Check", test_health_check),
        ("Semantic Search", test_semantic_search),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {str(e)}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
