# -*- coding: utf-8 -*-
import json
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class SemanticModel(models.Model):
    """Local cache of semantic models from Supabase catalog.

    Mirrors catalog.semantic_models for offline/fast access.
    """

    _name = "ipai.semantic.model"
    _description = "Semantic Model"
    _order = "name"
    _rec_name = "label"

    # Link to catalog asset
    asset_id = fields.Many2one(
        "ipai.catalog.asset",
        string="Catalog Asset",
        required=True,
        ondelete="cascade",
        index=True,
    )

    # Identity
    name = fields.Char(string="Name", required=True, index=True)
    label = fields.Char(string="Label")
    description = fields.Text(string="Description")

    # Source
    source_type = fields.Selection(
        selection=[
            ("table", "Table"),
            ("view", "View"),
            ("sql", "SQL Query"),
            ("ref", "Reference"),
        ],
        string="Source Type",
        default="table",
    )
    source_ref = fields.Char(string="Source Reference")
    primary_key = fields.Char(string="Primary Key", help="Comma-separated columns")

    # Time dimension
    time_dimension = fields.Char(string="Time Dimension")
    default_time_grain = fields.Selection(
        selection=[
            ("day", "Day"),
            ("week", "Week"),
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("year", "Year"),
            ("hour", "Hour"),
        ],
        string="Default Time Grain",
        default="day",
    )

    # Status
    status = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("deprecated", "Deprecated"),
            ("archived", "Archived"),
        ],
        string="Status",
        default="draft",
    )

    # Children
    dimension_ids = fields.One2many(
        "ipai.semantic.dimension",
        "model_id",
        string="Dimensions",
    )
    metric_ids = fields.One2many(
        "ipai.semantic.metric",
        "model_id",
        string="Metrics",
    )

    # Sync tracking
    supabase_id = fields.Char(string="Supabase ID", index=True)
    last_sync = fields.Datetime(string="Last Sync")

    _sql_constraints = [
        ("asset_name_unique", "unique(asset_id, name)", "Model name must be unique per asset."),
    ]

    def name_get(self):
        result = []
        for record in self:
            name = record.label or record.name
            if record.asset_id:
                name = f"{record.asset_id.title} / {name}"
            result.append((record.id, name))
        return result

    @api.model
    def get_model_schema(self, model_id):
        """Get full model schema with dimensions and metrics."""
        model = self.browse(model_id)
        if not model.exists():
            return {}

        return {
            "model": {
                "id": model.id,
                "name": model.name,
                "label": model.label,
                "description": model.description,
                "source_type": model.source_type,
                "source_ref": model.source_ref,
                "time_dimension": model.time_dimension,
                "default_time_grain": model.default_time_grain,
                "status": model.status,
            },
            "dimensions": [
                {
                    "name": d.name,
                    "label": d.label,
                    "description": d.description,
                    "expr": d.expr,
                    "data_type": d.data_type,
                    "is_time_dimension": d.is_time_dimension,
                }
                for d in model.dimension_ids
                if not d.is_hidden
            ],
            "metrics": [
                {
                    "name": m.name,
                    "label": m.label,
                    "description": m.description,
                    "metric_type": m.metric_type,
                    "aggregation": m.aggregation,
                    "expr": m.expr,
                    "formula": m.formula,
                    "format_string": m.format_string,
                    "unit": m.unit,
                }
                for m in model.metric_ids
                if not m.is_hidden
            ],
        }


class SemanticDimension(models.Model):
    """Semantic dimension definition."""

    _name = "ipai.semantic.dimension"
    _description = "Semantic Dimension"
    _order = "is_time_dimension desc, name"

    model_id = fields.Many2one(
        "ipai.semantic.model",
        string="Semantic Model",
        required=True,
        ondelete="cascade",
        index=True,
    )

    # Identity
    name = fields.Char(string="Name", required=True)
    label = fields.Char(string="Label")
    description = fields.Text(string="Description")

    # Definition
    expr = fields.Char(string="Expression", required=True)
    data_type = fields.Selection(
        selection=[
            ("string", "String"),
            ("number", "Number"),
            ("date", "Date"),
            ("datetime", "Datetime"),
            ("boolean", "Boolean"),
        ],
        string="Data Type",
        default="string",
    )

    # Time dimension
    is_time_dimension = fields.Boolean(string="Is Time Dimension", default=False)
    time_grain = fields.Selection(
        selection=[
            ("day", "Day"),
            ("week", "Week"),
            ("month", "Month"),
            ("quarter", "Quarter"),
            ("year", "Year"),
            ("hour", "Hour"),
        ],
        string="Time Grain",
    )

    # Hierarchy
    hierarchy_level = fields.Integer(string="Hierarchy Level")
    parent_dimension_id = fields.Many2one(
        "ipai.semantic.dimension",
        string="Parent Dimension",
    )

    # Display
    tags = fields.Char(string="Tags")
    is_hidden = fields.Boolean(string="Hidden", default=False)

    _sql_constraints = [
        ("model_name_unique", "unique(model_id, name)", "Dimension name must be unique per model."),
    ]


class SemanticMetric(models.Model):
    """Semantic metric definition."""

    _name = "ipai.semantic.metric"
    _description = "Semantic Metric"
    _order = "name"

    model_id = fields.Many2one(
        "ipai.semantic.model",
        string="Semantic Model",
        required=True,
        ondelete="cascade",
        index=True,
    )

    # Identity
    name = fields.Char(string="Name", required=True)
    label = fields.Char(string="Label")
    description = fields.Text(string="Description")

    # Definition
    metric_type = fields.Selection(
        selection=[
            ("simple", "Simple"),
            ("derived", "Derived"),
            ("cumulative", "Cumulative"),
            ("ratio", "Ratio"),
            ("conversion", "Conversion"),
        ],
        string="Metric Type",
        default="simple",
    )
    aggregation = fields.Selection(
        selection=[
            ("sum", "Sum"),
            ("count", "Count"),
            ("count_distinct", "Count Distinct"),
            ("avg", "Average"),
            ("min", "Min"),
            ("max", "Max"),
            ("median", "Median"),
        ],
        string="Aggregation",
    )
    expr = fields.Char(string="Expression", required=True)

    # For derived metrics
    depends_on = fields.Char(string="Depends On", help="Comma-separated metric names")
    formula = fields.Text(string="Formula")

    # Formatting
    format_string = fields.Char(string="Format String")
    unit = fields.Char(string="Unit")

    # Display
    tags = fields.Char(string="Tags")
    is_hidden = fields.Boolean(string="Hidden", default=False)

    _sql_constraints = [
        ("model_name_unique", "unique(model_id, name)", "Metric name must be unique per model."),
    ]
