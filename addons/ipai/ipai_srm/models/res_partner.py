# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    """Extend res.partner with SRM link."""

    _inherit = "res.partner"

    srm_supplier_id = fields.Many2one(
        "srm.supplier",
        string="SRM Profile",
        readonly=True,
    )
    srm_tier = fields.Selection(
        related="srm_supplier_id.tier",
        string="Supplier Tier",
    )
    srm_overall_score = fields.Float(
        related="srm_supplier_id.overall_score",
        string="SRM Score",
    )

    def action_view_srm_profile(self):
        """Open SRM profile for this partner."""
        self.ensure_one()
        if self.srm_supplier_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "srm.supplier",
                "view_mode": "form",
                "res_id": self.srm_supplier_id.id,
            }
        else:
            return {
                "type": "ir.actions.act_window",
                "res_model": "srm.supplier",
                "view_mode": "form",
                "context": {"default_partner_id": self.id},
            }
