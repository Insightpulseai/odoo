from odoo import _, api, fields, models


class IpaiCampaignParticipant(models.Model):
    _name = "ipai.marketing.campaign.participant"
    _description = "Campaign Participant"
    _order = "create_date desc"

    campaign_id = fields.Many2one(
        "ipai.marketing.campaign", required=True, ondelete="cascade"
    )
    res_id = fields.Integer(string="Record ID", required=True, index=True)
    state = fields.Selection(
        [
            ("active", "Active"),
            ("completed", "Completed"),
            ("error", "Error"),
            ("excluded", "Excluded"),
        ],
        default="active",
        required=True,
    )
    current_step_id = fields.Many2one(
        "ipai.marketing.campaign.step",
        string="Current Step",
    )
    last_completed_step_id = fields.Many2one(
        "ipai.marketing.campaign.step",
        string="Last Completed Step",
    )
    step_completed_at = fields.Datetime(string="Step Completed At")
    enrolled_at = fields.Datetime(
        default=fields.Datetime.now,
    )
    record_name = fields.Char(
        compute="_compute_record_name",
        string="Record",
    )

    @api.depends("res_id", "campaign_id.model_name")
    def _compute_record_name(self):
        for rec in self:
            if rec.campaign_id.model_name and rec.res_id:
                target = self.env[rec.campaign_id.model_name].browse(
                    rec.res_id
                )
                rec.record_name = (
                    target.display_name if target.exists() else _("Deleted")
                )
            else:
                rec.record_name = False

    _sql_constraints = [
        (
            "unique_participant",
            "unique(campaign_id, res_id)",
            "A record can only participate once per campaign.",
        ),
    ]
