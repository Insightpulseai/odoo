# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MattermostChannel(models.Model):
    """Cached Mattermost channel information."""

    _name = "ipai.mattermost.channel"
    _description = "Mattermost Channel"
    _order = "display_name"

    connector_id = fields.Many2one(
        "ipai.integration.connector",
        required=True,
        ondelete="cascade",
        domain="[('connector_type', '=', 'mattermost')]"
    )

    # Mattermost IDs
    mm_channel_id = fields.Char(required=True, index=True)
    mm_team_id = fields.Char(index=True)

    # Channel info
    name = fields.Char(required=True)
    display_name = fields.Char()
    channel_type = fields.Selection([
        ("O", "Open"),
        ("P", "Private"),
        ("D", "Direct"),
        ("G", "Group"),
    ])
    header = fields.Text()
    purpose = fields.Text()

    # Sync status
    last_sync = fields.Datetime()
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("channel_uniq", "unique(connector_id, mm_channel_id)",
         "Channel already exists for this connector!"),
    ]

    @api.model
    def sync_channels(self, connector):
        """Sync channels from Mattermost API."""
        from ..services.mattermost_client import MattermostClient

        client = MattermostClient(connector)
        channels = client.get_channels(connector.mm_team_id)

        for ch in channels:
            existing = self.search([
                ("connector_id", "=", connector.id),
                ("mm_channel_id", "=", ch["id"]),
            ], limit=1)

            vals = {
                "connector_id": connector.id,
                "mm_channel_id": ch["id"],
                "mm_team_id": ch.get("team_id"),
                "name": ch["name"],
                "display_name": ch.get("display_name", ch["name"]),
                "channel_type": ch.get("type"),
                "header": ch.get("header"),
                "purpose": ch.get("purpose"),
                "last_sync": fields.Datetime.now(),
            }

            if existing:
                existing.write(vals)
            else:
                self.create(vals)

        return True
