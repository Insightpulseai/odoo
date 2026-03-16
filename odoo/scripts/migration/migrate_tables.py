#!/usr/bin/env python3
"""Migrate tables from managed Supabase to self-hosted target.

Tiered migration: reference -> master -> transactional tables.
Supports resumable checkpoints.

Usage:
    python migrate_tables.py \
        --mode dry-run \
        --output docs/evidence/migration/tables \
        --checkpoint /tmp/table_migration_checkpoint.json
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("migrate_tables")

TIER_DEFINITIONS = {
    "1": {
        "label": "critical",
        "description": "auth.users, storage.objects, public tables with >1000 rows",
        "filter": lambda t: (
            t["schema"] in ("auth", "storage")
            or (t["schema"] == "public" and t.get("row_count", 0) > 1000)
        ),
    },
    "2": {
        "label": "operational",
        "description": "ops.*, mcp_jobs.*, scout.* tables",
        "filter": lambda t: t["schema"] in ("ops", "mcp_jobs", "scout"),
    },
    "3": {
        "label": "reference",
        "description": "lookup tables, config tables, remaining",
        "filter": lambda t: True,  # catch-all for anything not in tier 1 or 2
    },
}
TIER_ORDER = ("1", "2", "3")


def load_inventory(inventory_path: Path) -> list[dict]:
    """Load table inventory from export_supabase_inventory output."""
    with open(inventory_path, "r") as fh:
        data = json.load(fh)
    tables = data.get("tables", [])
    logger.info("Loaded %d tables from inventory", len(tables))
    return tables


def classify_tables(tables: list[dict]) -> dict[str, list[dict]]:
    """Classify tables into tiered groups for ordered migration.

    Tier 1 (critical): auth.users, storage.objects, public tables with >1000 rows.
    Tier 2 (operational): ops.*, mcp_jobs.*, scout.* tables.
    Tier 3 (reference): lookup tables, config tables, everything else.
    """
    tiered: dict[str, list[dict]] = {"1": [], "2": [], "3": []}
    assigned: set[str] = set()

    for tier_id in ("1", "2"):
        tier_def = TIER_DEFINITIONS[tier_id]
        for table in tables:
            fqn = f"{table['schema']}.{table['table']}"
            if fqn not in assigned and tier_def["filter"](table):
                tiered[tier_id].append(table)
                assigned.add(fqn)

    # Tier 3 catches everything not already assigned
    for table in tables:
        fqn = f"{table['schema']}.{table['table']}"
        if fqn not in assigned:
            tiered["3"].append(table)

    for tier_id in TIER_ORDER:
        label = TIER_DEFINITIONS[tier_id]["label"]
        logger.info("Tier %s (%s): %d tables", tier_id, label, len(tiered[tier_id]))

    return tiered


def load_checkpoint(checkpoint_path: Path) -> dict:
    """Load resumable checkpoint state."""
    if checkpoint_path.exists():
        with open(checkpoint_path, "r") as fh:
            state = json.load(fh)
        logger.info("Resumed from checkpoint: %d tables completed", len(state.get("completed", [])))
        return state
    return {"completed": [], "failed": [], "started_at": datetime.now(timezone.utc).isoformat()}


def save_checkpoint(checkpoint_path: Path, state: dict) -> None:
    """Persist checkpoint state to disk."""
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(checkpoint_path, "w") as fh:
        json.dump(state, fh, indent=2)


def dump_table(schema: str, table: str, source_dsn: str) -> bytes | None:
    """Run pg_dump --data-only for a single table, return stdout bytes."""
    fqn = f"{schema}.{table}"
    cmd = [
        "pg_dump",
        source_dsn,
        "--data-only",
        "--no-owner",
        "--no-acl",
        f"--table={fqn}",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=600)
        if result.returncode != 0:
            logger.error("pg_dump failed for %s: %s", fqn, result.stderr.decode())
            return None
        return result.stdout
    except subprocess.TimeoutExpired:
        logger.error("pg_dump timed out for %s", fqn)
        return None
    except FileNotFoundError:
        logger.error("pg_dump binary not found in PATH")
        return None


def restore_table(dump_data: bytes, target_dsn: str) -> bool:
    """Restore pg_dump output to target via psql."""
    cmd = ["psql", target_dsn, "--single-transaction", "--set", "ON_ERROR_STOP=on"]
    try:
        result = subprocess.run(cmd, input=dump_data, capture_output=True, timeout=600)
        if result.returncode != 0:
            logger.error("psql restore failed: %s", result.stderr.decode()[:500])
            return False
        return True
    except subprocess.TimeoutExpired:
        logger.error("psql restore timed out")
        return False
    except FileNotFoundError:
        logger.error("psql binary not found in PATH")
        return False


def reset_sequences(conn: psycopg2.extensions.connection, schema: str, table: str) -> None:
    """Reset sequences associated with a table using setval()."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name, pg_get_serial_sequence(%s, column_name)
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            """,
            (f"{schema}.{table}", schema, table),
        )
        for col, seq in cur.fetchall():
            if seq:
                cur.execute(
                    f"SELECT setval('{seq}', COALESCE((SELECT max({col}) FROM \"{schema}\".\"{table}\"), 1))"
                )
                logger.info("Reset sequence %s for %s.%s.%s", seq, schema, table, col)
    conn.commit()


def verify_row_counts(
    source_conn: psycopg2.extensions.connection,
    target_conn: psycopg2.extensions.connection,
    tables: list[dict],
) -> list[dict]:
    """Compare row counts between source and target for each table."""
    results = []
    for table in tables:
        schema, tbl = table["schema"], table["table"]
        fqn = f'"{schema}"."{tbl}"'
        try:
            with source_conn.cursor() as cur:
                cur.execute(f"SELECT count(*) FROM {fqn}")
                source_count = cur.fetchone()[0]
            with target_conn.cursor() as cur:
                cur.execute(f"SELECT count(*) FROM {fqn}")
                target_count = cur.fetchone()[0]
            match = source_count == target_count
            results.append({
                "schema": schema, "table": tbl,
                "source_rows": source_count, "target_rows": target_count,
                "match": match,
            })
            if not match:
                logger.warning("Row mismatch %s.%s: source=%d target=%d", schema, tbl, source_count, target_count)
        except psycopg2.Error as exc:
            results.append({
                "schema": schema, "table": tbl,
                "source_rows": -1, "target_rows": -1,
                "match": False, "error": str(exc),
            })
            source_conn.rollback()
            target_conn.rollback()
    return results


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate tables from managed Supabase to self-hosted target."
    )
    parser.add_argument("--mode", choices=["dry-run", "execute"], default="dry-run")
    parser.add_argument("--output", type=Path, default=Path("docs/evidence/migration/tables"))
    parser.add_argument("--checkpoint", type=Path, default=Path("/tmp/table_migration_checkpoint.json"))
    parser.add_argument("--inventory", type=Path, default=Path("docs/evidence/migration/inventory/supabase_inventory.json"))
    parser.add_argument("--manifest", type=Path, default=None, help="Optional migration manifest YAML")
    parser.add_argument("--tier", choices=["1", "2", "3"], default=None,
                        help="Migrate only a specific tier (1=critical, 2=operational, 3=reference)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logger.info("Mode: %s | Output: %s | Checkpoint: %s", args.mode, args.output, args.checkpoint)

    if not args.inventory.exists():
        logger.error("Inventory file not found: %s (run export_supabase_inventory.py first)", args.inventory)
        return 1

    tables = load_inventory(args.inventory)
    checkpoint = load_checkpoint(args.checkpoint)
    completed_set = set(checkpoint.get("completed", []))

    tiered = classify_tables(tables)
    tiers_to_run = [args.tier] if args.tier else list(TIER_ORDER)

    if args.mode == "dry-run":
        logger.info("[DRY-RUN] Would classify %d tables into tiers", len(tables))
        for tier_id in tiers_to_run:
            label = TIER_DEFINITIONS[tier_id]["label"]
            logger.info("[DRY-RUN] Would migrate tier %s (%s): %d tables",
                        tier_id, label, len(tiered[tier_id]))
        pending = [
            f"{t['schema']}.{t['table']}" for tier_id in tiers_to_run
            for t in tiered[tier_id]
            if f"{t['schema']}.{t['table']}" not in completed_set
        ]
        logger.info("[DRY-RUN] %d tables pending, %d already completed", len(pending), len(completed_set))
        logger.info("[DRY-RUN] Would pg_dump each table from SOURCE_PG_DSN")
        logger.info("[DRY-RUN] Would psql restore to TARGET_PG_DSN")
        logger.info("[DRY-RUN] Would reset sequences and verify row counts")

        args.output.mkdir(parents=True, exist_ok=True)
        report = {
            "mode": "dry-run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_tables": len(tables),
            "pending": len(pending),
            "completed": len(completed_set),
            "tiers": {t: len(tiered[t]) for t in tiers_to_run},
        }
        with open(args.output / "table_migration_report.json", "w") as fh:
            json.dump(report, fh, indent=2)
        print("STATUS: PASS table_classification (%d tables across %d tiers)" % (len(tables), len(tiers_to_run)))
        return 0

    # Execute mode
    source_dsn = os.environ.get("SOURCE_PG_DSN")
    target_dsn = os.environ.get("TARGET_PG_DSN")
    if not source_dsn or not target_dsn:
        logger.error("SOURCE_PG_DSN and TARGET_PG_DSN must be set")
        return 1

    try:
        source_conn = psycopg2.connect(source_dsn)
        target_conn = psycopg2.connect(target_dsn)
    except Exception as exc:
        logger.error("Failed to connect: %s", exc)
        return 1

    try:
        failed = []

        for tier in tiers_to_run:
            logger.info("=== Migrating tier: %s (%d tables) ===", tier, len(tiered[tier]))
            for table in tiered[tier]:
                fqn = f"{table['schema']}.{table['table']}"
                if fqn in completed_set:
                    logger.info("Skipping %s (already completed)", fqn)
                    continue

                logger.info("Dumping %s ...", fqn)
                dump_data = dump_table(table["schema"], table["table"], source_dsn)
                if dump_data is None:
                    failed.append({"table": fqn, "stage": "dump"})
                    checkpoint["failed"] = failed
                    save_checkpoint(args.checkpoint, checkpoint)
                    continue

                logger.info("Restoring %s (%d bytes) ...", fqn, len(dump_data))
                if not restore_table(dump_data, target_dsn):
                    failed.append({"table": fqn, "stage": "restore"})
                    checkpoint["failed"] = failed
                    save_checkpoint(args.checkpoint, checkpoint)
                    continue

                reset_sequences(target_conn, table["schema"], table["table"])
                checkpoint["completed"].append(fqn)
                completed_set.add(fqn)
                save_checkpoint(args.checkpoint, checkpoint)
                logger.info("Completed %s", fqn)

        logger.info("=== Verifying row counts ===")
        verification = verify_row_counts(source_conn, target_conn, tables)

        args.output.mkdir(parents=True, exist_ok=True)
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "completed": len(completed_set),
            "failed": failed,
            "verification": verification,
        }
        with open(args.output / "table_migration_report.json", "w") as fh:
            json.dump(report, fh, indent=2, default=str)

        mismatches = [v for v in verification if not v.get("match", False)]
        if mismatches:
            logger.warning("%d tables have row count mismatches", len(mismatches))
            print("STATUS: FAIL row_count_validation (%d mismatches)" % len(mismatches))
        else:
            print("STATUS: PASS row_count_validation")

        if failed:
            logger.error("%d tables failed migration", len(failed))
            print("STATUS: FAIL table_migration (%d failed)" % len(failed))
            return 1

        print("STATUS: PASS table_migration (%d tables)" % len(completed_set))
        logger.info("Table migration complete: %d tables migrated", len(completed_set))
        return 0

    finally:
        source_conn.close()
        target_conn.close()


if __name__ == "__main__":
    sys.exit(main())
