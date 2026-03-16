#!/usr/bin/env python3
"""Generate Supabase shadow DDL from Odoo canonical model index.

This script reads ODOO_MODEL_INDEX.json and generates:
1. Shadow schema creation SQL
2. Shadow table DDL for all stored models
3. Tracking columns for incremental sync

Usage:
    python scripts/generate_shadow_ddl.py [--output PATH] [--filter PREFIX]

Examples:
    python scripts/generate_shadow_ddl.py
    python scripts/generate_shadow_ddl.py --filter ipai
    python scripts/generate_shadow_ddl.py --output /tmp/shadow.sql
"""

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
MODEL_INDEX_PATH = ROOT / "docs" / "data-model" / "ODOO_MODEL_INDEX.json"
DEFAULT_OUTPUT_PATH = ROOT / "docs" / "data-model" / "ODOO_SHADOW_SCHEMA.sql"


def odoo_to_pg_type(field: dict[str, Any]) -> str:
    """Map Odoo field type to PostgreSQL type."""
    ftype = (field.get("type") or "").lower()

    type_map = {
        "char": "text",
        "selection": "text",
        "text": "text",
        "html": "text",
        "integer": "bigint",
        "many2one": "bigint",
        "float": "double precision",
        "float_factor": "double precision",
        "boolean": "boolean",
        "bool": "boolean",
        "date": "date",
        "datetime": "timestamptz",
        "datetime64": "timestamptz",
        "binary": "bytea",
        "monetary": "numeric(16, 2)",
        "json": "jsonb",
        "jsonb": "jsonb",
        "serialized": "jsonb",
    }

    return type_map.get(ftype, "jsonb")


def is_stored_column(field: dict[str, Any]) -> bool:
    """Check if field should be a physical column in shadow table."""
    if field.get("store") is False:
        return False

    ftype = (field.get("type") or "").lower()

    # Relational containers are not stored as columns
    if ftype in ("one2many", "many2many"):
        return False

    return True


def sanitize_identifier(name: str) -> str:
    """Sanitize SQL identifier (table/column name)."""
    # Replace dots with underscores, remove special chars
    sanitized = name.replace(".", "_").replace("-", "_")
    # Ensure it starts with letter or underscore
    if sanitized and sanitized[0].isdigit():
        sanitized = "_" + sanitized
    return sanitized


def generate_table_ddl(model: dict[str, Any]) -> str | None:
    """Generate CREATE TABLE DDL for one Odoo model."""
    model_name = model.get("name", "")
    table_name = model.get("table")

    if not table_name:
        logger.debug(f"Skipping {model_name}: no table (abstract/transient)")
        return None

    shadow_table = f"odoo_shadow_{sanitize_identifier(table_name)}"
    fields = [f for f in model.get("fields", []) if is_stored_column(f)]

    if not fields:
        logger.debug(f"Skipping {model_name}: no stored fields")
        return None

    lines = []
    lines.append(f"-- Model: {model_name}")
    lines.append(f"-- Module: {model.get('module', 'unknown')}")
    lines.append(f"CREATE TABLE IF NOT EXISTS {shadow_table} (")

    # Primary key
    lines.append("    id bigint PRIMARY KEY,")

    # Model fields
    for field in fields:
        name = field.get("name", "")
        if name == "id":
            continue

        col_name = sanitize_identifier(name)
        pg_type = odoo_to_pg_type(field)

        # Add comment for computed fields
        comment = ""
        if field.get("compute"):
            comment = "  -- computed, stored"

        lines.append(f"    {col_name} {pg_type},{comment}")

    # Tracking columns
    lines.append("    -- Shadow tracking columns")
    lines.append("    _odoo_write_date timestamptz,")
    lines.append("    _synced_at timestamptz DEFAULT now(),")
    lines.append("    _sync_hash text")
    lines.append(");")

    # Index on write_date for incremental sync
    lines.append(f"CREATE INDEX IF NOT EXISTS idx_{shadow_table}_write_date")
    lines.append(f"    ON {shadow_table} (_odoo_write_date DESC);")
    lines.append("")

    return "\n".join(lines)


def generate_shadow_ddl(
    model_index_path: Path,
    output_path: Path,
    filter_prefix: str | None = None,
) -> dict[str, Any]:
    """Generate complete shadow DDL from model index."""
    if not model_index_path.exists():
        raise FileNotFoundError(f"Model index not found: {model_index_path}")

    with model_index_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    models = data.get("models", [])
    logger.info(f"Loaded {len(models)} models from {model_index_path}")

    # Filter by prefix if specified
    if filter_prefix:
        models = [
            m
            for m in models
            if m.get("name", "").startswith(filter_prefix)
            or m.get("module", "").startswith(filter_prefix)
        ]
        logger.info(f"Filtered to {len(models)} models with prefix '{filter_prefix}'")

    # Generate header
    ddl_parts = []
    ddl_parts.append(
        "-- ============================================================================="
    )
    ddl_parts.append(
        "-- ODOO SHADOW SCHEMA - Auto-generated from ODOO_MODEL_INDEX.json"
    )
    ddl_parts.append(f"-- Generated: {datetime.now().isoformat()}")
    ddl_parts.append(f"-- Source: {model_index_path.name}")
    ddl_parts.append(f"-- Models: {len(models)}")
    if filter_prefix:
        ddl_parts.append(f"-- Filter: {filter_prefix}*")
    ddl_parts.append("-- ")
    ddl_parts.append("-- DO NOT EDIT MANUALLY - Regenerate via:")
    ddl_parts.append("--   python scripts/generate_shadow_ddl.py")
    ddl_parts.append(
        "-- ============================================================================="
    )
    ddl_parts.append("")

    # Schema creation
    ddl_parts.append("-- Create shadow schema if not exists")
    ddl_parts.append("CREATE SCHEMA IF NOT EXISTS odoo_shadow;")
    ddl_parts.append("")
    ddl_parts.append("-- Set search path for this session")
    ddl_parts.append("SET search_path TO public;")
    ddl_parts.append("")

    # Metadata table
    ddl_parts.append(
        "-- ============================================================================="
    )
    ddl_parts.append("-- Shadow Metadata Registry")
    ddl_parts.append(
        "-- ============================================================================="
    )
    ddl_parts.append("")
    ddl_parts.append("CREATE TABLE IF NOT EXISTS odoo_shadow_meta (")
    ddl_parts.append("    id bigserial PRIMARY KEY,")
    ddl_parts.append("    table_name text NOT NULL UNIQUE,")
    ddl_parts.append("    odoo_model text NOT NULL,")
    ddl_parts.append("    odoo_module text,")
    ddl_parts.append("    field_count integer,")
    ddl_parts.append("    last_sync_at timestamptz,")
    ddl_parts.append("    row_count bigint,")
    ddl_parts.append("    created_at timestamptz DEFAULT now(),")
    ddl_parts.append("    updated_at timestamptz DEFAULT now()")
    ddl_parts.append(");")
    ddl_parts.append("")

    # Generate tables
    ddl_parts.append(
        "-- ============================================================================="
    )
    ddl_parts.append("-- Shadow Tables")
    ddl_parts.append(
        "-- ============================================================================="
    )
    ddl_parts.append("")

    stats = {
        "total_models": len(models),
        "tables_generated": 0,
        "tables_skipped": 0,
        "total_fields": 0,
    }

    meta_inserts = []

    for model in sorted(models, key=lambda m: m.get("name", "")):
        table_ddl = generate_table_ddl(model)
        if table_ddl:
            ddl_parts.append(table_ddl)
            stats["tables_generated"] += 1

            # Count stored fields
            stored_fields = [f for f in model.get("fields", []) if is_stored_column(f)]
            stats["total_fields"] += len(stored_fields)

            # Prepare metadata insert
            table_name = model.get("table", "")
            shadow_table = f"odoo_shadow_{sanitize_identifier(table_name)}"
            meta_inserts.append(
                f"    ('{shadow_table}', '{model.get('name', '')}', "
                f"'{model.get('module', '')}', {len(stored_fields)})"
            )
        else:
            stats["tables_skipped"] += 1

    # Insert metadata
    if meta_inserts:
        ddl_parts.append(
            "-- ============================================================================="
        )
        ddl_parts.append("-- Populate Shadow Metadata")
        ddl_parts.append(
            "-- ============================================================================="
        )
        ddl_parts.append("")
        ddl_parts.append(
            "INSERT INTO odoo_shadow_meta (table_name, odoo_model, odoo_module, field_count)"
        )
        ddl_parts.append("VALUES")
        ddl_parts.append(",\n".join(meta_inserts))
        ddl_parts.append("ON CONFLICT (table_name) DO UPDATE SET")
        ddl_parts.append("    odoo_model = EXCLUDED.odoo_model,")
        ddl_parts.append("    odoo_module = EXCLUDED.odoo_module,")
        ddl_parts.append("    field_count = EXCLUDED.field_count,")
        ddl_parts.append("    updated_at = now();")
        ddl_parts.append("")

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(ddl_parts), encoding="utf-8")

    logger.info(f"Generated {stats['tables_generated']} shadow tables")
    logger.info(f"Skipped {stats['tables_skipped']} models (no table/fields)")
    logger.info(f"Total fields: {stats['total_fields']}")
    logger.info(f"Output: {output_path}")

    return stats


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Supabase shadow DDL from Odoo model index"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output SQL file (default: {DEFAULT_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--filter",
        "-f",
        type=str,
        default=None,
        help="Filter models by prefix (e.g., 'ipai' for IPAI modules only)",
    )
    parser.add_argument(
        "--model-index",
        type=Path,
        default=MODEL_INDEX_PATH,
        help=f"Path to ODOO_MODEL_INDEX.json (default: {MODEL_INDEX_PATH})",
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

    try:
        stats = generate_shadow_ddl(
            model_index_path=args.model_index,
            output_path=args.output,
            filter_prefix=args.filter,
        )
        return 0
    except Exception as e:
        logger.error(f"Failed to generate shadow DDL: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
