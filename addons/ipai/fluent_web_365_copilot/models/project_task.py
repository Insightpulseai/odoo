# Copyright 2026 InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):
    """Extend project.task with Copilot integration.

    Adds a smart button to open or create a Copilot session
    bound to this task.
    """

    _inherit = "project.task"

    copilot_session_ids = fields.One2many(
        comodel_name="fluent.copilot.session",
        compute="_compute_copilot_session_ids",
        string="Copilot Sessions",
    )
    copilot_session_count = fields.Integer(
        string="Copilot Sessions",
        compute="_compute_copilot_session_ids",
    )

    @api.depends()
    def _compute_copilot_session_ids(self):
        """Find Copilot sessions bound to this task."""
        for task in self:
            sessions = self.env["fluent.copilot.session"].search([
                ("context_model", "=", "project.task"),
                ("context_res_id", "=", task.id),
            ])
            task.copilot_session_ids = sessions
            task.copilot_session_count = len(sessions)

    def action_open_copilot(self):
        """Open Copilot panel for this task.

        Creates a new active session if none exists, otherwise
        opens the most recent active session.
        """
        self.ensure_one()

        # Find existing active session
        existing_session = self.env["fluent.copilot.session"].search([
            ("context_model", "=", "project.task"),
            ("context_res_id", "=", self.id),
            ("user_id", "=", self.env.user.id),
            ("status", "=", "active"),
        ], limit=1, order="create_date desc")

        if existing_session:
            session = existing_session
        else:
            # Create new session
            session = self.env["fluent.copilot.session"].create({
                "context_model": "project.task",
                "context_res_id": self.id,
                "user_id": self.env.user.id,
                "status": "active",
            })

            # Add system welcome message
            self.env["fluent.copilot.message"].with_context(
                skip_auto_response=True
            ).create({
                "session_id": session.id,
                "role": "system",
                "message_type": "suggestion",
                "body": (
                    f"**Welcome to Copilot!**\n\n"
                    f"I'm here to help you with task: **{self.name}**\n\n"
                    f"You can ask me to:\n"
                    f"- Summarize this task\n"
                    f"- Show progress metrics\n"
                    f"- Explain blockers or dependencies\n"
                    f"- Navigate to related records\n\n"
                    f"*Type your question below to get started.*"
                ),
            })

        return {
            "type": "ir.actions.act_window",
            "name": "Copilot",
            "res_model": "fluent.copilot.session",
            "res_id": session.id,
            "view_mode": "form",
            "target": "new",
            "context": {"form_view_initial_mode": "edit"},
        }

    def action_view_copilot_sessions(self):
        """View all Copilot sessions for this task."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Copilot Sessions",
            "res_model": "fluent.copilot.session",
            "view_mode": "list,form",
            "domain": [
                ("context_model", "=", "project.task"),
                ("context_res_id", "=", self.id),
            ],
            "context": {
                "default_context_model": "project.task",
                "default_context_res_id": self.id,
            },
        }
