# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models


class IpaiWorkosRow(models.Model):
    """Row - Data record in a database."""

    _name = "ipai.workos.row"
    _description = "Work OS Database Row"
    _order = "sequence, id"

    name = fields.Char(
        string="Title",
        compute="_compute_name",
        store=True,
    )
    database_id = fields.Many2one(
        "ipai.workos.database",
        string="Database",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)

    # Cell values stored as JSON
    values_json = fields.Text(
        string="Values (JSON)",
        default="{}",
        help="Property values stored as JSON: {property_id: value}",
    )

    # Archived state
    active = fields.Boolean(default=True)

    @api.depends("values_json", "database_id.property_ids")
    def _compute_name(self):
        for record in self:
            title_prop = record.database_id.property_ids.filtered(lambda p: p.is_title)
            if title_prop:
                values = record.get_values()
                record.name = values.get(str(title_prop[0].id), "Untitled")
            else:
                record.name = f"Row {record.id}"

    def get_values(self):
        """Get parsed values dictionary."""
        try:
            return json.loads(self.values_json or "{}")
        except json.JSONDecodeError:
            return {}

    def set_values(self, values):
        """Set values dictionary."""
        self.values_json = json.dumps(values)

    def get_value(self, property_id):
        """Get value for a specific property."""
        values = self.get_values()
        return values.get(str(property_id))

    def set_value(self, property_id, value):
        """Set value for a specific property."""
        values = self.get_values()
        values[str(property_id)] = value
        self.set_values(values)

    def get_display_value(self, property_id):
        """Get formatted display value for a property."""
        prop = self.env["ipai.workos.property"].browse(property_id)
        value = self.get_value(property_id)

        if value is None:
            return ""

        if prop.property_type == "checkbox":
            return "Yes" if value else "No"
        elif prop.property_type == "person":
            user = self.env["res.users"].browse(value)
            return user.name if user else ""
        elif prop.property_type == "select":
            options = prop.get_options()
            opt = next((o for o in options if o.get("id") == value), None)
            return opt.get("label", "") if opt else ""
        elif prop.property_type == "multi_select":
            options = prop.get_options()
            labels = []
            for v in (value or []):
                opt = next((o for o in options if o.get("id") == v), None)
                if opt:
                    labels.append(opt.get("label", ""))
            return ", ".join(labels)
        elif prop.property_type == "relation":
            related = self.env["ipai.workos.row"].browse(value or [])
            return ", ".join(related.mapped("name"))

        return str(value)
