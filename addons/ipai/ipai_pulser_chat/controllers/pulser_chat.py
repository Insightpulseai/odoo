# -*- coding: utf-8 -*-

import json
import logging
import socket
import urllib.error
import urllib.parse
import urllib.request

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

# Hard cap on upstream response body to prevent memory exhaustion.
_MAX_RESPONSE_BYTES = 512 * 1024  # 512 KB

# Permitted URL schemes for the upstream Pulser endpoint.
_ALLOWED_SCHEMES = frozenset({"http", "https"})


class PulserChatController(http.Controller):
    """Thin Odoo-side proxy for the external Pulser runtime.

    Security model:
    - All endpoints require ``auth="user"`` — no anonymous access.
    - CSRF protection is enforced (type="json" with csrf=True).
    - The upstream URL is read from ir.config_parameter via sudo; callers
      cannot influence which host is contacted.
    - Secrets (API keys on the upstream) never transit through this layer.
    - Error responses never expose stack traces or internal config values.
    """

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _settings(self):
        """Return validated settings dict.  Fails closed on missing config."""
        config = request.env["ir.config_parameter"].sudo()
        timeout_raw = config.get_param("ipai.pulser_chat.timeout_seconds", "30")
        try:
            timeout = int(timeout_raw)
        except (TypeError, ValueError):
            _logger.warning(
                "ipai.pulser_chat.timeout_seconds is not an integer (%r); using 30",
                timeout_raw,
            )
            timeout = 30
        # Clamp to a safe range: minimum 5 s, maximum 120 s.
        timeout = min(max(timeout, 5), 120)

        backend_url = config.get_param("ipai.pulser_chat.backend_url", "").strip()
        return {
            "enabled": config.get_param("ipai.pulser_chat.enabled", "False") == "True",
            "backend_url": backend_url,
            "timeout_seconds": timeout,
        }

    @staticmethod
    def _validate_backend_url(url):
        """Return True if *url* is an absolute http/https URL; False otherwise.

        Prevents open-redirect/SSRF via scheme confusion or relative URLs.
        """
        if not url:
            return False
        try:
            parsed = urllib.parse.urlparse(url)
        except Exception:
            return False
        return parsed.scheme in _ALLOWED_SCHEMES and bool(parsed.netloc)

    @staticmethod
    def _sanitize_context(context):
        """Validate and normalise caller-supplied context dict.

        Rejects any context_model value that contains characters outside the
        Odoo model-name alphabet to prevent injection.
        """
        context = context or {}
        model = context.get("context_model") or ""
        if model and not all(ch.isalnum() or ch in "._" for ch in model):
            _logger.warning(
                "Rejected invalid context_model value: %r", model[:80]
            )
            model = ""
        record_id = context.get("context_res_id")
        try:
            record_id = int(record_id) if record_id else False
        except (TypeError, ValueError):
            record_id = False
        surface = str(context.get("surface") or "erp")[:32]
        return {
            "surface": surface,
            "context_model": model or False,
            "context_res_id": record_id or False,
        }

    def _build_envelope(self, sanitized_context, conversation_id):
        """Construct the session envelope forwarded to the Pulser runtime."""
        user = request.env.user
        company = request.env.company
        # conversation_id is an opaque string from a previous turn; coerce to str.
        if conversation_id is not None:
            safe_cid = str(conversation_id)[:128]
        else:
            safe_cid = None
        return {
            "source": "odoo_systray",
            "conversation_id": safe_cid,
            "user": {
                "id": user.id,
                "name": user.name,
                "login": user.login,
                "lang": user.lang,
                "tz": user.tz,
            },
            "company": {
                "id": company.id,
                "name": company.name,
            },
            "odoo_context": sanitized_context,
        }

    def _proxy_message(self, backend_url, payload, timeout_seconds):
        """Forward *payload* to the upstream Pulser runtime.

        Raises:
            urllib.error.HTTPError  — upstream returned non-2xx.
            urllib.error.URLError   — network / DNS failure.
            TimeoutError / socket.timeout — upstream did not respond in time.
            json.JSONDecodeError    — upstream response was not valid JSON.
            ValueError              — response exceeded _MAX_RESPONSE_BYTES.
        """
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            backend_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            raw = resp.read(_MAX_RESPONSE_BYTES + 1)
            if len(raw) > _MAX_RESPONSE_BYTES:
                raise ValueError(
                    "Upstream response exceeded %d-byte limit" % _MAX_RESPONSE_BYTES
                )
            if not raw:
                return {}
            return json.loads(raw.decode("utf-8", errors="replace"))

    # ------------------------------------------------------------------
    # Endpoints
    # ------------------------------------------------------------------

    @http.route(
        "/ipai/pulser_chat/bootstrap",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=True,
    )
    def bootstrap(self):
        """Return feature flags and display metadata for the frontend shell.

        Never exposes the backend URL or any secrets to the client.
        """
        settings = self._settings()
        backend_ok = self._validate_backend_url(settings["backend_url"])
        user = request.env.user
        company = request.env.company
        return {
            "enabled": settings["enabled"],
            "backend_configured": settings["enabled"] and backend_ok,
            "user_name": user.name,
            "company_name": company.name,
        }

    @http.route(
        "/ipai/pulser_chat/message",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=True,
    )
    def message(self, message=None, context=None, conversation_id=None, **kwargs):
        """Proxy a user message to the external Pulser runtime.

        Returns a structured ``{"ok": bool, ...}`` envelope in all branches so
        the frontend can rely on a stable shape regardless of error type.
        """
        settings = self._settings()

        # --- Pre-flight checks (fail closed) ---
        if not settings["enabled"]:
            return {"ok": False, "error": "Pulser chat is disabled in Settings."}

        if not self._validate_backend_url(settings["backend_url"]):
            _logger.warning(
                "Pulser chat message rejected: backend URL missing or invalid"
            )
            return {
                "ok": False,
                "error": "Pulser chat backend URL is not configured or invalid.",
            }

        text = (message or "").strip()
        if not text:
            return {"ok": False, "error": "Message cannot be empty."}

        # Enforce a reasonable message length to prevent oversized upstreams calls.
        if len(text) > 8000:
            return {
                "ok": False,
                "error": "Message exceeds the 8 000-character limit.",
            }

        # --- Build and forward payload ---
        sanitized_ctx = self._sanitize_context(context)
        payload = {
            "message": text,
            "session": self._build_envelope(sanitized_ctx, conversation_id),
        }

        try:
            response = self._proxy_message(
                settings["backend_url"], payload, settings["timeout_seconds"]
            )
        except (TimeoutError, socket.timeout):
            _logger.warning(
                "Pulser backend timed out after %d s", settings["timeout_seconds"]
            )
            return {
                "ok": False,
                "error": "Pulser backend did not respond in time. Try again.",
            }
        except urllib.error.HTTPError as err:
            _logger.warning("Pulser backend HTTP error %s", err.code)
            return {
                "ok": False,
                "error": "Pulser backend returned HTTP %s." % err.code,
            }
        except urllib.error.URLError as err:
            # err.reason may be an exception — convert to str for safe logging.
            _logger.warning("Pulser backend unreachable: %s", str(err.reason)[:200])
            return {"ok": False, "error": "Pulser backend is unreachable."}
        except json.JSONDecodeError:
            _logger.warning("Pulser backend returned non-JSON response")
            return {
                "ok": False,
                "error": "Pulser backend returned an invalid response.",
            }
        except ValueError as err:
            _logger.warning("Pulser backend response rejected: %s", err)
            return {
                "ok": False,
                "error": "Pulser backend response was too large.",
            }
        except Exception:
            # Catch-all: log full traceback server-side only; never expose to client.
            _logger.exception("Unexpected error proxying to Pulser backend")
            return {
                "ok": False,
                "error": "An unexpected error occurred. Contact your administrator.",
            }

        # --- Extract content from upstream response ---
        content = ""
        new_cid = None
        citations = []
        metadata = {}

        if isinstance(response, dict):
            content = (
                response.get("content")
                or response.get("message")
                or response.get("reply")
                or response.get("response")
                or ""
            )
            new_cid = response.get("conversation_id")
            raw_citations = response.get("citations", [])
            citations = raw_citations if isinstance(raw_citations, list) else []
            raw_meta = response.get("metadata", {})
            metadata = raw_meta if isinstance(raw_meta, dict) else {}

        return {
            "ok": True,
            "content": str(content)[:32768],  # cap display content
            "conversation_id": str(new_cid)[:128] if new_cid else None,
            "citations": citations[:50],  # cap citation list
            "metadata": metadata,
        }
