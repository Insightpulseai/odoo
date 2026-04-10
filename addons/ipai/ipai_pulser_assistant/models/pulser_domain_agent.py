# -*- coding: utf-8 -*-
"""
pulser.domain.agent — Domain agent registry.

Each domain agent has bounded tool access, inherits user Odoo security groups,
and cannot bypass Odoo approval or permission controls (Constitution Principle 5).
"""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PulserDomainAgent(models.Model):
    _name = "pulser.domain.agent"
    _description = "Pulser Domain Agent"
    _order = "name"

    name = fields.Char(string="Agent Name", required=True)
    domain = fields.Char(
        string="Domain Key",
        required=True,
        help="Machine-readable domain key (e.g. 'expense', 'project', 'hr', 'accounting')",
    )
    description = fields.Text(string="Description")
    is_active = fields.Boolean(string="Active", default=True)

    supported_intent_ids = fields.Many2many(
        comodel_name="pulser.intent",
        relation="pulser_agent_intent_rel",
        column1="agent_id",
        column2="intent_id",
        string="Supported Intents",
        help="Intent types this domain agent can handle",
    )
    tool_binding_ids = fields.One2many(
        comodel_name="pulser.tool.binding",
        inverse_name="agent_id",
        string="Tool Bindings",
        help="Odoo RPC tool bindings available to this agent",
    )
    security_group_id = fields.Many2one(
        comodel_name="res.groups",
        string="Required Security Group",
        help=(
            "Odoo security group required to invoke this agent. "
            "Agent actions are bounded by this group and user's own record rules."
        ),
    )
    tool_count = fields.Integer(
        string="Tool Count",
        compute="_compute_tool_count",
    )

    _sql_constraints = [
        (
            "unique_domain_key",
            "UNIQUE(domain)",
            "Domain key must be unique across agents.",
        )
    ]

    @api.depends("tool_binding_ids")
    def _compute_tool_count(self):
        for rec in self:
            rec.tool_count = len(rec.tool_binding_ids)

    @api.constrains("domain")
    def _check_domain_key(self):
        for rec in self:
            if not rec.domain or not rec.domain.strip():
                raise ValidationError("Domain key cannot be blank.")
            if " " in rec.domain:
                raise ValidationError(
                    "Domain key must not contain spaces. Use underscore-delimited lowercase."
                )
