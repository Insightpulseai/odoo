# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

import json
import logging
import os
import time
from datetime import datetime, timezone

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)

FOUNDRY_TIMEOUT = 30
POLL_INTERVAL = 0.5
MAX_POLL_TIME = 60

SYSTEM_PROMPT = """You are Pulser, the InsightPulseAI operational intelligence assistant inside Odoo.

Rules:
- You help users navigate Odoo workflows, understand records, and make decisions.
- You can read the current record context provided to you.
- You CANNOT modify records directly — propose actions via the action queue.
- Use canonical naming: InsightPulseAI, Pulser, Odoo on Cloud.
- Never say "Odoo Copilot", "IPAI Copilot", or "Copilot" as your name.
- Keep answers concise and actionable (2-4 sentences).
- If you don't know, say so. Don't hallucinate Odoo data.
- You are in authenticated mode — the user is logged into Odoo.
- When you use tools, cite the source (e.g., [Odoo docs], [record #123]).
- For write actions, always use propose_action to queue for human approval."""

# ---------------------------------------------------------------------------
# Skill → Tool mapping (loaded from YAML at module init, hardcoded fallback)
# ---------------------------------------------------------------------------
# Skills are intent packs. Each skill maps to one or more Foundry tools.
# The skill router classifies user intent → picks skill → agent uses tools.
SKILL_TOOL_MAP = {
    "odoo_docs_explainer": ["search_odoo_docs", "search_azure_docs"],
    "odoo_module_scaffolder": ["search_odoo_docs", "read_record"],
    "odoo_upgrade_advisor": ["search_odoo_docs", "search_records"],
    "finance_qa": ["read_record", "search_records", "query_fabric_data"],
    "reconciliation_assist": ["read_record", "search_records", "query_fabric_data"],
    "collections_assist": ["read_record", "search_records", "query_fabric_data"],
    "variance_analysis": ["read_record", "search_records", "query_fabric_data"],
    "record_reader": ["read_record", "search_records"],
    "search_docs": ["search_odoo_docs", "search_azure_docs", "search_spec_bundles"],
    "fabric_data_query": ["query_fabric_data"],
    "propose_write": ["propose_action"],
}

# ---------------------------------------------------------------------------
# Tool activity labels — human-safe, operational, no raw reasoning
# ---------------------------------------------------------------------------
TOOL_ACTIVITY_LABELS = {
    "read_record": "Reading Odoo data",
    "search_records": "Searching Odoo records",
    "search_odoo_docs": "Searching Odoo docs",
    "search_azure_docs": "Searching Azure docs",
    "search_databricks_docs": "Searching Databricks docs",
    "search_org_docs": "Searching org docs",
    "search_spec_bundles": "Searching spec bundles",
    "search_architecture_docs": "Searching architecture docs",
    "search_odoo_docs_web": "Searching Odoo docs (web)",
    "query_fabric_data": "Querying Fabric",
    "propose_action": "Drafting proposed action",
    "search_docs": "Searching docs",
    "get_report": "Loading report",
    "read_finance_close": "Reading finance close data",
    "view_campaign_perf": "Loading campaign performance",
    "view_dashboard": "Loading dashboard",
    "search_strategy_docs": "Searching strategy docs",
}

# ---------------------------------------------------------------------------
# Tool function schemas for Foundry agent
# ---------------------------------------------------------------------------
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_record",
            "description": "Read an Odoo record by model and ID. Returns field values.",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name (e.g. 'account.move')",
                    },
                    "record_id": {
                        "type": "integer",
                        "description": "Record ID to read",
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to return (empty = all readable)",
                    },
                },
                "required": ["model", "record_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_records",
            "description": "Search Odoo records by domain filter. Returns matching records.",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name",
                    },
                    "domain": {
                        "type": "array",
                        "description": "Odoo domain filter (list of tuples)",
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to return",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max records (default 10)",
                        "default": 10,
                    },
                },
                "required": ["model", "domain"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_odoo_docs",
            "description": "Search Odoo framework documentation and repo specs via AI Search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for documentation",
                    },
                    "index": {
                        "type": "string",
                        "description": "Index to search: 'odoo-framework' or 'repo-specs'",
                        "enum": ["odoo-framework", "repo-specs"],
                        "default": "odoo-framework",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results (default 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_fabric_data",
            "description": (
                "Query governed business data from Fabric SQL endpoint. "
                "Access gold-layer semantic entities: revenue, aging, KPIs, "
                "budget variance. Returns tabular data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "SQL query against gold-layer views. "
                            "Allowed schemas: gold.*, semantic.*"
                        ),
                    },
                    "max_rows": {
                        "type": "integer",
                        "description": "Max rows to return (default 100)",
                        "default": 100,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "propose_action",
            "description": (
                "Propose a write action for human approval. "
                "Never execute writes directly — always queue for review."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "One-line description of the proposed action",
                    },
                    "target_model": {
                        "type": "string",
                        "description": "Odoo model to act on",
                    },
                    "target_res_id": {
                        "type": "integer",
                        "description": "Record ID (0 for create)",
                        "default": 0,
                    },
                    "action_type": {
                        "type": "string",
                        "enum": ["create", "write", "action"],
                        "description": "Action type",
                    },
                    "payload": {
                        "type": "object",
                        "description": "Values dict or method args",
                    },
                },
                "required": ["summary", "target_model", "action_type", "payload"],
            },
        },
    },
]


def _try_import_agents_sdk():
    """Try to import azure-ai-agents SDK. Returns module or None."""
    try:
        from azure.ai.agents import AgentsClient
        from azure.ai.agents.models import FunctionTool, ToolSet
        from azure.identity import DefaultAzureCredential
        return {
            "AgentsClient": AgentsClient,
            "FunctionTool": FunctionTool,
            "ToolSet": ToolSet,
            "DefaultAzureCredential": DefaultAzureCredential,
        }
    except ImportError:
        return None


class FoundryService(models.AbstractModel):
    """Bridge to Microsoft Foundry Agent Service.

    Supports two modes:
      1. SDK mode (azure-ai-agents >= 1.1.0): Uses AgentsClient with
         FunctionTool definitions, managed identity auth, thread management.
      2. HTTP mode (fallback): Raw Assistants API calls with API key auth.
         Used when SDK is not installed or managed identity unavailable.

    Config parameters:
      - ipai_copilot.foundry_endpoint: Azure AI project endpoint
      - ipai_copilot.foundry_api_key: API key (fallback when no managed identity)
      - ipai_copilot.foundry_agent_id: Agent/Assistant ID
      - ipai_copilot.foundry_api_version: API version
      - ipai_copilot.foundry_auth_mode: 'managed_identity' or 'api_key'
    """

    _name = "ipai.foundry.service"
    _description = "Microsoft Foundry Agent Bridge"

    # --- Activity timeline ---

    @staticmethod
    def _activity(key, label, status="active", meta=None):
        """Create a structured activity event for the UI timeline."""
        return {
            "id": key,
            "label": label,
            "status": status,
            "ts": datetime.now(timezone.utc).isoformat(),
            "meta": meta or {},
        }

    @staticmethod
    def _emit_activity(context_envelope, key, label, status="active",
                       meta=None):
        """Append an activity event to the context envelope's activity list.

        If an activity with the same key already exists, update its status.
        """
        if not isinstance(context_envelope, dict):
            return
        activities = context_envelope.setdefault("_activities", [])
        # Update existing activity if key matches
        for act in activities:
            if act["id"] == key:
                act["status"] = status
                act["ts"] = datetime.now(timezone.utc).isoformat()
                if meta:
                    act["meta"] = meta
                return
        # Append new activity
        activities.append({
            "id": key,
            "label": label,
            "status": status,
            "ts": datetime.now(timezone.utc).isoformat(),
            "meta": meta or {},
        })

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
            "auth_mode": ICP.get_param(
                "ipai_copilot.foundry_auth_mode", "api_key"
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

    # --- SDK Client ---

    def _get_sdk_client(self, settings):
        """Get AgentsClient via SDK with managed identity or API key.

        Returns AgentsClient or None if SDK unavailable.
        """
        sdk = _try_import_agents_sdk()
        if not sdk:
            return None

        endpoint = settings["endpoint"]
        if not endpoint:
            return None

        try:
            if settings["auth_mode"] == "managed_identity":
                credential = sdk["DefaultAzureCredential"]()
                return sdk["AgentsClient"](
                    endpoint=endpoint,
                    credential=credential,
                )
            else:
                # API key auth via AzureKeyCredential
                from azure.core.credentials import AzureKeyCredential
                return sdk["AgentsClient"](
                    endpoint=endpoint,
                    credential=AzureKeyCredential(settings["api_key"]),
                )
        except Exception as e:
            _logger.warning("Failed to create AgentsClient: %s", e)
            return None

    # --- Tool Execution (called when agent invokes tools) ---

    def _execute_tool_call(self, tool_name, arguments, user_id=None,
                           context_envelope=None):
        """Execute a tool call from the Foundry agent.

        Dispatches to the appropriate handler in tool_executor or
        specialized services. Returns the tool output as a string.
        Emits activity events for the UI timeline.
        """
        # Emit tool-start activity
        tool_label = TOOL_ACTIVITY_LABELS.get(tool_name, tool_name)
        self._emit_activity(
            context_envelope, "tool:%s" % tool_name,
            tool_label, "active",
        )

        start = time.time()
        try:
            executor = self.env["ipai.copilot.tool.executor"]
            result = executor.execute_tool(
                tool_name=tool_name,
                arguments=arguments,
                user_id=user_id or self.env.uid,
                context_envelope=context_envelope,
            )
            # Track telemetry
            latency_ms = int((time.time() - start) * 1000)
            self.env["ipai.copilot.telemetry"].track_tool_execution(
                tool_name=tool_name,
                user_id=user_id,
                surface=context_envelope.get("surface", "") if context_envelope else "",
                latency_ms=latency_ms,
            )
            # Mark tool done
            self._emit_activity(
                context_envelope, "tool:%s" % tool_name,
                tool_label, "done",
                meta={"latency_ms": latency_ms},
            )
            return json.dumps(result) if isinstance(result, dict) else str(result)
        except Exception as e:
            _logger.error("Tool execution error (%s): %s", tool_name, e)
            self._emit_activity(
                context_envelope, "tool:%s" % tool_name,
                tool_label, "error",
                meta={"error": str(e)},
            )
            return json.dumps({"error": str(e)})

    # --- Chat (SDK mode) ---

    def _sdk_chat(self, client, settings, user_message, context_envelope):
        """Chat using azure-ai-agents SDK with tool execution loop."""
        sdk = _try_import_agents_sdk()
        agent_id = settings["agent_id"]

        # Build instructions with context
        instructions = SYSTEM_PROMPT
        if context_envelope:
            instructions += f"\n\nCurrent context: {json.dumps(context_envelope)}"

        # Create thread
        thread = client.threads.create()

        # Add user message
        client.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message,
        )

        # Create run with tool definitions
        run = client.runs.create(
            thread_id=thread.id,
            assistant_id=agent_id,
            instructions=instructions,
            tools=TOOL_DEFINITIONS,
        )

        # Poll and handle tool calls
        deadline = time.time() + MAX_POLL_TIME
        while run.status in ("queued", "in_progress", "requires_action"):
            if time.time() > deadline:
                raise TimeoutError("Foundry agent run timed out")

            if run.status == "requires_action":
                # Agent wants to call tools
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for tc in tool_calls:
                    args = json.loads(tc.function.arguments)
                    output = self._execute_tool_call(
                        tool_name=tc.function.name,
                        arguments=args,
                        context_envelope=context_envelope,
                    )
                    tool_outputs.append({
                        "tool_call_id": tc.id,
                        "output": output,
                    })

                run = client.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs,
                )
            else:
                time.sleep(POLL_INTERVAL)
                run = client.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id,
                )

        if run.status != "completed":
            raise RuntimeError(
                "Foundry agent run failed: %s" % run.status
            )

        # Get latest assistant message
        messages = client.messages.list(
            thread_id=thread.id, order="desc", limit=1
        )
        for msg in messages:
            if msg.role == "assistant":
                # Extract text from content blocks
                for block in msg.content:
                    if hasattr(block, "text"):
                        return block.text.value
        return None

    # --- Chat (HTTP fallback mode) ---

    def _http_chat(self, settings, user_message, context_envelope):
        """Chat using raw HTTP Assistants API (fallback when SDK unavailable)."""
        endpoint = settings["endpoint"]
        api_key = settings["api_key"]
        agent_id = settings["agent_id"]
        api_version = settings["api_version"]

        base_url = f"{endpoint}/openai"
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
        }

        # Build instructions with context
        instructions = SYSTEM_PROMPT
        if context_envelope:
            instructions += f"\n\nCurrent context: {json.dumps(context_envelope)}"

        # Create thread
        thread_resp = requests.post(
            f"{base_url}/threads?api-version={api_version}",
            headers=headers,
            json={},
            timeout=FOUNDRY_TIMEOUT,
        )
        thread_resp.raise_for_status()
        thread_id = thread_resp.json()["id"]

        # Add user message
        requests.post(
            f"{base_url}/threads/{thread_id}/messages?api-version={api_version}",
            headers=headers,
            json={"role": "user", "content": user_message},
            timeout=FOUNDRY_TIMEOUT,
        )

        # Create run with tool definitions
        run_resp = requests.post(
            f"{base_url}/threads/{thread_id}/runs?api-version={api_version}",
            headers=headers,
            json={
                "assistant_id": agent_id,
                "instructions": instructions,
                "tools": TOOL_DEFINITIONS,
            },
            timeout=FOUNDRY_TIMEOUT,
        )
        run_resp.raise_for_status()
        run = run_resp.json()

        # Poll and handle tool calls
        deadline = time.time() + MAX_POLL_TIME
        while run["status"] in ("queued", "in_progress", "requires_action"):
            if time.time() > deadline:
                raise TimeoutError("Foundry run timed out")

            if run["status"] == "requires_action":
                tool_calls = (
                    run["required_action"]["submit_tool_outputs"]["tool_calls"]
                )
                tool_outputs = []
                for tc in tool_calls:
                    args = json.loads(tc["function"]["arguments"])
                    output = self._execute_tool_call(
                        tool_name=tc["function"]["name"],
                        arguments=args,
                        context_envelope=context_envelope,
                    )
                    tool_outputs.append({
                        "tool_call_id": tc["id"],
                        "output": output,
                    })

                submit_resp = requests.post(
                    f"{base_url}/threads/{thread_id}/runs/{run['id']}"
                    f"/submit_tool_outputs?api-version={api_version}",
                    headers=headers,
                    json={"tool_outputs": tool_outputs},
                    timeout=FOUNDRY_TIMEOUT,
                )
                submit_resp.raise_for_status()
                run = submit_resp.json()
            else:
                time.sleep(POLL_INTERVAL)
                poll_resp = requests.get(
                    f"{base_url}/threads/{thread_id}/runs/{run['id']}"
                    f"?api-version={api_version}",
                    headers=headers,
                    timeout=FOUNDRY_TIMEOUT,
                )
                run = poll_resp.json()

        if run["status"] != "completed":
            raise RuntimeError("Foundry run failed: %s" % run["status"])

        # Get latest assistant message
        msgs_resp = requests.get(
            f"{base_url}/threads/{thread_id}/messages"
            f"?api-version={api_version}&order=desc&limit=1",
            headers=headers,
            timeout=FOUNDRY_TIMEOUT,
        )
        msgs_data = msgs_resp.json()
        for msg in msgs_data.get("data", []):
            if msg["role"] == "assistant":
                return msg["content"][0]["text"]["value"]
        return None

    # --- Chat (main entry point) ---

    @api.model
    def chat_completion(self, user_message, user_id=None,
                        history=None, context_envelope=None):
        """Send a message to Foundry and get a response.

        Tries SDK mode first, falls back to HTTP mode, then to simple
        chat completion, then to offline response.
        """
        settings = self._get_settings()
        if not settings["enabled"]:
            return None

        endpoint = settings["endpoint"]
        api_key = settings["api_key"]
        agent_id = settings["agent_id"]

        # Initialize activity list in context envelope
        if context_envelope is None:
            context_envelope = {}
        context_envelope.setdefault("_activities", [])

        self._emit_activity(
            context_envelope, "classify", "Classifying request", "done",
        )

        if not endpoint or not agent_id:
            _logger.warning(
                "Foundry not configured: endpoint=%s agent=%s",
                bool(endpoint), bool(agent_id),
            )
            self._emit_activity(
                context_envelope, "respond",
                "Preparing response", "done",
            )
            return self._fallback_response(user_message)

        # Track request telemetry
        start = time.time()
        telemetry = self.env["ipai.copilot.telemetry"]
        surface = context_envelope.get("surface", "") if context_envelope else ""
        telemetry.track_chat_request(
            user_id=user_id, surface=surface, source="api",
        )

        # Emit context activity
        if context_envelope.get("record_model"):
            self._emit_activity(
                context_envelope, "context",
                "Loading record context", "done",
            )

        # Attempt 1: SDK mode (managed identity or API key)
        self._emit_activity(
            context_envelope, "foundry", "Connecting to Foundry", "active",
        )
        try:
            client = self._get_sdk_client(settings)
            if client:
                result = self._sdk_chat(
                    client, settings, user_message, context_envelope,
                )
                if result:
                    self._emit_activity(
                        context_envelope, "foundry",
                        "Connecting to Foundry", "done",
                    )
                    self._emit_activity(
                        context_envelope, "respond",
                        "Preparing response", "done",
                    )
                    latency_ms = int((time.time() - start) * 1000)
                    telemetry.track_chat_response(
                        user_id=user_id, surface=surface,
                        latency_ms=latency_ms, source="sdk",
                    )
                    context_envelope["_foundry_mode"] = "sdk"
                    self._log_audit(
                        user_id, user_message, result,
                        context_envelope, source="api",
                    )
                    return result
        except Exception as e:
            _logger.warning("SDK chat failed, falling back to HTTP: %s", e)

        # Attempt 2: HTTP mode (raw Assistants API)
        if api_key:
            try:
                result = self._http_chat(
                    settings, user_message, context_envelope,
                )
                if result:
                    self._emit_activity(
                        context_envelope, "foundry",
                        "Connecting to Foundry", "done",
                    )
                    self._emit_activity(
                        context_envelope, "respond",
                        "Preparing response", "done",
                    )
                    latency_ms = int((time.time() - start) * 1000)
                    telemetry.track_chat_response(
                        user_id=user_id, surface=surface,
                        latency_ms=latency_ms, source="http",
                    )
                    context_envelope["_foundry_mode"] = "http"
                    self._log_audit(
                        user_id, user_message, result,
                        context_envelope, source="api",
                    )
                    return result
            except Exception as e:
                _logger.error("HTTP chat failed: %s", e)

        # Attempt 3: Simple chat completion (no tools)
        if api_key:
            try:
                self._emit_activity(
                    context_envelope, "foundry",
                    "Connecting to Foundry", "done",
                )
                result = self._simple_chat_completion(
                    endpoint, api_key, settings["api_version"],
                    user_message, context_envelope,
                )
                if result:
                    self._emit_activity(
                        context_envelope, "respond",
                        "Preparing response", "done",
                    )
                    context_envelope["_foundry_mode"] = "simple"
                    self._log_audit(
                        user_id, user_message, result,
                        context_envelope, source="api",
                    )
                    return result
            except Exception as e:
                _logger.error("Simple completion fallback error: %s", e)

        # Attempt 4: Offline response
        self._emit_activity(
            context_envelope, "foundry",
            "Connecting to Foundry", "error",
        )
        self._emit_activity(
            context_envelope, "respond",
            "Preparing response", "done",
        )
        context_envelope["_foundry_mode"] = "offline"
        return self._fallback_response(user_message)

    def _simple_chat_completion(self, endpoint, api_key, api_version,
                                 message, context_envelope):
        """Fallback: use simple chat completions API (no tools)."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if context_envelope:
            messages.append({
                "role": "system",
                "content": "Context: %s" % json.dumps(context_envelope),
            })
        messages.append({"role": "user", "content": message})

        resp = requests.post(
            "%s/openai/deployments/gpt-4.1/chat/completions"
            "?api-version=%s" % (endpoint, api_version),
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
        """Last-resort response when Foundry is unreachable."""
        return (
            "I'm Pulser, your operational intelligence assistant. "
            "I'm currently unable to reach the AI service. "
            "Please try again in a moment, or contact support "
            "if the issue persists."
        )

    def _log_audit(self, user_id, prompt, response, context_envelope,
                   source="api"):
        """Create audit record for this interaction."""
        try:
            self.env["ipai.copilot.audit"].sudo().create({
                "user_id": user_id or self.env.uid,
                "prompt": prompt,
                "response_excerpt": (response or "")[:500],
                "source": source,
                "surface": (
                    context_envelope.get("surface", "erp")
                    if context_envelope else "erp"
                ),
                "context_envelope": json.dumps(context_envelope or {}),
                "company_id": self.env.company.id,
            })
        except Exception:
            _logger.debug("Audit log creation failed", exc_info=True)
