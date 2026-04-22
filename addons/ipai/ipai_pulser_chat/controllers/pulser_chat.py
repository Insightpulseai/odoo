# -*- coding: utf-8 -*-

import json
import logging
import urllib.error
import urllib.request

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PulserChatController(http.Controller):
    """Thin Odoo-side proxy for the external Pulser runtime."""

    def _settings(self):
        config = request.env["ir.config_parameter"].sudo()
        timeout_value = config.get_param("ipai.pulser_chat.timeout_seconds", "30")
        try:
            timeout = int(timeout_value)
        except (TypeError, ValueError):
            timeout = 30
        timeout = min(max(timeout, 5), 120)
        return {
            "enabled": config.get_param("ipai.pulser_chat.enabled", "False") == "True",
            "backend_url": config.get_param("ipai.pulser_chat.backend_url", "").strip(),
            "timeout_seconds": timeout,
        }

    def _sanitize_context(self, context):
        context = context or {}
        model = context.get("context_model") or ""
        if model and not all(char.isalnum() or char in "._" for char in model):
            model = ""
        record_id = context.get("context_res_id")
        try:
            record_id = int(record_id) if record_id else False
        except (TypeError, ValueError):
            record_id = False
        return {
            "surface": context.get("surface") or "erp",
            "context_model": model or False,
            "context_res_id": record_id or False,
        }

    def _build_envelope(self, sanitized_context, conversation_id):
        user = request.env.user
        company = request.env.company
        return {
            "source": "odoo_systray",
            "conversation_id": conversation_id,
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
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            backend_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            if not raw:
                return {}
            return json.loads(raw)

    @http.route(
        "/ipai/pulser_chat/bootstrap",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=True,
    )
    def bootstrap(self):
        settings = self._settings()
        user = request.env.user
        company = request.env.company
        return {
            "enabled": settings["enabled"],
            "backend_configured": bool(settings["backend_url"]),
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
        settings = self._settings()
        text = (message or "").strip()
        if not settings["enabled"]:
            return {
                "ok": False,
                "error": "Pulser chat is disabled in Settings.",
            }
        if not settings["backend_url"]:
            return {
                "ok": False,
                "error": "Pulser chat backend URL is not configured.",
            }
        if not text:
            return {
                "ok": False,
                "error": "Message cannot be empty.",
            }

        sanitized_context = self._sanitize_context(context)
        payload = {
            "message": text,
            "session": self._build_envelope(sanitized_context, conversation_id),
        }

        try:
            response = self._proxy_message(
                settings["backend_url"], payload, settings["timeout_seconds"]
            )
        except urllib.error.HTTPError as err:
            _logger.warning("Pulser backend HTTP error %s", err.code)
            return {
                "ok": False,
                "error": "Pulser backend returned HTTP %s." % err.code,
            }
        except urllib.error.URLError as err:
            _logger.warning("Pulser backend unreachable: %s", err.reason)
            return {
                "ok": False,
                "error": "Pulser backend is unreachable.",
            }
        except json.JSONDecodeError:
            _logger.warning("Pulser backend returned non-JSON response")
            return {
                "ok": False,
                "error": "Pulser backend returned an invalid response.",
            }

        content = ""
        if isinstance(response, dict):
            content = (
                response.get("content")
                or response.get("message")
                or response.get("reply")
                or response.get("response")
                or ""
            )
        return {
            "ok": True,
            "content": content,
            "conversation_id": response.get("conversation_id") if isinstance(response, dict) else False,
            "citations": response.get("citations", []) if isinstance(response, dict) else [],
            "metadata": response.get("metadata", {}) if isinstance(response, dict) else {},
        }
