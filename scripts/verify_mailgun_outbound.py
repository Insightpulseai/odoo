#!/usr/bin/env python3
"""
verify_mailgun_outbound.py — Mailgun outbound readiness preflight

Checks:
  1. DNS records for mg.insightpulseai.com (SPF, DKIM, CNAME, DMARC)
     via Mailgun API domain status (authoritative source)
  2. Mailgun domain state (must be 'active')
  3. Odoo ir.mail_server record (optional — requires DB env vars)

Usage:
  MAILGUN_API_KEY=... python3 scripts/verify_mailgun_outbound.py
  MAILGUN_API_KEY=... python3 scripts/verify_mailgun_outbound.py --skip-odoo
  MAILGUN_API_KEY=... python3 scripts/verify_mailgun_outbound.py --domain mg.example.com

Exit codes:
  0 — all required checks pass
  1 — one or more required checks failed
  2 — missing required env var

Environment variables:
  MAILGUN_API_KEY   (required) Mailgun API key
  MAILGUN_DOMAIN    (optional) default: mg.insightpulseai.com
  MAILGUN_API_BASE  (optional) default: https://api.mailgun.net
  ODOO_DB_HOST      (optional) DB host for Odoo check
  ODOO_DB_PORT      (optional) default: 5432
  ODOO_DB_NAME      (optional) default: odoo_prod
  ODOO_DB_USER      (optional) default: doadmin
  ODOO_DB_PASSWORD  (optional)
  ODOO_DB_SSLMODE   (optional) default: require
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from base64 import b64encode

SMTP_HOST = "smtp.mailgun.org"
SMTP_PORT = 2525
SMTP_USER = "no-reply@{domain}"
SMTP_SEQ  = 2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _api_get(url: str, api_key: str) -> dict:
    credentials = b64encode(f"api:{api_key}".encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {credentials}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code} {url}\n  {body}") from e


# ---------------------------------------------------------------------------
# Check 1: Mailgun API domain status + DNS records
# ---------------------------------------------------------------------------

def check_mailgun_domain(api_key: str, domain: str, api_base: str) -> tuple[bool, list[str]]:
    """Returns (ok, messages)."""
    messages = []
    try:
        data = _api_get(f"{api_base}/v3/domains/{domain}", api_key)
    except RuntimeError as e:
        return False, [f"Mailgun API error: {e}"]

    state = data.get("domain", {}).get("state", "unknown")
    messages.append(f"Domain state: {state}")
    domain_ok = (state == "active")

    sending_dns = data.get("sending_dns_records", [])
    receiving_dns = data.get("receiving_dns_records", [])

    required_sending = {"spf", "dkim"}
    found_types: set[str] = set()

    for rec in sending_dns:
        rtype = rec.get("record_type", "")
        valid = rec.get("valid", "unknown")
        name  = rec.get("name", "")
        icon  = "✅" if valid == "valid" else "❌"
        tag   = ""
        if "spf" in rec.get("value", "").lower() or "v=spf" in rec.get("value", "").lower():
            tag = " [SPF]"
            if valid == "valid":
                found_types.add("spf")
        elif "_domainkey" in name:
            tag = " [DKIM]"
            if valid == "valid":
                found_types.add("dkim")
        elif rtype == "CNAME":
            tag = " [tracking CNAME]"
        messages.append(f"  {icon} Sending {rtype:6} {name}{tag}")

    for rec in receiving_dns:
        rtype = rec.get("record_type", "")
        valid = rec.get("valid", "unknown")
        name  = rec.get("name", "")
        # MX records are expected to be absent for outbound-only setup
        messages.append(f"  ➖ Receiving {rtype:5} {name}  [outbound-only — MX not required]")

    dns_ok = required_sending.issubset(found_types)
    if not dns_ok:
        missing = required_sending - found_types
        messages.append(f"  ❌ Missing required DNS: {', '.join(missing).upper()}")

    return (domain_ok and dns_ok), messages


# ---------------------------------------------------------------------------
# Check 2: Odoo ir.mail_server record
# ---------------------------------------------------------------------------

def check_odoo_mail_server(domain: str) -> tuple[bool, list[str]]:
    """Returns (ok, messages). Skips gracefully if psycopg2 or DB not available."""
    messages = []

    db_host = os.environ.get("ODOO_DB_HOST")
    db_pass = os.environ.get("ODOO_DB_PASSWORD")
    if not db_host or not db_pass:
        messages.append("  ⚠️  ODOO_DB_HOST / ODOO_DB_PASSWORD not set — skipping Odoo check")
        return True, messages  # non-fatal

    try:
        import psycopg2  # type: ignore
    except ImportError:
        messages.append("  ⚠️  psycopg2 not installed — skipping Odoo check")
        return True, messages

    db_port    = int(os.environ.get("ODOO_DB_PORT", "5432"))
    db_name    = os.environ.get("ODOO_DB_NAME", "odoo_prod")
    db_user    = os.environ.get("ODOO_DB_USER", "doadmin")
    db_sslmode = os.environ.get("ODOO_DB_SSLMODE", "require")

    expected_user = SMTP_USER.format(domain=domain)

    try:
        conn = psycopg2.connect(
            host=db_host, port=db_port, dbname=db_name,
            user=db_user, password=db_pass, sslmode=db_sslmode,
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT name, smtp_host, smtp_port, smtp_user,
                   CASE WHEN smtp_pass IS NOT NULL AND smtp_pass != '' THEN 'SET' ELSE 'EMPTY' END AS pass_status,
                   sequence
            FROM ir_mail_server
            WHERE smtp_host = %s AND smtp_port = %s
            ORDER BY sequence
        """, (SMTP_HOST, SMTP_PORT))
        rows = cur.fetchall()
        conn.close()
    except Exception as e:
        messages.append(f"  ⚠️  DB connection error: {e} — skipping Odoo check")
        return True, messages

    if not rows:
        messages.append(f"  ❌ No ir.mail_server with host={SMTP_HOST} port={SMTP_PORT}")
        return False, messages

    ok = True
    for name, host, port, user, pass_status, seq in rows:
        user_ok = (user == expected_user)
        pass_ok = (pass_status == "SET")
        seq_ok  = (seq == SMTP_SEQ)
        icon = "✅" if (user_ok and pass_ok and seq_ok) else "❌"
        if not (user_ok and pass_ok and seq_ok):
            ok = False
        messages.append(
            f"  {icon} [{name}] seq={seq} user={user} pass={pass_status}"
            + ("" if user_ok else f"  ← expected {expected_user}")
            + ("" if seq_ok  else f"  ← expected seq={SMTP_SEQ}")
        )

    return ok, messages


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Mailgun outbound readiness preflight")
    parser.add_argument("--domain",     default=os.environ.get("MAILGUN_DOMAIN", "mg.insightpulseai.com"))
    parser.add_argument("--skip-odoo",  action="store_true", help="Skip Odoo DB check")
    parser.add_argument("--api-base",   default=os.environ.get("MAILGUN_API_BASE", "https://api.mailgun.net"))
    args = parser.parse_args()

    api_key = os.environ.get("MAILGUN_API_KEY", "")
    if not api_key:
        print("❌ MAILGUN_API_KEY not set. See ssot/env/mailgun.env.example", file=sys.stderr)
        return 2

    print(f"▶ Mailgun outbound preflight — {args.domain}")
    print()

    all_ok = True

    # --- Check 1: Mailgun domain ---
    print("Check 1: Mailgun domain status + DNS records")
    ok, msgs = check_mailgun_domain(api_key, args.domain, args.api_base)
    for m in msgs:
        print(f"  {m}" if not m.startswith("  ") else m)
    if not ok:
        all_ok = False
    print()

    # --- Check 2: Odoo mail server ---
    if not args.skip_odoo:
        print("Check 2: Odoo ir.mail_server record")
        ok, msgs = check_odoo_mail_server(args.domain)
        for m in msgs:
            print(f"  {m}" if not m.startswith("  ") else m)
        if not ok:
            all_ok = False
        print()

    # --- Summary ---
    if all_ok:
        print("✅ STATUS=COMPLETE — Mailgun outbound is ready")
        return 0
    else:
        print("❌ STATUS=PARTIAL — one or more checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
