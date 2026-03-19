# -*- coding: utf-8 -*-
import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SkillCategory(models.Model):
    _name = "ipai.skill.category"
    _description = "Agent Skill Category"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    description = fields.Text()
    skill_ids = fields.One2many("ipai.skill.definition", "category_id", string="Skills")
    skill_count = fields.Integer(compute="_compute_skill_count")

    @api.depends("skill_ids")
    def _compute_skill_count(self):
        for rec in self:
            rec.skill_count = len(rec.skill_ids)


class SkillDefinition(models.Model):
    _name = "ipai.skill.definition"
    _description = "Agent Skill Definition"
    _inherit = ["mail.thread"]
    _order = "category_id, sequence, name"

    name = fields.Char(required=True, tracking=True)
    key = fields.Char(
        required=True,
        index=True,
        help="Dot-notation skill key (e.g., odoo.consultation)",
    )
    version = fields.Char(default="1.0.0")
    category_id = fields.Many2one(
        "ipai.skill.category", string="Category", ondelete="restrict"
    )
    sequence = fields.Integer(default=10)
    description = fields.Text()
    active = fields.Boolean(default=True)

    # Intents
    intent_ids = fields.Text(
        string="Intents (JSON)",
        help="JSON array of natural language trigger phrases",
    )

    # Guardrails
    guardrails = fields.Text(help="JSON array of safety constraints for this skill")

    # Tools
    tool_ids = fields.Text(
        string="Tools (JSON)",
        help="JSON array of tool definitions with key, name, target_model, "
        "target_method, description",
    )

    # Workflow
    workflow = fields.Text(help="JSON array of tool keys defining execution order")

    # Schemas
    input_schema = fields.Text(help="JSON Schema for skill input validation")
    output_schema = fields.Text(help="JSON Schema for skill output validation")

    # Agent instructions
    agent_instructions = fields.Text(
        help="Prose instructions for AI agent on how to execute this skill"
    )

    # Statistics
    execution_count = fields.Integer(compute="_compute_execution_count", store=False)
    last_execution_date = fields.Datetime(
        compute="_compute_execution_count", store=False
    )

    _sql_constraints = [
        ("key_unique", "UNIQUE(key)", "Skill key must be unique."),
    ]

    @api.depends()
    def _compute_execution_count(self):
        execution_model = self.env["ipai.skill.execution"]
        for rec in self:
            executions = execution_model.search(
                [("skill_id", "=", rec.id)], order="create_date desc"
            )
            rec.execution_count = len(executions)
            rec.last_execution_date = executions[0].create_date if executions else False

    def get_tools_list(self):
        """Return parsed tool definitions."""
        self.ensure_one()
        if self.tool_ids:
            try:
                return json.loads(self.tool_ids)
            except (json.JSONDecodeError, TypeError):
                _logger.warning("Invalid tools JSON for skill %s", self.key)
        return []

    def get_workflow_list(self):
        """Return parsed workflow sequence."""
        self.ensure_one()
        if self.workflow:
            try:
                return json.loads(self.workflow)
            except (json.JSONDecodeError, TypeError):
                _logger.warning("Invalid workflow JSON for skill %s", self.key)
        return []

    def get_intents_list(self):
        """Return parsed intent phrases."""
        self.ensure_one()
        if self.intent_ids:
            try:
                return json.loads(self.intent_ids)
            except (json.JSONDecodeError, TypeError):
                _logger.warning("Invalid intents JSON for skill %s", self.key)
        return []
