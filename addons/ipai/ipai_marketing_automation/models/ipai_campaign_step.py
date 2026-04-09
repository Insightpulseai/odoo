import logging
from datetime import timedelta

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class IpaiCampaignStep(models.Model):
    _name = "ipai.marketing.campaign.step"
    _description = "Campaign Automation Step"
    _order = "sequence"

    campaign_id = fields.Many2one(
        "ipai.marketing.campaign", required=True, ondelete="cascade"
    )
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    trigger_type = fields.Selection(
        [
            ("begin", "On Campaign Start"),
            ("delay", "After Delay"),
            ("condition", "If Condition Met"),
        ],
        required=True,
        default="delay",
    )
    delay_days = fields.Integer(
        string="Delay (Days)",
        default=0,
        help="Days to wait after previous step or enrollment",
    )
    delay_hours = fields.Integer(
        string="Delay (Hours)",
        default=0,
    )
    condition_domain = fields.Char(
        default="[]",
        help="Domain filter on target records — only matching participants proceed",
    )
    action_type = fields.Selection(
        [
            ("send_mailing", "Send Mailing"),
            ("add_tag", "Add Tag"),
            ("move_stage", "Move CRM Stage"),
            ("create_activity", "Create Activity"),
        ],
        required=True,
        default="send_mailing",
    )
    mailing_id = fields.Many2one(
        "mailing.mailing",
        string="Mailing",
        help="Mailing to send (for send_mailing action)",
    )
    tag_id = fields.Many2one(
        "crm.tag",
        string="CRM Tag",
        help="Tag to add (for add_tag action)",
    )
    stage_id = fields.Many2one(
        "crm.stage",
        string="CRM Stage",
        help="Stage to move to (for move_stage action)",
    )
    activity_type_id = fields.Many2one(
        "mail.activity.type",
        string="Activity Type",
    )
    activity_summary = fields.Char(string="Activity Summary")
    processed_count = fields.Integer(
        compute="_compute_processed_count",
    )

    @api.depends("campaign_id.participant_ids.current_step_id")
    def _compute_processed_count(self):
        for step in self:
            step.processed_count = self.env[
                "ipai.marketing.campaign.participant"
            ].search_count(
                [
                    ("campaign_id", "=", step.campaign_id.id),
                    ("last_completed_step_id", "=", step.id),
                ]
            )

    def _execute_step(self):
        """Process eligible participants for this step."""
        self.ensure_one()
        campaign = self.campaign_id
        if campaign.state != "running":
            return

        delay = timedelta(
            days=self.delay_days, hours=self.delay_hours
        )
        now = fields.Datetime.now()

        participants = self.env[
            "ipai.marketing.campaign.participant"
        ].search(
            [
                ("campaign_id", "=", campaign.id),
                ("state", "=", "active"),
                ("current_step_id", "=", self._get_previous_step_id()),
            ]
        )

        for participant in participants:
            if participant.step_completed_at and (
                participant.step_completed_at + delay > now
            ):
                continue

            if self.trigger_type == "condition":
                domain = eval(self.condition_domain or "[]")  # noqa: S307
                target = self.env[campaign.model_name].browse(
                    participant.res_id
                )
                if not target.filtered_domain(domain):
                    continue

            self._apply_action(participant)
            participant.write(
                {
                    "current_step_id": self.id,
                    "last_completed_step_id": self.id,
                    "step_completed_at": now,
                }
            )

        _logger.info(
            "Step %s/%s: processed %d participants",
            campaign.name,
            self.name,
            len(participants),
        )

    def _get_previous_step_id(self):
        """Get the step ID that should precede this one."""
        steps = self.campaign_id.step_ids.sorted("sequence")
        idx = list(steps.ids).index(self.id)
        if idx == 0:
            return False
        return steps[idx - 1].id

    def _apply_action(self, participant):
        """Execute the configured action on a participant."""
        target = self.env[self.campaign_id.model_name].browse(
            participant.res_id
        )
        if not target.exists():
            participant.state = "error"
            return

        if self.action_type == "send_mailing" and self.mailing_id:
            self.mailing_id.with_context(
                default_res_ids=[target.id]
            ).action_send_mail()
        elif self.action_type == "add_tag" and self.tag_id:
            if hasattr(target, "tag_ids"):
                target.write({"tag_ids": [(4, self.tag_id.id)]})
        elif self.action_type == "move_stage" and self.stage_id:
            if hasattr(target, "stage_id"):
                target.stage_id = self.stage_id
        elif self.action_type == "create_activity":
            if hasattr(target, "activity_schedule"):
                target.activity_schedule(
                    act_type_xmlid=False,
                    date_deadline=fields.Date.today()
                    + timedelta(days=3),
                    summary=self.activity_summary or self.name,
                    activity_type_id=self.activity_type_id.id
                    if self.activity_type_id
                    else False,
                )
