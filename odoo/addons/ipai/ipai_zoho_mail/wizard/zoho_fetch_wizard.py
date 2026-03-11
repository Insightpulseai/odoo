# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class IpaiZohoFetchWizard(models.TransientModel):
    """Wizard to manually trigger a Zoho IMAP fetch."""

    _name = "ipai.zoho.fetch.wizard"
    _description = "Zoho Mail Fetch Wizard"

    server_id = fields.Many2one(
        comodel_name="fetchmail.server",
        string="Incoming Mail Server",
        domain=[("server_type", "=", "imap")],
        required=True,
        help="Select the Zoho IMAP server to fetch mail from.",
    )

    date_from = fields.Datetime(
        string="Fetch From Date",
        help="Optional. Only fetch messages received on or after this date/time. "
        "Leave empty to fetch all pending messages.",
    )

    def action_fetch_now(self):
        """Trigger an immediate IMAP fetch on the selected server."""
        self.ensure_one()
        server = self.server_id

        if not server.active:
            raise UserError(
                _(
                    "The selected incoming mail server '%s' is not active. "
                    "Please activate it first.",
                    server.name,
                )
            )

        try:
            server._fetch_mails()
        except Exception as e:
            raise UserError(
                _(
                    "Fetch failed for server '%(server)s': %(error)s",
                    server=server.name,
                    error=str(e),
                )
            ) from e

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Mail Fetched"),
                "message": _(
                    "Fetch completed for '%(server)s'.", server=server.name
                ),
                "type": "success",
                "sticky": False,
            },
        }
