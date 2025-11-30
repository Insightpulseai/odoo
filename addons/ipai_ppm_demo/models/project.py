# ipai_ppm_demo/models/project.py
from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    ppm_strategy_category = fields.Char(string="Strategy Category")
    ppm_total_budget = fields.Monetary(
        string="Total Budget",
        currency_field="company_currency_id",
    )
    ppm_total_spend = fields.Monetary(
        string="Total Spend",
        currency_field="company_currency_id",
    )
    ppm_health_status = fields.Selection(
        [
            ("on_track", "On Track"),
            ("at_risk", "At Risk"),
            ("off_track", "Off Track"),
        ],
        string="Health Status",
        default="on_track",
    )
    ppm_roi_percentage = fields.Float(string="ROI %")

    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        readonly=True,
    )
