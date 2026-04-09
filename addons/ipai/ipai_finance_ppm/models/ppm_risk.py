"""PPM Risk Register — project risk tracking.

Delta model: CE/OCA do not provide a risk register for projects.
"""

from odoo import fields, models


class PPMRisk(models.Model):
    _name = "ppm.risk"
    _description = "PPM Risk"
    _order = "risk_score desc, create_date desc"

    name = fields.Char(string="Risk Title", required=True)
    project_id = fields.Many2one(
        "project.project",
        string="Project",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        related="project_id.company_id",
        store=True,
    )
    description = fields.Text(string="Description")
    category = fields.Selection(
        [
            ("financial", "Financial"),
            ("schedule", "Schedule"),
            ("resource", "Resource"),
            ("technical", "Technical"),
            ("compliance", "Compliance"),
            ("external", "External"),
        ],
        string="Category",
        default="financial",
    )
    state = fields.Selection(
        [
            ("identified", "Identified"),
            ("assessed", "Assessed"),
            ("mitigating", "Mitigating"),
            ("accepted", "Accepted"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="identified",
        tracking=True,
    )
    probability = fields.Selection(
        [("1", "Very Low"), ("2", "Low"), ("3", "Medium"), ("4", "High"), ("5", "Very High")],
        string="Probability",
        default="3",
    )
    impact = fields.Selection(
        [("1", "Very Low"), ("2", "Low"), ("3", "Medium"), ("4", "High"), ("5", "Very High")],
        string="Impact",
        default="3",
    )
    risk_score = fields.Integer(
        string="Risk Score",
        compute="_compute_risk_score",
        store=True,
    )
    owner_id = fields.Many2one("res.users", string="Risk Owner")
    mitigation_plan = fields.Text(string="Mitigation Plan")
    target_date = fields.Date(string="Target Resolution Date")

    def _compute_risk_score(self):
        for risk in self:
            p = int(risk.probability or "0")
            i = int(risk.impact or "0")
            risk.risk_score = p * i
