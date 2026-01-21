# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaasSubscription(models.Model):
    """Links tenants to provider services - the core billing relationship."""

    _name = "saas.subscription"
    _description = "SaaS Subscription"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(
        string="Name",
        compute="_compute_name",
        store=True,
    )
    tenant_account_id = fields.Many2one(
        "saas.account",
        string="Tenant Account",
        required=True,
        ondelete="cascade",
        index=True,
        domain="[('is_tenant', '=', True)]",
        tracking=True,
    )
    provider_account_id = fields.Many2one(
        "saas.account",
        string="Provider Account",
        required=True,
        ondelete="cascade",
        index=True,
        domain="[('is_provider', '=', True)]",
        tracking=True,
    )
    service_id = fields.Many2one(
        "saas.service",
        string="Service",
        required=True,
        ondelete="cascade",
        index=True,
        tracking=True,
    )
    plan_id = fields.Many2one(
        "saas.service.plan",
        string="Plan",
        domain="[('service_id', '=', service_id)]",
        tracking=True,
    )

    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )

    # Lifecycle dates
    started_at = fields.Datetime(
        string="Started At",
        tracking=True,
    )
    ended_at = fields.Datetime(
        string="Ended At",
    )
    trial_ends_at = fields.Datetime(
        string="Trial Ends At",
    )
    next_billing_at = fields.Date(
        string="Next Billing Date",
    )
    cancelled_at = fields.Datetime(
        string="Cancelled At",
    )

    # Billing reference
    external_ref = fields.Char(
        string="External Reference",
        help="Stripe/Invoice ID for external billing",
        copy=False,
    )
    billing_metadata = fields.Text(
        string="Billing Metadata (JSON)",
        default="{}",
    )

    # External IDs
    supabase_id = fields.Char(
        string="Supabase Subscription ID",
        copy=False,
    )

    # Computed
    is_trial = fields.Boolean(
        string="In Trial",
        compute="_compute_is_trial",
    )
    days_remaining = fields.Integer(
        string="Days Remaining",
        compute="_compute_days_remaining",
    )

    @api.depends("tenant_account_id", "service_id")
    def _compute_name(self):
        for record in self:
            if record.tenant_account_id and record.service_id:
                record.name = (
                    f"{record.tenant_account_id.name} - {record.service_id.name}"
                )
            else:
                record.name = "New Subscription"

    def _compute_is_trial(self):
        now = fields.Datetime.now()
        for record in self:
            record.is_trial = (
                record.trial_ends_at
                and record.trial_ends_at > now
                and record.status == "active"
            )

    def _compute_days_remaining(self):
        now = fields.Date.today()
        for record in self:
            if record.ended_at:
                delta = fields.Date.from_string(record.ended_at.date()) - now
                record.days_remaining = max(0, delta.days)
            elif record.trial_ends_at:
                delta = fields.Date.from_string(record.trial_ends_at.date()) - now
                record.days_remaining = max(0, delta.days)
            else:
                record.days_remaining = -1  # Unlimited

    def action_activate(self):
        """Activate the subscription."""
        for record in self:
            if record.status == "draft":
                record.write(
                    {
                        "status": "active",
                        "started_at": fields.Datetime.now(),
                    }
                )
        return True

    def action_suspend(self):
        """Suspend the subscription."""
        for record in self:
            if record.status == "active":
                record.status = "suspended"
        return True

    def action_cancel(self):
        """Cancel the subscription."""
        for record in self:
            if record.status in ("active", "suspended"):
                record.write(
                    {
                        "status": "cancelled",
                        "cancelled_at": fields.Datetime.now(),
                        "ended_at": fields.Datetime.now(),
                    }
                )
        return True

    def action_reactivate(self):
        """Reactivate a suspended subscription."""
        for record in self:
            if record.status == "suspended":
                record.status = "active"
        return True


class SaasAccountLink(models.Model):
    """Explicit relationships between accounts."""

    _name = "saas.account.link"
    _description = "SaaS Account Link"

    from_account_id = fields.Many2one(
        "saas.account",
        string="From Account",
        required=True,
        ondelete="cascade",
        index=True,
    )
    to_account_id = fields.Many2one(
        "saas.account",
        string="To Account",
        required=True,
        ondelete="cascade",
        index=True,
    )
    link_type = fields.Selection(
        [
            ("provider_of", "Provider Of"),
            ("reseller_of", "Reseller Of"),
            ("partner_of", "Partner Of"),
        ],
        string="Link Type",
        required=True,
    )
    is_active = fields.Boolean(
        string="Active",
        default=True,
    )
    metadata = fields.Text(
        string="Metadata (JSON)",
        default="{}",
    )

    _sql_constraints = [
        (
            "link_unique",
            "UNIQUE(from_account_id, to_account_id, link_type)",
            "This link already exists.",
        ),
        (
            "no_self_link",
            "CHECK(from_account_id != to_account_id)",
            "Cannot create a link to the same account.",
        ),
    ]
