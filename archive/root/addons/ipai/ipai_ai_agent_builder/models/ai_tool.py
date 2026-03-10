# -*- coding: utf-8 -*-
# Part of IPAI. See LICENSE file for full copyright and licensing details.

import importlib
import json
import logging

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


class IpaiAiTool(models.Model):
    """Tool registry for callable business actions."""

    _name = "ipai.ai.tool"
    _description = "IPAI AI Tool"
    _order = "name"

    key = fields.Char(
        string="Key",
        required=True,
        index=True,
        help="Unique identifier for the tool (e.g., crm_create_lead).",
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    description = fields.Text(
        string="Description",
        help="Description of what this tool does, shown to the LLM.",
    )
    python_entrypoint = fields.Char(
        string="Python Entrypoint",
        required=True,
        help="Module path and function (e.g., ipai_ai_tools.tools.crm_tools:create_lead).",
    )
    parameters_schema = fields.Text(
        string="Parameters Schema",
        help="JSON Schema defining the tool's input parameters.",
    )
    group_ids = fields.Many2many(
        comodel_name="res.groups",
        relation="ipai_ai_tool_group_rel",
        column1="tool_id",
        column2="group_id",
        string="Allowed Groups",
        help="Only users in these groups can execute this tool.",
    )
    dry_run_supported = fields.Boolean(
        string="Supports Dry Run",
        default=False,
        help="Whether this tool supports dry-run mode for testing.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    topic_ids = fields.Many2many(
        comodel_name="ipai.ai.topic",
        relation="ipai_ai_topic_tool_rel",
        column1="tool_id",
        column2="topic_id",
        string="Topics",
    )

    _sql_constraints = [
        ("key_unique", "UNIQUE(key)", "Tool key must be unique."),
    ]

    @api.constrains("python_entrypoint")
    def _check_python_entrypoint(self):
        """Validate that the Python entrypoint is properly formatted."""
        for tool in self:
            if ":" not in tool.python_entrypoint:
                raise ValidationError(
                    f"Invalid entrypoint format: {tool.python_entrypoint}. "
                    "Expected format: module.path:function_name"
                )

    def check_permission(self, user=None):
        """Check if the given user has permission to execute this tool."""
        self.ensure_one()
        user = user or self.env.user
        if not self.group_ids:
            return True  # No restrictions
        return bool(user.groups_id & self.group_ids)

    def get_function(self):
        """Load and return the Python function for this tool."""
        self.ensure_one()
        module_path, func_name = self.python_entrypoint.rsplit(":", 1)
        try:
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        except (ImportError, AttributeError) as e:
            _logger.error(f"Failed to load tool function: {self.python_entrypoint}")
            raise ValidationError(f"Failed to load tool: {e}")

    def get_llm_definition(self):
        """Get the tool definition in LLM-compatible format (OpenAI function calling)."""
        self.ensure_one()
        definition = {
            "type": "function",
            "function": {
                "name": self.key,
                "description": self.description or self.name,
            },
        }
        if self.parameters_schema:
            try:
                definition["function"]["parameters"] = json.loads(self.parameters_schema)
            except json.JSONDecodeError:
                _logger.warning(f"Invalid parameters schema for tool {self.key}")
        return definition

    def execute(self, env, input_data, dry_run=False):
        """Execute the tool with the given input data."""
        self.ensure_one()

        # Permission check
        if not self.check_permission():
            raise AccessError(f"You do not have permission to execute tool: {self.key}")

        # Dry run check
        if dry_run and not self.dry_run_supported:
            raise ValidationError(f"Tool {self.key} does not support dry-run mode.")

        # Load and execute function
        func = self.get_function()
        return func(env, input_data, dry_run=dry_run)
