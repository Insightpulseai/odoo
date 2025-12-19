# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResUsers(models.Model):
    """
    Extend res.users with employee code for finance team assignment resolution.

    The x_employee_code field is used by the closing task generator to resolve
    assignments from seed JSON to actual Odoo users.
    """

    _inherit = "res.users"

    x_employee_code = fields.Char(
        string="Employee Code",
        index=True,
        help="Unique code for task assignment resolution (e.g., CKVC, RIM, BOM).",
    )

    _sql_constraints = [
        (
            "x_employee_code_unique",
            "unique(x_employee_code)",
            "Employee code must be unique when set!",
        )
    ]
