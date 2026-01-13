# -*- coding: utf-8 -*-
# Part of InsightPulse AI. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaasEnvironment(models.Model):
    """Maps accounts to infrastructure bindings."""

    _name = "saas.environment"
    _description = "SaaS Environment"
    _order = "account_id, env_type"

    name = fields.Char(
        string="Name",
        compute="_compute_name",
        store=True,
    )
    account_id = fields.Many2one(
        "saas.account",
        string="Account",
        required=True,
        ondelete="cascade",
        index=True,
    )
    env_type = fields.Selection(
        [
            ("dev", "Development"),
            ("staging", "Staging"),
            ("prod", "Production"),
        ],
        string="Environment Type",
        required=True,
    )

    # Supabase binding
    supabase_project_ref = fields.Char(
        string="Supabase Project Ref",
        help="Supabase project reference (e.g., cxzllzyxwpyptfretryc)",
    )
    supabase_service_role = fields.Char(
        string="Supabase Service Role",
        help="Encrypted service role key",
        groups="base.group_system",
    )

    # Vercel binding
    vercel_project_id = fields.Char(
        string="Vercel Project ID",
    )
    vercel_team_id = fields.Char(
        string="Vercel Team ID",
    )

    # DigitalOcean binding
    digitalocean_app_id = fields.Char(
        string="DigitalOcean App ID",
    )
    digitalocean_cluster = fields.Char(
        string="DigitalOcean Cluster",
    )

    # Odoo binding
    odoo_db_name = fields.Char(
        string="Odoo Database Name",
        help="Odoo database name for this tenant",
    )
    odoo_base_url = fields.Char(
        string="Odoo Base URL",
        help="Odoo instance URL",
    )

    # Superset binding
    superset_database_key = fields.Char(
        string="Superset Database Key",
        help="Logical DB name in Superset",
    )
    superset_dashboard_ids = fields.Char(
        string="Superset Dashboard IDs",
        help="Comma-separated dashboard IDs",
    )

    is_active = fields.Boolean(
        string="Active",
        default=True,
    )

    # External IDs
    supabase_id = fields.Char(
        string="Supabase Environment ID",
        copy=False,
    )

    _sql_constraints = [
        (
            "account_env_unique",
            "UNIQUE(account_id, env_type)",
            "Each environment type can only exist once per account.",
        ),
    ]

    @api.depends("account_id", "env_type")
    def _compute_name(self):
        for record in self:
            if record.account_id and record.env_type:
                env_label = dict(record._fields["env_type"].selection).get(
                    record.env_type, record.env_type
                )
                record.name = f"{record.account_id.name} - {env_label}"
            else:
                record.name = "New Environment"

    def action_test_connection(self):
        """Test connection to all configured services."""
        self.ensure_one()
        # Placeholder for connection testing logic
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Connection Test",
                "message": "Connection test not yet implemented.",
                "type": "warning",
            },
        }


class SaasUsageRecord(models.Model):
    """Tracks service usage for billing and limit enforcement."""

    _name = "saas.usage.record"
    _description = "SaaS Usage Record"
    _order = "period_start desc"

    subscription_id = fields.Many2one(
        "saas.subscription",
        string="Subscription",
        required=True,
        ondelete="cascade",
        index=True,
    )
    tenant_account_id = fields.Many2one(
        "saas.account",
        string="Tenant Account",
        required=True,
        ondelete="cascade",
        index=True,
    )
    service_id = fields.Many2one(
        "saas.service",
        string="Service",
        required=True,
        ondelete="cascade",
        index=True,
    )

    period_start = fields.Date(
        string="Period Start",
        required=True,
    )
    period_end = fields.Date(
        string="Period End",
        required=True,
    )

    # Metrics
    request_count = fields.Integer(
        string="Request Count",
        default=0,
    )
    token_count = fields.Integer(
        string="Token Count",
        default=0,
        help="AI token usage",
    )
    storage_bytes = fields.Float(
        string="Storage (bytes)",
        default=0,
    )
    compute_seconds = fields.Integer(
        string="Compute (seconds)",
        default=0,
    )

    # Status
    is_billed = fields.Boolean(
        string="Billed",
        default=False,
    )
    billed_at = fields.Datetime(
        string="Billed At",
    )

    _sql_constraints = [
        (
            "usage_period_unique",
            "UNIQUE(subscription_id, period_start)",
            "Only one usage record per period per subscription.",
        ),
    ]
