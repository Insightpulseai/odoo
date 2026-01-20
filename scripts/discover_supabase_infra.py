#!/usr/bin/env python3
"""
Supabase Infrastructure Discovery
Queries Supabase Management API and database catalog to discover infrastructure
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime

try:
    from supabase import create_client, Client
except ImportError:
    print("ERROR: supabase-py not installed. Install with: pip install supabase")
    sys.exit(1)


def get_supabase_client() -> Client:
    """Create Supabase client from environment variables"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    project_ref = os.environ.get("SUPABASE_PROJECT_REF", "spdtwktxdalcfigzeqrz")

    if not url or not key:
        print("ERROR: Missing Supabase credentials")
        print("Required environment variables:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_SERVICE_ROLE_KEY")
        print("  - SUPABASE_PROJECT_REF (optional, defaults to spdtwktxdalcfigzeqrz)")
        sys.exit(1)

    return create_client(url, key), project_ref


def discover_database_schemas(client: Client, project_ref: str) -> tuple[List[Dict], List[Dict]]:
    """Discover database schemas via information_schema"""
    nodes = []
    edges = []

    # Create project node
    project_id = f"supabase:project:{project_ref}"
    nodes.append({
        "id": project_id,
        "source": "supabase",
        "kind": "project",
        "key": project_ref,
        "name": f"Supabase Project ({project_ref})",
        "props": {
            "project_ref": project_ref,
            "url": os.environ.get("SUPABASE_URL")
        }
    })

    # Query information_schema for schemas
    try:
        result = client.rpc("get_schemas_info").execute()

        if result.data:
            for schema_info in result.data:
                schema_name = schema_info.get("schema_name")

                # Skip internal schemas
                if schema_name in ["pg_catalog", "information_schema", "pg_toast"]:
                    continue

                schema_id = f"supabase:schema:{project_ref}:{schema_name}"
                nodes.append({
                    "id": schema_id,
                    "source": "supabase",
                    "kind": "schema",
                    "key": f"{project_ref}:{schema_name}",
                    "name": schema_name,
                    "props": {
                        "project_ref": project_ref,
                        "schema_name": schema_name,
                        "table_count": schema_info.get("table_count", 0)
                    }
                })

                # Create edge: project HAS_SCHEMA schema
                edges.append({
                    "id": f"{project_id}→{schema_id}",
                    "source": "supabase",
                    "from_id": project_id,
                    "to_id": schema_id,
                    "type": "HAS_SCHEMA",
                    "props": {}
                })
    except Exception as e:
        print(f"WARNING: Could not query schemas via RPC: {e}")
        print("Falling back to hardcoded known schemas...")

        # Fallback to known schemas
        known_schemas = ["public", "auth", "storage", "infra", "scout"]
        for schema_name in known_schemas:
            schema_id = f"supabase:schema:{project_ref}:{schema_name}"
            nodes.append({
                "id": schema_id,
                "source": "supabase",
                "kind": "schema",
                "key": f"{project_ref}:{schema_name}",
                "name": schema_name,
                "props": {
                    "project_ref": project_ref,
                    "schema_name": schema_name,
                    "discovered_via": "fallback"
                }
            })

            edges.append({
                "id": f"{project_id}→{schema_id}",
                "source": "supabase",
                "from_id": project_id,
                "to_id": schema_id,
                "type": "HAS_SCHEMA",
                "props": {}
            })

    return nodes, edges


def discover_tables(client: Client, project_ref: str) -> tuple[List[Dict], List[Dict]]:
    """Discover tables in key schemas"""
    nodes = []
    edges = []

    # Key schemas to discover
    target_schemas = ["public", "auth", "storage", "infra", "scout"]

    for schema_name in target_schemas:
        schema_id = f"supabase:schema:{project_ref}:{schema_name}"

        try:
            # Query tables in schema (simplified - assumes table listing endpoint)
            # Note: This is a placeholder - actual implementation depends on available RPC functions
            tables = []

            # For now, use hardcoded known tables for each schema
            if schema_name == "public":
                tables = ["profiles", "organizations", "memberships"]
            elif schema_name == "auth":
                tables = ["users", "identities", "sessions", "refresh_tokens"]
            elif schema_name == "storage":
                tables = ["buckets", "objects"]
            elif schema_name == "infra":
                tables = ["sources", "nodes", "edges", "snapshots"]
            elif schema_name == "scout":
                tables = ["transactions", "categories", "vendors", "receipts"]

            for table_name in tables:
                table_id = f"supabase:table:{project_ref}:{schema_name}.{table_name}"
                nodes.append({
                    "id": table_id,
                    "source": "supabase",
                    "kind": "table",
                    "key": f"{project_ref}:{schema_name}.{table_name}",
                    "name": f"{schema_name}.{table_name}",
                    "props": {
                        "project_ref": project_ref,
                        "schema_name": schema_name,
                        "table_name": table_name,
                        "discovered_via": "hardcoded"  # TODO: Replace with actual discovery
                    }
                })

                # Create edge: schema HAS_TABLE table
                edges.append({
                    "id": f"{schema_id}→{table_id}",
                    "source": "supabase",
                    "from_id": schema_id,
                    "to_id": table_id,
                    "type": "HAS_TABLE",
                    "props": {}
                })

        except Exception as e:
            print(f"WARNING: Could not discover tables in schema {schema_name}: {e}")
            continue

    return nodes, edges


def discover_storage_buckets(client: Client, project_ref: str) -> tuple[List[Dict], List[Dict]]:
    """Discover Supabase Storage buckets"""
    nodes = []
    edges = []

    storage_id = f"supabase:storage:{project_ref}"

    # Create storage service node
    nodes.append({
        "id": storage_id,
        "source": "supabase",
        "kind": "storage",
        "key": project_ref,
        "name": "Supabase Storage",
        "props": {
            "project_ref": project_ref
        }
    })

    # Edge: project HAS_STORAGE storage
    project_id = f"supabase:project:{project_ref}"
    edges.append({
        "id": f"{project_id}→{storage_id}",
        "source": "supabase",
        "from_id": project_id,
        "to_id": storage_id,
        "type": "HAS_STORAGE",
        "props": {}
    })

    try:
        # Query buckets
        result = client.storage.list_buckets()

        for bucket in result:
            bucket_id = bucket.get("id") or bucket.get("name")
            bucket_node_id = f"supabase:bucket:{project_ref}:{bucket_id}"

            nodes.append({
                "id": bucket_node_id,
                "source": "supabase",
                "kind": "bucket",
                "key": f"{project_ref}:{bucket_id}",
                "name": bucket.get("name", bucket_id),
                "props": {
                    "project_ref": project_ref,
                    "bucket_id": bucket_id,
                    "public": bucket.get("public", False),
                    "file_size_limit": bucket.get("file_size_limit"),
                    "allowed_mime_types": bucket.get("allowed_mime_types", [])
                }
            })

            # Edge: storage HAS_BUCKET bucket
            edges.append({
                "id": f"{storage_id}→{bucket_node_id}",
                "source": "supabase",
                "from_id": storage_id,
                "to_id": bucket_node_id,
                "type": "HAS_BUCKET",
                "props": {}
            })

    except Exception as e:
        print(f"WARNING: Could not query storage buckets: {e}")

    return nodes, edges


def main():
    """Main discovery routine"""
    print("=" * 60)
    print("Supabase Infrastructure Discovery")
    print("=" * 60)
    print()

    # Get Supabase client
    client, project_ref = get_supabase_client()
    print(f"Connected to Supabase project: {project_ref}")
    print()

    all_nodes = []
    all_edges = []

    # Discover database schemas
    print("Discovering database schemas...")
    schema_nodes, schema_edges = discover_database_schemas(client, project_ref)
    all_nodes.extend(schema_nodes)
    all_edges.extend(schema_edges)
    print(f"  Found {len(schema_nodes)} schemas")
    print()

    # Discover tables
    print("Discovering tables...")
    table_nodes, table_edges = discover_tables(client, project_ref)
    all_nodes.extend(table_nodes)
    all_edges.extend(table_edges)
    print(f"  Found {len(table_nodes)} tables")
    print()

    # Discover storage buckets
    print("Discovering storage buckets...")
    bucket_nodes, bucket_edges = discover_storage_buckets(client, project_ref)
    all_nodes.extend(bucket_nodes)
    all_edges.extend(bucket_edges)
    print(f"  Found {len(bucket_nodes)} storage buckets")
    print()

    # Write output files
    repo_root = Path(__file__).parent.parent
    output_dir = repo_root / "infra" / "infra_graph" / "sources"
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes_path = output_dir / "supabase_nodes.json"
    edges_path = output_dir / "supabase_edges.json"

    with open(nodes_path, 'w') as f:
        json.dump(all_nodes, f, indent=2)

    with open(edges_path, 'w') as f:
        json.dump(all_edges, f, indent=2)

    print("=" * 60)
    print("✅ Supabase discovery complete")
    print("=" * 60)
    print(f"Nodes discovered: {len(all_nodes)}")
    print(f"Edges discovered: {len(all_edges)}")
    print()
    print(f"Output files:")
    print(f"  {nodes_path}")
    print(f"  {edges_path}")
    print()
    print("Next step: Run scripts/build_infra_graph.py to merge into unified graph")
    print()


if __name__ == "__main__":
    main()
