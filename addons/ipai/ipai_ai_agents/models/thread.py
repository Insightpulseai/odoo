# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IPAIAIThread(models.Model):
    _name = "ipai.ai.thread"
    _description = "AI Conversation Thread"
    _order = "create_date desc"
    _rec_name = "display_name"

    name = fields.Char(default="AI Thread")
    display_name = fields.Char(compute="_compute_display_name", store=True)

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    user_id = fields.Many2one(
        "res.users", required=True, default=lambda self: self.env.user, string="User"
    )
    agent_id = fields.Many2one("ipai.ai.agent", required=True, string="Agent")

    message_ids = fields.One2many("ipai.ai.message", "thread_id", string="Messages")
    message_count = fields.Integer(compute="_compute_message_count", string="Messages")

    # Context reference (optional: link thread to a specific record)
    res_model = fields.Char(string="Related Model")
    res_id = fields.Integer(string="Related Record ID")

    @api.depends("name", "agent_id", "create_date")
    def _compute_display_name(self):
        for rec in self:
            agent_name = rec.agent_id.name if rec.agent_id else "AI"
            date_str = (
                rec.create_date.strftime("%Y-%m-%d %H:%M") if rec.create_date else ""
            )
            rec.display_name = f"{agent_name} - {date_str}"

    @api.depends("message_ids")
    def _compute_message_count(self):
        for rec in self:
            rec.message_count = len(rec.message_ids)

    def action_view_messages(self):
        """Open messages for this thread."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Messages - {self.display_name}",
            "res_model": "ipai.ai.message",
            "view_mode": "tree,form",
            "domain": [("thread_id", "=", self.id)],
            "context": {"default_thread_id": self.id},
        }
