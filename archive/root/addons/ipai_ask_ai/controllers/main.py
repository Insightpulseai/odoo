# -*- coding: utf-8 -*-
"""
Ask AI Controllers

HTTP controllers for AI chat functionality.
"""

import json
import logging

from odoo.http import request

from odoo import http

_logger = logging.getLogger(__name__)


class AskAIController(http.Controller):
    """
    Controller for Ask AI HTTP endpoints.
    """

    @http.route("/ai/generate_response", type="json", auth="user")
    def generate_response(self, message_body, channel_id=None, context=None):
        """
        Generate AI response for a user message.

        Args:
            message_body: User's message text
            channel_id: Optional channel ID
            context: Optional context dict

        Returns:
            dict: AI response data
        """
        try:
            ai_service = request.env["ipai.ask.ai.service"]
            result = ai_service.process_query(message_body, context or {})

            return {
                "success": result.get("success", False),
                "response": result.get("response", ""),
                "data": result.get("data"),
                "records": result.get("records"),
                "action": result.get("action"),
            }

        except Exception as e:
            _logger.exception("Error generating AI response: %s", str(e))
            return {
                "success": False,
                "response": "I encountered an error. Please try again.",
                "error": str(e),
            }

    @http.route("/ai/channel/create", type="json", auth="user")
    def create_ai_channel(self):
        """
        Create or get the AI chat channel for the current user.

        Returns:
            dict: Channel data
        """
        try:
            Channel = request.env["discuss.channel"]
            result = Channel.create_ai_draft_channel()
            return result

        except Exception as e:
            _logger.exception("Error creating AI channel: %s", str(e))
            return {
                "error": str(e),
            }

    @http.route("/ai/channel/message", type="json", auth="user")
    def post_message(self, channel_id, message_body, context=None):
        """
        Post a message to the AI channel and get response.

        Args:
            channel_id: The channel ID
            message_body: User's message
            context: Optional context

        Returns:
            dict: Message result with AI response
        """
        try:
            channel = request.env["discuss.channel"].browse(channel_id)

            if not channel.exists():
                return {"error": "Channel not found"}

            result = channel.ai_message_post(message_body, context)
            return result

        except Exception as e:
            _logger.exception("Error posting AI message: %s", str(e))
            return {
                "error": str(e),
            }

    @http.route("/ai/capabilities", type="json", auth="user")
    def get_capabilities(self):
        """
        Get the AI assistant's capabilities.

        Returns:
            dict: List of capabilities and examples
        """
        return {
            "capabilities": [
                {
                    "category": "Customers",
                    "examples": [
                        "Do I have any customers in Japan?",
                        "How many customers do I have?",
                        "Find customers from France",
                    ],
                },
                {
                    "category": "Sales",
                    "examples": [
                        "Sales this month",
                        "How many orders this week?",
                        "Total sales this year",
                    ],
                },
                {
                    "category": "Invoices",
                    "examples": [
                        "Show unpaid invoices",
                        "Outstanding amount",
                        "Overdue invoices",
                    ],
                },
                {
                    "category": "Tasks",
                    "examples": [
                        "My assigned tasks",
                        "Overdue tasks",
                        "What's on my todo?",
                    ],
                },
            ],
            "version": "1.0.0",
        }
