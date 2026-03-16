# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiWorkosDatabase(models.Model):
    """Database - Notion-style database (table) container."""

    _name = "ipai.workos.database"
    _description = "Work OS Database"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Name", required=True, tracking=True)
    description = fields.Text(string="Description")
    icon = fields.Char(string="Icon", default="table")

    # Location
    space_id = fields.Many2one(
        "ipai.workos.space",
        string="Space",
        ondelete="cascade",
    )
    page_id = fields.Many2one(
        "ipai.workos.page",
        string="Inline Page",
        ondelete="cascade",
        help="If set, database is inline within this page",
    )

    # Schema
    property_ids = fields.One2many(
        "ipai.workos.property",
        "database_id",
        string="Properties",
    )

    # Data
    row_ids = fields.One2many(
        "ipai.workos.row",
        "database_id",
        string="Rows",
    )
    row_count = fields.Integer(
        string="Rows",
        compute="_compute_row_count",
    )

    # Status
    active = fields.Boolean(default=True)

    @api.depends("row_ids")
    def _compute_row_count(self):
        for record in self:
            record.row_count = len(record.row_ids)

    def action_view_rows(self):
        """Open rows in this database."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Rows in {self.name}",
            "res_model": "ipai.workos.row",
            "view_mode": "tree,form",
            "domain": [("database_id", "=", self.id)],
            "context": {"default_database_id": self.id},
        }
