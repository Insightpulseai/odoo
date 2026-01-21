# Copyright 2026 InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FluentCopilotMessage(models.Model):
    """A single message in a Copilot conversation.

    Messages can be from the user, the assistant (AI), or system-generated.
    Different message types support various UX patterns like questions,
    suggestions, explanations, KPI summaries, and navigation hints.

    In production, this would be extended with:
    - Streaming response support
    - Feedback/rating fields
    - Source citations
    - Action execution results
    """

    _name = "fluent.copilot.message"
    _description = "Copilot Message"
    _order = "create_date asc"

    session_id = fields.Many2one(
        comodel_name="fluent.copilot.session",
        string="Session",
        required=True,
        ondelete="cascade",
    )
    role = fields.Selection(
        selection=[
            ("user", "User"),
            ("assistant", "Assistant"),
            ("system", "System"),
        ],
        string="Role",
        required=True,
        default="user",
        help="Who sent this message",
    )
    message_type = fields.Selection(
        selection=[
            ("question", "Question"),
            ("suggestion", "Suggestion"),
            ("explanation", "Explanation"),
            ("kpi_summary", "KPI Summary"),
            ("navigation_hint", "Navigation Hint"),
            ("action_result", "Action Result"),
            ("error", "Error"),
        ],
        string="Message Type",
        default="question",
        help="Type of message for UI rendering",
    )
    body = fields.Text(
        string="Message Body",
        required=True,
        help="The actual message content",
    )
    intent_id = fields.Many2one(
        comodel_name="fluent.copilot.intent",
        string="Triggered Intent",
        help="If this message triggered a specific intent",
    )

    # UI decoration fields
    icon = fields.Char(
        string="Icon",
        compute="_compute_icon",
        help="Icon for message display",
    )
    css_class = fields.Char(
        string="CSS Class",
        compute="_compute_css_class",
        help="CSS class for styling",
    )

    # Mock fields for prototype
    mock_confidence = fields.Float(
        string="Confidence (Mock)",
        default=0.95,
        help="Simulated AI confidence score",
    )
    mock_latency_ms = fields.Integer(
        string="Latency (Mock)",
        default=450,
        help="Simulated response latency in milliseconds",
    )
    mock_tokens = fields.Integer(
        string="Tokens (Mock)",
        default=0,
        help="Simulated token count for this message",
    )

    @api.depends("role", "message_type")
    def _compute_icon(self):
        """Assign icon based on role and type."""
        role_icons = {
            "user": "fa-user",
            "assistant": "fa-robot",
            "system": "fa-cog",
        }
        type_icons = {
            "kpi_summary": "fa-chart-bar",
            "navigation_hint": "fa-compass",
            "suggestion": "fa-lightbulb-o",
            "explanation": "fa-info-circle",
            "error": "fa-exclamation-triangle",
        }
        for message in self:
            if message.message_type in type_icons:
                message.icon = type_icons[message.message_type]
            else:
                message.icon = role_icons.get(message.role, "fa-comment")

    @api.depends("role")
    def _compute_css_class(self):
        """Assign CSS class for chat bubble styling."""
        for message in self:
            if message.role == "user":
                message.css_class = "o_copilot_message_user"
            elif message.role == "assistant":
                message.css_class = "o_copilot_message_assistant"
            else:
                message.css_class = "o_copilot_message_system"

    @api.model_create_multi
    def create(self, vals_list):
        """Generate mock assistant response for user messages."""
        messages = super().create(vals_list)

        # Auto-generate mock responses for user questions (prototype behavior)
        for message in messages:
            if message.role == "user" and message.session_id:
                self._generate_mock_response(message)

        return messages

    def _generate_mock_response(self, user_message):
        """Generate a mock assistant response for demonstration.

        In production, this would:
        - Call the configured AI provider
        - Apply prompt templates based on intent
        - Include context from the bound record
        - Stream the response
        """
        # Simple keyword-based mock responses
        body_lower = user_message.body.lower()

        if "summar" in body_lower:
            response_body = (
                "**Summary (Mock)**\n\n"
                "This record contains the following key information:\n"
                "- Status: Active\n"
                "- Created: Recently\n"
                "- Owner: Current User\n\n"
                "*This is a mock response for prototype demonstration.*"
            )
            response_type = "explanation"
        elif "kpi" in body_lower or "metric" in body_lower:
            response_body = (
                "**KPI Summary (Mock)**\n\n"
                "| Metric | Value | Trend |\n"
                "|--------|-------|-------|\n"
                "| Progress | 75% | +5% |\n"
                "| On-time | Yes | Stable |\n"
                "| Budget | Within | -2% |\n\n"
                "*This is a mock KPI summary for prototype demonstration.*"
            )
            response_type = "kpi_summary"
        elif "explain" in body_lower or "what" in body_lower or "why" in body_lower:
            response_body = (
                "**Explanation (Mock)**\n\n"
                "Based on the current context, this record represents a "
                "standard workflow item. The key points to understand are:\n\n"
                "1. The record follows standard processing rules\n"
                "2. All required fields are properly filled\n"
                "3. No blocking issues detected\n\n"
                "*This is a mock explanation for prototype demonstration.*"
            )
            response_type = "explanation"
        elif "navigate" in body_lower or "go to" in body_lower or "show" in body_lower:
            response_body = (
                "**Navigation Suggestion (Mock)**\n\n"
                "To view related information, you can:\n\n"
                "- Click the **Related Records** smart button above\n"
                "- Open **Reporting > Analytics** from the main menu\n"
                "- Use the search bar with filter: `status:active`\n\n"
                "*This is a mock navigation hint for prototype demonstration.*"
            )
            response_type = "navigation_hint"
        else:
            response_body = (
                "**Assistant Response (Mock)**\n\n"
                "I understand your question. In a production environment, "
                "I would analyze the current record context and provide "
                "specific, actionable insights.\n\n"
                "Try asking me to:\n"
                "- Summarize this record\n"
                "- Show KPIs and metrics\n"
                "- Explain a specific field\n"
                "- Navigate to related information\n\n"
                "*This is a mock response for prototype demonstration.*"
            )
            response_type = "suggestion"

        # Create the mock response
        self.create({
            "session_id": user_message.session_id.id,
            "role": "assistant",
            "message_type": response_type,
            "body": response_body,
            "mock_confidence": 0.92,
            "mock_latency_ms": 380,
            "mock_tokens": len(response_body.split()),
        })

        # Update session mock token count
        user_message.session_id.mock_tokens_used += len(response_body.split()) + len(
            user_message.body.split()
        )
