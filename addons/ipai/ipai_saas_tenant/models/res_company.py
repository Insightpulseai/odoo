# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResCompany(models.Model):
    """Extend res.company with SaaS account link."""

    _inherit = "res.company"

    saas_account_id = fields.Many2one(
        "saas.account",
        string="SaaS Account",
        help="Linked SaaS account for multi-tenant operations",
    )

    def action_create_saas_account(self):
        """Create a SaaS account from this company."""
        self.ensure_one()
        if self.saas_account_id:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "SaaS Account Exists",
                    "message": "This company already has a linked SaaS account.",
                    "type": "warning",
                },
            }

        # Create slug from company name
        slug = self.name.lower().replace(" ", "-").replace(".", "")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")

        # Check for uniqueness and modify if needed
        existing = self.env["saas.account"].search([("slug", "=", slug)])
        if existing:
            slug = f"{slug}-{self.id}"

        account = self.env["saas.account"].create({
            "name": self.name,
            "slug": slug,
            "legal_name": self.name,
            "country_id": self.country_id.id if self.country_id else False,
            "company_id": self.id,
            "partner_id": self.partner_id.id,
            "billing_email": self.email,
        })

        # Add tenant role by default
        self.env["saas.account.role"].create({
            "account_id": account.id,
            "role": "tenant",
            "is_primary": True,
        })

        self.saas_account_id = account

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "SaaS Account Created",
                "message": f"Created SaaS account: {account.name} ({account.slug})",
                "type": "success",
            },
        }
