# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models


PROPERTY_TYPES = [
    ("text", "Text"),
    ("number", "Number"),
    ("select", "Select"),
    ("multi_select", "Multi-select"),
    ("date", "Date"),
    ("checkbox", "Checkbox"),
    ("person", "Person"),
    ("url", "URL"),
    ("email", "Email"),
    ("phone", "Phone"),
    ("relation", "Relation"),
]


class IpaiWorkosProperty(models.Model):
    """Property - Column definition for a database."""

    _name = "ipai.workos.property"
    _description = "Work OS Database Property"
    _order = "sequence, id"

    name = fields.Char(string="Name", required=True)
    database_id = fields.Many2one(
        "ipai.workos.database",
        string="Database",
        required=True,
        ondelete="cascade",
    )
    property_type = fields.Selection(
        PROPERTY_TYPES,
        string="Type",
        required=True,
        default="text",
    )
    sequence = fields.Integer(string="Sequence", default=10)
    is_title = fields.Boolean(
        string="Is Title",
        default=False,
        help="Title property is shown as the row name",
    )

    # Select/Multi-select options
    options_json = fields.Text(
        string="Options (JSON)",
        default="[]",
        help="Options for select/multi-select properties",
    )

    # Relation configuration
    related_database_id = fields.Many2one(
        "ipai.workos.database",
        string="Related Database",
        ondelete="set null",
    )

    # Display configuration
    width = fields.Integer(string="Column Width", default=200)
    is_visible = fields.Boolean(string="Visible", default=True)

    def get_options(self):
        """Get parsed options for select properties."""
        try:
            return json.loads(self.options_json or "[]")
        except json.JSONDecodeError:
            return []

    def set_options(self, options):
        """Set options for select properties."""
        self.options_json = json.dumps(options)

    def add_option(self, label, color=None):
        """Add an option to select property."""
        options = self.get_options()
        new_option = {"id": len(options) + 1, "label": label}
        if color:
            new_option["color"] = color
        options.append(new_option)
        self.set_options(options)
        return new_option
