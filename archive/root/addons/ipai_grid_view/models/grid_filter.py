# -*- coding: utf-8 -*-
"""
Grid Filter Configuration Model

Manages saved filters and filter presets for grid views including:
- Filter conditions and operators
- Saved filter configurations
- User-specific and global filters
"""

import json
import logging

from odoo.exceptions import ValidationError

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class IpaiGridFilter(models.Model):
    """
    Saved filter configuration for grid views.

    Stores filter presets that users can apply to grid views
    for quick data filtering.
    """

    _name = "ipai.grid.filter"
    _description = "Grid View Filter"
    _order = "is_default desc, sequence, name"

    # Basic fields
    name = fields.Char(
        string="Filter Name", required=True, help="Display name for this filter"
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    # Parent reference
    grid_view_id = fields.Many2one(
        "ipai.grid.view", string="Grid View", ondelete="cascade"
    )

    # Filter scope
    is_default = fields.Boolean(
        string="Default Filter",
        default=False,
        help="Apply this filter by default when opening the view",
    )
    is_global = fields.Boolean(
        string="Global Filter",
        default=True,
        help="Available to all users (otherwise user-specific)",
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        default=lambda self: self.env.user,
        help="Owner of user-specific filters",
    )

    # Filter definition
    domain = fields.Char(
        string="Domain", default="[]", help="Odoo domain expression for this filter"
    )
    filter_json = fields.Text(
        string="Filter Definition (JSON)",
        default="[]",
        help="Filter conditions as JSON array",
    )

    # Visual properties
    color = fields.Selection(
        [
            ("gray", "Gray"),
            ("blue", "Blue"),
            ("green", "Green"),
            ("yellow", "Yellow"),
            ("orange", "Orange"),
            ("red", "Red"),
            ("purple", "Purple"),
        ],
        default="gray",
    )
    icon = fields.Char(help="Font Awesome icon class")

    # Computed fields
    condition_count = fields.Integer(
        compute="_compute_condition_count", string="Conditions"
    )

    @api.depends("filter_json")
    def _compute_condition_count(self):
        for record in self:
            try:
                conditions = json.loads(record.filter_json or "[]")
                record.condition_count = len(conditions)
            except json.JSONDecodeError:
                record.condition_count = 0

    def get_filter_conditions(self):
        """Parse and return filter conditions."""
        self.ensure_one()
        try:
            return json.loads(self.filter_json or "[]")
        except json.JSONDecodeError:
            _logger.warning("Invalid JSON in filter_json for filter %s", self.id)
            return []

    def set_filter_conditions(self, conditions):
        """Set filter conditions from a list."""
        self.ensure_one()
        self.filter_json = json.dumps(conditions, indent=2)

    def get_domain(self):
        """
        Convert filter conditions to Odoo domain.

        Returns:
            list: Odoo domain expression
        """
        self.ensure_one()
        try:
            stored_domain = eval(self.domain or "[]")
            if stored_domain:
                return stored_domain
        except Exception:
            pass

        # Build domain from filter conditions
        conditions = self.get_filter_conditions()
        domain = []

        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator", "=")
            value = condition.get("value")

            if field and value is not None:
                domain.append((field, operator, value))

        return domain

    @api.model
    def get_filters_for_view(self, grid_view_id, user_id=None):
        """
        Get all applicable filters for a grid view.

        Args:
            grid_view_id: ID of the grid view
            user_id: Optional user ID for user-specific filters

        Returns:
            recordset: Applicable filters
        """
        if user_id is None:
            user_id = self.env.uid

        domain = [
            ("grid_view_id", "=", grid_view_id),
            "|",
            ("is_global", "=", True),
            ("user_id", "=", user_id),
        ]

        return self.search(domain)

    def action_set_as_default(self):
        """Set this filter as the default for its view."""
        self.ensure_one()
        # Clear other defaults
        self.search(
            [
                ("grid_view_id", "=", self.grid_view_id.id),
                ("is_default", "=", True),
                ("id", "!=", self.id),
            ]
        ).write({"is_default": False})
        self.is_default = True

    def action_clear_default(self):
        """Clear the default flag from this filter."""
        self.ensure_one()
        self.is_default = False


class IpaiGridFilterCondition(models.TransientModel):
    """
    Individual filter condition (transient model for wizards).

    Used in filter configuration dialogs.
    """

    _name = "ipai.grid.filter.condition"
    _description = "Grid Filter Condition"

    filter_id = fields.Many2one("ipai.grid.filter", string="Filter")

    field_name = fields.Char(string="Field", required=True)
    field_label = fields.Char(string="Field Label")
    field_type = fields.Selection(
        [
            ("char", "Text"),
            ("text", "Long Text"),
            ("integer", "Integer"),
            ("float", "Decimal"),
            ("boolean", "Boolean"),
            ("date", "Date"),
            ("datetime", "Date & Time"),
            ("selection", "Selection"),
            ("many2one", "Many2One"),
        ],
        default="char",
    )

    operator = fields.Selection(
        [
            ("=", "equals"),
            ("!=", "not equals"),
            ("like", "contains"),
            ("ilike", "contains (case insensitive)"),
            ("not like", "does not contain"),
            (">", "greater than"),
            (">=", "greater or equal"),
            ("<", "less than"),
            ("<=", "less or equal"),
            ("in", "in list"),
            ("not in", "not in list"),
            ("=?", "is set"),
            ("child_of", "child of"),
            ("parent_of", "parent of"),
        ],
        default="=",
        required=True,
    )

    # Value fields (for different types)
    value_char = fields.Char(string="Text Value")
    value_integer = fields.Integer(string="Integer Value")
    value_float = fields.Float(string="Decimal Value")
    value_boolean = fields.Boolean(string="Boolean Value")
    value_date = fields.Date(string="Date Value")
    value_datetime = fields.Datetime(string="DateTime Value")
    value_selection = fields.Char(string="Selection Value")
    value_many2one = fields.Integer(string="Record ID")

    def get_condition_dict(self):
        """Get condition as dictionary."""
        self.ensure_one()

        # Determine value based on field type
        value = None
        if self.field_type == "char":
            value = self.value_char
        elif self.field_type == "integer":
            value = self.value_integer
        elif self.field_type == "float":
            value = self.value_float
        elif self.field_type == "boolean":
            value = self.value_boolean
        elif self.field_type == "date":
            value = str(self.value_date) if self.value_date else None
        elif self.field_type == "datetime":
            value = str(self.value_datetime) if self.value_datetime else None
        elif self.field_type == "selection":
            value = self.value_selection
        elif self.field_type == "many2one":
            value = self.value_many2one

        return {
            "field": self.field_name,
            "label": self.field_label or self.field_name,
            "operator": self.operator,
            "value": value,
            "type": self.field_type,
        }
