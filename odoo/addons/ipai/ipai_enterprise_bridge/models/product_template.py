# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    """Retail/grocery overlay fields for Scout vertical."""

    _inherit = "product.template"

    # Scout retail fields
    ipai_is_grocery = fields.Boolean(
        string="Is Grocery Item",
        default=False,
        help="Mark as grocery/FMCG item for Scout tracking",
    )
    ipai_shelf_code = fields.Char(
        string="Shelf Code",
        help="Shelf/aisle location code for retail stores",
    )
    ipai_expiry_required = fields.Boolean(
        string="Expiry Required",
        default=False,
        help="Requires expiry date tracking",
    )
    ipai_substitution_group_id = fields.Many2one(
        "ipai.substitution.group",
        string="Substitution Group",
        help="Group of products that can substitute this item",
    )


class IpaiSubstitutionGroup(models.Model):
    """Product substitution groups for retail."""

    _name = "ipai.substitution.group"
    _description = "Product Substitution Group"

    name = fields.Char(string="Group Name", required=True)
    product_ids = fields.One2many(
        "product.template",
        "ipai_substitution_group_id",
        string="Products",
    )
    priority_order = fields.Text(
        string="Priority Order",
        help="JSON list of product IDs in substitution priority order",
    )
    active = fields.Boolean(default=True)
