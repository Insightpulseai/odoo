# -*- coding: utf-8 -*-
import json

from odoo import api, fields, models


class IpaiWorkosView(models.Model):
    """View - Saved view configuration for a database."""

    _name = "ipai.workos.view"
    _description = "Work OS Database View"
    _order = "sequence, name"

    name = fields.Char(string="View Name", required=True)
    database_id = fields.Many2one(
        "ipai.workos.database",
        string="Database",
        required=True,
        ondelete="cascade",
        index=True,
    )
    view_type = fields.Selection(
        [
            ("table", "Table"),
            ("kanban", "Kanban"),
            ("calendar", "Calendar"),
            ("gallery", "Gallery"),
            ("list", "List"),
        ],
        string="View Type",
        required=True,
        default="table",
    )
    sequence = fields.Integer(string="Sequence", default=10)
    is_default = fields.Boolean(string="Default View", default=False)

    # Sharing
    is_shared = fields.Boolean(string="Shared", default=True)
    user_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
    )

    # Configuration (stored as JSON)
    config_json = fields.Text(
        string="Configuration (JSON)",
        default="{}",
    )

    # Specific view settings
    group_by_property_id = fields.Many2one(
        "ipai.workos.property",
        string="Group By",
        help="Property to group by (for Kanban)",
    )
    date_property_id = fields.Many2one(
        "ipai.workos.property",
        string="Date Property",
        help="Property to use as date (for Calendar)",
    )

    # Filter/sort
    filter_json = fields.Text(
        string="Filters (JSON)",
        default="[]",
    )
    sort_json = fields.Text(
        string="Sorts (JSON)",
        default="[]",
    )

    # Visible properties
    visible_property_ids = fields.Many2many(
        "ipai.workos.property",
        string="Visible Properties",
    )

    def get_config(self):
        """Get parsed configuration."""
        try:
            return json.loads(self.config_json or "{}")
        except json.JSONDecodeError:
            return {}

    def set_config(self, config):
        """Set configuration."""
        self.config_json = json.dumps(config)

    def get_filters(self):
        """Get parsed filters."""
        try:
            return json.loads(self.filter_json or "[]")
        except json.JSONDecodeError:
            return []

    def get_sorts(self):
        """Get parsed sorts."""
        try:
            return json.loads(self.sort_json or "[]")
        except json.JSONDecodeError:
            return []

    def apply_to_rows(self, rows):
        """Apply filters and sorts to row recordset."""
        # This is a simplified implementation
        # In production, would build dynamic domain and order
        result = rows

        # Apply sorts
        sorts = self.get_sorts()
        if sorts:
            order_fields = []
            for sort in sorts:
                prop_id = sort.get("property_id")
                direction = "desc" if sort.get("descending") else "asc"
                # Note: actual implementation would need to sort by JSON values
                order_fields.append(f"sequence {direction}")
            if order_fields:
                result = result.sorted(key=lambda r: r.sequence)

        return result

    @api.model
    def get_views_for_database(self, database_id):
        """Get all views for a database (shared + user's private)."""
        return self.search(
            [
                ("database_id", "=", database_id),
                "|",
                ("is_shared", "=", True),
                ("user_id", "=", self.env.user.id),
            ]
        )
