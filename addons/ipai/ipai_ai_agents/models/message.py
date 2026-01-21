# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IPAIAIMessage(models.Model):
    _name = "ipai.ai.message"
    _description = "AI Message"
    _order = "create_date asc"

    thread_id = fields.Many2one("ipai.ai.thread", required=True, ondelete="cascade")
    role = fields.Selection(
        [
            ("user", "User"),
            ("assistant", "Assistant"),
            ("system", "System"),
        ],
        required=True,
    )
    content = fields.Text(required=True)

    # Citations and confidence
    citations_json = fields.Json(
        default=list, help="Array of {index, title, url, score} citation objects"
    )
    confidence = fields.Float(default=0.0, help="Confidence score (0.0 to 1.0)")
    is_uncertain = fields.Boolean(
        default=False,
        help="Flag indicating the response is uncertain and may need escalation",
    )

    # Metadata
    model_used = fields.Char(help="The LLM model used for this response")
    tokens_used = fields.Integer(help="Token count for this message")
    latency_ms = fields.Integer(help="Response latency in milliseconds")

    # Feedback
    feedback = fields.Selection(
        [
            ("positive", "Helpful"),
            ("negative", "Not Helpful"),
        ],
        help="User feedback on this response",
    )
    feedback_reason = fields.Text(help="Reason for feedback")

    @api.model
    def create(self, vals):
        """Override to auto-link to thread's company/user if not set."""
        res = super().create(vals)
        return res

    def action_mark_helpful(self):
        """Mark message as helpful."""
        self.ensure_one()
        self.feedback = "positive"

    def action_mark_unhelpful(self):
        """Mark message as not helpful."""
        self.ensure_one()
        self.feedback = "negative"
