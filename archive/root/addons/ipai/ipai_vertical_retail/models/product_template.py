# -*- coding: utf-8 -*-
# Copyright (C) InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    scout_category = fields.Selection(
        [
            ("dairy", "Dairy"),
            ("snacks", "Snacks"),
            ("beverage", "Beverage"),
            ("tobacco", "Tobacco"),
            ("cleaning", "Home Cleaning"),
            ("personal_care", "Personal Care"),
            ("frozen", "Frozen Foods"),
            ("canned", "Canned Goods"),
            ("condiments", "Condiments & Sauces"),
            ("instant", "Instant Noodles & Meals"),
            ("baby", "Baby Products"),
            ("health", "Health & Wellness"),
            ("other", "Other"),
        ],
        string="Scout Category",
        help="High-level FMCG category used by Scout Analytics.",
    )
    scout_subcategory = fields.Char(
        string="Scout Subcategory",
        help="Detailed subcategory for Scout reporting.",
    )
    scout_brand = fields.Char(
        string="Brand Name (Scout)",
        help="Brand label for Scout; may differ from product's internal brand.",
    )
    scout_manufacturer = fields.Char(
        string="Manufacturer (Scout)",
        help="Manufacturer name as used in Scout analytics.",
    )
    scout_is_competitor = fields.Boolean(
        string="Competitor Brand",
        help="Tick if this product belongs to a competitor brand.",
    )
    scout_is_focus_sku = fields.Boolean(
        string="Focus SKU",
        help="Mark as focus SKU for priority tracking in Scout.",
    )
    scout_pack_size = fields.Char(
        string="Pack Size",
        help="Pack size descriptor for Scout (e.g., '12x500ml', '24pcs').",
    )
    scout_srp = fields.Float(
        string="Suggested Retail Price",
        digits="Product Price",
        help="Recommended SRP for Scout price monitoring.",
    )
    scout_min_order_qty = fields.Float(
        string="Min Order Qty",
        help="Minimum order quantity for retail outlets.",
    )
    scout_shelf_life_days = fields.Integer(
        string="Shelf Life (Days)",
        help="Product shelf life in days for inventory management.",
    )
