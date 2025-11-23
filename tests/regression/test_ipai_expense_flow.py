from odoo.tests.common import TransactionCase, tagged

@tagged('post_install', 'regression', '-at_install')
class TestIpaiExpenseFlow(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Expense = self.env['hr.expense']

    def test_create_basic_expense(self):
        expense = self.Expense.create({
            'name': 'Test Taxi',
            'total_amount': 500.0,
        })
        self.assertTrue(expense.id)
        self.assertEqual(expense.name, 'Test Taxi')
