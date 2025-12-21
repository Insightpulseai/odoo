# -*- coding: utf-8 -*-
"""
A1 Workstream

Represents organizational units/streams that own task templates.
Maps to close.task.category in the close orchestration module.
"""
from odoo import api, fields, models


class A1Workstream(models.Model):
    """
    Workstream representing an organizational unit.

    Examples: Finance Ops, Tax Compliance, Treasury, etc.
    """

    _name = "a1.workstream"
    _description = "A1 Workstream"
    _order = "sequence, code"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _sql_constraints = [
        ("code_uniq", "unique(code, company_id)", "Workstream code must be unique per company."),
    ]

    # Core fields
    code = fields.Char(
        string="Code",
        required=True,
        index=True,
        tracking=True,
        help="Unique identifier like 'FIN_OPS', 'TAX_COMP'",
    )
    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)

    # Hierarchy
    phase_code = fields.Char(
        string="Phase Code",
        help="Parent phase identifier (e.g., 'CLOSE', 'REPORT')",
    )

    # Ownership
    owner_role_id = fields.Many2one(
        "a1.role",
        string="Owner Role",
        help="Primary role responsible for this workstream",
    )
    owner_user_id = fields.Many2one(
        "res.users",
        string="Owner User",
        compute="_compute_owner_user",
        store=True,
    )

    # Templates
    template_ids = fields.One2many(
        "a1.template",
        "workstream_id",
        string="Task Templates",
    )
    template_count = fields.Integer(
        string="Template Count",
        compute="_compute_template_count",
    )

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    # Bridge to close orchestration
    close_category_id = fields.Many2one(
        "close.task.category",
        string="Close Category",
        help="Linked category in Close Orchestration module",
    )

    # Description
    description = fields.Html(
        string="Description",
        help="Detailed description of workstream scope",
    )

    @api.depends("owner_role_id")
    def _compute_owner_user(self):
        """Resolve owner role to default user."""
        for ws in self:
            if ws.owner_role_id:
                ws.owner_user_id = self.env["a1.role"].resolve_user(
                    ws.owner_role_id.code,
                    ws.company_id.id,
                )
            else:
                ws.owner_user_id = False

    @api.depends("template_ids")
    def _compute_template_count(self):
        for ws in self:
            ws.template_count = len(ws.template_ids)

    def action_view_templates(self):
        """Open templates for this workstream."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Templates - {self.name}",
            "res_model": "a1.template",
            "view_mode": "tree,form",
            "domain": [("workstream_id", "=", self.id)],
            "context": {"default_workstream_id": self.id},
        }
