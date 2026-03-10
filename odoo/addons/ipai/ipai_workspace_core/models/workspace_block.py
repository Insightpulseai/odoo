# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class WorkspaceBlock(models.Model):
    _name = "workspace.block"
    _description = "Workspace Content Block"
    _order = "sequence, id"

    page_id = fields.Many2one(
        "workspace.page",
        string="Page",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)
    block_type = fields.Selection(
        [
            ("text", "Text"),
            ("heading", "Heading"),
            ("code", "Code"),
            ("list", "List"),
            ("embed_view", "Embedded View"),
            ("saved_query", "Saved Query"),
            ("evidence_ref", "Evidence Reference"),
        ],
        string="Block Type",
        required=True,
        default="text",
    )
    content = fields.Html(string="Content", sanitize_style=True)
    # For embed_view type
    res_model = fields.Char(string="Model Name")
    view_type = fields.Selection(
        [
            ("list", "List"),
            ("form", "Form"),
            ("kanban", "Kanban"),
            ("pivot", "Pivot"),
            ("graph", "Graph"),
        ],
        string="View Type",
    )
    domain = fields.Char(string="Domain Filter")
    # For saved_query type
    saved_query_id = fields.Many2one(
        "workspace.saved.query",
        string="Saved Query",
    )
    # For evidence_ref type
    evidence_pack_id = fields.Many2one(
        "workspace.evidence.pack",
        string="Evidence Pack",
    )
