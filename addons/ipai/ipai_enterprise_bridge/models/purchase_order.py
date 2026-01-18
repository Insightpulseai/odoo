# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    """Purchase order overlay for bridge integration."""

    _inherit = "purchase.order"

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

    # Supplier catalog reference
    ipai_supplier_catalog_ref = fields.Char(
        string="Supplier Catalog Reference",
        help="Reference to supplier's catalog system",
    )

    def action_mark_exported(self):
        """Mark PO as exported to external system."""
        self.write({
            "ipai_exported": True,
            "ipai_export_date": fields.Datetime.now(),
        })
