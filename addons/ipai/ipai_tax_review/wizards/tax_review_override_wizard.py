"""TaxPulse PH — Override wizard with mandatory reason.

Constitution C2.4: every decision includes human-readable explanations.
Override must capture a reason and post it to the chatter.
"""

from odoo import fields, models
from odoo.exceptions import UserError


class TaxReviewOverrideWizard(models.TransientModel):
    _name = "ipai.tax.review.override.wizard"
    _description = "Tax Review Override Wizard"

    review_id = fields.Many2one(
        "ipai.tax.review",
        string="Tax Review",
        required=True,
    )
    override_reason = fields.Text(
        string="Override Reason",
        required=True,
        help="Explain why this review is being overridden despite findings.",
    )

    def action_confirm_override(self):
        """Apply override with reason."""
        self.ensure_one()
        if not self.override_reason.strip():
            raise UserError("An override reason is required.")
        self.review_id.write({
            "state": "overridden",
            "reviewer_id": self.env.uid,
            "reviewed_date": fields.Datetime.now(),
            "override_reason": self.override_reason,
        })
        self.review_id.message_post(
            body=f"Review overridden by {self.env.user.name}.\n"
                 f"Reason: {self.override_reason}",
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )
        return {"type": "ir.actions.act_window_close"}
