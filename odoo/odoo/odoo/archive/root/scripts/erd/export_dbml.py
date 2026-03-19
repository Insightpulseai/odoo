#!/usr/bin/env python3
"""
Export PostgreSQL schema as DBML (Database Markup Language).

Uses pg_catalog exclusively — no Odoo system tables required.
Output is deterministic (sorted by schema + table name).

Environment variables:
  DATABASE_URL          Full Postgres DSN (overrides PG* vars)
  PGHOST / DB_HOST      Database host (default: db)
  PGPORT / DB_PORT      Database port (default: 5432)
  PGDATABASE / DB_NAME  Database name (default: odoo)
  PGUSER / DB_USER      Database user (default: postgres)
  PGPASSWORD / DB_PASSWORD  Password (default: empty)

  ERD_SCHEMAS           Comma-separated schemas to include (default: public)
  ERD_TABLE_INCLUDE_REGEX  Optional: only include tables matching this regex
  ERD_TABLE_EXCLUDE_REGEX  Optional: exclude tables matching this regex
  ERD_DBML_OUT          Output path (default: docs/erd/odoo.dbml)

Exit codes:
  0  success
  1  export error
  2  db connection error
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import psycopg2
except ImportError as e:
    raise SystemExit(
        "psycopg2 missing. Install: pip install psycopg2-binary"
    ) from e


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def pg_conn():
    """Create PostgreSQL connection — mirrors tools/odoo_schema/export_schema.py pattern."""
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        try:
            import psycopg2
            return psycopg2.connect(database_url)
        except Exception as e:
            raise SystemExit(f"DB connection error (DATABASE_URL): {e}") from e

    host = os.environ.get("PGHOST") or os.environ.get("DB_HOST") or "db"
    port = int(os.environ.get("PGPORT") or os.environ.get("DB_PORT") or "5432")
    db = os.environ.get("PGDATABASE") or os.environ.get("DB_NAME") or "odoo"
    user = os.environ.get("PGUSER") or os.environ.get("DB_USER") or "postgres"
    pwd = os.environ.get("PGPASSWORD") or os.environ.get("DB_PASSWORD") or ""

    try:
        return psycopg2.connect(host=host, port=port, dbname=db, user=user, password=pwd)
    except Exception as e:
        raise SystemExit(f"DB connection error: {e}") from e


def fetchall(cur, query: str, args=None) -> list:
    cur.execute(query, args or ())
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


# ---------------------------------------------------------------------------
# Scoping filters
# ---------------------------------------------------------------------------

def _compile_optional(pattern: Optional[str]):
    return re.compile(pattern) if pattern else None


def table_included(table: str, include_re, exclude_re) -> bool:
    if exclude_re and exclude_re.search(table):
        return False
    if include_re and not include_re.search(table):
        return False
    return True


# ---------------------------------------------------------------------------
# pg_catalog queries
# ---------------------------------------------------------------------------

TABLES_SQL = """
SELECT
    n.nspname  AS schema_name,
    c.relname  AS table_name,
    obj_description(c.oid, 'pg_class') AS table_comment
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
  AND n.nspname = ANY(%s)
ORDER BY n.nspname, c.relname
"""

COLUMNS_SQL = """
SELECT
    n.nspname  AS schema_name,
    c.relname  AS table_name,
    a.attname  AS col_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) AS col_type,
    NOT a.attnotnull AS nullable,
    CASE WHEN ad.adbin IS NOT NULL
         THEN pg_get_expr(ad.adbin, ad.adrelid)
         ELSE NULL
    END AS col_default,
    col_description(a.attrelid, a.attnum) AS col_comment
FROM pg_attribute a
JOIN pg_class c ON c.oid = a.attrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
LEFT JOIN pg_attrdef ad ON ad.adrelid = a.attrelid AND ad.adnum = a.attnum
WHERE c.relkind = 'r'
  AND a.attnum > 0
  AND NOT a.attisdropped
  AND n.nspname = ANY(%s)
ORDER BY n.nspname, c.relname, a.attnum
"""

PKS_SQL = """
SELECT
    n.nspname  AS schema_name,
    c.relname  AS table_name,
    a.attname  AS col_name
FROM pg_index i
JOIN pg_class c ON c.oid = i.indrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = ANY(i.indkey)
WHERE i.indisprimary
  AND n.nspname = ANY(%s)
ORDER BY n.nspname, c.relname, a.attnum
"""

FKS_SQL = """
SELECT
    n.nspname                AS schema_name,
    c.relname                AS table_name,
    con.conname              AS fk_name,
    array_agg(a.attname ORDER BY a.attnum) AS src_cols,
    fn.nspname               AS dst_schema,
    fc.relname               AS dst_table,
    array_agg(fa.attname ORDER BY fa.attnum) AS dst_cols
FROM pg_constraint con
JOIN pg_class c ON c.oid = con.conrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_class fc ON fc.oid = con.confrelid
JOIN pg_namespace fn ON fn.oid = fc.relnamespace
JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = ANY(con.conkey)
JOIN pg_attribute fa ON fa.attrelid = fc.oid AND fa.attnum = ANY(con.confkey)
WHERE con.contype = 'f'
  AND n.nspname = ANY(%s)
GROUP BY n.nspname, c.relname, con.conname, fn.nspname, fc.relname
ORDER BY n.nspname, c.relname, con.conname
"""


# ---------------------------------------------------------------------------
# DBML rendering
# ---------------------------------------------------------------------------

def _dbml_type(pg_type: str) -> str:
    """Pass-through — DBML accepts PG native types."""
    return pg_type


def render_dbml(tables, columns, pks, fks, include_re, exclude_re) -> str:
    lines = [
        "// DBML — auto-generated by scripts/erd/export_dbml.py",
        "// Do not edit by hand. Regenerate with: bash scripts/erd/generate_all.sh",
        "",
    ]

    # Index: schema.table → set of pk cols
    pk_map: dict[str, set] = {}
    for r in pks:
        key = f"{r['schema_name']}.{r['table_name']}"
        pk_map.setdefault(key, set()).add(r["col_name"])

    # Index: schema.table → list of column dicts
    col_map: dict[str, list] = {}
    for r in columns:
        key = f"{r['schema_name']}.{r['table_name']}"
        col_map.setdefault(key, []).append(r)

    # Emit Table blocks
    for t in tables:
        fq = f"{t['schema_name']}.{t['table_name']}"
        tname = t["table_name"] if t["schema_name"] == "public" else fq
        if not table_included(tname, include_re, exclude_re):
            continue

        lines.append(f"Table {tname} {{")
        for col in col_map.get(fq, []):
            annotations = []
            if col["col_name"] in pk_map.get(fq, set()):
                annotations.append("pk")
            if not col["nullable"]:
                annotations.append("not null")
            if col["col_default"] is not None:
                default_val = col["col_default"]
                # Quote string defaults; leave numeric/function defaults bare
                if not re.match(r"^-?\d|nextval\(|now\(|true|false|null", default_val, re.I):
                    default_val = f"'{default_val}'"
                annotations.append(f"default: {default_val}")
            if col["col_comment"]:
                annotations.append(f'note: "{col["col_comment"]}"')
            ann_str = f" [{', '.join(annotations)}]" if annotations else ""
            lines.append(f"  {col['col_name']} {_dbml_type(col['col_type'])}{ann_str}")
        if t["table_comment"]:
            lines.append(f'  Note: "{t["table_comment"]}"')
        lines.append("}")
        lines.append("")

    # Emit Ref lines
    for fk in fks:
        src_tname = (
            fk["table_name"] if fk["schema_name"] == "public"
            else f"{fk['schema_name']}.{fk['table_name']}"
        )
        dst_tname = (
            fk["dst_table"] if fk["dst_schema"] == "public"
            else f"{fk['dst_schema']}.{fk['dst_table']}"
        )
        if not table_included(src_tname, include_re, exclude_re):
            continue
        src_cols = ", ".join(fk["src_cols"])
        dst_cols = ", ".join(fk["dst_cols"])
        lines.append(
            f"Ref: {src_tname}.{src_cols} > {dst_tname}.{dst_cols} // {fk['fk_name']}"
        )

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    schemas_raw = os.environ.get("ERD_SCHEMAS", "public")
    schemas = [s.strip() for s in schemas_raw.split(",") if s.strip()]

    include_re = _compile_optional(os.environ.get("ERD_TABLE_INCLUDE_REGEX"))
    exclude_re = _compile_optional(os.environ.get("ERD_TABLE_EXCLUDE_REGEX"))

    out_path = Path(os.environ.get("ERD_DBML_OUT", "docs/erd/odoo.dbml"))
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Connecting to database …")
    conn = pg_conn()

    with conn, conn.cursor() as cur:
        tables  = fetchall(cur, TABLES_SQL,  (schemas,))
        columns = fetchall(cur, COLUMNS_SQL, (schemas,))
        pks     = fetchall(cur, PKS_SQL,     (schemas,))
        fks     = fetchall(cur, FKS_SQL,     (schemas,))

    print(f"  {len(tables)} tables, {len(columns)} columns, {len(fks)} FK constraints")

    dbml = render_dbml(tables, columns, pks, fks, include_re, exclude_re)

    out_path.write_text(dbml, encoding="utf-8")
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
