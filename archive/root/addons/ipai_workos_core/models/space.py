# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiWorkosSpace(models.Model):
    """Space - Container within a workspace for organizing pages."""

    _name = "ipai.workos.space"
    _description = "Work OS Space"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    name = fields.Char(string="Name", required=True, tracking=True)
    description = fields.Text(string="Description")
    icon = fields.Char(string="Icon", default="folder-open")
    color = fields.Integer(string="Color Index", default=0)
    sequence = fields.Integer(string="Sequence", default=10)

    # Parent workspace
    workspace_id = fields.Many2one(
        "ipai.workos.workspace",
        string="Workspace",
        required=True,
        ondelete="cascade",
    )

    # Visibility
    visibility = fields.Selection(
        [
            ("private", "Private"),
            ("shared", "Shared"),
        ],
        string="Visibility",
        default="shared",
        required=True,
    )

    # Pages in this space
    page_ids = fields.One2many(
        "ipai.workos.page",
        "space_id",
        string="Pages",
        domain=[("parent_id", "=", False)],  # Only root pages
    )
    page_count = fields.Integer(
        string="Pages",
        compute="_compute_page_count",
    )

    # Status
    active = fields.Boolean(default=True)

    @api.depends("page_ids")
    def _compute_page_count(self):
        for record in self:
            record.page_count = self.env["ipai.workos.page"].search_count(
                [("space_id", "=", record.id)]
            )

    def action_view_pages(self):
        """Open pages in this space."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Pages in {self.name}",
            "res_model": "ipai.workos.page",
            "view_mode": "tree,form",
            "domain": [("space_id", "=", self.id)],
            "context": {"default_space_id": self.id},
        }
