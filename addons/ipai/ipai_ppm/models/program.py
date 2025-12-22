# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PpmProgram(models.Model):
    """Program container linking multiple projects."""

    _name = "ppm.program"
    _description = "PPM Program"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    name = fields.Char(
        string="Program Name",
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
        copy=False,
        help="Unique program identifier (e.g., PG-FINANCE-2025)",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Parent portfolio
    portfolio_id = fields.Many2one(
        "ppm.portfolio",
        string="Portfolio",
        tracking=True,
        ondelete="restrict",
    )

    # Program ownership
    program_manager_id = fields.Many2one(
        "res.users",
        string="Program Manager",
        tracking=True,
    )
    sponsor_id = fields.Many2one(
        "res.users",
        string="Sponsor",
    )

    description = fields.Html(string="Description")
    objectives = fields.Text(string="Program Objectives")

    # Linked projects (M2M for flexibility)
    project_ids = fields.Many2many(
        "project.project",
        "ppm_program_project_rel",
        "program_id",
        "project_id",
        string="Projects",
    )
    project_count = fields.Integer(
        compute="_compute_project_count",
        string="Projects",
    )

    # Budget
    budget = fields.Monetary(
        string="Budget",
        currency_field="currency_id",
        tracking=True,
    )
    actual_cost = fields.Monetary(
        string="Actual Cost",
        currency_field="currency_id",
        compute="_compute_actual_cost",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    # Dates
    date_start = fields.Date(string="Start Date", tracking=True)
    date_end = fields.Date(string="Target End Date", tracking=True)

    # Health status
    health_status = fields.Selection(
        [
            ("green", "On Track"),
            ("yellow", "At Risk"),
            ("red", "Critical"),
            ("grey", "Not Started"),
        ],
        string="Health Status",
        default="grey",
        tracking=True,
    )
    health_score = fields.Integer(
        string="Health Score",
        default=0,
        help="0-100 health score",
    )
    health_notes = fields.Text(string="Health Notes")

    # Risk summary
    risk_ids = fields.One2many(
        "ppm.risk",
        "program_id",
        string="Risks",
    )
    risk_count = fields.Integer(
        compute="_compute_risk_count",
        string="Risks",
    )
    open_high_risks = fields.Integer(
        compute="_compute_risk_count",
        string="Open High Risks",
    )

    # KPIs
    kpi_snapshot_ids = fields.One2many(
        "ppm.kpi.snapshot",
        "program_id",
        string="KPI Snapshots",
    )

    # Resource allocations
    allocation_ids = fields.One2many(
        "ppm.resource.allocation",
        "program_id",
        string="Resource Allocations",
    )

    @api.depends("project_ids")
    def _compute_project_count(self):
        for rec in self:
            rec.project_count = len(rec.project_ids)

    @api.depends("risk_ids", "risk_ids.status", "risk_ids.severity")
    def _compute_risk_count(self):
        for program in self:
            risks = program.risk_ids
            program.risk_count = len(risks)
            program.open_high_risks = len(
                risks.filtered(
                    lambda r: r.status == "open" and r.severity in ("high", "critical")
                )
            )

    @api.depends("project_ids")
    def _compute_actual_cost(self):
        """Compute actual cost from linked projects' analytic lines."""
        for program in self:
            # Sum from analytic accounts if available
            total = 0.0
            for project in program.project_ids:
                if project.analytic_account_id:
                    lines = self.env["account.analytic.line"].search(
                        [
                            ("account_id", "=", project.analytic_account_id.id),
                            ("amount", "<", 0),  # Costs are negative
                        ]
                    )
                    total += abs(sum(lines.mapped("amount")))
            program.actual_cost = total

    def action_view_projects(self):
        """Open projects linked to this program."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Projects - {self.name}",
            "res_model": "project.project",
            "view_mode": "kanban,list,form",
            "domain": [("id", "in", self.project_ids.ids)],
            "context": {"default_ppm_program_id": self.id},
        }

    def action_view_risks(self):
        """Open risks for this program."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Risks - {self.name}",
            "res_model": "ppm.risk",
            "view_mode": "list,form",
            "domain": [("program_id", "=", self.id)],
            "context": {"default_program_id": self.id},
        }

    _sql_constraints = [
        ("code_unique", "UNIQUE(code)", "Program code must be unique!"),
    ]


class ProjectProject(models.Model):
    """Extend project.project with program link."""

    _inherit = "project.project"

    ppm_program_ids = fields.Many2many(
        "ppm.program",
        "ppm_program_project_rel",
        "project_id",
        "program_id",
        string="Programs",
    )
