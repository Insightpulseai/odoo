# -*- coding: utf-8 -*-
"""
IPAI AI Prompt Model.

Reusable prompt templates with variable support.
"""
import re

from odoo import api, fields, models


class IpaiAiPrompt(models.Model):
    """AI prompt template with variable placeholders."""

    _name = "ipai.ai.prompt"
    _description = "AI Prompt Template"
    _order = "topic_id, sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Topic association
    topic_id = fields.Many2one(
        "ipai.ai.topic",
        required=True,
        ondelete="cascade",
        index=True,
    )

    # Prompt type
    prompt_type = fields.Selection(
        [
            ("quick", "Quick Action"),
            ("template", "Full Template"),
            ("few_shot", "Few-Shot Example"),
            ("chain", "Chain of Thought"),
        ],
        default="quick",
        required=True,
    )

    # The prompt content
    prompt_template = fields.Text(
        required=True,
        translate=True,
        help="Prompt template. Use {{variable}} for placeholders.",
    )

    # Optional system override
    system_prompt_override = fields.Text(
        translate=True,
        help="Override the topic's system prompt for this specific prompt",
    )

    # Output configuration
    output_format = fields.Selection(
        [
            ("text", "Plain Text"),
            ("markdown", "Markdown"),
            ("json", "JSON"),
            ("list", "Bullet List"),
            ("table", "Table"),
        ],
        default="text",
    )
    output_instructions = fields.Text(
        translate=True,
        help="Additional instructions for output formatting",
    )

    # Few-shot examples
    examples = fields.Text(
        help="Few-shot examples in format: Input: ... Output: ...",
    )

    # UI configuration
    icon = fields.Char(default="fa-comment")
    color = fields.Integer(default=0)
    show_in_menu = fields.Boolean(
        default=True,
        help="Show this prompt as a quick action in menus",
    )

    # Variables extracted from template
    variable_names = fields.Char(
        compute="_compute_variable_names",
        store=True,
    )

    # Usage tracking
    usage_count = fields.Integer(readonly=True)
    last_used = fields.Datetime(readonly=True)

    _sql_constraints = [
        ("code_unique", "unique(code)", "Prompt code must be unique."),
    ]

    @api.depends("prompt_template")
    def _compute_variable_names(self):
        for prompt in self:
            if prompt.prompt_template:
                # Extract {{variable}} patterns
                variables = re.findall(r"\{\{(\w+)\}\}", prompt.prompt_template)
                prompt.variable_names = ",".join(sorted(set(variables)))
            else:
                prompt.variable_names = ""

    def get_variables(self):
        """Return list of variable names in this prompt."""
        self.ensure_one()
        if self.variable_names:
            return self.variable_names.split(",")
        return []

    def render(self, variables=None, **kwargs):
        """
        Render the prompt with variables substituted.

        Args:
            variables: Dict of variable values
            **kwargs: Additional variables (merged with variables dict)

        Returns:
            str: Rendered prompt text
        """
        self.ensure_one()
        prompt = self.prompt_template or ""

        # Merge variable sources
        all_vars = {}
        if variables:
            all_vars.update(variables)
        all_vars.update(kwargs)

        # Substitute variables
        for key, value in all_vars.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))

        # Add output instructions if specified
        if self.output_instructions:
            prompt += f"\n\n{self.output_instructions}"

        # Add few-shot examples if specified
        if self.examples and self.prompt_type == "few_shot":
            prompt = f"{self.examples}\n\n{prompt}"

        return prompt

    def get_system_prompt(self):
        """Get the system prompt to use with this prompt template."""
        self.ensure_one()
        if self.system_prompt_override:
            return self.system_prompt_override
        return self.topic_id.get_system_prompt() if self.topic_id else ""

    def execute(self, variables=None, **kwargs):
        """
        Execute this prompt and return AI response.

        Args:
            variables: Dict of variable values
            **kwargs: Additional parameters for AI provider

        Returns:
            dict: AI generation result
        """
        self.ensure_one()

        # Update usage stats
        self.sudo().write(
            {
                "usage_count": self.usage_count + 1,
                "last_used": fields.Datetime.now(),
            }
        )

        # Render prompt
        rendered = self.render(variables, **kwargs)

        # Get system prompt
        system = self.get_system_prompt()

        # Build messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": rendered})

        # Call AI provider
        provider = self.env["ipai.ai.provider"]
        return provider.generate(messages, **kwargs)

    @api.model
    def get_by_code(self, code):
        """Get prompt by code."""
        return self.search([("code", "=", code), ("active", "=", True)], limit=1)

    @api.model
    def get_quick_actions(self, topic_code=None, model_name=None):
        """
        Get quick action prompts.

        Args:
            topic_code: Optional topic code filter
            model_name: Optional model name filter

        Returns:
            recordset of prompts
        """
        domain = [
            ("active", "=", True),
            ("show_in_menu", "=", True),
            ("prompt_type", "=", "quick"),
        ]

        if topic_code:
            topic = self.env["ipai.ai.topic"].get_by_code(topic_code)
            if topic:
                domain.append(("topic_id", "=", topic.id))

        return self.search(domain)
