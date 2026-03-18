# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class WorkspaceEvidencePack(models.Model):
    _name = "workspace.evidence.pack"
    _description = "Audit Evidence Pack"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    name = fields.Char(
        string="Evidence Pack Name",
        required=True,
        tracking=True,
    )
    description = fields.Text(string="Description")
    date = fields.Date(
        string="Evidence Date",
        default=fields.Date.today,
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Attachments",
    )
    record_refs = fields.Text(
        string="Linked Records (JSON)",
        help="JSON array of {model, res_id, display_name}",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sealed", "Sealed"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
