# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiCopilotMixin(models.AbstractModel):
    """Mixin to add Ask AI functionality to any model.

    Inherit this mixin in models where you want the Ask AI button:

        class AccountMove(models.Model):
            _name = "account.move"
            _inherit = ["account.move", "ipai.copilot.mixin"]
    """

    _name = "ipai.copilot.mixin"
    _description = "AI Copilot Mixin"

    ai_session_ids = fields.One2many(
        "ipai.ai.thread",
        compute="_compute_ai_session_ids",
        string="AI Sessions",
    )
    ai_session_count = fields.Integer(
        compute="_compute_ai_session_ids",
        string="AI Sessions",
    )

    def _compute_ai_session_ids(self):
        """Compute AI sessions related to this record."""
        Thread = self.env["ipai.ai.thread"]
        model = self.env["ir.model"].search([("model", "=", self._name)], limit=1)

        for rec in self:
            if model and rec.id:
                sessions = Thread.search(
                    [
                        ("model_id", "=", model.id),
                        ("res_id", "=", rec.id),
                    ]
                )
                rec.ai_session_ids = sessions
                rec.ai_session_count = len(sessions)
            else:
                rec.ai_session_ids = Thread
                rec.ai_session_count = 0

    def action_open_ai_copilot(self):
        """Open AI copilot sidebar/wizard for this record."""
        self.ensure_one()

        # Get or create a session for this record
        model = self.env["ir.model"].search([("model", "=", self._name)], limit=1)
        provider = self.env["ipai.ai.provider"].get_default()

        if not provider:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "No AI Provider",
                    "message": "Please configure an AI provider in Settings → AI Providers",
                    "type": "warning",
                },
            }

        # Find existing active session or create new
        session = self.env["ipai.ai.thread"].search(
            [
                ("model_id", "=", model.id),
                ("res_id", "=", self.id),
                ("state", "=", "active"),
                ("user_id", "=", self.env.user.id),
            ],
            limit=1,
        )

        if not session:
            session = self.env["ipai.ai.thread"].create(
                {
                    "provider_id": provider.id,
                    "model_id": model.id,
                    "res_id": self.id,
                }
            )

        return {
            "name": "Ask AI",
            "type": "ir.actions.act_window",
            "res_model": "ipai.ai.thread",
            "res_id": session.id,
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_model_id": model.id,
                "default_res_id": self.id,
            },
        }

    def action_view_ai_sessions(self):
        """View all AI sessions for this record."""
        self.ensure_one()
        model = self.env["ir.model"].search([("model", "=", self._name)], limit=1)

        return {
            "name": "AI Sessions",
            "type": "ir.actions.act_window",
            "res_model": "ipai.ai.thread",
            "view_mode": "list,form",
            "domain": [
                ("model_id", "=", model.id),
                ("res_id", "=", self.id),
            ],
            "context": {
                "default_model_id": model.id,
                "default_res_id": self.id,
            },
        }

    @api.model
    def _is_ai_enabled(self):
        """Check if AI is enabled for this model.

        Models must be listed in System Parameter 'ipai.allow_ai_on_models'
        as a comma-separated list.
        """
        allowed_models = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai.allow_ai_on_models", "")
        )
        if not allowed_models:
            return False
        return self._name in [m.strip() for m in allowed_models.split(",")]

    def get_ai_context(self):
        """Get context data for AI prompting.

        Override in specific models to provide relevant context.

        Returns:
            dict with context data for the AI
        """
        self.ensure_one()
        return {
            "model": self._name,
            "model_description": self._description,
            "record_id": self.id,
            "record_name": self.display_name,
            "user": self.env.user.name,
            "company": self.env.company.name,
        }


class IpaiAiThreadExtension(models.Model):
    """Extend AI Thread with model binding fields."""

    _inherit = "ipai.ai.thread"

    model_id = fields.Many2one(
        "ir.model",
        string="Related Model",
        index=True,
    )
    res_id = fields.Integer(
        string="Related Record ID",
        index=True,
    )
    res_name = fields.Char(
        string="Related Record",
        compute="_compute_res_name",
    )

    @api.depends("model_id", "res_id")
    def _compute_res_name(self):
        for rec in self:
            if rec.model_id and rec.res_id:
                try:
                    record = self.env[rec.model_id.model].browse(rec.res_id)
                    rec.res_name = record.display_name if record.exists() else False
                except Exception:
                    rec.res_name = False
            else:
                rec.res_name = False
