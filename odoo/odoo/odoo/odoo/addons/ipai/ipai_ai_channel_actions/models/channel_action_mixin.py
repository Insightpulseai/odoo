"""
Odoo Copilot — Channel Action Mixin.

Lightweight mixin adding optional channel correlation fields to existing
business models. Applied via _inherit only where needed.

Does NOT create a new approval state machine. Uses Odoo's existing
mail.activity system for pending actions.
"""

from odoo import fields, models


class ChannelActionMixin(models.AbstractModel):
    """Mixin for tracking channel-originated business actions."""

    _name = "ipai.channel.action.mixin"
    _description = "Channel Action Tracking Mixin"

    channel_source = fields.Selection(
        [
            ("slack", "Slack"),
            ("teams", "Teams"),
            ("web", "Web Copilot"),
        ],
        string="Channel Source",
        readonly=True,
        copy=False,
        help="External channel from which this action was initiated.",
    )
    channel_ref = fields.Char(
        string="Channel Reference",
        readonly=True,
        copy=False,
        help="External reference (e.g., Slack message ts, Teams activity ID).",
    )
