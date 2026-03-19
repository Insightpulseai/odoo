#!/usr/bin/env python3
# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""
E2E test for ipai_zoho_mail_api — Zoho Mail REST API transport.

Run INSIDE the Odoo container (avoids XML-RPC None-marshal issue):

    docker cp scripts/mail/e2e_zoho_mail_test.py odoo-prod:/tmp/
    docker exec odoo-prod python3 /tmp/e2e_zoho_mail_test.py

Exits:
    0 — mail.mail.state='sent', delivery confirmed
    1 — mail.mail.state='exception', failure_reason printed
    2 — timed out waiting for terminal state
    3 — unexpected error

Environment:
    ODOO_DB   — database name (default: odoo_prod)
    TO_EMAIL  — recipient address (default: jake.tolentino@insightpulseai.com)
"""

import json
import logging
import os
import sys
import time

_logger = logging.getLogger("e2e_zoho_mail")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

ODOO_DB = os.environ.get("ODOO_DB", "odoo_prod")
TO_EMAIL = os.environ.get("TO_EMAIL", "jake.tolentino@insightpulseai.com")
POLL_TIMEOUT = 120  # seconds
POLL_INTERVAL = 5   # seconds


def _emit(status, mail_id=None, server=None, to=None, reason=None):
    """Print a single-line JSON result for CI/health-check consumers."""
    print(json.dumps({
        "status": status,   # PASS | EXCEPTION | TIMEOUT | ERROR
        "mail_id": mail_id,
        "server": server,
        "to": to or TO_EMAIL,
        "reason": reason,
        "stamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }), flush=True)


def main():
    try:
        import odoo.tools.config
        # DB_PASSWORD env var overrides the ${DB_PASSWORD} template in odoo.conf
        db_password = os.environ.get("DB_PASSWORD", "")
        parse_args = ["--config=/etc/odoo/odoo.conf"]
        if db_password:
            parse_args.append(f"--db_password={db_password}")
        odoo.tools.config.parse_config(parse_args)
        from odoo.modules.registry import Registry
        from odoo import api

        registry = Registry(ODOO_DB)
    except Exception as exc:
        _logger.error("Failed to initialise Odoo registry: %s", exc)
        _emit("ERROR", reason=str(exc))
        return 3

    try:
        with registry.cursor() as cr:
            env = api.Environment(cr, 1, {})  # uid=1 (admin)

            subject = f"[ipai_zoho_mail_api] E2E test {time.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            mail = env["mail.mail"].create({
                "subject": subject,
                "body_html": (
                    "<p>Zoho Mail REST API end-to-end delivery test.</p>"
                    "<p>If you received this, the HTTPS transport is working.</p>"
                ),
                "email_to": TO_EMAIL,
                "email_from": "noreply@insightpulseai.com",
            })
            mail_id = mail.id
            _logger.info("Created mail.mail id=%d subject=%r", mail_id, subject)

            mail.send()
            _logger.info("send() called — polling state (up to %ds)…", POLL_TIMEOUT)
            cr.commit()

        # Poll outside the write cursor to see committed state
        deadline = time.time() + POLL_TIMEOUT
        while time.time() < deadline:
            time.sleep(POLL_INTERVAL)
            with registry.cursor() as cr:
                env = api.Environment(cr, 1, {})
                rec = env["mail.mail"].browse(mail_id)
                state = rec.state
                reason = rec.failure_reason or ""

            _logger.info("  state=%r  failure_reason=%r", state, reason)

            if state == "sent":
                _logger.info("✅ SUCCESS — mail delivered via Zoho API (id=%d)", mail_id)
                _emit("PASS", mail_id=mail_id, server="Zoho Mail API", to=TO_EMAIL)
                return 0
            if state == "exception":
                _logger.error("❌ EXCEPTION (id=%d): %s", mail_id, reason)
                _emit("EXCEPTION", mail_id=mail_id, server="Zoho Mail API", reason=reason)
                return 1

        _logger.error("⏱  Timed out after %ds — last state=%r", POLL_TIMEOUT, state)
        _emit("TIMEOUT", mail_id=mail_id, reason=f"last_state={state}")
        return 2

    except Exception as exc:
        _logger.exception("Unexpected error: %s", exc)
        _emit("ERROR", reason=str(exc))
        return 3


if __name__ == "__main__":
    sys.exit(main())
