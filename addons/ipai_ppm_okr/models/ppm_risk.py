from odoo import api, fields, models


class PpmRisk(models.Model):
    _name = "ppm.risk"
    _description = "PPM Risk"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "score desc, id desc"

    project_id = fields.Many2one(
        "project.project", required=True, ondelete="cascade", index=True, tracking=True
    )
    task_id = fields.Many2one("project.task", ondelete="set null", index=True)
    title = fields.Char(required=True, tracking=True)
    description = fields.Text()

    probability = fields.Selection(
        [(str(i), str(i)) for i in range(1, 6)], default="3", tracking=True
    )
    impact = fields.Selection(
        [(str(i), str(i)) for i in range(1, 6)], default="3", tracking=True
    )
    score = fields.Integer(compute="_compute_score", store=True)

    mitigation_plan = fields.Text()
    owner_user_id = fields.Many2one(
        "res.users", default=lambda self: self.env.user, tracking=True
    )
    due_date = fields.Date()
    status = fields.Selection(
        [
            ("open", "Open"),
            ("mitigating", "Mitigating"),
            ("closed", "Closed"),
        ],
        default="open",
        tracking=True,
    )

    @api.depends("probability", "impact")
    def _compute_score(self):
        for r in self:
            r.score = int(r.probability or "0") * int(r.impact or "0")
