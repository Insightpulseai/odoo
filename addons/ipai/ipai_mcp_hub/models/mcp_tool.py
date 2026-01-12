# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiMcpTool(models.Model):
    """Catalog of tools available from MCP servers."""

    _name = "ipai.mcp.tool"
    _description = "MCP Tool"
    _order = "server_id, name"

    name = fields.Char(required=True)
    tool_name = fields.Char(
        required=True,
        index=True,
        help="MCP tool identifier (e.g., 'list_tables', 'create_droplet')",
    )

    # Server relationship
    server_id = fields.Many2one(
        "ipai.mcp.server",
        required=True,
        index=True,
        ondelete="cascade",
    )
    server_code = fields.Char(
        related="server_id.code",
        store=True,
        index=True,
    )

    # Tool metadata
    description = fields.Text()
    input_schema = fields.Text(
        help="JSON schema for tool input parameters",
    )
    output_schema = fields.Text(
        help="JSON schema for tool output",
    )

    # Classification
    category = fields.Selection(
        [
            ("read", "Read/Query"),
            ("write", "Write/Mutate"),
            ("execute", "Execute/Action"),
            ("admin", "Admin/Config"),
        ],
        default="read",
        required=True,
    )
    is_destructive = fields.Boolean(
        default=False,
        help="True if this tool can delete or permanently modify data",
    )
    requires_confirmation = fields.Boolean(
        default=False,
        help="True if this tool should require user confirmation before execution",
    )
    tags = fields.Char(
        help="Comma-separated tags for filtering",
    )

    # Ownership
    company_id = fields.Many2one(
        related="server_id.company_id",
        store=True,
        index=True,
    )
    active = fields.Boolean(default=True)

    # Bindings
    binding_ids = fields.One2many(
        "ipai.mcp.binding",
        "tool_id",
        string="Model Bindings",
    )
    binding_count = fields.Integer(
        compute="_compute_binding_count",
        store=True,
    )

    _sql_constraints = [
        (
            "unique_tool_server",
            "UNIQUE(tool_name, server_id)",
            "Tool name must be unique per server",
        ),
    ]

    @api.depends("binding_ids")
    def _compute_binding_count(self):
        for rec in self:
            rec.binding_count = len(rec.binding_ids)

    @api.depends("name", "server_id")
    def _compute_display_name(self):
        for rec in self:
            if rec.server_id:
                rec.display_name = f"{rec.server_id.code}:{rec.name}"
            else:
                rec.display_name = rec.name

    @api.model
    def get_tools_for_model(self, model_name, usage=None):
        """Get tools bound to a specific Odoo model.

        Args:
            model_name: Technical model name (e.g., 'account.move')
            usage: Optional filter by usage type

        Returns:
            recordset of ipai.mcp.tool
        """
        domain = [
            ("binding_ids.model_id.model", "=", model_name),
            ("active", "=", True),
            ("server_id.active", "=", True),
        ]
        if usage:
            domain.append(("binding_ids.usage", "=", usage))
        return self.search(domain)
