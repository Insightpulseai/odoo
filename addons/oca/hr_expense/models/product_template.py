# Copyright 2024 IPAI - InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    """Extend product template with expense capability."""

    _inherit = "product.template"

    can_be_expensed = fields.Boolean(
        string="Can be Expensed",
        help="Check this box if this product can be used as an expense type.",
    )
