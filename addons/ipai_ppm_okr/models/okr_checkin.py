from odoo import api, fields, models


class OkrCheckin(models.Model):
    _name = "okr.checkin"
    _description = "OKR Check-in"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "checkin_at desc"

    key_result_id = fields.Many2one(
        "okr.key.result", required=True, ondelete="cascade", index=True, tracking=True
    )
    checkin_at = fields.Datetime(required=True, default=fields.Datetime.now)
    value = fields.Float()
    confidence = fields.Selection(
        [(str(i), str(i)) for i in range(1, 6)], default="4", tracking=True
    )
    comment = fields.Text()
    user_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user)

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for r in recs:
            r.key_result_id.write(
                {
                    "current_value": r.value,
                    "last_checkin_at": r.checkin_at,
                }
            )
        return recs
