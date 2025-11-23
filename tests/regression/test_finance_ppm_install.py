from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', 'regression', '-at_install')
class TestFinancePpmInstall(TransactionCase):

    def test_module_loaded(self):
        module = self.env['ir.module.module'].search(
            [('name', '=', 'ipai_finance_ppm')], limit=1
        )
        self.assertTrue(module, "Module ipai_finance_ppm should exist in registry")
        self.assertEqual(module.state, 'installed')
