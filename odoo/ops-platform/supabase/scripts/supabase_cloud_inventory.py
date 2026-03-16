#!/usr/bin/env python3
"""
supabase_cloud_inventory.py — Inventory cloud Supabase project assets.

Connects to spdtwktxdalcfigzeqrz via service_role key from Azure Key Vault.
Inventories: tables, schemas, extensions, RLS policies, functions, storage buckets, auth.users.
Outputs JSON inventory to stdout and evidence directory.

Usage:
    python3 supabase_cloud_inventory.py [--output-dir DIR] [--dry-run]
    python3 supabase_cloud_inventory.py --help
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone


CLOUD_PROJECT_REF = "spdtwktxdalcfigzeqrz"
CLOUD_API_URL = f"https://{CLOUD_PROJECT_REF}.supabase.co"
KV_NAME = os.environ.get("KV_NAME", "kv-ipai-dev")
DEFAULT_EVIDENCE_DIR = f"docs/evidence/{datetime.now().strftime('%Y%m%d-%H%M')}/supabase-migration"


def get_kv_secret(name: str) -> str:
    """Fetch secret from Azure Key Vault. Returns empty string on failure."""
    try:
        result = subprocess.run(
            [
                "az", "keyvault", "secret", "show",
                "--vault-name", KV_NAME,
                "--name", name,
                "--query", "value",
                "-o", "tsv",
            ],
            capture_output=True, text=True, check=True, timeout=30,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"[WARN] Failed to fetch secret '{name}' from KV '{KV_NAME}': {exc}", file=sys.stderr)
        return ""


def supabase_rest_query(service_role_key: str, query: str) -> list:
    """Execute SQL via Supabase REST /rest/v1/rpc or PostgREST. Falls back to pg_meta."""
    import requests

    url = f"{CLOUD_API_URL}/rest/v1/rpc/query"
    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json",
    }
    # Use the pg_meta SQL endpoint via management API
    # Fallback: direct PostgREST doesn't support arbitrary SQL, so use pg connection
    return []


def inventory_via_psql(db_url: str) -> dict:
    """Run inventory queries via psql against cloud DB."""
    inventory = {}

    queries = {
        "schemas": """
            SELECT schema_name FROM information_schema.schemata
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schema_name;
        """,
        "tables": """
            SELECT schemaname, tablename,
                   pg_stat_get_live_tuples(c.oid) AS row_count
            FROM pg_tables t
            JOIN pg_class c ON c.relname = t.tablename
            JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.schemaname
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schemaname, tablename;
        """,
        "extensions": """
            SELECT extname, extversion FROM pg_extension ORDER BY extname;
        """,
        "rls_policies": """
            SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
            FROM pg_policies
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schemaname, tablename, policyname;
        """,
        "functions": """
            SELECT n.nspname AS schema, p.proname AS name,
                   pg_get_function_arguments(p.oid) AS arguments,
                   pg_get_function_result(p.oid) AS return_type
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            WHERE n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY n.nspname, p.proname;
        """,
        "storage_buckets": """
            SELECT id, name, public, created_at FROM storage.buckets ORDER BY name;
        """,
        "auth_users_count": """
            SELECT count(*) AS user_count FROM auth.users;
        """,
    }

    for key, sql in queries.items():
        try:
            result = subprocess.run(
                ["psql", db_url, "-t", "-A", "-F", "\t", "-c", sql],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode != 0:
                inventory[key] = {"error": result.stderr.strip()}
                continue

            rows = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    rows.append(line.split("\t"))
            inventory[key] = rows
        except Exception as exc:
            inventory[key] = {"error": str(exc)}

    return inventory


def inventory_via_rest(service_role_key: str) -> dict:
    """Inventory via Supabase REST API (no psql required)."""
    import requests

    inventory = {}
    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
    }

    # Storage buckets
    try:
        resp = requests.get(f"{CLOUD_API_URL}/storage/v1/bucket", headers=headers, timeout=15)
        if resp.ok:
            inventory["storage_buckets"] = resp.json()
        else:
            inventory["storage_buckets"] = {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as exc:
        inventory["storage_buckets"] = {"error": str(exc)}

    # Auth users count (admin API)
    try:
        resp = requests.get(
            f"{CLOUD_API_URL}/auth/v1/admin/users?page=1&per_page=1",
            headers=headers, timeout=15,
        )
        if resp.ok:
            # Total from header or response
            total = resp.headers.get("x-total-count", "unknown")
            inventory["auth_users_count"] = total
        else:
            inventory["auth_users_count"] = {"error": f"HTTP {resp.status_code}"}
    except Exception as exc:
        inventory["auth_users_count"] = {"error": str(exc)}

    return inventory


def build_inventory(db_url: str, service_role_key: str) -> dict:
    """Build full inventory using psql (primary) and REST (supplementary)."""
    stamp = datetime.now(timezone.utc).isoformat()

    inventory = {
        "project_ref": CLOUD_PROJECT_REF,
        "api_url": CLOUD_API_URL,
        "timestamp": stamp,
        "method": "psql",
        "data": {},
    }

    if db_url:
        inventory["data"] = inventory_via_psql(db_url)
        inventory["method"] = "psql"
    elif service_role_key:
        inventory["data"] = inventory_via_rest(service_role_key)
        inventory["method"] = "rest_api"
    else:
        inventory["error"] = "No database URL or service_role key available"

    # Enrich with REST data if we have the key
    if service_role_key:
        rest_data = inventory_via_rest(service_role_key)
        for k, v in rest_data.items():
            if k not in inventory["data"] or "error" in str(inventory["data"].get(k, {})):
                inventory["data"][k] = v

    # Summary
    data = inventory["data"]
    inventory["summary"] = {
        "schema_count": len(data.get("schemas", [])) if isinstance(data.get("schemas"), list) else "error",
        "table_count": len(data.get("tables", [])) if isinstance(data.get("tables"), list) else "error",
        "extension_count": len(data.get("extensions", [])) if isinstance(data.get("extensions"), list) else "error",
        "rls_policy_count": len(data.get("rls_policies", [])) if isinstance(data.get("rls_policies"), list) else "error",
        "function_count": len(data.get("functions", [])) if isinstance(data.get("functions"), list) else "error",
        "storage_bucket_count": len(data.get("storage_buckets", [])) if isinstance(data.get("storage_buckets"), list) else "error",
        "auth_users_count": data.get("auth_users_count", "unknown"),
    }

    return inventory


def main():
    parser = argparse.ArgumentParser(
        description="Inventory cloud Supabase project assets.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--output-dir",
        default=os.environ.get("EVIDENCE_DIR", DEFAULT_EVIDENCE_DIR),
        help="Directory for evidence output (default: evidence dir with timestamp)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be inventoried without connecting",
    )
    args = parser.parse_args()

    if args.dry_run:
        print("[DRY RUN] Would inventory cloud Supabase project:")
        print(f"  Project ref: {CLOUD_PROJECT_REF}")
        print(f"  API URL:     {CLOUD_API_URL}")
        print(f"  Key Vault:   {KV_NAME}")
        print(f"  Output dir:  {args.output_dir}")
        print("[DRY RUN] Secrets needed from KV:")
        print("  - supabase-db-url (PostgreSQL connection string)")
        print("  - supabase-service-role-key")
        print("[DRY RUN] Queries: schemas, tables+row_counts, extensions, RLS policies,")
        print("          functions, storage buckets, auth.users count")
        sys.exit(0)

    # Fetch secrets
    print(f"[INFO] Fetching secrets from Key Vault '{KV_NAME}'...", file=sys.stderr)
    db_url = get_kv_secret("supabase-db-url")
    service_role_key = get_kv_secret("supabase-service-role-key")

    if not db_url and not service_role_key:
        print("[ERROR] Neither supabase-db-url nor supabase-service-role-key found in KV.", file=sys.stderr)
        print("[ERROR] Set them in KV or provide via env: SUPABASE_DB_URL, SUPABASE_SERVICE_ROLE_KEY", file=sys.stderr)
        # Try env fallback
        db_url = os.environ.get("SUPABASE_DB_URL", "")
        service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        if not db_url and not service_role_key:
            sys.exit(1)

    # Build inventory
    print(f"[INFO] Building inventory for {CLOUD_PROJECT_REF}...", file=sys.stderr)
    inventory = build_inventory(db_url, service_role_key)

    # Output to stdout
    output = json.dumps(inventory, indent=2, default=str)
    print(output)

    # Save to evidence dir
    os.makedirs(args.output_dir, exist_ok=True)
    evidence_path = os.path.join(args.output_dir, "cloud_inventory.json")
    with open(evidence_path, "w") as f:
        f.write(output)
    print(f"[INFO] Evidence saved to {evidence_path}", file=sys.stderr)

    # Summary to stderr
    summary = inventory.get("summary", {})
    print(f"[INFO] Summary:", file=sys.stderr)
    for k, v in summary.items():
        print(f"  {k}: {v}", file=sys.stderr)


if __name__ == "__main__":
    main()
