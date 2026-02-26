# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""Zoho Mail OAuth2 + REST API client.

Reads credentials from ``ir.config_parameter`` (never from env vars directly).
Wire credentials using scripts/setup_zoho_mail_api.sh before first use.

Token cache: access_token + expires_at stored in ir.config_parameter so
restarts/worker rotations don't thrash the token endpoint.
"""

import logging
import time

import requests

_logger = logging.getLogger(__name__)

# ── ir.config_parameter keys ─────────────────────────────────────────────────
PARAM_CLIENT_ID = "ipai.zoho.client_id"
PARAM_CLIENT_SECRET = "ipai.zoho.client_secret"
PARAM_REFRESH_TOKEN = "ipai.zoho.refresh_token"
PARAM_ACCOUNT_ID = "ipai.zoho.account_id"
PARAM_ACCOUNTS_BASE = "ipai.zoho.accounts_base"
PARAM_MAIL_BASE = "ipai.zoho.mail_base"
PARAM_ACCESS_TOKEN = "ipai.zoho.access_token"
PARAM_EXPIRES_AT = "ipai.zoho.access_token_expires_at"  # stored as str(float epoch)

# Refresh 60 s before actual expiry so we never send an expired token.
_TOKEN_BUFFER_SECS = 60
_HTTP_TIMEOUT = 20  # seconds


class ZohoMailClient:
    """Stateless helper — pass the Odoo ``env`` on each call."""

    def __init__(self, env):
        self._env = env

    # ── Low-level param helpers ───────────────────────────────────────────────

    def _get(self, key, default=""):
        return self._env["ir.config_parameter"].sudo().get_param(key, default)

    def _set(self, key, value):
        self._env["ir.config_parameter"].sudo().set_param(key, str(value))

    # ── Token management ─────────────────────────────────────────────────────

    def get_access_token(self):
        """Return a valid access token, refreshing if expired."""
        try:
            expires_at = float(self._get(PARAM_EXPIRES_AT, "0"))
        except ValueError:
            expires_at = 0.0

        if time.time() < expires_at - _TOKEN_BUFFER_SECS:
            cached = self._get(PARAM_ACCESS_TOKEN)
            if cached:
                return cached

        return self._refresh_token()

    def _refresh_token(self):
        client_id = self._get(PARAM_CLIENT_ID)
        client_secret = self._get(PARAM_CLIENT_SECRET)
        refresh_token = self._get(PARAM_REFRESH_TOKEN)
        accounts_base = self._get(PARAM_ACCOUNTS_BASE) or "https://accounts.zoho.com"

        if not (client_id and client_secret and refresh_token):
            raise ValueError(
                "Zoho OAuth credentials not configured. "
                "Run scripts/setup_zoho_mail_api.sh to set them."
            )

        resp = requests.post(
            f"{accounts_base}/oauth/v2/token",
            data={
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
            },
            timeout=_HTTP_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        if "error" in data:
            raise ValueError(f"Zoho token refresh error: {data['error']}")

        access_token = data["access_token"]
        expires_in = int(data.get("expires_in", 3600))
        expires_at = time.time() + expires_in

        self._set(PARAM_ACCESS_TOKEN, access_token)
        self._set(PARAM_EXPIRES_AT, expires_at)

        _logger.info(
            "ipai_zoho_mail_api: access token refreshed (expires_in=%s s)", expires_in
        )
        return access_token

    # ── Send ─────────────────────────────────────────────────────────────────

    def send_message(
        self,
        *,
        from_addr,
        to_addrs,
        subject,
        html_body=None,
        text_body=None,
        cc_addrs=None,
        bcc_addrs=None,
        reply_to=None,
    ):
        """POST to Zoho Mail API. Raises RuntimeError on non-2xx response.

        Returns the full Zoho response dict.
        """
        account_id = self._get(PARAM_ACCOUNT_ID)
        mail_base = self._get(PARAM_MAIL_BASE) or "https://mail.zoho.com"

        if not account_id:
            raise ValueError(
                "ipai.zoho.account_id not configured. "
                "Run scripts/setup_zoho_mail_api.sh to set it."
            )

        access_token = self.get_access_token()

        def _join(addrs):
            if not addrs:
                return None
            return ", ".join(addrs) if isinstance(addrs, (list, tuple)) else addrs

        payload = {
            "fromAddress": from_addr,
            "toAddress": _join(to_addrs),
            "subject": subject,
            "content": html_body or text_body or "",
            "mailFormat": "html" if html_body else "plaintext",
        }
        if cc_addrs:
            payload["ccAddress"] = _join(cc_addrs)
        if bcc_addrs:
            payload["bccAddress"] = _join(bcc_addrs)
        if reply_to:
            payload["replyTo"] = reply_to

        resp = requests.post(
            f"{mail_base}/api/accounts/{account_id}/messages",
            headers={
                "Authorization": f"Zoho-oauthtoken {access_token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=_HTTP_TIMEOUT,
        )

        if not resp.ok:
            raise RuntimeError(
                f"Zoho Mail API error ({resp.status_code}): {resp.text}"
            )

        result = resp.json()
        status_code = result.get("status", {}).get("code", "?")
        msg_id = result.get("data", {}).get("messageId", "?")

        _logger.info(
            "ipai_zoho_mail_api: sent to=%r subject=%r zoho_code=%s messageId=%s",
            payload["toAddress"],
            subject,
            status_code,
            msg_id,
        )
        return result
