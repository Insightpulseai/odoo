# -*- coding: utf-8 -*-

import json
import logging
import os
import ssl
import urllib.error
import urllib.request

from odoo import models

_logger = logging.getLogger(__name__)

PARAM_PREFIX = "ipai_odoo_copilot"

# Azure IMDS base endpoint for managed-identity token acquisition.
# Only reachable from within Azure-hosted compute (ACA, VM, etc.).
_IMDS_BASE = (
    "http://169.254.169.254/metadata/identity/oauth2/token"
    "?api-version=2018-02-01"
)
_IMDS_TIMEOUT = 2  # seconds — fast fail when not on Azure

# Token audiences by API family.
# Foundry project/agent APIs (threads, assistants, runs):
_FOUNDRY_SCOPE = "https://ai.azure.com/.default"
# Azure OpenAI / Cognitive Services direct inference:
_COGNITIVE_SCOPE = "https://cognitiveservices.azure.com/.default"

# Probe timeout for Foundry API calls.
_PROBE_TIMEOUT = 10

# Azure AI Agent Service API version.
# This is the stable GA version for the Assistants-compatible API.
_AGENTS_API_VERSION = "2024-12-01-preview"


class FoundryService(models.Model):
    """Thin bridge service for Azure Foundry agent operations.

    Uses _auto = False so no database table is created, but the model
    is registered in ir.model (required for ir.cron and ir.actions.server
    references).

    Auth precedence:
      1. Managed identity (Azure IMDS) — preferred, zero-secret
      2. AZURE_FOUNDRY_API_KEY env var — fallback for local/dev
      3. None — reported clearly as auth-unavailable

    Token audiences by API family:
      - Foundry project/agent APIs: https://ai.azure.com/.default
      - Azure OpenAI / Cognitive Services: https://cognitiveservices.azure.com/.default

    Two endpoints:
      - Portal URL (foundry_endpoint): for "Open Portal" button
      - API endpoint (foundry_api_endpoint): full Foundry project API URL
        (e.g. https://<resource>.services.ai.azure.com/api/projects/<project>)

    Never stores Azure secrets in ir.config_parameter or Odoo DB.
    """

    _name = "ipai.foundry.service"
    _description = "Azure Foundry Service Bridge"
    _auto = False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_param(self, key, default=""):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(f"{PARAM_PREFIX}.{key}", default)
        )

    def _get_settings(self):
        return {
            "enabled": self._get_param("foundry_enabled", "False") == "True",
            "endpoint": self._get_param("foundry_endpoint"),
            "api_endpoint": self._get_param("foundry_api_endpoint"),
            "project": self._get_param("foundry_project"),
            "agent_name": self._get_param("foundry_agent_name"),
            "model": self._get_param("foundry_model"),
            "search_service": self._get_param("foundry_search_service"),
            "search_connection": self._get_param("foundry_search_connection"),
            "search_index": self._get_param("foundry_search_index"),
            "memory_enabled": self._get_param(
                "foundry_memory_enabled", "False"
            ) == "True",
            "read_only_mode": self._get_param(
                "foundry_read_only_mode", "True"
            ) == "True",
        }

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def _get_auth_mode(self, scope=None):
        """Detect available auth mode. Returns (mode, token_or_key).

        mode is one of: 'managed-identity', 'api-key', 'none'.
        token_or_key is the bearer value or empty string.
        scope: token audience for managed identity (default: _FOUNDRY_SCOPE).
        """
        # 1. Try managed identity (IMDS) — only works on Azure compute
        token = self._try_managed_identity(scope=scope)
        if token:
            return "managed-identity", token

        # 2. Env-var API key fallback
        api_key = os.environ.get("AZURE_FOUNDRY_API_KEY", "")
        if api_key:
            return "api-key", api_key

        return "none", ""

    def _try_managed_identity(self, scope=None):
        """Attempt IMDS token acquisition. Returns token str or empty.

        scope: token audience URI. Defaults to _FOUNDRY_SCOPE
               (https://ai.azure.com/.default) for Foundry project APIs.
        """
        if scope is None:
            scope = _FOUNDRY_SCOPE
        # IMDS resource param expects the base URI without /.default suffix
        resource = scope.replace("/.default", "")
        imds_url = "%s&resource=%s" % (_IMDS_BASE, resource)

        req = urllib.request.Request(
            imds_url, headers={"Metadata": "true"}
        )
        try:
            with urllib.request.urlopen(req, timeout=_IMDS_TIMEOUT) as resp:
                data = json.loads(resp.read())
                return data.get("access_token", "")
        except Exception:
            # Not on Azure compute, or IMDS unreachable — expected in dev
            return ""

    def _get_auth_headers(self, scope=None):
        """Build auth headers from best available mode.

        scope: token audience for managed identity (default: _FOUNDRY_SCOPE).
        Returns (headers_dict, auth_mode_str).
        """
        mode, secret = self._get_auth_mode(scope=scope)
        if mode == "none":
            _logger.info("Foundry auth: no credentials available")
            return {}, mode
        _logger.info("Foundry auth: using %s (scope=%s)", mode, scope)
        if mode == "api-key":
            # Azure AI services accept api-key via header
            return {"api-key": secret}, mode
        # Managed identity uses Bearer token
        return {"Authorization": f"Bearer {secret}"}, mode

    # ------------------------------------------------------------------
    # Network
    # ------------------------------------------------------------------

    def _http_request(self, url, headers=None, method="GET", body=None):
        """HTTP request with optional JSON body.

        Returns (status_code, body_str_or_none, error_str_or_none).
        status_code == 0 means network-level failure.
        body: dict to send as JSON (sets Content-Type and encodes).
        """
        hdrs = {"Accept": "application/json"}
        if headers:
            hdrs.update(headers)

        data = None
        if body is not None:
            hdrs["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(
            url, headers=hdrs, method=method, data=data
        )
        ctx = ssl.create_default_context()

        try:
            with urllib.request.urlopen(
                req, timeout=_PROBE_TIMEOUT, context=ctx
            ) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                return resp.status, body, None
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            return e.code, body, str(e.reason)
        except urllib.error.URLError as e:
            return 0, None, str(e.reason)
        except Exception as e:
            return 0, None, str(e)

    def _classify_http_status(self, status, error, auth_mode, context=""):
        """Classify an HTTP status into an operator-facing (ok, msg) tuple."""
        if status == 0:
            return False, "%sUnreachable — %s" % (context, error)
        if status == 401:
            return False, (
                "%sUnauthorized (401). Auth: %s. "
                "Check credentials or managed-identity binding."
                % (context, auth_mode)
            )
        if status == 403:
            return False, (
                "%sForbidden (403). Auth: %s. "
                "The identity may lack required permissions."
                % (context, auth_mode)
            )
        if status == 404:
            return False, "%sNot found (404)." % context
        if status >= 500:
            return False, (
                "%sServer error (%d). Try again later." % (context, status)
            )
        if status >= 400:
            return False, "%sClient error (%d): %s" % (
                context, status, error or "unknown"
            )
        return True, ""

    # ------------------------------------------------------------------
    # Agent resolution
    # ------------------------------------------------------------------

    def _resolve_agent(self, api_endpoint, auth_headers, auth_mode,
                       agent_name):
        """Attempt to find a named agent via the Azure AI Agent Service API.

        Uses GET /openai/assistants?api-version=... to list agents and
        searches for one matching the configured name.

        This is read-only — never creates or modifies agents.

        Returns (found: bool, message: str).
        """
        url = (
            "%s/openai/assistants?api-version=%s"
            % (api_endpoint.rstrip("/"), _AGENTS_API_VERSION)
        )
        _logger.info(
            "Foundry agent resolve: GET %s (looking for name=%s)",
            url, agent_name,
        )

        status, body, error = self._http_request(url, auth_headers)

        # Check for HTTP-level failures
        ok, msg = self._classify_http_status(
            status, error, auth_mode, context="Agent list: "
        )
        if not ok:
            return False, msg

        # Parse response
        try:
            data = json.loads(body) if body else {}
        except (json.JSONDecodeError, TypeError):
            return False, (
                "Agent list: unexpected response format (not JSON)."
            )

        # Azure Assistants API returns {"data": [...], ...}
        agents = data.get("data", [])
        if not isinstance(agents, list):
            return False, (
                "Agent list: unexpected response shape "
                "(expected 'data' array)."
            )

        # Search by name field
        for agent in agents:
            if agent.get("name") == agent_name:
                agent_id = agent.get("id", "?")
                agent_model = agent.get("model", "?")
                return True, (
                    "Agent '%s' found (id=%s, model=%s)."
                    % (agent_name, agent_id, agent_model)
                )

        # Not found — list what we did find for debugging
        known = [a.get("name", "?") for a in agents[:5]]
        suffix = ""
        if len(agents) > 5:
            suffix = " (and %d more)" % (len(agents) - 5)
        return False, (
            "Agent '%s' not found. "
            "Available agents: %s%s."
            % (agent_name, ", ".join(known) if known else "(none)", suffix)
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def test_connection(self):
        """Real bounded health probe against Azure Foundry.

        Validates in order:
          1. Addon enabled
          2. Required config fields present
          3. Auth available (managed-identity or env key)
          4. API endpoint reachable (HTTP GET, non-mutating)
          5. Reports search/knowledge binding state

        Returns (ok: bool, message: str).
        Never mutates remote state.
        """
        settings = self._get_settings()

        # --- 1. Enabled check ---
        if not settings["enabled"]:
            msg = "Foundry copilot is disabled. Enable it in settings first."
            _logger.info("Foundry probe: %s", msg)
            return False, msg

        # --- 2. Config shape ---
        missing = []
        if not settings["api_endpoint"]:
            missing.append("API Endpoint")
        if not settings["project"]:
            missing.append("Foundry Project")
        if not settings["agent_name"]:
            missing.append("Agent Name")
        if not settings["model"]:
            missing.append("Model Deployment")
        if missing:
            msg = "Missing required config: %s" % ", ".join(missing)
            _logger.info("Foundry probe FAIL (config): %s", msg)
            return False, msg

        # --- 2b. Endpoint shape validation ---
        api_ep = settings["api_endpoint"]
        if ".services.ai.azure.com" not in api_ep:
            msg = (
                "API Endpoint does not look like an Azure AI services URL. "
                "Expected: https://<resource>.services.ai.azure.com/api/projects/<project>"
            )
            _logger.warning("Foundry probe FAIL (shape): %s", msg)
            return False, msg

        endpoint_warnings = []
        if "/api/projects/" not in api_ep:
            endpoint_warnings.append(
                "Endpoint missing /api/projects/ path — "
                "agent operations may fail. Expected shape: "
                "https://<resource>.services.ai.azure.com"
                "/api/projects/<project>"
            )
            _logger.warning("Foundry probe WARNING: %s", endpoint_warnings[0])

        # --- 3. Auth ---
        # Foundry project APIs use ai.azure.com scope, not cognitiveservices
        auth_headers, auth_mode = self._get_auth_headers(
            scope=_FOUNDRY_SCOPE
        )
        if auth_mode == "none":
            msg = (
                "No auth available. Set AZURE_FOUNDRY_API_KEY in env "
                "or deploy on Azure compute with managed identity."
            )
            _logger.warning("Foundry probe FAIL (auth): %s", msg)
            return False, msg

        # --- 4. API endpoint reachability ---
        api_endpoint = settings["api_endpoint"].rstrip("/")
        _logger.info(
            "Foundry probe: target=%s project=%s agent=%s auth=%s",
            api_endpoint, settings["project"],
            settings["agent_name"], auth_mode,
        )

        # Probe the base endpoint (lightweight GET)
        status, body, error = self._http_request(
            api_endpoint, auth_headers
        )

        if status == 0:
            msg = "API endpoint unreachable: %s — %s" % (
                api_endpoint, error
            )
            _logger.warning("Foundry probe FAIL (network): %s", msg)
            return False, msg

        # For reachability, any authenticated response (even 404 on /)
        # proves network + auth are working. Only true failures matter.
        if status == 401:
            ok, msg = self._classify_http_status(
                status, error, auth_mode, context="API endpoint: "
            )
            _logger.warning("Foundry probe FAIL (auth): %s", msg)
            return False, msg

        if status == 403:
            ok, msg = self._classify_http_status(
                status, error, auth_mode, context="API endpoint: "
            )
            _logger.warning("Foundry probe FAIL (authz): %s", msg)
            return False, msg

        if status >= 500:
            msg = (
                "API endpoint returned server error (%d). Try again later."
                % status
            )
            _logger.warning("Foundry probe FAIL (server): %s", msg)
            return False, msg

        # --- 5. Success — report binding state ---
        parts = [
            "API endpoint reachable (%d)." % status,
            "Auth: %s." % auth_mode,
            "Scope: %s." % _FOUNDRY_SCOPE,
            "Agent: %s." % settings["agent_name"],
            "Project: %s." % settings["project"],
            "Model: %s." % settings["model"],
        ]
        if endpoint_warnings:
            parts.extend("WARNING: %s" % w for w in endpoint_warnings)
        if settings["search_service"] and settings["search_index"]:
            parts.append(
                "Knowledge: service=%s index=%s."
                % (settings["search_service"], settings["search_index"])
            )
        elif settings["search_service"]:
            parts.append(
                "Knowledge: service=%s index=(not set)."
                % settings["search_service"]
            )
        elif settings["search_connection"] and settings["search_index"]:
            parts.append(
                "Knowledge: search=%s index=%s."
                % (settings["search_connection"], settings["search_index"])
            )
        else:
            parts.append("Knowledge/search binding not yet configured.")

        msg = " ".join(parts)
        _logger.info("Foundry probe OK: %s", msg)
        return True, msg

    def ensure_agent(self):
        """Verify the configured agent exists in Azure Foundry.

        Performs a read-only lookup via the Agents API:
          1. Runs test_connection() first (config + auth + reachability)
          2. Lists agents via GET /openai/assistants
          3. Searches for the configured agent name
          4. Reports found/not-found with details

        Never creates, updates, or deletes agents.
        """
        # Step 1: validate connection first
        ok, msg = self.test_connection()
        if not ok:
            return False, msg

        settings = self._get_settings()
        api_endpoint = settings["api_endpoint"].rstrip("/")
        auth_headers, auth_mode = self._get_auth_headers(
            scope=_FOUNDRY_SCOPE
        )

        # Step 2: resolve agent
        found, resolve_msg = self._resolve_agent(
            api_endpoint, auth_headers, auth_mode, settings["agent_name"]
        )

        if found:
            _logger.info(
                "Foundry ensure_agent: %s (project=%s)",
                resolve_msg, settings["project"],
            )
            return True, resolve_msg

        _logger.warning(
            "Foundry ensure_agent: %s (project=%s)",
            resolve_msg, settings["project"],
        )
        return False, resolve_msg

    def nightly_healthcheck(self):
        """Cron entry point: run real probe and log result."""
        ok, msg = self.test_connection()
        level = logging.INFO if ok else logging.WARNING
        _logger.log(
            level,
            "Foundry nightly healthcheck: %s — %s",
            "OK" if ok else "FAIL",
            msg,
        )
        return ok

    # ------------------------------------------------------------------
    # Chat completion (Foundry Agent API)
    # ------------------------------------------------------------------

    def chat_completion(self, user_message, history=None, user_id=None):
        """Send a chat completion request via the Foundry Agent API.

        Uses the Azure AI Agent Service (Assistants-compatible API):
          1. Get or create a thread (per-user)
          2. Add the user message to the thread
          3. Create a run (agent processes the thread)
          4. Poll for completion
          5. Return the assistant's response text

        Returns response text string, or empty string on failure.
        Never raises — all errors are logged and return empty.
        """
        settings = self._get_settings()
        if not settings["enabled"]:
            return ""

        api_endpoint = settings["api_endpoint"].rstrip("/")
        if not api_endpoint:
            _logger.warning("Copilot chat: no API endpoint configured")
            return ""

        auth_headers, auth_mode = self._get_auth_headers(
            scope=_FOUNDRY_SCOPE
        )
        if auth_mode == "none":
            _logger.warning("Copilot chat: no auth available")
            return ""

        # Thread management
        reuse_threads = settings.get("memory_enabled", False)
        thread_id = None
        if reuse_threads and user_id:
            thread_id = self._get_thread_id(user_id)

        if not thread_id:
            thread_id = self._create_thread(api_endpoint, auth_headers)
            if not thread_id:
                return ""
            if reuse_threads and user_id:
                self._save_thread_id(user_id, thread_id)

        # Add user message
        ok = self._add_message(
            api_endpoint, auth_headers, thread_id, user_message
        )
        if not ok:
            return ""

        # Create run with the configured agent
        agent_name = settings.get("agent_name", "")
        run_id = self._create_run(
            api_endpoint, auth_headers, thread_id, agent_name
        )
        if not run_id:
            return ""

        # Poll for result
        return self._poll_run(
            api_endpoint, auth_headers, thread_id, run_id
        )

    def _get_thread_id(self, user_id):
        """Retrieve cached thread ID for a user."""
        key = "%s.thread_%s" % (PARAM_PREFIX, user_id)
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(key, "")
        )

    def _save_thread_id(self, user_id, thread_id):
        """Cache a Foundry thread ID for a user."""
        key = "%s.thread_%s" % (PARAM_PREFIX, user_id)
        self.env["ir.config_parameter"].sudo().set_param(key, thread_id)

    def _create_thread(self, api_endpoint, auth_headers):
        """Create a new Foundry thread. Returns thread_id or empty."""
        url = "%s/openai/threads?api-version=%s" % (
            api_endpoint, _AGENTS_API_VERSION
        )
        status, body, error = self._http_request(
            url, auth_headers, method="POST", body={}
        )
        if status < 200 or status >= 300:
            _logger.warning(
                "Copilot create_thread failed: %d %s", status, error
            )
            return ""
        try:
            data = json.loads(body) if body else {}
        except (json.JSONDecodeError, TypeError):
            return ""
        return data.get("id", "")

    def _add_message(self, api_endpoint, auth_headers, thread_id, content):
        """Add a user message to a thread. Returns True on success."""
        url = "%s/openai/threads/%s/messages?api-version=%s" % (
            api_endpoint, thread_id, _AGENTS_API_VERSION
        )
        payload = {"role": "user", "content": content}
        status, body, error = self._http_request(
            url, auth_headers, method="POST", body=payload
        )
        if status < 200 or status >= 300:
            _logger.warning(
                "Copilot add_message failed: %d %s", status, error
            )
            return False
        return True

    def _create_run(self, api_endpoint, auth_headers, thread_id,
                    agent_name):
        """Create a run on a thread. Returns run_id or empty.

        The agent_name is used as the assistant_id if it looks like an
        assistant ID (starts with 'asst_'), otherwise we attempt to
        resolve it to an ID first.
        """
        # If agent_name is already an assistant ID, use directly
        assistant_id = agent_name
        if agent_name and not agent_name.startswith("asst_"):
            # Try to resolve name to ID
            found, msg = self._resolve_agent(
                api_endpoint, auth_headers, "api-key", agent_name
            )
            if found and "id=" in msg:
                # Extract ID from "Agent 'x' found (id=asst_xxx, ...)"
                import re  # noqa: PLC0415
                match = re.search(r"id=(asst_\w+)", msg)
                if match:
                    assistant_id = match.group(1)

        url = "%s/openai/threads/%s/runs?api-version=%s" % (
            api_endpoint, thread_id, _AGENTS_API_VERSION
        )
        payload = {"assistant_id": assistant_id}
        status, body, error = self._http_request(
            url, auth_headers, method="POST", body=payload
        )
        if status < 200 or status >= 300:
            _logger.warning(
                "Copilot create_run failed: %d %s %s",
                status, error, (body or "")[:200],
            )
            return ""
        try:
            data = json.loads(body) if body else {}
        except (json.JSONDecodeError, TypeError):
            return ""
        return data.get("id", "")

    def _poll_run(self, api_endpoint, auth_headers, thread_id, run_id,
                  max_wait=30, interval=1):
        """Poll a run until completion. Returns assistant response text.

        max_wait: maximum seconds to wait (default 30).
        interval: seconds between polls (default 1).
        """
        import time  # noqa: PLC0415

        url = "%s/openai/threads/%s/runs/%s?api-version=%s" % (
            api_endpoint, thread_id, run_id, _AGENTS_API_VERSION
        )
        deadline = time.time() + max_wait

        while time.time() < deadline:
            status, body, error = self._http_request(url, auth_headers)
            if status < 200 or status >= 300:
                _logger.warning(
                    "Copilot poll_run failed: %d %s", status, error
                )
                return ""

            try:
                data = json.loads(body) if body else {}
            except (json.JSONDecodeError, TypeError):
                return ""

            run_status = data.get("status", "")
            if run_status == "completed":
                return self._get_latest_assistant_message(
                    api_endpoint, auth_headers, thread_id
                )
            if run_status in ("failed", "cancelled", "expired"):
                _logger.warning(
                    "Copilot run %s ended with status: %s",
                    run_id, run_status,
                )
                return ""

            # Still in progress — wait and retry
            time.sleep(interval)

        _logger.warning(
            "Copilot run %s timed out after %ds", run_id, max_wait
        )
        return ""

    def _get_latest_assistant_message(self, api_endpoint, auth_headers,
                                      thread_id):
        """Get the latest assistant message from a thread."""
        url = (
            "%s/openai/threads/%s/messages?api-version=%s&limit=1&order=desc"
            % (api_endpoint, thread_id, _AGENTS_API_VERSION)
        )
        status, body, error = self._http_request(url, auth_headers)
        if status < 200 or status >= 300:
            return ""

        try:
            data = json.loads(body) if body else {}
        except (json.JSONDecodeError, TypeError):
            return ""

        messages = data.get("data", [])
        if not messages:
            return ""

        msg = messages[0]
        if msg.get("role") != "assistant":
            return ""

        # Extract text from content blocks
        content = msg.get("content", [])
        parts = []
        for block in content:
            if block.get("type") == "text":
                text_val = block.get("text", {})
                if isinstance(text_val, dict):
                    parts.append(text_val.get("value", ""))
                else:
                    parts.append(str(text_val))
        return "\n".join(parts)
