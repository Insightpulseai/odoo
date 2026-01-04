from odoo.exceptions import ValidationError

from odoo import api, fields, models


class CrmLead(models.Model):
    """
    Enhanced CRM Lead with Salesforce-like pipeline features.

    Capability ID: crm.pipeline.board
    """

    _inherit = "crm.lead"

    # Stage rule validation
    stage_rule_validated = fields.Boolean(
        string="Stage Rules Met",
        compute="_compute_stage_rule_validated",
        store=True,
    )

    stage_missing_fields = fields.Char(
        string="Missing Required Fields",
        compute="_compute_stage_rule_validated",
        store=True,
    )

    # Quick action tracking
    last_call_date = fields.Datetime(
        string="Last Call",
        tracking=True,
    )

    last_meeting_date = fields.Datetime(
        string="Last Meeting",
        tracking=True,
    )

    # Pipeline metrics
    days_in_stage = fields.Integer(
        string="Days in Stage",
        compute="_compute_days_in_stage",
    )

    stage_entry_date = fields.Datetime(
        string="Stage Entry Date",
        tracking=True,
    )

    @api.depends(
        "stage_id", "name", "contact_name", "partner_id", "email_from", "phone"
    )
    def _compute_stage_rule_validated(self):
        """Check if all stage-required fields are filled."""
        for lead in self:
            if not lead.stage_id:
                lead.stage_rule_validated = True
                lead.stage_missing_fields = False
                continue

            # Get required fields for this stage
            required_fields = lead.stage_id.ipai_required_field_ids.mapped("name")
            missing = []

            for field_name in required_fields:
                if hasattr(lead, field_name):
                    value = getattr(lead, field_name)
                    if not value:
                        # Get field label for user-friendly message
                        field_obj = lead._fields.get(field_name)
                        label = field_obj.string if field_obj else field_name
                        missing.append(label)

            lead.stage_rule_validated = len(missing) == 0
            lead.stage_missing_fields = ", ".join(missing) if missing else False

    @api.depends("stage_entry_date")
    def _compute_days_in_stage(self):
        """Compute days since entering current stage."""
        for lead in self:
            if lead.stage_entry_date:
                delta = fields.Datetime.now() - lead.stage_entry_date
                lead.days_in_stage = delta.days
            else:
                lead.days_in_stage = 0

    def write(self, vals):
        """Track stage changes for days-in-stage calculation."""
        if "stage_id" in vals:
            vals["stage_entry_date"] = fields.Datetime.now()

            # Validate stage rules before transition (if enforced)
            for lead in self:
                if lead.stage_id:
                    new_stage = self.env["crm.stage"].browse(vals["stage_id"])
                    if new_stage.ipai_enforce_rules and not lead.stage_rule_validated:
                        raise ValidationError(
                            f"Cannot move to '{new_stage.name}' - "
                            f"missing required fields: {lead.stage_missing_fields}"
                        )

        return super().write(vals)

    # -------------------------------------------------------------------------
    # Quick Actions
    # -------------------------------------------------------------------------

    def action_quick_call(self):
        """Log a quick call activity."""
        self.ensure_one()
        self.last_call_date = fields.Datetime.now()

        # Create activity/message
        self.message_post(
            body="<p><b>Call logged</b></p>",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )

        # Open activity scheduling wizard if mail.activity available
        if "mail.activity" in self.env:
            return {
                "name": "Log Call",
                "type": "ir.actions.act_window",
                "res_model": "mail.activity",
                "view_mode": "form",
                "target": "new",
                "context": {
                    "default_res_model": "crm.lead",
                    "default_res_id": self.id,
                    "default_activity_type_id": (
                        self.env.ref(
                            "mail.mail_activity_data_call", raise_if_not_found=False
                        ).id
                        if self.env.ref(
                            "mail.mail_activity_data_call", raise_if_not_found=False
                        )
                        else False
                    ),
                },
            }

        return True

    def action_quick_meeting(self):
        """Schedule a quick meeting."""
        self.ensure_one()
        self.last_meeting_date = fields.Datetime.now()

        # Open calendar event creation
        return {
            "name": "Schedule Meeting",
            "type": "ir.actions.act_window",
            "res_model": "calendar.event",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_name": f"Meeting: {self.name}",
                "default_res_model": "crm.lead",
                "default_res_id": self.id,
                "default_opportunity_id": (
                    self.id if self.type == "opportunity" else False
                ),
            },
        }

    def action_quick_email(self):
        """Compose a quick email."""
        self.ensure_one()

        # Get email template if available
        template = self.env.ref(
            "crm.email_template_opportunity_mail", raise_if_not_found=False
        )

        return {
            "name": "Send Email",
            "type": "ir.actions.act_window",
            "res_model": "mail.compose.message",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_model": "crm.lead",
                "default_res_ids": [self.id],
                "default_template_id": template.id if template else False,
                "default_composition_mode": "comment",
            },
        }
