# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

import json
import logging
import os

from odoo import api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Batch size for embedding API calls
EMBEDDING_BATCH_SIZE = 100


class IpaiAiEmbeddingService(models.AbstractModel):
    """Service for generating and managing embeddings."""

    _name = "ipai.ai.embedding.service"
    _description = "IPAI AI Embedding Service"

    @api.model
    def get_embedding_model(self):
        """Get configured embedding model."""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai.ai.embedding_model", "text-embedding-3-small")
        )

    @api.model
    def get_api_key(self):
        """Get OpenAI API key for embeddings."""
        key = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai.ai.openai_api_key")
        )
        return key or os.environ.get("OPENAI_API_KEY", "")

    @api.model
    def generate_embedding(self, text, model=None):
        """Generate embedding for a single text.

        Args:
            text: Text to embed
            model: Optional model name (default from config)

        Returns:
            list: Embedding vector
        """
        embeddings = self.generate_embeddings([text], model=model)
        return embeddings[0] if embeddings else None

    @api.model
    def generate_embeddings(self, texts, model=None):
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            model: Optional model name (default from config)

        Returns:
            list of embedding vectors
        """
        if not texts:
            return []

        api_key = self.get_api_key()
        if not api_key:
            raise UserError("OpenAI API key not configured for embeddings.")

        model = model or self.get_embedding_model()

        try:
            import openai
        except ImportError:
            raise UserError("OpenAI Python package not installed.")

        client = openai.OpenAI(api_key=api_key)

        all_embeddings = []
        for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
            batch = texts[i:i + EMBEDDING_BATCH_SIZE]
            try:
                response = client.embeddings.create(
                    model=model,
                    input=batch,
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            except openai.APIError as e:
                _logger.error(f"OpenAI API error generating embeddings: {e}")
                raise UserError(f"Failed to generate embeddings: {e}")

        return all_embeddings

    @api.model
    def generate_embeddings_for_source(self, source):
        """Generate embeddings for all chunks in a source.

        Args:
            source: ipai.ai.source record
        """
        model = self.get_embedding_model()
        chunks = source.chunk_ids.filtered(lambda c: not c.has_embedding)

        if not chunks:
            _logger.info(f"No chunks need embeddings for source {source.id}")
            return

        # Collect texts
        texts = [chunk.content for chunk in chunks]

        # Generate embeddings
        embeddings = self.generate_embeddings(texts, model=model)

        # Store embeddings
        Embedding = self.env["ipai.ai.embedding"]
        for chunk, vector in zip(chunks, embeddings):
            Embedding.create({
                "chunk_id": chunk.id,
                "vector": json.dumps(vector),
                "model": model,
                "dimensions": len(vector),
            })

        _logger.info(f"Generated {len(embeddings)} embeddings for source {source.id}")

    @api.model
    def get_embedding_cache_key(self, content_hash, model):
        """Generate cache key for an embedding.

        Args:
            content_hash: SHA-256 hash of content
            model: Embedding model name

        Returns:
            str: Cache key
        """
        return f"{model}:{content_hash}"
