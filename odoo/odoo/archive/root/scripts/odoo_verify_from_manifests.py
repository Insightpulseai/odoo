#!/usr/bin/env python3
"""
OCA Multi-Manifest Module Verification Script
Validates that all modules from one or more manifests (with include support) are installed.
Usage: ./scripts/odoo_verify_from_manifests.py <manifest.yml> [manifest2.yml ...]
"""
import os
import sys
from pathlib import Path

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


def load(p: Path):
    with p.open("r") as f:
        return yaml.safe_load(f) or {}


def resolve_manifest(p: Path, seen=None):
    if seen is None:
        seen = set()
    p = p.resolve()
    if p in seen:
        return []
    seen.add(p)

    d = load(p)
    mods = list(d.get("modules") or [])

    # Process includes relative to manifest directory
    for inc in (d.get("includes") or []):
        inc_path = (p.parent / inc).resolve()
        if inc_path.exists():
            mods += resolve_manifest(inc_path, seen)

    # de-dupe preserving order
    out = []
    s = set()
    for m in mods:
        if m and m not in s:
            s.add(m)
            out.append(m)
    return out


if len(sys.argv) < 2:
    print("usage: odoo_verify_from_manifests.py <manifest.yml> [manifest2.yml ...]", file=sys.stderr)
    sys.exit(2)

mods = []
s = set()
for arg in sys.argv[1:]:
    for m in resolve_manifest(Path(arg)):
        if m not in s:
            s.add(m)
            mods.append(m)

if not mods:
    print("ERROR: no modules resolved from manifests", file=sys.stderr)
    sys.exit(2)

# DB connection
PGURL = os.getenv("ODOO_PGURL")
DBNAME = os.getenv("ODOO_DB")

if PGURL:
    conn = psycopg2.connect(PGURL)
elif DBNAME:
    conn = psycopg2.connect(
        dbname=DBNAME,
        user=os.getenv("PGUSER", "odoo"),
        password=os.getenv("PGPASSWORD", "odoo"),
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=int(os.getenv("PGPORT", "5432")),
    )
else:
    print("ERROR: set ODOO_PGURL or ODOO_DB (and PG* env vars).", file=sys.stderr)
    sys.exit(2)

cur = conn.cursor()
cur.execute("SELECT name, state FROM ir_module_module WHERE name = ANY(%s)", (mods,))
rows = {name: state for (name, state) in cur.fetchall()}

conn.close()

missing = [m for m in mods if m not in rows]
not_installed = [m for m, s in rows.items() if s not in ("installed", "to upgrade")]

if missing or not_installed:
    print("FAIL: OCA multi-manifest verification failed.")
    if missing:
        print("Missing from ir_module_module:", missing)
    if not_installed:
        print("Present but not installed:", {m: rows[m] for m in not_installed})
    sys.exit(1)

print(f"OK: all {len(mods)} manifest modules installed.")
for m in mods:
    print(f"  - {m}: {rows[m]}")
