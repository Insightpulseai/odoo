# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

import os

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """Configuration settings for IPAI AI Agent Builder."""

    _inherit = "res.config.settings"

    ipai_ai_openai_api_key = fields.Char(
        string="OpenAI API Key",
        config_parameter="ipai.ai.openai_api_key",
        help="API key for OpenAI (ChatGPT). Can also be set via OPENAI_API_KEY env var.",
    )
    ipai_ai_google_api_key = fields.Char(
        string="Google API Key",
        config_parameter="ipai.ai.google_api_key",
        help="API key for Google (Gemini). Can also be set via GOOGLE_API_KEY env var.",
    )
    ipai_ai_default_provider = fields.Selection(
        selection=[
            ("openai", "OpenAI (ChatGPT)"),
            ("google", "Google (Gemini)"),
        ],
        string="Default Provider",
        config_parameter="ipai.ai.default_provider",
        default="openai",
    )
    ipai_ai_embedding_model = fields.Char(
        string="Embedding Model",
        config_parameter="ipai.ai.embedding_model",
        default="text-embedding-3-small",
        help="Model used for generating embeddings.",
    )
    ipai_ai_chunk_size = fields.Integer(
        string="Chunk Size",
        config_parameter="ipai.ai.chunk_size",
        default=1000,
        help="Default chunk size for RAG in tokens.",
    )
    ipai_ai_chunk_overlap = fields.Integer(
        string="Chunk Overlap",
        config_parameter="ipai.ai.chunk_overlap",
        default=200,
        help="Overlap between chunks in tokens.",
    )
    ipai_ai_retrieval_top_k = fields.Integer(
        string="Retrieval Top K",
        config_parameter="ipai.ai.retrieval_top_k",
        default=5,
        help="Number of chunks to retrieve for context.",
    )

    @api.model
    def get_openai_api_key(self):
        """Get OpenAI API key from config or environment."""
        key = self.env["ir.config_parameter"].sudo().get_param("ipai.ai.openai_api_key")
        return key or os.environ.get("OPENAI_API_KEY", "")

    @api.model
    def get_google_api_key(self):
        """Get Google API key from config or environment."""
        key = self.env["ir.config_parameter"].sudo().get_param("ipai.ai.google_api_key")
        return key or os.environ.get("GOOGLE_API_KEY", "")
