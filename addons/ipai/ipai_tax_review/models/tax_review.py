"""TaxPulse PH — Tax Review model.

Stores the result of deterministic invoice validation from the
TaxPulse PH service. Linked 1:1 to an account.move (vendor bill
or customer invoice).

Constitution C3.1: Odoo owns review states and audit visibility.
"""

from odoo import api, fields, models


class TaxReview(models.Model):
    _name = "ipai.tax.review"
    _description = "Tax Validation Review"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("ipai.tax.review") or "/",
    )
    move_id = fields.Many2one(
        "account.move",
        string="Accounting Document",
        required=True,
        ondelete="cascade",
        index=True,
    )
    state = fields.Selection(
        [
            ("validated", "Validated"),
            ("needs_review", "Needs Review"),
            ("rejected", "Rejected"),
            ("overridden", "Overridden"),
        ],
        string="Status",
        required=True,
        default="needs_review",
        tracking=True,
    )

    # Computed values from validator
    expected_subtotal = fields.Float(string="Expected Subtotal", digits=(16, 2))
    expected_vat = fields.Float(string="Expected VAT", digits=(16, 2))
    expected_gross = fields.Float(string="Expected Gross", digits=(16, 2))
    expected_withholding = fields.Float(string="Expected Withholding", digits=(16, 2))
    expected_payable = fields.Float(string="Expected Payable", digits=(16, 2))
    printed_total_due = fields.Float(string="Printed Total Due", digits=(16, 2))
    delta = fields.Float(string="Delta", digits=(16, 2))

    # Findings
    findings_json = fields.Text(string="Findings (JSON)")
    explanation_summary = fields.Text(string="Explanation Summary")

    # Review trail
    reviewer_id = fields.Many2one("res.users", string="Reviewer")
    override_reason = fields.Text(string="Override Reason")
    reviewed_date = fields.Datetime(string="Reviewed Date")

    # Explanations (Phase 3 — Foundry-generated)
    explanation_ids = fields.One2many(
        "ipai.tax.review.explanation",
        "review_id",
        string="AI Explanations",
    )
    explanation_count = fields.Integer(
        string="Explanation Count",
        compute="_compute_explanation_count",
    )

    # Source
    source_attachment_id = fields.Many2one(
        "ir.attachment", string="Source Attachment"
    )
    extraction_confidence = fields.Float(string="Extraction Confidence", digits=(4, 2))

    @api.depends("explanation_ids")
    def _compute_explanation_count(self):
        for review in self:
            review.explanation_count = len(review.explanation_ids)

    def action_request_explanation(self):
        """Request AI explanation from Foundry service.

        Creates a placeholder explanation record. In production, this
        triggers an async call to the Foundry explanation service.
        """
        self.ensure_one()
        self.env["ipai.tax.review.explanation"].create({
            "review_id": self.id,
            "explanation_text": (
                "<p><i>Explanation generation queued. "
                "The Foundry service will populate this when ready.</i></p>"
            ),
            "suggested_resolution": "",
            "model_id": "pending",
        })
        self.message_post(
            body="AI explanation requested.",
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )

    def action_override(self):
        """Open override wizard — requires mandatory reason."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Override Tax Review",
            "res_model": "ipai.tax.review.override.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_review_id": self.id},
        }

    def action_reject(self):
        """Reject the document — block posting permanently."""
        self.ensure_one()
        self.write({
            "state": "rejected",
            "reviewer_id": self.env.uid,
            "reviewed_date": fields.Datetime.now(),
        })
        self.message_post(body=f"Review rejected by {self.env.user.name}.")

    def action_reset_to_review(self):
        """Reset back to needs_review for re-evaluation."""
        self.ensure_one()
        self.write({
            "state": "needs_review",
            "reviewer_id": False,
            "reviewed_date": False,
            "override_reason": False,
        })
        self.message_post(body=f"Review reset to needs_review by {self.env.user.name}.")
