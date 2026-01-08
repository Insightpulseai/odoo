# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.http import request

from ..services.retriever import KBRetriever
from ..services.llm_provider import OpenAICompatLLM

_logger = logging.getLogger(__name__)


class IPAIAIAgentsController(http.Controller):
    """
    JSON-RPC endpoints for AI Agents panel.

    Endpoints:
    - /ipai_ai_agents/bootstrap: Get available agents for current user/company
    - /ipai_ai_agents/ask: Submit a question and get a grounded answer
    - /ipai_ai_agents/feedback: Submit feedback on a message
    """

    @http.route("/ipai_ai_agents/bootstrap", type="json", auth="user")
    def bootstrap(self):
        """
        Bootstrap endpoint: returns available agents and user context.
        Called when the AI panel loads.
        """
        Agent = request.env["ipai.ai.agent"].sudo()
        agents = Agent.search([
            ("enabled", "=", True),
            "|",
            ("company_id", "=", request.env.company.id),
            ("company_id", "=", False),
        ])
        return {
            "agents": agents.read(["name", "system_prompt", "model", "provider", "read_only"]),
            "user": {
                "id": request.env.user.id,
                "name": request.env.user.name,
            },
            "company": {
                "id": request.env.company.id,
                "name": request.env.company.name,
            },
        }

    @http.route("/ipai_ai_agents/ask", type="json", auth="user")
    def ask(self, agent_id, message, thread_id=None, context=None):
        """
        Ask endpoint: process a user question through RAG pipeline.

        Args:
            agent_id: ID of the agent to use
            message: User's question text
            thread_id: Optional existing thread ID to continue conversation
            context: Optional context dict {res_model, res_id} for record-specific questions

        Returns:
            {ok: bool, thread_id: int, messages: list, error: str}
        """
        if not message or not str(message).strip():
            return {"ok": False, "error": "Empty message."}

        env = request.env
        Agent = env["ipai.ai.agent"].sudo()
        Thread = env["ipai.ai.thread"].sudo()
        Message = env["ipai.ai.message"].sudo()

        # Validate agent
        agent = Agent.browse(int(agent_id))
        if not agent.exists() or not agent.enabled:
            return {"ok": False, "error": "Agent not found or disabled."}
        if agent.company_id and agent.company_id.id != env.company.id:
            return {"ok": False, "error": "Agent not available for this company."}

        # Get or create thread
        if thread_id:
            thread = Thread.browse(int(thread_id))
            if not thread.exists() or thread.user_id.id != env.user.id:
                return {"ok": False, "error": "Thread not found."}
        else:
            thread_vals = {
                "agent_id": agent.id,
                "user_id": env.user.id,
                "company_id": env.company.id,
            }
            if context:
                thread_vals["res_model"] = context.get("res_model")
                thread_vals["res_id"] = context.get("res_id")
            thread = Thread.create(thread_vals)

        # Store user message
        Message.create({
            "thread_id": thread.id,
            "role": "user",
            "content": str(message).strip(),
        })

        try:
            # Retrieval (citations)
            retriever = KBRetriever.from_env()
            evidence = retriever.retrieve(
                tenant_ref=self._tenant_ref(env),
                query=str(message).strip(),
                limit=8,
            )
        except Exception as e:
            _logger.warning("Retrieval failed: %s", e)
            evidence = []

        try:
            # LLM answer
            llm = OpenAICompatLLM.from_env(default_model=agent.model or "gpt-4o-mini")
            answer = llm.answer(
                system_prompt=agent.system_prompt or self._default_system_prompt(),
                user_message=str(message).strip(),
                evidence=evidence,
            )
        except Exception as e:
            _logger.error("LLM call failed: %s", e)
            # Store error response
            Message.create({
                "thread_id": thread.id,
                "role": "assistant",
                "content": f"I apologize, but I encountered an error processing your request. Please try again or contact support.\n\nError: {str(e)[:200]}",
                "is_uncertain": True,
                "confidence": 0.0,
            })
            return {
                "ok": True,
                "thread_id": thread.id,
                "messages": thread.message_ids.read([
                    "role", "content", "citations_json", "confidence", "is_uncertain", "create_date"
                ]),
            }

        # Store assistant message
        Message.create({
            "thread_id": thread.id,
            "role": "assistant",
            "content": answer.get("answer_markdown", ""),
            "citations_json": answer.get("citations", []),
            "confidence": answer.get("confidence", 0.0),
            "is_uncertain": bool(answer.get("is_uncertain", False)),
        })

        return {
            "ok": True,
            "thread_id": thread.id,
            "messages": thread.message_ids.read([
                "role", "content", "citations_json", "confidence", "is_uncertain", "create_date"
            ]),
        }

    @http.route("/ipai_ai_agents/feedback", type="json", auth="user")
    def feedback(self, message_id, feedback, reason=None):
        """
        Feedback endpoint: record user feedback on a message.

        Args:
            message_id: ID of the message to provide feedback on
            feedback: 'positive' or 'negative'
            reason: Optional text explaining the feedback

        Returns:
            {ok: bool, error: str}
        """
        if feedback not in ("positive", "negative"):
            return {"ok": False, "error": "Invalid feedback value."}

        Message = request.env["ipai.ai.message"].sudo()
        msg = Message.browse(int(message_id))

        if not msg.exists():
            return {"ok": False, "error": "Message not found."}

        # Verify user owns the thread
        if msg.thread_id.user_id.id != request.env.user.id:
            return {"ok": False, "error": "Not authorized to provide feedback on this message."}

        msg.write({
            "feedback": feedback,
            "feedback_reason": reason,
        })

        return {"ok": True}

    @http.route("/ipai_ai_agents/threads", type="json", auth="user")
    def list_threads(self, agent_id=None, limit=20, offset=0):
        """
        List threads endpoint: get user's conversation history.

        Args:
            agent_id: Optional filter by agent
            limit: Max threads to return
            offset: Pagination offset

        Returns:
            {ok: bool, threads: list, total: int}
        """
        Thread = request.env["ipai.ai.thread"].sudo()
        domain = [("user_id", "=", request.env.user.id)]
        if agent_id:
            domain.append(("agent_id", "=", int(agent_id)))

        total = Thread.search_count(domain)
        threads = Thread.search(domain, limit=limit, offset=offset)

        return {
            "ok": True,
            "threads": threads.read(["display_name", "agent_id", "message_count", "create_date"]),
            "total": total,
        }

    def _default_system_prompt(self):
        return (
            "You are an in-product help assistant. "
            "Rules:\n"
            "- Use the provided evidence snippets when answering.\n"
            "- Cite sources for any factual claim using the citation list.\n"
            "- If evidence is insufficient, say you don't know and ask a clarifying question.\n"
            "- Never invent URLs or citations.\n"
        )

    def _tenant_ref(self, env):
        """
        Generate a stable tenant reference for KB retrieval.
        Maps Odoo company to Supabase tenant_ref.
        """
        return f"odoo_company:{env.company.id}"
