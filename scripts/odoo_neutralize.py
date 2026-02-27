#!/usr/bin/env python3
"""
odoo_neutralize.py — Idempotent Odoo environment neutralization script.

Implements the Odoo.sh "neutralized database" concept for non-production environments.
Run after every DB restore/clone to prevent sending live emails or triggering disruptive
scheduled actions from a copied production database.

References:
  https://www.odoo.com/documentation/17.0/administration/neutralized_database.html
  https://www.odoo.com/documentation/19.0/administration/odoo_sh/getting_started/create.html

Usage:
  IPAI_ENV=stage python3 scripts/odoo_neutralize.py
  IPAI_ENV=dev    python3 scripts/odoo_neutralize.py
  IPAI_ENV=prod   python3 scripts/odoo_neutralize.py  # no-op

Environment variables (same as Odoo container):
  IPAI_ENV      prod | stage | dev  (required)
  DB_HOST       PostgreSQL host     (default: localhost)
  DB_PORT       PostgreSQL port     (default: 5432)
  DB_USER       DB username         (default: odoo)
  DB_PASSWORD   DB password         (required if not trust auth)
  DB_NAME       DB name             (default: odoo)

Exit codes:
  0 — success (neutralized or prod no-op)
  1 — configuration error (missing IPAI_ENV, DB connection failed, etc.)
"""

import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("odoo_neutralize")

# ---------------------------------------------------------------------------
# Cron allowlist — only these jobs remain active in neutralized environments.
# Add technical_name or xml_id (partial match on cron_name_contains).
# ---------------------------------------------------------------------------
CRON_ALLOWLIST = [
    "mail.mail_gc_notifications",        # Clean stale mail notifications
    "base_automation.autovacuum",        # DB maintenance
    "base.ir_cron_auto_vacuum",          # Base auto-vacuum
    "base.autovacuum_message_attachments", # Attachment cleanup
]

# ---------------------------------------------------------------------------
# SQL for neutralization
# ---------------------------------------------------------------------------

SQL_DISABLE_MAIL_SERVERS = """
UPDATE ir_mail_server
SET active = false
WHERE active = true;
"""

SQL_DISABLE_SCHEDULED_ACTIONS = """
UPDATE ir_cron
SET active = false
WHERE active = true
  AND name NOT IN %(allowlist)s;
"""

SQL_VERIFY_MAIL_SERVERS = """
SELECT COUNT(*) FROM ir_mail_server WHERE active = true;
"""

SQL_VERIFY_CRON = """
SELECT COUNT(*) FROM ir_cron WHERE active = true
  AND name NOT IN %(allowlist)s;
"""

SQL_SET_PARAM = """
INSERT INTO ir_config_parameter (key, value, create_date, write_date)
VALUES (%(key)s, %(value)s, NOW(), NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();
"""

# Mark the DB as neutralized with a timestamp
SQL_NEUTRALIZATION_MARKER = """
INSERT INTO ir_config_parameter (key, value, create_date, write_date)
VALUES ('ipai.neutralized', %(env)s || ':' || NOW()::text, NOW(), NOW())
ON CONFLICT (key) DO UPDATE
  SET value = EXCLUDED.value,
      write_date = NOW();
"""

SQL_CHECK_ALREADY_NEUTRALIZED = """
SELECT value FROM ir_config_parameter WHERE key = 'ipai.neutralized';
"""


def get_db_connection():
    """Build a psycopg2 connection from environment variables."""
    try:
        import psycopg2  # noqa: PLC0415
    except ImportError:
        log.error(
            "psycopg2 not available. Install with: pip install psycopg2-binary"
        )
        sys.exit(1)

    conn_params = {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", "5432")),
        "user": os.environ.get("DB_USER", "odoo"),
        "dbname": os.environ.get("DB_NAME", "odoo"),
    }
    password = os.environ.get("DB_PASSWORD")
    if password:
        conn_params["password"] = password

    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = False
        log.info(
            "Connected to %s@%s:%s/%s",
            conn_params["user"],
            conn_params["host"],
            conn_params["port"],
            conn_params["dbname"],
        )
        return conn
    except Exception as exc:
        log.error("DB connection failed: %s", exc)
        sys.exit(1)


def table_exists(cur, table_name: str) -> bool:
    """Check if a table exists in the public schema."""
    cur.execute(
        "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=%s)",
        (table_name,),
    )
    return cur.fetchone()[0]


def neutralize(env: str) -> None:
    """Apply neutralization to the connected database."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Verify this looks like an Odoo DB
    if not table_exists(cur, "ir_config_parameter"):
        log.error(
            "ir_config_parameter table not found — this does not look like an Odoo DB."
        )
        conn.close()
        sys.exit(1)

    # Check if already neutralized (idempotency fast-path)
    cur.execute(SQL_CHECK_ALREADY_NEUTRALIZED)
    existing = cur.fetchone()
    if existing:
        log.info("DB already marked neutralized: %s", existing[0])
        log.info("Re-running neutralization to ensure consistency...")

    allowlist_tuple = tuple(CRON_ALLOWLIST)

    try:
        # 1. Disable outgoing mail servers
        if table_exists(cur, "ir_mail_server"):
            cur.execute(SQL_DISABLE_MAIL_SERVERS)
            log.info("Disabled %d outgoing mail server(s).", cur.rowcount)
        else:
            log.info("ir_mail_server table not found — skipping (module not installed).")

        # 2. Disable scheduled actions (crons) except allowlist
        if table_exists(cur, "ir_cron"):
            cur.execute(SQL_DISABLE_SCHEDULED_ACTIONS, {"allowlist": allowlist_tuple})
            log.info("Disabled %d scheduled action(s) (allowlist preserved).", cur.rowcount)
        else:
            log.info("ir_cron table not found — skipping (module not installed).")

        # 3. Set neutralization system parameter
        cur.execute(SQL_NEUTRALIZATION_MARKER, {"env": env})

        # 4. Set debug_key env marker (surfaced by OdooOps Console)
        cur.execute(
            SQL_SET_PARAM,
            {"key": "ipai.environment", "value": env},
        )

        conn.commit()

        # 5. Verify: assert no active mail servers remain
        if table_exists(cur, "ir_mail_server"):
            cur.execute(SQL_VERIFY_MAIL_SERVERS)
            remaining_mail = cur.fetchone()[0]
            if remaining_mail > 0:
                log.error(
                    "FAIL: %d active mail server(s) still enabled after neutralization.",
                    remaining_mail,
                )
                conn.close()
                sys.exit(1)
            log.info("VERIFY: ✅ 0 active mail servers (neutralized).")

        # 6. Verify: assert no non-allowlisted crons active
        if table_exists(cur, "ir_cron"):
            cur.execute(SQL_VERIFY_CRON, {"allowlist": allowlist_tuple})
            remaining_cron = cur.fetchone()[0]
            if remaining_cron > 0:
                log.error(
                    "FAIL: %d non-allowlisted scheduled action(s) still active.",
                    remaining_cron,
                )
                conn.close()
                sys.exit(1)
            log.info("VERIFY: ✅ 0 non-allowlisted scheduled actions active.")

        log.info("Neutralization complete. DB is safe for %s environment.", env)

    except Exception as exc:
        conn.rollback()
        log.error("Neutralization failed (rolled back): %s", exc)
        conn.close()
        sys.exit(1)

    conn.close()


def main() -> None:
    env = os.environ.get("IPAI_ENV", "").strip().lower()

    if not env:
        log.error(
            "IPAI_ENV is not set. Set to 'prod', 'stage', or 'dev' before running."
        )
        sys.exit(1)

    valid_envs = {"prod", "stage", "dev"}
    if env not in valid_envs:
        # Allow dev/* variants (dev_feature, dev_tbwa, etc.)
        if not env.startswith("dev"):
            log.error("IPAI_ENV='%s' is not valid. Must be prod | stage | dev (or dev_*).", env)
            sys.exit(1)

    if env == "prod":
        log.info("IPAI_ENV=prod — no neutralization applied (live system).")
        sys.exit(0)

    log.info("IPAI_ENV=%s — applying neutralization...", env)
    neutralize(env)


if __name__ == "__main__":
    main()
