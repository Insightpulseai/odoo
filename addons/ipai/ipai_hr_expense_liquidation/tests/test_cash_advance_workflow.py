# -*- coding: utf-8 -*-
"""Tests for cash advance request workflow and state transitions."""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('expense', 'concur', 'post_install', '-at_install')
class TestCashAdvanceWorkflow(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee CA',
        })

    def _create_advance(self, amount=10000.0, **kwargs):
        vals = {
            'employee_id': self.employee.id,
            'payee_name': 'Test Employee',
            'date_needed': '2026-04-01',
            'travel_event_date_from': '2026-04-05',
            'travel_event_date_to': '2026-04-07',
            'payment_method': 'autocredit',
        }
        vals.update(kwargs)
        advance = self.env['cash.advance'].create(vals)
        # Add purpose line
        self.env['cash.advance.line'].create({
            'cash_advance_id': advance.id,
            'purpose': 'Client meeting expenses',
            'amount': amount,
        })
        return advance

    def test_initial_state_is_draft(self):
        advance = self._create_advance()
        self.assertEqual(advance.state, 'draft')

    def test_submit_transitions_to_submitted(self):
        advance = self._create_advance()
        advance.action_submit()
        self.assertEqual(advance.state, 'submitted')

    def test_dept_approve_transitions(self):
        advance = self._create_advance()
        advance.action_submit()
        advance.action_dept_approve()
        self.assertEqual(advance.state, 'dept_approved')

    def test_finance_approve_transitions(self):
        advance = self._create_advance()
        advance.action_submit()
        advance.action_dept_approve()
        advance.action_finance_approve()
        self.assertEqual(advance.state, 'finance_approved')

    def test_release_transitions(self):
        advance = self._create_advance()
        advance.action_submit()
        advance.action_dept_approve()
        advance.action_finance_approve()
        advance.action_release()
        self.assertEqual(advance.state, 'released')

    def test_total_amount_computed(self):
        advance = self._create_advance(amount=5000.0)
        self.env['cash.advance.line'].create({
            'cash_advance_id': advance.id,
            'purpose': 'Transportation',
            'amount': 3000.0,
        })
        self.assertEqual(advance.total_amount, 8000.0)

    def test_cancel_from_draft(self):
        advance = self._create_advance()
        advance.action_cancel()
        self.assertEqual(advance.state, 'cancelled')

    def test_reject_from_submitted(self):
        advance = self._create_advance()
        advance.action_submit()
        advance.action_reject()
        self.assertEqual(advance.state, 'rejected')

    def test_cannot_submit_without_lines(self):
        advance = self.env['cash.advance'].create({
            'employee_id': self.employee.id,
            'date_needed': '2026-04-01',
            'payment_method': 'online_transfer',
        })
        with self.assertRaises(ValidationError):
            advance.action_submit()

    def test_reset_to_draft_from_rejected(self):
        advance = self._create_advance()
        advance.action_submit()
        advance.action_reject()
        advance.action_reset_to_draft()
        self.assertEqual(advance.state, 'draft')

    def test_liquidation_due_date_set_on_release(self):
        """Release computes liquidation due date = travel_event_date_to + 15 days."""
        from datetime import date, timedelta
        advance = self._create_advance()
        advance.action_submit()
        advance.action_dept_approve()
        advance.action_finance_approve()
        advance.action_release()
        expected = date(2026, 4, 7) + timedelta(days=15)
        self.assertEqual(advance.liquidation_due_date, expected)

    def test_overdue_flag(self):
        """Advance becomes overdue when past due date and in released state."""
        from datetime import date, timedelta
        advance = self._create_advance()
        advance.action_submit()
        advance.action_dept_approve()
        advance.action_finance_approve()
        advance.action_release()
        # Manually set past due date to force overdue
        past_date = date.today() - timedelta(days=1)
        advance.liquidation_due_date = past_date
        advance._compute_is_overdue()
        self.assertTrue(advance.is_overdue)
