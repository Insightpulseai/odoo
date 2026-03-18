# -*- coding: utf-8 -*-

import json
import logging
import os
import time
import urllib.request

from odoo import models

_logger = logging.getLogger(__name__)

# App Insights Track API v2 endpoint.
# The ingestion endpoint is extracted from the connection string.
_TRACK_PATH = "/v2/track"

# Event type constants
EVENT_CHAT_REQUEST = "copilot_chat_request"
EVENT_CHAT_RESPONSE = "copilot_chat_response"
EVENT_TOOL_EXECUTION = "copilot_tool_execution"
EVENT_ERROR = "copilot_error"
EVENT_BLOCKED = "copilot_blocked"


class CopilotTelemetry(models.Model):
    """Non-blocking telemetry sender for Azure Application Insights.

    Uses _auto = False — no database table. All telemetry is sent
    directly to the App Insights ingestion endpoint via HTTP POST.

    Gracefully degrades when APPINSIGHTS_CONNECTION_STRING is not set.
    All methods catch exceptions internally — telemetry failures never
    break the main application flow.

    Connection string format:
      InstrumentationKey=<guid>;IngestionEndpoint=https://...
    """

    _name = "ipai.copilot.telemetry"
    _description = "Copilot App Insights Telemetry"
    _auto = False

    # ------------------------------------------------------------------
    # Connection string parsing
    # ------------------------------------------------------------------

    def _parse_connection_string(self):
        """Parse APPINSIGHTS_CONNECTION_STRING into components.

        Returns (instrumentation_key, ingestion_endpoint) or (None, None).
        """
        conn_str = os.environ.get("APPINSIGHTS_CONNECTION_STRING", "")
        if not conn_str:
            return None, None

        parts = {}
        for segment in conn_str.split(";"):
            segment = segment.strip()
            if "=" in segment:
                key, _, value = segment.partition("=")
                parts[key.strip()] = value.strip()

        ikey = parts.get("InstrumentationKey", "")
        endpoint = parts.get("IngestionEndpoint", "").rstrip("/")

        if not ikey:
            return None, None
        if not endpoint:
            endpoint = "https://dc.services.visualstudio.com"

        return ikey, endpoint

    # ------------------------------------------------------------------
    # Track API
    # ------------------------------------------------------------------

    def _send_event(self, name, properties=None, measurements=None):
        """Send a custom event to App Insights Track API.

        Fire-and-forget pattern: catches all errors, logs warnings,
        never raises. Safe to call from any context.

        Args:
            name: Event name (e.g. EVENT_CHAT_REQUEST).
            properties: Dict of string dimensions.
            measurements: Dict of numeric measurements.
        """
        try:
            ikey, endpoint = self._parse_connection_string()
            if not ikey:
                return  # Telemetry not configured — silent no-op

            envelope = {
                "name": "Microsoft.ApplicationInsights.Event",
                "time": time.strftime(
                    "%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()
                ),
                "iKey": ikey,
                "data": {
                    "baseType": "EventData",
                    "baseData": {
                        "ver": 2,
                        "name": name,
                        "properties": properties or {},
                        "measurements": measurements or {},
                    },
                },
            }

            url = endpoint + _TRACK_PATH
            payload = json.dumps([envelope]).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            # Fire-and-forget with short timeout
            with urllib.request.urlopen(req, timeout=3):
                pass
        except Exception:
            # Telemetry is non-critical — log and continue
            _logger.debug(
                "App Insights telemetry send failed for event '%s'",
                name, exc_info=True,
            )

    def _send_exception(self, exception_type, message, properties=None):
        """Send an exception telemetry event.

        Args:
            exception_type: Exception class name.
            message: Error message string.
            properties: Additional context dimensions.
        """
        try:
            ikey, endpoint = self._parse_connection_string()
            if not ikey:
                return

            envelope = {
                "name": "Microsoft.ApplicationInsights.Exception",
                "time": time.strftime(
                    "%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()
                ),
                "iKey": ikey,
                "data": {
                    "baseType": "ExceptionData",
                    "baseData": {
                        "ver": 2,
                        "exceptions": [
                            {
                                "typeName": exception_type,
                                "message": (message or "")[:1024],
                                "hasFullStack": False,
                            }
                        ],
                        "properties": properties or {},
                    },
                },
            }

            url = endpoint + _TRACK_PATH
            payload = json.dumps([envelope]).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=3):
                pass
        except Exception:
            _logger.debug(
                "App Insights exception telemetry failed",
                exc_info=True,
            )

    # ------------------------------------------------------------------
    # Public convenience methods
    # ------------------------------------------------------------------

    def track_chat_request(self, user_id=None, surface="", mode="",
                           source=""):
        """Track a copilot chat request event."""
        self._send_event(EVENT_CHAT_REQUEST, properties={
            "user_id": str(user_id or self.env.uid),
            "surface": surface or "copilot",
            "mode": mode or "advisory",
            "source": source or "api",
        })

    def track_chat_response(self, user_id=None, surface="", mode="",
                            source="", latency_ms=0):
        """Track a copilot chat response event with latency."""
        self._send_event(
            EVENT_CHAT_RESPONSE,
            properties={
                "user_id": str(user_id or self.env.uid),
                "surface": surface or "copilot",
                "mode": mode or "advisory",
                "source": source or "api",
            },
            measurements={
                "response_latency_ms": latency_ms,
            },
        )

    def track_tool_execution(self, tool_name, user_id=None, surface="",
                             mode="", source="", latency_ms=0):
        """Track a tool execution event."""
        self._send_event(
            EVENT_TOOL_EXECUTION,
            properties={
                "tool_name": tool_name,
                "user_id": str(user_id or self.env.uid),
                "surface": surface or "copilot",
                "mode": mode or "advisory",
                "source": source or "api",
            },
            measurements={
                "response_latency_ms": latency_ms,
            },
        )

    def track_error(self, error_type, message, user_id=None, surface="",
                    source=""):
        """Track a copilot error event."""
        self._send_event(EVENT_ERROR, properties={
            "user_id": str(user_id or self.env.uid),
            "surface": surface or "copilot",
            "source": source or "api",
            "error_type": error_type,
            "error_message": (message or "")[:500],
        })
        self._send_exception(error_type, message, properties={
            "user_id": str(user_id or self.env.uid),
            "surface": surface or "copilot",
        })

    def track_blocked(self, reason, user_id=None, surface="", mode="",
                      source=""):
        """Track a blocked request event."""
        self._send_event(EVENT_BLOCKED, properties={
            "user_id": str(user_id or self.env.uid),
            "surface": surface or "copilot",
            "mode": mode or "advisory",
            "source": source or "api",
            "blocked": "true",
            "reason": (reason or "")[:500],
        })
