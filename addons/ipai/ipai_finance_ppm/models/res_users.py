# -*- coding: utf-8 -*-
"""
res.users Extension for Employee Code Mapping
==============================================

Adds x_employee_code field to res.users for generator assignment resolution.

Assignment Resolution Flow:
    Seed JSON employee_code → res.users.x_employee_code → res.users.id → project.task.user_ids

Example:
    Seed: "employee_code": "RIM"
    Lookup: env['res.users'].search([('x_employee_code', '=', 'RIM')])
    Assign: task.user_ids = [(4, user.id)]
"""

from odoo import api, fields, models


class ResUsers(models.Model):
    """
    Extension of res.users for generator integration
    """

    _inherit = "res.users"

    x_employee_code = fields.Char(
        string="Employee Code",
        index=True,
        help="Unique employee identifier for generator assignment (e.g., RIM, CKVC, BOM, JPAL)",
    )

    _sql_constraints = [
        (
            "x_employee_code_uniq",
            "UNIQUE(x_employee_code)",
            "Employee code must be unique",
        )
    ]

    @api.model
    def resolve_employee_code(self, employee_code):
        """
        Resolve employee code to user ID for generator

        Args:
            employee_code (str): Employee code from seed JSON (e.g., 'RIM')

        Returns:
            int|bool: User ID if found, False otherwise
        """
        if not employee_code:
            return False

        user = self.search([("x_employee_code", "=", employee_code)], limit=1)
        return user.id if user else False
