# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IntegrationConnector(models.Model):
    """Extend connector with Focalboard-specific functionality."""

    _inherit = "ipai.integration.connector"

    # Focalboard-specific fields
    fb_workspace_id = fields.Char(
        string="Workspace ID",
        help="Focalboard workspace/team ID"
    )
    fb_default_board_id = fields.Char(
        string="Default Board ID",
        help="Default board for new cards"
    )

    def action_test_connection(self):
        """Test connection to Focalboard API."""
        self.ensure_one()
        if self.connector_type != "focalboard":
            return super().action_test_connection()

        from ..services.focalboard_client import FocalboardClient

        try:
            client = FocalboardClient(self)
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
            _logger.warning("Focalboard connection test failed: %s", e)
            self.write({
                "state": "error",
                "last_error": str(e),
            })
            self._log_audit("test_connection", f"Connection failed: {e}", level="error")

        return True

    def fb_sync_boards(self):
        """Sync boards from Focalboard."""
        self.ensure_one()
        if self.connector_type != "focalboard":
            raise ValueError("Connector is not a Focalboard connector")

        return self.env["ipai.focalboard.board"].sync_boards(self)
