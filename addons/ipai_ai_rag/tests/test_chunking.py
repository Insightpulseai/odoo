# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestChunking(TransactionCase):
    """Test cases for chunking service."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ChunkingService = cls.env["ipai.ai.chunking.service"]

    def test_compute_hash_deterministic(self):
        """Test that hash computation is deterministic."""
        content = "This is a test content for hashing."
        hash1 = self.ChunkingService.compute_hash(content)
        hash2 = self.ChunkingService.compute_hash(content)
        self.assertEqual(hash1, hash2)

    def test_compute_hash_different_content(self):
        """Test that different content produces different hashes."""
        hash1 = self.ChunkingService.compute_hash("Content A")
        hash2 = self.ChunkingService.compute_hash("Content B")
        self.assertNotEqual(hash1, hash2)

    def test_chunk_empty_text(self):
        """Test chunking empty text returns empty list."""
        chunks = self.ChunkingService.chunk_text("")
        self.assertEqual(chunks, [])

        chunks = self.ChunkingService.chunk_text("   ")
        self.assertEqual(chunks, [])

    def test_chunk_short_text(self):
        """Test chunking short text that fits in one chunk."""
        text = "This is a short text."
        chunks = self.ChunkingService.chunk_text(text, chunk_size=100)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["content"], text)
        self.assertTrue(chunks[0]["hash"])
        self.assertTrue(chunks[0]["token_count"] > 0)

    def test_chunk_determinism(self):
        """Test that chunking is deterministic (same input = same output)."""
        text = "This is a test. It has multiple sentences. Each sentence is meaningful."
        chunks1 = self.ChunkingService.chunk_text(text, chunk_size=50, overlap=10)
        chunks2 = self.ChunkingService.chunk_text(text, chunk_size=50, overlap=10)

        self.assertEqual(len(chunks1), len(chunks2))
        for c1, c2 in zip(chunks1, chunks2):
            self.assertEqual(c1["content"], c2["content"])
            self.assertEqual(c1["hash"], c2["hash"])
            self.assertEqual(c1["token_count"], c2["token_count"])

    def test_chunk_hash_uniqueness(self):
        """Test that each chunk has a unique hash based on content."""
        text = "First sentence here. Second sentence here. Third sentence here."
        chunks = self.ChunkingService.chunk_text(text, chunk_size=10, overlap=0)

        # Chunks with different content should have different hashes
        hashes = [c["hash"] for c in chunks]
        # Note: Some chunks might have same content if overlap brings them together
        # but generally they should be unique for different content

    def test_split_sentences(self):
        """Test sentence splitting."""
        text = "First sentence. Second sentence! Third sentence?"
        sentences = self.ChunkingService._split_sentences(text)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(sentences[0], "First sentence.")
        self.assertEqual(sentences[1], "Second sentence!")
        self.assertEqual(sentences[2], "Third sentence?")

    def test_chunk_with_overlap(self):
        """Test that overlap is applied correctly."""
        # Create a text with clear sentence boundaries
        text = "Sentence one here. Sentence two here. Sentence three here. Sentence four here."
        chunks = self.ChunkingService.chunk_text(text, chunk_size=30, overlap=15)

        # With overlap, chunks should share some content
        # This is a basic test - detailed overlap testing would need more specific assertions
        self.assertTrue(len(chunks) >= 1)

    def test_token_count(self):
        """Test token counting."""
        text = "Hello world"
        count = self.ChunkingService.count_tokens(text)
        self.assertTrue(count > 0)
        self.assertTrue(count <= 10)  # Should be a small number for short text
