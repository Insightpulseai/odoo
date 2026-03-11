# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class WorkspaceSavedQuery(models.Model):
    _name = "workspace.saved.query"
    _description = "Saved RAG Query"
    _order = "write_date desc"

    name = fields.Char(string="Query Name", required=True)
    query_text = fields.Text(string="Query Text", required=True)
    corpus_id = fields.Char(string="Corpus ID")
    top_k = fields.Integer(string="Max Results", default=5)
    cached_results = fields.Text(string="Cached Results (JSON)")
    last_run = fields.Datetime(string="Last Run")
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
    )
    block_ids = fields.One2many(
        "workspace.block",
        "saved_query_id",
        string="Used In Blocks",
    )
