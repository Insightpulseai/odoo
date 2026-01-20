#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2026 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
"""
Odoo Shadow Schema ETL Sync

Synchronizes Odoo data to Supabase shadow tables for analytics, RAG, and reporting.
Uses incremental sync via write_date watermarks.

Usage:
    # Set environment variables
    export ODOO_URL="https://erp.insightpulseai.net"
    export ODOO_DB="odoo_core"
    export ODOO_USER="api-user@example.com"
    export ODOO_PASSWORD="your-password"
    export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
    export SUPABASE_SERVICE_KEY="your-service-role-key"

    # Sync all tables (incremental)
    python scripts/sync_odoo_shadow.py

    # Sync specific models
    python scripts/sync_odoo_shadow.py --models res.partner,account.move

    # Full sync (ignore watermarks)
    python scripts/sync_odoo_shadow.py --full

    # Dry run
    python scripts/sync_odoo_shadow.py --dry-run

Environment Variables:
    ODOO_URL             Odoo server URL (required)
    ODOO_DB              Odoo database name (required)
    ODOO_USER            Odoo API user email (required)
    ODOO_PASSWORD        Odoo API user password (required)
    SUPABASE_URL         Supabase project URL (required)
    SUPABASE_SERVICE_KEY Supabase service role key (required)
"""

import argparse
import hashlib
import json
import logging
import os
import sys
import time
import uuid
import xmlrpc.client
from datetime import datetime, timezone
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Try to import supabase client
try:
    from supabase import Client, create_client
except ImportError:
    logger.error("supabase-py not installed. Run: pip install supabase")
    sys.exit(1)


# =============================================================================
# Configuration
# =============================================================================

# Priority models to sync (core business data)
PRIORITY_MODELS = [
    "res.partner",
    "res.users",
    "res.company",
    "account.move",
    "account.move.line",
    "account.account",
    "account.journal",
    "sale.order",
    "sale.order.line",
    "purchase.order",
    "purchase.order.line",
    "stock.picking",
    "stock.move",
    "product.product",
    "product.template",
    "hr.employee",
    "project.project",
    "project.task",
]

# Models to skip (transient, abstract, or no direct table)
SKIP_MODELS = [
    "base",
    "ir.actions.actions",  # abstract
    "mail.thread",  # mixin
    "mail.activity.mixin",  # mixin
]

# Batch size for sync operations
DEFAULT_BATCH_SIZE = 1000

# Type mapping: Odoo field type -> conversion function
TYPE_CONVERTERS = {
    "datetime": lambda v: v if v else None,
    "date": lambda v: v if v else None,
    "binary": lambda v: None,  # Skip binary fields in shadow
    "many2one": lambda v: v[0] if isinstance(v, (list, tuple)) and v else (v if v else None),
}


# =============================================================================
# Helpers
# =============================================================================


def get_env_var(name: str, required: bool = True) -> str | None:
    """Get environment variable with optional requirement check."""
    value = os.environ.get(name)
    if required and not value:
        logger.error(f"Missing required environment variable: {name}")
        sys.exit(1)
    return value


def model_to_table_name(model: str) -> str:
    """Convert Odoo model name to shadow table name."""
    # res.partner -> odoo_shadow_res_partner
    return "odoo_shadow_" + model.replace(".", "_")


def compute_row_hash(row: dict) -> str:
    """Compute hash of row data for change detection."""
    # Remove tracking columns before hashing
    data = {k: v for k, v in row.items() if not k.startswith("_")}
    return hashlib.md5(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()


# =============================================================================
# Odoo Connection
# =============================================================================


class OdooConnection:
    """Manages connection to Odoo via XML-RPC."""

    def __init__(self):
        self.url = get_env_var("ODOO_URL")
        self.db = get_env_var("ODOO_DB")
        self.user = get_env_var("ODOO_USER")
        self.password = get_env_var("ODOO_PASSWORD")
        self.uid = None
        self.models = None

    def connect(self):
        """Establish connection to Odoo."""
        logger.info(f"Connecting to Odoo at {self.url}...")

        try:
            common = xmlrpc.client.ServerProxy(
                f"{self.url}/xmlrpc/2/common",
                allow_none=True,
            )
            self.uid = common.authenticate(self.db, self.user, self.password, {})
            if not self.uid:
                raise Exception("Authentication failed")

            self.models = xmlrpc.client.ServerProxy(
                f"{self.url}/xmlrpc/2/object",
                allow_none=True,
            )
            logger.info(f"Connected to Odoo as uid={self.uid}")
        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {e}")
            sys.exit(1)

    def execute(self, model: str, method: str, *args, **kwargs):
        """Execute method on Odoo model."""
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            method,
            args,
            kwargs,
        )

    def search_read(
        self,
        model: str,
        domain: list,
        fields: list,
        limit: int = 0,
        offset: int = 0,
        order: str = "id",
    ) -> list[dict]:
        """Search and read records from Odoo."""
        return self.execute(
            model,
            "search_read",
            domain,
            fields=fields,
            limit=limit,
            offset=offset,
            order=order,
        )

    def get_model_fields(self, model: str) -> dict:
        """Get field definitions for a model."""
        return self.execute(model, "fields_get", [], attributes=["type", "store", "readonly"])

    def get_record_count(self, model: str, domain: list = None) -> int:
        """Get count of records matching domain."""
        return self.execute(model, "search_count", domain or [])


# =============================================================================
# Supabase Connection
# =============================================================================


class SupabaseConnection:
    """Manages connection to Supabase."""

    def __init__(self):
        self.url = get_env_var("SUPABASE_URL")
        self.key = get_env_var("SUPABASE_SERVICE_KEY")
        self.client: Client = None

    def connect(self):
        """Establish connection to Supabase."""
        logger.info(f"Connecting to Supabase at {self.url}...")

        try:
            self.client = create_client(self.url, self.key)
            logger.info("Connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            sys.exit(1)

    def get_watermark(self, table_name: str) -> str | None:
        """Get last sync watermark for a table."""
        try:
            response = self.client.rpc(
                "get_shadow_watermark",
                {"p_table_name": table_name},
            ).execute()
            return response.data if response.data else None
        except Exception as e:
            logger.debug(f"Could not get watermark for {table_name}: {e}")
            return None

    def update_watermark(
        self,
        table_name: str,
        write_date: str,
        last_id: int = None,
        rows_synced: int = 0,
    ):
        """Update sync watermark for a table."""
        try:
            self.client.rpc(
                "update_shadow_watermark",
                {
                    "p_table_name": table_name,
                    "p_write_date": write_date,
                    "p_last_id": last_id,
                    "p_rows_synced": rows_synced,
                },
            ).execute()
        except Exception as e:
            logger.warning(f"Could not update watermark for {table_name}: {e}")

    def upsert_shadow(self, table_name: str, rows: list[dict]) -> int:
        """Upsert rows to shadow table."""
        if not rows:
            return 0

        try:
            # Use schema-qualified table via postgrest
            response = (
                self.client.schema("odoo_shadow")
                .table(table_name.replace("odoo_shadow_", ""))
                .upsert(rows, on_conflict="id")
                .execute()
            )
            return len(response.data) if response.data else len(rows)
        except Exception as e:
            logger.error(f"Failed to upsert to {table_name}: {e}")
            raise

    def log_sync_start(self, table_name: str) -> str:
        """Log sync start and return run_id."""
        run_id = str(uuid.uuid4())
        try:
            self.client.table("odoo_shadow_sync_log").insert(
                {
                    "sync_run_id": run_id,
                    "table_name": table_name,
                    "status": "running",
                }
            ).execute()
        except Exception as e:
            logger.warning(f"Could not log sync start: {e}")
        return run_id

    def log_sync_complete(
        self,
        run_id: str,
        table_name: str,
        rows_inserted: int = 0,
        rows_updated: int = 0,
        duration_ms: int = 0,
        error: str = None,
    ):
        """Log sync completion."""
        try:
            self.client.table("odoo_shadow_sync_log").update(
                {
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "rows_inserted": rows_inserted,
                    "rows_updated": rows_updated,
                    "duration_ms": duration_ms,
                    "status": "error" if error else "success",
                    "error_message": error,
                }
            ).eq("sync_run_id", run_id).execute()
        except Exception as e:
            logger.warning(f"Could not log sync complete: {e}")


# =============================================================================
# Shadow Sync Engine
# =============================================================================


class ShadowSyncEngine:
    """Main sync engine for Odoo -> Supabase shadow tables."""

    def __init__(self, odoo: OdooConnection, supabase: SupabaseConnection):
        self.odoo = odoo
        self.supabase = supabase
        self.dry_run = False
        self.full_sync = False
        self.batch_size = DEFAULT_BATCH_SIZE

    def get_syncable_fields(self, model: str) -> list[str]:
        """Get list of fields that can be synced for a model."""
        try:
            fields = self.odoo.get_model_fields(model)
            syncable = ["id", "write_date", "create_date"]

            for name, attrs in fields.items():
                if name in syncable:
                    continue
                # Skip non-stored, relational (except many2one), and binary fields
                if not attrs.get("store", True):
                    continue
                if attrs.get("type") in ("one2many", "many2many"):
                    continue
                if attrs.get("type") == "binary":
                    continue
                syncable.append(name)

            return syncable
        except Exception as e:
            logger.warning(f"Could not get fields for {model}: {e}")
            return ["id", "write_date"]

    def transform_row(self, row: dict, fields_info: dict) -> dict:
        """Transform Odoo row to shadow table format."""
        result = {}

        for key, value in row.items():
            if key == "write_date":
                result["_odoo_write_date"] = value
                continue
            if key == "create_date":
                continue

            # Get field type and convert
            field_info = fields_info.get(key, {})
            field_type = field_info.get("type", "char")

            if field_type in TYPE_CONVERTERS:
                result[key] = TYPE_CONVERTERS[field_type](value)
            elif isinstance(value, (list, tuple)):
                # Handle many2one that returns [id, name]
                result[key] = value[0] if value else None
            else:
                result[key] = value

        # Add tracking columns
        result["_synced_at"] = datetime.now(timezone.utc).isoformat()
        result["_sync_hash"] = compute_row_hash(result)

        return result

    def sync_model(self, model: str) -> dict:
        """Sync a single Odoo model to its shadow table."""
        table_name = model_to_table_name(model)
        logger.info(f"Syncing {model} -> {table_name}")

        start_time = time.time()
        run_id = None if self.dry_run else self.supabase.log_sync_start(table_name)

        try:
            # Get syncable fields
            fields = self.get_syncable_fields(model)
            fields_info = self.odoo.get_model_fields(model)

            # Build domain (incremental or full)
            domain = []
            if not self.full_sync:
                watermark = self.supabase.get_watermark(table_name)
                if watermark:
                    domain = [("write_date", ">", watermark)]
                    logger.info(f"  Incremental sync from {watermark}")
                else:
                    logger.info("  Full sync (no watermark)")

            # Count records to sync
            total_count = self.odoo.get_record_count(model, domain)
            logger.info(f"  Found {total_count} records to sync")

            if total_count == 0:
                return {"model": model, "synced": 0, "duration_ms": 0}

            # Sync in batches
            synced = 0
            offset = 0
            max_write_date = None
            max_id = None

            while offset < total_count:
                # Fetch batch from Odoo
                batch = self.odoo.search_read(
                    model,
                    domain,
                    fields,
                    limit=self.batch_size,
                    offset=offset,
                    order="write_date asc, id asc",
                )

                if not batch:
                    break

                # Transform rows
                transformed = []
                for row in batch:
                    transformed.append(self.transform_row(row, fields_info))
                    if row.get("write_date"):
                        if not max_write_date or row["write_date"] > max_write_date:
                            max_write_date = row["write_date"]
                    if row.get("id"):
                        if not max_id or row["id"] > max_id:
                            max_id = row["id"]

                # Upsert to Supabase
                if not self.dry_run:
                    self.supabase.upsert_shadow(table_name, transformed)

                synced += len(batch)
                offset += self.batch_size
                logger.info(f"  Synced {synced}/{total_count} records")

            # Update watermark
            if not self.dry_run and max_write_date:
                self.supabase.update_watermark(
                    table_name,
                    max_write_date,
                    max_id,
                    synced,
                )

            duration_ms = int((time.time() - start_time) * 1000)

            # Log completion
            if not self.dry_run:
                self.supabase.log_sync_complete(
                    run_id,
                    table_name,
                    rows_inserted=synced,
                    duration_ms=duration_ms,
                )

            return {"model": model, "synced": synced, "duration_ms": duration_ms}

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            if not self.dry_run and run_id:
                self.supabase.log_sync_complete(
                    run_id,
                    table_name,
                    duration_ms=duration_ms,
                    error=str(e),
                )
            logger.error(f"  Failed to sync {model}: {e}")
            return {"model": model, "synced": 0, "duration_ms": duration_ms, "error": str(e)}

    def sync_all(self, models: list[str] = None) -> list[dict]:
        """Sync multiple models."""
        if not models:
            models = PRIORITY_MODELS

        results = []
        for model in models:
            if model in SKIP_MODELS:
                logger.info(f"Skipping {model} (in skip list)")
                continue
            result = self.sync_model(model)
            results.append(result)

        return results


# =============================================================================
# Main
# =============================================================================


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sync Odoo data to Supabase shadow tables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--models",
        type=str,
        default=None,
        help="Comma-separated list of models to sync (default: priority models)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full sync (ignore watermarks)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Batch size for sync operations (default: {DEFAULT_BATCH_SIZE})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch from Odoo but don't write to Supabase",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    start_time = time.time()
    logger.info("=" * 70)
    logger.info("Odoo Shadow Schema ETL Sync")
    logger.info("=" * 70)

    if args.dry_run:
        logger.info("DRY RUN MODE - No writes to Supabase")

    # Connect to both systems
    odoo = OdooConnection()
    odoo.connect()

    supabase = SupabaseConnection()
    supabase.connect()

    # Initialize sync engine
    engine = ShadowSyncEngine(odoo, supabase)
    engine.dry_run = args.dry_run
    engine.full_sync = args.full
    engine.batch_size = args.batch_size

    # Parse models
    models = None
    if args.models:
        models = [m.strip() for m in args.models.split(",")]
        logger.info(f"Syncing {len(models)} specified models")
    else:
        logger.info(f"Syncing {len(PRIORITY_MODELS)} priority models")

    # Run sync
    results = engine.sync_all(models)

    # Summary
    elapsed = time.time() - start_time
    total_synced = sum(r.get("synced", 0) for r in results)
    errors = [r for r in results if r.get("error")]

    logger.info("=" * 70)
    logger.info("Sync Summary")
    logger.info("=" * 70)
    logger.info(f"  Models processed: {len(results)}")
    logger.info(f"  Total rows synced: {total_synced}")
    logger.info(f"  Errors: {len(errors)}")
    logger.info(f"  Duration: {elapsed:.2f}s")

    if errors:
        logger.info("")
        logger.info("Failed models:")
        for r in errors:
            logger.info(f"  - {r['model']}: {r['error']}")

    logger.info("=" * 70)

    # Exit with error code if any failures
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
