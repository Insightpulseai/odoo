#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2026 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
"""
Sync script: Odoo ipai.sample.metric → Supabase ipai.ipai_sample_metrics

This script pulls metrics from Odoo via XML-RPC and upserts them into
Supabase for consumption by Fluent dashboards and external analytics.

Usage:
    # Set environment variables
    export ODOO_URL="https://erp.insightpulseai.net"
    export ODOO_DB="odoo_core"
    export ODOO_USER="api-user@example.com"
    export ODOO_PASSWORD="your-password"
    export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
    export SUPABASE_SERVICE_KEY="your-service-role-key"

    # Run sync
    python scripts/sync_ipai_sample_metrics_to_supabase.py

    # Or with options
    python scripts/sync_ipai_sample_metrics_to_supabase.py --limit 1000 --since 2026-01-01

Environment Variables:
    ODOO_URL            Odoo server URL (required)
    ODOO_DB             Odoo database name (required)
    ODOO_USER           Odoo API user email (required)
    ODOO_PASSWORD       Odoo API user password (required)
    SUPABASE_URL        Supabase project URL (required)
    SUPABASE_SERVICE_KEY Supabase service role key (required)
"""

import argparse
import logging
import os
import sys
import time
import xmlrpc.client
from datetime import datetime, timedelta
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


def get_env_var(name: str, required: bool = True) -> str | None:
    """Get environment variable with optional requirement check."""
    value = os.environ.get(name)
    if required and not value:
        logger.error(f"Missing required environment variable: {name}")
        sys.exit(1)
    return value


def connect_odoo() -> tuple[int, Any]:
    """Connect to Odoo via XML-RPC and return uid and models proxy."""
    odoo_url = get_env_var("ODOO_URL")
    odoo_db = get_env_var("ODOO_DB")
    odoo_user = get_env_var("ODOO_USER")
    odoo_password = get_env_var("ODOO_PASSWORD")

    logger.info(f"Connecting to Odoo at {odoo_url}...")

    try:
        common = xmlrpc.client.ServerProxy(
            f"{odoo_url}/xmlrpc/2/common",
            allow_none=True,
        )
        uid = common.authenticate(odoo_db, odoo_user, odoo_password, {})
        if not uid:
            logger.error("Odoo authentication failed")
            sys.exit(1)

        models = xmlrpc.client.ServerProxy(
            f"{odoo_url}/xmlrpc/2/object",
            allow_none=True,
        )
        logger.info(f"Connected to Odoo as uid={uid}")
        return uid, models, odoo_db, odoo_password
    except Exception as e:
        logger.error(f"Failed to connect to Odoo: {e}")
        sys.exit(1)


def connect_supabase() -> Client:
    """Connect to Supabase and return client."""
    supabase_url = get_env_var("SUPABASE_URL")
    supabase_key = get_env_var("SUPABASE_SERVICE_KEY")

    logger.info(f"Connecting to Supabase at {supabase_url}...")

    try:
        client = create_client(supabase_url, supabase_key)
        logger.info("Connected to Supabase")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        sys.exit(1)


def fetch_odoo_metrics(
    uid: int,
    models: Any,
    db: str,
    password: str,
    limit: int = 5000,
    since_date: str | None = None,
) -> list[dict]:
    """Fetch metrics from Odoo via XML-RPC."""
    logger.info(f"Fetching metrics from Odoo (limit={limit}, since={since_date})...")

    try:
        payload = models.execute_kw(
            db,
            uid,
            password,
            "ipai.sample.metric",
            "export_to_supabase_payload",
            [],
            {"limit": limit, "since_date": since_date},
        )
        logger.info(f"Fetched {len(payload)} metrics from Odoo")
        return payload
    except Exception as e:
        logger.error(f"Failed to fetch metrics from Odoo: {e}")
        sys.exit(1)


def upsert_to_supabase(client: Client, payload: list[dict]) -> int:
    """Upsert metrics to Supabase table."""
    if not payload:
        logger.info("No metrics to upsert")
        return 0

    logger.info(f"Upserting {len(payload)} metrics to Supabase...")

    try:
        # Upsert using odoo_id as conflict key
        response = (
            client.schema("ipai")
            .table("ipai_sample_metrics")
            .upsert(payload, on_conflict="odoo_id")
            .execute()
        )

        count = len(response.data) if response.data else 0
        logger.info(f"Upserted {count} metrics to Supabase")
        return count
    except Exception as e:
        logger.error(f"Failed to upsert to Supabase: {e}")
        sys.exit(1)


def get_sync_stats(
    uid: int,
    models: Any,
    db: str,
    password: str,
) -> dict:
    """Get sync statistics from Odoo."""
    try:
        return models.execute_kw(
            db,
            uid,
            password,
            "ipai.sample.metric",
            "get_sync_stats",
            [],
            {},
        )
    except Exception as e:
        logger.warning(f"Could not get sync stats: {e}")
        return {}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sync Odoo ipai.sample.metric to Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5000,
        help="Maximum number of records to sync (default: 5000)",
    )
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Only sync records modified since this date (ISO format: YYYY-MM-DD)",
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
    logger.info("=" * 60)
    logger.info("IPAI Sample Metrics Sync: Odoo → Supabase")
    logger.info("=" * 60)

    # Connect to both systems
    uid, models, db, password = connect_odoo()
    supabase = connect_supabase()

    # Get pre-sync stats
    stats = get_sync_stats(uid, models, db, password)
    if stats:
        logger.info(
            f"Odoo stats: total={stats.get('total', '?')}, "
            f"active={stats.get('active', '?')}, "
            f"alerts={stats.get('alerts', '?')}"
        )

    # Fetch from Odoo
    payload = fetch_odoo_metrics(
        uid,
        models,
        db,
        password,
        limit=args.limit,
        since_date=args.since,
    )

    # Upsert to Supabase
    if args.dry_run:
        logger.info(f"DRY RUN: Would upsert {len(payload)} metrics")
        upserted = 0
    else:
        upserted = upsert_to_supabase(supabase, payload)

    # Summary
    elapsed = time.time() - start_time
    logger.info("=" * 60)
    logger.info("Sync complete")
    logger.info(f"  Fetched:  {len(payload)} metrics from Odoo")
    logger.info(f"  Upserted: {upserted} metrics to Supabase")
    logger.info(f"  Duration: {elapsed:.2f}s")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
