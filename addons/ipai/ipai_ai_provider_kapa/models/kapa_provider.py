# -*- coding: utf-8 -*-
import json
import logging

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.kapa.ai"
DEFAULT_TIMEOUT = 30


class IpaiAiProviderKapa(models.AbstractModel):
    _name = "ipai.ai.provider.kapa"
    _description = "IPAI AI Provider (Kapa-style RAG)"

    @api.model
    def call(self, prompt, external_thread_id=None, context=None):
        """
        Call the Kapa-style RAG API.

        Args:
            prompt: The user's query
            external_thread_id: Optional existing thread ID for context
            context: Optional dict with additional context

        Returns:
            dict with answer, citations, external_thread_id, confidence, status
        """
        icp = self.env["ir.config_parameter"].sudo()
        base_url = (icp.get_param("ipai.kapa.base_url") or DEFAULT_BASE_URL).rstrip("/")
        api_key = icp.get_param("ipai.kapa.api_key") or ""
        project_id = icp.get_param("ipai.kapa.project_id") or ""

        if not api_key or not project_id:
            raise ValueError(
                "Kapa provider not configured: missing api_key or project_id. "
                "Go to Settings -> IPAI Kapa Provider to configure."
            )

        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Use thread endpoint if we have an external thread ID
        if external_thread_id:
            url = f"{base_url}/api/threads/{external_thread_id}/chat"
            payload = {"query": prompt}
        else:
            url = f"{base_url}/api/chat"
            payload = {"project_id": project_id, "query": prompt}

        # Add optional context
        if context:
            payload["context"] = context

        try:
            _logger.debug("Kapa API call: %s", url)
            r = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                timeout=DEFAULT_TIMEOUT,
            )
            status = str(r.status_code)

            if r.status_code >= 400:
                _logger.warning("Kapa API error: %s - %s", r.status_code, r.text[:200])
                return {
                    "status": status,
                    "answer": f"Provider error (HTTP {r.status_code}).",
                    "citations": [],
                    "confidence": 0.0,
                    "external_thread_id": external_thread_id,
                }

            data = r.json() if r.content else {}
            return self._parse_response(data, external_thread_id, status)

        except requests.Timeout:
            _logger.error("Kapa API timeout after %ds", DEFAULT_TIMEOUT)
            return {
                "status": "timeout",
                "answer": "The AI service timed out. Please try again.",
                "citations": [],
                "confidence": 0.0,
                "external_thread_id": external_thread_id,
            }
        except requests.RequestException as e:
            _logger.exception("Kapa API request failed: %s", e)
            return {
                "status": "error",
                "answer": f"Network error: {str(e)}",
                "citations": [],
                "confidence": 0.0,
                "external_thread_id": external_thread_id,
            }

    def _parse_response(self, data, external_thread_id, status):
        """
        Parse and normalize the Kapa API response.

        Handles various response shapes:
        - answer: data["answer"] or data["output"]["answer"] or data["response"]
        - thread: data["thread_id"] or data["thread"]["id"]
        - citations: data["citations"] or data["output"]["citations"]
        """
        # Extract answer
        answer = (
            data.get("answer")
            or (data.get("output") or {}).get("answer")
            or data.get("response")
            or data.get("text")
            or ""
        )

        # Extract thread ID
        thread_id = (
            data.get("thread_id")
            or (data.get("thread") or {}).get("id")
            or external_thread_id
        )

        # Extract citations
        raw_cites = (
            data.get("citations")
            or (data.get("output") or {}).get("citations")
            or data.get("sources")
            or []
        )

        citations = []
        for c in raw_cites:
            citations.append(
                {
                    "source_id": c.get("source_id") or c.get("id"),
                    "title": c.get("title") or c.get("source") or "",
                    "url": c.get("url") or c.get("link"),
                    "snippet": c.get("snippet")
                    or c.get("text")
                    or c.get("content")
                    or "",
                    "score": float(c.get("score") or c.get("relevance") or 0.0),
                }
            )

        # Extract confidence
        confidence = float(
            data.get("confidence")
            or (data.get("output") or {}).get("confidence")
            or data.get("score")
            or 0.0
        )

        # Extract tokens if available
        tokens = int(
            data.get("tokens") or data.get("usage", {}).get("total_tokens") or 0
        )

        return {
            "status": status,
            "answer": answer,
            "citations": citations,
            "confidence": confidence,
            "external_thread_id": thread_id,
            "tokens": tokens,
        }
