# -*- coding: utf-8 -*-
from odoo import models, fields


class SrmKpiCategory(models.Model):
    """Supplier KPI category for scorecard evaluation."""

    _name = "srm.kpi.category"
    _description = "Supplier KPI Category"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    description = fields.Text()
    weight = fields.Float(
        string="Weight (%)",
        default=20.0,
        help="Percentage weight in overall supplier score",
    )
    active = fields.Boolean(default=True)

    # Evaluation method
    eval_method = fields.Selection(
        [
            ("manual", "Manual Rating"),
            ("computed", "Computed from Data"),
        ],
        default="manual",
        help="How this KPI is evaluated",
    )

    # Computed source (if applicable)
    compute_source = fields.Selection(
        [
            ("po_otd", "PO On-Time Delivery"),
            ("quality_issues", "Quality Issues"),
            ("price_variance", "Price Variance"),
            ("response_time", "Response Time"),
        ],
        string="Data Source",
        help="Automatic computation source if eval_method is 'computed'",
    )
