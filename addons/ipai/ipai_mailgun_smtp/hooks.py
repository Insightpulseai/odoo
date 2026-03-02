# -*- coding: utf-8 -*-
# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""
post_install_hook: inject ODOO_MAILGUN_SMTP_PASSWORD into the ir.mail_server record.

The XML seed (data/ir_mail_server.xml) intentionally leaves smtp_pass empty.
This hook reads the env var and writes it once — idempotently — after install.

Secret management:
  - Local dev : set ODOO_MAILGUN_SMTP_PASSWORD in .env (gitignored)
  - Production: set via systemd EnvironmentFile or Docker --env-file (never committed)
  - Vault      : stored as mailgun_smtp_password in Supabase Vault
                 SSOT: ssot/secrets/registry.yaml#mailgun_smtp_password
"""
import logging
import os

_logger = logging.getLogger(__name__)

_SERVER_XMLID = "ipai_mailgun_smtp.mail_server_mailgun_smtp"
_ENV_VAR = "ODOO_MAILGUN_SMTP_PASSWORD"


def post_install_hook(env):
    """Idempotently set smtp_pass on the Mailgun ir.mail_server record.

    Called automatically by Odoo after ``ipai_mailgun_smtp`` is installed
    or upgraded (via the manifest ``post_install`` key).

    Does nothing if the env var is absent — this allows the module to install
    cleanly in CI/test environments where the password is not required.
    """
    password = os.environ.get(_ENV_VAR, "").strip()
    if not password:
        _logger.warning(
            "ipai_mailgun_smtp: %s not set — smtp_pass left empty. "
            "Set this env var before running Odoo in production.",
            _ENV_VAR,
        )
        return

    server = env.ref(_SERVER_XMLID, raise_if_not_found=False)
    if not server:
        _logger.error(
            "ipai_mailgun_smtp: mail server xmlid %r not found — "
            "password injection skipped.",
            _SERVER_XMLID,
        )
        return

    if server.smtp_pass == password:
        _logger.info(
            "ipai_mailgun_smtp: smtp_pass already up to date for %r, skipping.",
            server.name,
        )
        return

    server.sudo().write({"smtp_pass": password})
    _logger.info(
        "ipai_mailgun_smtp: smtp_pass injected for mail server %r (id=%s).",
        server.name,
        server.id,
    )
