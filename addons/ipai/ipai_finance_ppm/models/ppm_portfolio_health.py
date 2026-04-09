"""PPM Portfolio Health — RAG status and health scoring per project.

Delta model: portfolio-level health rollup is not available in CE or OCA.
"""

from odoo import api, fields, models


class PPMPortfolioHealth(models.Model):
    _name = "ppm.portfolio.health"
    _description = "PPM Portfolio Health"
    _order = "assessment_date desc"
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
    assessment_date = fields.Date(
        string="Assessment Date",
        required=True,
        default=fields.Date.today,
    )
    assessor_id = fields.Many2one(
        "res.users",
        string="Assessor",
        default=lambda self: self.env.uid,
    )

    # RAG status
    schedule_rag = fields.Selection(
        [("green", "Green"), ("amber", "Amber"), ("red", "Red")],
        string="Schedule",
        required=True,
        default="green",
    )
    budget_rag = fields.Selection(
        [("green", "Green"), ("amber", "Amber"), ("red", "Red")],
        string="Budget",
        required=True,
        default="green",
    )
    scope_rag = fields.Selection(
        [("green", "Green"), ("amber", "Amber"), ("red", "Red")],
        string="Scope",
        required=True,
        default="green",
    )
    resource_rag = fields.Selection(
        [("green", "Green"), ("amber", "Amber"), ("red", "Red")],
        string="Resources",
        required=True,
        default="green",
    )
    overall_rag = fields.Selection(
        [("green", "Green"), ("amber", "Amber"), ("red", "Red")],
        string="Overall",
        compute="_compute_overall_rag",
        store=True,
    )

    health_score = fields.Float(
        string="Health Score",
        digits=(4, 1),
        compute="_compute_health_score",
        store=True,
        help="0-100 composite health score",
    )
    commentary = fields.Text(string="Commentary")

    @api.depends("schedule_rag", "budget_rag", "scope_rag", "resource_rag")
    def _compute_overall_rag(self):
        for rec in self:
            rags = [rec.schedule_rag, rec.budget_rag, rec.scope_rag, rec.resource_rag]
            if "red" in rags:
                rec.overall_rag = "red"
            elif "amber" in rags:
                rec.overall_rag = "amber"
            else:
                rec.overall_rag = "green"

    @api.depends("schedule_rag", "budget_rag", "scope_rag", "resource_rag")
    def _compute_health_score(self):
        rag_scores = {"green": 100, "amber": 50, "red": 0}
        for rec in self:
            scores = [
                rag_scores.get(rec.schedule_rag, 0),
                rag_scores.get(rec.budget_rag, 0),
                rag_scores.get(rec.scope_rag, 0),
                rag_scores.get(rec.resource_rag, 0),
            ]
            rec.health_score = sum(scores) / len(scores) if scores else 0
