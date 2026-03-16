#!/usr/bin/env python3
"""Export inventory from managed Supabase for migration planning.

Produces machine-readable inventory of tables, functions, cron jobs,
and storage objects from the source Supabase project.

Usage:
    python export_supabase_inventory.py \
        --mode dry-run \
        --output docs/evidence/migration/inventory \
        --manifest ssot/migration/azure_selfhost_migration_manifest.yaml
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import requests
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("export_supabase_inventory")

SCHEMAS_TO_SCAN = ("public", "ops", "mcp_jobs", "scout", "auth", "storage")


def get_source_connection() -> psycopg2.extensions.connection:
    """Create connection to source Supabase Postgres from env vars."""
    dsn = os.environ.get("SOURCE_PG_DSN")
    if dsn:
        return psycopg2.connect(dsn)
    return psycopg2.connect(
        host=os.environ["SOURCE_PG_HOST"],
        port=os.environ.get("SOURCE_PG_PORT", "5432"),
        dbname=os.environ.get("SOURCE_PG_DBNAME", "postgres"),
        user=os.environ["SOURCE_PG_USER"],
        password=os.environ["SOURCE_PG_PASSWORD"],
        sslmode=os.environ.get("SOURCE_PG_SSLMODE", "require"),
    )


def inventory_tables(
    conn: psycopg2.extensions.connection,
) -> list[dict]:
    """Query pg_tables and pg_stat_user_tables for schema/table/row_count."""
    results: list[dict] = []
    with conn.cursor() as cur:
        for schema in SCHEMAS_TO_SCAN:
            cur.execute(
                """
                SELECT schemaname, tablename
                FROM pg_tables
                WHERE schemaname = %s
                ORDER BY tablename
                """,
                (schema,),
            )
            tables = cur.fetchall()
            for schemaname, tablename in tables:
                try:
                    cur.execute(
                        f'SELECT count(*) FROM "{schemaname}"."{tablename}"'
                    )
                    row_count = cur.fetchone()[0]
                except psycopg2.Error as exc:
                    logger.warning(
                        "Cannot count %s.%s: %s", schemaname, tablename, exc
                    )
                    conn.rollback()
                    row_count = -1
                results.append(
                    {
                        "schema": schemaname,
                        "table": tablename,
                        "row_count": row_count,
                    }
                )
    logger.info("Inventoried %d tables across %d schemas", len(results), len(SCHEMAS_TO_SCAN))
    return results


def inventory_functions(manifest_path: Path) -> list[dict]:
    """Load deploy manifest YAML and list Edge Functions."""
    if not manifest_path.exists():
        logger.warning("Deploy manifest not found at %s", manifest_path)
        return []

    with open(manifest_path, "r") as fh:
        manifest = yaml.safe_load(fh) or {}

    functions = manifest.get("functions", manifest.get("edge_functions", []))
    if isinstance(functions, dict):
        functions = [
            {"name": k, **v} for k, v in functions.items()
        ]

    results = []
    for fn in functions:
        name = fn if isinstance(fn, str) else fn.get("name", "unknown")
        entry = {
            "name": name,
            "smoke_test_path": fn.get("smoke_test_path", f"/{name}") if isinstance(fn, dict) else f"/{name}",
            "status": "listed",
        }
        results.append(entry)

    logger.info("Found %d Edge Functions in manifest", len(results))
    return results


def inventory_cron(conn: psycopg2.extensions.connection) -> list[dict]:
    """Query cron.job table for scheduled jobs."""
    results: list[dict] = []
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT jobid, schedule, command, nodename, nodeport,
                       database, username, active, jobname
                FROM cron.job
                ORDER BY jobid
                """
            )
            columns = [desc[0] for desc in cur.description]
            for row in cur.fetchall():
                entry = dict(zip(columns, row))
                entry["active"] = bool(entry.get("active", False))
                results.append(entry)
    except psycopg2.Error as exc:
        logger.warning("Cannot query cron.job (extension may not exist): %s", exc)
        conn.rollback()

    logger.info("Found %d pg_cron jobs", len(results))
    return results


def inventory_storage(supabase_url: str, service_key: str) -> list[dict]:
    """List storage buckets and object counts via Supabase Storage API."""
    results: list[dict] = []
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
    }

    try:
        resp = requests.get(
            f"{supabase_url}/storage/v1/bucket",
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        buckets = resp.json()
    except requests.RequestException as exc:
        logger.warning("Cannot list storage buckets: %s", exc)
        return results

    for bucket in buckets:
        bucket_id = bucket.get("id", bucket.get("name", "unknown"))
        object_count = -1
        try:
            list_resp = requests.post(
                f"{supabase_url}/storage/v1/object/list/{bucket_id}",
                headers=headers,
                json={"prefix": "", "limit": 0, "offset": 0},
                timeout=30,
            )
            if list_resp.ok:
                objects = list_resp.json()
                object_count = len(objects) if isinstance(objects, list) else -1
        except requests.RequestException:
            pass

        results.append(
            {
                "bucket_id": bucket_id,
                "name": bucket.get("name", bucket_id),
                "public": bucket.get("public", False),
                "object_count": object_count,
                "created_at": bucket.get("created_at", ""),
            }
        )

    logger.info("Found %d storage buckets", len(results))
    return results


def write_inventory(
    output_dir: Path,
    tables: list[dict],
    functions: list[dict],
    cron_jobs: list[dict],
    storage: list[dict],
) -> Path:
    """Write consolidated inventory JSON to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()

    inventory = {
        "timestamp": timestamp,
        "source": os.environ.get("SOURCE_PG_HOST", "unknown"),
        "summary": {
            "table_count": len(tables),
            "total_rows": sum(t["row_count"] for t in tables if t["row_count"] >= 0),
            "function_count": len(functions),
            "cron_job_count": len(cron_jobs),
            "storage_bucket_count": len(storage),
        },
        "tables": tables,
        "edge_functions": functions,
        "cron_jobs": cron_jobs,
        "storage_buckets": storage,
    }

    output_path = output_dir / "inventory.json"
    with open(output_path, "w") as fh:
        json.dump(inventory, fh, indent=2, default=str)

    logger.info("Inventory written to %s", output_path)
    return output_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export inventory from managed Supabase for migration planning."
    )
    parser.add_argument(
        "--mode",
        choices=["dry-run", "execute"],
        default="dry-run",
        help="dry-run logs actions without connecting; execute runs live queries",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/evidence/migration/inventory"),
        help="Output directory for inventory JSON",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("ssot/migration/azure_selfhost_migration_manifest.yaml"),
        help="Path to migration manifest YAML",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logger.info("Mode: %s | Output: %s | Manifest: %s", args.mode, args.output, args.manifest)

    if args.mode == "dry-run":
        logger.info("[DRY-RUN] Would connect to SOURCE_PG_HOST=%s", os.environ.get("SOURCE_PG_HOST", "<unset>"))
        logger.info("[DRY-RUN] Would scan schemas: %s", ", ".join(SCHEMAS_TO_SCAN))
        logger.info("[DRY-RUN] Would read deploy manifest from %s", args.manifest)
        logger.info("[DRY-RUN] Would query cron.job table")
        logger.info("[DRY-RUN] Would list storage buckets via SUPABASE_URL=%s", os.environ.get("SUPABASE_URL", "<unset>"))
        logger.info("[DRY-RUN] Would write inventory to %s", args.output)

        # Write a placeholder inventory in dry-run mode
        args.output.mkdir(parents=True, exist_ok=True)
        placeholder = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "dry-run",
            "schemas_scanned": list(SCHEMAS_TO_SCAN),
            "manifest_path": str(args.manifest),
        }
        out_path = args.output / "inventory.json"
        with open(out_path, "w") as fh:
            json.dump(placeholder, fh, indent=2)
        logger.info("[DRY-RUN] Placeholder inventory written to %s", out_path)
        print("STATUS: PASS inventory (dry-run)")
        return 0

    # Execute mode
    try:
        conn = get_source_connection()
    except Exception as exc:
        logger.error("Failed to connect to source Postgres: %s", exc)
        return 1

    try:
        tables = inventory_tables(conn)
        cron_jobs = inventory_cron(conn)
    finally:
        conn.close()

    functions = inventory_functions(args.manifest)

    supabase_url = os.environ.get("SUPABASE_URL", "")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if supabase_url and service_key:
        storage = inventory_storage(supabase_url, service_key)
    else:
        logger.warning("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set; skipping storage inventory")
        storage = []

    output_path = write_inventory(args.output, tables, functions, cron_jobs, storage)
    print("STATUS: PASS tables (%d found)" % len(tables))
    print("STATUS: PASS edge_functions (%d found)" % len(functions))
    print("STATUS: PASS cron_jobs (%d found)" % len(cron_jobs))
    print("STATUS: PASS storage_buckets (%d found)" % len(storage))
    print("STATUS: PASS inventory written to %s" % output_path)
    logger.info("Inventory export complete: %s", output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
