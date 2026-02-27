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
  # Dry-run (no DB writes — validates config, prints plan):
  IPAI_ENV=stage DB_NAME=odoo_stage python3 scripts/odoo_neutralize.py --dry-run

  # Live run (requires explicit confirmation):
  IPAI_ENV=stage IPAI_NEUTRALIZE_CONFIRM=YES python3 scripts/odoo_neutralize.py
  IPAI_ENV=dev   IPAI_NEUTRALIZE_CONFIRM=YES python3 scripts/odoo_neutralize.py

  # Prod (always a no-op regardless of flags):
  IPAI_ENV=prod  python3 scripts/odoo_neutralize.py

Environment variables (same as Odoo container):
  IPAI_ENV                  prod | stage | dev  (required)
  IPAI_NEUTRALIZE_CONFIRM   Must be "YES" for live writes (prevents accidental runs)
  DB_HOST                   PostgreSQL host     (default: localhost)
  DB_PORT                   PostgreSQL port     (default: 5432)
  DB_USER                   DB username         (default: odoo)
  DB_PASSWORD               DB password         (required if not trust auth)
  DB_NAME                   DB name             (required; validated against env SSOT)

Exit codes:
  0 — success (neutralized, prod no-op, or dry-run)
  1 — configuration error (invalid env, DB name mismatch, confirmation missing, etc.)
  2 — neutralization failure (DB error, verification failed)
"""

__version__ = "1.1.0"

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("odoo_neutralize")

# ---------------------------------------------------------------------------
# Environment safety maps — each env has an expected DB name.
# This prevents accidentally neutralizing the wrong database.
# ---------------------------------------------------------------------------
ENV_DB_MAP = {
    "stage": "odoo_stage",
    "dev":   "odoo_dev",
    # dev/* variants (dev_tbwa, dev_uat, etc.) map to odoo_dev by default;
    # override with DB_NAME if a different naming convention is used.
}

VALID_ENVS = {"prod", "stage", "dev"}

# ---------------------------------------------------------------------------
# Cron allowlist — only these jobs remain active in neutralized environments.
# Matched against ir_cron.name (exact) or code (substring).
# ---------------------------------------------------------------------------
CRON_ALLOWLIST = [
    "mail.mail_gc_notifications",          # Clean stale mail notifications
    "base_automation.autovacuum",          # DB maintenance
    "base.ir_cron_auto_vacuum",            # Base auto-vacuum
    "base.autovacuum_message_attachments", # Attachment cleanup
]

# ---------------------------------------------------------------------------
# SQL
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

SQL_COUNT_ACTIVE_MAIL_SERVERS = """
SELECT COUNT(*) FROM ir_mail_server WHERE active = true;
"""

SQL_COUNT_ACTIVE_CRONS_NOT_ALLOWLISTED = """
SELECT COUNT(*) FROM ir_cron WHERE active = true
  AND name NOT IN %(allowlist)s;
"""

SQL_COUNT_WOULD_DISABLE_MAIL = """
SELECT COUNT(*) FROM ir_mail_server WHERE active = true;
"""

SQL_COUNT_WOULD_DISABLE_CRONS = """
SELECT COUNT(*) FROM ir_cron WHERE active = true
  AND name NOT IN %(allowlist)s;
"""

SQL_SET_PARAM = """
INSERT INTO ir_config_parameter (key, value, create_date, write_date)
VALUES (%(key)s, %(value)s, NOW(), NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();
"""

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def validate_config(env: str, db_name: str) -> None:
    """Hard-stop on any unsafe configuration before touching the DB."""
    # 1. IPAI_ENV must be a known value
    norm_env = env.lower()
    base_env = "dev" if norm_env.startswith("dev") else norm_env
    if base_env not in VALID_ENVS:
        log.error(
            "IPAI_ENV='%s' is not valid. Must be one of: %s (or dev_* variants).",
            env, ", ".join(sorted(VALID_ENVS)),
        )
        sys.exit(1)

    if base_env == "prod":
        return  # prod is always safe (no-op)

    # 2. DB_NAME must match the expected name for this env
    expected_db = ENV_DB_MAP.get(base_env, "odoo_dev")
    if db_name != expected_db:
        log.error(
            "DB_NAME='%s' does not match the expected database for IPAI_ENV='%s' (expected: '%s').",
            db_name, env, expected_db,
        )
        log.error(
            "This is a safety gate to prevent accidentally neutralizing the wrong database."
        )
        log.error(
            "If you are using a non-standard DB name, verify your environment mapping."
        )
        sys.exit(1)


def get_db_connection(db_name: str):
    """Build a psycopg2 connection from environment variables."""
    try:
        import psycopg2  # noqa: PLC0415
    except ImportError:
        log.error(
            "psycopg2 not available. Install with: pip install psycopg2-binary"
        )
        sys.exit(2)

    conn_params = {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", "5432")),
        "user": os.environ.get("DB_USER", "odoo"),
        "dbname": db_name,
    }
    password = os.environ.get("DB_PASSWORD")
    if password:
        conn_params["password"] = password

    try:
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = False
        log.info(
            "Connected to %s@%s:%s/%s",
            conn_params["user"], conn_params["host"],
            conn_params["port"], conn_params["dbname"],
        )
        return conn
    except Exception as exc:
        log.error("DB connection failed: %s", exc)
        sys.exit(2)


def table_exists(cur, table_name: str) -> bool:
    cur.execute(
        "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=%s)",
        (table_name,),
    )
    return cur.fetchone()[0]


def emit_summary(
    env: str,
    db_name: str,
    dry_run: bool,
    mail_servers_changed: Optional[int],
    crons_changed: Optional[int],
    already_neutralized: Optional[str],
    status: str,
) -> None:
    """Emit a single structured JSON line for CI evidence capture."""
    summary = {
        "tool": "odoo_neutralize",
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "env": env,
        "db": db_name,
        "dry_run": dry_run,
        "already_neutralized": already_neutralized,
        "mail_servers_disabled": mail_servers_changed,
        "crons_disabled": crons_changed,
        "cron_allowlist_size": len(CRON_ALLOWLIST),
        "status": status,
    }
    print("NEUTRALIZE_SUMMARY: " + json.dumps(summary, separators=(",", ":")))


# ---------------------------------------------------------------------------
# Dry-run mode
# ---------------------------------------------------------------------------

def dry_run(env: str, db_name: str) -> None:
    """
    Connect, count what would change, print JSON summary, exit 0.
    No writes are performed.
    """
    log.info("DRY-RUN mode — no changes will be written.")
    conn = get_db_connection(db_name)
    cur = conn.cursor()

    if not table_exists(cur, "ir_config_parameter"):
        log.warning("ir_config_parameter not found — not an Odoo DB, or tables not yet created.")

    already = None
    if table_exists(cur, "ir_config_parameter"):
        cur.execute(SQL_CHECK_ALREADY_NEUTRALIZED)
        row = cur.fetchone()
        already = row[0] if row else None

    allowlist_tuple = tuple(CRON_ALLOWLIST)
    mail_count = 0
    cron_count = 0

    if table_exists(cur, "ir_mail_server"):
        cur.execute(SQL_COUNT_WOULD_DISABLE_MAIL)
        mail_count = cur.fetchone()[0]
        log.info("Would disable %d active mail server(s).", mail_count)
    else:
        log.info("ir_mail_server not present — would skip.")

    if table_exists(cur, "ir_cron"):
        cur.execute(SQL_COUNT_WOULD_DISABLE_CRONS, {"allowlist": allowlist_tuple})
        cron_count = cur.fetchone()[0]
        log.info("Would disable %d scheduled action(s) (allowlist preserved).", cron_count)
    else:
        log.info("ir_cron not present — would skip.")

    conn.close()
    emit_summary(
        env=env, db_name=db_name, dry_run=True,
        mail_servers_changed=mail_count,
        crons_changed=cron_count,
        already_neutralized=already,
        status="DRY_RUN_OK",
    )
    log.info("Dry-run complete. To apply: set IPAI_NEUTRALIZE_CONFIRM=YES and re-run.")


# ---------------------------------------------------------------------------
# Live neutralization
# ---------------------------------------------------------------------------

def neutralize(env: str, db_name: str) -> None:
    """Apply neutralization writes to the database."""
    conn = get_db_connection(db_name)
    cur = conn.cursor()

    if not table_exists(cur, "ir_config_parameter"):
        log.error(
            "ir_config_parameter table not found — this does not look like an Odoo DB."
        )
        conn.close()
        sys.exit(2)

    # Check idempotency marker
    cur.execute(SQL_CHECK_ALREADY_NEUTRALIZED)
    existing = cur.fetchone()
    already = existing[0] if existing else None
    if already:
        log.info("DB already marked neutralized: %s — re-running for consistency.", already)

    allowlist_tuple = tuple(CRON_ALLOWLIST)
    mail_disabled = 0
    cron_disabled = 0

    try:
        # 1. Disable outgoing mail servers
        if table_exists(cur, "ir_mail_server"):
            cur.execute(SQL_DISABLE_MAIL_SERVERS)
            mail_disabled = cur.rowcount
            log.info("Disabled %d outgoing mail server(s).", mail_disabled)
        else:
            log.info("ir_mail_server not present — skipping.")

        # 2. Disable scheduled actions (except allowlist)
        if table_exists(cur, "ir_cron"):
            cur.execute(SQL_DISABLE_SCHEDULED_ACTIONS, {"allowlist": allowlist_tuple})
            cron_disabled = cur.rowcount
            log.info("Disabled %d scheduled action(s).", cron_disabled)
        else:
            log.info("ir_cron not present — skipping.")

        # 3. Write neutralization marker + env parameter
        cur.execute(SQL_NEUTRALIZATION_MARKER, {"env": env})
        cur.execute(SQL_SET_PARAM, {"key": "ipai.environment", "value": env})
        conn.commit()

        # 4. Verify: no active mail servers remain
        if table_exists(cur, "ir_mail_server"):
            cur.execute(SQL_COUNT_ACTIVE_MAIL_SERVERS)
            remaining_mail = cur.fetchone()[0]
            if remaining_mail > 0:
                log.error(
                    "VERIFY FAIL: %d active mail server(s) still enabled.", remaining_mail
                )
                emit_summary(
                    env=env, db_name=db_name, dry_run=False,
                    mail_servers_changed=mail_disabled, crons_changed=cron_disabled,
                    already_neutralized=already, status="VERIFY_FAIL_MAIL",
                )
                conn.close()
                sys.exit(2)
            log.info("VERIFY: ✅ 0 active mail servers.")

        # 5. Verify: no non-allowlisted crons remain active
        if table_exists(cur, "ir_cron"):
            cur.execute(SQL_COUNT_ACTIVE_CRONS_NOT_ALLOWLISTED, {"allowlist": allowlist_tuple})
            remaining_cron = cur.fetchone()[0]
            if remaining_cron > 0:
                log.error(
                    "VERIFY FAIL: %d non-allowlisted crons still active.", remaining_cron
                )
                emit_summary(
                    env=env, db_name=db_name, dry_run=False,
                    mail_servers_changed=mail_disabled, crons_changed=cron_disabled,
                    already_neutralized=already, status="VERIFY_FAIL_CRON",
                )
                conn.close()
                sys.exit(2)
            log.info("VERIFY: ✅ 0 non-allowlisted scheduled actions.")

        log.info("Neutralization complete. DB is safe for %s environment.", env)
        emit_summary(
            env=env, db_name=db_name, dry_run=False,
            mail_servers_changed=mail_disabled, crons_changed=cron_disabled,
            already_neutralized=already, status="OK",
        )

    except Exception as exc:
        conn.rollback()
        log.error("Neutralization failed (rolled back): %s", exc)
        emit_summary(
            env=env, db_name=db_name, dry_run=False,
            mail_servers_changed=None, crons_changed=None,
            already_neutralized=already, status="ERROR",
        )
        conn.close()
        sys.exit(2)

    conn.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Odoo environment neutralization script.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Connect, count changes, print JSON summary — no writes performed.",
    )
    args = parser.parse_args()

    # ---- Read env config ----
    env = os.environ.get("IPAI_ENV", "").strip().lower()
    if not env:
        log.error(
            "IPAI_ENV is not set. Set to 'prod', 'stage', or 'dev' before running."
        )
        sys.exit(1)

    db_name = os.environ.get("DB_NAME", "odoo").strip()

    # ---- Validate config (hard-stops before any DB work) ----
    validate_config(env=env, db_name=db_name)

    # ---- Prod: always no-op ----
    norm_env = env.lower()
    if norm_env == "prod":
        log.info("IPAI_ENV=prod — no neutralization applied (live system).")
        emit_summary(
            env=env, db_name=db_name, dry_run=args.dry_run,
            mail_servers_changed=0, crons_changed=0,
            already_neutralized=None, status="PROD_NOOP",
        )
        sys.exit(0)

    # ---- Dry-run: no confirmation required ----
    if args.dry_run:
        log.info("IPAI_ENV=%s DB_NAME=%s — dry-run mode.", env, db_name)
        dry_run(env=env, db_name=db_name)
        sys.exit(0)

    # ---- Live run: require explicit confirmation ----
    confirm = os.environ.get("IPAI_NEUTRALIZE_CONFIRM", "").strip().upper()
    if confirm != "YES":
        log.error(
            "Live neutralization requires IPAI_NEUTRALIZE_CONFIRM=YES.\n"
            "  This prevents accidental writes from CI pipelines or scripts.\n"
            "  To preview changes without writing: add --dry-run flag.\n"
            "  To apply: export IPAI_NEUTRALIZE_CONFIRM=YES"
        )
        sys.exit(1)

    log.info("IPAI_ENV=%s DB_NAME=%s — applying live neutralization...", env, db_name)
    neutralize(env=env, db_name=db_name)


if __name__ == "__main__":
    main()
