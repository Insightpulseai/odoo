"""Supabase bridge configuration (singleton via ir.config_parameter)."""

import hashlib
import hmac
import json
import logging
import time

import requests

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PARAM_PREFIX = "ipai_llm_supabase_bridge"


class IpaiBridgeConfig(models.TransientModel):
    """Settings UI for the Supabase bridge. Persisted via ir.config_parameter."""

    _name = "ipai.bridge.config"
    _description = "IPAI Supabase Bridge Configuration"

    webhook_url = fields.Char(
        string="Webhook URL",
        help="Supabase Edge Function URL for event ingestion "
             "(e.g. https://<ref>.supabase.co/functions/v1/llm-webhook-ingest)",
    )
    webhook_secret = fields.Char(
        string="HMAC Signing Secret",
        help="Shared secret for HMAC-SHA256 webhook signatures",
    )
    enabled = fields.Boolean(
        string="Bridge Enabled",
        default=False,
    )
    max_retries = fields.Integer(
        string="Max Retries",
        default=5,
        help="Maximum retry attempts for failed webhook deliveries",
    )
    retry_backoff_base = fields.Integer(
        string="Backoff Base (seconds)",
        default=60,
        help="Base delay for exponential backoff between retries",
    )
    batch_size = fields.Integer(
        string="Batch Size",
        default=50,
        help="Number of events to send per webhook call",
    )

    # ---- Persistence helpers via ir.config_parameter ----

    def _get_param(self, key, default=""):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(f"{PARAM_PREFIX}.{key}", default)
        )

    def _set_param(self, key, value):
        self.env["ir.config_parameter"].sudo().set_param(
            f"{PARAM_PREFIX}.{key}", value
        )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res.update(
            {
                "webhook_url": self._get_param("webhook_url"),
                "webhook_secret": self._get_param("webhook_secret"),
                "enabled": self._get_param("enabled", "False") == "True",
                "max_retries": int(self._get_param("max_retries", "5")),
                "retry_backoff_base": int(
                    self._get_param("retry_backoff_base", "60")
                ),
                "batch_size": int(self._get_param("batch_size", "50")),
            }
        )
        return res

    def action_save(self):
        self.ensure_one()
        self._set_param("webhook_url", self.webhook_url or "")
        self._set_param("webhook_secret", self.webhook_secret or "")
        self._set_param("enabled", str(self.enabled))
        self._set_param("max_retries", str(self.max_retries))
        self._set_param("retry_backoff_base", str(self.retry_backoff_base))
        self._set_param("batch_size", str(self.batch_size))
        return {"type": "ir.actions.act_window_close"}

    def action_test_connection(self):
        """Send a ping event to verify webhook connectivity."""
        self.ensure_one()
        if not self.webhook_url:
            raise UserError("Webhook URL is required.")
        payload = {
            "event_type": "bridge.ping",
            "source": "odoo",
            "odoo_db": self.env.cr.dbname,
            "timestamp": fields.Datetime.now().isoformat(),
        }
        try:
            _send_webhook(
                self.webhook_url,
                self.webhook_secret or "",
                payload,
                timeout=10,
            )
        except Exception as e:
            raise UserError(f"Connection test failed: {e}") from e
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Success",
                "message": "Supabase webhook responded OK.",
                "type": "success",
                "sticky": False,
            },
        }


# ---- Module-level helpers (importable by other models) ----


def _sign_payload(secret: str, body_bytes: bytes) -> str:
    """HMAC-SHA256 signature for webhook payload."""
    return hmac.new(
        secret.encode(), body_bytes, hashlib.sha256
    ).hexdigest()


def _send_webhook(url: str, secret: str, payload: dict, timeout: int = 15):
    """POST a signed JSON payload to the Supabase Edge Function."""
    body = json.dumps(payload, default=str).encode()
    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": f"sha256={_sign_payload(secret, body)}",
        "X-Source": "odoo-llm-bridge",
    }
    resp = requests.post(url, data=body, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp
