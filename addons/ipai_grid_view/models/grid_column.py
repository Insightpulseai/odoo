# -*- coding: utf-8 -*-
"""
Grid Column Configuration Model

Defines individual column settings for grid views including:
- Field binding
- Display properties (width, alignment, format)
- Sort and filter capabilities
- Custom rendering options
"""

from odoo import api, fields, models, _


class IpaiGridColumn(models.Model):
    """
    Column definition for grid views.

    Each column maps to a model field and defines how it should
    be displayed in the grid, including width, alignment, format,
    and interactive behaviors.
    """
    _name = "ipai.grid.column"
    _description = "Grid Column Configuration"
    _order = "sequence, id"

    # Parent reference
    grid_view_id = fields.Many2one(
        "ipai.grid.view",
        string="Grid View",
        required=True,
        ondelete="cascade"
    )

    # Field binding
    field_name = fields.Char(
        string="Field Name",
        required=True,
        help="Technical name of the model field"
    )
    label = fields.Char(
        string="Column Header",
        help="Display label for the column header"
    )
    field_type = fields.Selection([
        ("char", "Text"),
        ("text", "Long Text"),
        ("integer", "Integer"),
        ("float", "Decimal"),
        ("monetary", "Monetary"),
        ("boolean", "Boolean"),
        ("date", "Date"),
        ("datetime", "Date & Time"),
        ("selection", "Selection"),
        ("many2one", "Many2One"),
        ("many2many", "Many2Many"),
        ("one2many", "One2Many"),
        ("binary", "Binary"),
        ("html", "HTML"),
    ], string="Field Type")

    # Display properties
    sequence = fields.Integer(default=10)
    visible = fields.Boolean(default=True)
    width = fields.Integer(
        default=150,
        help="Column width in pixels"
    )
    min_width = fields.Integer(
        default=80,
        help="Minimum column width in pixels"
    )
    max_width = fields.Integer(
        default=500,
        help="Maximum column width in pixels"
    )
    alignment = fields.Selection([
        ("left", "Left"),
        ("center", "Center"),
        ("right", "Right"),
    ], default="left")

    # Formatting
    format_string = fields.Char(
        help="Python format string for displaying values"
    )
    date_format = fields.Char(
        default="%Y-%m-%d",
        help="Date format string"
    )
    decimal_places = fields.Integer(
        default=2,
        help="Number of decimal places for numeric fields"
    )
    currency_field = fields.Char(
        help="Field name containing currency for monetary columns"
    )

    # Interactivity
    sortable = fields.Boolean(
        default=True,
        help="Allow sorting by this column"
    )
    filterable = fields.Boolean(
        default=True,
        help="Allow filtering by this column"
    )
    searchable = fields.Boolean(
        default=True,
        help="Include in quick search"
    )
    resizable = fields.Boolean(
        default=True,
        help="Allow resizing this column"
    )
    editable = fields.Boolean(
        default=False,
        help="Allow inline editing"
    )
    clickable = fields.Boolean(
        default=True,
        help="Make cell content clickable (opens record)"
    )

    # Column type/widget
    column_type = fields.Selection([
        ("standard", "Standard"),
        ("checkbox", "Checkbox"),
        ("avatar", "Avatar"),
        ("badge", "Badge/Tag"),
        ("progress", "Progress Bar"),
        ("button", "Action Button"),
        ("link", "Link"),
        ("activity", "Activity"),
        ("menu", "Action Menu"),
    ], default="standard")

    # Widget-specific settings (stored as JSON)
    widget_options = fields.Text(
        default="{}",
        help="Widget-specific configuration as JSON"
    )

    # Styling
    css_class = fields.Char(
        help="Additional CSS classes for the column"
    )
    header_css_class = fields.Char(
        help="CSS classes for the column header"
    )
    cell_css_class = fields.Char(
        help="CSS classes for cells in this column"
    )

    # Special columns
    is_primary = fields.Boolean(
        default=False,
        help="Primary display column (usually the name field)"
    )
    is_avatar_column = fields.Boolean(
        default=False,
        help="Column displays user/record avatar"
    )
    is_selection_column = fields.Boolean(
        default=False,
        help="This is the row selection checkbox column"
    )
    is_action_column = fields.Boolean(
        default=False,
        help="This column contains row action buttons"
    )

    # Computed display name
    display_name = fields.Char(compute="_compute_display_name", store=True)

    @api.depends("field_name", "label")
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.label or record.field_name or _("Unnamed Column")

    def get_column_definition(self):
        """
        Get column definition as dictionary for JavaScript.

        Returns:
            dict: Column configuration for frontend
        """
        self.ensure_one()
        return {
            "id": self.id,
            "field": self.field_name,
            "label": self.label or self.field_name,
            "type": self.field_type,
            "width": self.width,
            "minWidth": self.min_width,
            "maxWidth": self.max_width,
            "alignment": self.alignment,
            "sortable": self.sortable,
            "filterable": self.filterable,
            "searchable": self.searchable,
            "resizable": self.resizable,
            "editable": self.editable,
            "clickable": self.clickable,
            "visible": self.visible,
            "columnType": self.column_type,
            "cssClass": self.css_class or "",
            "isPrimary": self.is_primary,
            "isAvatar": self.is_avatar_column,
            "isSelection": self.is_selection_column,
            "isAction": self.is_action_column,
        }

    @api.model
    def get_default_columns_for_model(self, model_name):
        """
        Generate default column configuration for a model.

        Args:
            model_name: The Odoo model name

        Returns:
            list: Default column definitions
        """
        Model = self.env[model_name]
        fields_info = Model.fields_get()

        columns = []
        sequence = 0

        # Add selection column first
        columns.append({
            "field_name": "_selection",
            "label": "",
            "column_type": "checkbox",
            "is_selection_column": True,
            "width": 40,
            "sortable": False,
            "filterable": False,
            "sequence": sequence,
        })
        sequence += 10

        # Priority fields to include
        priority_fields = ["name", "display_name", "email", "phone", "active"]

        for field_name in priority_fields:
            if field_name in fields_info:
                field = fields_info[field_name]
                columns.append({
                    "field_name": field_name,
                    "label": field.get("string", field_name),
                    "field_type": field.get("type"),
                    "is_primary": field_name == "name",
                    "sequence": sequence,
                })
                sequence += 10

        # Add other commonly useful fields
        for field_name, field in fields_info.items():
            if field_name in priority_fields or field_name.startswith("_"):
                continue
            if field.get("type") in ["char", "selection", "date", "datetime", "integer", "float"]:
                if len(columns) < 10:  # Limit default columns
                    columns.append({
                        "field_name": field_name,
                        "label": field.get("string", field_name),
                        "field_type": field.get("type"),
                        "sequence": sequence,
                    })
                    sequence += 10

        # Add action column last
        columns.append({
            "field_name": "_actions",
            "label": "",
            "column_type": "menu",
            "is_action_column": True,
            "width": 50,
            "sortable": False,
            "filterable": False,
            "sequence": 9999,
        })

        return columns
