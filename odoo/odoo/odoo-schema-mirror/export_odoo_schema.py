#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo Schema Export Script

Extracts schema metadata (tables, columns, types, constraints) from Odoo PostgreSQL
and writes it to a normalized JSON artifact. NO DATA is exported.

Usage:
    python odoo-schema-mirror/export_odoo_schema.py

Environment Variables:
    ODOO_DB_HOST      Odoo PostgreSQL host
    ODOO_DB_PORT      Odoo PostgreSQL port (default: 5432)
    ODOO_DB_NAME      Odoo database name
    ODOO_DB_USER      Odoo database user
    ODOO_DB_PASSWORD  Odoo database password
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Configure logging
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
        "host": os.environ.get("ODOO_DB_HOST"),
        "port": int(os.environ.get("ODOO_DB_PORT", "5432")),
        "database": os.environ.get("ODOO_DB_NAME"),
        "user": os.environ.get("ODOO_DB_USER"),
        "password": os.environ.get("ODOO_DB_PASSWORD"),
        "output_dir": os.environ.get("SCHEMA_ARTIFACT_DIR", "./odoo-schema-mirror/artifacts"),
        "include_views": os.environ.get("ODOO_SCHEMA_INCLUDE_VIEWS", "false").lower() == "true",
        "include_functions": os.environ.get("ODOO_SCHEMA_INCLUDE_FUNCTIONS", "false").lower() == "true",
        "include_tables": [t.strip() for t in os.environ.get("ODOO_SCHEMA_INCLUDE_TABLES", "").split(",") if t.strip()],
        "exclude_tables": [t.strip() for t in os.environ.get("ODOO_SCHEMA_EXCLUDE_TABLES", "").split(",") if t.strip()],
    }


def validate_config(config: dict) -> bool:
    """Validate required configuration."""
    required = ["host", "database", "user", "password"]
    missing = [k for k in required if not config.get(k)]
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(f'ODOO_DB_{k.upper()}' for k in missing)}")
        return False
    return True


# =============================================================================
# Schema Extraction Queries
# =============================================================================

QUERY_TABLES = """
SELECT
    t.table_schema,
    t.table_name,
    t.table_type,
    pg_catalog.obj_description(pgc.oid, 'pg_class') as table_comment
FROM information_schema.tables t
LEFT JOIN pg_catalog.pg_class pgc ON pgc.relname = t.table_name
WHERE t.table_schema = 'public'
  AND t.table_type IN ('BASE TABLE'{view_clause})
ORDER BY t.table_name;
"""

QUERY_COLUMNS = """
SELECT
    c.table_name,
    c.column_name,
    c.ordinal_position,
    c.column_default,
    c.is_nullable,
    c.data_type,
    c.character_maximum_length,
    c.numeric_precision,
    c.numeric_scale,
    c.udt_name,
    pg_catalog.col_description(
        (SELECT oid FROM pg_catalog.pg_class WHERE relname = c.table_name AND relnamespace = 'public'::regnamespace),
        c.ordinal_position
    ) as column_comment
FROM information_schema.columns c
WHERE c.table_schema = 'public'
ORDER BY c.table_name, c.ordinal_position;
"""

QUERY_PRIMARY_KEYS = """
SELECT
    tc.table_name,
    kcu.column_name,
    tc.constraint_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'PRIMARY KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.ordinal_position;
"""

QUERY_FOREIGN_KEYS = """
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    tc.constraint_name,
    rc.update_rule,
    rc.delete_rule
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
JOIN information_schema.referential_constraints rc
    ON rc.constraint_name = tc.constraint_name
    AND rc.constraint_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;
"""

QUERY_UNIQUE_CONSTRAINTS = """
SELECT
    tc.table_name,
    kcu.column_name,
    tc.constraint_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'UNIQUE'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, tc.constraint_name, kcu.ordinal_position;
"""

QUERY_INDEXES = """
SELECT
    t.relname as table_name,
    i.relname as index_name,
    a.attname as column_name,
    ix.indisunique as is_unique,
    ix.indisprimary as is_primary,
    am.amname as index_type
FROM pg_class t
JOIN pg_index ix ON t.oid = ix.indrelid
JOIN pg_class i ON i.oid = ix.indexrelid
JOIN pg_am am ON i.relam = am.oid
JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
JOIN pg_namespace n ON n.oid = t.relnamespace
WHERE n.nspname = 'public'
  AND t.relkind = 'r'
ORDER BY t.relname, i.relname, a.attnum;
"""

QUERY_CHECK_CONSTRAINTS = """
SELECT
    tc.table_name,
    tc.constraint_name,
    cc.check_clause
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc
    ON tc.constraint_name = cc.constraint_name
    AND tc.table_schema = cc.constraint_schema
WHERE tc.constraint_type = 'CHECK'
  AND tc.table_schema = 'public'
  AND tc.constraint_name NOT LIKE '%_not_null'
ORDER BY tc.table_name, tc.constraint_name;
"""


# =============================================================================
# Schema Extraction
# =============================================================================

class OdooSchemaExporter:
    """Extracts schema from Odoo PostgreSQL."""

    def __init__(self, config: dict):
        self.config = config
        self.conn = None

    def connect(self):
        """Connect to Odoo PostgreSQL."""
        logger.info(f"Connecting to Odoo PostgreSQL at {self.config['host']}:{self.config['port']}/{self.config['database']}")
        self.conn = psycopg2.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["database"],
            user=self.config["user"],
            password=self.config["password"],
            cursor_factory=RealDictCursor,
        )
        logger.info("Connected successfully")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Connection closed")

    def _execute_query(self, query: str) -> list[dict]:
        """Execute a query and return results."""
        with self.conn.cursor() as cur:
            cur.execute(query)
            return [dict(row) for row in cur.fetchall()]

    def _should_include_table(self, table_name: str) -> bool:
        """Check if table should be included based on filters."""
        include = self.config["include_tables"]
        exclude = self.config["exclude_tables"]

        # If include list is specified, table must match
        if include:
            if not any(pattern in table_name for pattern in include):
                return False

        # Exclude list always applies
        if exclude:
            if any(pattern in table_name for pattern in exclude):
                return False

        return True

    def extract_tables(self) -> list[dict]:
        """Extract table metadata."""
        view_clause = ", 'VIEW'" if self.config["include_views"] else ""
        query = QUERY_TABLES.format(view_clause=view_clause)
        tables = self._execute_query(query)
        return [t for t in tables if self._should_include_table(t["table_name"])]

    def extract_columns(self) -> dict[str, list[dict]]:
        """Extract column metadata grouped by table."""
        columns = self._execute_query(QUERY_COLUMNS)
        result = {}
        for col in columns:
            table = col.pop("table_name")
            if table not in result:
                result[table] = []
            result[table].append(col)
        return result

    def extract_primary_keys(self) -> dict[str, list[str]]:
        """Extract primary key columns grouped by table."""
        pks = self._execute_query(QUERY_PRIMARY_KEYS)
        result = {}
        for pk in pks:
            table = pk["table_name"]
            if table not in result:
                result[table] = []
            result[table].append(pk["column_name"])
        return result

    def extract_foreign_keys(self) -> dict[str, list[dict]]:
        """Extract foreign key metadata grouped by table."""
        fks = self._execute_query(QUERY_FOREIGN_KEYS)
        result = {}
        for fk in fks:
            table = fk.pop("table_name")
            if table not in result:
                result[table] = []
            result[table].append(fk)
        return result

    def extract_unique_constraints(self) -> dict[str, list[dict]]:
        """Extract unique constraints grouped by table."""
        ucs = self._execute_query(QUERY_UNIQUE_CONSTRAINTS)
        result = {}
        for uc in ucs:
            table = uc.pop("table_name")
            if table not in result:
                result[table] = []
            # Group columns by constraint name
            constraint_name = uc["constraint_name"]
            existing = next((c for c in result[table] if c["constraint_name"] == constraint_name), None)
            if existing:
                existing["columns"].append(uc["column_name"])
            else:
                result[table].append({
                    "constraint_name": constraint_name,
                    "columns": [uc["column_name"]],
                })
        return result

    def extract_indexes(self) -> dict[str, list[dict]]:
        """Extract index metadata grouped by table."""
        indexes = self._execute_query(QUERY_INDEXES)
        result = {}
        for idx in indexes:
            table = idx.pop("table_name")
            if table not in result:
                result[table] = []
            # Group columns by index name
            index_name = idx["index_name"]
            existing = next((i for i in result[table] if i["index_name"] == index_name), None)
            if existing:
                existing["columns"].append(idx["column_name"])
            else:
                result[table].append({
                    "index_name": index_name,
                    "columns": [idx["column_name"]],
                    "is_unique": idx["is_unique"],
                    "is_primary": idx["is_primary"],
                    "index_type": idx["index_type"],
                })
        return result

    def extract_check_constraints(self) -> dict[str, list[dict]]:
        """Extract check constraints grouped by table."""
        checks = self._execute_query(QUERY_CHECK_CONSTRAINTS)
        result = {}
        for chk in checks:
            table = chk.pop("table_name")
            if table not in result:
                result[table] = []
            result[table].append(chk)
        return result

    def export(self) -> dict:
        """Export complete schema as a normalized dictionary."""
        logger.info("Extracting schema metadata...")

        # Extract all components
        tables = self.extract_tables()
        columns = self.extract_columns()
        primary_keys = self.extract_primary_keys()
        foreign_keys = self.extract_foreign_keys()
        unique_constraints = self.extract_unique_constraints()
        indexes = self.extract_indexes()
        check_constraints = self.extract_check_constraints()

        # Build normalized schema
        schema = {
            "metadata": {
                "source": f"{self.config['host']}:{self.config['port']}/{self.config['database']}",
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "table_count": len(tables),
            },
            "tables": {},
        }

        for table in tables:
            table_name = table["table_name"]
            schema["tables"][table_name] = {
                "table_type": table["table_type"],
                "comment": table["table_comment"],
                "columns": columns.get(table_name, []),
                "primary_key": primary_keys.get(table_name, []),
                "foreign_keys": foreign_keys.get(table_name, []),
                "unique_constraints": unique_constraints.get(table_name, []),
                "indexes": indexes.get(table_name, []),
                "check_constraints": check_constraints.get(table_name, []),
            }

        logger.info(f"Extracted {len(schema['tables'])} tables")
        return schema

    def save(self, schema: dict, output_path: str):
        """Save schema to JSON file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(schema, f, indent=2, default=str)

        logger.info(f"Schema saved to {output_path}")


# =============================================================================
# Main
# =============================================================================

def main():
    """Main entry point."""
    logger.info("=" * 70)
    logger.info("Odoo Schema Export")
    logger.info("=" * 70)

    config = get_config()
    if not validate_config(config):
        sys.exit(1)

    output_path = Path(config["output_dir"]) / "odoo_schema.json"

    exporter = OdooSchemaExporter(config)
    try:
        exporter.connect()
        schema = exporter.export()
        exporter.save(schema, output_path)

        # Print summary
        logger.info("=" * 70)
        logger.info("Export Summary")
        logger.info("=" * 70)
        logger.info(f"  Tables: {schema['metadata']['table_count']}")
        logger.info(f"  Output: {output_path}")
        logger.info("=" * 70)

    finally:
        exporter.close()


if __name__ == "__main__":
    main()
