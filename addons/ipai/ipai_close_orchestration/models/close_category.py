# -*- coding: utf-8 -*-
"""
Close Task Category

Organizational groupings for close tasks (maps from A1 Workstreams).
"""
from odoo import api, fields, models


class CloseTaskCategory(models.Model):
    """
    Category for grouping close tasks.

    Bridged from A1 Workstreams.
    """

    _name = "close.task.category"
    _description = "Close Task Category"
    _order = "sequence, code"

    _sql_constraints = [
        ("code_uniq", "unique(code, company_id)", "Category code must be unique per company."),
    ]

    # Core fields
    code = fields.Char(
        string="Code",
        required=True,
        index=True,
        help="Unique identifier",
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)
    color = fields.Integer(string="Color")

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    # Bridge to A1
    a1_workstream_id = fields.Many2one(
        "a1.workstream",
        string="A1 Workstream",
        help="Source workstream from A1 Control Center",
    )

    # Templates
    template_ids = fields.One2many(
        "close.task.template",
        "category_id",
        string="Templates",
    )

    description = fields.Text(string="Description")
