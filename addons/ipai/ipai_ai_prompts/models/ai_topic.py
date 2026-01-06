# -*- coding: utf-8 -*-
"""
IPAI AI Topic Model.

Topics categorize AI prompts and define domain-specific contexts.
"""
from odoo import api, fields, models


class IpaiAiTopic(models.Model):
    """AI topic/category for organizing prompts."""

    _name = "ipai.ai.topic"
    _description = "AI Topic"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Classification
    category = fields.Selection(
        [
            ("finance", "Finance & Accounting"),
            ("marketing", "Marketing & Sales"),
            ("hr", "HR & Operations"),
            ("tech", "Technical"),
            ("general", "General"),
        ],
        default="general",
        required=True,
    )

    # Description
    description = fields.Text(translate=True)
    icon = fields.Char(default="fa-lightbulb-o")
    color = fields.Integer(default=0)

    # System prompt for this topic
    system_prompt = fields.Text(
        string="System Prompt",
        translate=True,
        help="Base system prompt used when this topic is selected",
    )

    # Persona configuration
    persona_name = fields.Char(
        default="AI Assistant",
        help="Name of the AI persona for this topic",
    )
    persona_tone = fields.Selection(
        [
            ("professional", "Professional"),
            ("friendly", "Friendly"),
            ("technical", "Technical"),
            ("concise", "Concise"),
        ],
        default="professional",
    )

    # Related prompts
    prompt_ids = fields.One2many(
        "ipai.ai.prompt",
        "topic_id",
        string="Prompts",
    )
    prompt_count = fields.Integer(
        compute="_compute_prompt_count",
        store=True,
    )

    # Target models (what this topic applies to)
    model_ids = fields.Many2many(
        "ir.model",
        string="Applicable Models",
        help="Models where this topic is relevant",
    )

    _sql_constraints = [
        ("code_unique", "unique(code)", "Topic code must be unique."),
    ]

    @api.depends("prompt_ids")
    def _compute_prompt_count(self):
        for topic in self:
            topic.prompt_count = len(topic.prompt_ids)

    def get_system_prompt(self, context=None):
        """
        Get the complete system prompt for this topic.

        Args:
            context: Optional dict of context variables

        Returns:
            str: Formatted system prompt
        """
        self.ensure_one()
        prompt = self.system_prompt or ""

        if context:
            for key, value in context.items():
                prompt = prompt.replace(f"{{{{{key}}}}}", str(value))

        return prompt

    @api.model
    def get_by_code(self, code):
        """Get topic by code."""
        return self.search([("code", "=", code), ("active", "=", True)], limit=1)

    @api.model
    def get_for_model(self, model_name):
        """Get topics applicable to a model."""
        model = self.env["ir.model"].search([("model", "=", model_name)], limit=1)
        if not model:
            return self.browse()
        return self.search([
            ("active", "=", True),
            "|",
            ("model_ids", "=", False),
            ("model_ids", "in", model.ids),
        ])
