# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaasService(models.Model):
    """Services offered by providers."""

    _name = "saas.service"
    _description = "SaaS Service"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    # Core fields
    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )
    key = fields.Char(
        string="Service Key",
        required=True,
        index=True,
        tracking=True,
        help="Unique key (e.g., scout-dashboard, ask-copilot)",
    )
    description = fields.Text(
        string="Description",
    )
    provider_account_id = fields.Many2one(
        "saas.account",
        string="Provider Account",
        required=True,
        ondelete="cascade",
        index=True,
        domain="[('is_provider', '=', True)]",
    )

    # Visibility
    is_public = fields.Boolean(
        string="Public",
        default=False,
        tracking=True,
        help="Listed in marketplace",
    )
    is_enabled = fields.Boolean(
        string="Enabled",
        default=True,
        tracking=True,
        help="Service can be subscribed to",
    )

    # Classification
    category = fields.Selection(
        [
            ("ai_agent", "AI Agent"),
            ("dashboard", "Dashboard"),
            ("erp_integration", "ERP Integration"),
            ("workflow", "Workflow"),
            ("analytics", "Analytics"),
            ("other", "Other"),
        ],
        string="Category",
        default="other",
    )
    default_environment_type = fields.Selection(
        [
            ("dev", "Development"),
            ("staging", "Staging"),
            ("prod", "Production"),
        ],
        string="Default Environment",
    )

    # Technical hints
    mcp_server_name = fields.Char(
        string="MCP Server Name",
        help="MCP server providing this service",
    )
    n8n_workflow_id = fields.Char(
        string="n8n Workflow ID",
        help="n8n workflow ID if workflow-based",
    )

    # Relations
    plan_ids = fields.One2many(
        "saas.service.plan",
        "service_id",
        string="Plans",
    )
    subscription_ids = fields.One2many(
        "saas.subscription",
        "service_id",
        string="Subscriptions",
    )

    # External IDs
    supabase_id = fields.Char(
        string="Supabase Service ID",
        help="UUID from saas.services in Supabase",
        copy=False,
    )

    # Computed
    active_subscription_count = fields.Integer(
        string="Active Subscriptions",
        compute="_compute_subscription_count",
    )

    _sql_constraints = [
        ("key_unique", "UNIQUE(key)", "Service key must be unique."),
    ]

    def _compute_subscription_count(self):
        for record in self:
            record.active_subscription_count = len(
                record.subscription_ids.filtered(lambda s: s.status == "active")
            )


class SaasServicePlan(models.Model):
    """Pricing plans for services."""

    _name = "saas.service.plan"
    _description = "SaaS Service Plan"
    _order = "sequence, id"

    name = fields.Char(
        string="Name",
        required=True,
    )
    key = fields.Char(
        string="Plan Key",
        required=True,
        help="Plan key (free, pro, enterprise)",
    )
    description = fields.Text(
        string="Description",
    )
    service_id = fields.Many2one(
        "saas.service",
        string="Service",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )

    # Pricing
    monthly_price = fields.Monetary(
        string="Monthly Price",
        currency_field="currency_id",
    )
    annual_price = fields.Monetary(
        string="Annual Price",
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    # Limits
    max_seats = fields.Integer(
        string="Max Seats",
        help="Maximum users, 0 = unlimited",
    )
    max_requests_month = fields.Integer(
        string="Max Requests/Month",
        help="API/usage limits per month, 0 = unlimited",
    )
    feature_flags = fields.Text(
        string="Feature Flags (JSON)",
        help="JSON object of feature toggles for this plan",
        default="{}",
    )

    is_active = fields.Boolean(
        string="Active",
        default=True,
    )

    # External IDs
    supabase_id = fields.Char(
        string="Supabase Plan ID",
        copy=False,
    )

    _sql_constraints = [
        (
            "service_key_unique",
            "UNIQUE(service_id, key)",
            "Plan key must be unique per service.",
        ),
    ]
