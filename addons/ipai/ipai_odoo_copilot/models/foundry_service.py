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

# Azure IMDS endpoint for managed-identity token acquisition.
# Only reachable from within Azure-hosted compute (ACA, VM, etc.).
# Resource scope targets Azure AI services (Cognitive Services).
_IMDS_URL = (
    "http://169.254.169.254/metadata/identity/oauth2/token"
    "?api-version=2018-02-01"
    "&resource=https://cognitiveservices.azure.com/"
)
_IMDS_TIMEOUT = 2  # seconds — fast fail when not on Azure

# Probe timeout for Foundry API calls.
_PROBE_TIMEOUT = 10

# Azure AI Agent Service API version.
# This is the stable GA version for the Assistants-compatible API.
_AGENTS_API_VERSION = "2024-12-01-preview"


class FoundryService(models.AbstractModel):
    """Thin bridge service for Azure Foundry agent operations.

    Auth precedence:
      1. Managed identity (Azure IMDS) — preferred, zero-secret
      2. AZURE_FOUNDRY_API_KEY env var — fallback for local/dev
      3. None — reported clearly as auth-unavailable

    Two endpoints:
      - Portal URL (foundry_endpoint): for "Open Portal" button
      - API endpoint (foundry_api_endpoint): for health probes and agent
        resolution (e.g. https://<resource>.services.ai.azure.com)

    Never stores Azure secrets in ir.config_parameter or Odoo DB.
    """

    _name = "ipai.foundry.service"
    _description = "Azure Foundry Service Bridge"

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

    def _get_auth_mode(self):
        """Detect available auth mode. Returns (mode, token_or_key).

        mode is one of: 'managed-identity', 'api-key', 'none'.
        token_or_key is the bearer value or empty string.
        """
        # 1. Try managed identity (IMDS) — only works on Azure compute
        token = self._try_managed_identity()
        if token:
            return "managed-identity", token

        # 2. Env-var API key fallback
        api_key = os.environ.get("AZURE_FOUNDRY_API_KEY", "")
        if api_key:
            return "api-key", api_key

        return "none", ""

    def _try_managed_identity(self):
        """Attempt IMDS token acquisition. Returns token str or empty."""
        req = urllib.request.Request(
            _IMDS_URL, headers={"Metadata": "true"}
        )
        try:
            with urllib.request.urlopen(req, timeout=_IMDS_TIMEOUT) as resp:
                data = json.loads(resp.read())
                return data.get("access_token", "")
        except Exception:
            # Not on Azure compute, or IMDS unreachable — expected in dev
            return ""

    def _get_auth_headers(self):
        """Build auth headers from best available mode.

        Returns (headers_dict, auth_mode_str).
        """
        mode, secret = self._get_auth_mode()
        if mode == "none":
            _logger.info("Foundry auth: no credentials available")
            return {}, mode
        _logger.info("Foundry auth: using %s", mode)
        if mode == "api-key":
            # Azure AI services accept api-key via header
            return {"api-key": secret}, mode
        # Managed identity uses Bearer token
        return {"Authorization": f"Bearer {secret}"}, mode

    # ------------------------------------------------------------------
    # Network
    # ------------------------------------------------------------------

    def _http_request(self, url, headers=None, method="GET"):
        """Non-mutating HTTP request.

        Returns (status_code, body_str_or_none, error_str_or_none).
        status_code == 0 means network-level failure.
        """
        hdrs = {"Accept": "application/json"}
        if headers:
            hdrs.update(headers)

        req = urllib.request.Request(url, headers=hdrs, method=method)
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

        # --- 3. Auth ---
        auth_headers, auth_mode = self._get_auth_headers()
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
            "Agent: %s." % settings["agent_name"],
            "Project: %s." % settings["project"],
            "Model: %s." % settings["model"],
        ]
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
        auth_headers, auth_mode = self._get_auth_headers()

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
