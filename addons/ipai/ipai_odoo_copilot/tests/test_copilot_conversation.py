# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestCopilotConversation(TransactionCase):
    """Tests for ipai.copilot.conversation model."""

    def setUp(self):
        super().setUp()
        self.Conversation = self.env['ipai.copilot.conversation']

    def test_create_assigns_correlation_id(self):
        """Creating a conversation auto-generates a gateway_correlation_id."""
        conv = self.Conversation.create({'name': 'Test Conv'})
        self.assertTrue(conv.gateway_correlation_id)
        self.assertEqual(len(conv.gateway_correlation_id), 36)  # UUID format

    def test_create_preserves_explicit_correlation_id(self):
        """Explicit correlation ID is not overwritten."""
        conv = self.Conversation.create({
            'name': 'Test Conv',
            'gateway_correlation_id': 'custom-id-123',
        })
        self.assertEqual(conv.gateway_correlation_id, 'custom-id-123')

    def test_default_state_is_active(self):
        """Default state should be 'active'."""
        conv = self.Conversation.create({'name': 'Test'})
        self.assertEqual(conv.state, 'active')

    def test_default_user_is_current(self):
        """Default user_id is the current user."""
        conv = self.Conversation.create({'name': 'Test'})
        self.assertEqual(conv.user_id, self.env.user)

    def test_action_archive(self):
        """action_archive sets state to 'archived'."""
        conv = self.Conversation.create({'name': 'Test'})
        conv.action_archive()
        self.assertEqual(conv.state, 'archived')

    def test_action_unarchive(self):
        """action_unarchive sets state back to 'active'."""
        conv = self.Conversation.create({'name': 'Test', 'state': 'archived'})
        conv.action_unarchive()
        self.assertEqual(conv.state, 'active')

    def test_message_count(self):
        """message_count computes correctly."""
        conv = self.Conversation.create({'name': 'Test'})
        self.assertEqual(conv.message_count, 0)

        self.env['ipai.copilot.message'].create({
            'conversation_id': conv.id,
            'role': 'user',
            'content': 'Hello',
        })
        conv.invalidate_recordset()
        self.assertEqual(conv.message_count, 1)

    def test_context_fields(self):
        """Context model and res_id are stored correctly."""
        conv = self.Conversation.create({
            'name': 'Test',
            'context_model': 'sale.order',
            'context_res_id': 42,
        })
        self.assertEqual(conv.context_model, 'sale.order')
        self.assertEqual(conv.context_res_id, 42)
