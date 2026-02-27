# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestLiquidationFormNo(TransactionCase):
    """Tests for Form No. (liquidation.name) binding, report-date field,
    and cross-scope constraints."""

    def setUp(self):
        super().setUp()
        self.employee = self.env.ref("hr.employee_admin")
        self.product = self.env.ref("hr_expense.product_product_fixed_cost")
        self.Liq = self.env["hr.expense.liquidation"]

    def _make_liquidation(self, employee=None, **kwargs):
        vals = {
            "employee_id": (employee or self.employee).id,
            "liquidation_type": "cash_advance",
            "date": date.today(),
        }
        vals.update(kwargs)
        return self.Liq.create(vals)

    def _make_expense(self, liquidation=None, employee=None, **kwargs):
        vals = {
            "name": "Test Expense",
            "employee_id": (employee or self.employee).id,
            "product_id": self.product.id,
            "total_amount": 100.0,
        }
        if liquidation:
            vals["cash_advance_liquidation_id"] = liquidation.id
        vals.update(kwargs)
        return self.env["hr.expense"].create(vals)

    # ------------------------------------------------------------------
    # Form No. / Date Prepared
    # ------------------------------------------------------------------

    def test_liquidation_report_date_default(self):
        """liquidation_report_date defaults to today on new record."""
        liq = self._make_liquidation()
        self.assertEqual(liq.liquidation_report_date, date.today())

    def test_cash_advance_form_no_related(self):
        """cash_advance_form_no on hr.expense mirrors liquidation name."""
        liq = self._make_liquidation()
        expense = self._make_expense(liquidation=liq)
        self.assertEqual(expense.cash_advance_form_no, liq.name)
        self.assertTrue(liq.name.startswith("LIQ/"))

    # ------------------------------------------------------------------
    # Sheet constraint
    # ------------------------------------------------------------------

    def test_single_advance_per_sheet_constraint(self):
        """Two different liquidation references on one expense sheet raise ValidationError."""
        liq1 = self._make_liquidation()
        liq2 = self._make_liquidation()
        expense1 = self._make_expense(liquidation=liq1, name="Expense A")
        expense2 = self._make_expense(liquidation=liq2, name="Expense B")
        with self.assertRaises(ValidationError):
            self.env["hr.expense.sheet"].create({
                "name": "Sheet two LIQ forms",
                "employee_id": self.employee.id,
                "expense_line_ids": [(4, expense1.id), (4, expense2.id)],
            })

    # ------------------------------------------------------------------
    # Cross-scope constraints
    # ------------------------------------------------------------------

    def test_expense_employee_mismatch_raises(self):
        """Linking an expense to a liquidation owned by a different employee raises ValidationError."""
        other_emp = self.env["hr.employee"].create({"name": "Other Employee"})
        liq = self._make_liquidation()  # employee = self.employee
        with self.assertRaises(ValidationError):
            self._make_expense(liquidation=liq, employee=other_emp, name="Wrong Employee")

    def test_expense_company_match_passes(self):
        """Linking an expense to a liquidation in the same company succeeds."""
        liq = self._make_liquidation()
        expense = self._make_expense(liquidation=liq, name="Same Company OK")
        self.assertEqual(expense.cash_advance_liquidation_id, liq)

    def test_form_no_is_readonly_sequence(self):
        """Form No. (LIQ/YYYY/####) is system-assigned and non-empty."""
        liq = self._make_liquidation()
        self.assertRegex(liq.name, r"^LIQ/\d{4}/\d+$")
