#!/usr/bin/env python3
"""
check_prod_mail_live.py — Optional live audit: verify ipai.mail.provider = zoho in prod DB.

Run in protected CI environment with DATABASE_URL set, or locally via:
  DATABASE_URL="postgresql://odoo:PASSWORD@178.128.112.214:5432/odoo" \
    python3 scripts/ci/check_prod_mail_live.py

Exit codes:
  0  ipai.mail.provider == zoho (pass)
  1  provider is wrong or absent (fail + actionable message)
  3  DATABASE_URL not set or psql unavailable (warn, no fail — optional check)

Environment:
  DATABASE_URL  — Postgres connection string for prod Odoo DB
                  Format: postgresql://USER:PASS@HOST:PORT/DBNAME
  ODOO_DB_NAME  — Alternative: database name when using local socket (optional)
"""
from __future__ import annotations

import os
import subprocess
import sys

EXPECTED_PROVIDER = "zoho"
PARAM_KEY = "ipai.mail.provider"


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def warn(msg: str) -> None:
    print(f"WARN: {msg}", file=sys.stderr)


def main() -> int:
    db_url = os.environ.get("DATABASE_URL", "").strip()
    if not db_url:
        warn(
            "DATABASE_URL not set — skipping live prod mail provider check. "
            "Set DATABASE_URL to run this audit."
        )
        print("OK (skipped): live mail provider audit not run (DATABASE_URL absent).")
        raise SystemExit(3)

    sql = (
        f"SELECT value FROM ir_config_parameter "
        f"WHERE key = '{PARAM_KEY}' LIMIT 1;"
    )

    try:
        result = subprocess.run(
            ["psql", db_url, "-t", "-A", "-c", sql],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except FileNotFoundError:
        warn("psql not found — install postgresql-client to run live audit.")
        print("OK (skipped): live mail provider audit not run (psql unavailable).")
        raise SystemExit(3)
    except subprocess.TimeoutExpired:
        die("psql timed out connecting to prod DB (15s). Check DATABASE_URL and network access.", code=3)

    if result.returncode != 0:
        die(
            f"psql failed (exit {result.returncode}): {result.stderr.strip()[:200]}\n"
            f"Check DATABASE_URL and that the user has SELECT on ir_config_parameter.",
            code=3,
        )

    actual = result.stdout.strip()
    if not actual:
        die(
            f"ir_config_parameter key '{PARAM_KEY}' is absent from prod DB. "
            f"Set it via: Odoo Settings → Technical → Parameters → System Parameters "
            f"(or run scripts/ci/apply_settings_as_code.sh if available).",
            code=1,
        )

    if actual != EXPECTED_PROVIDER:
        die(
            f"PROD DRIFT: ir_config_parameter['{PARAM_KEY}'] = '{actual}' "
            f"(expected '{EXPECTED_PROVIDER}'). "
            f"Run: UPDATE ir_config_parameter SET value = 'zoho' WHERE key = '{PARAM_KEY}'; "
            f"or use Odoo Settings → Technical → Parameters → System Parameters.",
            code=1,
        )

    print(f"OK (live): ir_config_parameter['{PARAM_KEY}'] = '{actual}' — Zoho is the active provider.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
