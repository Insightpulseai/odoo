# Copyright 2026 InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FluentCopilotSession(models.Model):
    """A Copilot conversation session tied to a specific context.

    Each session represents a conversation between a user and the Copilot,
    optionally bound to a specific record (e.g., an invoice, task, or lead).

    In production, this would be extended with:
    - Token usage tracking
    - Conversation summarization
    - Privacy/retention policies
    - Multi-turn context management
    """

    _name = "fluent.copilot.session"
    _description = "Copilot Session"
    _order = "create_date desc"
    _inherit = ["mail.thread"]

    name = fields.Char(
        string="Session Title",
        compute="_compute_name",
        store=True,
        readonly=False,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
        help="User who initiated this Copilot session",
    )
    context_model = fields.Char(
        string="Context Model",
        help="Technical name of the model this session is bound to "
        "(e.g., 'account.move', 'project.task')",
    )
    context_res_id = fields.Integer(
        string="Context Record ID",
        help="Database ID of the record this session is bound to",
    )
    context_record_name = fields.Char(
        string="Context Record",
        compute="_compute_context_record_name",
        help="Display name of the bound record",
    )
    started_at = fields.Datetime(
        string="Started At",
        default=fields.Datetime.now,
        required=True,
    )
    ended_at = fields.Datetime(
        string="Ended At",
        help="When the session was closed/archived",
    )
    status = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("archived", "Archived"),
        ],
        string="Status",
        default="active",
        required=True,
        tracking=True,
    )
    message_ids = fields.One2many(
        comodel_name="fluent.copilot.message",
        inverse_name="session_id",
        string="Messages",
    )
    message_count = fields.Integer(
        string="Message Count",
        compute="_compute_message_count",
    )

    # Mock fields for prototype demonstration
    mock_ai_provider = fields.Selection(
        selection=[
            ("mock", "Mock (Demo)"),
            ("openai", "OpenAI GPT"),
            ("anthropic", "Anthropic Claude"),
            ("azure", "Azure OpenAI"),
        ],
        string="AI Provider",
        default="mock",
        help="AI provider for this session (mock in prototype)",
    )
    mock_tokens_used = fields.Integer(
        string="Tokens Used (Mock)",
        default=0,
        help="Simulated token usage for demonstration",
    )

    @api.depends("context_model", "context_res_id", "user_id", "started_at")
    def _compute_name(self):
        """Generate a descriptive session name."""
        for session in self:
            if session.context_model and session.context_res_id:
                model_name = (
                    self.env["ir.model"]
                    .search([("model", "=", session.context_model)], limit=1)
                    .name
                    or session.context_model
                )
                session.name = f"Copilot: {model_name} #{session.context_res_id}"
            else:
                date_str = (
                    session.started_at.strftime("%Y-%m-%d %H:%M")
                    if session.started_at
                    else "New"
                )
                session.name = f"Copilot Session - {date_str}"

    @api.depends("context_model", "context_res_id")
    def _compute_context_record_name(self):
        """Fetch the display name of the bound record."""
        for session in self:
            if session.context_model and session.context_res_id:
                try:
                    record = self.env[session.context_model].browse(
                        session.context_res_id
                    )
                    if record.exists():
                        session.context_record_name = record.display_name
                    else:
                        session.context_record_name = (
                            f"[Deleted] #{session.context_res_id}"
                        )
                except Exception:
                    session.context_record_name = f"[Error] #{session.context_res_id}"
            else:
                session.context_record_name = False

    @api.depends("message_ids")
    def _compute_message_count(self):
        """Count messages in this session."""
        for session in self:
            session.message_count = len(session.message_ids)

    def action_archive(self):
        """Archive the session."""
        self.write(
            {
                "status": "archived",
                "ended_at": fields.Datetime.now(),
            }
        )

    def action_reopen(self):
        """Reopen an archived session."""
        self.write(
            {
                "status": "active",
                "ended_at": False,
            }
        )

    def action_open_context_record(self):
        """Open the bound record in a new window."""
        self.ensure_one()
        if not self.context_model or not self.context_res_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "res_model": self.context_model,
            "res_id": self.context_res_id,
            "view_mode": "form",
            "target": "current",
        }

    def action_send_mock_message(self):
        """Open wizard to send a mock message (prototype action)."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Send Message",
            "res_model": "fluent.copilot.message",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_session_id": self.id,
                "default_role": "user",
            },
        }
