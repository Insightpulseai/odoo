# -*- coding: utf-8 -*-
"""
Superset Audit Log model.

Tracks every guest token issuance for security and usage analytics.
"""
from odoo import models, fields


class SupersetAudit(models.Model):
    """
    Audit log for Superset guest token issuance.

    Every time a user requests a guest token to view a dashboard,
    a record is created here for traceability.
    """
    _name = "ipai.superset.audit"
    _description = "Superset Dashboard Access Audit"
    _order = "create_date desc"
    _rec_name = "display_name"

    dashboard_id = fields.Many2one(
        comodel_name="ipai.superset.dashboard",
        string="Dashboard",
        required=True,
        ondelete="cascade",
        index=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        ondelete="set null",
        index=True,
    )
    rls_summary = fields.Char(
        string="RLS Rules Applied",
        help="Summary of Row-Level Security rules included in token",
    )
    ip_address = fields.Char(
        string="IP Address",
        help="Client IP address (if available)",
    )

    # Computed display name
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
    )

    @fields.depends("dashboard_id", "user_id", "create_date")
    def _compute_display_name(self):
        """Generate display name for tree views."""
        for record in self:
            dashboard_name = record.dashboard_id.name or "Unknown"
            user_name = record.user_id.name or "Unknown"
            date_str = record.create_date.strftime("%Y-%m-%d %H:%M") if record.create_date else ""
            record.display_name = f"{dashboard_name} - {user_name} ({date_str})"
