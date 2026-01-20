#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schema Parity Validation Script

Compares Odoo PostgreSQL schema with Supabase shadow schema to detect drift.
Exits with non-zero code if critical drift is detected.

Usage:
    python odoo-schema-mirror/validate_parity.py

Environment Variables:
    ODOO_DB_*           Odoo PostgreSQL connection
    SUPABASE_DB_URL     Supabase PostgreSQL connection
    SUPABASE_DB_SCHEMA  Target schema (default: odoo_shadow)
"""

import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    logger.error("psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)


# =============================================================================
# Configuration
# =============================================================================

def get_config() -> dict:
    """Load configuration from environment variables."""
    return {
        # Odoo
        "odoo_host": os.environ.get("ODOO_DB_HOST"),
        "odoo_port": int(os.environ.get("ODOO_DB_PORT", "5432")),
        "odoo_database": os.environ.get("ODOO_DB_NAME"),
        "odoo_user": os.environ.get("ODOO_DB_USER"),
        "odoo_password": os.environ.get("ODOO_DB_PASSWORD"),
        # Supabase
        "supabase_url": os.environ.get("SUPABASE_DB_URL"),
        "supabase_schema": os.environ.get("SUPABASE_DB_SCHEMA", "odoo_shadow"),
        "table_prefix": os.environ.get("ODOO_SCHEMA_TABLE_PREFIX", "odoo_shadow_"),
        # Output
        "output_dir": os.environ.get("SCHEMA_ARTIFACT_DIR", "./odoo-schema-mirror/artifacts"),
    }


# =============================================================================
# Drift Detection
# =============================================================================

@dataclass
class DriftReport:
    """Report of schema drift between Odoo and Supabase."""
    missing_tables: list[str]
    extra_tables: list[str]
    missing_columns: dict[str, list[str]]
    type_mismatches: list[dict]
    critical_drift: bool

    def to_dict(self) -> dict:
        return {
            "missing_tables": self.missing_tables,
            "extra_tables": self.extra_tables,
            "missing_columns": self.missing_columns,
            "type_mismatches": self.type_mismatches,
            "critical_drift": self.critical_drift,
        }


class ParityValidator:
    """Validates schema parity between Odoo and Supabase."""

    def __init__(self, config: dict):
        self.config = config
        self.odoo_conn = None
        self.supabase_conn = None

    def connect(self):
        """Connect to both databases."""
        logger.info("Connecting to Odoo PostgreSQL...")
        self.odoo_conn = psycopg2.connect(
            host=self.config["odoo_host"],
            port=self.config["odoo_port"],
            database=self.config["odoo_database"],
            user=self.config["odoo_user"],
            password=self.config["odoo_password"],
            cursor_factory=RealDictCursor,
        )
        logger.info("Connected to Odoo")

        logger.info("Connecting to Supabase PostgreSQL...")
        self.supabase_conn = psycopg2.connect(
            self.config["supabase_url"],
            cursor_factory=RealDictCursor,
        )
        logger.info("Connected to Supabase")

    def close(self):
        """Close database connections."""
        if self.odoo_conn:
            self.odoo_conn.close()
        if self.supabase_conn:
            self.supabase_conn.close()

    def _get_odoo_tables(self) -> set[str]:
        """Get table names from Odoo."""
        with self.odoo_conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
            """)
            return {row["table_name"] for row in cur.fetchall()}

    def _get_supabase_tables(self) -> set[str]:
        """Get table names from Supabase shadow schema."""
        prefix = self.config["table_prefix"]
        schema = self.config["supabase_schema"]

        with self.supabase_conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                  AND table_type = 'BASE TABLE'
            """, (schema,))

            # Strip prefix to get original names
            tables = set()
            for row in cur.fetchall():
                name = row["table_name"]
                if name.startswith(prefix):
                    tables.add(name[len(prefix):])
                else:
                    tables.add(name)
            return tables

    def _get_odoo_columns(self, table: str) -> dict[str, str]:
        """Get columns and types for an Odoo table."""
        with self.odoo_conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                ORDER BY ordinal_position
            """, (table,))
            return {row["column_name"]: row["data_type"] for row in cur.fetchall()}

    def _get_supabase_columns(self, table: str) -> dict[str, str]:
        """Get columns and types for a Supabase shadow table."""
        prefix = self.config["table_prefix"]
        schema = self.config["supabase_schema"]
        shadow_name = f"{prefix}{table}"

        with self.supabase_conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = %s
                  AND table_name = %s
                ORDER BY ordinal_position
            """, (schema, shadow_name))
            return {row["column_name"]: row["data_type"] for row in cur.fetchall()}

    def validate(self) -> DriftReport:
        """Perform parity validation."""
        logger.info("Validating schema parity...")

        # Compare tables
        odoo_tables = self._get_odoo_tables()
        supabase_tables = self._get_supabase_tables()

        missing_tables = sorted(odoo_tables - supabase_tables)
        extra_tables = sorted(supabase_tables - odoo_tables)

        # Compare columns for common tables
        common_tables = odoo_tables & supabase_tables
        missing_columns = {}
        type_mismatches = []

        for table in sorted(common_tables):
            odoo_cols = self._get_odoo_columns(table)
            supa_cols = self._get_supabase_columns(table)

            # Skip shadow tracking columns
            supa_cols = {k: v for k, v in supa_cols.items() if not k.startswith("_")}

            # Find missing columns
            missing = set(odoo_cols.keys()) - set(supa_cols.keys())
            if missing:
                missing_columns[table] = sorted(missing)

            # Find type mismatches (basic comparison)
            for col in set(odoo_cols.keys()) & set(supa_cols.keys()):
                odoo_type = odoo_cols[col]
                supa_type = supa_cols[col]
                # Normalize types for comparison
                if not self._types_compatible(odoo_type, supa_type):
                    type_mismatches.append({
                        "table": table,
                        "column": col,
                        "odoo_type": odoo_type,
                        "supabase_type": supa_type,
                    })

        # Determine if drift is critical
        critical_drift = len(missing_tables) > 10 or len(type_mismatches) > 20

        return DriftReport(
            missing_tables=missing_tables,
            extra_tables=extra_tables,
            missing_columns=missing_columns,
            type_mismatches=type_mismatches,
            critical_drift=critical_drift,
        )

    def _types_compatible(self, odoo_type: str, supa_type: str) -> bool:
        """Check if two types are compatible."""
        # Normalize common equivalents
        equivalents = {
            ("integer", "bigint"),
            ("character varying", "text"),
            ("timestamp without time zone", "timestamp with time zone"),
        }
        if odoo_type == supa_type:
            return True
        if (odoo_type, supa_type) in equivalents or (supa_type, odoo_type) in equivalents:
            return True
        return False

    def save_report(self, report: DriftReport) -> str:
        """Save drift report to JSON."""
        path = Path(self.config["output_dir"]) / "parity_report.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(report.to_dict(), f, indent=2)

        logger.info(f"Report saved to {path}")
        return str(path)


# =============================================================================
# Main
# =============================================================================

def main():
    """Main entry point."""
    logger.info("=" * 70)
    logger.info("Schema Parity Validation")
    logger.info("=" * 70)

    config = get_config()

    # Check if we have enough config to run
    if not config.get("odoo_host") or not config.get("supabase_url"):
        logger.warning("Missing database credentials, skipping parity check")
        logger.info("Set ODOO_DB_* and SUPABASE_DB_URL to enable validation")
        sys.exit(0)

    validator = ParityValidator(config)
    try:
        validator.connect()
        report = validator.validate()
        report_path = validator.save_report(report)

        # Print summary
        logger.info("=" * 70)
        logger.info("Validation Summary")
        logger.info("=" * 70)
        logger.info(f"  Missing tables: {len(report.missing_tables)}")
        logger.info(f"  Extra tables: {len(report.extra_tables)}")
        logger.info(f"  Tables with missing columns: {len(report.missing_columns)}")
        logger.info(f"  Type mismatches: {len(report.type_mismatches)}")
        logger.info(f"  Critical drift: {report.critical_drift}")
        logger.info(f"  Report: {report_path}")
        logger.info("=" * 70)

        if report.missing_tables[:10]:
            logger.info("Missing tables (first 10):")
            for t in report.missing_tables[:10]:
                logger.info(f"  - {t}")

        if report.type_mismatches[:5]:
            logger.info("Type mismatches (first 5):")
            for m in report.type_mismatches[:5]:
                logger.info(f"  - {m['table']}.{m['column']}: {m['odoo_type']} vs {m['supabase_type']}")

        if report.critical_drift:
            logger.error("CRITICAL: Schema drift exceeds threshold!")
            sys.exit(1)

    finally:
        validator.close()


if __name__ == "__main__":
    main()
