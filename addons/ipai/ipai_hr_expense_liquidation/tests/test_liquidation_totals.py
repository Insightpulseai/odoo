# -*- coding: utf-8 -*-
"""Tests for liquidation total computation and settlement logic."""
from odoo.tests.common import TransactionCase


class TestLiquidationTotals(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.branch = cls.env.ref('ipai_branch_profile.branch_pasig_ho')
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
        })

    def _create_liquidation(self, cash_advanced=10000.0):
        liq = self.env['hr.expense.liquidation'].create({
            'employee_id': self.employee.id,
            'liquidation_type': 'cash_advance',
            'cash_advanced_amount': cash_advanced,
            'branch_id': self.branch.id,
        })
        return liq

    def _add_line(self, liq, meals=0, transport=0, misc=0, **kwargs):
        vals = {
            'liquidation_id': liq.id,
            'expense_date': '2026-04-06',
            'particulars': 'Test expense',
            'meals_amount': meals,
            'transport_amount': transport,
            'misc_amount': misc,
        }
        vals.update(kwargs)
        return self.env['hr.expense.liquidation.line'].create(vals)

    def test_line_total_meals_transport_misc(self):
        """Line total = meals + transport + misc."""
        liq = self._create_liquidation()
        line = self._add_line(liq, meals=500, transport=300, misc=200)
        self.assertEqual(line.line_total, 1000.0)

    def test_grand_total_with_other_pages(self):
        """Grand total = sum of lines + other_pages_total."""
        liq = self._create_liquidation()
        self._add_line(liq, meals=1000, transport=500)
        self._add_line(liq, meals=800, misc=200)
        liq.other_pages_total = 5000.0
        self.assertEqual(liq.grand_total, 7500.0)  # 1500 + 1000 + 5000

    def test_amount_due_to_employee(self):
        """When expenses exceed advance, amount due to employee is positive."""
        liq = self._create_liquidation(cash_advanced=5000.0)
        self._add_line(liq, meals=4000, transport=3000)
        # grand_total = 7000, advance = 5000 -> due to employee = 2000
        self.assertEqual(liq.amount_due_to_employee, 2000.0)
        self.assertEqual(liq.amount_refundable_to_company, 0.0)

    def test_amount_refundable_to_company(self):
        """When advance exceeds expenses, refundable to company is positive."""
        liq = self._create_liquidation(cash_advanced=10000.0)
        self._add_line(liq, meals=3000, transport=2000)
        # grand_total = 5000, advance = 10000 -> refundable = 5000
        self.assertEqual(liq.amount_refundable_to_company, 5000.0)
        self.assertEqual(liq.amount_due_to_employee, 0.0)

    def test_exact_liquidation(self):
        """When expenses exactly match advance, both settlement fields are zero."""
        liq = self._create_liquidation(cash_advanced=5000.0)
        self._add_line(liq, meals=3000, transport=2000)
        self.assertEqual(liq.amount_due_to_employee, 0.0)
        self.assertEqual(liq.amount_refundable_to_company, 0.0)

    def test_withholding_tax_on_line(self):
        """Lines can track gross/withholding/net amounts."""
        liq = self._create_liquidation()
        line = self._add_line(liq, meals=1000)
        line.write({
            'gross_amount': 1120.0,
            'withholding_tax_amount': 120.0,
            'net_paid_amount': 1000.0,
        })
        self.assertEqual(line.gross_amount, 1120.0)
        self.assertEqual(line.withholding_tax_amount, 120.0)
