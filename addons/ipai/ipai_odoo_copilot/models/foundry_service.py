# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

import json
import logging
import time

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)

FOUNDRY_TIMEOUT = 30
POLL_INTERVAL = 0.5
MAX_POLL_TIME = 30

SYSTEM_PROMPT = """You are Pulser, the InsightPulseAI operational intelligence assistant inside Odoo.

Rules:
- You help users navigate Odoo workflows, understand records, and make decisions.
- You can read the current record context provided to you.
- You CANNOT modify records directly — suggest actions the user should take.
- Use canonical naming: InsightPulseAI, Pulser, Odoo on Cloud.
- Never say "Odoo Copilot", "IPAI Copilot", or "Copilot" as your name.
- Keep answers concise and actionable (2-4 sentences).
- If you don't know, say so. Don't hallucinate Odoo data.
- You are in authenticated mode — the user is logged into Odoo."""


class FoundryService(models.AbstractModel):
    """Bridge to Azure AI Foundry Agent Service (OpenAI Assistants API).

    Uses the Assistants API with threads and runs for conversation management.
    Config parameters:
      - ipai_copilot.foundry_endpoint: Azure OpenAI endpoint
      - ipai_copilot.foundry_api_key: API key
      - ipai_copilot.foundry_agent_id: Assistant ID (asst_*)
    """

    _name = "ipai.foundry.service"
    _description = "Azure AI Foundry Agent Bridge"

    # --- Settings ---

    def _get_settings(self):
        """Get Foundry service configuration."""
        ICP = self.env["ir.config_parameter"].sudo()
        return {
            "enabled": ICP.get_param(
                "ipai_copilot.enabled", "False"
            ).lower() in ("true", "1"),
            "endpoint": ICP.get_param("ipai_copilot.foundry_endpoint", ""),
            "api_key": ICP.get_param("ipai_copilot.foundry_api_key", ""),
            "agent_id": ICP.get_param("ipai_copilot.foundry_agent_id", ""),
            "api_version": ICP.get_param(
                "ipai_copilot.foundry_api_version", "2024-10-01-preview"
            ),
        }

    # --- Context ---

    def _build_context_envelope(self, user_id=None, record_model=None,
                                 record_id=None, surface="erp"):
        """Build context envelope for Foundry agent."""
        env = self.env
        user = env["res.users"].browse(user_id) if user_id else env.user
        envelope = {
            "surface": surface,
            "user_name": user.name,
            "user_login": user.login,
            "company": env.company.name,
        }
        if record_model and record_id:
            try:
                record = env[record_model].browse(int(record_id))
                if record.exists():
                    envelope["record_model"] = record_model
                    envelope["record_id"] = record_id
                    if hasattr(record, "display_name"):
                        envelope["record_name"] = record.display_name
                    if hasattr(record, "state"):
                        envelope["record_state"] = record.state
            except Exception:
                pass
        return envelope

    # --- Chat ---

    @api.model
    def chat_completion(self, user_message, user_id=None,
                        history=None, context_envelope=None):
        """Send a message to Foundry and get a response.

        Returns the assistant's reply text, or None on failure.
        Falls back to a simple completion if Assistants API fails.
        """
        settings = self._get_settings()
        if not settings["enabled"]:
            return None

        endpoint = settings["endpoint"]
        api_key = settings["api_key"]
        agent_id = settings["agent_id"]
        api_version = settings["api_version"]

        if not all([endpoint, api_key, agent_id]):
            _logger.warning(
                "Foundry not fully configured: endpoint=%s agent=%s",
                bool(endpoint), bool(agent_id),
            )
            return self._fallback_response(user_message)

        try:
            return self._assistants_api_chat(
                endpoint, api_key, agent_id, api_version,
                user_message, context_envelope,
            )
        except Exception as e:
            _logger.error("Foundry Assistants API error: %s", e)
            # Fallback to simple chat completion
            try:
                return self._simple_chat_completion(
                    endpoint, api_key, api_version,
                    user_message, context_envelope,
                )
            except Exception as e2:
                _logger.error("Foundry simple completion fallback error: %s", e2)
                return self._fallback_response(user_message)

    def _assistants_api_chat(self, endpoint, api_key, agent_id,
                              api_version, message, context_envelope):
        """Use OpenAI Assistants API (threads + runs)."""
        base_url = f"{endpoint}/openai"
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
        }

        # Create thread
        thread_resp = requests.post(
            f"{base_url}/threads?api-version={api_version}",
            headers=headers,
            json={},
            timeout=FOUNDRY_TIMEOUT,
        )
        thread_resp.raise_for_status()
        thread_id = thread_resp.json()["id"]

        # Build context instruction
        instructions = SYSTEM_PROMPT
        if context_envelope:
            instructions += f"\n\nCurrent context: {json.dumps(context_envelope)}"

        # Add user message
        requests.post(
            f"{base_url}/threads/{thread_id}/messages?api-version={api_version}",
            headers=headers,
            json={"role": "user", "content": message},
            timeout=FOUNDRY_TIMEOUT,
        )

        # Create run
        run_resp = requests.post(
            f"{base_url}/threads/{thread_id}/runs?api-version={api_version}",
            headers=headers,
            json={
                "assistant_id": agent_id,
                "instructions": instructions,
            },
            timeout=FOUNDRY_TIMEOUT,
        )
        run_resp.raise_for_status()
        run = run_resp.json()

        # Poll for completion
        deadline = time.time() + MAX_POLL_TIME
        status = run["status"]
        while status in ("queued", "in_progress"):
            if time.time() > deadline:
                raise TimeoutError("Foundry run timed out")
            time.sleep(POLL_INTERVAL)
            poll_resp = requests.get(
                f"{base_url}/threads/{thread_id}/runs/{run['id']}"
                f"?api-version={api_version}",
                headers=headers,
                timeout=FOUNDRY_TIMEOUT,
            )
            status = poll_resp.json()["status"]

        if status != "completed":
            raise RuntimeError(f"Foundry run failed: {status}")

        # Get latest assistant message
        msgs_resp = requests.get(
            f"{base_url}/threads/{thread_id}/messages"
            f"?api-version={api_version}&order=desc&limit=1",
            headers=headers,
            timeout=FOUNDRY_TIMEOUT,
        )
        msgs_data = msgs_resp.json()
        assistant_msg = next(
            (m for m in msgs_data.get("data", []) if m["role"] == "assistant"),
            None,
        )
        if not assistant_msg:
            return None

        return assistant_msg["content"][0]["text"]["value"]

    def _simple_chat_completion(self, endpoint, api_key, api_version,
                                 message, context_envelope):
        """Fallback: use simple chat completions API."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if context_envelope:
            messages.append({
                "role": "system",
                "content": f"Context: {json.dumps(context_envelope)}",
            })
        messages.append({"role": "user", "content": message})

        resp = requests.post(
            f"{endpoint}/openai/deployments/gpt-4.1/chat/completions"
            f"?api-version={api_version}",
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
            },
            json={
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7,
            },
            timeout=FOUNDRY_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _fallback_response(self, message):
        """Last-resort mock response when Foundry is unreachable."""
        return (
            "I'm Pulser, your operational intelligence assistant. "
            "I'm currently unable to reach the AI service. "
            "Please try again in a moment, or contact support "
            "if the issue persists."
        )
