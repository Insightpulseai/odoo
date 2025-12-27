# -*- coding: utf-8 -*-
"""
Grid View Configuration Model

This model stores the configuration for grid/list views including:
- View type (list/kanban)
- Column visibility and order
- Sort configuration
- Filter presets
- Pagination settings
"""

import json
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class IpaiGridView(models.Model):
    """
    Main configuration model for grid/list views.

    Stores view settings, column configurations, and filter presets
    that persist across user sessions.
    """
    _name = "ipai.grid.view"
    _description = "Grid View Configuration"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    # Basic fields
    name = fields.Char(
        string="View Name",
        required=True,
        tracking=True,
        help="Display name for this grid view configuration"
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    # Model reference
    model_id = fields.Many2one(
        "ir.model",
        string="Target Model",
        required=True,
        ondelete="cascade",
        tracking=True,
        help="The Odoo model this grid view displays"
    )
    model_name = fields.Char(
        related="model_id.model",
        string="Model Name",
        store=True
    )

    # View type configuration
    view_type = fields.Selection([
        ("list", "List View"),
        ("kanban", "Kanban View"),
        ("table", "Table View"),
    ], default="list", required=True, tracking=True)

    # Column configuration
    column_ids = fields.One2many(
        "ipai.grid.column",
        "grid_view_id",
        string="Columns",
        help="Column definitions for this grid view"
    )
    visible_column_ids = fields.Many2many(
        "ipai.grid.column",
        "ipai_grid_view_visible_columns_rel",
        "grid_view_id",
        "column_id",
        string="Visible Columns"
    )

    # Filter configuration
    filter_ids = fields.One2many(
        "ipai.grid.filter",
        "grid_view_id",
        string="Saved Filters"
    )
    active_filter_id = fields.Many2one(
        "ipai.grid.filter",
        string="Active Filter"
    )

    # JSON configuration storage
    config_json = fields.Text(
        string="Configuration (JSON)",
        default="{}",
        help="Additional view configuration stored as JSON"
    )
    sort_json = fields.Text(
        string="Sort Configuration (JSON)",
        default="[]",
        help="Column sort order as JSON array"
    )

    # Pagination settings
    page_size = fields.Integer(
        default=10,
        help="Number of records per page"
    )
    page_size_options = fields.Char(
        default="10,25,50,100",
        help="Comma-separated list of page size options"
    )

    # Display settings
    show_row_numbers = fields.Boolean(default=False)
    show_checkboxes = fields.Boolean(default=True)
    enable_row_selection = fields.Boolean(default=True)
    enable_column_resize = fields.Boolean(default=True)
    enable_column_reorder = fields.Boolean(default=True)
    enable_quick_search = fields.Boolean(default=True)
    enable_export = fields.Boolean(default=True)

    # Computed fields
    column_count = fields.Integer(
        compute="_compute_column_count",
        string="Number of Columns"
    )

    @api.depends("column_ids")
    def _compute_column_count(self):
        for record in self:
            record.column_count = len(record.column_ids)

    def get_config(self):
        """Parse and return the JSON configuration."""
        self.ensure_one()
        try:
            return json.loads(self.config_json or "{}")
        except json.JSONDecodeError:
            _logger.warning("Invalid JSON in config_json for grid view %s", self.id)
            return {}

    def set_config(self, config_dict):
        """Set the JSON configuration from a dictionary."""
        self.ensure_one()
        self.config_json = json.dumps(config_dict, indent=2)

    def get_sort_config(self):
        """Parse and return the sort configuration."""
        self.ensure_one()
        try:
            return json.loads(self.sort_json or "[]")
        except json.JSONDecodeError:
            _logger.warning("Invalid JSON in sort_json for grid view %s", self.id)
            return []

    def set_sort_config(self, sort_list):
        """Set the sort configuration from a list."""
        self.ensure_one()
        self.sort_json = json.dumps(sort_list)

    @api.model
    def get_grid_data(self, model_name, domain=None, offset=0, limit=None, order=None):
        """
        Fetch grid data for a given model.

        Args:
            model_name: The Odoo model name (e.g., 'res.partner')
            domain: Search domain for filtering
            offset: Pagination offset
            limit: Number of records to return
            order: Sort order string

        Returns:
            dict: Contains 'records', 'total', and 'columns'
        """
        if domain is None:
            domain = []
        if limit is None:
            limit = 10

        Model = self.env[model_name]

        # Get total count
        total = Model.search_count(domain)

        # Fetch records
        records = Model.search_read(
            domain,
            offset=offset,
            limit=limit,
            order=order
        )

        # Get model fields for column definitions
        model_fields = Model.fields_get()

        return {
            "records": records,
            "total": total,
            "offset": offset,
            "limit": limit,
            "fields": model_fields,
        }

    @api.model
    def get_available_fields(self, model_name):
        """
        Get all available fields for a model that can be displayed in grid.

        Args:
            model_name: The Odoo model name

        Returns:
            list: Field definitions suitable for column configuration
        """
        Model = self.env[model_name]
        fields_info = Model.fields_get()

        available_fields = []
        for field_name, field_data in fields_info.items():
            # Skip internal/technical fields
            if field_name.startswith("_") or field_data.get("store") is False:
                continue

            available_fields.append({
                "name": field_name,
                "string": field_data.get("string", field_name),
                "type": field_data.get("type"),
                "sortable": field_data.get("sortable", True),
                "searchable": field_data.get("searchable", True),
                "relation": field_data.get("relation"),
            })

        return sorted(available_fields, key=lambda x: x.get("string", ""))

    @api.model
    def apply_bulk_action(self, model_name, record_ids, action, params=None):
        """
        Apply a bulk action to selected records.

        Args:
            model_name: The Odoo model name
            record_ids: List of record IDs to act on
            action: Action name ('delete', 'archive', 'unarchive', 'custom')
            params: Additional parameters for the action

        Returns:
            dict: Result of the action
        """
        if params is None:
            params = {}

        Model = self.env[model_name]
        records = Model.browse(record_ids)

        if action == "delete":
            records.unlink()
            return {"success": True, "message": _("Records deleted successfully")}
        elif action == "archive":
            records.write({"active": False})
            return {"success": True, "message": _("Records archived successfully")}
        elif action == "unarchive":
            records.write({"active": True})
            return {"success": True, "message": _("Records unarchived successfully")}
        else:
            raise ValidationError(_("Unknown bulk action: %s") % action)

    def action_switch_to_kanban(self):
        """Switch this view to kanban mode."""
        self.ensure_one()
        self.view_type = "kanban"

    def action_switch_to_list(self):
        """Switch this view to list mode."""
        self.ensure_one()
        self.view_type = "list"

    def action_reset_columns(self):
        """Reset column configuration to defaults."""
        self.ensure_one()
        if self.model_id:
            self.column_ids.unlink()
            available_fields = self.get_available_fields(self.model_name)
            for idx, field_info in enumerate(available_fields[:10]):
                self.env["ipai.grid.column"].create({
                    "grid_view_id": self.id,
                    "field_name": field_info["name"],
                    "label": field_info["string"],
                    "field_type": field_info["type"],
                    "sequence": idx * 10,
                    "visible": True,
                })
