from __future__ import annotations
import os
import json
import requests
from tenacity import retry, stop_after_attempt, wait_exponential


class LlmClient:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
        self.model = os.getenv("LLM_MODEL", "").strip()
        if not self.model:
            raise ValueError("LLM_MODEL is required")
        self.timeout = int(os.getenv("LLM_HTTP_TIMEOUT", "60"))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def complete_json(self, prompt: str) -> dict:
        if self.provider == "openai":
            return self._openai(prompt)
        if self.provider == "anthropic":
            return self._anthropic(prompt)
        if self.provider == "gemini":
            return self._gemini(prompt)
        raise ValueError(f"Unsupported LLM_PROVIDER: {self.provider}")

    def _openai(self, prompt: str) -> dict:
        # Uses Chat Completions compatible endpoint.
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is required for openai provider")

        url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=self.timeout)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        return json.loads(content)

    def _anthropic(self, prompt: str) -> dict:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY is required for anthropic provider")

        url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1/messages")
        headers = {
            "x-api-key": key,
            "anthropic-version": os.getenv("ANTHROPIC_VERSION", "2023-06-01"),
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "max_tokens": int(os.getenv("ANTHROPIC_MAX_TOKENS", "2048")),
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        }
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=self.timeout)
        r.raise_for_status()
        content = r.json()["content"][0]["text"]
        return json.loads(content)

    def _gemini(self, prompt: str) -> dict:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY is required for gemini provider")

        # Gemini REST endpoint (text-only).
        model = self.model
        url = os.getenv(
            "GEMINI_BASE_URL",
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
        )
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0, "response_mime_type": "application/json"},
        }
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=self.timeout)
        r.raise_for_status()
        # Extract first candidate text
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)
