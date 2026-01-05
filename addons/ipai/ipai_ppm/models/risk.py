# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PpmRisk(models.Model):
    """Risk register for portfolios, programs, and projects."""

    _name = "ppm.risk"
    _description = "PPM Risk"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "risk_score desc, create_date desc"

    name = fields.Char(
        string="Risk Title",
        required=True,
        tracking=True,
    )
    code = fields.Char(
        string="Risk ID",
        readonly=True,
        copy=False,
        default="New",
    )

    # Scope
    scope = fields.Selection(
        [
            ("portfolio", "Portfolio"),
            ("program", "Program"),
            ("project", "Project"),
        ],
        string="Scope",
        required=True,
        default="project",
    )
    portfolio_id = fields.Many2one(
        "ppm.portfolio",
        string="Portfolio",
    )
    program_id = fields.Many2one(
        "ppm.program",
        string="Program",
    )
    project_id = fields.Many2one(
        "project.project",
        string="Project",
    )

    # Classification
    category = fields.Selection(
        [
            ("schedule", "Schedule"),
            ("cost", "Cost/Budget"),
            ("scope", "Scope"),
            ("resource", "Resource"),
            ("technical", "Technical"),
            ("external", "External/Vendor"),
            ("compliance", "Compliance/Regulatory"),
            ("security", "Security"),
            ("other", "Other"),
        ],
        string="Category",
        required=True,
        default="other",
    )

    description = fields.Text(
        string="Description",
        help="Detailed description of the risk",
    )

    # Impact & Probability (1-5 scale)
    impact = fields.Selection(
        [
            ("1", "1 - Negligible"),
            ("2", "2 - Minor"),
            ("3", "3 - Moderate"),
            ("4", "4 - Major"),
            ("5", "5 - Severe"),
        ],
        string="Impact",
        required=True,
        default="3",
        tracking=True,
    )
    probability = fields.Selection(
        [
            ("1", "1 - Rare"),
            ("2", "2 - Unlikely"),
            ("3", "3 - Possible"),
            ("4", "4 - Likely"),
            ("5", "5 - Almost Certain"),
        ],
        string="Probability",
        required=True,
        default="3",
        tracking=True,
    )

    # Computed risk score
    risk_score = fields.Integer(
        string="Risk Score",
        compute="_compute_risk_score",
        store=True,
        help="Impact x Probability (1-25)",
    )
    severity = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Severity",
        compute="_compute_risk_score",
        store=True,
    )

    # Mitigation
    mitigation_strategy = fields.Selection(
        [
            ("avoid", "Avoid"),
            ("mitigate", "Mitigate"),
            ("transfer", "Transfer"),
            ("accept", "Accept"),
        ],
        string="Strategy",
        default="mitigate",
    )
    mitigation_plan = fields.Text(
        string="Mitigation Plan",
        help="Actions to reduce risk likelihood or impact",
    )
    contingency_plan = fields.Text(
        string="Contingency Plan",
        help="Actions if risk materializes",
    )

    # Ownership
    owner_id = fields.Many2one(
        "res.users",
        string="Risk Owner",
        tracking=True,
    )
    assigned_to_id = fields.Many2one(
        "res.users",
        string="Assigned To",
        help="Person responsible for mitigation actions",
    )

    # Status
    status = fields.Selection(
        [
            ("identified", "Identified"),
            ("open", "Open/Active"),
            ("mitigating", "Mitigating"),
            ("closed", "Closed"),
            ("realized", "Realized (Issue)"),
        ],
        string="Status",
        default="identified",
        tracking=True,
    )

    # Dates
    date_identified = fields.Date(
        string="Date Identified",
        default=fields.Date.context_today,
    )
    date_target = fields.Date(
        string="Target Resolution Date",
    )
    date_closed = fields.Date(
        string="Date Closed",
    )

    # Financial impact
    potential_cost = fields.Monetary(
        string="Potential Cost Impact",
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    @api.depends("impact", "probability")
    def _compute_risk_score(self):
        for risk in self:
            impact_val = int(risk.impact) if risk.impact else 0
            prob_val = int(risk.probability) if risk.probability else 0
            score = impact_val * prob_val
            risk.risk_score = score

            # Determine severity
            if score >= 15:
                risk.severity = "critical"
            elif score >= 10:
                risk.severity = "high"
            elif score >= 5:
                risk.severity = "medium"
            else:
                risk.severity = "low"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code", "New") == "New":
                vals["code"] = self.env["ir.sequence"].next_by_code("ppm.risk") or "New"
        return super().create(vals_list)

    def action_open(self):
        self.write({"status": "open"})

    def action_close(self):
        self.write(
            {
                "status": "closed",
                "date_closed": fields.Date.context_today(self),
            }
        )
