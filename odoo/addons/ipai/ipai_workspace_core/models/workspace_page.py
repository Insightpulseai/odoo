# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, fields, models


class IpaiWorkspacePage(models.Model):
    """Workspace page with block-based content storage.

    Supports hierarchical nesting (parent/child pages), templates,
    and JSON-based content for Notion-like block editing.
    """

    _name = "ipai.workspace.page"
    _description = "Workspace Page"
    _order = "sequence, id"
    _inherit = ["mail.thread"]

    workspace_id = fields.Many2one(
        "ipai.workspace",
        string="Workspace",
        required=True,
        ondelete="cascade",
        index=True,
    )
    title = fields.Char(
        string="Title",
        required=True,
        default="Untitled",
        tracking=True,
    )
    content_json = fields.Text(
        string="Content (JSON)",
        default="{}",
        help="Block-based content stored as JSON",
    )
    parent_id = fields.Many2one(
        "ipai.workspace.page",
        string="Parent Page",
        ondelete="set null",
        index=True,
        help="Parent page for nested hierarchy",
    )
    child_ids = fields.One2many(
        "ipai.workspace.page",
        "parent_id",
        string="Sub-Pages",
    )
    icon = fields.Char(
        string="Icon",
        help="Emoji or icon name for the page",
    )
    cover_image_url = fields.Char(
        string="Cover Image URL",
        help="URL of the page cover image",
    )
    is_template = fields.Boolean(
        string="Is Template",
        default=False,
        help="Mark this page as a reusable template",
    )
    created_by = fields.Many2one(
        "res.users",
        string="Created By",
        default=lambda self: self.env.user,
        readonly=True,
        index=True,
    )
    last_modified_by = fields.Many2one(
        "res.users",
        string="Last Modified By",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )

    _sql_constraints = [
        (
            "parent_not_self",
            "CHECK(id != parent_id)",
            "A page cannot be its own parent.",
        ),
    ]

    def write(self, vals):
        """Track the last user who modified the page."""
        if "last_modified_by" not in vals:
            vals["last_modified_by"] = self.env.user.id
        return super().write(vals)
