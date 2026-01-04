# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PpmKpiSnapshot(models.Model):
    """Time-series KPI measurements from various sources."""

    _name = "ppm.kpi.snapshot"
    _description = "PPM KPI Snapshot"
    _order = "as_of desc, kpi_key"

    name = fields.Char(
        compute="_compute_name",
        store=True,
    )

    # Scope (polymorphic reference)
    scope = fields.Selection(
        [
            ("portfolio", "Portfolio"),
            ("program", "Program"),
            ("project", "Project"),
            ("company", "Company-wide"),
        ],
        string="Scope",
        required=True,
        default="project",
    )
    portfolio_id = fields.Many2one(
        "ppm.portfolio",
        string="Portfolio",
        index=True,
    )
    program_id = fields.Many2one(
        "ppm.program",
        string="Program",
        index=True,
    )
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        index=True,
    )

    # KPI definition
    kpi_key = fields.Char(
        string="KPI Key",
        required=True,
        index=True,
        help="Unique identifier for the KPI (e.g., 'schedule_variance', 'cost_performance_index')",
    )
    kpi_label = fields.Char(
        string="KPI Label",
        help="Human-readable name",
    )
    kpi_category = fields.Selection(
        [
            ("schedule", "Schedule"),
            ("cost", "Cost"),
            ("quality", "Quality"),
            ("scope", "Scope"),
            ("resource", "Resource"),
            ("risk", "Risk"),
            ("custom", "Custom"),
        ],
        string="Category",
        default="custom",
    )

    # Value
    value = fields.Float(
        string="Value",
        required=True,
    )
    value_text = fields.Char(
        string="Value (Text)",
        help="For non-numeric KPIs",
    )
    unit = fields.Char(
        string="Unit",
        help="e.g., %, days, currency",
    )

    # Thresholds
    target_value = fields.Float(string="Target")
    threshold_green = fields.Float(string="Green Threshold")
    threshold_yellow = fields.Float(string="Yellow Threshold")

    # Status
    status = fields.Selection(
        [
            ("green", "On Track"),
            ("yellow", "At Risk"),
            ("red", "Critical"),
            ("grey", "No Target"),
        ],
        string="Status",
        compute="_compute_status",
        store=True,
    )

    # Timestamp
    as_of = fields.Datetime(
        string="As Of",
        required=True,
        default=fields.Datetime.now,
        index=True,
    )

    # Source tracking
    source = fields.Selection(
        [
            ("odoo", "Odoo"),
            ("superset", "Superset"),
            ("supabase", "Supabase"),
            ("manual", "Manual"),
            ("api", "External API"),
        ],
        string="Source",
        default="odoo",
    )
    source_ref = fields.Char(
        string="Source Reference",
        help="External ID or query reference",
    )

    @api.depends("kpi_key", "as_of", "scope")
    def _compute_name(self):
        for rec in self:
            scope_name = ""
            if rec.scope == "portfolio" and rec.portfolio_id:
                scope_name = rec.portfolio_id.name
            elif rec.scope == "program" and rec.program_id:
                scope_name = rec.program_id.name
            elif rec.scope == "project" and rec.project_id:
                scope_name = rec.project_id.name
            else:
                scope_name = rec.scope

            rec.name = f"{rec.kpi_key} - {scope_name} - {rec.as_of.date() if rec.as_of else 'N/A'}"

    @api.depends("value", "target_value", "threshold_green", "threshold_yellow")
    def _compute_status(self):
        for rec in self:
            if not rec.target_value and not rec.threshold_green:
                rec.status = "grey"
                continue

            # Higher is better logic (can be inverted per KPI)
            if rec.threshold_green and rec.value >= rec.threshold_green:
                rec.status = "green"
            elif rec.threshold_yellow and rec.value >= rec.threshold_yellow:
                rec.status = "yellow"
            elif rec.threshold_green or rec.threshold_yellow:
                rec.status = "red"
            else:
                rec.status = "grey"

    @api.model
    def create_snapshot(self, scope, scope_id, kpi_key, value, **kwargs):
        """Helper to create a snapshot programmatically."""
        vals = {
            "scope": scope,
            "kpi_key": kpi_key,
            "value": value,
            "as_of": kwargs.get("as_of", fields.Datetime.now()),
            "source": kwargs.get("source", "odoo"),
            "kpi_label": kwargs.get("kpi_label"),
            "unit": kwargs.get("unit"),
            "target_value": kwargs.get("target_value"),
            "threshold_green": kwargs.get("threshold_green"),
            "threshold_yellow": kwargs.get("threshold_yellow"),
        }

        if scope == "portfolio":
            vals["portfolio_id"] = scope_id
        elif scope == "program":
            vals["program_id"] = scope_id
        elif scope == "project":
            vals["project_id"] = scope_id

        return self.create(vals)
