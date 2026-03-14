#!/usr/bin/env python3
"""Validate migration parity and cutover readiness.

Compares source (managed Supabase) and target (self-hosted) across
all asset types. Produces a machine-readable cutover readiness report.

Usage:
    python validate_cutover.py \
        --mode full \
        --output docs/evidence/migration/validation \
        --manifest ssot/migration/azure_selfhost_migration_manifest.yaml
"""

import argparse
import hashlib
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
logger = logging.getLogger("validate_cutover")

ROW_COUNT_TOLERANCE = 0.01  # 1%


def load_manifest(manifest_path: Path) -> dict:
    """Load the migration manifest YAML."""
    with open(manifest_path, "r") as fh:
        return yaml.safe_load(fh) or {}


def get_connection(dsn_env_var: str) -> psycopg2.extensions.connection:
    """Create a PG connection from the named environment variable."""
    dsn = os.environ.get(dsn_env_var)
    if not dsn:
        raise RuntimeError(f"{dsn_env_var} not set")
    return psycopg2.connect(dsn)


def validate_table_parity(
    source_conn: psycopg2.extensions.connection,
    target_conn: psycopg2.extensions.connection,
    schemas: list[str],
) -> list[dict]:
    """Compare row counts between source and target with tolerance."""
    results: list[dict] = []

    with source_conn.cursor() as cur:
        tables = []
        for schema in schemas:
            cur.execute(
                "SELECT schemaname, tablename FROM pg_tables WHERE schemaname = %s ORDER BY tablename",
                (schema,),
            )
            tables.extend(cur.fetchall())

    for schema, table in tables:
        fqn = f'"{schema}"."{table}"'
        entry = {"schema": schema, "table": table}

        try:
            with source_conn.cursor() as cur:
                cur.execute(f"SELECT count(*) FROM {fqn}")
                entry["source_rows"] = cur.fetchone()[0]
        except psycopg2.Error as exc:
            entry["source_rows"] = -1
            entry["source_error"] = str(exc)
            source_conn.rollback()

        try:
            with target_conn.cursor() as cur:
                cur.execute(f"SELECT count(*) FROM {fqn}")
                entry["target_rows"] = cur.fetchone()[0]
        except psycopg2.Error as exc:
            entry["target_rows"] = -1
            entry["target_error"] = str(exc)
            target_conn.rollback()

        src = entry.get("source_rows", -1)
        tgt = entry.get("target_rows", -1)

        if src >= 0 and tgt >= 0:
            if src == 0 and tgt == 0:
                entry["parity"] = True
                entry["drift_pct"] = 0.0
            elif src == 0:
                entry["parity"] = False
                entry["drift_pct"] = 100.0
            else:
                drift = abs(src - tgt) / src
                entry["drift_pct"] = round(drift * 100, 2)
                entry["parity"] = drift <= ROW_COUNT_TOLERANCE
        else:
            entry["parity"] = False
            entry["drift_pct"] = -1.0

        results.append(entry)

        if not entry["parity"]:
            logger.warning(
                "Table parity FAIL: %s.%s source=%s target=%s drift=%.2f%%",
                schema, table, src, tgt, entry.get("drift_pct", -1),
            )

    passed = sum(1 for r in results if r["parity"])
    logger.info("Table parity: %d/%d passed (tolerance %.0f%%)", passed, len(results), ROW_COUNT_TOLERANCE * 100)
    return results


def validate_checksums(
    source_conn: psycopg2.extensions.connection,
    target_conn: psycopg2.extensions.connection,
    checksum_tables: list[dict],
) -> list[dict]:
    """MD5 checksum validation on key columns of critical tables."""
    results: list[dict] = []

    for spec in checksum_tables:
        schema = spec.get("schema", "public")
        table = spec["table"]
        columns = spec.get("columns", ["id"])
        order_by = spec.get("order_by", columns[0])
        fqn = f'"{schema}"."{table}"'

        col_expr = " || ".join(f"COALESCE(CAST({c} AS text), '')" for c in columns)
        query = f"SELECT md5(string_agg({col_expr}, '|' ORDER BY {order_by})) FROM {fqn}"

        entry = {"schema": schema, "table": table, "columns": columns}

        try:
            with source_conn.cursor() as cur:
                cur.execute(query)
                entry["source_md5"] = cur.fetchone()[0]
        except psycopg2.Error as exc:
            entry["source_md5"] = None
            entry["source_error"] = str(exc)
            source_conn.rollback()

        try:
            with target_conn.cursor() as cur:
                cur.execute(query)
                entry["target_md5"] = cur.fetchone()[0]
        except psycopg2.Error as exc:
            entry["target_md5"] = None
            entry["target_error"] = str(exc)
            target_conn.rollback()

        entry["match"] = (
            entry.get("source_md5") is not None
            and entry["source_md5"] == entry.get("target_md5")
        )
        results.append(entry)

        if not entry["match"]:
            logger.warning("Checksum FAIL: %s.%s source=%s target=%s",
                           schema, table, entry.get("source_md5", "?")[:12], entry.get("target_md5", "?")[:12] if entry.get("target_md5") else "?")

    passed = sum(1 for r in results if r["match"])
    logger.info("Checksum validation: %d/%d passed", passed, len(results))
    return results


def validate_edge_functions(
    target_url: str, functions: list[dict]
) -> list[dict]:
    """GET each smoke_test_path and report health status."""
    results: list[dict] = []

    for fn in functions:
        name = fn.get("name", "unknown")
        path = fn.get("smoke_test_path", f"/{name}")
        url = f"{target_url}/functions/v1{path}"

        try:
            resp = requests.get(url, timeout=15)
            healthy = 200 <= resp.status_code < 500
            results.append({
                "name": name,
                "url": url,
                "status_code": resp.status_code,
                "healthy": healthy,
            })
        except requests.RequestException as exc:
            results.append({
                "name": name,
                "url": url,
                "status_code": -1,
                "healthy": False,
                "error": str(exc),
            })

        status = "OK" if results[-1]["healthy"] else "FAIL"
        logger.info("Edge function %s: %s (HTTP %s)", name, status, results[-1]["status_code"])

    healthy_count = sum(1 for r in results if r["healthy"])
    logger.info("Edge function health: %d/%d healthy", healthy_count, len(results))
    return results


def validate_cron_parity(
    source_conn: psycopg2.extensions.connection,
    target_conn: psycopg2.extensions.connection,
) -> dict:
    """Compare pg_cron job counts and state."""
    result = {"source_count": 0, "target_count": 0, "target_active": 0, "match": False}

    try:
        with source_conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM cron.job")
            result["source_count"] = cur.fetchone()[0]
    except psycopg2.Error:
        source_conn.rollback()

    try:
        with target_conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM cron.job")
            result["target_count"] = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM cron.job WHERE active = true")
            result["target_active"] = cur.fetchone()[0]
    except psycopg2.Error:
        target_conn.rollback()

    result["match"] = result["source_count"] == result["target_count"]
    logger.info("Cron parity: source=%d target=%d active=%d match=%s",
                result["source_count"], result["target_count"],
                result["target_active"], result["match"])
    return result


def validate_n8n_workflows(n8n_url: str, api_key: str, expected_state: str) -> dict:
    """Check n8n workflow import state and activity."""
    result = {"total": 0, "active": 0, "inactive": 0, "state_valid": False}

    headers = {"X-N8N-API-KEY": api_key}
    try:
        resp = requests.get(f"{n8n_url}/api/v1/workflows", headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        workflows = data.get("data", data) if isinstance(data, dict) else data
        if not isinstance(workflows, list):
            workflows = []

        result["total"] = len(workflows)
        result["active"] = sum(1 for w in workflows if w.get("active"))
        result["inactive"] = result["total"] - result["active"]

        if expected_state == "pre-cutover":
            result["state_valid"] = result["active"] == 0
        elif expected_state.startswith("wave-"):
            # For wave checks, active count should be > 0
            result["state_valid"] = result["active"] > 0
        else:
            result["state_valid"] = True

    except requests.RequestException as exc:
        result["error"] = str(exc)

    logger.info("n8n workflows: total=%d active=%d inactive=%d state_valid=%s (expected: %s)",
                result["total"], result["active"], result["inactive"],
                result["state_valid"], expected_state)
    return result


def validate_consumers(consumers_file: Path, target_url: str) -> list[dict]:
    """Smoke test each consumer endpoint from consumers.yaml."""
    results: list[dict] = []

    if not consumers_file.exists():
        logger.warning("Consumers file not found: %s", consumers_file)
        return results

    with open(consumers_file, "r") as fh:
        data = yaml.safe_load(fh) or {}

    consumers = data.get("consumers", [])
    for consumer in consumers:
        name = consumer.get("name", "unknown")
        health_path = consumer.get("health_path", "/health")
        base = consumer.get("base_url", target_url)
        url = f"{base}{health_path}"

        try:
            resp = requests.get(url, timeout=15)
            healthy = resp.status_code == 200
            results.append({"name": name, "url": url, "status_code": resp.status_code, "healthy": healthy})
        except requests.RequestException as exc:
            results.append({"name": name, "url": url, "status_code": -1, "healthy": False, "error": str(exc)})

        logger.info("Consumer %s: %s (HTTP %s)", name, "OK" if results[-1]["healthy"] else "FAIL", results[-1]["status_code"])

    return results


def generate_readiness_summary(
    table_parity: list[dict],
    checksums: list[dict],
    edge_functions: list[dict],
    cron_parity: dict,
    n8n_state: dict,
    consumers: list[dict],
) -> dict:
    """Produce overall cutover readiness determination."""
    checks = {
        "table_parity": all(t["parity"] for t in table_parity) if table_parity else False,
        "checksums": all(c["match"] for c in checksums) if checksums else True,
        "edge_functions": all(f["healthy"] for f in edge_functions) if edge_functions else True,
        "cron_parity": cron_parity.get("match", False),
        "n8n_workflows": n8n_state.get("state_valid", False),
        "consumers": all(c["healthy"] for c in consumers) if consumers else True,
    }

    ready = all(checks.values())
    summary = {
        "cutover_ready": ready,
        "checks": checks,
        "blocking": [k for k, v in checks.items() if not v],
    }

    if ready:
        logger.info("CUTOVER READY: All validation checks passed")
    else:
        logger.warning("CUTOVER NOT READY: Blocking checks: %s", ", ".join(summary["blocking"]))

    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate migration parity and cutover readiness."
    )
    parser.add_argument("--mode", choices=["dry-run", "full"], default="dry-run")
    parser.add_argument("--output", type=Path, default=Path("docs/evidence/migration/validation"))
    parser.add_argument("--manifest", type=Path,
                        default=Path("ssot/migration/azure_selfhost_migration_manifest.yaml"))
    parser.add_argument("--consumers", type=Path, default=Path("ssot/migration/consumers.yaml"))
    parser.add_argument("--n8n-state", choices=["pre-cutover", "wave-1", "wave-2", "wave-3", "post-cutover"],
                        default="pre-cutover", help="Expected n8n workflow state for validation")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logger.info("Mode: %s | Output: %s | Manifest: %s", args.mode, args.output, args.manifest)

    if not args.manifest.exists():
        logger.error("Migration manifest not found: %s", args.manifest)
        return 1

    manifest = load_manifest(args.manifest)
    schemas = manifest.get("schemas", ["public", "ops", "mcp_jobs", "scout"])
    checksum_tables = manifest.get("checksum_tables", [])
    edge_functions = manifest.get("edge_functions", [])
    if isinstance(edge_functions, dict):
        edge_functions = [{"name": k, **v} for k, v in edge_functions.items()]

    if args.mode == "dry-run":
        logger.info("[DRY-RUN] Would validate table parity across schemas: %s", ", ".join(schemas))
        logger.info("[DRY-RUN] Would checksum %d critical tables", len(checksum_tables))
        logger.info("[DRY-RUN] Would smoke test %d edge functions", len(edge_functions))
        logger.info("[DRY-RUN] Would verify pg_cron job parity")
        logger.info("[DRY-RUN] Would validate n8n workflow state (expected: %s)", args.n8n_state)
        logger.info("[DRY-RUN] Would smoke test consumers from %s", args.consumers)

        args.output.mkdir(parents=True, exist_ok=True)
        report = {
            "mode": "dry-run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "validation_plan": {
                "schemas": schemas,
                "checksum_tables": len(checksum_tables),
                "edge_functions": len(edge_functions),
                "n8n_expected_state": args.n8n_state,
                "consumers_file": str(args.consumers),
            },
        }
        with open(args.output / "cutover_readiness_report.json", "w") as fh:
            json.dump(report, fh, indent=2)
        return 0

    # Full validation mode
    target_url = os.environ.get("TARGET_SUPABASE_URL", "")
    n8n_url = os.environ.get("TARGET_N8N_URL", "")
    n8n_api_key = os.environ.get("N8N_API_KEY", "")

    try:
        source_conn = get_connection("SOURCE_PG_DSN")
        target_conn = get_connection("TARGET_PG_DSN")
    except RuntimeError as exc:
        logger.error("Connection failed: %s", exc)
        return 1

    try:
        # 1. Table parity
        logger.info("=== Table Parity Validation ===")
        table_parity = validate_table_parity(source_conn, target_conn, schemas)

        # 2. Checksum validation
        logger.info("=== Checksum Validation ===")
        checksums = validate_checksums(source_conn, target_conn, checksum_tables)

        # 3. Edge function health
        logger.info("=== Edge Function Health ===")
        if target_url:
            ef_results = validate_edge_functions(target_url, edge_functions)
        else:
            logger.warning("TARGET_SUPABASE_URL not set; skipping edge function validation")
            ef_results = []

        # 4. Cron parity
        logger.info("=== Cron Parity ===")
        cron_parity = validate_cron_parity(source_conn, target_conn)

        # 5. n8n workflow state
        logger.info("=== n8n Workflow State ===")
        if n8n_url and n8n_api_key:
            n8n_state = validate_n8n_workflows(n8n_url, n8n_api_key, args.n8n_state)
        else:
            logger.warning("TARGET_N8N_URL or N8N_API_KEY not set; skipping n8n validation")
            n8n_state = {"state_valid": False, "error": "not configured"}

        # 6. Consumer health
        logger.info("=== Consumer Health ===")
        consumer_results = validate_consumers(args.consumers, target_url)

        # Generate readiness summary
        summary = generate_readiness_summary(
            table_parity, checksums, ef_results, cron_parity, n8n_state, consumer_results
        )

    finally:
        source_conn.close()
        target_conn.close()

    # Write report
    args.output.mkdir(parents=True, exist_ok=True)
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "readiness": summary,
        "table_parity": table_parity,
        "checksums": checksums,
        "edge_functions": ef_results,
        "cron_parity": cron_parity,
        "n8n_workflows": n8n_state,
        "consumers": consumer_results,
    }
    with open(args.output / "cutover_readiness_report.json", "w") as fh:
        json.dump(report, fh, indent=2, default=str)

    # Print summary
    logger.info("=" * 60)
    logger.info("CUTOVER READINESS: %s", "READY" if summary["cutover_ready"] else "NOT READY")
    for check, passed in summary["checks"].items():
        logger.info("  %s: %s", check, "PASS" if passed else "FAIL")
    if summary["blocking"]:
        logger.info("  Blocking: %s", ", ".join(summary["blocking"]))
    logger.info("=" * 60)

    return 0 if summary["cutover_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
