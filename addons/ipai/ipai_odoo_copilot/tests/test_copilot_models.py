# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

"""Odoo-native tests for copilot core models.

Covers:
  - ipai.copilot.conversation: CRUD, state transitions, correlation ID
  - ipai.copilot.message: creation, attachment ref linking, serialization
  - ipai.copilot.attachment.ref: SHA256, file size, extraction pipeline,
    MIME validation, ingestion state machine
"""

import base64
import hashlib

from odoo.tests import TransactionCase, tagged


class TestCopilotConversation(TransactionCase):
    """Tests for ipai.copilot.conversation model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Conversation = cls.env["ipai.copilot.conversation"]

    def test_create_generates_correlation_id(self):
        """New conversation gets a UUID correlation ID automatically."""
        conv = self.Conversation.create({"name": "Test Chat"})
        self.assertTrue(conv.gateway_correlation_id)
        self.assertEqual(len(conv.gateway_correlation_id), 36)  # UUID format

    def test_create_preserves_explicit_correlation_id(self):
        """Explicit correlation ID is not overwritten."""
        conv = self.Conversation.create({
            "name": "Test",
            "gateway_correlation_id": "custom-id-123",
        })
        self.assertEqual(conv.gateway_correlation_id, "custom-id-123")

    def test_default_state_is_active(self):
        conv = self.Conversation.create({"name": "Test"})
        self.assertEqual(conv.state, "active")

    def test_archive_unarchive(self):
        conv = self.Conversation.create({"name": "Test"})
        conv.action_archive()
        self.assertEqual(conv.state, "archived")
        conv.action_unarchive()
        self.assertEqual(conv.state, "active")

    def test_message_count_computed(self):
        conv = self.Conversation.create({"name": "Test"})
        self.assertEqual(conv.message_count, 0)
        self.env["ipai.copilot.message"].create({
            "conversation_id": conv.id,
            "role": "user",
            "content": "Hello",
        })
        conv.invalidate_recordset()
        self.assertEqual(conv.message_count, 1)


class TestCopilotMessage(TransactionCase):
    """Tests for ipai.copilot.message model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conv = cls.env["ipai.copilot.conversation"].create({
            "name": "Test Conversation",
        })

    def test_create_user_message(self):
        msg = self.env["ipai.copilot.message"].create({
            "conversation_id": self.conv.id,
            "role": "user",
            "content": "What is the VAT rate?",
        })
        self.assertEqual(msg.role, "user")
        self.assertEqual(msg.content, "What is the VAT rate?")

    def test_create_assistant_message(self):
        msg = self.env["ipai.copilot.message"].create({
            "conversation_id": self.conv.id,
            "role": "assistant",
            "content": "The VAT rate is 12%.",
        })
        self.assertEqual(msg.role, "assistant")

    def test_attachment_count_computed(self):
        msg = self.env["ipai.copilot.message"].create({
            "conversation_id": self.conv.id,
            "role": "user",
            "content": "See attached",
        })
        self.assertEqual(msg.attachment_count, 0)

    def test_serialize_attachment_context_empty(self):
        msg = self.env["ipai.copilot.message"].create({
            "conversation_id": self.conv.id,
            "role": "user",
            "content": "test",
        })
        result = msg.serialize_attachment_context()
        self.assertEqual(result, [])


class TestCopilotAttachmentRef(TransactionCase):
    """Tests for ipai.copilot.attachment.ref model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conv = cls.env["ipai.copilot.conversation"].create({
            "name": "Attachment Test",
        })
        # A simple text file for testing
        cls.text_content = b"Invoice #001\nNet: 100,000\nVAT: 12,000\nTotal: 112,000"
        cls.text_b64 = base64.b64encode(cls.text_content).decode()

    def _create_attachment(self, name="test.txt", content=None, mime="text/plain"):
        """Helper to create an ir.attachment + copilot ref."""
        b64 = content or self.text_b64
        att = self.env["ir.attachment"].create({
            "name": name,
            "datas": b64,
            "mimetype": mime,
            "type": "binary",
        })
        ref = self.env["ipai.copilot.attachment.ref"].create({
            "attachment_id": att.id,
            "conversation_id": self.conv.id,
            "filename": name,
            "mime_type": mime,
            "origin": "upload",
        })
        return ref

    def test_sha256_computed_on_create(self):
        """SHA256 is auto-computed from ir.attachment data on creation."""
        ref = self._create_attachment()
        expected_sha = hashlib.sha256(self.text_content).hexdigest()
        self.assertEqual(ref.content_sha256, expected_sha)

    def test_file_size_computed_on_create(self):
        """File size is auto-computed from ir.attachment data."""
        ref = self._create_attachment()
        self.assertEqual(ref.file_size, len(self.text_content))

    def test_default_ingestion_state_pending(self):
        ref = self._create_attachment()
        self.assertEqual(ref.ingestion_state, "pending")

    def test_text_extraction_direct(self):
        """Plain text files extract via 'direct' method."""
        ref = self._create_attachment()
        ref.run_extraction()
        self.assertEqual(ref.ingestion_state, "done")
        self.assertEqual(ref.extraction_method, "direct")
        self.assertIn("Invoice #001", ref.extracted_text)
        self.assertGreater(ref.token_estimate, 0)

    def test_json_extraction_direct(self):
        """JSON files extract via 'direct' method."""
        content = base64.b64encode(b'{"amount": 100}').decode()
        ref = self._create_attachment(
            name="data.json", content=content, mime="application/json",
        )
        ref.run_extraction()
        self.assertEqual(ref.ingestion_state, "done")
        self.assertEqual(ref.extraction_method, "direct")
        self.assertIn("amount", ref.extracted_text)

    def test_csv_extraction_direct(self):
        """CSV files extract via 'direct' method."""
        content = base64.b64encode(b"name,amount\nService,100000").decode()
        ref = self._create_attachment(
            name="data.csv", content=content, mime="text/csv",
        )
        ref.run_extraction()
        self.assertEqual(ref.ingestion_state, "done")
        self.assertIn("Service", ref.extracted_text)

    def test_skip_already_extracted(self):
        """run_extraction skips refs not in pending/error state."""
        ref = self._create_attachment()
        ref.run_extraction()
        self.assertEqual(ref.ingestion_state, "done")
        # Run again — should not change anything
        old_text = ref.extracted_text
        ref.run_extraction()
        self.assertEqual(ref.extracted_text, old_text)

    def test_empty_file_skipped(self):
        """Empty file produces 'skip' state."""
        content = base64.b64encode(b"").decode()
        att = self.env["ir.attachment"].create({
            "name": "empty.txt",
            "datas": content,
            "mimetype": "text/plain",
            "type": "binary",
        })
        ref = self.env["ipai.copilot.attachment.ref"].create({
            "attachment_id": att.id,
            "conversation_id": self.conv.id,
            "filename": "empty.txt",
            "mime_type": "text/plain",
            "origin": "upload",
        })
        ref.run_extraction()
        self.assertEqual(ref.ingestion_state, "skip")

    def test_serialize_in_message_context(self):
        """Extracted ref appears in message attachment serialization."""
        msg = self.env["ipai.copilot.message"].create({
            "conversation_id": self.conv.id,
            "role": "user",
            "content": "See attached",
        })
        ref = self._create_attachment()
        ref.run_extraction()
        ref.message_id = msg.id

        ctx = msg.serialize_attachment_context()
        self.assertEqual(len(ctx), 1)
        self.assertEqual(ctx[0]["filename"], "test.txt")
        self.assertEqual(ctx[0]["mime_type"], "text/plain")
        self.assertIn("Invoice #001", ctx[0]["snippet"])

    def test_token_estimate(self):
        """Token estimate is roughly len(text) / 4."""
        ref = self._create_attachment()
        ref.run_extraction()
        expected = len(ref.extracted_text) // 4
        self.assertEqual(ref.token_estimate, expected)
