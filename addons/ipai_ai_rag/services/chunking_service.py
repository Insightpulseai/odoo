# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

import hashlib
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class IpaiAiChunkingService(models.AbstractModel):
    """Service for deterministic text chunking."""

    _name = "ipai.ai.chunking.service"
    _description = "IPAI AI Chunking Service"

    @api.model
    def get_chunk_size(self):
        """Get configured chunk size in tokens."""
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai.ai.chunk_size", "1000")
        )

    @api.model
    def get_chunk_overlap(self):
        """Get configured chunk overlap in tokens."""
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai.ai.chunk_overlap", "200")
        )

    @api.model
    def count_tokens(self, text):
        """Count tokens in text using tiktoken.

        Args:
            text: Text to count tokens for

        Returns:
            int: Number of tokens
        """
        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            # Fallback: approximate tokens as words * 1.3
            return int(len(text.split()) * 1.3)

    @api.model
    def compute_hash(self, content):
        """Compute SHA-256 hash of content.

        Args:
            content: Text content to hash

        Returns:
            str: Hex digest of hash
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @api.model
    def chunk_text(self, text, chunk_size=None, overlap=None):
        """Chunk text into smaller pieces with overlap.

        Uses a deterministic algorithm:
        1. Split text into sentences
        2. Accumulate sentences until chunk_size is reached
        3. Create chunk and backtrack by overlap tokens

        Args:
            text: Text to chunk
            chunk_size: Maximum tokens per chunk (default from config)
            overlap: Overlap tokens between chunks (default from config)

        Returns:
            list of dicts with 'content', 'hash', 'token_count'
        """
        chunk_size = chunk_size or self.get_chunk_size()
        overlap = overlap or self.get_chunk_overlap()

        if not text or not text.strip():
            return []

        # Split into sentences (simple heuristic)
        sentences = self._split_sentences(text)
        if not sentences:
            return []

        chunks = []
        current_tokens = []
        current_count = 0

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)

            # If single sentence exceeds chunk_size, split it further
            if sentence_tokens > chunk_size:
                # Flush current chunk if not empty
                if current_tokens:
                    chunk_content = " ".join(current_tokens)
                    chunks.append({
                        "content": chunk_content,
                        "hash": self.compute_hash(chunk_content),
                        "token_count": current_count,
                    })
                    current_tokens = []
                    current_count = 0

                # Split long sentence into smaller pieces
                sub_chunks = self._split_long_text(sentence, chunk_size)
                for sub_chunk in sub_chunks:
                    chunk_content = sub_chunk
                    chunks.append({
                        "content": chunk_content,
                        "hash": self.compute_hash(chunk_content),
                        "token_count": self.count_tokens(chunk_content),
                    })
                continue

            # Check if adding sentence exceeds chunk_size
            if current_count + sentence_tokens > chunk_size:
                # Create chunk
                chunk_content = " ".join(current_tokens)
                chunks.append({
                    "content": chunk_content,
                    "hash": self.compute_hash(chunk_content),
                    "token_count": current_count,
                })

                # Keep overlap tokens for next chunk
                overlap_tokens = []
                overlap_count = 0
                for token in reversed(current_tokens):
                    token_count = self.count_tokens(token)
                    if overlap_count + token_count <= overlap:
                        overlap_tokens.insert(0, token)
                        overlap_count += token_count
                    else:
                        break

                current_tokens = overlap_tokens
                current_count = overlap_count

            # Add sentence to current chunk
            current_tokens.append(sentence)
            current_count += sentence_tokens

        # Flush remaining tokens
        if current_tokens:
            chunk_content = " ".join(current_tokens)
            chunks.append({
                "content": chunk_content,
                "hash": self.compute_hash(chunk_content),
                "token_count": current_count,
            })

        _logger.info(f"Chunked text into {len(chunks)} chunks")
        return chunks

    @api.model
    def _split_sentences(self, text):
        """Split text into sentences.

        Args:
            text: Text to split

        Returns:
            list of sentence strings
        """
        import re

        # Simple sentence splitting on common delimiters
        # Preserve the delimiter at the end of each sentence
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in sentences if s.strip()]

    @api.model
    def _split_long_text(self, text, max_tokens):
        """Split long text into smaller pieces by words.

        Args:
            text: Long text to split
            max_tokens: Maximum tokens per piece

        Returns:
            list of text pieces
        """
        words = text.split()
        pieces = []
        current_words = []
        current_count = 0

        for word in words:
            word_tokens = self.count_tokens(word)
            if current_count + word_tokens > max_tokens:
                if current_words:
                    pieces.append(" ".join(current_words))
                current_words = [word]
                current_count = word_tokens
            else:
                current_words.append(word)
                current_count += word_tokens

        if current_words:
            pieces.append(" ".join(current_words))

        return pieces
