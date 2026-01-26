# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class IpaiAiEmbedding(models.Model):
    """Vector embedding for a chunk."""

    _name = "ipai.ai.embedding"
    _description = "IPAI AI Embedding"
    _order = "create_date desc"

    chunk_id = fields.Many2one(
        comodel_name="ipai.ai.chunk",
        string="Chunk",
        required=True,
        ondelete="cascade",
        index=True,
    )
    vector = fields.Text(
        string="Vector",
        help="Embedding vector stored as JSON array.",
    )
    model = fields.Char(
        string="Model",
        required=True,
        index=True,
        help="Embedding model used (e.g., text-embedding-3-small).",
    )
    dimensions = fields.Integer(
        string="Dimensions",
        help="Number of dimensions in the embedding vector.",
    )
    create_date = fields.Datetime(
        string="Created At",
        readonly=True,
    )

    _sql_constraints = [
        (
            "chunk_model_unique",
            "UNIQUE(chunk_id, model)",
            "Each chunk can only have one embedding per model.",
        ),
    ]
