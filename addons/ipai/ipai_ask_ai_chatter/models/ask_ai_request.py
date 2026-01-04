# -*- coding: utf-8 -*-
"""
Ask AI Request Model.

Stores Q&A interactions linked to specific documents via Chatter.
"""
import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AskAiRequest(models.Model):
    """
    Ask AI Request linked to a document.

    Stores AI interactions that occur within the context of a specific
    document (Invoice, Task, Expense, etc.) via the Chatter widget.
    """

    _name = "ask.ai.request"
    _description = "Ask AI Chatter Request"
    _order = "create_date desc"
    _rec_name = "user_prompt"

    # Context Linking
    res_model = fields.Char(
        string="Related Model",
        required=True,
        index=True,
        help="Model name of the document this request is linked to",
    )

    res_id = fields.Integer(
        string="Related Document ID",
        required=True,
        index=True,
        help="ID of the document in the related model",
    )

    # The Conversation
    user_prompt = fields.Text(
        string="User Query",
        required=True,
    )

    ai_response = fields.Html(
        string="AI Answer",
        readonly=True,
    )

    # RAG Metadata
    sources_used = fields.Text(
        string="Context Sources (JSON)",
        help="JSON list of context sources used for this response",
    )

    tokens_used = fields.Integer(
        string="Token Usage",
        help="Number of tokens consumed",
    )

    processing_time = fields.Float(
        string="Latency (s)",
        digits=(6, 3),
    )

    model_used = fields.Char(
        string="Model",
    )

    # User Feedback
    rating = fields.Selection(
        [
            ("1", "Bad"),
            ("5", "Good"),
        ],
        string="User Feedback",
    )

    user_id = fields.Many2one(
        "res.users",
        string="User",
        default=lambda self: self.env.user,
        readonly=True,
    )

    def action_rate_good(self):
        """Mark response as good"""
        self.write({"rating": "5"})

    def action_rate_bad(self):
        """Mark response as bad"""
        self.write({"rating": "1"})

    @api.model
    def create_from_chatter(self, res_model, res_id, prompt):
        """
        Create a new Ask AI request from Chatter context.

        Args:
            res_model: Model name of the document
            res_id: ID of the document
            prompt: User's question

        Returns:
            dict: Response with request details
        """
        # Get document context
        document_context = self._get_document_context(res_model, res_id)

        # Call LLM service with document context
        llm_service = self.env["llm.client.service"]
        rag_service = self.env["afc.rag.service"]

        # Retrieve RAG context
        context = rag_service.retrieve_context(prompt)

        # Add document-specific context
        context["document"] = document_context

        # Generate response
        result = llm_service.generate_response(prompt, context)

        # Create request record
        request = self.create(
            {
                "res_model": res_model,
                "res_id": res_id,
                "user_prompt": prompt,
                "ai_response": result.get("response", ""),
                "sources_used": json.dumps(context.get("sources", [])),
                "tokens_used": result.get("tokens_used", 0),
                "processing_time": result.get("latency", 0),
                "model_used": result.get("model", ""),
            }
        )

        return {
            "success": result.get("success", False),
            "request_id": request.id,
            "response": result.get("response", ""),
            "error": result.get("error"),
        }

    @api.model
    def _get_document_context(self, res_model, res_id):
        """
        Get context information from the linked document.

        Returns relevant fields based on document type.
        """
        if res_model not in self.env:
            return {}

        try:
            record = self.env[res_model].browse(res_id)
            if not record.exists():
                return {}

            context = {
                "model": res_model,
                "id": res_id,
            }

            # Add common fields if they exist
            if hasattr(record, "name"):
                context["name"] = record.name
            if hasattr(record, "state"):
                context["state"] = record.state
            if hasattr(record, "date"):
                context["date"] = str(record.date) if record.date else None

            # Model-specific fields
            if res_model == "project.task":
                context.update(
                    {
                        "project": record.project_id.name if record.project_id else None,
                        "assignee": record.user_id.name if record.user_id else None,
                        "deadline": str(record.date_deadline) if record.date_deadline else None,
                        "finance_state": record.finance_state if hasattr(record, "finance_state") else None,
                        "is_closing_task": record.is_closing_task if hasattr(record, "is_closing_task") else False,
                        "is_compliance_task": record.is_compliance_task if hasattr(record, "is_compliance_task") else False,
                    }
                )
            elif res_model == "hr.expense":
                context.update(
                    {
                        "amount": record.total_amount_currency if hasattr(record, "total_amount_currency") else None,
                        "employee": record.employee_id.name if record.employee_id else None,
                        "description": record.name,
                    }
                )
            elif res_model == "account.move":
                context.update(
                    {
                        "move_type": record.move_type if hasattr(record, "move_type") else None,
                        "partner": record.partner_id.name if record.partner_id else None,
                        "amount_total": record.amount_total if hasattr(record, "amount_total") else None,
                    }
                )

            return context

        except Exception as e:
            _logger.warning("Could not get document context: %s", str(e))
            return {}

    @api.model
    def get_requests_for_document(self, res_model, res_id):
        """
        Get all Ask AI requests for a specific document.

        Args:
            res_model: Model name
            res_id: Document ID

        Returns:
            list: Request data for display
        """
        requests = self.search(
            [("res_model", "=", res_model), ("res_id", "=", res_id)],
            order="create_date desc",
            limit=20,
        )

        return [
            {
                "id": r.id,
                "prompt": r.user_prompt,
                "response": r.ai_response,
                "rating": r.rating,
                "timestamp": r.create_date.isoformat() if r.create_date else None,
                "user": r.user_id.name if r.user_id else None,
            }
            for r in requests
        ]
