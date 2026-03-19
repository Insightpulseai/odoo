# -*- coding: utf-8 -*-

import logging
import urllib.request
import urllib.error

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Copilot gateway
    ipai_copilot_enabled = fields.Boolean(
        string="Copilot Enabled",
        config_parameter="ipai.copilot.enabled",
    )
    ipai_copilot_gateway_url = fields.Char(
        string="Gateway URL",
        config_parameter="ipai.copilot.gateway_url",
        help="URL of the agent-platform gateway service.",
    )
    ipai_copilot_mode = fields.Selection(
        selection=[
            ("PROD-ADVISORY", "Advisory (read-only, assisted)"),
            ("PROD-ASSISTED", "Assisted (read + limited write)"),
            ("DEV", "Development (all tools)"),
        ],
        string="Operating Mode",
        config_parameter="ipai.copilot.mode",
        default="PROD-ADVISORY",
    )

    def action_test_copilot_connection(self):
        """Test the gateway connection by hitting its health endpoint."""
        self.ensure_one()
        gateway_url = (
            self.env['ir.config_parameter']
            .sudo()
            .get_param('ipai.copilot.gateway_url', '')
        )
        if not gateway_url:
            raise UserError(_('Gateway URL is not configured.'))

        health_url = gateway_url.rstrip('/') + '/health'
        try:
            req = urllib.request.Request(health_url, method='GET')
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = resp.status
                body = resp.read().decode('utf-8', errors='replace')[:200]
        except urllib.error.HTTPError as e:
            raise UserError(
                _('Gateway returned HTTP %d: %s', e.code, e.reason)
            )
        except urllib.error.URLError as e:
            raise UserError(
                _('Gateway unreachable at %s — %s', health_url, e.reason)
            )
        except Exception as e:
            raise UserError(_('Connection error: %s', str(e)))

        if status == 200:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Successful'),
                    'message': _('Gateway is reachable at %s', gateway_url),
                    'type': 'success',
                    'sticky': False,
                },
            }
        raise UserError(
            _('Unexpected response: HTTP %d — %s', status, body)
        )
