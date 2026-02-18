# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiWorkosWorkspace(models.Model):
    """Workspace - Top-level container for organizing content."""

    _name = "ipai.workos.workspace"
    _description = "Work OS Workspace"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Name", required=True, tracking=True)
    description = fields.Text(string="Description")
    icon = fields.Char(string="Icon", default="folder")
    color = fields.Integer(string="Color Index", default=0)

    # Ownership
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
        required=True,
    )
    member_ids = fields.Many2many(
        "res.users",
        "workspace_member_rel",
        "workspace_id",
        "user_id",
        string="Members",
    )

    # Relations
    space_ids = fields.One2many(
        "ipai.workos.space",
        "workspace_id",
        string="Spaces",
    )
    space_count = fields.Integer(
        string="Spaces",
        compute="_compute_space_count",
    )

    # Status
    active = fields.Boolean(default=True)

    @api.depends("space_ids")
    def _compute_space_count(self):
        for record in self:
            record.space_count = len(record.space_ids)

    def action_view_spaces(self):
        """Open spaces in this workspace."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Spaces in {self.name}",
            "res_model": "ipai.workos.space",
            "view_mode": "tree,form",
            "domain": [("workspace_id", "=", self.id)],
            "context": {"default_workspace_id": self.id},
        }
