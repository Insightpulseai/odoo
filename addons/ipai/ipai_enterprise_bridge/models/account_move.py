# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    """Invoice/bill overlay for bridge integration."""

    _inherit = "account.move"

    # External sync tracking
    ipai_external_id = fields.Char(
        string="External Transaction ID",
        index=True,
        help="External system reference ID for sync",
    )
    ipai_exported = fields.Boolean(
        string="Exported to External System",
        default=False,
    )
    ipai_export_date = fields.Datetime(
        string="Export Date",
    )

    # BIR compliance fields (PH localization)
    ipai_bir_form_type = fields.Selection(
        [
            ("2307", "BIR Form 2307"),
            ("2316", "BIR Form 2316"),
            ("1601c", "BIR Form 1601-C"),
            ("2550m", "BIR Form 2550M"),
            ("2550q", "BIR Form 2550Q"),
        ],
        string="BIR Form Type",
        help="Philippine BIR tax form classification",
    )

    def action_mark_exported(self):
        """Mark invoice as exported to external system."""
        self.write({
            "ipai_exported": True,
            "ipai_export_date": fields.Datetime.now(),
        })
