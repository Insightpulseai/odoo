# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class WorkspacePage(models.Model):
    _name = "workspace.page"
    _description = "Workspace Page"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "write_date desc"

    name = fields.Char(string="Title", required=True, tracking=True)
    body = fields.Html(string="Content", sanitize_style=True)
    parent_id = fields.Many2one(
        "workspace.page",
        string="Parent Page",
        ondelete="set null",
        index=True,
    )
    child_ids = fields.One2many(
        "workspace.page",
        "parent_id",
        string="Sub-pages",
    )
    tag_ids = fields.Many2many("workspace.tag", string="Tags")
    block_ids = fields.One2many(
        "workspace.block",
        "page_id",
        string="Blocks",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
        index=True,
    )
    is_published = fields.Boolean(string="Published", default=False)
    color = fields.Integer(string="Color Index")
