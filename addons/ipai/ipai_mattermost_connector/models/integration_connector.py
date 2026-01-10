# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IntegrationConnector(models.Model):
    """Extend connector with Mattermost-specific functionality."""

    _inherit = "ipai.integration.connector"

    # Mattermost-specific fields
    mm_team_id = fields.Char(
        string="Default Team ID",
        help="Mattermost team ID for default operations"
    )
    mm_default_channel_id = fields.Char(
        string="Default Channel ID",
        help="Default channel for notifications"
    )

    def action_test_connection(self):
        """Test connection to Mattermost API."""
        self.ensure_one()
        if self.connector_type != "mattermost":
            return super().action_test_connection()

        from ..services.mattermost_client import MattermostClient

        try:
            client = MattermostClient(self)
            result = client.ping()
            if result:
                self.write({
                    "state": "testing",
                    "last_ping": fields.Datetime.now(),
                    "last_error": False,
                })
                self._log_audit("test_connection", "Connection successful")
            else:
                raise Exception("Ping returned unsuccessful status")
        except Exception as e:
            _logger.warning("Mattermost connection test failed: %s", e)
            self.write({
                "state": "error",
                "last_error": str(e),
            })
            self._log_audit("test_connection", f"Connection failed: {e}", level="error")

        return True

    def mm_post_message(self, channel_id, message, props=None):
        """Post a message to a Mattermost channel."""
        self.ensure_one()
        if self.connector_type != "mattermost":
            raise ValueError("Connector is not a Mattermost connector")

        from ..services.mattermost_client import MattermostClient

        client = MattermostClient(self)
        return client.post_message(channel_id, message, props)
