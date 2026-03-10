#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DBML Generation Script

Connects to Supabase PostgreSQL and generates DBML (Database Markup Language)
for visualization in dbdiagram.io and ERD rendering tools.

Usage:
    python odoo-schema-mirror/generate_dbml.py

Environment Variables:
    SUPABASE_DB_URL     Full postgres:// connection string
    SUPABASE_DB_SCHEMA  Schema to export (default: odoo_shadow)
    DBML_OUTPUT_DIR     Output directory for DBML files
"""

import logging
import os
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
        "schema": os.environ.get("SUPABASE_DB_SCHEMA", "odoo_shadow"),
        "output_dir": os.environ.get("DBML_OUTPUT_DIR", "./docs/dbml"),
    }


def validate_config(config: dict) -> bool:
    """Validate required configuration."""
    if not config.get("supabase_url"):
        logger.error("Missing required environment variable: SUPABASE_DB_URL")
        return False
    return True


# =============================================================================
# DBML Type Mapping
# =============================================================================

DBML_TYPE_MAP = {
    "bigint": "bigint",
    "integer": "int",
    "smallint": "smallint",
    "boolean": "boolean",
    "text": "text",
    "character varying": "varchar",
    "numeric": "numeric",
    "real": "float",
    "double precision": "float",
    "date": "date",
    "timestamp without time zone": "timestamp",
    "timestamp with time zone": "timestamptz",
    "bytea": "bytea",
    "json": "json",
    "jsonb": "jsonb",
    "uuid": "uuid",
    "ARRAY": "array",
}


def to_dbml_type(pg_type: str) -> str:
    """Convert PostgreSQL type to DBML type."""
    return DBML_TYPE_MAP.get(pg_type, pg_type)


# =============================================================================
# DBML Generator
# =============================================================================

class DBMLGenerator:
    """Generates DBML from Supabase PostgreSQL schema."""

    def __init__(self, config: dict):
        self.config = config
        self.conn = None

    def connect(self):
        """Connect to Supabase PostgreSQL."""
        logger.info("Connecting to Supabase PostgreSQL...")
        self.conn = psycopg2.connect(
            self.config["supabase_url"],
            cursor_factory=RealDictCursor,
        )
        logger.info("Connected successfully")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def _get_tables(self) -> list[dict]:
        """Get all tables in the schema."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT
                    t.table_name,
                    pg_catalog.obj_description(pgc.oid, 'pg_class') as table_comment
                FROM information_schema.tables t
                LEFT JOIN pg_catalog.pg_class pgc ON pgc.relname = t.table_name
                WHERE t.table_schema = %s
                  AND t.table_type = 'BASE TABLE'
                ORDER BY t.table_name
            """, (self.config["schema"],))
            return list(cur.fetchall())

    def _get_columns(self, table_name: str) -> list[dict]:
        """Get columns for a table."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    c.column_default,
                    c.character_maximum_length,
                    pg_catalog.col_description(
                        (SELECT oid FROM pg_catalog.pg_class WHERE relname = %s),
                        c.ordinal_position
                    ) as column_comment
                FROM information_schema.columns c
                WHERE c.table_schema = %s AND c.table_name = %s
                ORDER BY c.ordinal_position
            """, (table_name, self.config["schema"], table_name))
            return list(cur.fetchall())

    def _get_primary_keys(self, table_name: str) -> list[str]:
        """Get primary key columns for a table."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'PRIMARY KEY'
                  AND tc.table_schema = %s
                  AND tc.table_name = %s
                ORDER BY kcu.ordinal_position
            """, (self.config["schema"], table_name))
            return [row["column_name"] for row in cur.fetchall()]

    def _get_foreign_keys(self) -> list[dict]:
        """Get all foreign keys in the schema."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table,
                    ccu.column_name AS foreign_column
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = %s
            """, (self.config["schema"],))
            return list(cur.fetchall())

    def _get_indexes(self, table_name: str) -> list[dict]:
        """Get indexes for a table."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT
                    i.relname as index_name,
                    array_agg(a.attname ORDER BY a.attnum) as columns,
                    ix.indisunique as is_unique
                FROM pg_class t
                JOIN pg_index ix ON t.oid = ix.indrelid
                JOIN pg_class i ON i.oid = ix.indexrelid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                JOIN pg_namespace n ON n.oid = t.relnamespace
                WHERE n.nspname = %s
                  AND t.relname = %s
                  AND NOT ix.indisprimary
                GROUP BY i.relname, ix.indisunique
            """, (self.config["schema"], table_name))
            return list(cur.fetchall())

    def _escape_dbml(self, text: str) -> str:
        """Escape special characters for DBML."""
        if not text:
            return ""
        return text.replace('"', '\\"').replace('\n', ' ')

    def generate(self) -> str:
        """Generate DBML content."""
        logger.info(f"Generating DBML for schema: {self.config['schema']}")

        tables = self._get_tables()
        foreign_keys = self._get_foreign_keys()

        lines = [
            "// =============================================================================",
            f"// Odoo Shadow Schema - DBML",
            f"// Generated: {datetime.now(timezone.utc).isoformat()}",
            f"// Schema: {self.config['schema']}",
            f"// Tables: {len(tables)}",
            "// =============================================================================",
            "",
            "Project odoo_shadow {",
            '  database_type: "PostgreSQL"',
            f'  Note: "Odoo CE shadow schema for analytics and RAG"',
            "}",
            "",
        ]

        # Generate table definitions
        for table in tables:
            table_name = table["table_name"]
            columns = self._get_columns(table_name)
            pk_columns = self._get_primary_keys(table_name)
            indexes = self._get_indexes(table_name)

            lines.append(f"Table {table_name} {{")

            # Add columns
            for col in columns:
                col_name = col["column_name"]
                col_type = to_dbml_type(col["data_type"])
                attrs = []

                if col_name in pk_columns:
                    attrs.append("pk")
                if col["is_nullable"] == "NO" and col_name not in pk_columns:
                    attrs.append("not null")
                if col["column_default"]:
                    default = col["column_default"]
                    if "now()" in default.lower():
                        attrs.append("default: `now()`")

                attr_str = f" [{', '.join(attrs)}]" if attrs else ""
                comment = f' // {self._escape_dbml(col["column_comment"])}' if col.get("column_comment") else ""

                lines.append(f"  {col_name} {col_type}{attr_str}{comment}")

            # Add indexes
            if indexes:
                lines.append("")
                lines.append("  indexes {")
                for idx in indexes:
                    cols = ", ".join(idx["columns"])
                    unique = " [unique]" if idx["is_unique"] else ""
                    lines.append(f"    ({cols}){unique}")
                lines.append("  }")

            # Add table note
            if table.get("table_comment"):
                lines.append("")
                lines.append(f'  Note: "{self._escape_dbml(table["table_comment"])}"')

            lines.append("}")
            lines.append("")

        # Generate relationships
        if foreign_keys:
            lines.append("// =============================================================================")
            lines.append("// Relationships")
            lines.append("// =============================================================================")
            lines.append("")

            for fk in foreign_keys:
                lines.append(
                    f"Ref: {fk['table_name']}.{fk['column_name']} > "
                    f"{fk['foreign_table']}.{fk['foreign_column']}"
                )

        logger.info(f"Generated DBML for {len(tables)} tables")
        return "\n".join(lines)

    def save(self, dbml: str, filename: str = "odoo_supabase_schema.dbml") -> str:
        """Save DBML to file."""
        output_dir = Path(self.config["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        path = output_dir / filename
        with open(path, "w") as f:
            f.write(dbml)

        logger.info(f"DBML saved to {path}")
        return str(path)


# =============================================================================
# Main
# =============================================================================

def main():
    """Main entry point."""
    logger.info("=" * 70)
    logger.info("DBML Generation")
    logger.info("=" * 70)

    config = get_config()
    if not validate_config(config):
        sys.exit(1)

    generator = DBMLGenerator(config)
    try:
        generator.connect()
        dbml = generator.generate()
        output_path = generator.save(dbml)

        # Print summary
        logger.info("=" * 70)
        logger.info("Generation Summary")
        logger.info("=" * 70)
        logger.info(f"  Output: {output_path}")
        logger.info("")
        logger.info("View at: https://dbdiagram.io/d")
        logger.info("=" * 70)

    finally:
        generator.close()


if __name__ == "__main__":
    main()
