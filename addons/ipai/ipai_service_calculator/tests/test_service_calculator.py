from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestServicePack(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Consulting Hour",
                "type": "service",
                "list_price": 150.0,
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Development Hour",
                "type": "service",
                "list_price": 200.0,
            }
        )
        cls.pack = cls.env["ipai.service.pack"].create(
            {
                "name": "Starter Pack",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_a.id,
                            "name": "Consulting",
                            "quantity": 10,
                            "price_unit": 150.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_b.id,
                            "name": "Development",
                            "quantity": 20,
                            "price_unit": 200.0,
                        },
                    ),
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})

    def test_pack_creation(self):
        """Pack created with 2 lines."""
        self.assertEqual(len(self.pack.line_ids), 2)
        self.assertTrue(self.pack.active)
        self.assertEqual(self.pack.line_ids[0].price_unit, 150.0)

    def test_action_open_calculator(self):
        """action_open_calculator returns wizard action with pack context."""
        action = self.pack.action_open_calculator()
        self.assertEqual(action["res_model"], "ipai.service.calculator.wizard")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["context"]["default_pack_id"], self.pack.id)

    def test_wizard_apply_to_draft_order(self):
        """Wizard applies pack lines to a draft sale order."""
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id}
        )
        wizard = self.env["ipai.service.calculator.wizard"].create(
            {
                "pack_id": self.pack.id,
                "sale_order_id": order.id,
                "multiplier": 1.0,
            }
        )
        # Simulate onchange to populate preview lines
        wizard._onchange_pack_id()
        self.assertEqual(len(wizard.preview_line_ids), 2)

        wizard.action_apply()
        self.assertEqual(len(order.order_line), 2)
        self.assertEqual(order.order_line[0].product_uom_qty, 10)
        self.assertEqual(order.order_line[1].product_uom_qty, 20)

    def test_wizard_multiplier(self):
        """Multiplier scales preview line quantities."""
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id}
        )
        wizard = self.env["ipai.service.calculator.wizard"].create(
            {
                "pack_id": self.pack.id,
                "sale_order_id": order.id,
                "multiplier": 2.5,
            }
        )
        wizard._onchange_pack_id()
        self.assertEqual(wizard.preview_line_ids[0].quantity, 25.0)
        self.assertEqual(wizard.preview_line_ids[1].quantity, 50.0)

    def test_wizard_subtotal_compute(self):
        """Preview line subtotal = quantity * price_unit."""
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id}
        )
        wizard = self.env["ipai.service.calculator.wizard"].create(
            {
                "pack_id": self.pack.id,
                "sale_order_id": order.id,
                "multiplier": 1.0,
            }
        )
        wizard._onchange_pack_id()
        line = wizard.preview_line_ids[0]
        self.assertEqual(line.subtotal, 10 * 150.0)

    def test_wizard_no_order_raises(self):
        """Applying without a sale order raises UserError."""
        wizard = self.env["ipai.service.calculator.wizard"].create(
            {
                "pack_id": self.pack.id,
                "multiplier": 1.0,
            }
        )
        with self.assertRaises(UserError):
            wizard.action_apply()

    def test_wizard_confirmed_order_raises(self):
        """Applying to a confirmed order raises UserError."""
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id}
        )
        order.action_confirm()
        wizard = self.env["ipai.service.calculator.wizard"].create(
            {
                "pack_id": self.pack.id,
                "sale_order_id": order.id,
                "multiplier": 1.0,
            }
        )
        wizard._onchange_pack_id()
        with self.assertRaises(UserError):
            wizard.action_apply()

    def test_wizard_sets_order_type(self):
        """If pack has a sale_order_type, it is applied to the SO."""
        SaleOrderType = self.env.get("sale.order.type")
        if not SaleOrderType:
            return  # sale_order_type not installed
        order_type = SaleOrderType.create({"name": "Service Project"})
        self.pack.sale_order_type_id = order_type
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id}
        )
        wizard = self.env["ipai.service.calculator.wizard"].create(
            {
                "pack_id": self.pack.id,
                "sale_order_id": order.id,
                "multiplier": 1.0,
            }
        )
        wizard._onchange_pack_id()
        wizard.action_apply()
        self.assertEqual(order.type_id, order_type)
