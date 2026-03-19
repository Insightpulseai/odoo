# -*- coding: utf-8 -*-
"""
Tests for ipai_ai_core:
- CRUD for all four models (provider, thread, message, citation)
- update_stats running average on provider
- Multi-company isolation
- Default provider uniqueness constraint
"""
from odoo.tests.common import TransactionCase


class TestAiCoreSetup(TransactionCase):
    """Base setup shared by all test classes."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_main = cls.env.ref("base.main_company")
        cls.company_alt = cls.env["res.company"].create({"name": "Alt Corp"})

        cls.provider = cls.env["ipai.ai.provider"].create(
            {
                "name": "Test OpenAI",
                "provider_type": "openai",
                "model_name": "gpt-4o",
                "base_url": "https://api.openai.com/v1",
                "api_key_param": "ipai.ai.test_key",
                "company_id": cls.company_main.id,
            }
        )


class TestAiProviderCRUD(TestAiCoreSetup):
    """Basic CRUD and field defaults for ipai.ai.provider."""

    def test_provider_created(self):
        self.assertTrue(self.provider.exists())
        self.assertEqual(self.provider.provider_type, "openai")

    def test_provider_defaults(self):
        self.assertEqual(self.provider.max_tokens, 4096)
        self.assertAlmostEqual(self.provider.temperature, 0.7, places=2)
        self.assertFalse(self.provider.is_default)
        self.assertTrue(self.provider.active)

    def test_provider_stats_initial(self):
        self.assertEqual(self.provider.total_requests, 0)
        self.assertAlmostEqual(self.provider.avg_latency_ms, 0.0)
        self.assertEqual(self.provider.total_tokens, 0)


class TestAiProviderUpdateStats(TestAiCoreSetup):
    """update_stats: running average for latency, accumulation for requests and tokens."""

    def test_single_call(self):
        self.provider.update_stats(150, 500)
        self.assertEqual(self.provider.total_requests, 1)
        self.assertAlmostEqual(self.provider.avg_latency_ms, 150.0)
        self.assertEqual(self.provider.total_tokens, 500)

    def test_running_average(self):
        self.provider.update_stats(100, 200)
        self.provider.update_stats(200, 300)
        self.assertEqual(self.provider.total_requests, 2)
        # avg = (100 + 200) / 2 = 150
        self.assertAlmostEqual(self.provider.avg_latency_ms, 150.0)
        self.assertEqual(self.provider.total_tokens, 500)

    def test_three_calls_average(self):
        self.provider.update_stats(100, 100)
        self.provider.update_stats(200, 200)
        self.provider.update_stats(300, 300)
        self.assertEqual(self.provider.total_requests, 3)
        # avg = (100 + 200 + 300) / 3 = 200
        self.assertAlmostEqual(self.provider.avg_latency_ms, 200.0)
        self.assertEqual(self.provider.total_tokens, 600)

    def test_zero_latency(self):
        self.provider.update_stats(0, 0)
        self.assertEqual(self.provider.total_requests, 1)
        self.assertAlmostEqual(self.provider.avg_latency_ms, 0.0)
        self.assertEqual(self.provider.total_tokens, 0)


class TestAiProviderDefault(TestAiCoreSetup):
    """Only one default provider per company."""

    def test_set_default_unsets_other(self):
        self.provider.write({"is_default": True})
        self.assertTrue(self.provider.is_default)

        provider2 = self.env["ipai.ai.provider"].create(
            {
                "name": "Second Provider",
                "provider_type": "anthropic",
                "is_default": True,
                "company_id": self.company_main.id,
            }
        )
        self.assertTrue(provider2.is_default)
        self.provider.invalidate_recordset()
        self.assertFalse(self.provider.is_default)

    def test_different_company_keeps_default(self):
        self.provider.write({"is_default": True})
        provider_alt = self.env["ipai.ai.provider"].create(
            {
                "name": "Alt Provider",
                "provider_type": "google",
                "is_default": True,
                "company_id": self.company_alt.id,
            }
        )
        self.provider.invalidate_recordset()
        # Both should remain default — different companies
        self.assertTrue(self.provider.is_default)
        self.assertTrue(provider_alt.is_default)


class TestAiThreadCRUD(TestAiCoreSetup):
    """CRUD for ipai.ai.thread."""

    def test_create_thread(self):
        thread = self.env["ipai.ai.thread"].create(
            {
                "provider_id": self.provider.id,
                "user_id": self.env.user.id,
            }
        )
        self.assertTrue(thread.exists())
        self.assertEqual(thread.provider_id, self.provider)
        self.assertEqual(thread.user_id, self.env.user)
        self.assertEqual(thread.company_id, self.env.company)

    def test_thread_default_user(self):
        thread = self.env["ipai.ai.thread"].create(
            {"provider_id": self.provider.id}
        )
        self.assertEqual(thread.user_id, self.env.user)


class TestAiMessageCRUD(TestAiCoreSetup):
    """CRUD for ipai.ai.message."""

    def test_create_message(self):
        thread = self.env["ipai.ai.thread"].create(
            {"provider_id": self.provider.id}
        )
        msg = self.env["ipai.ai.message"].create(
            {
                "thread_id": thread.id,
                "role": "user",
                "content": "What is Odoo?",
            }
        )
        self.assertTrue(msg.exists())
        self.assertEqual(msg.role, "user")
        self.assertEqual(msg.content, "What is Odoo?")
        self.assertAlmostEqual(msg.confidence, 0.0)
        self.assertEqual(msg.provider_latency_ms, 0)

    def test_message_cascade_delete(self):
        thread = self.env["ipai.ai.thread"].create(
            {"provider_id": self.provider.id}
        )
        msg = self.env["ipai.ai.message"].create(
            {
                "thread_id": thread.id,
                "role": "assistant",
                "content": "Odoo is an ERP.",
                "confidence": 0.95,
                "provider_latency_ms": 250,
            }
        )
        msg_id = msg.id
        thread.unlink()
        self.assertFalse(self.env["ipai.ai.message"].browse(msg_id).exists())

    def test_thread_message_ids(self):
        thread = self.env["ipai.ai.thread"].create(
            {"provider_id": self.provider.id}
        )
        msg1 = self.env["ipai.ai.message"].create(
            {"thread_id": thread.id, "role": "user", "content": "Hello"}
        )
        msg2 = self.env["ipai.ai.message"].create(
            {"thread_id": thread.id, "role": "assistant", "content": "Hi"}
        )
        self.assertEqual(len(thread.message_ids), 2)
        self.assertIn(msg1, thread.message_ids)
        self.assertIn(msg2, thread.message_ids)


class TestAiCitationCRUD(TestAiCoreSetup):
    """CRUD for ipai.ai.citation."""

    def test_create_citation(self):
        thread = self.env["ipai.ai.thread"].create(
            {"provider_id": self.provider.id}
        )
        msg = self.env["ipai.ai.message"].create(
            {
                "thread_id": thread.id,
                "role": "assistant",
                "content": "See [1] for details.",
            }
        )
        cite = self.env["ipai.ai.citation"].create(
            {
                "message_id": msg.id,
                "rank": 1,
                "title": "Odoo Documentation",
                "url": "https://www.odoo.com/documentation",
                "snippet": "Odoo is a suite of business apps.",
                "score": 0.92,
            }
        )
        self.assertTrue(cite.exists())
        self.assertEqual(cite.rank, 1)
        self.assertAlmostEqual(cite.score, 0.92, places=2)

    def test_citation_cascade_delete(self):
        thread = self.env["ipai.ai.thread"].create(
            {"provider_id": self.provider.id}
        )
        msg = self.env["ipai.ai.message"].create(
            {
                "thread_id": thread.id,
                "role": "assistant",
                "content": "Answer with citation.",
            }
        )
        cite = self.env["ipai.ai.citation"].create(
            {
                "message_id": msg.id,
                "rank": 1,
                "title": "Source",
                "url": "https://example.com",
                "snippet": "Example content.",
                "score": 0.5,
            }
        )
        cite_id = cite.id
        msg.unlink()
        self.assertFalse(self.env["ipai.ai.citation"].browse(cite_id).exists())

    def test_message_citation_ids(self):
        thread = self.env["ipai.ai.thread"].create(
            {"provider_id": self.provider.id}
        )
        msg = self.env["ipai.ai.message"].create(
            {
                "thread_id": thread.id,
                "role": "assistant",
                "content": "Multi-citation answer [1][2].",
            }
        )
        cite1 = self.env["ipai.ai.citation"].create(
            {"message_id": msg.id, "rank": 1, "title": "First"}
        )
        cite2 = self.env["ipai.ai.citation"].create(
            {"message_id": msg.id, "rank": 2, "title": "Second"}
        )
        self.assertEqual(len(msg.citation_ids), 2)
        self.assertIn(cite1, msg.citation_ids)
        self.assertIn(cite2, msg.citation_ids)


class TestMultiCompanyIsolation(TestAiCoreSetup):
    """Multi-company isolation: providers scoped to company_id."""

    def test_provider_company_filter(self):
        provider_alt = self.env["ipai.ai.provider"].create(
            {
                "name": "Alt Provider",
                "provider_type": "anthropic",
                "company_id": self.company_alt.id,
            }
        )
        # Search for main company providers only
        main_providers = self.env["ipai.ai.provider"].search(
            [("company_id", "=", self.company_main.id)]
        )
        self.assertIn(self.provider, main_providers)
        self.assertNotIn(provider_alt, main_providers)

    def test_global_provider_visible_to_all(self):
        """A provider with company_id=False should be found by any company search
        using the pattern from ipai_ai_agents_ui bootstrap controller."""
        global_provider = self.env["ipai.ai.provider"].create(
            {
                "name": "Global Provider",
                "provider_type": "ollama",
                "company_id": False,
            }
        )
        results = self.env["ipai.ai.provider"].search(
            [
                ("active", "=", True),
                "|",
                ("company_id", "=", self.company_alt.id),
                ("company_id", "=", False),
            ]
        )
        self.assertIn(global_provider, results)

    def test_thread_inherits_company(self):
        thread = self.env["ipai.ai.thread"].create(
            {"provider_id": self.provider.id}
        )
        self.assertEqual(thread.company_id, self.env.company)


class TestFullConversationFlow(TestAiCoreSetup):
    """End-to-end: create provider -> thread -> messages -> citations -> stats."""

    def test_full_flow(self):
        # 1. Thread
        thread = self.env["ipai.ai.thread"].create(
            {"provider_id": self.provider.id}
        )

        # 2. User message
        user_msg = self.env["ipai.ai.message"].create(
            {
                "thread_id": thread.id,
                "role": "user",
                "content": "How do I create an invoice?",
            }
        )
        self.assertEqual(user_msg.role, "user")

        # 3. Assistant message with latency
        asst_msg = self.env["ipai.ai.message"].create(
            {
                "thread_id": thread.id,
                "role": "assistant",
                "content": "Navigate to Invoicing > Invoices [1].",
                "confidence": 0.88,
                "provider_latency_ms": 320,
            }
        )

        # 4. Citations on the assistant message
        self.env["ipai.ai.citation"].create(
            {
                "message_id": asst_msg.id,
                "rank": 1,
                "title": "Odoo Invoicing Docs",
                "url": "https://www.odoo.com/documentation/19.0/invoicing.html",
                "snippet": "To create a new invoice, go to...",
                "score": 0.95,
            }
        )

        # 5. Verify thread messages
        self.assertEqual(len(thread.message_ids), 2)
        self.assertEqual(len(asst_msg.citation_ids), 1)

        # 6. Update provider stats
        self.provider.update_stats(320, 450)
        self.assertEqual(self.provider.total_requests, 1)
        self.assertAlmostEqual(self.provider.avg_latency_ms, 320.0)
        self.assertEqual(self.provider.total_tokens, 450)
