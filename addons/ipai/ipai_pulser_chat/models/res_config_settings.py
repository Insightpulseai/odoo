# -*- coding: utf-8 -*-

import urllib.parse

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ipai_pulser_chat_enabled = fields.Boolean(
        string="Pulser Chat Enabled",
        config_parameter="ipai.pulser_chat.enabled",
        help=(
            "Show the Pulser chat shell in the Odoo systray. "
            "Requires a valid Backend URL to be functional."
        ),
    )
    ipai_pulser_chat_backend_url = fields.Char(
        string="Pulser Chat Backend URL",
        config_parameter="ipai.pulser_chat.backend_url",
        help=(
            "Absolute http/https URL of the external Pulser chat endpoint. "
            "Example: https://pulser.example.com/api/chat"
        ),
    )
    ipai_pulser_chat_timeout_seconds = fields.Integer(
        string="Pulser Chat Timeout (seconds)",
        config_parameter="ipai.pulser_chat.timeout_seconds",
        default=30,
        help=(
            "Seconds Odoo waits for the external Pulser backend to respond. "
            "Minimum 5, maximum 120."
        ),
    )

    @api.constrains("ipai_pulser_chat_backend_url")
    def _check_backend_url(self):
        """Reject non-HTTP/HTTPS or relative backend URL values at save time."""
        for record in self:
            url = (record.ipai_pulser_chat_backend_url or "").strip()
            if not url:
                # Empty URL is allowed; the feature simply won't be functional.
                continue
            try:
                parsed = urllib.parse.urlparse(url)
            except Exception:
                raise ValidationError(
                    _("Pulser Chat Backend URL is not a valid URL.")
                )
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                raise ValidationError(
                    _(
                        "Pulser Chat Backend URL must be an absolute http or https URL. "
                        "Received: %s"
                    )
                    % url
                )

    @api.constrains("ipai_pulser_chat_timeout_seconds")
    def _check_timeout(self):
        """Enforce the 5–120 s timeout range at the model layer."""
        for record in self:
            t = record.ipai_pulser_chat_timeout_seconds
            if t is not False and t is not None:
                if not (5 <= t <= 120):
                    raise ValidationError(
                        _("Pulser Chat Timeout must be between 5 and 120 seconds.")
                    )
