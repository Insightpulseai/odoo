import json
import logging

import requests
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AiBridgeIpai(models.Model):
    """Extend ai.bridge with optional ipai.ai.provider routing."""

    _inherit = "ai.bridge"

    ipai_provider_id = fields.Many2one(
        "ipai.ai.provider",
        string="IPAI Provider",
        help="When set, bridge executions route through this provider "
        "instead of the default URL POST.",
    )

    def _execute(self, payload):
        """Override to route through ipai.ai.provider when configured."""
        if self.ipai_provider_id:
            return self._execute_via_ipai_provider(payload)
        return super()._execute(payload)

    def _execute_via_ipai_provider(self, payload):
        """Route execution through the IPAI provider (Supabase Edge Function)."""
        provider = self.ipai_provider_id
        endpoint = provider.endpoint_url
        token = provider.api_token

        if not endpoint:
            _logger.warning("IPAI provider %s has no endpoint_url", provider.name)
            return super()._execute(payload)

        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            resp = requests.post(
                endpoint,
                data=json.dumps(payload),
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            _logger.error(
                "IPAI provider %s execution failed: %s", provider.name, exc
            )
            raise
