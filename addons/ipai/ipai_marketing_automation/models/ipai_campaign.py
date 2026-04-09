import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IpaiCampaign(models.Model):
    _name = "ipai.marketing.campaign"
    _description = "Marketing Automation Campaign"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("running", "Running"),
            ("paused", "Paused"),
            ("done", "Done"),
        ],
        default="draft",
        tracking=True,
        required=True,
    )
    model_id = fields.Many2one(
        "ir.model",
        string="Target Model",
        required=True,
        ondelete="cascade",
        domain=[("model", "in", ["crm.lead", "res.partner", "mailing.contact"])],
        help="Model on which participants are tracked",
    )
    model_name = fields.Char(related="model_id.model", store=True)
    domain = fields.Char(
        default="[]",
        help="Filter for target records",
    )
    step_ids = fields.One2many(
        "ipai.marketing.campaign.step",
        "campaign_id",
        string="Steps",
    )
    participant_ids = fields.One2many(
        "ipai.marketing.campaign.participant",
        "campaign_id",
        string="Participants",
    )
    participant_count = fields.Integer(compute="_compute_participant_count")
    mailing_list_id = fields.Many2one(
        "mailing.list", string="Mailing List"
    )
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company
    )

    @api.depends("participant_ids")
    def _compute_participant_count(self):
        for rec in self:
            rec.participant_count = len(rec.participant_ids)

    def action_start(self):
        self.ensure_one()
        if not self.step_ids:
            raise UserError(_("Add at least one step before starting."))
        self._sync_participants()
        self.state = "running"

    def action_pause(self):
        self.ensure_one()
        self.state = "paused"

    def action_resume(self):
        self.ensure_one()
        self.state = "running"

    def action_done(self):
        self.ensure_one()
        self.state = "done"

    def action_reset_draft(self):
        self.ensure_one()
        self.state = "draft"

    def _sync_participants(self):
        """Add new matching records as participants."""
        self.ensure_one()
        domain = eval(self.domain or "[]")  # noqa: S307
        target_model = self.env[self.model_name]
        records = target_model.search(domain)
        existing_res_ids = set(
            self.participant_ids.mapped("res_id")
        )
        new_participants = []
        for rec in records:
            if rec.id not in existing_res_ids:
                new_participants.append(
                    {
                        "campaign_id": self.id,
                        "res_id": rec.id,
                    }
                )
        if new_participants:
            self.env["ipai.marketing.campaign.participant"].create(
                new_participants
            )
        _logger.info(
            "Campaign %s: synced %d new participants (total %d)",
            self.name,
            len(new_participants),
            len(self.participant_ids) + len(new_participants),
        )

    def action_view_participants(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Participants"),
            "res_model": "ipai.marketing.campaign.participant",
            "view_mode": "list",
            "domain": [("campaign_id", "=", self.id)],
            "context": {"default_campaign_id": self.id},
        }

    @api.model
    def _cron_execute_campaigns(self):
        """Cron: process all running campaigns."""
        campaigns = self.search([("state", "=", "running")])
        for campaign in campaigns:
            campaign._sync_participants()
            for step in campaign.step_ids.sorted("sequence"):
                step._execute_step()
