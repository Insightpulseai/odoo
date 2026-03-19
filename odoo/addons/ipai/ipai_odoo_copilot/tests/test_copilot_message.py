# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCopilotMessage(TransactionCase):
    """Tests for ipai.copilot.message model."""

    def setUp(self):
        super().setUp()
        self.Conversation = self.env['ipai.copilot.conversation']
        self.Message = self.env['ipai.copilot.message']
        self.conversation = self.Conversation.create({'name': 'Test Conv'})

    def test_create_user_message(self):
        """User messages are created with correct role."""
        msg = self.Message.create({
            'conversation_id': self.conversation.id,
            'role': 'user',
            'content': 'Hello copilot',
        })
        self.assertEqual(msg.role, 'user')
        self.assertEqual(msg.content, 'Hello copilot')
        self.assertEqual(msg.conversation_id, self.conversation)

    def test_create_assistant_message(self):
        """Assistant messages store latency and request_id."""
        msg = self.Message.create({
            'conversation_id': self.conversation.id,
            'role': 'assistant',
            'content': 'Hello! How can I help?',
            'latency_ms': 245,
            'request_id': 'req-abc-123',
        })
        self.assertEqual(msg.role, 'assistant')
        self.assertEqual(msg.latency_ms, 245)
        self.assertEqual(msg.request_id, 'req-abc-123')

    def test_tool_calls_json(self):
        """Tool calls are stored as JSON."""
        tool_data = [{'name': 'search', 'args': {'query': 'invoices'}}]
        msg = self.Message.create({
            'conversation_id': self.conversation.id,
            'role': 'assistant',
            'content': 'Searching...',
            'tool_calls': tool_data,
        })
        self.assertEqual(msg.tool_calls, tool_data)

    def test_empty_content_raises(self):
        """Empty or whitespace-only content raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.Message.create({
                'conversation_id': self.conversation.id,
                'role': 'user',
                'content': '   ',
            })

    def test_all_roles(self):
        """All four role values are accepted."""
        for role in ('user', 'assistant', 'system', 'tool'):
            msg = self.Message.create({
                'conversation_id': self.conversation.id,
                'role': role,
                'content': 'Test message for role %s' % role,
            })
            self.assertEqual(msg.role, role)

    def test_cascade_delete(self):
        """Deleting conversation cascades to messages."""
        self.Message.create({
            'conversation_id': self.conversation.id,
            'role': 'user',
            'content': 'Test',
        })
        msg_count_before = self.Message.search_count([
            ('conversation_id', '=', self.conversation.id),
        ])
        self.assertEqual(msg_count_before, 1)

        self.conversation.unlink()
        msg_count_after = self.Message.search_count([
            ('conversation_id', '=', self.conversation.id),
        ])
        self.assertEqual(msg_count_after, 0)
