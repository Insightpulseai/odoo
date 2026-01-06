# -*- coding: utf-8 -*-
"""
IPAI AI Agents UI Controllers
=============================

JSON-RPC endpoints for the React + Fluent UI Ask AI panel.

Endpoints:
----------
- /ipai_ai_agents/bootstrap: Initialize panel with available agents
- /ipai_ai_agents/ask: Send message and get AI response with citations
- /ipai_ai_agents/feedback: Submit user feedback on answers

All endpoints require Odoo session authentication (cookie-based).
"""
import os
import json
import logging
from datetime import datetime

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

# Optional: import retriever and LLM services
try:
    import requests as http_requests
except ImportError:
    http_requests = None
    _logger.warning("Python 'requests' package not available; external API calls disabled")


class IPAIAIAgentsController(http.Controller):
    """Controller for AI Agents UI JSON-RPC endpoints."""

    # =========================================================================
    # Bootstrap Endpoint
    # =========================================================================

    @http.route("/ipai_ai_agents/bootstrap", type="json", auth="user")
    def bootstrap(self):
        """
        Initialize the AI panel with available agents and user context.

        Returns:
            dict: {
                agents: List of available agents for this company,
                user: Current user info,
                company: Current company info,
                config: UI configuration
            }
        """
        env = request.env
        Provider = env["ipai.ai.provider"].sudo()

        # Get available providers (agents) for this company
        providers = Provider.search([
            ("active", "=", True),
            "|",
            ("company_id", "=", env.company.id),
            ("company_id", "=", False),
        ])

        agents = []
        for p in providers:
            agents.append({
                "id": p.id,
                "name": p.name,
                "provider_type": p.provider_type,
                "is_default": p.is_default,
            })

        return {
            "agents": agents,
            "user": {
                "id": env.user.id,
                "name": env.user.name,
            },
            "company": {
                "id": env.company.id,
                "name": env.company.name,
            },
            "config": {
                "max_message_length": 4000,
                "supports_streaming": False,  # Future enhancement
            },
        }

    # =========================================================================
    # Ask Endpoint
    # =========================================================================

    @http.route("/ipai_ai_agents/ask", type="json", auth="user")
    def ask(self, provider_id, message, thread_id=None):
        """
        Send a message to the AI agent and get a response.

        Args:
            provider_id: ID of the provider/agent to use
            message: User's question/message
            thread_id: Optional existing thread ID for continuation

        Returns:
            dict: {
                ok: bool,
                thread_id: int,
                messages: List of messages in thread,
                error: Optional error message
            }
        """
        if not message or not str(message).strip():
            return {"ok": False, "error": "Empty message."}

        env = request.env
        Provider = env["ipai.ai.provider"].sudo()
        Thread = env["ipai.ai.thread"].sudo()
        Message = env["ipai.ai.message"].sudo()
        Citation = env["ipai.ai.citation"].sudo()

        # Validate provider
        provider = Provider.browse(int(provider_id))
        if not provider.exists() or not provider.active:
            return {"ok": False, "error": "Provider not found or disabled."}

        # Company isolation check
        if provider.company_id and provider.company_id.id != env.company.id:
            return {"ok": False, "error": "Provider not available for this company."}

        # Get or create thread
        if thread_id:
            thread = Thread.browse(int(thread_id))
            if not thread.exists() or thread.user_id.id != env.user.id:
                return {"ok": False, "error": "Thread not found."}
        else:
            thread = Thread.create({
                "provider_id": provider.id,
                "user_id": env.user.id,
            })

        # Store user message
        user_msg = Message.create({
            "thread_id": thread.id,
            "role": "user",
            "content": str(message).strip(),
        })

        # Get AI response
        try:
            result = self._get_ai_response(provider, thread, str(message).strip())
        except Exception as e:
            _logger.exception("AI response error")
            result = {
                "answer": f"Sorry, I encountered an error: {str(e)[:200]}",
                "citations": [],
                "confidence": 0.0,
                "is_uncertain": True,
            }

        # Store assistant message
        assistant_msg = Message.create({
            "thread_id": thread.id,
            "role": "assistant",
            "content": result.get("answer", ""),
            "confidence": result.get("confidence", 0.0),
            "provider_latency_ms": result.get("latency_ms", 0),
        })

        # Store citations
        for i, cite in enumerate(result.get("citations", []), start=1):
            Citation.create({
                "message_id": assistant_msg.id,
                "rank": i,
                "title": cite.get("title"),
                "url": cite.get("url"),
                "snippet": cite.get("snippet"),
                "score": cite.get("score", 0.0),
            })

        # Return thread messages
        messages = self._format_thread_messages(thread)

        return {
            "ok": True,
            "thread_id": thread.id,
            "messages": messages,
        }

    def _get_ai_response(self, provider, thread, message):
        """
        Get response from AI provider with RAG retrieval.

        This method:
        1. Retrieves relevant evidence from Supabase KB
        2. Constructs prompt with evidence
        3. Calls LLM provider
        4. Parses response and citations

        Returns:
            dict: {answer, citations, confidence, is_uncertain, latency_ms}
        """
        import time
        start_time = time.time()

        # Get tenant reference for KB lookup
        tenant_ref = f"odoo_company:{request.env.company.id}"

        # Retrieve evidence from KB
        evidence = self._retrieve_evidence(tenant_ref, message)

        # Build prompt
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_user_prompt(message, evidence)

        # Call LLM
        llm_result = self._call_llm(system_prompt, user_prompt)

        latency_ms = int((time.time() - start_time) * 1000)

        # Update provider stats
        provider.update_stats(latency_ms, llm_result.get("tokens", 0))

        return {
            "answer": llm_result.get("answer", ""),
            "citations": llm_result.get("citations", []),
            "confidence": llm_result.get("confidence", 0.5),
            "is_uncertain": llm_result.get("is_uncertain", False),
            "latency_ms": latency_ms,
        }

    def _retrieve_evidence(self, tenant_ref, query, limit=8):
        """
        Retrieve relevant evidence from Supabase KB.

        Uses vector search if embeddings are available,
        falls back to text search otherwise.
        """
        if not http_requests:
            return []

        supabase_url = os.environ.get("IPAI_SUPABASE_URL", "").rstrip("/")
        supabase_key = (
            os.environ.get("IPAI_SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("IPAI_SUPABASE_ANON_KEY")
            or ""
        ).strip()

        if not supabase_url or not supabase_key:
            _logger.warning("Supabase not configured; returning empty evidence")
            return []

        # Try embedding-based search first
        embedding = self._get_embedding(query)
        if embedding:
            return self._search_vector(supabase_url, supabase_key, tenant_ref, embedding, limit)
        else:
            return self._search_text(supabase_url, supabase_key, tenant_ref, query, limit)

    def _get_embedding(self, text):
        """Get embedding vector for text using OpenAI API."""
        provider = os.environ.get("IPAI_EMBEDDINGS_PROVIDER", "").lower()
        if provider != "openai":
            return None

        api_key = (
            os.environ.get("IPAI_EMBEDDINGS_API_KEY")
            or os.environ.get("IPAI_LLM_API_KEY")
            or ""
        ).strip()
        if not api_key:
            return None

        base_url = (
            os.environ.get("IPAI_EMBEDDINGS_BASE_URL")
            or os.environ.get("IPAI_LLM_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        model = os.environ.get("IPAI_EMBEDDINGS_MODEL", "text-embedding-3-small")

        try:
            resp = http_requests.post(
                f"{base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": model, "input": text},
                timeout=30,
            )
            if resp.status_code < 300:
                data = resp.json()
                return data["data"][0]["embedding"]
        except Exception as e:
            _logger.warning(f"Embedding request failed: {e}")

        return None

    def _search_vector(self, supabase_url, supabase_key, tenant_ref, embedding, limit):
        """Search KB using vector similarity."""
        try:
            resp = http_requests.post(
                f"{supabase_url}/rest/v1/rpc/search_chunks",
                headers={
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "p_tenant_ref": tenant_ref,
                    "p_query_embedding": embedding,
                    "p_limit": limit,
                },
                timeout=20,
            )
            if resp.status_code < 300:
                return resp.json() or []
        except Exception as e:
            _logger.warning(f"Vector search failed: {e}")

        return []

    def _search_text(self, supabase_url, supabase_key, tenant_ref, query, limit):
        """Fallback text search in KB."""
        try:
            resp = http_requests.post(
                f"{supabase_url}/rest/v1/rpc/search_chunks_text",
                headers={
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "p_tenant_ref": tenant_ref,
                    "p_query": query,
                    "p_limit": limit,
                },
                timeout=20,
            )
            if resp.status_code < 300:
                return resp.json() or []
        except Exception as e:
            _logger.warning(f"Text search failed: {e}")

        return []

    def _get_system_prompt(self):
        """Get system prompt for AI responses."""
        return """You are an AI assistant embedded in Odoo ERP. Your role is to help users with their workflows and answer questions about the system.

IMPORTANT RULES:
1. Use the provided evidence snippets to ground your answers
2. Always cite sources using [1], [2], etc. when referencing evidence
3. If evidence is insufficient, say "I don't have enough information" and set is_uncertain to true
4. Never invent URLs or citations
5. Keep answers concise and actionable
6. If asked about specific records, explain how to find them in Odoo

OUTPUT FORMAT:
You must respond with valid JSON containing:
{
    "answer": "Your markdown-formatted answer with [1] citations",
    "citations": [
        {"index": 1, "title": "Source Title", "url": "https://...", "snippet": "Brief relevant excerpt", "score": 0.95}
    ],
    "confidence": 0.85,
    "is_uncertain": false,
    "followups": ["Optional follow-up question 1"]
}"""

    def _build_user_prompt(self, message, evidence):
        """Build user prompt with evidence context."""
        evidence_text = "\n\n".join([
            f"[{i+1}] {e.get('title', 'Untitled')}\n"
            f"URL: {e.get('url', 'N/A')}\n"
            f"Score: {e.get('score', 0):.2f}\n"
            f"Content:\n{(e.get('content', '')[:500])}"
            for i, e in enumerate(evidence)
        ]) if evidence else "(No evidence found in knowledge base)"

        return f"""User Question:
{message}

Evidence from Knowledge Base:
{evidence_text}

Remember to respond with valid JSON only."""

    def _call_llm(self, system_prompt, user_prompt):
        """Call LLM API and parse response."""
        if not http_requests:
            return self._fallback_response()

        api_key = os.environ.get("IPAI_LLM_API_KEY", "").strip()
        if not api_key:
            return self._fallback_response("LLM API key not configured")

        base_url = os.environ.get("IPAI_LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        model = os.environ.get("IPAI_LLM_MODEL", "gpt-4o-mini")
        temperature = float(os.environ.get("IPAI_LLM_TEMPERATURE", "0.2"))

        try:
            resp = http_requests.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": temperature,
                    "response_format": {"type": "json_object"},
                },
                timeout=60,
            )

            if resp.status_code >= 300:
                _logger.error(f"LLM API error: {resp.status_code} - {resp.text[:500]}")
                return self._fallback_response(f"LLM API error: {resp.status_code}")

            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Parse JSON response
            try:
                parsed = json.loads(content)
                return {
                    "answer": parsed.get("answer", ""),
                    "citations": [
                        {
                            "title": c.get("title"),
                            "url": c.get("url"),
                            "snippet": c.get("snippet"),
                            "score": c.get("score", 0.0),
                        }
                        for c in parsed.get("citations", [])
                    ],
                    "confidence": parsed.get("confidence", 0.5),
                    "is_uncertain": parsed.get("is_uncertain", False),
                    "tokens": data.get("usage", {}).get("total_tokens", 0),
                }
            except json.JSONDecodeError:
                # Fallback: use raw content as answer
                return {
                    "answer": content,
                    "citations": [],
                    "confidence": 0.3,
                    "is_uncertain": True,
                }

        except Exception as e:
            _logger.exception("LLM request failed")
            return self._fallback_response(str(e))

    def _fallback_response(self, reason="Service unavailable"):
        """Return fallback response when LLM is unavailable."""
        return {
            "answer": f"I'm sorry, I couldn't process your request. {reason}. Please try again later or contact support.",
            "citations": [],
            "confidence": 0.0,
            "is_uncertain": True,
        }

    def _format_thread_messages(self, thread):
        """Format thread messages for UI response."""
        messages = []
        for msg in thread.message_ids:
            citations = []
            for cite in msg.citation_ids:
                citations.append({
                    "rank": cite.rank,
                    "title": cite.title,
                    "url": cite.url,
                    "snippet": cite.snippet,
                    "score": cite.score,
                })

            messages.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "confidence": msg.confidence,
                "citations": citations,
                "create_date": msg.create_date.isoformat() if msg.create_date else None,
            })

        return messages

    # =========================================================================
    # Feedback Endpoint
    # =========================================================================

    @http.route("/ipai_ai_agents/feedback", type="json", auth="user")
    def feedback(self, message_id, rating, reason=None):
        """
        Submit user feedback on an AI response.

        Args:
            message_id: ID of the message being rated
            rating: 'helpful' or 'not_helpful'
            reason: Optional text reason

        Returns:
            dict: {ok: bool, error: Optional error message}
        """
        env = request.env
        Message = env["ipai.ai.message"].sudo()

        message = Message.browse(int(message_id))
        if not message.exists():
            return {"ok": False, "error": "Message not found."}

        # Verify user owns the thread
        if message.thread_id.user_id.id != env.user.id:
            return {"ok": False, "error": "Access denied."}

        # Log feedback (could be extended to a dedicated model)
        _logger.info(
            f"AI feedback: message_id={message_id}, rating={rating}, "
            f"user={env.user.id}, reason={reason}"
        )

        return {"ok": True}
