# -*- coding: utf-8 -*-
"""
OpenAI-compatible LLM provider for AI Agents.

Supports OpenAI, Azure OpenAI, and any provider with compatible API surface.
"""
import json
import logging
import os
from typing import Any, Dict, List

_logger = logging.getLogger(__name__)

try:
    import requests
except ImportError:
    requests = None


class OpenAICompatLLM:
    """
    OpenAI-compatible Chat Completions provider.

    Environment variables:
    - IPAI_LLM_BASE_URL: API base URL (default: https://api.openai.com/v1)
    - IPAI_LLM_API_KEY: API key (required)
    - IPAI_LLM_MODEL: Default model (default: gpt-4o-mini)
    - IPAI_LLM_TEMPERATURE: Temperature (default: 0.2)
    """

    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    @classmethod
    def from_env(cls, default_model: str = "gpt-4o-mini") -> "OpenAICompatLLM":
        """Create LLM provider from environment variables."""
        base_url = (
            os.environ.get("IPAI_LLM_BASE_URL") or "https://api.openai.com/v1"
        ).strip()
        api_key = (os.environ.get("IPAI_LLM_API_KEY") or "").strip()
        model = (os.environ.get("IPAI_LLM_MODEL") or default_model).strip()

        if not api_key:
            raise RuntimeError("Missing IPAI_LLM_API_KEY env var.")

        return cls(base_url, api_key, model)

    def answer(
        self, system_prompt: str, user_message: str, evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate an answer with citations.

        Returns:
            {
                answer_markdown: str,
                citations: list[{index, title, url, score}],
                confidence: float,
                is_uncertain: bool,
                followups: list[str]
            }
        """
        if not requests:
            raise RuntimeError("Python package 'requests' is required for LLM calls.")

        prompt = self._build_prompt(system_prompt, user_message, evidence)
        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]},
            ],
            "temperature": float(os.environ.get("IPAI_LLM_TEMPERATURE", "0.2")),
        }

        resp = requests.post(
            endpoint, headers=headers, data=json.dumps(body), timeout=60
        )
        if resp.status_code >= 300:
            raise RuntimeError(f"LLM error {resp.status_code}: {resp.text[:1000]}")

        data = resp.json()
        content = (data.get("choices") or [{}])[0].get("message", {}).get(
            "content"
        ) or ""

        # Try to parse structured JSON response
        try:
            parsed = json.loads(content)
            return self._normalize(parsed, evidence)
        except Exception:
            # Fallback: wrap as markdown with citations from evidence
            _logger.info("LLM response not JSON, wrapping as markdown")
            return {
                "answer_markdown": content,
                "citations": self._citations_from_evidence(evidence),
                "confidence": 0.5 if evidence else 0.25,
                "is_uncertain": len(evidence) < 2,
                "followups": [],
            }

    def _build_prompt(
        self, system_prompt: str, user_message: str, evidence: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Build the system and user prompts with evidence."""
        citations = self._citations_from_evidence(evidence)
        evidence_block = []

        for i, c in enumerate(citations, start=1):
            snippet = (c.get("snippet") or "").strip()
            if len(snippet) > 900:
                snippet = snippet[:900] + "…"
            evidence_block.append(
                f"[{i}] title={c.get('title') or ''}\n"
                f"url={c.get('url') or ''}\n"
                f"score={c.get('score')}\n---\n{snippet}\n"
            )

        evidence_text = (
            "\n".join(evidence_block) if evidence_block else "(no evidence found)"
        )

        system = (
            system_prompt.strip()
            + "\n\nYou MUST output a single JSON object with keys:\n"
            "- answer_markdown (string)\n"
            "- citations (array of {index,title,url,score}) ONLY from the evidence provided\n"
            "- confidence (number 0..1)\n"
            "- is_uncertain (boolean)\n"
            "- followups (array of strings)\n"
            "Rules:\n"
            "- If evidence is missing/weak, set is_uncertain=true and confidence<=0.4.\n"
            "- Do not invent URLs. Do not cite anything not in evidence.\n"
        )
        user = (
            f"User question:\n{user_message}\n\n"
            f"Evidence snippets:\n{evidence_text}\n\n"
            "Return JSON only."
        )
        return {"system": system, "user": user}

    def _citations_from_evidence(
        self, evidence: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Convert evidence chunks to citation format."""
        out = []
        for e in evidence or []:
            out.append(
                {
                    "title": e.get("title"),
                    "url": e.get("url"),
                    "score": e.get("score"),
                    "snippet": e.get("content"),
                }
            )
        return out

    def _normalize(
        self, obj: Dict[str, Any], evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Normalize the LLM JSON response."""
        citations = obj.get("citations") or []
        norm_cites = []

        for i, c in enumerate(citations, start=1):
            norm_cites.append(
                {
                    "index": int(c.get("index") or i),
                    "title": c.get("title"),
                    "url": c.get("url"),
                    "score": float(c.get("score") or 0.0),
                }
            )

        return {
            "answer_markdown": obj.get("answer_markdown") or "",
            "citations": norm_cites,
            "confidence": float(obj.get("confidence") or 0.0),
            "is_uncertain": bool(obj.get("is_uncertain", False)),
            "followups": obj.get("followups") or [],
        }
