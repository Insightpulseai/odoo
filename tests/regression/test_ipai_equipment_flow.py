from odoo.tests.common import TransactionCase, tagged

@tagged('post_install', 'regression', '-at_install')
class TestIpaiEquipmentFlow(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Equipment = self.env['ipai.equipment']

    def test_create_basic_equipment(self):
        eq = self.Equipment.create({
            'name': 'Test Camera',
            'code': 'CAM-TEST-001',
        })
        self.assertTrue(eq.id)
        self.assertEqual(eq.name, 'Test Camera')
