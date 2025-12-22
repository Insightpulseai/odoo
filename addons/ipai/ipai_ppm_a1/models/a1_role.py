# -*- coding: utf-8 -*-
"""
A1 Role Configuration

Maps role codes (RIM, JPAL, BOM, CKVC, etc.) to Odoo groups and default users.
Provides the canonical resolver for role → user assignment.
"""
from odoo import api, fields, models


class A1Role(models.Model):
    """
    Role configuration for A1 Control Center.

    Maps role codes to Odoo groups and provides default assignee resolution.
    """

    _name = "a1.role"
    _description = "A1 Role Configuration"
    _order = "sequence, code"

    _sql_constraints = [
        (
            "code_uniq",
            "unique(code, company_id)",
            "Role code must be unique per company.",
        ),
    ]

    # Core fields
    code = fields.Char(
        string="Role Code",
        required=True,
        index=True,
        help="Short code like RIM, JPAL, BOM, CKVC, FD",
    )
    name = fields.Char(
        string="Role Name",
        required=True,
        help="Full name like 'RIM - Rent & Leases Manager'",
    )
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)

    # Assignment
    group_ids = fields.Many2many(
        "res.groups",
        string="Linked Groups",
        help="Odoo groups associated with this role",
    )
    default_user_id = fields.Many2one(
        "res.users",
        string="Default Assignee",
        help="Default user when role assignment is unresolved",
    )
    fallback_user_id = fields.Many2one(
        "res.users",
        string="Fallback User",
        help="User to assign when default user is unavailable",
    )

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    # Description
    description = fields.Text(
        string="Description",
        help="Detailed description of role responsibilities",
    )

    @api.model
    def resolve_user(self, role_code, company_id=None):
        """
        Resolve role code to user ID.

        Args:
            role_code: The role code (e.g., 'RIM', 'JPAL')
            company_id: Optional company ID (defaults to current company)

        Returns:
            res.users record or False
        """
        if not role_code:
            return False

        company_id = company_id or self.env.company.id

        role = self.search(
            [
                ("code", "=", role_code),
                ("company_id", "=", company_id),
            ],
            limit=1,
        )

        if not role:
            return False

        # Return default user, or fallback, or first user from linked groups
        if role.default_user_id:
            return role.default_user_id
        if role.fallback_user_id:
            return role.fallback_user_id
        if role.group_ids:
            user = self.env["res.users"].search(
                [
                    ("groups_id", "in", role.group_ids.ids),
                    ("company_id", "=", company_id),
                ],
                limit=1,
            )
            if user:
                return user
        return False

    @api.model
    def resolve_users(self, role_code, company_id=None):
        """
        Resolve role code to all matching users.

        Args:
            role_code: The role code
            company_id: Optional company ID

        Returns:
            res.users recordset
        """
        if not role_code:
            return self.env["res.users"]

        company_id = company_id or self.env.company.id

        role = self.search(
            [
                ("code", "=", role_code),
                ("company_id", "=", company_id),
            ],
            limit=1,
        )

        if not role:
            return self.env["res.users"]

        users = self.env["res.users"]
        if role.default_user_id:
            users |= role.default_user_id
        if role.group_ids:
            users |= self.env["res.users"].search(
                [
                    ("groups_id", "in", role.group_ids.ids),
                    ("company_id", "=", company_id),
                ]
            )
        return users
