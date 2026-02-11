from odoo import api, fields, models


class OkrKeyResult(models.Model):
    _name = "okr.key.result"
    _description = "OKR Key Result"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "due_date asc, id desc"

    objective_id = fields.Many2one(
        "okr.objective", required=True, ondelete="cascade", index=True, tracking=True
    )
    owner_user_id = fields.Many2one("res.users", default=lambda self: self.env.user, tracking=True)

    title = fields.Char(required=True, tracking=True)
    metric_type = fields.Selection(
        [
            ("number", "Number"),
            ("percent", "Percent"),
            ("currency", "Currency"),
            ("boolean", "Boolean"),
        ],
        default="number",
        tracking=True,
    )
    unit = fields.Char()

    baseline_value = fields.Float()
    target_value = fields.Float(required=True)
    current_value = fields.Float()
    scoring_method = fields.Selection(
        [
            ("linear", "Linear"),
            ("threshold", "Threshold"),
        ],
        default="linear",
    )

    weight = fields.Float()
    due_date = fields.Date()
    last_checkin_at = fields.Datetime()

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

    checkin_ids = fields.One2many("okr.checkin", "key_result_id")
    initiative_ids = fields.One2many("okr.initiative", "key_result_id")

    progress = fields.Float(compute="_compute_progress", store=True)

    @api.depends("baseline_value", "target_value", "current_value", "metric_type")
    def _compute_progress(self):
        for kr in self:
            if kr.metric_type == "boolean":
                kr.progress = 100.0 if (kr.current_value or 0.0) >= 1.0 else 0.0
                continue
            denom = (
                (kr.target_value - kr.baseline_value)
                if (kr.target_value is not None and kr.baseline_value is not None)
                else 0.0
            )
            if denom == 0:
                kr.progress = 0.0
            else:
                kr.progress = max(
                    0.0, min(100.0, ((kr.current_value - kr.baseline_value) / denom) * 100.0)
                )
