# -*- coding: utf-8 -*-
"""
Tests for IPAI AI Agents UI Controller
======================================

These tests verify the JSON-RPC endpoints for the Ask AI panel.
"""
import json
from unittest.mock import patch, MagicMock

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAIAgentsController(TransactionCase):
    """Test cases for AI Agents controller endpoints."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test provider
        cls.provider = cls.env["ipai.ai.provider"].create(
            {
                "name": "Test Provider",
                "provider_type": "kapa",
                "is_default": True,
                "company_id": cls.env.company.id,
            }
        )

    def test_bootstrap_returns_providers(self):
        """Test that bootstrap returns available providers."""
        # Import controller class
        from ..controllers.main import IPAIAIAgentsController

        controller = IPAIAIAgentsController()

        # Mock request
        with patch("odoo.http.request") as mock_request:
            mock_request.env = self.env
            result = controller.bootstrap()

        self.assertIn("agents", result)
        self.assertIn("user", result)
        self.assertIn("company", result)
        self.assertTrue(len(result["agents"]) >= 1)

        # Check provider is in list
        agent_ids = [a["id"] for a in result["agents"]]
        self.assertIn(self.provider.id, agent_ids)

    def test_thread_creation(self):
        """Test that asking creates a new thread."""
        Thread = self.env["ipai.ai.thread"]

        # Count threads before
        count_before = Thread.search_count([("user_id", "=", self.env.user.id)])

        # Create thread
        thread = Thread.create(
            {
                "provider_id": self.provider.id,
                "user_id": self.env.user.id,
            }
        )

        # Verify thread created
        count_after = Thread.search_count([("user_id", "=", self.env.user.id)])
        self.assertEqual(count_after, count_before + 1)
        self.assertEqual(thread.provider_id, self.provider)

    def test_message_creation(self):
        """Test that messages are created correctly."""
        Thread = self.env["ipai.ai.thread"]
        Message = self.env["ipai.ai.message"]

        # Create thread
        thread = Thread.create(
            {
                "provider_id": self.provider.id,
                "user_id": self.env.user.id,
            }
        )

        # Create user message
        user_msg = Message.create(
            {
                "thread_id": thread.id,
                "role": "user",
                "content": "Test question",
            }
        )

        self.assertEqual(user_msg.role, "user")
        self.assertEqual(user_msg.content, "Test question")
        self.assertEqual(len(thread.message_ids), 1)

        # Create assistant message
        assistant_msg = Message.create(
            {
                "thread_id": thread.id,
                "role": "assistant",
                "content": "Test answer",
                "confidence": 0.85,
            }
        )

        self.assertEqual(assistant_msg.role, "assistant")
        self.assertEqual(assistant_msg.confidence, 0.85)
        self.assertEqual(len(thread.message_ids), 2)

    def test_citation_creation(self):
        """Test that citations are created correctly."""
        Thread = self.env["ipai.ai.thread"]
        Message = self.env["ipai.ai.message"]
        Citation = self.env["ipai.ai.citation"]

        # Create thread and message
        thread = Thread.create(
            {
                "provider_id": self.provider.id,
                "user_id": self.env.user.id,
            }
        )
        message = Message.create(
            {
                "thread_id": thread.id,
                "role": "assistant",
                "content": "Answer with citation [1]",
            }
        )

        # Create citation
        citation = Citation.create(
            {
                "message_id": message.id,
                "rank": 1,
                "title": "Source Document",
                "url": "https://example.com/doc",
                "snippet": "Relevant text...",
                "score": 0.95,
            }
        )

        self.assertEqual(citation.message_id, message)
        self.assertEqual(citation.rank, 1)
        self.assertEqual(message.citation_count, 1)

    def test_provider_stats_update(self):
        """Test that provider stats are updated correctly."""
        initial_requests = self.provider.total_requests

        # Update stats
        self.provider.update_stats(latency_ms=150, tokens=100)

        self.assertEqual(self.provider.total_requests, initial_requests + 1)
        self.assertEqual(self.provider.total_tokens, 100)
        self.assertEqual(self.provider.avg_latency_ms, 150.0)

        # Update again
        self.provider.update_stats(latency_ms=250, tokens=200)

        self.assertEqual(self.provider.total_requests, initial_requests + 2)
        self.assertEqual(self.provider.total_tokens, 300)
        # Average should be (150 + 250) / 2 = 200
        self.assertAlmostEqual(self.provider.avg_latency_ms, 200.0, places=1)

    def test_thread_name_computation(self):
        """Test that thread name is computed from first message."""
        Thread = self.env["ipai.ai.thread"]
        Message = self.env["ipai.ai.message"]

        # Create thread (name should be default)
        thread = Thread.create(
            {
                "provider_id": self.provider.id,
                "user_id": self.env.user.id,
            }
        )

        # Add user message
        Message.create(
            {
                "thread_id": thread.id,
                "role": "user",
                "content": "How do I create a new project in Odoo?",
            }
        )

        # Refresh and check name
        thread.invalidate_recordset()
        self.assertIn("create a new project", thread.name)

    def test_provider_default_constraint(self):
        """Test that only one provider can be default per company."""
        Provider = self.env["ipai.ai.provider"]

        # Create second provider as default
        provider2 = Provider.create(
            {
                "name": "Test Provider 2",
                "provider_type": "openai",
                "is_default": True,
                "company_id": self.env.company.id,
            }
        )

        # Refresh first provider
        self.provider.invalidate_recordset()

        # First provider should no longer be default
        self.assertFalse(self.provider.is_default)
        self.assertTrue(provider2.is_default)
