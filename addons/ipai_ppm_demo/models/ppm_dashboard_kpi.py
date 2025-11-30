# ipai_ppm_demo/models/ppm_dashboard_kpi.py
from odoo import fields, models


class PpmDashboardKpi(models.Model):
    _name = "ppm.dashboard.kpi"
    _description = "PPM Dashboard KPI Snapshot"

    name = fields.Char(required=True)
    projects_ongoing = fields.Integer()
    total_cost = fields.Float()
    cost_variance = fields.Float()
    project_health_score = fields.Float()
    budget_health_score = fields.Float()


class PpmStrategySpend(models.Model):
    _name = "ppm.strategy.spend"
    _description = "PPM Spend by Strategy"

    name = fields.Char(required=True)
    strategy = fields.Char(required=True)
    spend = fields.Float()
