from odoo import api, fields, models


class OkrObjective(models.Model):
    _name = "okr.objective"
    _description = "OKR Objective"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    cycle_id = fields.Many2one("okr.cycle", required=True, ondelete="cascade", tracking=True)
    parent_objective_id = fields.Many2one("okr.objective", ondelete="set null")
    child_objective_ids = fields.One2many("okr.objective", "parent_objective_id")

    owner_user_id = fields.Many2one(
        "res.users", required=True, default=lambda self: self.env.user, tracking=True
    )

    portfolio_id = fields.Many2one("ppm.portfolio", ondelete="set null", tracking=True)
    program_id = fields.Many2one("ppm.program", ondelete="set null", tracking=True)
    project_id = fields.Many2one("project.project", ondelete="set null", tracking=True)

    title = fields.Char(required=True, tracking=True)
    description = fields.Text()
    weight = fields.Float()

    status = fields.Selection(
        [
            ("on_track", "On Track"),
            ("at_risk", "At Risk"),
            ("off_track", "Off Track"),
        ],
        default="on_track",
        tracking=True,
    )
    confidence = fields.Selection(
        [(str(i), str(i)) for i in range(1, 6)], default="4", tracking=True
    )

    key_result_ids = fields.One2many("okr.key.result", "objective_id")
    initiative_ids = fields.One2many("okr.initiative", "objective_id")

    progress = fields.Float(compute="_compute_progress", store=True)

    @api.depends("key_result_ids.progress")
    def _compute_progress(self):
        for o in self:
            krs = o.key_result_ids
            o.progress = sum(krs.mapped("progress")) / len(krs) if krs else 0.0
