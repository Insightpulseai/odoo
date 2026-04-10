# -*- coding: utf-8 -*-
"""
pulser.tool.binding — Odoo RPC tool binding per domain agent.

Defines the bounded tool contract for each domain agent.
Tools only execute via Odoo ORM/RPC — never direct DB writes (Constitution Principle 5).
"""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PulserToolBinding(models.Model):
    _name = "pulser.tool.binding"
    _description = "Pulser Tool Binding"
    _order = "agent_id, name"

    agent_id = fields.Many2one(
        comodel_name="pulser.domain.agent",
        string="Domain Agent",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        string="Tool Name",
        required=True,
        help="Machine-readable tool identifier (e.g. 'get_expense_status')",
    )
    model_name = fields.Char(
        string="Odoo Model",
        required=True,
        help="Technical model name (e.g. 'hr.expense', 'project.project')",
    )
    method_name = fields.Char(
        string="Method / Action",
        required=True,
        help=(
            "ORM method or action name the tool binds to "
            "(e.g. 'search_read', 'action_submit_sheet')"
        ),
    )
    action_class_id = fields.Many2one(
        comodel_name="pulser.action.class",
        string="Action Class",
        required=True,
        help="Safety gate classification: advisory, approval_gated, or auto_routable",
    )
    description = fields.Text(string="Description")
    is_read_only = fields.Boolean(
        string="Read Only",
        default=False,
        help="If True, this tool only reads Odoo state and never triggers mutations",
    )
    domain_filter = fields.Char(
        string="Domain Filter",
        help=(
            "Optional Odoo domain expression string applied when this tool reads records "
            "(e.g. \"[('state', 'in', ['draft', 'reported'])]\")"
        ),
    )

    _sql_constraints = [
        (
            "unique_tool_per_agent",
            "UNIQUE(agent_id, name)",
            "Tool name must be unique within a domain agent.",
        )
    ]

    @api.constrains("is_read_only", "action_class_id")
    def _check_read_only_class(self):
        for rec in self:
            if rec.is_read_only and rec.action_class_id:
                cls_type = rec.action_class_id.class_type
                if cls_type in ("approval_gated", "auto_routable"):
                    raise ValidationError(
                        f"Read-only tool '{rec.name}' cannot have action class "
                        f"'{cls_type}'. Use 'advisory' for read-only tools."
                    )
