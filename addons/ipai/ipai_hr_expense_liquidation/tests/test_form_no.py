# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestLiquidationFormNo(TransactionCase):
    """Tests for Form No. (liquidation.name) binding and report-date field."""

    def setUp(self):
        super().setUp()
        self.employee = self.env.ref("hr.employee_admin")
        self.Liq = self.env["hr.expense.liquidation"]

    def _make_liquidation(self, **kwargs):
        vals = {
            "employee_id": self.employee.id,
            "liquidation_type": "cash_advance",
            "date": date.today(),
        }
        vals.update(kwargs)
        return self.Liq.create(vals)

    def test_liquidation_report_date_default(self):
        """liquidation_report_date defaults to today on new record."""
        liq = self._make_liquidation()
        self.assertEqual(liq.liquidation_report_date, date.today())

    def test_cash_advance_form_no_related(self):
        """cash_advance_form_no on hr.expense mirrors liquidation name."""
        liq = self._make_liquidation()
        expense = self.env["hr.expense"].create({
            "name": "Test Expense",
            "employee_id": self.employee.id,
            "product_id": self.env.ref("hr_expense.product_product_fixed_cost").id,
            "total_amount": 100.0,
            "cash_advance_liquidation_id": liq.id,
        })
        self.assertEqual(expense.cash_advance_form_no, liq.name)
        self.assertTrue(liq.name.startswith("LIQ/"))

    def test_single_advance_per_sheet_constraint(self):
        """Two different liquidation references on one expense sheet raise ValidationError."""
        liq1 = self._make_liquidation()
        liq2 = self._make_liquidation()

        product = self.env.ref("hr_expense.product_product_fixed_cost")
        expense1 = self.env["hr.expense"].create({
            "name": "Expense A",
            "employee_id": self.employee.id,
            "product_id": product.id,
            "total_amount": 50.0,
            "cash_advance_liquidation_id": liq1.id,
        })
        expense2 = self.env["hr.expense"].create({
            "name": "Expense B",
            "employee_id": self.employee.id,
            "product_id": product.id,
            "total_amount": 75.0,
            "cash_advance_liquidation_id": liq2.id,
        })

        with self.assertRaises(ValidationError):
            self.env["hr.expense.sheet"].create({
                "name": "Sheet with two LIQ forms",
                "employee_id": self.employee.id,
                "expense_line_ids": [(4, expense1.id), (4, expense2.id)],
            })
