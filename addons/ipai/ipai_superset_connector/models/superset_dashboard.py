# -*- coding: utf-8 -*-
"""
Superset Dashboard mapping model.

Maps Superset dashboard IDs to Odoo access controls and RLS configurations.
"""
from odoo import models, fields, api


class SupersetDashboard(models.Model):
    """
    Mapping between Superset dashboards and Odoo access control.

    Each record represents a Superset dashboard that can be embedded in Odoo.
    Access is controlled via Odoo groups, and RLS rules can be configured
    to scope data by company, user, or custom SQL clauses.
    """

    _name = "ipai.superset.dashboard"
    _description = "Superset Dashboard Configuration"
    _order = "sequence, name"

    name = fields.Char(
        string="Dashboard Name",
        required=True,
        help="Display name in Odoo (can differ from Superset title)",
    )
    superset_dashboard_id = fields.Char(
        string="Superset Dashboard ID",
        required=True,
        index=True,
        help="The numeric or UUID dashboard ID from Superset",
    )
    description = fields.Text(
        string="Description",
        help="Optional description shown to users",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Display order in dashboard list",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Inactive dashboards are hidden from users",
    )

    # Access Control
    allowed_group_ids = fields.Many2many(
        comodel_name="res.groups",
        relation="superset_dashboard_groups_rel",
        column1="dashboard_id",
        column2="group_id",
        string="Allowed Groups",
        help="If set, only users in these groups can access this dashboard. "
        "Leave empty to allow all authenticated users.",
    )

    # Row-Level Security Configuration
    rls_by_company = fields.Boolean(
        string="RLS by Company",
        default=True,
        help="Add RLS rule: company_id = <user's company>",
    )
    rls_by_user = fields.Boolean(
        string="RLS by User",
        default=False,
        help="Add RLS rule: user_id = <user's id>",
    )
    rls_custom_clause = fields.Char(
        string="Custom RLS Clause",
        help="Custom SQL clause for RLS. Placeholders: "
        "${company_id}, ${user_id}, ${user_login}",
    )

    # UI Configuration
    hide_title = fields.Boolean(
        string="Hide Dashboard Title",
        default=True,
        help="Hide the Superset dashboard title in embed",
    )
    hide_filters = fields.Boolean(
        string="Hide Filters",
        default=False,
        help="Hide the filter bar in embedded view",
    )
    hide_charts_controls = fields.Boolean(
        string="Hide Chart Controls",
        default=False,
        help="Hide chart control menus in embedded view",
    )

    # Audit
    audit_ids = fields.One2many(
        comodel_name="ipai.superset.audit",
        inverse_name="dashboard_id",
        string="Access Audit Log",
    )
    access_count = fields.Integer(
        string="Access Count",
        compute="_compute_access_count",
        store=False,
    )

    _sql_constraints = [
        (
            "superset_dashboard_id_unique",
            "UNIQUE(superset_dashboard_id)",
            "Superset Dashboard ID must be unique",
        ),
    ]

    @api.depends("audit_ids")
    def _compute_access_count(self):
        """Count total accesses from audit log."""
        for record in self:
            record.access_count = len(record.audit_ids)

    def action_view_audit_log(self):
        """Open audit log for this dashboard."""
        self.ensure_one()
        return {
            "name": f"Access Log: {self.name}",
            "type": "ir.actions.act_window",
            "res_model": "ipai.superset.audit",
            "view_mode": "list,form",
            "domain": [("dashboard_id", "=", self.id)],
            "context": {"default_dashboard_id": self.id},
        }

    def action_open_embed(self):
        """Open the embedded dashboard view."""
        self.ensure_one()
        return {
            "name": self.name,
            "type": "ir.actions.client",
            "tag": "ipai_superset_embed",
            "params": {
                "dashboard_id": self.superset_dashboard_id,
                "dashboard_name": self.name,
                "hide_title": self.hide_title,
                "hide_filters": self.hide_filters,
                "hide_charts_controls": self.hide_charts_controls,
            },
        }
