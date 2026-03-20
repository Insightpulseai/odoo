# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAiJob(TransactionCase):

    def setUp(self):
        super().setUp()
        self.job = self.env['ipai.ai.job'].create({
            'source_model': 'res.partner',
            'source_record_id': 1,
            'source_record_name': 'Test Partner',
            'job_type': 'ocr_extract',
        })

    def test_job_created_queued(self):
        self.assertEqual(self.job.state, 'queued')
        self.assertTrue(self.job.correlation_id)

    def test_start_sets_running(self):
        self.job.action_start()
        self.assertEqual(self.job.state, 'running')
        self.assertTrue(self.job.started_at)

    def test_complete_sets_done(self):
        self.job.action_start()
        self.job.action_complete(result_payload={'text': 'hello'}, confidence=0.95)
        self.assertEqual(self.job.state, 'done')

    def test_low_confidence_triggers_review(self):
        self.job.action_start()
        self.job.action_complete(result_payload={'text': 'hello'}, confidence=0.5)
        self.assertEqual(self.job.state, 'needs_review')
        self.assertTrue(self.job.needs_human_review)

    def test_fail_sets_error(self):
        self.job.action_start()
        self.job.action_fail('Connection timeout', 'timeout')
        self.assertEqual(self.job.state, 'failed')
        self.assertEqual(self.job.error_class, 'timeout')

    def test_retry_increments_count(self):
        self.job.action_start()
        self.job.action_fail('Error', 'network')
        self.job.action_retry()
        self.assertEqual(self.job.state, 'queued')
        self.assertEqual(self.job.retry_count, 1)

    def test_retry_exceeds_max(self):
        self.job.write({'retry_count': 3, 'state': 'failed'})
        with self.assertRaises(UserError):
            self.job.action_retry()

    def test_cancel(self):
        self.job.action_cancel()
        self.assertEqual(self.job.state, 'cancelled')
