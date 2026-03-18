# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestRetrieval(TransactionCase):
    """Test cases for retrieval service."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RetrievalService = cls.env["ipai.ai.retrieval.service"]

    def test_cosine_similarity_identical(self):
        """Test cosine similarity of identical vectors is 1."""
        vec = [1.0, 2.0, 3.0]
        similarity = self.RetrievalService.cosine_similarity(vec, vec)
        self.assertAlmostEqual(similarity, 1.0, places=5)

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity of orthogonal vectors is 0."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        similarity = self.RetrievalService.cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 0.0, places=5)

    def test_cosine_similarity_opposite(self):
        """Test cosine similarity of opposite vectors is -1."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [-1.0, -2.0, -3.0]
        similarity = self.RetrievalService.cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, -1.0, places=5)

    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector is 0."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [0.0, 0.0, 0.0]
        similarity = self.RetrievalService.cosine_similarity(vec1, vec2)
        self.assertEqual(similarity, 0.0)

    def test_cosine_similarity_different_lengths(self):
        """Test cosine similarity with different length vectors."""
        vec1 = [1.0, 2.0]
        vec2 = [1.0, 2.0, 3.0]
        similarity = self.RetrievalService.cosine_similarity(vec1, vec2)
        self.assertEqual(similarity, 0.0)

    def test_stable_tie_breaking(self):
        """Test that tie-breaking is stable (sort by score desc, id asc)."""
        # Create mock results with same scores
        results = [
            {"id": 3, "content": "C", "score": 0.9, "source_id": 1},
            {"id": 1, "content": "A", "score": 0.9, "source_id": 1},
            {"id": 2, "content": "B", "score": 0.9, "source_id": 1},
        ]

        # Apply the same sort as retrieval service
        results.sort(key=lambda x: (-x["score"], x["id"]))

        # Should be sorted by id ascending when scores are equal
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[1]["id"], 2)
        self.assertEqual(results[2]["id"], 3)

    def test_stable_tie_breaking_mixed_scores(self):
        """Test tie-breaking with mixed scores."""
        results = [
            {"id": 3, "content": "C", "score": 0.8, "source_id": 1},
            {"id": 1, "content": "A", "score": 0.9, "source_id": 1},
            {"id": 4, "content": "D", "score": 0.9, "source_id": 1},
            {"id": 2, "content": "B", "score": 0.7, "source_id": 1},
        ]

        results.sort(key=lambda x: (-x["score"], x["id"]))

        # Score 0.9 items first (id 1, then 4)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[0]["score"], 0.9)
        self.assertEqual(results[1]["id"], 4)
        self.assertEqual(results[1]["score"], 0.9)
        # Then score 0.8
        self.assertEqual(results[2]["id"], 3)
        self.assertEqual(results[2]["score"], 0.8)
        # Then score 0.7
        self.assertEqual(results[3]["id"], 2)
        self.assertEqual(results[3]["score"], 0.7)

    def test_format_context_empty(self):
        """Test formatting empty context."""
        formatted = self.RetrievalService.format_context_for_prompt([])
        self.assertEqual(formatted, "")

    def test_format_context_single_chunk(self):
        """Test formatting single chunk."""
        chunks = [{"id": 1, "content": "Test content", "score": 0.9, "source_id": 1}]
        formatted = self.RetrievalService.format_context_for_prompt(chunks)
        self.assertIn("[1]", formatted)
        self.assertIn("Test content", formatted)

    def test_format_context_multiple_chunks(self):
        """Test formatting multiple chunks."""
        chunks = [
            {"id": 1, "content": "First chunk", "score": 0.9, "source_id": 1},
            {"id": 2, "content": "Second chunk", "score": 0.8, "source_id": 1},
        ]
        formatted = self.RetrievalService.format_context_for_prompt(chunks)
        self.assertIn("[1]", formatted)
        self.assertIn("[2]", formatted)
        self.assertIn("First chunk", formatted)
        self.assertIn("Second chunk", formatted)
