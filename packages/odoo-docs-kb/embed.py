"""
Odoo 18 Documentation Embedder

Azure OpenAI embedding client per agents/knowledge/odoo18_docs/indexing.yaml.
Uses text-embedding-ada-002 (1536 dims) with batched requests.
"""

import logging
import os
import time
from dataclasses import dataclass

from openai import AzureOpenAI

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Embedding result for a single chunk."""

    chunk_id: str
    vector: list[float]
    model: str
    usage_tokens: int


class AzureEmbedder:
    """Batch embedder using Azure OpenAI."""

    def __init__(
        self,
        deployment: str | None = None,
        dimensions: int = 1536,
        batch_size: int = 100,
        max_retries: int = 3,
    ):
        self.client = AzureOpenAI(
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-06-01"),
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        )
        self.deployment = deployment or os.environ.get(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002"
        )
        self.dimensions = dimensions
        self.batch_size = batch_size
        self.max_retries = max_retries

    def embed_texts(
        self, texts: list[str], chunk_ids: list[str]
    ) -> list[EmbeddingResult]:
        """Embed a list of texts in batches.

        Args:
            texts: Text content to embed.
            chunk_ids: Corresponding chunk IDs (same order).

        Returns:
            List of EmbeddingResult with vectors.
        """
        if len(texts) != len(chunk_ids):
            raise ValueError("texts and chunk_ids must have same length")

        results = []
        total_tokens = 0

        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i : i + self.batch_size]
            batch_ids = chunk_ids[i : i + self.batch_size]

            response = self._embed_batch_with_retry(batch_texts)

            for j, embedding_data in enumerate(response.data):
                results.append(
                    EmbeddingResult(
                        chunk_id=batch_ids[j],
                        vector=embedding_data.embedding,
                        model=response.model,
                        usage_tokens=0,  # per-item not available
                    )
                )

            batch_tokens = response.usage.total_tokens
            total_tokens += batch_tokens
            logger.info(
                "Embedded batch %d-%d (%d tokens)",
                i,
                i + len(batch_texts),
                batch_tokens,
            )

        logger.info(
            "Embedded %d chunks, %d total tokens", len(results), total_tokens
        )
        return results

    def _embed_batch_with_retry(self, texts: list[str]):
        """Embed a single batch with exponential backoff retry."""
        for attempt in range(self.max_retries):
            try:
                return self.client.embeddings.create(
                    input=texts,
                    model=self.deployment,
                )
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                wait = 2 ** (attempt + 1)
                logger.warning(
                    "Embedding attempt %d failed: %s. Retrying in %ds...",
                    attempt + 1,
                    e,
                    wait,
                )
                time.sleep(wait)

    def embed_single(self, text: str, chunk_id: str) -> EmbeddingResult:
        """Embed a single text."""
        results = self.embed_texts([text], [chunk_id])
        return results[0]
