# -*- coding: utf-8 -*-
"""
Ask AI Conversation Model.

Stores Q&A interactions and maintains conversation history.
"""
import json
import logging
from datetime import datetime

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AskAiConversation(models.Model):
    """
    AI Conversation Thread.

    Groups related Q&A interactions into a conversation session.
    """

    _name = "ask.ai.conversation"
    _description = "Ask AI Conversation"
    _order = "create_date desc"

    name = fields.Char(
        string="Title",
        compute="_compute_name",
        store=True,
    )

    user_id = fields.Many2one(
        "res.users",
        string="User",
        default=lambda self: self.env.user,
        required=True,
    )

    message_ids = fields.One2many(
        "ask.ai.message",
        "conversation_id",
        string="Messages",
    )

    message_count = fields.Integer(
        string="Message Count",
        compute="_compute_message_count",
    )

    # Context linking (optional)
    res_model = fields.Char(
        string="Related Model",
        index=True,
        help="Model name if conversation is linked to a specific record",
    )

    res_id = fields.Integer(
        string="Related Record ID",
        index=True,
    )

    active = fields.Boolean(default=True)

    @api.depends("message_ids")
    def _compute_name(self):
        for conv in self:
            first_msg = conv.message_ids.filtered(lambda m: m.role == "user")[:1]
            if first_msg:
                conv.name = first_msg.content[:50] + "..." if len(first_msg.content) > 50 else first_msg.content
            else:
                conv.name = f"Conversation {conv.id}"

    def _compute_message_count(self):
        for conv in self:
            conv.message_count = len(conv.message_ids)

    def action_clear_history(self):
        """Clear all messages in this conversation"""
        self.message_ids.unlink()

    @api.model
    def get_or_create_conversation(self, res_model=None, res_id=None):
        """
        Get existing conversation or create new one.

        Args:
            res_model: Optional model to link to
            res_id: Optional record ID to link to

        Returns:
            ask.ai.conversation record
        """
        domain = [("user_id", "=", self.env.user.id)]
        if res_model and res_id:
            domain.extend([("res_model", "=", res_model), ("res_id", "=", res_id)])
        else:
            domain.extend([("res_model", "=", False), ("res_id", "=", False)])

        conversation = self.search(domain, limit=1)
        if not conversation:
            conversation = self.create(
                {
                    "user_id": self.env.user.id,
                    "res_model": res_model,
                    "res_id": res_id,
                }
            )
        return conversation


class AskAiMessage(models.Model):
    """
    Individual message in an AI conversation.
    """

    _name = "ask.ai.message"
    _description = "Ask AI Message"
    _order = "create_date asc"

    conversation_id = fields.Many2one(
        "ask.ai.conversation",
        string="Conversation",
        required=True,
        ondelete="cascade",
    )

    role = fields.Selection(
        [
            ("user", "User"),
            ("assistant", "AI Assistant"),
            ("system", "System"),
        ],
        string="Role",
        required=True,
    )

    content = fields.Text(
        string="Content",
        required=True,
    )

    # AI Response Metadata
    sources_used = fields.Text(
        string="Context Sources (JSON)",
        help="JSON list of context sources used for this response",
    )

    tokens_used = fields.Integer(
        string="Token Usage",
        help="Number of tokens consumed by this interaction",
    )

    processing_time = fields.Float(
        string="Latency (s)",
        digits=(6, 3),
        help="Time taken to generate response",
    )

    model_used = fields.Char(
        string="Model",
        help="LLM model used for this response",
    )

    # User Feedback
    rating = fields.Selection(
        [
            ("1", "Bad"),
            ("5", "Good"),
        ],
        string="User Feedback",
    )

    feedback_note = fields.Text(
        string="Feedback Note",
    )

    def action_rate_good(self):
        """Mark response as good"""
        self.write({"rating": "5"})

    def action_rate_bad(self):
        """Mark response as bad"""
        self.write({"rating": "1"})

    @api.model
    def create_user_message(self, conversation_id, content):
        """Create a user message"""
        return self.create(
            {
                "conversation_id": conversation_id,
                "role": "user",
                "content": content,
            }
        )

    @api.model
    def create_assistant_message(
        self, conversation_id, content, sources=None, tokens=0, latency=0.0, model=None
    ):
        """Create an assistant message with metadata"""
        return self.create(
            {
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": content,
                "sources_used": json.dumps(sources) if sources else None,
                "tokens_used": tokens,
                "processing_time": latency,
                "model_used": model,
            }
        )
