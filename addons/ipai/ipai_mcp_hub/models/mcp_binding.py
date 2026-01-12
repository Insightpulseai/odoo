# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiMcpBinding(models.Model):
    """Links MCP tools to Odoo models/fields for context-aware invocation."""

    _name = "ipai.mcp.binding"
    _description = "MCP Tool Binding"
    _order = "model_id, tool_id"

    # Tool relationship
    tool_id = fields.Many2one(
        "ipai.mcp.tool",
        required=True,
        index=True,
        ondelete="cascade",
    )
    tool_name = fields.Char(
        related="tool_id.tool_name",
        store=True,
    )
    server_code = fields.Char(
        related="tool_id.server_code",
        store=True,
    )

    # Model/Field binding
    model_id = fields.Many2one(
        "ir.model",
        required=True,
        index=True,
        ondelete="cascade",
        string="Odoo Model",
    )
    model_name = fields.Char(
        related="model_id.model",
        store=True,
        index=True,
    )
    field_ids = fields.Many2many(
        "ir.model.fields",
        "ipai_mcp_binding_field_rel",
        "binding_id",
        "field_id",
        string="Relevant Fields",
        domain="[('model_id', '=', model_id)]",
        help="Fields that this tool operates on or requires as context",
    )

    # Usage classification
    usage = fields.Selection(
        [
            ("ask_ai_context", "Ask AI Context"),
            ("write_back", "Write Back to Record"),
            ("analytics", "Analytics/Reporting"),
            ("monitoring", "Monitoring/Health"),
            ("automation", "Automation Trigger"),
        ],
        required=True,
        default="ask_ai_context",
    )

    # Configuration
    auto_invoke = fields.Boolean(
        default=False,
        help="Automatically invoke this tool when working with bound model",
    )
    priority = fields.Integer(
        default=10,
        help="Priority for tool ordering (lower = higher priority)",
    )
    context_template = fields.Text(
        help="Jinja2 template for generating tool input from record context",
    )

    # Ownership
    company_id = fields.Many2one(
        related="tool_id.company_id",
        store=True,
        index=True,
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "unique_tool_model_usage",
            "UNIQUE(tool_id, model_id, usage)",
            "Tool can only be bound once per model per usage type",
        ),
    ]

    @api.depends("tool_id", "model_id", "usage")
    def _compute_display_name(self):
        for rec in self:
            parts = []
            if rec.tool_id:
                parts.append(rec.tool_id.display_name)
            if rec.model_id:
                parts.append(rec.model_id.model)
            if rec.usage:
                parts.append(f"({rec.usage})")
            rec.display_name = " → ".join(parts) if parts else "New Binding"

    @api.model
    def get_bindings_for_record(self, model_name, record_id=None, usage=None):
        """Get bindings applicable to a specific record.

        Args:
            model_name: Technical model name
            record_id: Optional specific record ID
            usage: Optional filter by usage type

        Returns:
            dict with structure:
            {
                'model': model_name,
                'record_id': record_id,
                'tools': [
                    {
                        'server': server_code,
                        'tool': tool_name,
                        'usage': usage,
                        'fields': [field_names],
                    },
                    ...
                ]
            }
        """
        domain = [
            ("model_name", "=", model_name),
            ("active", "=", True),
            ("tool_id.active", "=", True),
            ("tool_id.server_id.active", "=", True),
        ]
        if usage:
            domain.append(("usage", "=", usage))

        bindings = self.search(domain, order="priority")

        return {
            "model": model_name,
            "record_id": record_id,
            "tools": [
                {
                    "server": b.server_code,
                    "tool": b.tool_name,
                    "usage": b.usage,
                    "fields": b.field_ids.mapped("name"),
                    "auto_invoke": b.auto_invoke,
                }
                for b in bindings
            ],
        }
