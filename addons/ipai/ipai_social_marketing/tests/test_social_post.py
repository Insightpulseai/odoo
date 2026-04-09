# -*- coding: utf-8 -*-

from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSocialPost(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account = cls.env['ipai.social.account'].create({
            'name': 'Test LinkedIn',
            'platform': 'linkedin',
        })
        cls.post = cls.env['ipai.social.post'].create({
            'message': 'Test post content',
            'account_ids': [(6, 0, [cls.account.id])],
            'scheduled_date': fields.Datetime.now() + timedelta(hours=1),
        })

    def test_default_state_is_draft(self):
        self.assertEqual(self.post.state, 'draft')

    def test_schedule_sets_state(self):
        self.post.action_schedule()
        self.assertEqual(self.post.state, 'scheduled')

    def test_schedule_requires_date(self):
        post = self.env['ipai.social.post'].create({
            'message': 'No date post',
            'account_ids': [(6, 0, [self.account.id])],
        })
        with self.assertRaises(Exception):
            post.action_schedule()

    def test_reset_draft_from_failed(self):
        self.post.state = 'failed'
        self.post.failure_reason = 'Test error'
        self.post.action_reset_draft()
        self.assertEqual(self.post.state, 'draft')
        self.assertFalse(self.post.failure_reason)

    def test_cron_picks_up_due_posts(self):
        self.post.scheduled_date = fields.Datetime.now() - timedelta(minutes=5)
        self.post.state = 'scheduled'
        with patch.object(
            type(self.post), '_enqueue_publish',
        ) as mock_enqueue:
            self.env['ipai.social.post']._cron_process_scheduled()
            mock_enqueue.assert_called_once()

    def test_post_count_on_account(self):
        self.assertEqual(self.account.post_count, 1)
