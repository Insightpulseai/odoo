from odoo import _, api, fields, models
from odoo.exceptions import UserError


class IpaiServiceCalculatorWizard(models.TransientModel):
    _name = "ipai.service.calculator.wizard"
    _description = "Service Pack Calculator"

    pack_id = fields.Many2one(
        "ipai.service.pack", required=True, string="Service Pack"
    )
    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
    partner_id = fields.Many2one(
        "res.partner",
        related="sale_order_id.partner_id",
        readonly=True,
    )
    multiplier = fields.Float(
        default=1.0,
        string="Quantity Multiplier",
        help="Multiply all pack line quantities by this factor",
    )
    preview_line_ids = fields.One2many(
        "ipai.service.calculator.wizard.line",
        "wizard_id",
        string="Preview Lines",
    )

    @api.onchange("pack_id", "multiplier")
    def _onchange_pack_id(self):
        lines = []
        if self.pack_id:
            for pl in self.pack_id.line_ids:
                lines.append(
                    (
                        0,
                        0,
                        {
                            "product_id": pl.product_id.id,
                            "name": pl.name or pl.product_id.display_name,
                            "quantity": pl.quantity * (self.multiplier or 1.0),
                            "price_unit": pl.price_unit,
                        },
                    )
                )
        self.preview_line_ids = [(5, 0, 0)] + lines

    def action_apply(self):
        self.ensure_one()
        if not self.sale_order_id:
            raise UserError(_("Please select a Sale Order first."))
        if self.sale_order_id.state != "draft":
            raise UserError(
                _("Can only apply service packs to draft quotations.")
            )
        order = self.sale_order_id
        for line in self.preview_line_ids:
            order.write(
                {
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": line.product_id.id,
                                "name": line.name,
                                "product_uom_qty": line.quantity,
                                "price_unit": line.price_unit,
                            },
                        )
                    ]
                }
            )
        if self.pack_id.sale_order_type_id:
            order.type_id = self.pack_id.sale_order_type_id
        return {"type": "ir.actions.act_window_close"}


class IpaiServiceCalculatorWizardLine(models.TransientModel):
    _name = "ipai.service.calculator.wizard.line"
    _description = "Service Pack Calculator Preview Line"

    wizard_id = fields.Many2one(
        "ipai.service.calculator.wizard", ondelete="cascade"
    )
    product_id = fields.Many2one("product.product", readonly=True)
    name = fields.Char()
    quantity = fields.Float()
    price_unit = fields.Float()
    subtotal = fields.Float(compute="_compute_subtotal")

    @api.depends("quantity", "price_unit")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.price_unit
