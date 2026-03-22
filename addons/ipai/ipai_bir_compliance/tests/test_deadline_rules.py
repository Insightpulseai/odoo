# -*- coding: utf-8 -*-
"""Unit tests for BIR deadline rule computation.

These tests validate the exact deadline logic from BIR form instructions:
- 0619E: 10th of next month, first two months of quarter
- 1601EQ: last day of month following quarter
- 1601C: 10th of next month, December exception (Jan 25)
- 1604C: January 31 of following year
- 1604E: March 1 of following year
- 2550Q: 25th day following quarter close
- 1701Q: Apr 15, Aug 15, Nov 15 (fixed)
- 1701: April 15 of following year
"""
from datetime import date

from odoo.tests.common import TransactionCase


class TestBirDeadlineRules(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Rule = cls.env['l10n.ph.bir.deadline.rule']

    def _get_rule(self, xmlid):
        return self.env.ref('ipai_bir_compliance.%s' % xmlid)

    # --- 0619E ---
    def test_0619e_january(self):
        """0619E for Jan period -> due Feb 10."""
        rule = self._get_rule('rule_0619e')
        due = rule.compute_due_date(date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(due, date(2026, 2, 10))

    def test_0619e_february(self):
        """0619E for Feb period -> due Mar 10."""
        rule = self._get_rule('rule_0619e')
        due = rule.compute_due_date(date(2026, 2, 1), date(2026, 2, 28))
        self.assertEqual(due, date(2026, 3, 10))

    # --- 1601EQ ---
    def test_1601eq_q1(self):
        """1601EQ for Q1 -> due Apr 30 (last day of month after quarter)."""
        rule = self._get_rule('rule_1601eq')
        due = rule.compute_due_date(date(2026, 1, 1), date(2026, 3, 31))
        self.assertEqual(due, date(2026, 4, 30))

    def test_1601eq_q2(self):
        """1601EQ for Q2 -> due Jul 31."""
        rule = self._get_rule('rule_1601eq')
        due = rule.compute_due_date(date(2026, 4, 1), date(2026, 6, 30))
        self.assertEqual(due, date(2026, 7, 31))

    # --- 1601C ---
    def test_1601c_regular_month(self):
        """1601C for March -> due Apr 10."""
        rule = self._get_rule('rule_1601c')
        due = rule.compute_due_date(date(2026, 3, 1), date(2026, 3, 31))
        self.assertEqual(due, date(2026, 4, 10))

    def test_1601c_december_exception(self):
        """1601C for December -> due Jan 25 next year (not Jan 10)."""
        rule = self._get_rule('rule_1601c')
        due = rule.compute_due_date(date(2026, 12, 1), date(2026, 12, 31))
        self.assertEqual(due, date(2027, 1, 25))

    # --- 1604C ---
    def test_1604c(self):
        """1604C for FY 2025 -> due Jan 31, 2026."""
        rule = self._get_rule('rule_1604c')
        due = rule.compute_due_date(date(2025, 1, 1), date(2025, 12, 31))
        self.assertEqual(due, date(2026, 1, 31))

    # --- 1604E ---
    def test_1604e(self):
        """1604E for FY 2025 -> due Mar 1, 2026."""
        rule = self._get_rule('rule_1604e')
        due = rule.compute_due_date(date(2025, 1, 1), date(2025, 12, 31))
        self.assertEqual(due, date(2026, 3, 1))

    # --- 2550Q ---
    def test_2550q_q1(self):
        """2550Q for Q1 -> due Apr 25."""
        rule = self._get_rule('rule_2550q')
        due = rule.compute_due_date(date(2026, 1, 1), date(2026, 3, 31))
        self.assertEqual(due, date(2026, 4, 25))

    def test_2550q_q4(self):
        """2550Q for Q4 -> due Jan 25 next year."""
        rule = self._get_rule('rule_2550q')
        due = rule.compute_due_date(date(2026, 10, 1), date(2026, 12, 31))
        self.assertEqual(due, date(2027, 1, 25))

    # --- 1701Q ---
    def test_1701q_q1(self):
        """1701Q Q1 -> due Apr 15."""
        rule = self._get_rule('rule_1701q')
        due = rule.compute_due_date(date(2026, 1, 1), date(2026, 3, 31))
        self.assertEqual(due, date(2026, 4, 15))

    def test_1701q_q2(self):
        """1701Q Q2 -> due Aug 15."""
        rule = self._get_rule('rule_1701q')
        due = rule.compute_due_date(date(2026, 4, 1), date(2026, 6, 30))
        self.assertEqual(due, date(2026, 8, 15))

    def test_1701q_q3(self):
        """1701Q Q3 -> due Nov 15."""
        rule = self._get_rule('rule_1701q')
        due = rule.compute_due_date(date(2026, 7, 1), date(2026, 9, 30))
        self.assertEqual(due, date(2026, 11, 15))

    # --- 1701 ---
    def test_1701_annual(self):
        """1701 for FY 2025 -> due Apr 15, 2026."""
        rule = self._get_rule('rule_1701')
        due = rule.compute_due_date(date(2025, 1, 1), date(2025, 12, 31))
        self.assertEqual(due, date(2026, 4, 15))
