from odoo import fields, models


class KnowledgeQueryLog(models.Model):
    _name = "ipai.knowledge.query.log"
    _description = "Knowledge Query Log"
    _order = "create_date desc"

    source_id = fields.Many2one(
        "ipai.knowledge.source",
        index=True,
        ondelete="set null",
    )
    query_text = fields.Text(required=True)
    answer_text = fields.Html()
    citations_json = fields.Text(
        help="Raw JSON array of citation objects from Azure",
    )
    top_confidence = fields.Float(
        help="Highest citation score returned",
    )
    answer_confidence = fields.Float(
        help="Overall answer confidence",
    )
    was_abstained = fields.Boolean(
        help="True if below threshold and abstained",
    )
    model_used = fields.Char(
        help="Azure OpenAI deployment name",
    )
    latency_ms = fields.Integer(
        help="End-to-end roundtrip time in milliseconds",
    )
    caller_uid = fields.Many2one("res.users")
    caller_surface = fields.Char(
        help="finance_close, taxpulse, pulser, direct",
    )
    error_message = fields.Char()

    citation_ids = fields.One2many(
        "ipai.knowledge.citation", "query_log_id",
    )
    citation_count = fields.Integer(
        compute="_compute_citation_count",
    )

    def _compute_citation_count(self):
        for rec in self:
            rec.citation_count = len(rec.citation_ids)
