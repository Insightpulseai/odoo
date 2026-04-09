from odoo import _, api, fields, models


class IpaiServicePack(models.Model):
    _name = "ipai.service.pack"
    _description = "Service Pack Template"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Html()
    line_ids = fields.One2many(
        "ipai.service.pack.line", "pack_id", string="Pack Lines"
    )
    sale_order_type_id = fields.Many2one(
        "sale.order.type", string="Sale Order Type"
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
    )

    def action_open_calculator(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Apply Service Pack"),
            "res_model": "ipai.service.calculator.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_pack_id": self.id},
        }


class IpaiServicePackLine(models.Model):
    _name = "ipai.service.pack.line"
    _description = "Service Pack Line"
    _order = "sequence"

    pack_id = fields.Many2one(
        "ipai.service.pack", required=True, ondelete="cascade"
    )
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain=[("type", "=", "service")],
    )
    name = fields.Char(string="Description")
    quantity = fields.Float(default=1.0)
    price_unit = fields.Float(string="Unit Price")

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.price_unit = self.product_id.list_price
