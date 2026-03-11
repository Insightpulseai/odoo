# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing.

from odoo import models, fields


class HrSalaryRuleCategory(models.Model):
    """Salary rule categories for payslip organization."""

    _name = "hr.salary.rule.category"
    _description = "Salary Rule Category"
    _order = "sequence"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    parent_id = fields.Many2one("hr.salary.rule.category", string="Parent")
    note = fields.Text(string="Description")


class HrSalaryRule(models.Model):
    """Salary rules for payslip computation."""

    _name = "hr.salary.rule"
    _description = "Salary Rule"
    _order = "sequence"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    category_id = fields.Many2one("hr.salary.rule.category", required=True)

    condition_select = fields.Selection(
        [
            ("none", "Always True"),
            ("python", "Python Expression"),
        ],
        string="Condition Based on",
        default="none",
    )
    condition_python = fields.Text(
        string="Python Condition",
        help="Python expression that evaluates to True or False",
    )

    amount_select = fields.Selection(
        [
            ("fix", "Fixed Amount"),
            ("percentage", "Percentage (%)"),
            ("code", "Python Code"),
        ],
        string="Amount Type",
        default="fix",
    )
    amount_fix = fields.Float(string="Fixed Amount")
    amount_percentage = fields.Float(string="Percentage (%)")
    amount_percentage_base = fields.Char(string="Percentage Based on")
    amount_python_compute = fields.Text(
        string="Python Code",
        help="Python code that computes the rule amount",
    )

    note = fields.Html(string="Description")
    active = fields.Boolean(default=True)

    # PH Statutory Categories
    is_sss = fields.Boolean(string="SSS Contribution")
    is_philhealth = fields.Boolean(string="PhilHealth Contribution")
    is_pagibig = fields.Boolean(string="Pag-IBIG Contribution")
    is_bir = fields.Boolean(string="BIR Withholding Tax")
