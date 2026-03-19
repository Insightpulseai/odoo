# -*- coding: utf-8 -*-
# Copyright (C) InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.en.html).

from odoo import fields, models


class FinanceRole(models.Model):
    """Finance workflow roles for task assignment."""

    _name = "ipai.finance.role"
    _description = "Finance Workflow Role"
    _order = "sequence, name"

    name = fields.Char(string="Role Name", required=True)
    code = fields.Char(
        string="Code",
        required=True,
        help="Short code for role (e.g., CKVC, RIM, BOM)",
    )
    sequence = fields.Integer(default=10)
    description = fields.Text(string="Description")
    user_ids = fields.Many2many(
        "res.users",
        "finance_role_user_rel",
        "role_id",
        "user_id",
        string="Assigned Users",
    )
    employee_ids = fields.Many2many(
        "hr.employee",
        "finance_role_employee_rel",
        "role_id",
        "employee_id",
        string="Assigned Employees",
    )
    role_type = fields.Selection(
        [
            ("director", "Finance Director"),
            ("senior_manager", "Senior Finance Manager"),
            ("supervisor", "Finance Supervisor"),
            ("accountant", "Accountant"),
            ("specialist", "Specialist"),
        ],
        string="Role Type",
        required=True,
        default="accountant",
    )
    can_approve = fields.Boolean(
        string="Can Approve",
        default=False,
        help="User with this role can approve finance tasks.",
    )
    can_review = fields.Boolean(
        string="Can Review",
        default=False,
        help="User with this role can review finance tasks.",
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_unique", "unique(code)", "Role code must be unique!"),
    ]


class ResUsers(models.Model):
    """Extend users with finance role."""

    _inherit = "res.users"

    finance_role_ids = fields.Many2many(
        "ipai.finance.role",
        "finance_role_user_rel",
        "user_id",
        "role_id",
        string="Finance Roles",
    )
    finance_code = fields.Char(
        string="Finance Code",
        help="Short identifier code for finance workflows (e.g., CKVC, RIM)",
    )
