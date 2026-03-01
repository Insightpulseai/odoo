# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""
Pulser intent claim + dispatch model.

Data flow:
  1. Cron tick calls _pulser_process_intents()
  2. Claims one queued odoo.* intent via Supabase RPC
  3. Dispatches to handler based on intent_type
  4. Writes result back to ops.taskbus_intents

Contract: docs/contracts/C-PULSER-ODOO-01.md
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Maximum intents per cron tick (MVP: 1)
MAX_INTENTS_PER_TICK = 1

# Lease duration in seconds
LEASE_SECONDS = 120


class PulserIntent(models.AbstractModel):
    _name = "ipai.pulser.intent"
    _description = "Pulser Intent Claim and Dispatch"

    # ── Supabase connectivity ───────────────────────────────────────────

    @api.model
    def _supabase_url(self):
        url = os.environ.get("SUPABASE_URL", "").strip()
        if not url:
            _logger.warning("SUPABASE_URL not configured")
        return url

    @api.model
    def _supabase_key(self):
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        if not key:
            _logger.warning("SUPABASE_SERVICE_ROLE_KEY not configured")
        return key

    @api.model
    def _instance_id(self):
        """Generate a stable instance identifier for claim ownership."""
        db_name = self.env.cr.dbname
        return "odoo:%s:%s" % (db_name, os.environ.get("HOSTNAME", "unknown"))

    # ── Supabase RPC call ───────────────────────────────────────────────

    @api.model
    def _call_supabase_rpc(self, function_name, params):
        """Call a Supabase RPC function. Returns parsed JSON or None."""
        url = self._supabase_url()
        key = self._supabase_key()
        if not url or not key:
            return None

        rpc_url = "%s/rest/v1/rpc/%s" % (url, function_name)
        headers = {
            "apikey": key,
            "Authorization": "Bearer %s" % key,
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(
                rpc_url, json=params, headers=headers, timeout=30
            )
            if resp.status_code >= 400:
                _logger.error(
                    "Supabase RPC %s failed: %s %s",
                    function_name,
                    resp.status_code,
                    resp.text[:500],
                )
                return None
            return resp.json()
        except requests.RequestException as exc:
            _logger.error("Supabase RPC %s error: %s", function_name, exc)
            return None

    @api.model
    def _supabase_patch(self, table, filters, data):
        """PATCH a row in Supabase via PostgREST."""
        url = self._supabase_url()
        key = self._supabase_key()
        if not url or not key:
            return False

        patch_url = "%s/rest/v1/%s?%s" % (url, table, filters)
        headers = {
            "apikey": key,
            "Authorization": "Bearer %s" % key,
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

        try:
            resp = requests.patch(
                patch_url, json=data, headers=headers, timeout=30
            )
            if resp.status_code >= 400:
                _logger.error(
                    "Supabase PATCH %s failed: %s %s",
                    table,
                    resp.status_code,
                    resp.text[:500],
                )
                return False
            return True
        except requests.RequestException as exc:
            _logger.error("Supabase PATCH %s error: %s", table, exc)
            return False

    # ── Intent claiming ─────────────────────────────────────────────────

    @api.model
    def _claim_intent(self):
        """Claim one queued odoo.* intent from Supabase. Returns dict or None."""
        result = self._call_supabase_rpc("claim_taskbus_intent", {
            "p_intent_prefix": "odoo.",
            "p_claimed_by": self._instance_id(),
            "p_lease_seconds": LEASE_SECONDS,
        })

        if not result:
            return None

        # RPC returns a list of rows (0 or 1)
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return None

    # ── Intent completion ───────────────────────────────────────────────

    @api.model
    def _complete_intent(self, intent_id, status, result_json, error_message=None):
        """Write completion back to ops.taskbus_intents."""
        now = datetime.now(timezone.utc).isoformat()
        data = {
            "status": status,
            "result": result_json,
            "completed_at": now,
            "updated_at": now,
        }
        if error_message:
            data["error_message"] = error_message

        return self._supabase_patch(
            "ops.taskbus_intents",
            "id=eq.%s" % intent_id,
            data,
        )

    # ── Result envelope builders ────────────────────────────────────────

    @api.model
    def _build_envelope(self, intent, data, start_time, meta=None):
        """Build the universal success envelope."""
        now = datetime.now(timezone.utc)
        duration_ms = int((time.time() - start_time) * 1000)
        meta = meta or {}

        return {
            "ok": True,
            "intent": {
                "intent_id": str(intent.get("intent_id", "")),
                "request_id": intent.get("request_id", ""),
                "intent_type": intent.get("intent_type", ""),
                "args": intent.get("args", {}),
                "claimed_by": self._instance_id(),
                "claim_token": None,  # set by RPC
                "claimed_at": intent.get("claimed_at"),
                "finished_at": now.isoformat(),
                "duration_ms": duration_ms,
            },
            "trace": {
                "work_item_ref": meta.get(
                    "work_item_ref", "spec:odooops-console"
                ),
                "run_id": str(intent.get("run_id", "")),
                "correlation_id": meta.get(
                    "correlation_id", str(uuid.uuid4())
                ),
            },
            "data": data,
            "evidence": {
                "artifacts": [],
                "links": [],
            },
        }

    @api.model
    def _build_error_envelope(self, intent, code, message, details=None,
                               retryable=False, start_time=None):
        """Build the universal failure envelope."""
        now = datetime.now(timezone.utc)
        duration_ms = int((time.time() - (start_time or time.time())) * 1000)

        return {
            "ok": False,
            "intent": {
                "intent_id": str(intent.get("intent_id", "")),
                "request_id": intent.get("request_id", ""),
                "intent_type": intent.get("intent_type", ""),
                "args": intent.get("args", {}),
                "claimed_by": self._instance_id(),
                "claim_token": None,
                "claimed_at": intent.get("claimed_at"),
                "finished_at": now.isoformat(),
                "duration_ms": duration_ms,
            },
            "trace": {
                "work_item_ref": "spec:odooops-console",
                "run_id": str(intent.get("run_id", "")),
                "correlation_id": str(uuid.uuid4()),
            },
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
                "retryable": retryable,
            },
            "evidence": {
                "artifacts": [],
                "links": [],
            },
        }

    # ── Main cron entry point ───────────────────────────────────────────

    @api.model
    def _pulser_process_intents(self):
        """Cron entry point: claim and process odoo.* intents.

        Bounded runtime: processes at most MAX_INTENTS_PER_TICK intents.
        """
        _logger.info("Pulser connector: checking for intents...")

        for _ in range(MAX_INTENTS_PER_TICK):
            intent = self._claim_intent()
            if not intent:
                _logger.info("Pulser connector: no intents in queue")
                break

            intent_type = intent.get("intent_type", "")
            intent_id = intent.get("intent_id")
            _logger.info(
                "Pulser connector: claimed intent_id=%s type=%s",
                intent_id,
                intent_type,
            )

            start_time = time.time()
            try:
                # Dispatch to handler
                from .pulser_handlers import ArgsValidationError
                handler = self.env["ipai.pulser.handlers"]

                # Extract meta for trace propagation
                args = intent.get("args", {})
                meta = args.get("meta", {})

                data = handler._dispatch(intent_type, args)

                # Build success envelope (propagate meta into trace)
                result_json = self._build_envelope(
                    intent, data, start_time, meta=meta
                )

                # Write back
                self._complete_intent(intent_id, "done", result_json)

                _logger.info(
                    "Pulser connector: intent_id=%s completed (done) in %dms",
                    intent_id,
                    result_json["intent"]["duration_ms"],
                )

            except ArgsValidationError as exc:
                _logger.warning(
                    "Pulser connector: intent_id=%s args invalid: %s",
                    intent_id,
                    exc,
                )
                error_envelope = self._build_error_envelope(
                    intent,
                    code=exc.code,
                    message=str(exc),
                    details=exc.details,
                    retryable=False,
                    start_time=start_time,
                )
                self._complete_intent(
                    intent_id,
                    "failed",
                    error_envelope,
                    error_message=str(exc)[:500],
                )

            except Exception as exc:
                _logger.exception(
                    "Pulser connector: intent_id=%s failed: %s",
                    intent_id,
                    exc,
                )

                error_envelope = self._build_error_envelope(
                    intent,
                    code="ODOO_EXEC_ERROR",
                    message=str(exc),
                    details={"intent_type": intent_type},
                    retryable=False,
                    start_time=start_time,
                )

                self._complete_intent(
                    intent_id,
                    "failed",
                    error_envelope,
                    error_message=str(exc)[:500],
                )
