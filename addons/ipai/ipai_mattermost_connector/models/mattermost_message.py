# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MattermostMessage(models.Model):
    """Log of messages sent to/from Mattermost."""

    _name = "ipai.mattermost.message"
    _description = "Mattermost Message Log"
    _order = "create_date desc"

    connector_id = fields.Many2one(
        "ipai.integration.connector",
        required=True,
        ondelete="cascade"
    )
    channel_id = fields.Many2one(
        "ipai.mattermost.channel",
        ondelete="set null"
    )

    # Message details
    direction = fields.Selection([
        ("outbound", "Outbound (Odoo -> Mattermost)"),
        ("inbound", "Inbound (Mattermost -> Odoo)"),
    ], required=True)

    mm_post_id = fields.Char(index=True)
    mm_channel_id = fields.Char()
    mm_user_id = fields.Char()

    message = fields.Text()
    props_json = fields.Text(help="Additional message properties (JSON)")

    # Status
    state = fields.Selection([
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
    ], default="pending")
    error = fields.Text()

    # Related Odoo records
    res_model = fields.Char(help="Related Odoo model")
    res_id = fields.Integer(help="Related Odoo record ID")

    @api.model
    def log_outbound(self, connector, channel_id, message, result=None, error=None):
        """Log an outbound message."""
        return self.create({
            "connector_id": connector.id,
            "mm_channel_id": channel_id,
            "direction": "outbound",
            "message": message,
            "mm_post_id": result.get("id") if result else None,
            "state": "sent" if result else "failed",
            "error": error,
        })

    @api.model
    def log_inbound(self, connector, payload):
        """Log an inbound message/event."""
        return self.create({
            "connector_id": connector.id,
            "mm_channel_id": payload.get("channel_id"),
            "mm_user_id": payload.get("user_id"),
            "mm_post_id": payload.get("post_id"),
            "direction": "inbound",
            "message": payload.get("text"),
            "state": "delivered",
        })
