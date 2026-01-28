# Copyright 2026 InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FluentCopilotIntent(models.Model):
    """Predefined intents/actions that the Copilot can recognize and execute.

    This is a configuration model for defining available intents like
    "Summarize", "Explain", "Show KPIs", "Navigate to...", etc.

    In production, this would be extended with:
    - AI prompt templates
    - Required context fields
    - Permission checks
    - Domain-specific handlers
    """

    _name = "fluent.copilot.intent"
    _description = "Copilot Intent"
    _order = "sequence, name"

    name = fields.Char(
        string="Intent Name",
        required=True,
        help="Display name for this intent (e.g., 'Summarize Record')",
    )
    code = fields.Char(
        string="Technical Code",
        required=True,
        help="Technical identifier (e.g., 'summarize', 'explain', 'show_kpis')",
    )
    description = fields.Text(
        string="Description",
        help="Detailed description of what this intent does",
    )
    example_utterance = fields.Char(
        string="Example Utterance",
        help="Example of how a user might phrase this intent "
        "(e.g., 'What is this invoice about?')",
    )
    icon = fields.Char(
        string="Icon",
        default="fa-lightbulb-o",
        help="Font Awesome icon class for UI display",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Display order in intent selection UI",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Inactive intents are hidden from users",
    )
    category = fields.Selection(
        selection=[
            ("general", "General"),
            ("finance", "Finance"),
            ("project", "Project"),
            ("crm", "CRM"),
            ("inventory", "Inventory"),
            ("hr", "Human Resources"),
            ("navigation", "Navigation"),
        ],
        string="Category",
        default="general",
        help="Domain category for this intent",
    )
    applicable_models = fields.Char(
        string="Applicable Models",
        help="Comma-separated list of model names where this intent applies "
        "(e.g., 'account.move,project.task'). Empty means all models.",
    )

    _sql_constraints = [
        (
            "code_uniq",
            "UNIQUE(code)",
            "Intent code must be unique!",
        ),
    ]

    def name_get(self):
        """Display name with icon hint."""
        result = []
        for record in self:
            name = f"[{record.code}] {record.name}"
            result.append((record.id, name))
        return result
