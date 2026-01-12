# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiMcpServer(models.Model):
    """Registry of MCP servers available for agent orchestration."""

    _name = "ipai.mcp.server"
    _description = "MCP Server"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    code = fields.Char(
        required=True,
        index=True,
        help="Technical identifier (e.g., 'supabase', 'github', 'digitalocean')",
    )

    # Connection
    base_url = fields.Char(
        help="MCP server base URL (if HTTP-based)",
    )
    transport = fields.Selection(
        [
            ("stdio", "Standard I/O"),
            ("http", "HTTP/REST"),
            ("websocket", "WebSocket"),
        ],
        default="stdio",
        required=True,
    )
    command = fields.Char(
        help="Command to start server (for stdio transport, e.g., 'npx @supabase/mcp-server')",
    )

    # Authentication
    env_key_name = fields.Char(
        help="Environment variable name containing API token/secret",
    )

    # Classification
    category = fields.Selection(
        [
            ("database", "Database"),
            ("cloud", "Cloud Infrastructure"),
            ("deployment", "Deployment"),
            ("repository", "Code Repository"),
            ("design", "Design"),
            ("docs", "Documentation"),
            ("automation", "Automation"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
    )
    tags = fields.Char(
        help="Comma-separated tags for filtering",
    )

    # Ownership
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    active = fields.Boolean(default=True)

    # Related records
    tool_ids = fields.One2many(
        "ipai.mcp.tool",
        "server_id",
        string="Tools",
    )
    tool_count = fields.Integer(
        compute="_compute_tool_count",
        store=True,
    )

    # Health tracking
    last_health_check = fields.Datetime(
        readonly=True,
    )
    health_status = fields.Selection(
        [
            ("unknown", "Unknown"),
            ("healthy", "Healthy"),
            ("degraded", "Degraded"),
            ("down", "Down"),
        ],
        default="unknown",
        readonly=True,
    )

    _sql_constraints = [
        (
            "unique_code_company",
            "UNIQUE(code, company_id)",
            "Server code must be unique per company",
        ),
    ]

    @api.depends("tool_ids")
    def _compute_tool_count(self):
        for rec in self:
            rec.tool_count = len(rec.tool_ids)

    def action_check_health(self):
        """Check server health status.

        Placeholder for actual health check implementation.
        In practice, this would be done via queue_job or external agent.
        """
        self.ensure_one()
        self.write({
            "last_health_check": fields.Datetime.now(),
            "health_status": "unknown",  # Would be set by actual check
        })
        return True

    @api.model
    def get_servers_for_category(self, category, company_id=None):
        """Get active servers for a category."""
        company = (
            self.env["res.company"].browse(company_id)
            if company_id
            else self.env.company
        )
        return self.search([
            ("company_id", "=", company.id),
            ("category", "=", category),
            ("active", "=", True),
        ])
