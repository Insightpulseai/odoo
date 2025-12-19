# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PpmPortfolio(models.Model):
    """Strategic portfolio container for programs."""

    _name = "ppm.portfolio"
    _description = "PPM Portfolio"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    name = fields.Char(
        string="Portfolio Name",
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
        copy=False,
        help="Unique portfolio identifier (e.g., PF-FINANCE, PF-OPS)",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    owner_id = fields.Many2one(
        "res.users",
        string="Portfolio Owner",
        tracking=True,
    )
    sponsor_id = fields.Many2one(
        "res.users",
        string="Executive Sponsor",
    )

    objective = fields.Text(
        string="Strategic Objective",
        help="High-level goals and success criteria",
    )
    description = fields.Html(string="Description")

    # Programs in this portfolio
    program_ids = fields.One2many(
        "ppm.program",
        "portfolio_id",
        string="Programs",
    )
    program_count = fields.Integer(
        compute="_compute_program_count",
        string="Programs",
    )

    # KPI tracking
    kpi_snapshot_ids = fields.One2many(
        "ppm.kpi.snapshot",
        "portfolio_id",
        string="KPI Snapshots",
    )

    # Health scoring
    health_status = fields.Selection(
        [
            ("green", "On Track"),
            ("yellow", "At Risk"),
            ("red", "Critical"),
            ("grey", "Not Started"),
        ],
        string="Health Status",
        compute="_compute_health_status",
        store=True,
        tracking=True,
    )
    health_score = fields.Integer(
        string="Health Score",
        compute="_compute_health_status",
        store=True,
        help="0-100 score based on program health",
    )

    # Budget rollup
    total_budget = fields.Monetary(
        string="Total Budget",
        compute="_compute_budget_rollup",
        currency_field="currency_id",
    )
    total_actual = fields.Monetary(
        string="Total Actual",
        compute="_compute_budget_rollup",
        currency_field="currency_id",
    )
    budget_variance_pct = fields.Float(
        string="Budget Variance %",
        compute="_compute_budget_rollup",
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    # Dates
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="Target End Date")

    @api.depends("program_ids")
    def _compute_program_count(self):
        for rec in self:
            rec.program_count = len(rec.program_ids)

    @api.depends("program_ids.health_status", "program_ids.health_score")
    def _compute_health_status(self):
        for portfolio in self:
            programs = portfolio.program_ids
            if not programs:
                portfolio.health_status = "grey"
                portfolio.health_score = 0
                continue

            # Count by status
            red_count = len(programs.filtered(lambda p: p.health_status == "red"))
            yellow_count = len(programs.filtered(lambda p: p.health_status == "yellow"))

            # Aggregate score
            scores = [p.health_score for p in programs if p.health_score]
            avg_score = sum(scores) / len(scores) if scores else 0

            # Determine status
            if red_count > 0:
                portfolio.health_status = "red"
            elif yellow_count > 0:
                portfolio.health_status = "yellow"
            else:
                portfolio.health_status = "green"

            portfolio.health_score = int(avg_score)

    @api.depends("program_ids.budget", "program_ids.actual_cost")
    def _compute_budget_rollup(self):
        for portfolio in self:
            programs = portfolio.program_ids
            portfolio.total_budget = sum(programs.mapped("budget"))
            portfolio.total_actual = sum(programs.mapped("actual_cost"))
            if portfolio.total_budget:
                portfolio.budget_variance_pct = (
                    (portfolio.total_actual - portfolio.total_budget)
                    / portfolio.total_budget
                ) * 100
            else:
                portfolio.budget_variance_pct = 0

    _sql_constraints = [
        ("code_unique", "UNIQUE(code)", "Portfolio code must be unique!"),
    ]
