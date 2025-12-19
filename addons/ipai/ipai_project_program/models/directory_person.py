# -*- coding: utf-8 -*-
"""Finance Directory Person model for role-based task assignment."""
from odoo import fields, models


class IPAIDirectoryPerson(models.Model):
    _name = "ipai.directory.person"
    _description = "Finance Directory Person (Code/Name/Email/Role)"
    _rec_name = "code"
    _order = "code"

    code = fields.Char(
        string="Code",
        required=True,
        index=True,
        help="Unique identifier code (e.g., RIM, BOM, CKVC)",
    )
    name = fields.Char(
        string="Full Name",
        required=True,
    )
    email = fields.Char(
        string="Email",
        help="Email address for matching to res.users",
    )
    role = fields.Char(
        string="Role",
        help="Job title or role description",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Linked User",
        compute="_compute_user_id",
        store=False,
        help="Automatically resolved Odoo user based on email",
    )

    _sql_constraints = [
        ("code_unique", "unique(code)", "Directory code must be unique!"),
    ]

    def _compute_user_id(self):
        """Resolve directory person to Odoo user by email."""
        Users = self.env["res.users"].sudo()
        for rec in self:
            if rec.email:
                user = Users.search([("login", "=", rec.email)], limit=1)
                if not user:
                    user = Users.search([("email", "=", rec.email)], limit=1)
                rec.user_id = user
            else:
                rec.user_id = False
