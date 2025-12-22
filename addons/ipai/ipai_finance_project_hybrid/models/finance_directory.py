# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FinanceDirectory(models.Model):
    _name = "ipai.finance.directory"
    _description = "Finance Directory (code → person)"
    _order = "code"

    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    email = fields.Char(index=True)
    user_id = fields.Many2one(
        "res.users", string="User", help="Optional link to an Odoo user."
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Directory code must be unique."),
    ]

    @api.constrains("email")
    def _check_email(self):
        for rec in self:
            if rec.email and "@" not in rec.email:
                raise ValidationError(_("Invalid email for %s") % rec.code)

    @api.model
    def _upsert_from_seed(self, row: dict, strict: bool = False):
        code = (row or {}).get("code")
        if not code:
            if strict:
                raise ValidationError(_("Seed directory row missing code."))
            return False
        vals = {
            "name": (row or {}).get("name") or code,
            "email": (row or {}).get("email"),
            "active": bool((row or {}).get("active", True)),
        }
        rec = self.search([("code", "=", code)], limit=1)
        if rec:
            rec.write(vals)
            return rec
        vals["code"] = code
        return self.create(vals)

    @api.model
    def resolve_user(self, code: str):
        rec = self.search([("code", "=", code), ("active", "=", True)], limit=1)
        if rec and rec.user_id:
            return rec.user_id
        # Soft match: map by email → user if exists
        if rec and rec.email:
            user = (
                self.env["res.users"]
                .sudo()
                .search([("login", "=", rec.email)], limit=1)
            )
            if user:
                rec.user_id = user.id
                return user
        return False
