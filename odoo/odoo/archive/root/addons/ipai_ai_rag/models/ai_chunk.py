# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class IpaiAiChunk(models.Model):
    """Content chunk for RAG retrieval."""

    _name = "ipai.ai.chunk"
    _description = "IPAI AI Chunk"
    _order = "source_id, index"

    source_id = fields.Many2one(
        comodel_name="ipai.ai.source",
        string="Source",
        required=True,
        ondelete="cascade",
        index=True,
    )
    index = fields.Integer(
        string="Index",
        required=True,
        help="Position of this chunk within the source.",
    )
    content = fields.Text(
        string="Content",
        required=True,
    )
    content_hash = fields.Char(
        string="Content Hash",
        index=True,
        help="SHA-256 hash for deduplication.",
    )
    token_count = fields.Integer(
        string="Token Count",
        help="Number of tokens in this chunk.",
    )
    embedding_ids = fields.One2many(
        comodel_name="ipai.ai.embedding",
        inverse_name="chunk_id",
        string="Embeddings",
    )
    has_embedding = fields.Boolean(
        string="Has Embedding",
        compute="_compute_has_embedding",
        store=True,
    )
    company_id = fields.Many2one(
        related="source_id.company_id",
        string="Company",
        store=True,
    )

    @api.depends("embedding_ids")
    def _compute_has_embedding(self):
        for chunk in self:
            chunk.has_embedding = bool(chunk.embedding_ids)

    def get_embedding(self, model=None):
        """Get the embedding vector for this chunk.

        Args:
            model: Optional model name to filter by

        Returns:
            list: Embedding vector or None
        """
        self.ensure_one()
        domain = [("chunk_id", "=", self.id)]
        if model:
            domain.append(("model", "=", model))
        embedding = self.env["ipai.ai.embedding"].search(domain, limit=1)
        if embedding and embedding.vector:
            import json
            return json.loads(embedding.vector)
        return None
