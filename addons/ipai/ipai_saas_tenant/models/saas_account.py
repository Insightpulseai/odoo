# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaasAccountRole(models.Model):
    """Account roles - allows same account to be TENANT + PROVIDER."""

    _name = "saas.account.role"
    _description = "SaaS Account Role"

    account_id = fields.Many2one(
        "saas.account",
        string="Account",
        required=True,
        ondelete="cascade",
        index=True,
    )
    role = fields.Selection(
        [
            ("tenant", "Tenant"),
            ("provider", "Provider"),
            ("internal", "Internal"),
        ],
        string="Role",
        required=True,
    )
    is_primary = fields.Boolean(
        string="Primary Role",
        default=False,
        help="Primary role for this account",
    )
    granted_at = fields.Datetime(
        string="Granted At",
        default=fields.Datetime.now,
    )
    granted_by_id = fields.Many2one(
        "res.users",
        string="Granted By",
    )

    _sql_constraints = [
        (
            "account_role_unique",
            "UNIQUE(account_id, role)",
            "Each role can only be assigned once per account.",
        ),
    ]


class SaasAccount(models.Model):
    """
    SaaS Account - represents organizations that can be tenants, providers, or both.
    Maps to saas.accounts in Supabase schema.
    """

    _name = "saas.account"
    _description = "SaaS Account"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    # Core fields
    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )
    slug = fields.Char(
        string="Slug",
        required=True,
        index=True,
        tracking=True,
        help="Human-readable unique identifier (e.g., tbwa-ph)",
    )
    legal_name = fields.Char(
        string="Legal Name",
        help="Legal entity name for contracts",
    )
    country_id = fields.Many2one(
        "res.country",
        string="Country",
    )
    timezone = fields.Selection(
        "_tz_get",
        string="Timezone",
    )
    is_active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
    )

    # Multi-tenancy hints
    default_locale = fields.Char(
        string="Default Locale",
        default="en_US",
        help="Default locale (e.g., en_PH)",
    )
    billing_email = fields.Char(
        string="Billing Email",
        help="Primary billing contact email",
    )

    # Odoo mapping
    company_id = fields.Many2one(
        "res.company",
        string="Odoo Company",
        help="Linked Odoo company (res.company)",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Odoo Partner",
        help="Linked Odoo partner (res.partner)",
    )

    # External IDs
    supabase_id = fields.Char(
        string="Supabase Account ID",
        help="UUID from saas.accounts in Supabase",
        copy=False,
    )

    # Relations
    role_ids = fields.One2many(
        "saas.account.role",
        "account_id",
        string="Roles",
    )
    user_ids = fields.One2many(
        "saas.account.user",
        "account_id",
        string="Users",
    )
    service_ids = fields.One2many(
        "saas.service",
        "provider_account_id",
        string="Provided Services",
    )
    tenant_subscription_ids = fields.One2many(
        "saas.subscription",
        "tenant_account_id",
        string="Subscriptions (as Tenant)",
    )
    provider_subscription_ids = fields.One2many(
        "saas.subscription",
        "provider_account_id",
        string="Subscriptions (as Provider)",
    )
    environment_ids = fields.One2many(
        "saas.environment",
        "account_id",
        string="Environments",
    )

    # Computed fields
    is_tenant = fields.Boolean(
        string="Is Tenant",
        compute="_compute_roles",
        store=True,
    )
    is_provider = fields.Boolean(
        string="Is Provider",
        compute="_compute_roles",
        store=True,
    )
    is_internal = fields.Boolean(
        string="Is Internal",
        compute="_compute_roles",
        store=True,
    )
    active_subscription_count = fields.Integer(
        string="Active Subscriptions",
        compute="_compute_subscription_stats",
    )
    provided_service_count = fields.Integer(
        string="Provided Services",
        compute="_compute_service_stats",
    )

    _sql_constraints = [
        ("slug_unique", "UNIQUE(slug)", "Slug must be unique."),
    ]

    @api.model
    def _tz_get(self):
        """Get timezone selection from pytz."""
        import pytz
        return [(tz, tz) for tz in sorted(pytz.all_timezones)]

    @api.depends("role_ids.role")
    def _compute_roles(self):
        for record in self:
            roles = record.role_ids.mapped("role")
            record.is_tenant = "tenant" in roles
            record.is_provider = "provider" in roles
            record.is_internal = "internal" in roles

    def _compute_subscription_stats(self):
        for record in self:
            record.active_subscription_count = len(
                record.tenant_subscription_ids.filtered(
                    lambda s: s.status == "active"
                )
            )

    def _compute_service_stats(self):
        for record in self:
            record.provided_service_count = len(
                record.service_ids.filtered(lambda s: s.is_enabled)
            )

    def action_add_tenant_role(self):
        """Add tenant role to account."""
        for record in self:
            if not record.role_ids.filtered(lambda r: r.role == "tenant"):
                self.env["saas.account.role"].create({
                    "account_id": record.id,
                    "role": "tenant",
                })
        return True

    def action_add_provider_role(self):
        """Add provider role to account."""
        for record in self:
            if not record.role_ids.filtered(lambda r: r.role == "provider"):
                self.env["saas.account.role"].create({
                    "account_id": record.id,
                    "role": "provider",
                })
        return True


class SaasAccountUser(models.Model):
    """Users belonging to a SaaS account."""

    _name = "saas.account.user"
    _description = "SaaS Account User"
    _order = "email"

    account_id = fields.Many2one(
        "saas.account",
        string="Account",
        required=True,
        ondelete="cascade",
        index=True,
    )
    email = fields.Char(
        string="Email",
        required=True,
        index=True,
    )
    full_name = fields.Char(
        string="Full Name",
    )
    is_admin = fields.Boolean(
        string="Account Admin",
        default=False,
        help="Has admin privileges for this account",
    )
    is_active = fields.Boolean(
        string="Active",
        default=True,
    )

    # External IDs
    supabase_auth_id = fields.Char(
        string="Supabase Auth ID",
        help="auth.users.id from Supabase",
        copy=False,
    )
    odoo_user_id = fields.Many2one(
        "res.users",
        string="Odoo User",
        help="Linked Odoo user (res.users)",
    )
    keycloak_id = fields.Char(
        string="Keycloak ID",
        help="Keycloak user ID for SSO",
        copy=False,
    )

    _sql_constraints = [
        ("email_unique", "UNIQUE(email)", "Email must be unique."),
    ]
