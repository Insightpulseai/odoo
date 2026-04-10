# -*- coding: utf-8 -*-
"""Tests for liquidation total computation and settlement logic."""
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('expense', 'concur', 'post_install', '-at_install')
class TestLiquidationTotals(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee LIQ',
        })

    def _create_liquidation(self, advance_amount=10000.0, liq_type='cash_advance'):
        liq = self.env['hr.expense.liquidation'].create({
            'employee_id': self.employee.id,
            'liquidation_type': liq_type,
            'advance_amount': advance_amount,
        })
        return liq

    def _add_line(self, liq, meals=0, transport=0, misc=0, amount=None, **kwargs):
        # Compute amount from sub-columns if not provided
        if amount is None:
            amount = meals + transport + misc
        vals = {
            'liquidation_id': liq.id,
            'date': '2026-04-06',
            'description': 'Test expense',
            'bucket': 'miscellaneous',
            'amount': amount,
            'meals_amount': meals,
            'transport_amount': transport,
            'misc_amount': misc,
        }
        vals.update(kwargs)
        return self.env['hr.expense.liquidation.line'].create(vals)

    def test_line_total_meals_transport_misc(self):
        """line_total = meals + transport + misc when sub-amounts provided."""
        liq = self._create_liquidation()
        line = self._add_line(liq, meals=500, transport=300, misc=200)
        self.assertEqual(line.line_total, 1000.0)

    def test_line_total_falls_back_to_amount(self):
        """line_total = amount when no sub-amounts set."""
        liq = self._create_liquidation()
        line = self._add_line(liq, amount=750)
        self.assertEqual(line.line_total, 750.0)

    def test_grand_total_with_other_pages(self):
        """Grand total = sum of lines + other_pages_total."""
        liq = self._create_liquidation()
        self._add_line(liq, meals=1000, transport=500)
        self._add_line(liq, meals=800, misc=200)
        liq.other_pages_total = 5000.0
        self.assertEqual(liq.grand_total, 7500.0)  # 1500 + 1000 + 5000

    def test_amount_due_to_employee(self):
        """When expenses exceed advance, amount due to employee is positive."""
        liq = self._create_liquidation(advance_amount=5000.0)
        self._add_line(liq, amount=4000)
        self._add_line(liq, amount=3000)
        # total_expenses = 7000, advance = 5000 -> due to employee = 2000
        self.assertAlmostEqual(liq.amount_due_to_employee, 2000.0)
        self.assertEqual(liq.amount_refundable_to_company, 0.0)
        self.assertEqual(liq.settlement_status, 'reimburse')

    def test_amount_refundable_to_company(self):
        """When advance exceeds expenses, refundable to company is positive."""
        liq = self._create_liquidation(advance_amount=10000.0)
        self._add_line(liq, amount=3000)
        self._add_line(liq, amount=2000)
        # total_expenses = 5000, advance = 10000 -> refundable = 5000
        self.assertAlmostEqual(liq.amount_refundable_to_company, 5000.0)
        self.assertEqual(liq.amount_due_to_employee, 0.0)
        self.assertEqual(liq.settlement_status, 'return')

    def test_exact_liquidation(self):
        """When expenses exactly match advance, both settlement fields are zero."""
        liq = self._create_liquidation(advance_amount=5000.0)
        self._add_line(liq, amount=3000)
        self._add_line(liq, amount=2000)
        self.assertEqual(liq.amount_due_to_employee, 0.0)
        self.assertEqual(liq.amount_refundable_to_company, 0.0)
        self.assertEqual(liq.settlement_status, 'balanced')

    def test_withholding_tax_on_line(self):
        """Lines can track gross/withholding/net amounts."""
        liq = self._create_liquidation()
        line = self._add_line(liq, amount=1000)
        line.write({
            'gross_amount': 1120.0,
            'withholding_tax_amount': 120.0,
            'net_paid_amount': 1000.0,
        })
        self.assertEqual(line.gross_amount, 1120.0)
        self.assertEqual(line.withholding_tax_amount, 120.0)

    def test_reimbursement_type_no_settlement(self):
        """Reimbursement type has no settlement amount (advance=0, status=balanced)."""
        liq = self._create_liquidation(advance_amount=0, liq_type='reimbursement')
        self._add_line(liq, amount=5000)
        self.assertEqual(liq.settlement_amount, 0.0)
        self.assertEqual(liq.settlement_status, 'balanced')

    def test_net_paid_computation(self):
        """Net paid = gross - withholding tax."""
        liq = self._create_liquidation()
        liq.write({
            'gross_amount': 10000.0,
            'withholding_tax_amount': 500.0,
        })
        self.assertEqual(liq.net_paid_amount, 9500.0)
