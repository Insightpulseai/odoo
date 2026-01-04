# -*- coding: utf-8 -*-
"""
Ask AI Controllers.

REST API endpoints for AI chat functionality.
"""
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class IpaiAskAiController(http.Controller):
    """
    Controller for Ask AI API endpoints.
    """

    @http.route(
        "/ipai/ask_ai/query",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def ask_ai_query(self, prompt, res_model=None, res_id=None, **kwargs):
        """
        Main API endpoint for Ask AI queries.

        Args:
            prompt: User's question
            res_model: Optional related model
            res_id: Optional related record ID

        Returns:
            dict: AI response with metadata
        """
        if not prompt:
            return {"success": False, "error": "Prompt is required"}

        try:
            llm_service = request.env["llm.client.service"]
            result = llm_service.ask(prompt, res_model, res_id)
            return result
        except Exception as e:
            _logger.error("Ask AI error: %s", str(e))
            return {"success": False, "error": str(e)}

    @http.route(
        "/ipai/ask_ai/conversation/<int:conversation_id>",
        type="json",
        auth="user",
        methods=["GET"],
    )
    def get_conversation(self, conversation_id):
        """
        Get conversation history.

        Args:
            conversation_id: ID of the conversation

        Returns:
            dict: Conversation with messages
        """
        conversation = request.env["ask.ai.conversation"].browse(conversation_id)
        if not conversation.exists():
            return {"success": False, "error": "Conversation not found"}

        return {
            "success": True,
            "conversation": {
                "id": conversation.id,
                "name": conversation.name,
                "messages": [
                    {
                        "id": m.id,
                        "role": m.role,
                        "content": m.content,
                        "timestamp": m.create_date.isoformat() if m.create_date else None,
                        "rating": m.rating,
                    }
                    for m in conversation.message_ids
                ],
            },
        }

    @http.route(
        "/ipai/ask_ai/feedback",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def submit_feedback(self, message_id, rating, note=None, **kwargs):
        """
        Submit feedback for an AI response.

        Args:
            message_id: ID of the message to rate
            rating: "1" (bad) or "5" (good)
            note: Optional feedback note

        Returns:
            dict: Success status
        """
        message = request.env["ask.ai.message"].browse(message_id)
        if not message.exists():
            return {"success": False, "error": "Message not found"}

        message.write({"rating": rating, "feedback_note": note})
        return {"success": True}

    @http.route(
        "/ipai/ask_ai/context",
        type="json",
        auth="user",
        methods=["GET"],
    )
    def get_current_context(self, project_id=None, **kwargs):
        """
        Get current RAG context without asking a question.

        Useful for dashboard widgets.

        Args:
            project_id: Optional project to scope context

        Returns:
            dict: Current context data
        """
        rag_service = request.env["afc.rag.service"]
        # Get general context
        context = rag_service.retrieve_context("summary", project_id)
        return {"success": True, "context": context}
