# -*- coding: utf-8 -*-
# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""
post_install_hook: inject ODOO_MAILGUN_SMTP_PASSWORD and disable competing mail servers.

The XML seed (data/ir_mail_server.xml) intentionally leaves smtp_pass empty.
This hook reads the env var and writes it once — idempotently — after install.

It also deactivates any competing outgoing mail server (e.g. Zoho API) in prod,
so that Mailgun is deterministically the only active sender.

Secret management:
  - Local dev : set ODOO_MAILGUN_SMTP_PASSWORD in .env (gitignored)
  - Production: set via systemd EnvironmentFile or Docker --env-file (never committed)
  - Vault      : stored as odoo_mailgun_smtp_password in Supabase Vault
                 SSOT: ssot/secrets/registry.yaml#odoo_mailgun_smtp_password

Prod detection (for competitor deactivation):
  - Primary  : RUNNING_ENV=prod environment variable
  - Fallback : web.base.url contains 'insightpulseai.com'
"""
import logging
import os

_logger = logging.getLogger(__name__)

_SERVER_XMLID = "ipai_mailgun_smtp.mail_server_mailgun_smtp"
_ENV_VAR = "ODOO_MAILGUN_SMTP_PASSWORD"
_RUNNING_ENV_VAR = "RUNNING_ENV"

# Zoho server xmlid — may or may not be installed; handled gracefully
_ZOHO_XMLID = "ipai_zoho_mail_api.mail_server_zoho_api"
# Competing servers are bumped to this sequence floor when deactivated
_COMPETING_SEQUENCE_FLOOR = 20


def _is_prod(env):
    """Return True when running in the production Odoo environment.

    Primary  : RUNNING_ENV=prod env var (set in Docker env / systemd EnvironmentFile).
    Fallback : web.base.url contains 'insightpulseai.com' (always present in prod DB).
    """
    running_env = os.environ.get(_RUNNING_ENV_VAR, "").strip().lower()
    if running_env:
        return running_env == "prod"
    base_url = (
        env["ir.config_parameter"].sudo().get_param("web.base.url", default="")
    )
    return "insightpulseai.com" in base_url


def _disable_competing_servers(env):
    """Deactivate ir.mail_server records that compete with the Mailgun primary.

    Only runs in prod (RUNNING_ENV=prod or web.base.url contains prod domain).
    Idempotent — safe to call on every install/upgrade.

    Strategy
    --------
    1. Resolve the authoritative Mailgun server by xmlid — never touched.
    2. Collect competitors via:
       a. Known Zoho xmlid (ipai_zoho_mail_api.mail_server_zoho_api)
       b. Any active server whose smtp_host contains 'zoho' (catches renamed records)
    3. Set active=False and sequence >= _COMPETING_SEQUENCE_FLOOR on each.
    """
    if not _is_prod(env):
        _logger.info(
            "ipai_mailgun_smtp: non-prod environment — skipping competitor deactivation."
        )
        return

    # The authoritative Mailgun server must never be touched
    mailgun = env.ref(_SERVER_XMLID, raise_if_not_found=False)
    safe_ids = {mailgun.id} if mailgun else set()

    # Collect competitor candidates
    MailServer = env["ir.mail_server"].sudo()
    candidates = MailServer.browse()

    # 1a. Known Zoho xmlid (module may or may not be installed)
    zoho_by_xmlid = env.ref(_ZOHO_XMLID, raise_if_not_found=False)
    if zoho_by_xmlid:
        candidates |= zoho_by_xmlid

    # 1b. Any active server with smtp_host containing "zoho"
    zoho_by_host = MailServer.search(
        [("smtp_host", "ilike", "zoho"), ("active", "=", True)]
    )
    if zoho_by_host:
        candidates |= zoho_by_host

    to_deactivate = candidates.filtered(
        lambda s: s.id not in safe_ids and s.active
    )

    if not to_deactivate:
        _logger.info(
            "ipai_mailgun_smtp: no competing active mail servers found."
        )
        return

    for server in to_deactivate:
        new_seq = max(server.sequence or 0, _COMPETING_SEQUENCE_FLOOR)
        server.write({"active": False, "sequence": new_seq})
        _logger.info(
            "ipai_mailgun_smtp: deactivated competing server %r "
            "(id=%s, host=%s, sequence→%s).",
            server.name,
            server.id,
            server.smtp_host,
            new_seq,
        )


def post_install_hook(env):
    """Idempotently inject smtp_pass and disable competing mail servers.

    Called automatically by Odoo after ``ipai_mailgun_smtp`` is installed
    or upgraded (via the manifest ``post_install`` key).

    Password injection is skipped (with a warning) when ODOO_MAILGUN_SMTP_PASSWORD
    is absent — this allows the module to install cleanly in CI environments.

    Competitor deactivation always runs but is a no-op outside prod.
    """
    # ── Password injection ────────────────────────────────────────────────────
    password = os.environ.get(_ENV_VAR, "").strip()
    if not password:
        _logger.warning(
            "ipai_mailgun_smtp: %s not set — smtp_pass left empty. "
            "Set this env var before running Odoo in production.",
            _ENV_VAR,
        )
    else:
        server = env.ref(_SERVER_XMLID, raise_if_not_found=False)
        if not server:
            _logger.error(
                "ipai_mailgun_smtp: mail server xmlid %r not found — "
                "password injection skipped.",
                _SERVER_XMLID,
            )
        elif server.smtp_pass == password:
            _logger.info(
                "ipai_mailgun_smtp: smtp_pass already up to date for %r, skipping.",
                server.name,
            )
        else:
            server.sudo().write({"smtp_pass": password})
            _logger.info(
                "ipai_mailgun_smtp: smtp_pass injected for mail server %r (id=%s).",
                server.name,
                server.id,
            )

    # ── Competitor deactivation (prod-gated) ─────────────────────────────────
    _disable_competing_servers(env)
