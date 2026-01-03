# -*- coding: utf-8 -*-
"""
Ask AI Service Model

Provides the core AI service functionality for processing
natural language queries and generating contextual responses.
"""

import json
import logging
import re
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

_logger = logging.getLogger(__name__)


class IpaiAskAIService(models.TransientModel):
    """
    AI Service for processing user queries.

    This transient model handles:
    - Natural language query processing
    - Context extraction from current view/model
    - Database queries based on user intent
    - Response generation with business data
    """
    _name = "ipai.ask.ai.service"
    _description = "Ask AI Service"

    @api.model
    def process_query(self, query, context=None):
        """
        Process a natural language query and return AI response.

        Args:
            query: User's natural language question
            context: Optional context dict with model, view, etc.

        Returns:
            dict: Response with message, data, and status
        """
        if context is None:
            context = {}

        _logger.info("Processing AI query: %s", query[:100])

        try:
            # Parse the query intent
            intent = self._parse_query_intent(query)

            # Execute based on intent type
            if intent["type"] == "search":
                result = self._execute_search_query(intent, context)
            elif intent["type"] == "count":
                result = self._execute_count_query(intent, context)
            elif intent["type"] == "aggregate":
                result = self._execute_aggregate_query(intent, context)
            elif intent["type"] == "rag":
                result = self._generate_rag_response(query, context)
            elif intent["type"] == "help":
                result = self._generate_help_response(intent)
            else:
                result = self._generate_generic_response(query, context)

            return {
                "success": True,
                "response": result["message"],
                "data": result.get("data"),
                "records": result.get("records"),
                "action": result.get("action"),
                "intent": intent,
            }

        except AccessError as e:
            _logger.warning("Access denied for AI query: %s", str(e))
            return {
                "success": False,
                "response": _("I don't have permission to access that information."),
                "error": str(e),
            }
        except Exception as e:
            _logger.exception("Error processing AI query: %s", str(e))
            return {
                "success": False,
                "response": _("I encountered an error processing your request. Please try again."),
                "error": str(e),
            }

    def _parse_query_intent(self, query):
        """
        Parse the user's query to determine intent.

        Returns:
            dict: Intent type, model, domain, fields
        """
        query_lower = query.lower().strip()

        # Common patterns for business queries
        patterns = {
            # Customer/Partner queries
            r"(customers?|partners?|contacts?)\s*(in|from)\s+(\w+)": {
                "type": "search",
                "model": "res.partner",
                "field": "country_id.name",
            },
            r"(how many|count)\s+(customers?|partners?|contacts?)": {
                "type": "count",
                "model": "res.partner",
            },
            r"(any|do i have)\s+(customers?|partners?)\s*(in|from)\s+(\w+)": {
                "type": "search",
                "model": "res.partner",
                "field": "country_id.name",
            },
            # Sales queries
            r"(sales?|orders?)\s*(this|last)\s+(month|week|year)": {
                "type": "aggregate",
                "model": "sale.order",
                "period": True,
            },
            r"(how many|count)\s+(sales?|orders?)": {
                "type": "count",
                "model": "sale.order",
            },
            # Invoice queries
            r"(invoices?|bills?)\s*(due|overdue|pending)": {
                "type": "search",
                "model": "account.move",
                "filter": "due",
            },
            r"(unpaid|outstanding)\s+(invoices?|amount)": {
                "type": "aggregate",
                "model": "account.move",
                "filter": "unpaid",
            },
            # Task/Project queries
            r"(my|assigned)\s+(tasks?|todo)": {
                "type": "search",
                "model": "project.task",
                "filter": "my_tasks",
            },
            r"(overdue|late)\s+(tasks?)": {
                "type": "search",
                "model": "project.task",
                "filter": "overdue",
            },
            # Help queries
            r"(help|what can you do|capabilities)": {
                "type": "help",
            },
        }

        # Try to match patterns
        for pattern, intent_template in patterns.items():
            match = re.search(pattern, query_lower)
        if match:
                intent = intent_template.copy()
                intent["query"] = query
                intent["match"] = match.groups() if match.groups() else []
                return intent

        # Fallback to Generative AI (RAG)
        return {
            "type": "rag",
            "query": query,
            "match": [],
        }

    def _execute_search_query(self, intent, context):
        """Execute a search query based on parsed intent."""
        model_name = intent.get("model", "res.partner")

        # Check if model exists and is accessible
        if model_name not in self.env:
            return {
                "message": _("I couldn't find the requested information."),
                "records": [],
            }

        Model = self.env[model_name]
        domain = []

        # Build domain based on intent
        if intent.get("field") and intent.get("match"):
            field = intent["field"]
            value = intent["match"][-1] if intent["match"] else ""
            if value:
                domain.append((field, "ilike", value))

        # Add context-based filters
        if intent.get("filter") == "my_tasks" and model_name == "project.task":
            domain.append(("user_ids", "in", [self.env.uid]))

        if intent.get("filter") == "overdue" and model_name == "project.task":
            domain.append(("date_deadline", "<", fields.Date.today()))
            domain.append(("stage_id.fold", "=", False))

        # Execute search
        try:
            records = Model.search_read(domain, limit=10)
            count = Model.search_count(domain)
        except AccessError:
            return {
                "message": _("I don't have permission to access that data."),
                "records": [],
            }

        if not records:
            # Try to provide helpful response
            search_term = intent["match"][-1] if intent.get("match") else ""
            return {
                "message": _("I couldn't find any %s%s.") % (
                    model_name.replace(".", " ").replace("_", " "),
                    " matching '%s'" % search_term if search_term else "",
                ),
                "records": [],
            }

        # Format response
        record_names = [r.get("display_name", r.get("name", "Unnamed")) for r in records[:5]]
        message = _("I found %d %s") % (count, model_name.replace(".", " ").replace("_", " "))

        if count <= 5:
            message += ": " + ", ".join(record_names)
        else:
            message += ". Here are the first 5: " + ", ".join(record_names)

        # Build action to open records
        action = {
            "type": "ir.actions.act_window",
            "res_model": model_name,
            "view_mode": "list,form",
            "domain": domain,
            "name": _("Search Results"),
        }

        return {
            "message": message,
            "records": records[:10],
            "count": count,
            "action": action,
        }

    def _execute_count_query(self, intent, context):
        """Execute a count query based on parsed intent."""
        model_name = intent.get("model", "res.partner")

        if model_name not in self.env:
            return {"message": _("I couldn't count the requested items.")}

        Model = self.env[model_name]
        domain = []

        # Add common filters
        if model_name == "res.partner":
            domain.append(("customer_rank", ">", 0))

        try:
            count = Model.search_count(domain)
        except AccessError:
            return {"message": _("I don't have permission to access that data.")}

        model_display = model_name.replace(".", " ").replace("_", " ")
        return {
            "message": _("You have %d %s in the system.") % (count, model_display),
            "data": {"count": count, "model": model_name},
        }

    def _execute_aggregate_query(self, intent, context):
        """Execute an aggregate query (sums, averages, etc.)."""
        model_name = intent.get("model", "sale.order")

        if model_name not in self.env:
            return {"message": _("I couldn't calculate the requested data.")}

        Model = self.env[model_name]
        domain = []

        # Time period filters
        if intent.get("period"):
            today = fields.Date.today()
            match = intent.get("match", [])
            period = match[-1] if match else "month"

            if period == "month":
                start_date = today.replace(day=1)
            elif period == "week":
                start_date = today - timedelta(days=today.weekday())
            elif period == "year":
                start_date = today.replace(month=1, day=1)
            else:
                start_date = today - timedelta(days=30)

            domain.append(("date_order", ">=", start_date))

        # Invoice filters
        if intent.get("filter") == "unpaid" and model_name == "account.move":
            domain.extend([
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("payment_state", "!=", "paid"),
                ("state", "=", "posted"),
            ])

        try:
            records = Model.search(domain)

            if model_name == "sale.order":
                total = sum(records.mapped("amount_total"))
                count = len(records)
                message = _("You have %d orders totaling %s this period.") % (
                    count, self._format_currency(total)
                )
            elif model_name == "account.move":
                total = sum(records.mapped("amount_residual"))
                count = len(records)
                message = _("You have %d unpaid invoices totaling %s.") % (
                    count, self._format_currency(total)
                )
            else:
                count = len(records)
                message = _("Found %d records matching your query.") % count

            return {
                "message": message,
                "data": {"count": count, "total": total if "total" in dir() else 0},
            }

        except AccessError:
            return {"message": _("I don't have permission to access that data.")}
        except Exception as e:
            _logger.exception("Aggregate query error: %s", str(e))
            return {"message": _("I encountered an error calculating that data.")}

    def _generate_help_response(self, intent):
        """Generate a help response listing capabilities."""
        capabilities = [
            _("• Find customers by country: 'Do I have any customers in Japan?'"),
            _("• Count records: 'How many customers do I have?'"),
            _("• Sales summary: 'Sales this month'"),
            _("• Unpaid invoices: 'Show unpaid invoices'"),
            _("• My tasks: 'Show my assigned tasks'"),
            _("• Overdue tasks: 'What tasks are overdue?'"),
        ]

        message = _("Hello! I can help you with:\n\n") + "\n".join(capabilities)
        message += _("\n\nJust ask me a question about your business data!")

        return {"message": message}

    def _generate_generic_response(self, query, context):
        """Generate a generic response for unrecognized queries."""
        return {
            "message": _(
                "I'm not sure how to answer that question. "
                "Try asking about customers, sales, invoices, or tasks. "
                "Type 'help' to see what I can do."
            ),
        }

    def _format_currency(self, amount, currency=None):
        """Format amount as currency string."""
        if currency is None:
            currency = self.env.company.currency_id
        return "%s %.2f" % (currency.symbol or "$", amount)

    @api.model
    def get_or_create_ai_channel(self):
        """
        Get or create the AI chat channel for the current user.

        Returns:
            discuss.channel: The AI channel for the user
        """
        Channel = self.env["discuss.channel"]
        user = self.env.user
        partner = user.partner_id

        # Look for existing AI channel
        existing = Channel.search([
            ("name", "=", "Ask AI"),
            ("channel_partner_ids", "in", [partner.id]),
            ("channel_type", "=", "chat"),
        ], limit=1)

        if existing:
            return existing

        # Create new AI channel
        ai_partner = self._get_or_create_ai_partner()

        channel = Channel.create({
            "name": "Ask AI",
            "channel_type": "chat",
            "channel_partner_ids": [(4, partner.id), (4, ai_partner.id)],
        })

        # Post welcome message
        channel.message_post(
            body=_("Hello! I'm your AI assistant. Ask me anything about your business data."),
            author_id=ai_partner.id,
            message_type="comment",
        )

        return channel

    @api.model
    def _get_or_create_ai_partner(self):
        """Get or create the AI bot partner."""
        ai_partner = self.env.ref("ipai_ask_ai.partner_ask_ai", raise_if_not_found=False)

        if not ai_partner:
            ai_partner = self.env["res.partner"].sudo().create({
                "name": "Ask AI",
                "email": "ai@insightpulseai.net",
                "is_company": False,
                "type": "contact",
                "active": True,
            })

        return ai_partner

    def _generate_rag_response(self, query, context):
        """Generate a response using the external RAG service (Copilot)."""
        import requests
        
        api_url = self.env['ir.config_parameter'].sudo().get_param('ipai_copilot.api_url')
        api_key = self.env['ir.config_parameter'].sudo().get_param('ipai_copilot.api_key')
        
        if not api_url:
            return {
                "message": _("AI Configuration Error: Copilot API URL is not set. Please check Settings."),
                "data": {}
            }
            
        try:
           payload = {
               "message": query,
               "odoo": {
                   "uid": self.env.uid,
                   "db": self.env.cr.dbname,
                   "context": context
               }
           }
           
           headers = {"Content-Type": "application/json"}
           if api_key:
               headers["Authorization"] = f"Bearer {api_key}"
               
           response = requests.post(api_url, json=payload, headers=headers, timeout=30)
           
           if response.status_code != 200:
               _logger.error("Copilot API Error: %s - %s", response.status_code, response.text)
               return {
                   "message": _("I'm having trouble connecting to my brain. (Error %s)") % response.status_code
               }
               
           data = response.json()
           answer = data.get("answer", _("I couldn't generate an answer."))
           citations = data.get("citations", [])
           
           # Append citations to message if present
           if citations:
               citation_text = "\n\nSources:\n" + "\n".join([f"- [{c.get('title', 'Link')}]({c.get('url', '#')})" for c in citations])
               answer += citation_text
               
           return {
               "message": answer,
               "data": {"citations": citations}
           }
           
        except Exception as e:
            _logger.exception("RAG connection error: %s", str(e))
            return {
                "message": _("I encountered a connection error while thinking. Please try again later.")
            }
