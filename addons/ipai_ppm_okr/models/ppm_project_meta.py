from odoo import fields, models


class PpmProjectMeta(models.Model):
    _name = "ppm.project.meta"
    _description = "PPM Project Meta"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    project_id = fields.Many2one(
        "project.project", required=True, ondelete="cascade", index=True
    )
    portfolio_id = fields.Many2one("ppm.portfolio", ondelete="set null", tracking=True)
    program_id = fields.Many2one("ppm.program", ondelete="set null", tracking=True)

    business_case = fields.Text()
    expected_benefits = fields.Text()

    priority_rank = fields.Integer()
    strategic_score = fields.Float()
    risk_score = fields.Float()

    capex_budget = fields.Float()
    opex_budget = fields.Float()
    currency_code = fields.Char(help="ISO currency code (simple CE-only field).")

    governance_owner_user_id = fields.Many2one("res.users", tracking=True)
    steering_group_notes = fields.Text()

    _sql_constraints = [
        (
            "ppm_project_meta_project_uniq",
            "unique(project_id)",
            "Only one meta record per project.",
        ),
    ]
