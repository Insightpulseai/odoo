# -*- coding: utf-8 -*-
"""IPAI Agent Skill model - workflow definitions with intent routing."""

from odoo import api, fields, models


class IpaiAgentSkill(models.Model):
    """Agent skill definition with workflow and guardrails."""

    _name = "ipai.agent.skill"
    _description = "IPAI Agent Skill"
    _order = "name"

    name = fields.Char(required=True, index=True)
    key = fields.Char(
        required=True,
        index=True,
        help="Stable identifier, e.g. 'odoo.ai_studio.build_module'"
    )
    version = fields.Char(default="1.0.0")
    description = fields.Text()
    intents = fields.Text(
        help="One intent per line. Used for routing/discovery."
    )
    workflow_json = fields.Text(
        help="JSON array of tool keys executed in order."
    )
    guardrails = fields.Text(
        help="One guardrail per line. Safety constraints."
    )
    is_active = fields.Boolean(default=True)

    tool_ids = fields.Many2many(
        "ipai.agent.tool",
        "ipai_skill_tool_rel",
        "skill_id",
        "tool_id",
        string="Bound Tools"
    )
    knowledge_ids = fields.Many2many(
        "ipai.agent.knowledge_source",
        "ipai_skill_knowledge_rel",
        "skill_id",
        "knowledge_id",
        string="Knowledge Sources"
    )

    run_ids = fields.One2many(
        "ipai.agent.run",
        "skill_id",
        string="Execution Runs"
    )
    run_count = fields.Integer(compute="_compute_run_count", store=True)

    _sql_constraints = [
        ("skill_key_unique", "unique(key)", "Skill key must be unique."),
    ]

    @api.depends("run_ids")
    def _compute_run_count(self):
        for rec in self:
            rec.run_count = len(rec.run_ids)

    def get_workflow_tools(self):
        """Return ordered list of tool keys from workflow_json."""
        self.ensure_one()
        import json
        try:
            return json.loads(self.workflow_json or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    def get_intents_list(self):
        """Return list of intents from multiline field."""
        self.ensure_one()
        if not self.intents:
            return []
        return [i.strip() for i in self.intents.split("\n") if i.strip()]

    def get_guardrails_list(self):
        """Return list of guardrails from multiline field."""
        self.ensure_one()
        if not self.guardrails:
            return []
        return [g.strip() for g in self.guardrails.split("\n") if g.strip()]
