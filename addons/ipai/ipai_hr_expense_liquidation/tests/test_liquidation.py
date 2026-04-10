# -*- coding: utf-8 -*-
"""
Comprehensive tests for hr.expense.liquidation model.

Covers: creation, advance linkage, settlement math (3 cases), workflow,
line totals, finance review metadata, and multi-line aggregation.

Tags: expense, concur — run with:
    odoo-bin -d test_ipai_liq -i ipai_hr_expense_liquidation \
        --test-tags expense,concur --stop-after-init
"""
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('expense', 'concur', 'post_install', '-at_install')
class TestLiquidationCreation(TransactionCase):
    """Test hr.expense.liquidation creation and basic defaults."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'LIQ Test Employee'})

    def _make_liq(self, advance_amount=10000.0, liq_type='cash_advance'):
        return self.env['hr.expense.liquidation'].create({
            'employee_id': self.employee.id,
            'liquidation_type': liq_type,
            'advance_amount': advance_amount,
        })

    def test_liquidation_creation(self):
        """Liquidation is created in draft state with auto sequence name."""
        liq = self._make_liq()
        self.assertEqual(liq.state, 'draft')
        self.assertTrue(liq.name and liq.name != 'New')

    def test_liquidation_defaults(self):
        """Company and currency default to current company."""
        liq = self._make_liq()
        self.assertEqual(liq.company_id, self.env.company)
        self.assertEqual(liq.currency_id, self.env.company.currency_id)

    def test_liquidation_line_count(self):
        """line_count reflects number of expense lines."""
        liq = self._make_liq()
        self.assertEqual(liq.line_count, 0)
        self.env['hr.expense.liquidation.line'].create({
            'liquidation_id': liq.id,
            'description': 'Lunch',
            'date': '2026-04-06',
            'bucket': 'meals',
            'amount': 500.0,
        })
        self.assertEqual(liq.line_count, 1)


@tagged('expense', 'concur', 'post_install', '-at_install')
class TestLiquidationAdvanceLinkage(TransactionCase):
    """Test advance linkage and reference tracking between cash.advance and liquidation."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'LIQ Linkage Employee'})

    def test_liquidation_advance_linkage(self):
        """Liquidation can reference a cash advance request via cash_advance_request_id."""
        advance = self.env['cash.advance'].create({
            'employee_id': self.employee.id,
            'date_needed': '2026-05-01',
            'payment_method': 'online_transfer',
        })
        self.env['cash.advance.line'].create({
            'cash_advance_id': advance.id,
            'purpose': 'Event expenses',
            'amount': 8000.0,
        })
        advance.action_submit()
        advance.action_dept_approve()
        advance.action_finance_approve()
        advance.action_release()

        # Use action_start_liquidation to create the linked liquidation
        result = advance.action_start_liquidation()
        self.assertEqual(advance.state, 'for_liquidation')
        self.assertTrue(advance.liquidation_id)
        liq = advance.liquidation_id
        self.assertEqual(liq.cash_advance_request_id, advance)
        self.assertAlmostEqual(liq.advance_amount, 8000.0)

    def test_liquidation_advance_reference_fields(self):
        """advance_reference and advance_date fields carry over from advance."""
        advance = self.env['cash.advance'].create({
            'employee_id': self.employee.id,
            'date_needed': '2026-05-10',
            'payment_method': 'check',
        })
        self.env['cash.advance.line'].create({
            'cash_advance_id': advance.id,
            'purpose': 'Office supplies',
            'amount': 5000.0,
        })
        advance.action_submit()
        advance.action_dept_approve()
        advance.action_finance_approve()
        advance.action_release()
        advance.action_start_liquidation()

        liq = advance.liquidation_id
        self.assertEqual(liq.advance_reference, advance.name)


@tagged('expense', 'concur', 'post_install', '-at_install')
class TestLiquidationSettlement(TransactionCase):
    """Test settlement math: due_to_employee, refundable_to_company, balanced."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'Settlement Test Emp'})

    def _make_liq(self, advance_amount):
        return self.env['hr.expense.liquidation'].create({
            'employee_id': self.employee.id,
            'liquidation_type': 'cash_advance',
            'advance_amount': advance_amount,
        })

    def _add_line(self, liq, amount, bucket='miscellaneous'):
        return self.env['hr.expense.liquidation.line'].create({
            'liquidation_id': liq.id,
            'description': 'Expense item',
            'date': '2026-04-06',
            'bucket': bucket,
            'amount': amount,
        })

    def test_settlement_due_to_employee(self):
        """When total_expenses > advance, employee is owed the difference."""
        liq = self._make_liq(advance_amount=5000.0)
        self._add_line(liq, 4000.0)
        self._add_line(liq, 3000.0)
        # total_expenses = 7000, advance = 5000
        self.assertAlmostEqual(liq.amount_due_to_employee, 2000.0)
        self.assertAlmostEqual(liq.amount_refundable_to_company, 0.0)
        self.assertEqual(liq.settlement_status, 'reimburse')
        self.assertAlmostEqual(liq.settlement_amount, -2000.0)

    def test_settlement_refundable(self):
        """When advance > total_expenses, company is refundable the difference."""
        liq = self._make_liq(advance_amount=10000.0)
        self._add_line(liq, 3000.0)
        self._add_line(liq, 2000.0)
        # total_expenses = 5000, advance = 10000
        self.assertAlmostEqual(liq.amount_refundable_to_company, 5000.0)
        self.assertAlmostEqual(liq.amount_due_to_employee, 0.0)
        self.assertEqual(liq.settlement_status, 'return')
        self.assertAlmostEqual(liq.settlement_amount, 5000.0)

    def test_settlement_exact_match(self):
        """When advance == total_expenses, both settlement fields are zero."""
        liq = self._make_liq(advance_amount=5000.0)
        self._add_line(liq, 3000.0)
        self._add_line(liq, 2000.0)
        self.assertAlmostEqual(liq.amount_due_to_employee, 0.0)
        self.assertAlmostEqual(liq.amount_refundable_to_company, 0.0)
        self.assertEqual(liq.settlement_status, 'balanced')
        self.assertAlmostEqual(liq.settlement_amount, 0.0)


@tagged('expense', 'concur', 'post_install', '-at_install')
class TestLiquidationWorkflow(TransactionCase):
    """Test hr.expense.liquidation state machine."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'LIQ Workflow Emp'})

    def _make_liq_with_line(self, advance_amount=5000.0):
        liq = self.env['hr.expense.liquidation'].create({
            'employee_id': self.employee.id,
            'liquidation_type': 'cash_advance',
            'advance_amount': advance_amount,
        })
        self.env['hr.expense.liquidation.line'].create({
            'liquidation_id': liq.id,
            'description': 'Test expense',
            'date': '2026-04-06',
            'bucket': 'meals',
            'amount': 2000.0,
        })
        return liq

    def test_liquidation_workflow(self):
        """Full workflow: draft → submitted → manager_approved → finance_approved → released → in_liquidation → liquidated → closed."""
        liq = self._make_liq_with_line()
        self.assertEqual(liq.state, 'draft')

        liq.action_submit()
        self.assertEqual(liq.state, 'submitted')

        liq.action_manager_approve()
        self.assertEqual(liq.state, 'manager_approved')
        self.assertTrue(liq.approver_id)

        liq.action_finance_approve()
        self.assertEqual(liq.state, 'finance_approved')
        self.assertTrue(liq.finance_approver_id)

        liq.action_release()
        self.assertEqual(liq.state, 'released')

        liq.action_start_liquidation()
        self.assertEqual(liq.state, 'in_liquidation')

        liq.action_liquidate()
        self.assertEqual(liq.state, 'liquidated')
        self.assertTrue(liq.finance_posted_by)

        liq.action_close()
        self.assertEqual(liq.state, 'closed')

    def test_liquidation_reject_from_submitted(self):
        """Liquidation can be rejected from submitted state."""
        liq = self._make_liq_with_line()
        liq.action_submit()
        liq.action_reject()
        self.assertEqual(liq.state, 'rejected')

    def test_liquidation_cancel_from_draft(self):
        """Liquidation can be cancelled from draft."""
        liq = self._make_liq_with_line()
        liq.action_cancel()
        self.assertEqual(liq.state, 'cancelled')

    def test_liquidation_reset_to_draft(self):
        """Rejected liquidation can be reset to draft."""
        liq = self._make_liq_with_line()
        liq.action_submit()
        liq.action_reject()
        liq.action_reset_to_draft()
        self.assertEqual(liq.state, 'draft')

    def test_liquidation_cannot_liquidate_without_lines(self):
        """Liquidating without expense lines raises ValidationError."""
        liq = self.env['hr.expense.liquidation'].create({
            'employee_id': self.employee.id,
            'liquidation_type': 'cash_advance',
            'advance_amount': 5000.0,
        })
        liq.action_submit()
        liq.action_manager_approve()
        liq.action_finance_approve()
        liq.action_release()
        liq.action_start_liquidation()
        with self.assertRaises(ValidationError):
            liq.action_liquidate()

    def test_finance_metadata_on_approve(self):
        """Finance approval date and approver are recorded."""
        liq = self._make_liq_with_line()
        liq.action_submit()
        liq.action_manager_approve()
        liq.action_finance_approve()
        self.assertTrue(liq.finance_approval_date)
        self.assertEqual(liq.finance_approver_id, self.env.user)


@tagged('expense', 'concur', 'post_install', '-at_install')
class TestLiquidationLineTotals(TransactionCase):
    """Test hr.expense.liquidation.line computation and bucket categorization."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'Line Test Emp'})

    def _make_liq(self):
        return self.env['hr.expense.liquidation'].create({
            'employee_id': self.employee.id,
            'liquidation_type': 'cash_advance',
            'advance_amount': 20000.0,
        })

    def test_liquidation_line_totals(self):
        """total_expenses = sum of all line amounts; bucket totals split correctly."""
        liq = self._make_liq()
        # meals lines
        self.env['hr.expense.liquidation.line'].create([
            {'liquidation_id': liq.id, 'description': 'Lunch', 'date': '2026-04-06',
             'bucket': 'meals', 'amount': 800.0, 'meals_amount': 800.0},
            {'liquidation_id': liq.id, 'description': 'Dinner', 'date': '2026-04-07',
             'bucket': 'meals', 'amount': 1200.0, 'meals_amount': 1200.0},
        ])
        # transportation line
        self.env['hr.expense.liquidation.line'].create({
            'liquidation_id': liq.id, 'description': 'Taxi', 'date': '2026-04-06',
            'bucket': 'transportation', 'amount': 500.0, 'transport_amount': 500.0,
        })
        # misc line
        self.env['hr.expense.liquidation.line'].create({
            'liquidation_id': liq.id, 'description': 'Misc item', 'date': '2026-04-06',
            'bucket': 'miscellaneous', 'amount': 300.0, 'misc_amount': 300.0,
        })

        self.assertAlmostEqual(liq.total_expenses, 2800.0)
        self.assertAlmostEqual(liq.total_meals, 2000.0)
        self.assertAlmostEqual(liq.total_transportation, 500.0)
        self.assertAlmostEqual(liq.total_miscellaneous, 300.0)

    def test_line_total_computed_from_sub_amounts(self):
        """line_total = meals + transport + misc when sub-amounts provided."""
        liq = self._make_liq()
        line = self.env['hr.expense.liquidation.line'].create({
            'liquidation_id': liq.id,
            'description': 'Mixed line',
            'date': '2026-04-06',
            'bucket': 'miscellaneous',
            'amount': 1600.0,
            'meals_amount': 600.0,
            'transport_amount': 700.0,
            'misc_amount': 300.0,
        })
        self.assertAlmostEqual(line.line_total, 1600.0)

    def test_line_total_falls_back_to_amount(self):
        """line_total = amount when no sub-amounts set."""
        liq = self._make_liq()
        line = self.env['hr.expense.liquidation.line'].create({
            'liquidation_id': liq.id,
            'description': 'Simple item',
            'date': '2026-04-06',
            'bucket': 'miscellaneous',
            'amount': 750.0,
        })
        self.assertAlmostEqual(line.line_total, 750.0)

    def test_grand_total_includes_other_pages(self):
        """grand_total = total_expenses + other_pages_total."""
        liq = self._make_liq()
        self.env['hr.expense.liquidation.line'].create({
            'liquidation_id': liq.id,
            'description': 'Item',
            'date': '2026-04-06',
            'bucket': 'meals',
            'amount': 3000.0,
        })
        liq.other_pages_total = 7000.0
        self.assertAlmostEqual(liq.grand_total, 10000.0)
