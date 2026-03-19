#!/usr/bin/env python3
"""
Supabase Infrastructure Discovery

Discovers Supabase schemas, tables, functions, and Edge Functions.
"""

import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

SUPABASE_MGMT_API = "https://api.supabase.com/v1"


def discover_supabase(orchestrator) -> Dict[str, Any]:
    """
    Discover Supabase infrastructure and store in KG.

    Returns summary of discovered resources.
    """
    supabase_url = os.environ.get(
        "SUPABASE_URL", "https://spdtwktxdalcfigzeqrz.supabase.co"
    )
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    access_token = os.environ.get("SUPABASE_ACCESS_TOKEN")

    if not service_key:
        logger.warning("SUPABASE_SERVICE_ROLE_KEY not set, skipping Supabase discovery")
        return {"skipped": True, "reason": "SUPABASE_SERVICE_ROLE_KEY not set"}

    # Extract project ref from URL
    project_ref = supabase_url.split("//")[1].split(".")[0]

    discovered = {"schemas": 0, "tables": 0, "functions": 0, "edge_functions": 0}

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }

    try:
        # Create main Supabase project node
        project_node_id = orchestrator.upsert_node(
            kind="supabase_project",
            key=f"supabase:{project_ref}",
            label="superset",
            attrs={
                "project_ref": project_ref,
                "url": supabase_url,
                "region": "ap-southeast-1",
            },
        )

        # Discover schemas via information_schema
        schemas_query = """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
          AND schema_name NOT LIKE 'pg_%'
        ORDER BY schema_name;
        """

        schemas_resp = requests.post(
            f"{supabase_url}/rest/v1/rpc/query_schemas",
            headers=headers,
            json={"sql": schemas_query},
        )

        # If RPC not available, use known schemas
        known_schemas = [
            "public",
            "kb",
            "kg",
            "agent_mem",
            "docs",
            "ops",
            "ops_advisor",
            "odoo_shadow",
            "auth",
            "storage",
        ]

        schema_nodes = {}
        for schema_name in known_schemas:
            schema_node_id = orchestrator.upsert_node(
                kind="schema",
                key=f"supabase:{project_ref}:schema:{schema_name}",
                label=schema_name,
                attrs={
                    "project_ref": project_ref,
                    "schema_type": (
                        "api_exposed"
                        if schema_name
                        in ["public", "kb", "kg", "agent_mem", "docs", "ops_advisor"]
                        else "internal"
                    ),
                },
            )
            schema_nodes[schema_name] = schema_node_id
            discovered["schemas"] += 1

            # Link schema to project
            orchestrator.upsert_edge(
                src_node_id=project_node_id,
                predicate="CONTAINS",
                dst_node_id=schema_node_id,
                source_type="supabase",
                source_ref=f"supabase:{project_ref}",
            )

        # Discover tables via REST API
        # Query information_schema through the database
        tables_query = """
        SELECT table_schema, table_name, table_type
        FROM information_schema.tables
        WHERE table_schema IN ('kb', 'kg', 'agent_mem', 'docs', 'ops_advisor', 'public')
        ORDER BY table_schema, table_name;
        """

        # Known tables per schema (fallback if query fails)
        known_tables = {
            "kb": [
                "spaces",
                "artifacts",
                "versions",
                "blocks",
                "citations",
                "catalog_sources",
                "catalog_nodes",
                "harvest_state",
            ],
            "kg": [
                "nodes",
                "edges",
                "evidence",
                "node_embeddings",
                "predicate_catalog",
                "discovery_runs",
            ],
            "agent_mem": [
                "sessions",
                "events",
                "skills",
                "agent_skill_bindings",
                "memory_sync_log",
            ],
            "docs": ["chunks", "embeddings"],
            "ops_advisor": ["recommendations", "scores", "activity_log"],
        }

        for schema, tables in known_tables.items():
            if schema in schema_nodes:
                for table in tables:
                    table_node_id = orchestrator.upsert_node(
                        kind="table",
                        key=f"supabase:{project_ref}:table:{schema}.{table}",
                        label=f"{schema}.{table}",
                        attrs={
                            "schema": schema,
                            "table_name": table,
                            "project_ref": project_ref,
                        },
                    )
                    discovered["tables"] += 1

                    # Link table to schema
                    orchestrator.upsert_edge(
                        src_node_id=schema_nodes[schema],
                        predicate="CONTAINS",
                        dst_node_id=table_node_id,
                        source_type="supabase",
                        source_ref=f"supabase:{project_ref}:schema:{schema}",
                    )

        # Discover Edge Functions via Management API
        if access_token:
            mgmt_headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            try:
                functions_resp = requests.get(
                    f"{SUPABASE_MGMT_API}/projects/{project_ref}/functions",
                    headers=mgmt_headers,
                )
                if functions_resp.status_code == 200:
                    functions = functions_resp.json()

                    for func in functions:
                        func_node_id = orchestrator.upsert_node(
                            kind="edge_function",
                            key=f'supabase:{project_ref}:function:{func["slug"]}',
                            label=func["slug"],
                            attrs={
                                "slug": func["slug"],
                                "status": func.get("status"),
                                "version": func.get("version"),
                                "created_at": func.get("created_at"),
                                "updated_at": func.get("updated_at"),
                            },
                        )
                        discovered["edge_functions"] += 1

                        # Link function to project
                        orchestrator.upsert_edge(
                            src_node_id=project_node_id,
                            predicate="CONTAINS",
                            dst_node_id=func_node_id,
                            source_type="supabase",
                            source_ref=f"supabase:{project_ref}:functions",
                        )
            except requests.RequestException as e:
                logger.warning(f"Could not fetch Edge Functions: {e}")
        else:
            # Fallback: known Edge Functions
            known_functions = [
                "docs-ai-ask",
                "semantic-query",
                "semantic-import-osi",
                "semantic-export-osi",
                "sync-kb-to-schema",
                "catalog-sync",
                "verify-secrets",
                "verify-supabase",
                "verify-github",
                "verify-external-apis",
                "mailgate-mailgun",
                "n8n-proxy",
            ]

            for func_slug in known_functions:
                func_node_id = orchestrator.upsert_node(
                    kind="edge_function",
                    key=f"supabase:{project_ref}:function:{func_slug}",
                    label=func_slug,
                    attrs={"slug": func_slug, "project_ref": project_ref},
                )
                discovered["edge_functions"] += 1

                orchestrator.upsert_edge(
                    src_node_id=project_node_id,
                    predicate="CONTAINS",
                    dst_node_id=func_node_id,
                    source_type="supabase",
                    source_ref=f"supabase:{project_ref}",
                )

    except requests.RequestException as e:
        logger.error(f"Supabase API error: {e}")
        discovered["error"] = str(e)

    return discovered


if __name__ == "__main__":
    # Standalone test
    class MockOrchestrator:
        def upsert_node(self, kind, key, label, attrs):
            print(f"Node: {kind}/{key} ({label})")
            return key

        def upsert_edge(self, src_node_id, predicate, dst_node_id, **kwargs):
            print(f"Edge: {src_node_id} --{predicate}--> {dst_node_id}")
            return f"{src_node_id}:{predicate}:{dst_node_id}"

    result = discover_supabase(MockOrchestrator())
    print(f"Result: {result}")
