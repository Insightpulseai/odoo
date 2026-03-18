# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiPolicy(models.Model):
    """Company-level policy configuration for approvals and governance."""

    _name = "ipai.policy"
    _description = "IPAI Policy Configuration"

    name = fields.Char(string="Policy Name", required=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)

    # Approval policies
    require_attachment_for_bills = fields.Boolean(
        string="Require Attachment for Bills",
        default=True,
        help="Require at least one attachment for vendor bills before approval",
    )
    min_approval_amount = fields.Float(
        string="Min Approval Amount",
        default=5000.0,
        help="Minimum amount requiring manager approval",
    )
    max_approval_amount = fields.Float(
        string="Max Approval Amount",
        default=50000.0,
        help="Amount requiring director-level approval",
    )

    # Document policies
    enforce_dms_linking = fields.Boolean(
        string="Enforce DMS Linking",
        default=False,
        help="Require DMS folder linking for key documents (if DMS installed)",
    )

    @api.model
    def get_company_policy(self, company_id=None):
        """Get the active policy for a company."""
        company = company_id or self.env.company.id
        policy = self.search(
            [("company_id", "=", company), ("active", "=", True)],
            limit=1,
        )
        return policy
