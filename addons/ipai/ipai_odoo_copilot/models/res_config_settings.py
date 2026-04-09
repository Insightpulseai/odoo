# -*- coding: utf-8 -*-

import logging
import urllib.error
import urllib.request

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # --- Pulser core ---
    ipai_copilot_enabled = fields.Boolean(
        string="Pulser Enabled",
        config_parameter="ipai.copilot.enabled",
    )
    ipai_copilot_gateway_url = fields.Char(
        string="Foundry Endpoint",
        config_parameter="ipai.copilot.foundry_endpoint",
        help="Azure AI Foundry project endpoint URL.",
    )
    ipai_copilot_mode = fields.Selection(
        selection=[
            ("PROD-ADVISORY", "Advisory (read-only, assisted)"),
            ("PROD-ASSISTED", "Assisted (read + limited write via queue)"),
            ("DEV", "Development (all tools)"),
        ],
        string="Operating Mode",
        config_parameter="ipai.copilot.mode",
        default="PROD-ADVISORY",
    )

    # --- Auth contract ---
    ipai_copilot_auth_mode = fields.Selection(
        selection=[
            ("managed_identity", "Managed Identity (production)"),
            ("api_key", "API Key (dev/emergency fallback)"),
        ],
        string="Auth Mode",
        config_parameter="ipai_copilot.foundry_auth_mode",
        default="managed_identity",
        help=(
            "Production: managed identity for Foundry, Search, and Fabric. "
            "API key: local dev or emergency fallback only. "
            "Managed identity requires Azure Container Apps with system-assigned identity."
        ),
    )
    ipai_copilot_api_key = fields.Char(
        string="API Key (fallback only)",
        config_parameter="ipai_copilot.foundry_api_key",
        help=(
            "Only used when auth mode is 'api_key'. "
            "In production, use managed identity instead. "
            "This key is stored in ir.config_parameter — "
            "prefer Azure Key Vault for runtime secrets."
        ),
    )
    ipai_copilot_agent_id = fields.Char(
        string="Foundry Agent ID",
        config_parameter="ipai_copilot.foundry_agent_id",
        help="Foundry assistant/agent ID (asst_* format).",
    )

    def action_test_pulser_connection(self):
        """Test the Foundry connection by verifying agent accessibility."""
        self.ensure_one()
        endpoint = (
            self.env['ir.config_parameter']
            .sudo()
            .get_param('ipai_copilot.foundry_endpoint', '')
        )
        if not endpoint:
            raise UserError(_('Foundry endpoint is not configured.'))

        # Test basic reachability of the endpoint
        health_url = endpoint.rstrip('/') + '/openai/models?api-version=2024-10-01-preview'
        api_key = (
            self.env['ir.config_parameter']
            .sudo()
            .get_param('ipai_copilot.foundry_api_key', '')
        )

        try:
            req = urllib.request.Request(health_url, method='GET')
            if api_key:
                req.add_header('api-key', api_key)
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.status
                body = resp.read().decode('utf-8', errors='replace')[:200]
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise UserError(
                    _('Auth failed (HTTP 401). Check API key or managed identity.')
                )
            raise UserError(
                _('Foundry returned HTTP %d: %s', e.code, e.reason)
            )
        except urllib.error.URLError as e:
            raise UserError(
                _('Foundry unreachable at %s — %s', endpoint, e.reason)
            )
        except Exception as e:
            raise UserError(_('Connection error: %s', str(e)))

        if status == 200:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Successful'),
                    'message': _('Foundry endpoint is reachable at %s', endpoint),
                    'type': 'success',
                    'sticky': False,
                },
            }
        raise UserError(
            _('Unexpected response: HTTP %d — %s', status, body)
        )
