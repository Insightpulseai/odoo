#!/usr/bin/env python3
"""
OCA Must-Have Module Verification Script
Validates that all modules in the manifest are installed in Odoo.
Usage: ./scripts/odoo_verify_oca_must_have.py [manifest_path]
"""
import os
import sys

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary", file=sys.stderr)
    sys.exit(2)

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

MANIFEST = sys.argv[1] if len(sys.argv) > 1 else "config/oca/oca_must_have_base.yml"

# DB connection can be either direct PG URL or host/user/db
PGURL = os.getenv("ODOO_PGURL")  # e.g. postgres://user:pass@host:5432/dbname
DBNAME = os.getenv("ODOO_DB")

if not PGURL and not DBNAME:
    print("ERROR: set ODOO_PGURL or ODOO_DB (and PG* env vars).", file=sys.stderr)
    sys.exit(2)

with open(MANIFEST, 'r') as f:
    d = yaml.safe_load(f)
must = d.get("modules", [])

if not must:
    print("ERROR: no modules defined in manifest", file=sys.stderr)
    sys.exit(2)

if PGURL:
    conn = psycopg2.connect(PGURL)
else:
    conn = psycopg2.connect(
        dbname=DBNAME,
        user=os.getenv("PGUSER", "odoo"),
        password=os.getenv("PGPASSWORD", "odoo"),
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=int(os.getenv("PGPORT", "5432")),
    )

cur = conn.cursor()
cur.execute("SELECT name, state FROM ir_module_module WHERE name = ANY(%s)", (must,))
rows = {name: state for (name, state) in cur.fetchall()}

conn.close()

missing = [m for m in must if m not in rows]
not_installed = [m for m, s in rows.items() if s not in ("installed", "to upgrade")]

if missing or not_installed:
    print("FAIL: OCA must-have verification failed.")
    if missing:
        print("Missing from ir_module_module:", missing)
    if not_installed:
        print("Present but not installed:", {m: rows[m] for m in not_installed})
    sys.exit(1)

print(f"OK: all {len(must)} must-have modules installed.")
for m in must:
    print(f"  - {m}: {rows[m]}")
