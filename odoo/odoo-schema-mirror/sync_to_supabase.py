#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase Schema Sync Script

Reads the exported Odoo schema JSON and generates idempotent SQL migrations
to create/update shadow tables in Supabase PostgreSQL.

Usage:
    python odoo-schema-mirror/sync_to_supabase.py

Environment Variables:
    SUPABASE_DB_URL           Full postgres:// connection string
    SUPABASE_DB_SCHEMA        Target schema (default: odoo_shadow)
    ODOO_SCHEMA_TABLE_PREFIX  Prefix for shadow tables (default: odoo_shadow_)
    ODOO_SCHEMA_ALLOW_DROPS   Allow DROP statements (default: false)
"""

import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
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
        "supabase_url": os.environ.get("SUPABASE_DB_URL"),
        "target_schema": os.environ.get("SUPABASE_DB_SCHEMA", "odoo_shadow"),
        "table_prefix": os.environ.get("ODOO_SCHEMA_TABLE_PREFIX", "odoo_shadow_"),
        "allow_drops": os.environ.get("ODOO_SCHEMA_ALLOW_DROPS", "false").lower() == "true",
        "artifact_dir": os.environ.get("SCHEMA_ARTIFACT_DIR", "./odoo-schema-mirror/artifacts"),
        "migration_dir": "./supabase/migrations/odoo_mirror",
    }


def validate_config(config: dict) -> bool:
    """Validate required configuration."""
    if not config.get("supabase_url"):
        logger.error("Missing required environment variable: SUPABASE_DB_URL")
        return False
    return True


# =============================================================================
# Type Mapping: Odoo PostgreSQL -> Supabase PostgreSQL
# =============================================================================

TYPE_MAPPING = {
    # Standard types (usually passthrough)
    "integer": "bigint",
    "bigint": "bigint",
    "smallint": "smallint",
    "boolean": "boolean",
    "text": "text",
    "character varying": "text",
    "varchar": "text",
    "numeric": "numeric",
    "real": "real",
    "double precision": "double precision",
    "date": "date",
    "timestamp without time zone": "timestamptz",
    "timestamp with time zone": "timestamptz",
    "bytea": "bytea",
    "json": "jsonb",
    "jsonb": "jsonb",
    "uuid": "uuid",
    # Array types
    "ARRAY": "text[]",
    "integer[]": "bigint[]",
    "text[]": "text[]",
}


def map_column_type(odoo_type: str, udt_name: str = None, char_length: int = None) -> str:
    """Map Odoo column type to Supabase type."""
    # Handle arrays
    if odoo_type == "ARRAY" and udt_name:
        base_type = udt_name.lstrip("_")
        mapped_base = TYPE_MAPPING.get(base_type, "text")
        return f"{mapped_base}[]"

    # Direct mapping
    if odoo_type in TYPE_MAPPING:
        return TYPE_MAPPING[odoo_type]

    # Fallback to text
    logger.warning(f"Unknown type '{odoo_type}', mapping to text")
    return "text"


# =============================================================================
# Migration Generator
# =============================================================================

class MigrationGenerator:
    """Generates SQL migrations from Odoo schema."""

    def __init__(self, config: dict):
        self.config = config
        self.conn = None
        self.existing_tables = set()
        self.existing_columns = {}

    def connect(self):
        """Connect to Supabase PostgreSQL."""
        logger.info("Connecting to Supabase PostgreSQL...")
        self.conn = psycopg2.connect(
            self.config["supabase_url"],
            cursor_factory=RealDictCursor,
        )
        logger.info("Connected successfully")
        self._load_existing_schema()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def _load_existing_schema(self):
        """Load existing schema information from Supabase."""
        schema = self.config["target_schema"]

        with self.conn.cursor() as cur:
            # Get existing tables
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
            """, (schema,))
            self.existing_tables = {row["table_name"] for row in cur.fetchall()}

            # Get existing columns
            cur.execute("""
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = %s
            """, (schema,))
            for row in cur.fetchall():
                table = row["table_name"]
                if table not in self.existing_columns:
                    self.existing_columns[table] = {}
                self.existing_columns[table][row["column_name"]] = {
                    "data_type": row["data_type"],
                    "is_nullable": row["is_nullable"],
                }

        logger.info(f"Found {len(self.existing_tables)} existing tables in {schema}")

    def _shadow_table_name(self, odoo_table: str) -> str:
        """Generate shadow table name from Odoo table name."""
        prefix = self.config["table_prefix"]
        # Remove any existing prefix to avoid double-prefixing
        if odoo_table.startswith(prefix):
            return odoo_table
        return f"{prefix}{odoo_table}"

    def _generate_create_table(self, table_name: str, table_info: dict) -> str:
        """Generate CREATE TABLE statement."""
        shadow_name = self._shadow_table_name(table_name)
        schema = self.config["target_schema"]
        columns = table_info.get("columns", [])
        pk_columns = table_info.get("primary_key", [])

        lines = [f'CREATE TABLE IF NOT EXISTS {schema}.{shadow_name} (']

        col_defs = []
        for col in columns:
            col_name = col["column_name"]
            col_type = map_column_type(
                col["data_type"],
                col.get("udt_name"),
                col.get("character_maximum_length"),
            )
            nullable = "" if col["is_nullable"] == "YES" else " NOT NULL"

            # Add primary key inline if single column
            pk_suffix = ""
            if len(pk_columns) == 1 and col_name in pk_columns:
                pk_suffix = " PRIMARY KEY"

            col_defs.append(f"    {col_name} {col_type}{nullable}{pk_suffix}")

        # Add shadow tracking columns
        col_defs.extend([
            "    _odoo_write_date timestamptz",
            "    _synced_at timestamptz DEFAULT now()",
            "    _sync_hash text",
        ])

        # Add composite primary key if needed
        if len(pk_columns) > 1:
            col_defs.append(f"    PRIMARY KEY ({', '.join(pk_columns)})")

        lines.append(",\n".join(col_defs))
        lines.append(");")

        # Add index on write_date for incremental sync
        lines.append(f"""
CREATE INDEX IF NOT EXISTS idx_{shadow_name}_write_date
    ON {schema}.{shadow_name} (_odoo_write_date DESC);""")

        return "\n".join(lines)

    def _generate_alter_table(self, table_name: str, table_info: dict) -> list[str]:
        """Generate ALTER TABLE statements for new columns."""
        shadow_name = self._shadow_table_name(table_name)
        schema = self.config["target_schema"]
        columns = table_info.get("columns", [])
        existing = self.existing_columns.get(shadow_name, {})

        statements = []
        for col in columns:
            col_name = col["column_name"]
            if col_name not in existing:
                col_type = map_column_type(
                    col["data_type"],
                    col.get("udt_name"),
                    col.get("character_maximum_length"),
                )
                statements.append(
                    f"ALTER TABLE {schema}.{shadow_name} "
                    f"ADD COLUMN IF NOT EXISTS {col_name} {col_type};"
                )

        return statements

    def generate_migration(self, odoo_schema: dict) -> str:
        """Generate complete migration SQL."""
        tables = odoo_schema.get("tables", {})
        schema = self.config["target_schema"]

        lines = [
            "-- =============================================================================",
            f"-- Odoo Shadow Schema Migration",
            f"-- Generated: {datetime.now(timezone.utc).isoformat()}",
            f"-- Source: {odoo_schema.get('metadata', {}).get('source', 'unknown')}",
            f"-- Tables: {len(tables)}",
            "-- =============================================================================",
            "",
            f"-- Create schema if not exists",
            f"CREATE SCHEMA IF NOT EXISTS {schema};",
            "",
        ]

        new_tables = 0
        altered_tables = 0

        for table_name, table_info in sorted(tables.items()):
            shadow_name = self._shadow_table_name(table_name)

            if shadow_name not in self.existing_tables:
                # New table
                lines.append(f"-- New table: {table_name}")
                lines.append(self._generate_create_table(table_name, table_info))
                lines.append("")
                new_tables += 1
            else:
                # Existing table - check for new columns
                alter_stmts = self._generate_alter_table(table_name, table_info)
                if alter_stmts:
                    lines.append(f"-- Alter table: {table_name}")
                    lines.extend(alter_stmts)
                    lines.append("")
                    altered_tables += 1

        # Add metadata update
        lines.extend([
            "-- Update migration metadata",
            f"INSERT INTO {schema}.odoo_shadow_meta (table_name, odoo_model, field_count, updated_at)",
            "SELECT",
            "    t.table_name,",
            "    REPLACE(REPLACE(t.table_name, 'odoo_shadow_', ''), '_', '.'),",
            "    (SELECT COUNT(*) FROM information_schema.columns c WHERE c.table_name = t.table_name AND c.table_schema = %s),",
            "    now()",
            f"FROM information_schema.tables t",
            f"WHERE t.table_schema = '{schema}'",
            f"  AND t.table_name LIKE 'odoo_shadow_%'",
            "ON CONFLICT (table_name) DO UPDATE SET",
            "    field_count = EXCLUDED.field_count,",
            "    updated_at = now();",
        ])

        logger.info(f"Generated migration: {new_tables} new tables, {altered_tables} altered tables")
        return "\n".join(lines)

    def save_migration(self, sql: str) -> str:
        """Save migration to file."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_odoo_schema_sync.sql"
        path = Path(self.config["migration_dir"]) / filename

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(sql)

        logger.info(f"Migration saved to {path}")
        return str(path)


# =============================================================================
# Main
# =============================================================================

def main():
    """Main entry point."""
    logger.info("=" * 70)
    logger.info("Supabase Schema Sync")
    logger.info("=" * 70)

    config = get_config()
    if not validate_config(config):
        sys.exit(1)

    # Load Odoo schema artifact
    schema_path = Path(config["artifact_dir"]) / "odoo_schema.json"
    if not schema_path.exists():
        logger.error(f"Schema artifact not found: {schema_path}")
        logger.error("Run export_odoo_schema.py first")
        sys.exit(1)

    with open(schema_path) as f:
        odoo_schema = json.load(f)

    logger.info(f"Loaded schema with {len(odoo_schema.get('tables', {}))} tables")

    # Generate migration
    generator = MigrationGenerator(config)
    try:
        generator.connect()
        migration_sql = generator.generate_migration(odoo_schema)
        migration_path = generator.save_migration(migration_sql)

        # Print summary
        logger.info("=" * 70)
        logger.info("Sync Summary")
        logger.info("=" * 70)
        logger.info(f"  Migration file: {migration_path}")
        logger.info(f"  Target schema: {config['target_schema']}")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Review the migration file")
        logger.info("  2. Run: supabase db push")
        logger.info("     OR: psql $SUPABASE_DB_URL -f <migration_file>")
        logger.info("=" * 70)

    finally:
        generator.close()


if __name__ == "__main__":
    main()
