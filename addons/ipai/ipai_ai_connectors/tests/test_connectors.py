# -*- coding: utf-8 -*-
"""
Tests for IPAI AI Connectors
============================

These tests verify the event intake webhook and event model.
"""
import os
from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAIConnectors(TransactionCase):
    """Test cases for AI Connectors module."""

    def test_event_creation(self):
        """Test that events are created correctly."""
        Event = self.env["ipai.ai.event"]

        event = Event.create(
            {
                "source": "n8n",
                "event_type": "workflow.completed",
                "ref": "test_123",
                "payload_json": {"status": "success"},
                "company_id": self.env.company.id,
            }
        )

        self.assertEqual(event.source, "n8n")
        self.assertEqual(event.event_type, "workflow.completed")
        self.assertEqual(event.ref, "test_123")
        self.assertEqual(event.state, "received")
        self.assertEqual(event.payload_json, {"status": "success"})

    def test_event_from_webhook(self):
        """Test event creation via webhook helper method."""
        Event = self.env["ipai.ai.event"]

        event = Event.create_from_webhook(
            source="github",
            event_type="issue.created",
            ref="issue_456",
            payload={"issue": {"title": "Test Issue"}},
            company_id=self.env.company.id,
        )

        self.assertEqual(event.source, "github")
        self.assertEqual(event.event_type, "issue.created")
        self.assertEqual(event.ref, "issue_456")

    def test_event_source_normalization(self):
        """Test that sources are normalized correctly."""
        Event = self.env["ipai.ai.event"]

        # Test n8n
        event = Event.create_from_webhook(
            source="N8N",  # uppercase
            event_type="test",
        )
        self.assertEqual(event.source, "n8n")

        # Test unknown source
        event = Event.create_from_webhook(
            source="unknown_source",
            event_type="test",
        )
        self.assertEqual(event.source, "custom")

    def test_event_state_transitions(self):
        """Test event state transition methods."""
        Event = self.env["ipai.ai.event"]

        event = Event.create(
            {
                "source": "n8n",
                "event_type": "test",
                "company_id": self.env.company.id,
            }
        )

        self.assertEqual(event.state, "received")

        # Mark as processed
        event.action_mark_processed()
        self.assertEqual(event.state, "processed")
        self.assertTrue(event.processed_date)

        # Retry (reset to received)
        event.action_retry()
        self.assertEqual(event.state, "received")

        # Mark as ignored
        event.action_mark_ignored()
        self.assertEqual(event.state, "ignored")

    def test_payload_text_computation(self):
        """Test that payload_text is computed correctly."""
        Event = self.env["ipai.ai.event"]

        event = Event.create(
            {
                "source": "n8n",
                "event_type": "test",
                "payload_json": {"key": "value", "nested": {"a": 1}},
                "company_id": self.env.company.id,
            }
        )

        self.assertIn("key", event.payload_text)
        self.assertIn("value", event.payload_text)
        self.assertIn("nested", event.payload_text)

    def test_event_name_get(self):
        """Test event display name."""
        Event = self.env["ipai.ai.event"]

        event = Event.create(
            {
                "source": "github",
                "event_type": "push",
                "ref": "main",
                "company_id": self.env.company.id,
            }
        )

        name = event.name_get()[0][1]
        self.assertIn("github", name)
        self.assertIn("push", name)
        self.assertIn("main", name)

    def test_controller_token_validation(self):
        """Test that controller validates token correctly."""
        from ..controllers.main import IPAIAIConnectorsController

        controller = IPAIAIConnectorsController()

        # Without token configured
        with patch.dict(os.environ, {"IPAI_CONNECTORS_TOKEN": ""}):
            with patch("odoo.http.request") as mock_request:
                mock_request.env = self.env
                mock_request.httprequest.remote_addr = "127.0.0.1"

                result = controller.event(
                    token="any_token", source="n8n", event_type="test"
                )

            self.assertFalse(result["ok"])
            self.assertIn("not configured", result["error"])

    def test_controller_with_valid_token(self):
        """Test that controller accepts valid token."""
        from ..controllers.main import IPAIAIConnectorsController

        controller = IPAIAIConnectorsController()

        with patch.dict(os.environ, {"IPAI_CONNECTORS_TOKEN": "test_secret"}):
            with patch("odoo.http.request") as mock_request:
                mock_request.env = self.env
                mock_request.httprequest.remote_addr = "127.0.0.1"

                result = controller.event(
                    token="test_secret",
                    source="n8n",
                    event_type="test",
                    payload={"data": "value"},
                )

            self.assertTrue(result["ok"])
            self.assertIn("event_id", result)

    def test_controller_health_check(self):
        """Test health check endpoint."""
        from ..controllers.main import IPAIAIConnectorsController

        controller = IPAIAIConnectorsController()
        result = controller.health()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["module"], "ipai_ai_connectors")
