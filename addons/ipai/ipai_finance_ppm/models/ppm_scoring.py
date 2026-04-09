"""PPM Investment Scoring — project prioritization model.

Delta model: investment scoring / prioritization is not in CE or OCA.
"""

from odoo import api, fields, models


class PPMScoring(models.Model):
    _name = "ppm.scoring"
    _description = "PPM Investment Scoring"
    _order = "total_score desc"
    _rec_name = "project_id"

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
    scored_by_id = fields.Many2one(
        "res.users",
        string="Scored By",
        default=lambda self: self.env.uid,
    )
    scored_date = fields.Date(
        string="Scored Date",
        default=fields.Date.today,
    )

    # Scoring dimensions (1-5 scale)
    strategic_alignment = fields.Integer(
        string="Strategic Alignment",
        default=3,
        help="1=Low, 5=High alignment with strategic objectives",
    )
    financial_benefit = fields.Integer(
        string="Financial Benefit",
        default=3,
        help="1=Low, 5=High expected financial return",
    )
    risk_level = fields.Integer(
        string="Risk Level (inverted)",
        default=3,
        help="1=Very High risk, 5=Very Low risk",
    )
    resource_availability = fields.Integer(
        string="Resource Availability",
        default=3,
        help="1=No resources, 5=Fully available",
    )
    urgency = fields.Integer(
        string="Urgency",
        default=3,
        help="1=Can wait, 5=Immediate",
    )

    total_score = fields.Float(
        string="Total Score",
        digits=(6, 1),
        compute="_compute_total_score",
        store=True,
    )
    investment_type = fields.Selection(
        [("run", "Run"), ("change", "Change"), ("grow", "Grow")],
        string="Investment Type",
        default="run",
    )
    recommendation = fields.Selection(
        [
            ("proceed", "Proceed"),
            ("defer", "Defer"),
            ("cancel", "Cancel"),
            ("review", "Review"),
        ],
        string="Recommendation",
    )
    notes = fields.Text(string="Notes")

    @api.depends(
        "strategic_alignment", "financial_benefit",
        "risk_level", "resource_availability", "urgency",
    )
    def _compute_total_score(self):
        for rec in self:
            rec.total_score = (
                rec.strategic_alignment
                + rec.financial_benefit
                + rec.risk_level
                + rec.resource_availability
                + rec.urgency
            )
