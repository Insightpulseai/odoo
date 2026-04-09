# -*- coding: utf-8 -*-

import base64

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestAgentSources(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Agent = cls.env["ipai.ai.agent"]
        cls.Source = cls.env["ipai.ai.agent.source"]
        cls.Run = cls.env["ipai.ai.agent.source.run"]
        cls.Wizard = cls.env["ipai.ai.agent.source.wizard"]
        cls.Bridge = cls.env["ipai.ai.agent.source.bridge"]

        cls.agent = cls.Agent.create({
            "name": "Test Agent",
            "description": "Test agent for source management",
        })

        # Dummy PDF attachment
        cls.pdf_attachment = cls.env["ir.attachment"].create({
            "name": "test_invoice.pdf",
            "datas": base64.b64encode(b"%PDF-1.4 test content"),
            "mimetype": "application/pdf",
        })

    # ------------------------------------------------------------------
    # Agent CRUD
    # ------------------------------------------------------------------

    def test_agent_create(self):
        self.assertTrue(self.agent.id)
        self.assertEqual(self.agent.source_count, 0)
        self.assertEqual(self.agent.indexed_source_count, 0)
        self.assertTrue(self.agent.restrict_to_sources)

    # ------------------------------------------------------------------
    # Source CRUD & state transitions
    # ------------------------------------------------------------------

    def test_source_create_draft(self):
        source = self.Source.create({
            "name": "test_invoice.pdf",
            "agent_id": self.agent.id,
            "source_type": "pdf",
            "attachment_id": self.pdf_attachment.id,
        })
        self.assertEqual(source.status, "draft")
        self.assertTrue(source.active)

    def test_source_weblink(self):
        source = self.Source.create({
            "name": "https://example.com/docs",
            "agent_id": self.agent.id,
            "source_type": "weblink",
            "url": "https://example.com/docs",
        })
        self.assertEqual(source.source_type, "weblink")
        self.assertEqual(source.status, "draft")

    def test_source_knowledge(self):
        source = self.Source.create({
            "name": "Knowledge: KB-001",
            "agent_id": self.agent.id,
            "source_type": "knowledge",
            "knowledge_ref": "KB-001",
        })
        self.assertEqual(source.source_type, "knowledge")

    def test_callback_indexed(self):
        source = self.Source.create({
            "name": "test.pdf",
            "agent_id": self.agent.id,
            "source_type": "pdf",
            "attachment_id": self.pdf_attachment.id,
            "status": "processing",
        })
        source.callback_indexed(
            external_source_id="ext-123",
            external_index_id="idx-456",
        )
        self.assertEqual(source.status, "indexed")
        self.assertEqual(source.external_source_id, "ext-123")
        self.assertEqual(source.external_index_id, "idx-456")
        self.assertTrue(source.processed_at)
        self.assertFalse(source.last_error)
        # Run record created
        self.assertEqual(len(source.run_ids), 1)
        self.assertEqual(source.run_ids[0].status, "success")

    def test_callback_failed(self):
        source = self.Source.create({
            "name": "bad.pdf",
            "agent_id": self.agent.id,
            "source_type": "pdf",
            "attachment_id": self.pdf_attachment.id,
            "status": "processing",
        })
        source.callback_failed("Document Intelligence returned 400: corrupt PDF")
        self.assertEqual(source.status, "failed")
        self.assertIn("corrupt PDF", source.last_error)
        self.assertEqual(len(source.run_ids), 1)
        self.assertEqual(source.run_ids[0].status, "failed")

    def test_activate_only_indexed(self):
        source = self.Source.create({
            "name": "draft.pdf",
            "agent_id": self.agent.id,
            "source_type": "pdf",
            "attachment_id": self.pdf_attachment.id,
            "active": False,
        })
        with self.assertRaises(UserError):
            source.action_activate()

        # Index it, then activate
        source.write({"status": "indexed"})
        source.action_activate()
        self.assertTrue(source.active)

    def test_deactivate(self):
        source = self.Source.create({
            "name": "active.pdf",
            "agent_id": self.agent.id,
            "source_type": "pdf",
            "attachment_id": self.pdf_attachment.id,
            "status": "indexed",
        })
        source.action_deactivate()
        self.assertFalse(source.active)

    # ------------------------------------------------------------------
    # Source counts
    # ------------------------------------------------------------------

    def test_source_counts(self):
        self.Source.create({
            "name": "s1.pdf",
            "agent_id": self.agent.id,
            "source_type": "pdf",
            "attachment_id": self.pdf_attachment.id,
            "status": "indexed",
        })
        self.Source.create({
            "name": "s2.pdf",
            "agent_id": self.agent.id,
            "source_type": "pdf",
            "attachment_id": self.pdf_attachment.id,
            "status": "draft",
        })
        self.Source.create({
            "name": "s3.pdf",
            "agent_id": self.agent.id,
            "source_type": "pdf",
            "attachment_id": self.pdf_attachment.id,
            "status": "indexed",
            "active": False,
        })
        self.agent.invalidate_recordset()
        self.assertEqual(self.agent.source_count, 3)
        self.assertEqual(self.agent.indexed_source_count, 1)

    # ------------------------------------------------------------------
    # Active indexed sources query
    # ------------------------------------------------------------------

    def test_get_active_indexed_sources(self):
        s1 = self.Source.create({
            "name": "indexed_active.pdf",
            "agent_id": self.agent.id,
            "source_type": "pdf",
            "attachment_id": self.pdf_attachment.id,
            "status": "indexed",
            "external_source_id": "ext-1",
            "external_index_id": "idx-1",
        })
        self.Source.create({
            "name": "indexed_inactive.pdf",
            "agent_id": self.agent.id,
            "source_type": "pdf",
            "attachment_id": self.pdf_attachment.id,
            "status": "indexed",
            "active": False,
            "external_source_id": "ext-2",
        })
        self.Source.create({
            "name": "draft.pdf",
            "agent_id": self.agent.id,
            "source_type": "pdf",
            "attachment_id": self.pdf_attachment.id,
            "status": "draft",
        })

        active = self.Source._get_active_indexed_sources(self.agent.id)
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].id, s1.id)

    def test_bridge_get_active_source_ids(self):
        self.Source.create({
            "name": "indexed.pdf",
            "agent_id": self.agent.id,
            "source_type": "pdf",
            "attachment_id": self.pdf_attachment.id,
            "status": "indexed",
            "external_source_id": "ext-abc",
            "external_index_id": "idx-def",
        })
        result = self.Bridge.get_active_source_ids(self.agent.id)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["external_source_id"], "ext-abc")
        self.assertEqual(result[0]["source_type"], "pdf")

    # ------------------------------------------------------------------
    # Checksum
    # ------------------------------------------------------------------

    def test_checksum_computed(self):
        source = self.Source.create({
            "name": "check.pdf",
            "agent_id": self.agent.id,
            "source_type": "pdf",
            "attachment_id": self.pdf_attachment.id,
        })
        source._compute_checksum()
        self.assertTrue(source.checksum)
        self.assertEqual(len(source.checksum), 64)  # SHA-256 hex

    def test_checksum_weblink(self):
        source = self.Source.create({
            "name": "https://example.com",
            "agent_id": self.agent.id,
            "source_type": "weblink",
            "url": "https://example.com",
        })
        source._compute_checksum()
        self.assertTrue(source.checksum)
