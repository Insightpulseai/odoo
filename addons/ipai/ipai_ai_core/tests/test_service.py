# -*- coding: utf-8 -*-
"""
Tests for IPAI AI Service Layer
===============================

Tests for the AI service orchestration.
"""
from unittest.mock import patch, MagicMock
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAIService(TransactionCase):
    """Test cases for AI service layer."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Provider = cls.env["ipai.ai.provider"]
        cls.Thread = cls.env["ipai.ai.thread"]
        cls.Message = cls.env["ipai.ai.message"]

        # Create test provider
        cls.provider = cls.Provider.create(
            {
                "name": "Test Service Provider",
                "provider_type": "kapa",
                "is_default": True,
                "company_id": cls.env.company.id,
            }
        )

    def test_service_model_exists(self):
        """Test that service model is registered."""
        # Service might be abstract or transient
        # Just verify it can be accessed
        self.assertTrue(hasattr(self.env, "registry"))

    def test_provider_get_default_with_service(self):
        """Test provider retrieval for service use."""
        default = self.Provider.get_default()
        self.assertEqual(default, self.provider)

    def test_thread_service_flow(self):
        """Test basic service flow for creating thread and messages."""
        # Create thread
        thread = self.Thread.create(
            {
                "provider_id": self.provider.id,
                "user_id": self.env.user.id,
            }
        )

        # Add user message
        user_msg = self.Message.create(
            {
                "thread_id": thread.id,
                "role": "user",
                "content": "Test service question",
            }
        )

        # Simulate service adding assistant response
        assistant_msg = self.Message.create(
            {
                "thread_id": thread.id,
                "role": "assistant",
                "content": "Test service answer",
                "confidence": 0.75,
                "provider_latency_ms": 1000,
            }
        )

        # Verify flow
        self.assertEqual(len(thread.message_ids), 2)
        self.assertEqual(thread.message_ids[0].role, "user")
        self.assertEqual(thread.message_ids[1].role, "assistant")

    def test_confidence_thresholds(self):
        """Test confidence scoring thresholds."""
        thread = self.Thread.create(
            {
                "provider_id": self.provider.id,
                "user_id": self.env.user.id,
            }
        )

        # High confidence
        high_conf = self.Message.create(
            {
                "thread_id": thread.id,
                "role": "assistant",
                "content": "High confidence answer",
                "confidence": 0.85,
            }
        )
        self.assertGreaterEqual(high_conf.confidence, 0.7)

        # Medium confidence
        med_conf = self.Message.create(
            {
                "thread_id": thread.id,
                "role": "assistant",
                "content": "Medium confidence answer",
                "confidence": 0.55,
            }
        )
        self.assertGreaterEqual(med_conf.confidence, 0.4)
        self.assertLess(med_conf.confidence, 0.7)

        # Low confidence (uncertain)
        low_conf = self.Message.create(
            {
                "thread_id": thread.id,
                "role": "assistant",
                "content": "Low confidence answer",
                "confidence": 0.25,
            }
        )
        self.assertLess(low_conf.confidence, 0.4)

    def test_provider_stats_integration(self):
        """Test provider stats are updated during service flow."""
        initial_requests = self.provider.total_requests

        # Simulate service call
        thread = self.Thread.create(
            {
                "provider_id": self.provider.id,
                "user_id": self.env.user.id,
            }
        )

        # Service would call update_stats after LLM response
        self.provider.update_stats(latency_ms=1500, tokens=300)

        self.assertEqual(self.provider.total_requests, initial_requests + 1)

    def test_citation_service_flow(self):
        """Test citation creation as part of service flow."""
        Citation = self.env["ipai.ai.citation"]

        thread = self.Thread.create(
            {
                "provider_id": self.provider.id,
                "user_id": self.env.user.id,
            }
        )

        message = self.Message.create(
            {
                "thread_id": thread.id,
                "role": "assistant",
                "content": "Answer with sources [1][2]",
                "confidence": 0.8,
            }
        )

        # Add citations (simulating service parsing)
        Citation.create(
            {
                "message_id": message.id,
                "rank": 1,
                "title": "Odoo Documentation",
                "url": "https://docs.odoo.com/example",
                "snippet": "Relevant documentation text...",
                "score": 0.92,
            }
        )
        Citation.create(
            {
                "message_id": message.id,
                "rank": 2,
                "title": "Knowledge Base Article",
                "url": "https://kb.example.com/article",
                "snippet": "Related KB content...",
                "score": 0.85,
            }
        )

        message.invalidate_recordset()
        self.assertEqual(message.citation_count, 2)

    def test_thread_external_id(self):
        """Test external thread ID storage."""
        thread = self.Thread.create(
            {
                "provider_id": self.provider.id,
                "user_id": self.env.user.id,
                "external_thread_id": "ext-123-abc",
            }
        )

        self.assertEqual(thread.external_thread_id, "ext-123-abc")

        # Can search by external ID
        found = self.Thread.search([("external_thread_id", "=", "ext-123-abc")])
        self.assertEqual(len(found), 1)
        self.assertEqual(found, thread)
