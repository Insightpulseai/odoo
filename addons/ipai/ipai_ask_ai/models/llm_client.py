# -*- coding: utf-8 -*-
"""
LLM Client Service.

Provides abstraction layer for various LLM providers.
"""
import json
import logging
import time

from odoo import api, models

_logger = logging.getLogger(__name__)


class LlmClientService(models.AbstractModel):
    """
    LLM Client Service.

    Supports:
    - OpenAI (GPT-4, GPT-3.5)
    - Azure OpenAI
    - Mock (for testing)
    """

    _name = "llm.client.service"
    _description = "LLM Client Service"

    SYSTEM_PROMPT = """You are an AI assistant for the InsightPulse Finance team.
You help with month-end close, tax compliance, and expense management tasks.

Your role is to:
1. Answer questions about finance tasks and deadlines
2. Summarize blocking issues and priorities
3. Provide guidance on expense policies
4. Help understand BIR tax compliance requirements

Be concise, professional, and action-oriented in your responses.
When referencing specific tasks or deadlines, include relevant details.
If you don't have enough information, ask clarifying questions."""

    @api.model
    def get_provider(self):
        """Get configured LLM provider"""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ask_ai.provider", "mock")
        )

    @api.model
    def get_api_key(self):
        """Get LLM API key"""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ask_ai.api_key", "")
        )

    @api.model
    def get_model_name(self):
        """Get configured model name"""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ask_ai.model", "gpt-4")
        )

    @api.model
    def get_endpoint(self):
        """Get API endpoint (for Azure)"""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ask_ai.endpoint", "")
        )

    @api.model
    def generate_response(self, query, context=None, conversation_history=None):
        """
        Generate AI response for a query.

        Args:
            query: User's question
            context: Dict of RAG context (from afc.rag.service)
            conversation_history: List of previous messages

        Returns:
            dict: {
                'success': bool,
                'response': str,
                'tokens_used': int,
                'latency': float,
                'model': str,
                'error': str (if failed)
            }
        """
        provider = self.get_provider()
        start_time = time.time()

        try:
            if provider == "mock":
                result = self._generate_mock(query, context)
            elif provider == "openai":
                result = self._generate_openai(query, context, conversation_history)
            elif provider == "azure":
                result = self._generate_azure(query, context, conversation_history)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown LLM provider: {provider}",
                }

            result["latency"] = time.time() - start_time
            return result

        except Exception as e:
            _logger.error("LLM generation error: %s", str(e))
            return {
                "success": False,
                "error": str(e),
                "latency": time.time() - start_time,
            }

    @api.model
    def _generate_mock(self, query, context):
        """
        Generate mock response for testing.

        Provides realistic responses based on query keywords.
        """
        query_lower = query.lower()
        model = "mock-v1"

        # Blocking tasks query
        if "blocking" in query_lower or "overdue" in query_lower:
            if context and context.get("blocking_tasks"):
                bt = context["blocking_tasks"]
                total = bt.get("total", 0)
                by_owner = bt.get("by_owner", {})

                if total == 0:
                    response = "Good news! There are no blocking tasks at the moment. All month-end close tasks are on track."
                else:
                    parts = [f"There are **{total} blocking tasks** that need attention:\n"]
                    for owner, tasks in by_owner.items():
                        parts.append(f"\n**{owner}** has {len(tasks)} overdue task(s):")
                        for t in tasks:
                            parts.append(f"  - {t['name']} ({t['days_overdue']} days overdue)")
                    parts.append("\n\nRecommendation: Prioritize the oldest overdue items first.")
                    response = "\n".join(parts)
            else:
                response = "I don't have current blocking task data. Please ensure the Finance PPM module is properly configured."

        # Deadline query
        elif "deadline" in query_lower or "due" in query_lower:
            if context and context.get("upcoming_deadlines"):
                deadlines = context["upcoming_deadlines"]
                if deadlines:
                    parts = ["Here are the upcoming deadlines:\n"]
                    for d in deadlines:
                        parts.append(f"- **{d['name']}**: Due {d['deadline']} ({d['days_until']} days) - Assigned to {d['owner']}")
                    response = "\n".join(parts)
                else:
                    response = "No upcoming deadlines found in the next 7 days."
            else:
                response = "I couldn't retrieve deadline information. Please check the task configuration."

        # Summary/priorities query
        elif "summary" in query_lower or "priorities" in query_lower or "today" in query_lower:
            parts = ["## Today's Finance Summary\n"]

            if context and context.get("finance_kpis"):
                kpi = context["finance_kpis"]
                parts.append(f"**Overall Progress:** {kpi.get('completion_rate', 0)}% complete")
                parts.append(f"- Tasks completed: {kpi.get('completed', 0)}/{kpi.get('total_tasks', 0)}")
                parts.append(f"- Overdue: {kpi.get('overdue', 0)}")
                parts.append(f"- In progress: {kpi.get('in_progress', 0)}")
                parts.append("")

            if context and context.get("blocking_tasks"):
                bt = context["blocking_tasks"]
                if bt.get("total", 0) > 0:
                    parts.append(f"**Priority Items:** {bt['total']} blocking tasks need attention")

            if context and context.get("upcoming_deadlines"):
                deadlines = context["upcoming_deadlines"]
                today_tasks = [d for d in deadlines if d.get("days_until") == 0]
                if today_tasks:
                    parts.append(f"\n**Due Today:** {len(today_tasks)} task(s)")
                    for t in today_tasks:
                        parts.append(f"  - {t['name']}")

            response = "\n".join(parts)

        # BIR/Tax query
        elif "bir" in query_lower or "tax" in query_lower:
            if context and context.get("bir_deadlines"):
                deadlines = context["bir_deadlines"]
                if deadlines:
                    parts = ["## Upcoming BIR Deadlines\n"]
                    for d in deadlines:
                        parts.append(f"- **{d['form']}**: {d['deadline']}")
                    response = "\n".join(parts)
                else:
                    response = "No BIR deadlines found in the next 30 days."
            else:
                response = "BIR deadline data is not available. Please ensure the BIR compliance module is configured."

        # Expense query
        elif "expense" in query_lower:
            if context and context.get("expense_summary"):
                es = context["expense_summary"]
                response = f"""## Expense Summary ({es.get('month', 'Current Month')})

- **Pending:** {es.get('pending', 0)} expenses awaiting submission
- **Submitted:** {es.get('submitted', 0)} awaiting approval
- **Approved:** {es.get('approved', 0)}"""
                if es.get("needs_ocr_review"):
                    response += f"\n- **Needs OCR Review:** {es['needs_ocr_review']}"
            else:
                response = "I couldn't retrieve expense data. Please check the Expense module."

        # Generic response
        else:
            response = f"""I can help you with:

1. **Blocking Tasks** - Ask "What's blocking the close?"
2. **Deadlines** - Ask "What are the upcoming deadlines?"
3. **Daily Summary** - Ask "What are today's priorities?"
4. **BIR Compliance** - Ask "What are the BIR deadlines?"
5. **Expenses** - Ask "What's the expense status?"

How can I assist you today?"""

        return {
            "success": True,
            "response": response,
            "tokens_used": len(response.split()) * 2,  # Rough estimate
            "model": model,
        }

    @api.model
    def _generate_openai(self, query, context, conversation_history):
        """Generate response using OpenAI API"""
        import requests

        api_key = self.get_api_key()
        model = self.get_model_name()

        if not api_key:
            return {"success": False, "error": "OpenAI API key not configured"}

        # Build messages
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Add context if available
        if context:
            rag_service = self.env["afc.rag.service"]
            context_text = rag_service.format_context_for_prompt(context)
            messages.append(
                {
                    "role": "system",
                    "content": f"Current context:\n\n{context_text}",
                }
            )

        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current query
        messages.append({"role": "user", "content": query})

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.7,
                },
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data["choices"][0]["message"]["content"],
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                    "model": model,
                }
            else:
                return {
                    "success": False,
                    "error": f"OpenAI API error: {response.status_code} - {response.text}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @api.model
    def _generate_azure(self, query, context, conversation_history):
        """Generate response using Azure OpenAI API"""
        import requests

        api_key = self.get_api_key()
        endpoint = self.get_endpoint()
        model = self.get_model_name()

        if not api_key or not endpoint:
            return {"success": False, "error": "Azure OpenAI not configured"}

        # Build messages (same as OpenAI)
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        if context:
            rag_service = self.env["afc.rag.service"]
            context_text = rag_service.format_context_for_prompt(context)
            messages.append(
                {
                    "role": "system",
                    "content": f"Current context:\n\n{context_text}",
                }
            )

        if conversation_history:
            for msg in conversation_history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": query})

        try:
            url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version=2024-02-15-preview"
            response = requests.post(
                url,
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.7,
                },
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data["choices"][0]["message"]["content"],
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                    "model": f"azure/{model}",
                }
            else:
                return {
                    "success": False,
                    "error": f"Azure API error: {response.status_code}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @api.model
    def ask(self, query, res_model=None, res_id=None):
        """
        Main entry point for Ask AI.

        Retrieves context, generates response, and saves to conversation.

        Args:
            query: User's question
            res_model: Optional related model
            res_id: Optional related record ID

        Returns:
            dict: Response with conversation metadata
        """
        # Get or create conversation
        Conversation = self.env["ask.ai.conversation"]
        Message = self.env["ask.ai.message"]
        RagService = self.env["afc.rag.service"]

        conversation = Conversation.get_or_create_conversation(res_model, res_id)

        # Save user message
        Message.create_user_message(conversation.id, query)

        # Get conversation history
        history = [
            {"role": m.role, "content": m.content}
            for m in conversation.message_ids
            if m.role in ("user", "assistant")
        ]

        # Retrieve context
        context = RagService.retrieve_context(query)

        # Generate response
        result = self.generate_response(query, context, history)

        if result.get("success"):
            # Save assistant message
            Message.create_assistant_message(
                conversation.id,
                result["response"],
                sources=context.get("sources"),
                tokens=result.get("tokens_used", 0),
                latency=result.get("latency", 0),
                model=result.get("model"),
            )

        return {
            "success": result.get("success", False),
            "response": result.get("response", ""),
            "conversation_id": conversation.id,
            "error": result.get("error"),
        }
