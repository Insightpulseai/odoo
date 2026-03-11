# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing.

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class HrEmployee(models.Model):
    """Extend employee with Philippine statutory fields."""

    _inherit = "hr.employee"

    # BIR Tax Information
    bir_tin = fields.Char(
        string="TIN",
        help="Bureau of Internal Revenue Tax Identification Number (XXX-XXX-XXX-XXX)",
    )
    bir_rdo = fields.Char(
        string="RDO Code",
        help="Revenue District Office code",
    )
    bir_tax_status = fields.Selection(
        [
            ("S", "Single"),
            ("S1", "Single with 1 dependent"),
            ("S2", "Single with 2 dependents"),
            ("S3", "Single with 3 dependents"),
            ("S4", "Single with 4 dependents"),
            ("ME", "Married (claiming exemption)"),
            ("ME1", "Married with 1 dependent"),
            ("ME2", "Married with 2 dependents"),
            ("ME3", "Married with 3 dependents"),
            ("ME4", "Married with 4 dependents"),
            ("Z", "Zero exemption (minimum wage earner)"),
        ],
        string="Tax Status",
        default="S",
        help="BIR withholding tax status for TRAIN Law computation",
    )

    # SSS Information
    sss_number = fields.Char(
        string="SSS Number",
        help="Social Security System number (XX-XXXXXXX-X)",
    )
    sss_contribution_type = fields.Selection(
        [
            ("regular", "Regular Employee"),
            ("kasambahay", "Kasambahay"),
            ("ofw", "OFW"),
            ("self_employed", "Self-Employed"),
            ("voluntary", "Voluntary"),
        ],
        string="SSS Type",
        default="regular",
    )

    # PhilHealth Information
    philhealth_number = fields.Char(
        string="PhilHealth Number",
        help="Philippine Health Insurance Corporation number",
    )
    philhealth_category = fields.Selection(
        [
            ("employed", "Employed"),
            ("kasambahay", "Kasambahay"),
            ("self_employed", "Self-Employed"),
            ("ofw", "OFW"),
            ("senior", "Senior Citizen"),
            ("pwd", "Person with Disability"),
        ],
        string="PhilHealth Category",
        default="employed",
    )

    # Pag-IBIG Information
    pagibig_number = fields.Char(
        string="Pag-IBIG MID Number",
        help="Home Development Mutual Fund Member ID",
    )
    pagibig_contribution_type = fields.Selection(
        [
            ("regular", "Regular (2%)"),
            ("modified_1", "Modified Pag-IBIG 1"),
            ("modified_2", "Modified Pag-IBIG 2"),
        ],
        string="Pag-IBIG Type",
        default="regular",
    )

    # Payroll Bank Information
    bank_account_id = fields.Many2one(
        "res.partner.bank",
        string="Salary Bank Account",
        domain="[('partner_id', '=', address_home_id)]",
    )

    @api.constrains("bir_tin")
    def _check_tin_format(self):
        """Validate TIN format: XXX-XXX-XXX-XXX."""
        tin_pattern = r"^\d{3}-\d{3}-\d{3}-\d{3}$"
        for employee in self:
            if employee.bir_tin and not re.match(tin_pattern, employee.bir_tin):
                raise ValidationError(
                    f"Invalid TIN format for {employee.name}. "
                    "Expected format: XXX-XXX-XXX-XXX"
                )

    @api.constrains("sss_number")
    def _check_sss_format(self):
        """Validate SSS number format: XX-XXXXXXX-X."""
        sss_pattern = r"^\d{2}-\d{7}-\d{1}$"
        for employee in self:
            if employee.sss_number and not re.match(sss_pattern, employee.sss_number):
                raise ValidationError(
                    f"Invalid SSS number format for {employee.name}. "
                    "Expected format: XX-XXXXXXX-X"
                )
