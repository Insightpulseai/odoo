# -*- coding: utf-8 -*-
"""
Comprehensive tests for the cash.advance model.

Covers: creation, amount computation, full lifecycle workflow, approval gates,
overdue detection, and advance-to-liquidation linkage.

Tags: expense, concur — run with:
    odoo-bin -d test_ipai_liq -i ipai_hr_expense_liquidation \
        --test-tags expense,concur --stop-after-init
"""
from datetime import date, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('expense', 'concur', 'post_install', '-at_install')
class TestCashAdvanceCreation(TransactionCase):
    """Test cash.advance record creation and basic field defaults."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'CA Test Employee'})

    def _make_advance(self, amount=5000.0, **kw):
        vals = {
            'employee_id': self.employee.id,
            'date_needed': date.today().isoformat(),
            'payment_method': 'online_transfer',
        }
        vals.update(kw)
        advance = self.env['cash.advance'].create(vals)
        if amount:
            self.env['cash.advance.line'].create({
                'cash_advance_id': advance.id,
                'purpose': 'Office supplies',
                'amount': amount,
            })
        return advance

    def test_advance_creation(self):
        """Cash advance is created in draft state with auto-generated sequence name."""
        advance = self._make_advance()
        self.assertEqual(advance.state, 'draft')
        self.assertTrue(advance.name and advance.name != 'New',
                        "Sequence name should be auto-assigned on create")

    def test_advance_amount_computation(self):
        """total_amount is sum of all purpose line amounts."""
        advance = self._make_advance(amount=3000.0)
        self.env['cash.advance.line'].create({
            'cash_advance_id': advance.id,
            'purpose': 'Transportation',
            'amount': 2000.0,
        })
        self.env['cash.advance.line'].create({
            'cash_advance_id': advance.id,
            'purpose': 'Meals',
            'amount': 1500.0,
        })
        self.assertAlmostEqual(advance.total_amount, 6500.0)

    def test_advance_defaults(self):
        """Employee default and company default are applied on creation."""
        advance = self._make_advance()
        self.assertEqual(advance.company_id, self.env.company)

    def test_advance_currency_inherits_company(self):
        """Currency defaults to company currency."""
        advance = self._make_advance()
        self.assertEqual(advance.currency_id, self.env.company.currency_id)

    def test_advance_travel_date_constraint(self):
        """Travel start date must not be after end date."""
        with self.assertRaises(ValidationError):
            self._make_advance(
                travel_event_date_from='2026-04-10',
                travel_event_date_to='2026-04-07',
            )

    def test_advance_name_uniqueness(self):
        """Two advances must not have the same reference name."""
        adv1 = self._make_advance()
        with self.assertRaises(Exception):
            # Force duplicate name via direct write
            self.env['cash.advance'].create({
                'name': adv1.name,
                'employee_id': self.employee.id,
                'date_needed': date.today().isoformat(),
                'payment_method': 'check',
            })


@tagged('expense', 'concur', 'post_install', '-at_install')
class TestCashAdvanceWorkflowFull(TransactionCase):
    """Test complete cash.advance lifecycle: draft → submitted → approved → released."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'CA Workflow Employee'})

    def _make_advance_with_line(self, amount=10000.0):
        advance = self.env['cash.advance'].create({
            'employee_id': self.employee.id,
            'date_needed': '2026-05-01',
            'travel_event_date_from': '2026-05-05',
            'travel_event_date_to': '2026-05-08',
            'payment_method': 'online_transfer',
        })
        self.env['cash.advance.line'].create({
            'cash_advance_id': advance.id,
            'purpose': 'Conference expenses',
            'amount': amount,
        })
        return advance

    def test_advance_workflow_draft_to_released(self):
        """Full happy path: draft → submitted → dept_approved → finance_approved → released."""
        adv = self._make_advance_with_line()
        self.assertEqual(adv.state, 'draft')

        adv.action_submit()
        self.assertEqual(adv.state, 'submitted')

        adv.action_dept_approve()
        self.assertEqual(adv.state, 'dept_approved')
        self.assertTrue(adv.approver_id)
        self.assertTrue(adv.approval_date)

        adv.action_finance_approve()
        self.assertEqual(adv.state, 'finance_approved')
        self.assertTrue(adv.finance_approver_id)

        adv.action_release()
        self.assertEqual(adv.state, 'released')

    def test_advance_approval_required_before_finance(self):
        """Finance approval must come after dept approval."""
        adv = self._make_advance_with_line()
        adv.action_submit()
        with self.assertRaises(ValidationError):
            adv.action_finance_approve()

    def test_advance_release_requires_finance_approval(self):
        """Release must follow finance approval."""
        adv = self._make_advance_with_line()
        adv.action_submit()
        adv.action_dept_approve()
        with self.assertRaises(ValidationError):
            adv.action_release()

    def test_advance_submit_requires_lines(self):
        """Submit must be blocked when no purpose lines exist."""
        adv = self.env['cash.advance'].create({
            'employee_id': self.employee.id,
            'date_needed': '2026-05-01',
            'payment_method': 'check',
        })
        with self.assertRaises(ValidationError):
            adv.action_submit()

    def test_advance_reject_from_submitted(self):
        """Advance can be rejected from submitted state."""
        adv = self._make_advance_with_line()
        adv.action_submit()
        adv.action_reject()
        self.assertEqual(adv.state, 'rejected')

    def test_advance_reject_from_dept_approved(self):
        """Advance can be rejected from dept_approved state."""
        adv = self._make_advance_with_line()
        adv.action_submit()
        adv.action_dept_approve()
        adv.action_reject()
        self.assertEqual(adv.state, 'rejected')

    def test_advance_cancel_from_draft(self):
        """Advance can be cancelled from draft state."""
        adv = self._make_advance_with_line()
        adv.action_cancel()
        self.assertEqual(adv.state, 'cancelled')

    def test_advance_reset_to_draft(self):
        """Rejected/cancelled advance can be reset to draft."""
        adv = self._make_advance_with_line()
        adv.action_submit()
        adv.action_reject()
        adv.action_reset_to_draft()
        self.assertEqual(adv.state, 'draft')

    def test_liquidation_due_date_on_release(self):
        """Liquidation due date = travel_event_date_to + 15 days."""
        adv = self._make_advance_with_line()
        adv.action_submit()
        adv.action_dept_approve()
        adv.action_finance_approve()
        adv.action_release()
        expected = date(2026, 5, 8) + timedelta(days=15)
        self.assertEqual(adv.liquidation_due_date, expected)

    def test_liquidation_due_date_fallback_to_date_needed(self):
        """When no travel dates, due date = date_needed + 15 days."""
        adv = self.env['cash.advance'].create({
            'employee_id': self.employee.id,
            'date_needed': '2026-05-01',
            'payment_method': 'check',
        })
        self.env['cash.advance.line'].create({
            'cash_advance_id': adv.id,
            'purpose': 'Misc',
            'amount': 2000.0,
        })
        adv.action_submit()
        adv.action_dept_approve()
        adv.action_finance_approve()
        adv.action_release()
        expected = date(2026, 5, 1) + timedelta(days=15)
        self.assertEqual(adv.liquidation_due_date, expected)

    def test_advance_overdue_detection(self):
        """is_overdue is True when liquidation_due_date is in the past and state=released."""
        adv = self._make_advance_with_line()
        adv.action_submit()
        adv.action_dept_approve()
        adv.action_finance_approve()
        adv.action_release()
        # Override due date to yesterday
        adv.liquidation_due_date = date.today() - timedelta(days=1)
        adv._compute_is_overdue()
        self.assertTrue(adv.is_overdue)

    def test_advance_not_overdue_when_closed(self):
        """is_overdue is False when state is not released/for_liquidation."""
        adv = self._make_advance_with_line()
        adv.action_submit()
        adv.action_dept_approve()
        adv.action_finance_approve()
        adv.action_release()
        adv.liquidation_due_date = date.today() - timedelta(days=1)
        adv.state = 'closed'
        adv._compute_is_overdue()
        self.assertFalse(adv.is_overdue)
