"""TaxPulse PH — AI-generated explanation records.

Constitution C3.3: AI may explain findings and propose actions,
but may NOT determine whether tax math is correct.

Each explanation is a Foundry-generated summary linked to a review.
"""

from odoo import api, fields, models


class TaxReviewExplanation(models.Model):
    _name = "ipai.tax.review.explanation"
    _description = "Tax Review AI Explanation"
    _order = "create_date desc"

    review_id = fields.Many2one(
        "ipai.tax.review",
        string="Tax Review",
        required=True,
        ondelete="cascade",
        index=True,
    )
    explanation_text = fields.Html(
        string="Explanation",
        help="AI-generated explanation of findings",
    )
    suggested_resolution = fields.Text(
        string="Suggested Resolution",
        help="AI-suggested steps to resolve the findings",
    )
    model_id = fields.Char(
        string="Model ID",
        help="AI model used to generate this explanation",
    )
    prompt_tokens = fields.Integer(string="Prompt Tokens")
    completion_tokens = fields.Integer(string="Completion Tokens")
    confidence_score = fields.Float(
        string="Explanation Confidence",
        digits=(4, 2),
    )
    generated_at = fields.Datetime(
        string="Generated At",
        default=fields.Datetime.now,
    )

    def action_apply_suggestion(self):
        """Post suggested resolution as a note on the review."""
        self.ensure_one()
        if self.suggested_resolution:
            self.review_id.message_post(
                body=f"<b>AI Suggested Resolution:</b><br/>{self.suggested_resolution}",
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
