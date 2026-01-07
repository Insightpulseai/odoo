# -*- coding: utf-8 -*-
"""
AI Provider Service - Unified API for multiple AI providers.

Supports:
- Kapa RAG (retrieval-augmented generation)
- OpenAI / ChatGPT
- Google Gemini
- Ollama (local)
"""
import json
import logging
import time

import requests

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IpaiAiProviderService(models.AbstractModel):
    _name = "ipai.ai.provider.service"
    _description = "IPAI AI Provider Service"

    # =========================================================================
    # Configuration Getters
    # =========================================================================
    def _get_config(self, key, default=None):
        """Get system parameter value."""
        return self.env["ir.config_parameter"].sudo().get_param(key, default)

    def _get_default_provider(self):
        """Get the configured default provider."""
        return self._get_config("ipai.default_provider", "openai")

    # =========================================================================
    # Provider Test Methods
    # =========================================================================
    @api.model
    def test_provider(self, provider_type):
        """Test connectivity for a specific provider."""
        test_methods = {
            "openai": self._test_openai,
            "gemini": self._test_gemini,
            "kapa": self._test_kapa,
            "ollama": self._test_ollama,
        }

        method = test_methods.get(provider_type)
        if not method:
            raise UserError(_("Unknown provider type: %s") % provider_type)

        try:
            result = method()
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Connection Successful"),
                    "message": result,
                    "type": "success",
                    "sticky": False,
                },
            }
        except Exception as e:
            _logger.exception("Provider test failed: %s", provider_type)
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Connection Failed"),
                    "message": str(e),
                    "type": "danger",
                    "sticky": True,
                },
            }

    def _test_openai(self):
        """Test OpenAI API connection."""
        api_key = self._get_config("ipai.openai.api_key")
        if not api_key:
            raise UserError(_("OpenAI API key not configured"))

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        org_id = self._get_config("ipai.openai.org_id")
        if org_id:
            headers["OpenAI-Organization"] = org_id

        # Test with models endpoint (minimal tokens)
        resp = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        models_count = len(resp.json().get("data", []))
        return _("OpenAI connected. %d models available.") % models_count

    def _test_gemini(self):
        """Test Google Gemini API connection."""
        api_key = self._get_config("ipai.gemini.api_key")
        if not api_key:
            raise UserError(_("Gemini API key not configured"))

        # Test with models list endpoint
        resp = requests.get(
            f"https://generativelanguage.googleapis.com/v1/models?key={api_key}",
            timeout=10,
        )
        resp.raise_for_status()
        models_data = resp.json().get("models", [])
        return _("Gemini connected. %d models available.") % len(models_data)

    def _test_kapa(self):
        """Test Kapa RAG API connection."""
        api_key = self._get_config("ipai.kapa.api_key")
        base_url = self._get_config("ipai.kapa.base_url", "https://api.kapa.ai")
        project_id = self._get_config("ipai.kapa.project_id")

        if not api_key:
            raise UserError(_("Kapa API key not configured"))
        if not project_id:
            raise UserError(_("Kapa Project ID not configured"))

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Health check endpoint
        resp = requests.get(
            f"{base_url.rstrip('/')}/health",
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 404:
            # Try project info as fallback
            return _("Kapa API reachable (project: %s)") % project_id

        resp.raise_for_status()
        return _("Kapa RAG connected successfully.")

    def _test_ollama(self):
        """Test Ollama local server connection."""
        base_url = self._get_config("ipai.ollama.base_url", "http://localhost:11434")

        resp = requests.get(
            f"{base_url.rstrip('/')}/api/tags",
            timeout=5,
        )
        resp.raise_for_status()
        models = resp.json().get("models", [])
        return _("Ollama connected. %d models installed.") % len(models)

    # =========================================================================
    # Chat Completion Methods
    # =========================================================================
    @api.model
    def chat(self, messages, provider=None, **kwargs):
        """
        Send chat completion request to configured provider.

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            provider: Override default provider (openai, gemini, kapa, ollama)
            **kwargs: Provider-specific options (temperature, max_tokens, etc.)

        Returns:
            dict with 'content', 'provider', 'model', 'usage'
        """
        provider = provider or self._get_default_provider()

        chat_methods = {
            "openai": self._chat_openai,
            "gemini": self._chat_gemini,
            "kapa": self._chat_kapa,
            "ollama": self._chat_ollama,
        }

        method = chat_methods.get(provider)
        if not method:
            raise UserError(_("Unknown provider: %s") % provider)

        start_time = time.time()
        result = method(messages, **kwargs)
        result["latency_ms"] = int((time.time() - start_time) * 1000)

        # Update provider stats
        self._update_provider_stats(provider, result)

        return result

    def _chat_openai(self, messages, **kwargs):
        """OpenAI chat completion."""
        api_key = self._get_config("ipai.openai.api_key")
        if not api_key:
            raise UserError(_("OpenAI API key not configured"))

        model = kwargs.get("model") or self._get_config("ipai.openai.model", "gpt-4o")
        temperature = kwargs.get("temperature") or float(
            self._get_config("ipai.openai.temperature", "0.7")
        )
        max_tokens = kwargs.get("max_tokens") or int(
            self._get_config("ipai.openai.max_tokens", "4096")
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        org_id = self._get_config("ipai.openai.org_id")
        if org_id:
            headers["OpenAI-Organization"] = org_id

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()

        return {
            "content": data["choices"][0]["message"]["content"],
            "provider": "openai",
            "model": model,
            "usage": data.get("usage", {}),
        }

    def _chat_gemini(self, messages, **kwargs):
        """Google Gemini chat completion."""
        api_key = self._get_config("ipai.gemini.api_key")
        if not api_key:
            raise UserError(_("Gemini API key not configured"))

        model = kwargs.get("model") or self._get_config(
            "ipai.gemini.model", "gemini-1.5-pro"
        )
        temperature = kwargs.get("temperature") or float(
            self._get_config("ipai.gemini.temperature", "0.7")
        )
        max_tokens = kwargs.get("max_tokens") or int(
            self._get_config("ipai.gemini.max_tokens", "8192")
        )

        # Convert OpenAI-style messages to Gemini format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            if msg["role"] == "system":
                # Prepend system message to first user message
                continue
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        # Add system instruction if present
        system_msg = next((m for m in messages if m["role"] == "system"), None)

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        if system_msg:
            payload["systemInstruction"] = {"parts": [{"text": system_msg["content"]}]}

        url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"

        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        content = ""
        if data.get("candidates"):
            parts = data["candidates"][0].get("content", {}).get("parts", [])
            content = "".join(p.get("text", "") for p in parts)

        return {
            "content": content,
            "provider": "gemini",
            "model": model,
            "usage": data.get("usageMetadata", {}),
        }

    def _chat_kapa(self, messages, **kwargs):
        """Kapa RAG chat completion."""
        api_key = self._get_config("ipai.kapa.api_key")
        base_url = self._get_config("ipai.kapa.base_url", "https://api.kapa.ai")
        project_id = self._get_config("ipai.kapa.project_id")

        if not api_key or not project_id:
            raise UserError(_("Kapa API key and Project ID required"))

        # Extract user query (last user message)
        user_query = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "",
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "query": user_query,
            "project_id": project_id,
            "max_sources": int(self._get_config("ipai.kapa.max_sources", "5")),
        }

        resp = requests.post(
            f"{base_url.rstrip('/')}/query",
            headers=headers,
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()

        # Format response with sources
        answer = data.get("answer", "")
        sources = data.get("sources", [])
        if sources:
            answer += "\n\n**Sources:**\n"
            for src in sources[:5]:
                title = src.get("title", "Source")
                url = src.get("url", "")
                answer += f"- [{title}]({url})\n"

        return {
            "content": answer,
            "provider": "kapa",
            "model": self._get_config("ipai.kapa.model", "gpt-4-turbo"),
            "usage": {"sources_retrieved": len(sources)},
            "sources": sources,
        }

    def _chat_ollama(self, messages, **kwargs):
        """Ollama local chat completion."""
        base_url = self._get_config("ipai.ollama.base_url", "http://localhost:11434")
        model = kwargs.get("model") or self._get_config("ipai.ollama.model", "llama3.1")

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }

        resp = requests.post(
            f"{base_url.rstrip('/')}/api/chat",
            json=payload,
            timeout=300,  # Local models can be slow
        )
        resp.raise_for_status()
        data = resp.json()

        return {
            "content": data.get("message", {}).get("content", ""),
            "provider": "ollama",
            "model": model,
            "usage": {
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
            },
        }

    def _update_provider_stats(self, provider_type, result):
        """Update provider statistics."""
        Provider = self.env["ipai.ai.provider"]
        provider = Provider.search(
            [
                ("company_id", "=", self.env.company.id),
                ("provider_type", "=", provider_type),
                ("active", "=", True),
            ],
            limit=1,
        )
        if provider:
            tokens = result.get("usage", {}).get("total_tokens", 0)
            if not tokens:
                tokens = result.get("usage", {}).get("prompt_tokens", 0) + result.get(
                    "usage", {}
                ).get("completion_tokens", 0)
            provider.update_stats(result.get("latency_ms", 0), tokens)

    # =========================================================================
    # RAG-Specific Methods
    # =========================================================================
    @api.model
    def rag_query(self, query, context_docs=None, provider=None):
        """
        RAG query with optional local document context.

        Args:
            query: User question
            context_docs: List of document snippets for context
            provider: AI provider to use

        Returns:
            dict with response and sources
        """
        provider = provider or self._get_default_provider()

        # If using Kapa, use native RAG
        if provider == "kapa":
            return self.chat(
                [{"role": "user", "content": query}],
                provider="kapa",
            )

        # For other providers, build RAG prompt manually
        system_prompt = """You are a helpful assistant. Answer questions based on the provided context.
If the context doesn't contain relevant information, say so clearly.
Always cite which part of the context you're using."""

        context_text = ""
        if context_docs:
            context_text = "\n\n---\nContext:\n" + "\n\n".join(context_docs)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{query}{context_text}"},
        ]

        return self.chat(messages, provider=provider)
