# -*- coding: utf-8 -*-
"""
Tests for IPAI AI Sources (Odoo Export)
=======================================

These tests verify the KB exporter functionality.
"""
from unittest.mock import patch, MagicMock

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestKBExporter(TransactionCase):
    """Test cases for KB Exporter."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test project and task
        cls.project = cls.env['project.project'].create({
            'name': 'Test Project',
        })
        cls.task = cls.env['project.task'].create({
            'name': 'Test Task',
            'project_id': cls.project.id,
            'description': '<p>Task description with <b>HTML</b></p>',
        })

    def test_export_run_creation(self):
        """Test that export runs are created."""
        ExportRun = self.env['ipai.kb.export.run']

        run = ExportRun.create({
            'company_id': self.env.company.id,
            'chunks_count': 5,
            'state': 'success',
        })

        self.assertEqual(run.company_id, self.env.company)
        self.assertEqual(run.chunks_count, 5)
        self.assertEqual(run.state, 'success')

    def test_task_collection(self):
        """Test that tasks are collected correctly."""
        Exporter = self.env['ipai.kb.exporter']

        # Get recent tasks
        from datetime import timedelta
        from odoo import fields
        since = fields.Datetime.now() - timedelta(hours=24)
        tenant_ref = f"odoo_company:{self.env.company.id}"

        chunks = Exporter._collect_tasks(tenant_ref, since)

        # Should include our test task
        task_refs = [c['source_ref'] for c in chunks]
        self.assertIn(f'project.task:{self.task.id}', task_refs)

        # Check chunk content
        task_chunk = next(c for c in chunks if c['source_ref'] == f'project.task:{self.task.id}')
        self.assertEqual(task_chunk['title'], 'Test Task')
        self.assertIn('Test Project', task_chunk['content'])
        self.assertEqual(task_chunk['source_type'], 'odoo_task')

    def test_html_stripping(self):
        """Test that HTML is stripped from content."""
        Exporter = self.env['ipai.kb.exporter']

        html = '<p>Hello <b>World</b>!</p>'
        result = Exporter._strip_html(html)

        self.assertNotIn('<p>', result)
        self.assertNotIn('<b>', result)
        self.assertIn('Hello', result)
        self.assertIn('World', result)

    def test_html_stripping_empty(self):
        """Test that empty HTML returns empty string."""
        Exporter = self.env['ipai.kb.exporter']

        self.assertEqual(Exporter._strip_html(''), '')
        self.assertEqual(Exporter._strip_html(None), '')

    def test_export_run_states(self):
        """Test export run state management."""
        ExportRun = self.env['ipai.kb.export.run']

        run = ExportRun.create({
            'company_id': self.env.company.id,
            'state': 'running',
        })

        self.assertEqual(run.state, 'running')
        self.assertFalse(run.completed_at)

        # Mark as success
        from odoo import fields
        run.write({
            'state': 'success',
            'completed_at': fields.Datetime.now(),
        })

        self.assertEqual(run.state, 'success')
        self.assertTrue(run.completed_at)
        self.assertTrue(run.duration_seconds >= 0)

    def test_chunk_payload_structure(self):
        """Test that chunk payloads have correct structure."""
        Exporter = self.env['ipai.kb.exporter']

        from datetime import timedelta
        from odoo import fields
        since = fields.Datetime.now() - timedelta(hours=24)
        tenant_ref = f"odoo_company:{self.env.company.id}"

        chunks = Exporter._collect_tasks(tenant_ref, since)

        for chunk in chunks:
            # Required fields
            self.assertIn('tenant_ref', chunk)
            self.assertIn('source_type', chunk)
            self.assertIn('source_ref', chunk)
            self.assertIn('content', chunk)
            self.assertIn('updated_at', chunk)

            # Correct tenant
            self.assertEqual(chunk['tenant_ref'], tenant_ref)

            # Valid source type
            self.assertIn(chunk['source_type'], ['odoo_task', 'odoo_kb'])

    def test_cron_without_supabase(self):
        """Test that cron handles missing Supabase config gracefully."""
        Exporter = self.env['ipai.kb.exporter']

        # Clear env vars
        import os
        with patch.dict(os.environ, {'IPAI_SUPABASE_URL': '', 'IPAI_SUPABASE_SERVICE_ROLE_KEY': ''}):
            # Should return True (skip) without error
            result = Exporter.cron_export_recent()
            self.assertTrue(result)

    def test_kb_pages_optional(self):
        """Test that KB pages collection handles missing module."""
        Exporter = self.env['ipai.kb.exporter']

        from datetime import timedelta
        from odoo import fields
        since = fields.Datetime.now() - timedelta(hours=24)
        tenant_ref = f"odoo_company:{self.env.company.id}"

        # Should return empty list if document.page not installed
        chunks = Exporter._collect_kb_pages(tenant_ref, since)
        self.assertIsInstance(chunks, list)

    def test_export_run_name_get(self):
        """Test export run display name."""
        ExportRun = self.env['ipai.kb.export.run']

        run = ExportRun.create({
            'company_id': self.env.company.id,
            'state': 'success',
        })

        name = run.name_get()[0][1]
        self.assertIn('Export Run', name)
        self.assertIn('success', name)


@tagged('post_install', '-at_install')
class TestKBExporterWithMock(TransactionCase):
    """Test cases for KB Exporter with mocked Supabase."""

    def test_upsert_chunks_with_mock(self):
        """Test upsert logic with mocked Supabase."""
        Exporter = self.env['ipai.kb.exporter']

        chunks = [
            {
                'tenant_ref': 'odoo_company:1',
                'source_type': 'odoo_task',
                'source_ref': 'project.task:1',
                'title': 'Test',
                'content': 'Content',
                'updated_at': '2024-01-01T00:00:00',
            }
        ]

        # Mock requests
        mock_response = MagicMock()
        mock_response.status_code = 201

        with patch('requests.post', return_value=mock_response) as mock_post:
            result = Exporter._upsert_chunks(
                'https://test.supabase.co',
                'test_key',
                chunks,
            )

            self.assertTrue(result)
            mock_post.assert_called_once()

            # Check request
            call_args = mock_post.call_args
            self.assertIn('kb.chunks', call_args[0][0])
            self.assertIn('apikey', call_args[1]['headers'])
