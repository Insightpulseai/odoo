# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, _

_logger = logging.getLogger(__name__)

AUTH_MODE = [
    ("none", "None (no auth)"),
    ("api_key", "API Key (ir.config_parameter)"),
    ("jwt", "Supabase JWT (user token)"),
    ("service_role", "Supabase Service Role"),
    ("hmac", "HMAC-SHA256 (webhook secret)"),
]


class IpaiAgentTool(models.Model):
    """
    Registry of tools that IPAI agents may call.

    Each tool represents a capability (e.g. ocr_extract, bir_validate)
    that an Edge Function / MCP node can invoke.

    auth_mode controls how calls to this tool are authenticated:
    - none          — no auth (internal-only, e.g. echo)
    - api_key       — secret read from ir.config_parameter
    - jwt           — user's Supabase JWT forwarded by Odoo
    - service_role  — Supabase service_role key (highest privilege)
    - hmac          — HMAC-SHA256 signature verification for callbacks
    """

    _name = "ipai.agent.tool"
    _description = "IPAI Agent Tool"
    _order = "name"

    name = fields.Char(string="Tool Name", required=True)
    technical_name = fields.Char(
        string="Technical Name",
        required=True,
        help="Snake-case identifier sent in the tool_calls_json payload.",
    )
    active = fields.Boolean(default=True)
    description = fields.Text(string="Description")
    auth_mode = fields.Selection(
        AUTH_MODE,
        string="Auth Mode",
        required=True,
        default="api_key",
    )
    endpoint_param = fields.Char(
        string="Endpoint ir.config_parameter Key",
        help="ir.config_parameter key that holds the tool's endpoint URL.",
    )
    secret_param = fields.Char(
        string="Secret ir.config_parameter Key",
        help="ir.config_parameter key that holds the tool's API key / HMAC secret.",
    )
    allowed_group_ids = fields.Many2many(
        "res.groups",
        "agent_tool_group_rel",
        "tool_id",
        "group_id",
        string="Allowed Groups",
        help="Only members of these groups may trigger runs using this tool.",
    )
    policy_ids = fields.Many2many(
        "ipai.agent.policy",
        "agent_policy_tool_rel",
        "tool_id",
        "policy_id",
        string="Policies",
    )

    _sql_constraints = [
        ("unique_technical_name", "UNIQUE(technical_name)", "Technical name must be unique."),
    ]

    def get_endpoint(self):
        """Return the live endpoint URL from ir.config_parameter (never hardcoded)."""
        self.ensure_one()
        if not self.endpoint_param:
            return None
        return self.env["ir.config_parameter"].sudo().get_param(self.endpoint_param)

    def get_secret(self):
        """Return the live secret from ir.config_parameter (never hardcoded)."""
        self.ensure_one()
        if not self.secret_param:
            return None
        return self.env["ir.config_parameter"].sudo().get_param(self.secret_param)
