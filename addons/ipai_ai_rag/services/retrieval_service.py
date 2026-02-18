# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

import json
import logging
import math

from odoo import api, models

_logger = logging.getLogger(__name__)


class IpaiAiRetrievalService(models.AbstractModel):
    """Service for retrieving relevant chunks via similarity search."""

    _name = "ipai.ai.retrieval.service"
    _description = "IPAI AI Retrieval Service"

    @api.model
    def get_top_k(self):
        """Get configured top-k retrieval count."""
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai.ai.retrieval_top_k", "5")
        )

    @api.model
    def retrieve_context(self, agent, query, top_k=None):
        """Retrieve relevant context for a query from agent's sources.

        Uses cosine similarity with stable tie-breaking (score DESC, chunk_id ASC).

        Args:
            agent: ipai.ai.agent record
            query: Query text
            top_k: Number of chunks to retrieve (default from config)

        Returns:
            list of dicts with 'id', 'content', 'score', 'source_id'
        """
        top_k = top_k or self.get_top_k()

        # Get all chunks from agent's sources
        sources = agent.source_ids.filtered(
            lambda s: s.active and s.ingest_status == "done"
        )
        if not sources:
            return []

        chunks = self.env["ipai.ai.chunk"].search([
            ("source_id", "in", sources.ids),
            ("has_embedding", "=", True),
        ])
        if not chunks:
            return []

        # Generate query embedding
        embedding_service = self.env["ipai.ai.embedding.service"]
        query_embedding = embedding_service.generate_embedding(query)
        if not query_embedding:
            _logger.warning("Failed to generate query embedding")
            return []

        # Calculate similarities
        results = []
        for chunk in chunks:
            chunk_embedding = chunk.get_embedding()
            if not chunk_embedding:
                continue

            similarity = self.cosine_similarity(query_embedding, chunk_embedding)
            results.append({
                "id": chunk.id,
                "content": chunk.content,
                "score": similarity,
                "source_id": chunk.source_id.id,
                "source_name": chunk.source_id.name,
            })

        # Sort by score DESC, then chunk_id ASC for stable tie-breaking
        results.sort(key=lambda x: (-x["score"], x["id"]))

        # Return top-k
        return results[:top_k]

    @api.model
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector (list of floats)
            vec2: Second vector (list of floats)

        Returns:
            float: Cosine similarity (-1 to 1)
        """
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    @api.model
    def format_context_for_prompt(self, context_chunks, max_tokens=2000):
        """Format retrieved context for inclusion in a prompt.

        Args:
            context_chunks: List of chunk dicts from retrieve_context
            max_tokens: Maximum tokens for context

        Returns:
            str: Formatted context string
        """
        if not context_chunks:
            return ""

        chunking_service = self.env["ipai.ai.chunking.service"]
        formatted_parts = []
        total_tokens = 0

        for i, chunk in enumerate(context_chunks):
            chunk_text = f"[{i+1}] {chunk['content']}"
            chunk_tokens = chunking_service.count_tokens(chunk_text)

            if total_tokens + chunk_tokens > max_tokens:
                break

            formatted_parts.append(chunk_text)
            total_tokens += chunk_tokens

        return "\n\n".join(formatted_parts)
