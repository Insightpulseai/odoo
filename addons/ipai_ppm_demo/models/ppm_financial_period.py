# ipai_ppm_demo/models/ppm_financial_period.py
from odoo import fields, models


class PpmFinancialPeriod(models.Model):
    _name = "ppm.financial.period"
    _description = "PPM Financial Period Data"

    name = fields.Char(required=True)
    period_code = fields.Char(required=True)
    cost_type = fields.Selection(
        [("capex", "Capex"), ("opex", "Opex")],
        required=True,
    )
    planned_value = fields.Float()
    actual_cost = fields.Float()
    earned_value = fields.Float()
    scenario = fields.Char(default="actuals")
