# -*- coding: utf-8 -*-
"""IPAI Agent Tool model - callable actions mapped to Odoo methods."""

from odoo.exceptions import UserError

from odoo import api, fields, models


class IpaiAgentTool(models.Model):
    """Agent tool definition with target model/method binding."""

    _name = "ipai.agent.tool"
    _description = "IPAI Agent Tool"
    _order = "name"

    name = fields.Char(required=True, index=True)
    key = fields.Char(
        required=True,
        index=True,
        help="Stable identifier, e.g. 'ipai.ai_studio.draft_spec'",
    )
    description = fields.Text()

    # Odoo execution target
    target_model = fields.Char(
        required=True, help="Target Odoo model, e.g. 'ipai.ai_studio.run'"
    )
    target_method = fields.Char(
        required=True, help="Method to call, e.g. 'action_draft_spec_from_prompt'"
    )

    # Schema definitions (optional, for validation/docs)
    input_schema_json = fields.Text(help="JSON Schema for inputs")
    output_schema_json = fields.Text(help="JSON Schema for outputs")

    is_active = fields.Boolean(default=True)
    requires_admin = fields.Boolean(
        default=False, help="If true, only admin users can execute this tool"
    )

    _sql_constraints = [
        ("tool_key_unique", "unique(key)", "Tool key must be unique."),
    ]

    def validate_target(self):
        """Check if target model and method exist."""
        self.ensure_one()
        if self.target_model not in self.env:
            raise UserError(f"Model '{self.target_model}' not found in registry")

        model = self.env[self.target_model]
        if not hasattr(model, self.target_method):
            raise UserError(
                f"Method '{self.target_method}' not found on model '{self.target_model}'"
            )
        return True

    def execute(self, record=None, **kwargs):
        """
        Execute the tool's target method.

        Args:
            record: Optional record to execute on (if method is instance method)
            **kwargs: Arguments to pass to the method

        Returns:
            Result from the target method
        """
        self.ensure_one()

        if self.requires_admin and not self.env.user.has_group("base.group_system"):
            raise UserError("This tool requires administrator privileges")

        model = self.env[self.target_model]
        method = getattr(model, self.target_method)

        if record:
            # Instance method on specific record
            return method(record, **kwargs)
        else:
            # Class method or method that creates its own records
            return method(**kwargs)

    def get_input_schema(self):
        """Parse and return input schema as dict."""
        self.ensure_one()
        import json

        try:
            return json.loads(self.input_schema_json or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_output_schema(self):
        """Parse and return output schema as dict."""
        self.ensure_one()
        import json

        try:
            return json.loads(self.output_schema_json or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}
