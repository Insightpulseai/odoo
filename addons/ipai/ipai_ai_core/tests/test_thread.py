# -*- coding: utf-8 -*-
"""
Tests for IPAI AI Thread and Message Models
==========================================

Tests for conversation threads, messages, and citations.
"""
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAIThread(TransactionCase):
    """Test cases for ipai.ai.thread model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Thread = cls.env['ipai.ai.thread']
        cls.Message = cls.env['ipai.ai.message']
        cls.Citation = cls.env['ipai.ai.citation']
        cls.Provider = cls.env['ipai.ai.provider']

        # Create test provider
        cls.provider = cls.Provider.create({
            'name': 'Test Provider',
            'provider_type': 'kapa',
            'company_id': cls.env.company.id,
        })

    def test_thread_create(self):
        """Test basic thread creation."""
        thread = self.Thread.create({
            'provider_id': self.provider.id,
            'user_id': self.env.user.id,
        })

        self.assertTrue(thread.id)
        self.assertEqual(thread.provider_id, self.provider)
        self.assertEqual(thread.user_id, self.env.user)
        self.assertEqual(thread.state, 'active')

    def test_thread_company_from_provider(self):
        """Test thread company is related from provider."""
        thread = self.Thread.create({
            'provider_id': self.provider.id,
            'user_id': self.env.user.id,
        })

        self.assertEqual(thread.company_id, self.provider.company_id)

    def test_thread_name_default(self):
        """Test thread default name before messages."""
        thread = self.Thread.create({
            'provider_id': self.provider.id,
            'user_id': self.env.user.id,
        })

        # Default name should include thread ID
        self.assertIn('Thread', thread.name)

    def test_thread_name_from_first_message(self):
        """Test thread name computed from first user message."""
        thread = self.Thread.create({
            'provider_id': self.provider.id,
            'user_id': self.env.user.id,
        })

        # Add user message
        self.Message.create({
            'thread_id': thread.id,
            'role': 'user',
            'content': 'How do I configure the accounting module?',
        })

        # Refresh and check name
        thread.invalidate_recordset()
        self.assertIn('configure the accounting', thread.name)

    def test_thread_message_count(self):
        """Test message count computation."""
        thread = self.Thread.create({
            'provider_id': self.provider.id,
            'user_id': self.env.user.id,
        })

        self.assertEqual(thread.message_count, 0)

        # Add messages
        self.Message.create({
            'thread_id': thread.id,
            'role': 'user',
            'content': 'Question',
        })
        thread.invalidate_recordset()
        self.assertEqual(thread.message_count, 1)

        self.Message.create({
            'thread_id': thread.id,
            'role': 'assistant',
            'content': 'Answer',
        })
        thread.invalidate_recordset()
        self.assertEqual(thread.message_count, 2)

    def test_thread_state_transition(self):
        """Test thread state can be changed."""
        thread = self.Thread.create({
            'provider_id': self.provider.id,
            'user_id': self.env.user.id,
        })

        self.assertEqual(thread.state, 'active')

        thread.write({'state': 'closed'})
        self.assertEqual(thread.state, 'closed')


@tagged('post_install', '-at_install')
class TestAIMessage(TransactionCase):
    """Test cases for ipai.ai.message model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Thread = cls.env['ipai.ai.thread']
        cls.Message = cls.env['ipai.ai.message']
        cls.Citation = cls.env['ipai.ai.citation']
        cls.Provider = cls.env['ipai.ai.provider']

        # Create test provider and thread
        cls.provider = cls.Provider.create({
            'name': 'Test Provider',
            'provider_type': 'kapa',
            'company_id': cls.env.company.id,
        })
        cls.thread = cls.Thread.create({
            'provider_id': cls.provider.id,
            'user_id': cls.env.user.id,
        })

    def test_message_create_user(self):
        """Test user message creation."""
        message = self.Message.create({
            'thread_id': self.thread.id,
            'role': 'user',
            'content': 'Test user question',
        })

        self.assertEqual(message.role, 'user')
        self.assertEqual(message.content, 'Test user question')
        self.assertFalse(message.confidence)

    def test_message_create_assistant(self):
        """Test assistant message creation."""
        message = self.Message.create({
            'thread_id': self.thread.id,
            'role': 'assistant',
            'content': 'Test assistant answer',
            'confidence': 0.85,
            'provider_latency_ms': 1500,
            'tokens_used': 250,
        })

        self.assertEqual(message.role, 'assistant')
        self.assertEqual(message.content, 'Test assistant answer')
        self.assertEqual(message.confidence, 0.85)
        self.assertEqual(message.provider_latency_ms, 1500)
        self.assertEqual(message.tokens_used, 250)

    def test_message_roles(self):
        """Test all message roles."""
        roles = ['user', 'assistant', 'system']

        for role in roles:
            message = self.Message.create({
                'thread_id': self.thread.id,
                'role': role,
                'content': f'Test {role} message',
            })
            self.assertEqual(message.role, role)

    def test_message_ordering(self):
        """Test messages are ordered by create_date ascending."""
        msg1 = self.Message.create({
            'thread_id': self.thread.id,
            'role': 'user',
            'content': 'First message',
        })
        msg2 = self.Message.create({
            'thread_id': self.thread.id,
            'role': 'assistant',
            'content': 'Second message',
        })

        messages = self.Message.search([
            ('thread_id', '=', self.thread.id)
        ])

        self.assertEqual(messages[0], msg1)
        self.assertEqual(messages[1], msg2)

    def test_message_cascade_delete(self):
        """Test messages are deleted when thread is deleted."""
        thread = self.Thread.create({
            'provider_id': self.provider.id,
            'user_id': self.env.user.id,
        })
        message = self.Message.create({
            'thread_id': thread.id,
            'role': 'user',
            'content': 'Test message',
        })
        message_id = message.id

        # Delete thread
        thread.unlink()

        # Message should also be deleted
        self.assertFalse(self.Message.browse(message_id).exists())


@tagged('post_install', '-at_install')
class TestAICitation(TransactionCase):
    """Test cases for ipai.ai.citation model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Thread = cls.env['ipai.ai.thread']
        cls.Message = cls.env['ipai.ai.message']
        cls.Citation = cls.env['ipai.ai.citation']
        cls.Provider = cls.env['ipai.ai.provider']

        # Create test data
        cls.provider = cls.Provider.create({
            'name': 'Test Provider',
            'provider_type': 'kapa',
            'company_id': cls.env.company.id,
        })
        cls.thread = cls.Thread.create({
            'provider_id': cls.provider.id,
            'user_id': cls.env.user.id,
        })
        cls.message = cls.Message.create({
            'thread_id': cls.thread.id,
            'role': 'assistant',
            'content': 'Answer with citations [1][2]',
        })

    def test_citation_create(self):
        """Test citation creation."""
        citation = self.Citation.create({
            'message_id': self.message.id,
            'rank': 1,
            'title': 'Source Document',
            'url': 'https://example.com/doc',
            'snippet': 'Relevant text excerpt...',
            'score': 0.95,
        })

        self.assertEqual(citation.message_id, self.message)
        self.assertEqual(citation.rank, 1)
        self.assertEqual(citation.title, 'Source Document')
        self.assertEqual(citation.score, 0.95)

    def test_citation_count_computed(self):
        """Test message citation_count is computed."""
        self.assertEqual(self.message.citation_count, 0)

        # Add citation
        self.Citation.create({
            'message_id': self.message.id,
            'rank': 1,
            'title': 'Source 1',
        })
        self.message.invalidate_recordset()
        self.assertEqual(self.message.citation_count, 1)

        # Add another
        self.Citation.create({
            'message_id': self.message.id,
            'rank': 2,
            'title': 'Source 2',
        })
        self.message.invalidate_recordset()
        self.assertEqual(self.message.citation_count, 2)

    def test_citation_ordering(self):
        """Test citations are ordered by rank."""
        c2 = self.Citation.create({
            'message_id': self.message.id,
            'rank': 2,
            'title': 'Second',
        })
        c1 = self.Citation.create({
            'message_id': self.message.id,
            'rank': 1,
            'title': 'First',
        })

        citations = self.Citation.search([
            ('message_id', '=', self.message.id)
        ])

        self.assertEqual(citations[0], c1)
        self.assertEqual(citations[1], c2)

    def test_citation_cascade_delete(self):
        """Test citations are deleted when message is deleted."""
        message = self.Message.create({
            'thread_id': self.thread.id,
            'role': 'assistant',
            'content': 'Test',
        })
        citation = self.Citation.create({
            'message_id': message.id,
            'rank': 1,
            'title': 'Test Source',
        })
        citation_id = citation.id

        # Delete message
        message.unlink()

        # Citation should also be deleted
        self.assertFalse(self.Citation.browse(citation_id).exists())
