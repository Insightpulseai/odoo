#!/usr/bin/env python3
"""
apply_mail_settings.py — Idempotent Odoo mail server configurator.

Reads config/odoo/mail_settings.yaml and upserts ir.mail_server and
fetchmail.server records via XML-RPC.

Usage:
    python3 scripts/odoo/apply_mail_settings.py --env prod
    python3 scripts/odoo/apply_mail_settings.py --env dev --dry-run
    python3 scripts/odoo/apply_mail_settings.py --env prod --verify

Environment variables required:
    ODOO_URL           Odoo base URL (e.g. https://erp.insightpulseai.com)
    ODOO_DB            Database name (e.g. odoo_prod)
    ODOO_USER          Admin username (e.g. admin)
    ODOO_PASSWORD      Admin password (or API key)
    ZOHO_SMTP_APP_PASSWORD  App password for SMTP
    ZOHO_IMAP_APP_PASSWORD  App password for IMAP (optional)
"""
import argparse
import os
import re
import sys
import xmlrpc.client
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = REPO_ROOT / "config" / "odoo" / "mail_settings.yaml"


def mask(value: str) -> str:
    """Mask a secret value for safe logging."""
    if not value or len(value) < 4:
        return "****"
    return value[:2] + "****"


def resolve_env_placeholders(value):
    """Replace ${ENV_VAR} tokens with actual env var values."""
    if not isinstance(value, str):
        return value
    pattern = re.compile(r"\$\{([^}]+)\}")
    def replacer(m):
        var = m.group(1)
        return os.environ.get(var, "")
    return pattern.sub(replacer, value)


def resolve_config(cfg: dict) -> dict:
    """Recursively resolve env placeholders in a config dict."""
    if isinstance(cfg, dict):
        return {k: resolve_config(v) for k, v in cfg.items()}
    if isinstance(cfg, list):
        return [resolve_config(i) for i in cfg]
    return resolve_env_placeholders(cfg)


def connect_odoo(url: str, db: str, user: str, password: str):
    """Connect to Odoo via XML-RPC. Returns (uid, models proxy)."""
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, user, password, {})
    if not uid:
        print(f"ERROR: Odoo authentication failed for user {user!r}")
        sys.exit(1)
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    return uid, models


def upsert_mail_server(models, uid, db, password, name: str, vals: dict, dry_run: bool):
    """Create or update ir.mail_server by name."""
    existing = models.execute_kw(db, uid, password, "ir.mail_server", "search",
                                  [[["name", "=", name]]])
    safe_vals = {k: (mask(v) if "pass" in k.lower() else v) for k, v in vals.items()}
    if existing:
        if not dry_run:
            models.execute_kw(db, uid, password, "ir.mail_server", "write",
                               [existing, vals])
        print(f"  SMTP {'[DRY-RUN] would update' if dry_run else 'updated'}: {name} → {safe_vals}")
    else:
        if not dry_run:
            models.execute_kw(db, uid, password, "ir.mail_server", "create", [vals])
        print(f"  SMTP {'[DRY-RUN] would create' if dry_run else 'created'}: {name} → {safe_vals}")


def upsert_fetchmail_server(models, uid, db, password, name: str, vals: dict, dry_run: bool):
    """Create or update fetchmail.server by name."""
    existing = models.execute_kw(db, uid, password, "fetchmail.server", "search",
                                  [[["name", "=", name]]])
    safe_vals = {k: (mask(v) if "pass" in k.lower() else v) for k, v in vals.items()}
    if existing:
        if not dry_run:
            models.execute_kw(db, uid, password, "fetchmail.server", "write",
                               [existing, vals])
        print(f"  IMAP {'[DRY-RUN] would update' if dry_run else 'updated'}: {name} → {safe_vals}")
    else:
        if not dry_run:
            models.execute_kw(db, uid, password, "fetchmail.server", "create", [vals])
        print(f"  IMAP {'[DRY-RUN] would create' if dry_run else 'created'}: {name} → {safe_vals}")


def verify(models, uid, db, password, smtp_name: str, imap_name: str):
    """Verify current state of mail server records."""
    smtp = models.execute_kw(db, uid, password, "ir.mail_server", "search_read",
                              [[["name", "=", smtp_name]]],
                              {"fields": ["name", "smtp_host", "smtp_port", "smtp_user", "active"]})
    imap = models.execute_kw(db, uid, password, "fetchmail.server", "search_read",
                              [[["name", "=", imap_name]]],
                              {"fields": ["name", "server", "port", "user", "active"]})
    print("\n[VERIFY]")
    if smtp:
        r = smtp[0]
        print(f"  SMTP: {r['name']} | host={r['smtp_host']}:{r['smtp_port']} | user={r['smtp_user']} | active={r['active']}")
    else:
        print(f"  SMTP: NOT FOUND ({smtp_name!r})")
    if imap:
        r = imap[0]
        print(f"  IMAP: {r['name']} | host={r['server']}:{r['port']} | user={r['user']} | active={r['active']}")
    else:
        print(f"  IMAP: NOT FOUND ({imap_name!r})")


def main():
    parser = argparse.ArgumentParser(description="Idempotent Odoo mail server configurator")
    parser.add_argument("--env", choices=["dev", "prod"], default="prod",
                        help="Target environment (default: prod)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would change without applying")
    parser.add_argument("--verify", action="store_true",
                        help="After applying, print current server state")
    parser.add_argument("--config", default=str(CONFIG_FILE),
                        help=f"Path to mail_settings.yaml (default: {CONFIG_FILE})")
    args = parser.parse_args()

    # Load config
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        raw = yaml.safe_load(f)
    cfg = resolve_config(raw.get(args.env, {}))

    # Odoo connection params
    odoo_url = os.environ.get("ODOO_URL", "http://localhost:8069").rstrip("/")
    odoo_db = os.environ.get("ODOO_DB", "odoo_prod" if args.env == "prod" else "odoo_dev")
    odoo_user = os.environ.get("ODOO_USER", "admin")
    odoo_pass = os.environ.get("ODOO_PASSWORD", "")
    if not odoo_pass:
        print("ERROR: ODOO_PASSWORD environment variable is required")
        sys.exit(1)

    print(f"[apply_mail_settings] env={args.env} url={odoo_url} db={odoo_db} dry_run={args.dry_run}")

    uid, models = connect_odoo(odoo_url, odoo_db, odoo_user, odoo_pass)

    # Apply SMTP
    smtp = cfg.get("smtp", {})
    if smtp:
        smtp_vals = {
            "name": smtp["name"],
            "smtp_host": smtp["host"],
            "smtp_port": smtp["port"],
            "smtp_encryption": smtp["encryption"],
            "smtp_user": smtp["user"],
            "smtp_pass": smtp.get("password", ""),
            "from_filter": smtp.get("from_filter", ""),
            "active": smtp.get("active", True),
            "sequence": smtp.get("sequence", 10),
        }
        upsert_mail_server(models, uid, odoo_db, odoo_pass, smtp["name"], smtp_vals, args.dry_run)

    # Apply IMAP
    imap = cfg.get("imap", {})
    if imap:
        imap_vals = {
            "name": imap["name"],
            "server": imap["host"],
            "port": imap["port"],
            "is_ssl": imap.get("ssl", True),
            "user": imap["user"],
            "password": imap.get("password", ""),
            "attach": imap.get("attach", True),
            "original": imap.get("original", True),
            "active": imap.get("active", True),
            "server_type": "imap",
            "state": "draft",
        }
        upsert_fetchmail_server(models, uid, odoo_db, odoo_pass, imap["name"], imap_vals, args.dry_run)

    if args.verify:
        verify(models, uid, odoo_db, odoo_pass,
               smtp.get("name", ""), imap.get("name", ""))

    print("[apply_mail_settings] Done.")


if __name__ == "__main__":
    main()
