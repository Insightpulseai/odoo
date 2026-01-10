# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IntegrationConnector(models.Model):
    """Extend connector with n8n-specific functionality."""

    _inherit = "ipai.integration.connector"

    # n8n-specific fields
    n8n_webhook_url = fields.Char(
        string="Webhook Base URL",
        help="Base URL for n8n webhooks"
    )

    def action_test_connection(self):
        """Test connection to n8n API."""
        self.ensure_one()
        if self.connector_type != "n8n":
            return super().action_test_connection()

        from ..services.n8n_client import N8nClient

        try:
            client = N8nClient(self)
            result = client.health_check()
            if result:
                self.write({
                    "state": "testing",
                    "last_ping": fields.Datetime.now(),
                    "last_error": False,
                })
                self._log_audit("test_connection", "Connection successful")
            else:
                raise Exception("Health check returned unsuccessful status")
        except Exception as e:
            _logger.warning("n8n connection test failed: %s", e)
            self.write({
                "state": "error",
                "last_error": str(e),
            })
            self._log_audit("test_connection", f"Connection failed: {e}", level="error")

        return True

    def n8n_trigger_webhook(self, webhook_path, payload):
        """Trigger an n8n webhook."""
        self.ensure_one()
        if self.connector_type != "n8n":
            raise ValueError("Connector is not an n8n connector")

        from ..services.n8n_client import N8nClient

        client = N8nClient(self)
        return client.trigger_webhook(webhook_path, payload)

    def n8n_sync_workflows(self):
        """Sync workflows from n8n."""
        self.ensure_one()
        if self.connector_type != "n8n":
            raise ValueError("Connector is not an n8n connector")

        return self.env["ipai.n8n.workflow"].sync_workflows(self)
