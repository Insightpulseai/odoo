import re
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    """Extend res.partner with Philippine TIN"""
    _inherit = "res.partner"

    tin = fields.Char(
        string="TIN",
        help="Philippine Tax Identification Number (XXX-XXX-XXX-XXX format)",
        index=True,
    )
    tin_branch_code = fields.Char(
        string="Branch Code",
        size=5,
        help="BIR branch code (for businesses with multiple branches)",
    )
    bir_registered = fields.Boolean(
        string="BIR Registered",
        default=False,
    )
    bir_registration_date = fields.Date(
        string="BIR Registration Date",
    )
    tax_type = fields.Selection([
        ("individual", "Individual"),
        ("sole_proprietor", "Sole Proprietor"),
        ("corporation", "Corporation"),
        ("partnership", "Partnership"),
        ("cooperative", "Cooperative"),
        ("government", "Government"),
        ("non_profit", "Non-Profit"),
    ], string="Tax Type", default="individual")

    @api.constrains("tin")
    def _check_tin_format(self):
        """Validate Philippine TIN format: XXX-XXX-XXX-XXX"""
        tin_pattern = re.compile(r"^\d{3}-\d{3}-\d{3}-\d{3}$")
        for rec in self:
            if rec.tin and not tin_pattern.match(rec.tin):
                raise ValidationError(
                    "Invalid TIN format. Use XXX-XXX-XXX-XXX (e.g., 123-456-789-000)"
                )

    @api.onchange("tin")
    def _onchange_tin_format(self):
        """Auto-format TIN as user types"""
        if self.tin:
            digits = re.sub(r"\D", "", self.tin)
            if len(digits) >= 12:
                self.tin = f"{digits[:3]}-{digits[3:6]}-{digits[6:9]}-{digits[9:12]}"
