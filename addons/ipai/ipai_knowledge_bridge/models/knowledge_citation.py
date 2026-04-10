from odoo import fields, models


class KnowledgeCitation(models.Model):
    _name = "ipai.knowledge.citation"
    _description = "Knowledge Citation"
    _order = "rank asc"

    query_log_id = fields.Many2one(
        "ipai.knowledge.query.log",
        required=True,
        ondelete="cascade",
        index=True,
    )
    rank = fields.Integer()
    document_title = fields.Char()
    document_url = fields.Char()
    section_heading = fields.Char()
    chunk_text = fields.Text()
    score = fields.Float()
    source_id = fields.Many2one("ipai.knowledge.source")
