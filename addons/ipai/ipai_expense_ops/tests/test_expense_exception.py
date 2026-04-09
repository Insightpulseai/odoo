from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged("post_install", "-at_install")
class TestExpenseException(TransactionCase):
    """Test expense exception model and approval blocking gate."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create({
            "name": "Test Employee",
        })
        cls.product = cls.env.ref(
            "hr_expense.product_product_fixed_cost",
            raise_if_not_found=False,
        )
        if not cls.product:
            cls.product = cls.env["product.product"].create({
                "name": "Fixed Cost",
                "can_be_expensed": True,
            })

    def _create_sheet_with_expense(self):
        expense = self.env["hr.expense"].create({
            "name": "Test Expense",
            "employee_id": self.employee.id,
            "product_id": self.product.id,
            "total_amount_currency": 100.0,
        })
        sheet = self.env["hr.expense.sheet"].create({
            "name": "Test Report",
            "employee_id": self.employee.id,
            "expense_line_ids": [(4, expense.id)],
        })
        return sheet

    def test_exception_create_and_resolve(self):
        sheet = self._create_sheet_with_expense()
        exc = self.env["ipai.expense.exception"].create({
            "exception_code": "RECEIPT_MISSING",
            "message": "Receipt not attached",
            "is_blocking": True,
            "sheet_id": sheet.id,
        })
        self.assertEqual(exc.state, "new")
        self.assertEqual(sheet.blocking_exception_count, 1)

        exc.action_resolve()
        self.assertEqual(exc.state, "resolved")
        self.assertEqual(sheet.blocking_exception_count, 0)

    def test_blocking_exception_prevents_approval(self):
        sheet = self._create_sheet_with_expense()
        self.env["ipai.expense.exception"].create({
            "exception_code": "AMOUNT_LIMIT",
            "message": "Exceeds daily limit",
            "is_blocking": True,
            "sheet_id": sheet.id,
        })

        # Submit first
        sheet.action_submit_sheet()

        with self.assertRaises(UserError):
            sheet.action_approve_expense_sheets()

    def test_non_blocking_exception_allows_approval(self):
        sheet = self._create_sheet_with_expense()
        self.env["ipai.expense.exception"].create({
            "exception_code": "MEMO_MISSING",
            "message": "Business purpose not provided",
            "is_blocking": False,
            "sheet_id": sheet.id,
        })

        sheet.action_submit_sheet()
        # Non-blocking should not raise
        sheet.action_approve_expense_sheets()
        self.assertEqual(sheet.state, "approve")

    def test_waive_exception(self):
        sheet = self._create_sheet_with_expense()
        exc = self.env["ipai.expense.exception"].create({
            "exception_code": "TEST",
            "message": "Test exception",
            "is_blocking": True,
            "sheet_id": sheet.id,
        })
        exc.action_waive()
        self.assertEqual(exc.state, "waived")
        self.assertEqual(sheet.blocking_exception_count, 0)
