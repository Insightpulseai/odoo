# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging
import time
import uuid
from datetime import datetime

import requests

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# Idempotency window: reject duplicate runs within this many seconds
IDEMPOTENCY_WINDOW_SEC = 300

STATE = [
    ("queued", "Queued"),
    ("running", "Running"),
    ("waiting_approval", "Waiting Approval"),
    ("succeeded", "Succeeded"),
    ("failed", "Failed"),
    ("cancelled", "Cancelled"),
]


class IpaiAgentRun(models.Model):
    """
    Single execution record for an IPAI agent invocation.

    Lifecycle
    ---------
    queued → running → succeeded / failed / cancelled
    queued → waiting_approval → (approved) → running → succeeded / failed
                              → (rejected) → cancelled

    Idempotency
    -----------
    `idempotency_key` prevents duplicate runs within IDEMPOTENCY_WINDOW_SEC.
    Default key is `<model>/<res_id>/<tool_technical_name>`.

    Secrets
    -------
    The Supabase Edge Function endpoint and HMAC secret are read from
    ir.config_parameter at dispatch time — never stored here.
    """

    _name = "ipai.agent.run"
    _description = "IPAI Agent Run"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "requested_at desc, id desc"

    # ── Identity ────────────────────────────────────────────────────────────

    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        default=lambda self: _("New"),
        copy=False,
    )
    idempotency_key = fields.Char(
        string="Idempotency Key",
        index=True,
        copy=False,
        help="Prevents duplicate runs. Auto-generated if not set.",
    )

    # ── Who / What ──────────────────────────────────────────────────────────

    requested_by = fields.Many2one(
        "res.users",
        string="Requested By",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    requested_at = fields.Datetime(
        string="Requested At",
        default=fields.Datetime.now,
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    tool_id = fields.Many2one(
        "ipai.agent.tool",
        string="Tool",
        required=True,
        tracking=True,
    )

    # ── Target record ───────────────────────────────────────────────────────

    target_model = fields.Char(
        string="Target Model",
        required=True,
        help="Technical model name of the record that triggered this run.",
    )
    target_res_id = fields.Integer(
        string="Target Record ID",
        required=True,
    )
    target_display = fields.Char(
        string="Target",
        compute="_compute_target_display",
        store=False,
    )

    # ── I/O payload ─────────────────────────────────────────────────────────

    input_json = fields.Text(
        string="Input (JSON)",
        help="Payload sent to the Edge Function.",
    )
    tool_calls_json = fields.Text(
        string="Tool Calls (JSON)",
        help="Tool calls made by the agent (received in callback).",
    )
    output_json = fields.Text(
        string="Output (JSON)",
        help="Final output from the agent.",
    )
    evidence_log = fields.Text(
        string="Evidence Log",
        help="Structured evidence / trace attached by the agent.",
    )

    # ── External references ─────────────────────────────────────────────────

    external_provider = fields.Char(
        string="External Provider",
        default="supabase",
    )
    external_run_id = fields.Char(
        string="External Run ID",
        index=True,
        help="Run ID returned by the Supabase Edge Function / MCP.",
    )

    # ── State machine ───────────────────────────────────────────────────────

    state = fields.Selection(
        STATE,
        string="State",
        default="queued",
        required=True,
        tracking=True,
    )
    approved_by = fields.Many2one(
        "res.users",
        string="Approved By",
        tracking=True,
    )
    approved_at = fields.Datetime(string="Approved At", readonly=True)
    dispatched_at = fields.Datetime(string="Dispatched At", readonly=True)
    completed_at = fields.Datetime(string="Completed At", readonly=True)

    error_message = fields.Text(string="Error Message")

    # ── Compute ─────────────────────────────────────────────────────────────

    @api.depends("target_model", "target_res_id")
    def _compute_target_display(self):
        for rec in self:
            try:
                target = self.env[rec.target_model].browse(rec.target_res_id)
                rec.target_display = target.display_name if target.exists() else f"{rec.target_model}#{rec.target_res_id}"
            except Exception:
                rec.target_display = f"{rec.target_model}#{rec.target_res_id}"

    # ── Sequence / create ───────────────────────────────────────────────────

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("ipai.agent.run") or _("New")
        if not vals.get("idempotency_key"):
            vals["idempotency_key"] = self._default_idempotency_key(vals)
        return super().create(vals)

    @api.model
    def _default_idempotency_key(self, vals):
        tool = self.env["ipai.agent.tool"].browse(vals.get("tool_id"))
        tech = tool.technical_name if tool else "unknown"
        return f"{vals.get('target_model', '')}/{vals.get('target_res_id', 0)}/{tech}"

    # ── Idempotency guard ───────────────────────────────────────────────────

    @api.model
    def find_or_create(self, vals):
        """
        Return an existing active run if one matches idempotency_key
        within IDEMPOTENCY_WINDOW_SEC, otherwise create a new one.
        """
        key = vals.get("idempotency_key") or self._default_idempotency_key(vals)
        cutoff = fields.Datetime.from_string(
            fields.Datetime.now()
        ).timestamp() - IDEMPOTENCY_WINDOW_SEC
        cutoff_dt = datetime.utcfromtimestamp(cutoff)
        existing = self.search([
            ("idempotency_key", "=", key),
            ("state", "in", ["queued", "running", "waiting_approval"]),
            ("requested_at", ">=", fields.Datetime.to_string(cutoff_dt)),
        ], limit=1)
        if existing:
            _logger.info("ipai.agent.run: returning existing run %s for key %s", existing.name, key)
            return existing
        vals["idempotency_key"] = key
        return self.create(vals)

    # ── State machine actions ───────────────────────────────────────────────

    def action_approve(self):
        self.ensure_one()
        if self.state != "waiting_approval":
            raise UserError(_("Only runs in 'Waiting Approval' state can be approved."))
        self.write({
            "state": "queued",
            "approved_by": self.env.user.id,
            "approved_at": fields.Datetime.now(),
        })
        self.message_post(body=_("Run approved by %s.") % self.env.user.name)

    def action_reject(self):
        self.ensure_one()
        if self.state != "waiting_approval":
            raise UserError(_("Only runs in 'Waiting Approval' state can be rejected."))
        self.write({"state": "cancelled"})
        self.message_post(body=_("Run rejected by %s.") % self.env.user.name)

    def action_cancel(self):
        self.ensure_one()
        if self.state not in ("queued", "waiting_approval"):
            raise UserError(_("Only queued or pending-approval runs can be cancelled."))
        self.write({"state": "cancelled"})

    def action_retry(self):
        self.ensure_one()
        if self.state not in ("failed", "cancelled"):
            raise UserError(_("Only failed or cancelled runs can be retried."))
        self.write({
            "state": "queued",
            "error_message": False,
            "external_run_id": False,
            "dispatched_at": False,
            "completed_at": False,
        })

    # ── Dispatch ────────────────────────────────────────────────────────────

    def action_dispatch(self):
        """
        Dispatch queued runs to the configured Supabase Edge Function.
        Called by the cron job (and available as a manual button for admins).
        """
        queued = self.filtered(lambda r: r.state == "queued")
        for run in queued:
            run._dispatch_single()

    def _dispatch_single(self):
        """
        Send this run to the Edge Function endpoint.
        Endpoint URL and HMAC secret are read from ir.config_parameter.
        """
        tool = self.tool_id
        endpoint = tool.get_endpoint()
        if not endpoint:
            self.write({
                "state": "failed",
                "error_message": _(
                    "Tool '%s' has no endpoint configured. "
                    "Set ir.config_parameter '%s'."
                ) % (tool.name, tool.endpoint_param or "?"),
            })
            return

        payload = {
            "run_id": self.name,
            "idempotency_key": self.idempotency_key,
            "tool": tool.technical_name,
            "target_model": self.target_model,
            "target_res_id": self.target_res_id,
            "input": json.loads(self.input_json or "{}"),
        }

        headers = {"Content-Type": "application/json"}

        # HMAC auth
        if tool.auth_mode == "hmac":
            secret = tool.get_secret()
            if secret:
                timestamp = str(int(time.time()))
                body_bytes = json.dumps(payload).encode()
                sig = hmac.new(
                    secret.encode(), body_bytes + timestamp.encode(), hashlib.sha256
                ).hexdigest()
                headers["x-signature"] = sig
                headers["x-timestamp"] = timestamp

        # Service-role auth
        elif tool.auth_mode == "service_role":
            secret = tool.get_secret()
            if secret:
                headers["Authorization"] = f"Bearer {secret}"

        # API key auth
        elif tool.auth_mode == "api_key":
            secret = tool.get_secret()
            if secret:
                headers["x-api-key"] = secret

        try:
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            self.write({
                "state": "running",
                "external_run_id": data.get("run_id") or data.get("id"),
                "dispatched_at": fields.Datetime.now(),
            })
            _logger.info("ipai.agent.run %s dispatched → external_run_id=%s", self.name, self.external_run_id)
        except Exception as exc:
            _logger.exception("ipai.agent.run %s dispatch failed: %s", self.name, exc)
            self.write({
                "state": "failed",
                "error_message": str(exc),
                "completed_at": fields.Datetime.now(),
            })

    # ── Cron entry point ────────────────────────────────────────────────────

    @api.model
    def cron_dispatch_queued(self):
        """
        Dispatches all queued runs respecting policy approval requirements.
        Called by ir.cron (every 2 minutes).
        """
        runs = self.search([("state", "=", "queued")])
        policy_model = self.env["ipai.agent.policy"]
        for run in runs:
            policy = policy_model.get_policy_for(run.target_model, run.company_id.id)
            if policy and policy.require_approval and not run.approved_by:
                run.write({"state": "waiting_approval"})
                run.message_post(body=_("Run moved to 'Waiting Approval' by policy '%s'.") % policy.name)
                continue
            run._dispatch_single()
