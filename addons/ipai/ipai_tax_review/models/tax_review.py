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

    # Source
    source_attachment_id = fields.Many2one(
        "ir.attachment", string="Source Attachment"
    )
    extraction_confidence = fields.Float(string="Extraction Confidence", digits=(4, 2))

    def action_override(self):
        """Override the review — mark as accepted despite findings."""
        self.ensure_one()
        self.write({
            "state": "overridden",
            "reviewer_id": self.env.uid,
            "reviewed_date": fields.Datetime.now(),
        })
        self.message_post(
            body=f"Review overridden by {self.env.user.name}. Reason: {self.override_reason or 'No reason provided'}",
        )

    def action_reject(self):
        """Reject the document — block posting permanently."""
        self.ensure_one()
        self.write({
            "state": "rejected",
            "reviewer_id": self.env.uid,
            "reviewed_date": fields.Datetime.now(),
        })
        self.message_post(body=f"Review rejected by {self.env.user.name}.")
