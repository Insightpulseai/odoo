#!/usr/bin/env python3
# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""
E2E test for Odoo outbound mail via Mailgun SMTP (smtp.mailgun.org:2525).

Run INSIDE the Odoo container:

    docker cp scripts/mail/e2e_mailgun_text.py odoo-prod:/tmp/
    docker exec odoo-prod python3 /tmp/e2e_mailgun_text.py

Exits:
    0 — mail.mail.state='sent', delivery confirmed
    1 — mail.mail.state='exception', failure_reason printed
    2 — timed out waiting for terminal state
    3 — unexpected error

Environment:
    ODOO_DB    — database name (default: odoo_prod)
    TO_EMAIL   — recipient address (default: jgtolentino.rn@gmail.com)
    DB_PASSWORD — optional, overrides ${DB_PASSWORD} template in odoo.conf
"""

import json
import logging
import os
import sys
import time

_logger = logging.getLogger("e2e_mailgun_text")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

ODOO_DB = os.environ.get("ODOO_DB", "odoo_prod")
TO_EMAIL = os.environ.get("TO_EMAIL", "jgtolentino.rn@gmail.com")
FROM_EMAIL = "no-reply@mg.insightpulseai.com"
TRANSPORT = "smtp.mailgun.org:2525"
POLL_TIMEOUT = 60   # seconds
POLL_INTERVAL = 5   # seconds


def _emit(status, mail_id=None, server=None, to=None, reason=None):
    """Print a single-line JSON result for CI/health-check consumers."""
    print(json.dumps({
        "status": status,   # PASS | EXCEPTION | TIMEOUT | ERROR
        "mail_id": mail_id,
        "server": server,
        "transport": TRANSPORT,
        "to": to or TO_EMAIL,
        "reason": reason,
        "stamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }), flush=True)


def main():
    try:
        import odoo.tools.config
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

            # Locate Mailgun SMTP server
            mg = env["ir.mail_server"].search([
                ("smtp_host", "=", "smtp.mailgun.org"),
                ("smtp_port", "=", 2525),
            ], limit=1)
            if not mg:
                _logger.error("No ir.mail_server with smtp.mailgun.org:2525 found")
                _emit("ERROR", reason="mailgun server not configured")
                return 3

            server_name = mg.name
            _logger.info("Using mail server: %r (id=%d)", server_name, mg.id)

            stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            subject = f"E2E-MAILGUN-ODOO-TEXT {stamp}"
            body = (
                f"Odoo -> Mailgun SMTP end-to-end text delivery test.\n\n"
                f"from:      {FROM_EMAIL}\n"
                f"to:        {TO_EMAIL}\n"
                f"transport: {TRANSPORT}\n"
                f"stamp:     {stamp}\n\n"
                f"If you received this, outbound via smtp.mailgun.org:2525 is working."
            )

            mail = env["mail.mail"].sudo().create({
                "subject": subject,
                "body_html": f"<pre>{body}</pre>",
                "email_from": FROM_EMAIL,
                "email_to": TO_EMAIL,
                "auto_delete": False,
                "mail_server_id": mg.id,
            })
            mail_id = mail.id
            _logger.info("Created mail.mail id=%d subject=%r", mail_id, subject)

            mail.send()
            _logger.info("send() called -- polling state (up to %ds)...", POLL_TIMEOUT)
            cr.commit()

        # Poll outside write cursor to see committed state
        state = "outgoing"
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
                _logger.info("PASS -- delivered via %s (id=%d)", TRANSPORT, mail_id)
                _emit("PASS", mail_id=mail_id, server=server_name, to=TO_EMAIL)
                return 0
            if state == "exception":
                _logger.error("EXCEPTION (id=%d): %s", mail_id, reason)
                _emit("EXCEPTION", mail_id=mail_id, server=server_name, reason=reason)
                return 1

        _logger.error("Timed out after %ds -- last state=%r", POLL_TIMEOUT, state)
        _emit("TIMEOUT", mail_id=mail_id, server=server_name, reason=f"last_state={state}")
        return 2

    except Exception as exc:
        _logger.exception("Unexpected error: %s", exc)
        _emit("ERROR", reason=str(exc))
        return 3


if __name__ == "__main__":
    sys.exit(main())
