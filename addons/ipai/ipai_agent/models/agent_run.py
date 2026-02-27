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
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

# Idempotency window: reject duplicate runs within this many seconds
IDEMPOTENCY_WINDOW_SEC = 300

# Activity type xmlid — see data/activity_types.xml
ACTIVITY_TYPE_APPROVE = "ipai_agent.activity_type_ipai_approve"

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

    Activities (Odoo Essentials alignment)
    --------------------------------------
    When a run enters `waiting_approval`, a `mail.activity` of type
    "IPAI: Approve Run" is created on this record and (if supported) on
    the target record. Approving or rejecting marks the activity done.

    Multi-company (General settings alignment)
    ------------------------------------------
    Every run is scoped to a company. Record rules in security.xml enforce
    that users can only see runs in their active companies.

    Tool access enforcement (General settings alignment)
    ----------------------------------------------------
    `_check_tool_access` enforces that the current user is in the tool's
    `allowed_group_ids` before a run is created. This is a server-side
    deny-by-default check — it cannot be bypassed via RPC.
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
        index=True,
    )
    requested_at = fields.Datetime(
        string="Requested At",
        default=fields.Datetime.now,
        readonly=True,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
        index=True,
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
        index=True,
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

    # ── Callback idempotency ─────────────────────────────────────────────────

    last_event_hash = fields.Char(
        string="Last Event Hash",
        copy=False,
        index=True,
        help=(
            "SHA-256 of (external_run_id | event_id | state | timestamp). "
            "Prevents duplicate state transitions from callback retry storms."
        ),
    )
    last_event_at = fields.Datetime(
        string="Last Event At",
        readonly=True,
        copy=False,
        help="Timestamp when the last callback event was successfully applied.",
    )

    # ── State machine ───────────────────────────────────────────────────────

    state = fields.Selection(
        STATE,
        string="State",
        default="queued",
        required=True,
        tracking=True,
        index=True,
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

    # ── Reporting: duration (pivot measure) ─────────────────────────────────

    duration_seconds = fields.Integer(
        string="Duration (s)",
        compute="_compute_duration_seconds",
        store=True,
        help="Elapsed seconds between dispatch and completion. Used in pivot reports.",
    )

    # ── Compute ─────────────────────────────────────────────────────────────

    @api.depends("target_model", "target_res_id")
    def _compute_target_display(self):
        for rec in self:
            try:
                target = self.env[rec.target_model].browse(rec.target_res_id)
                rec.target_display = (
                    target.display_name if target.exists()
                    else "%s#%s" % (rec.target_model, rec.target_res_id)
                )
            except Exception:
                rec.target_display = "%s#%s" % (rec.target_model, rec.target_res_id)

    @api.depends("dispatched_at", "completed_at")
    def _compute_duration_seconds(self):
        for rec in self:
            if rec.dispatched_at and rec.completed_at:
                delta = rec.completed_at - rec.dispatched_at
                rec.duration_seconds = max(0, int(delta.total_seconds()))
            else:
                rec.duration_seconds = 0

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
        return "%s/%s/%s" % (vals.get("target_model", ""), vals.get("target_res_id", 0), tech)

    # ── Idempotency guard ───────────────────────────────────────────────────

    @api.model
    def find_or_create(self, vals):
        """
        Return an existing active run if one matches idempotency_key
        within IDEMPOTENCY_WINDOW_SEC, otherwise create a new one.

        Server-side access check: the calling user must be in the tool's
        allowed_group_ids (deny-by-default). Bypassed for superuser/cron.
        """
        tool = self.env["ipai.agent.tool"].browse(vals.get("tool_id"))
        if not self.env.su:
            self._check_tool_access(tool)

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
            _logger.info(
                "ipai.agent.run: returning existing run %s for key %s",
                existing.name, key,
            )
            return existing
        vals["idempotency_key"] = key
        return self.create(vals)

    # ── Tool access enforcement ─────────────────────────────────────────────

    @api.model
    def _check_tool_access(self, tool):
        """
        Server-side deny-by-default enforcement.
        Checks:
          1. Tool must exist and be active.
          2. If tool has no allowed_group_ids, any agent user may use it.
          3. If allowed_group_ids are set, the calling user must be in at least one.
        This check runs regardless of UI visibility — cannot be bypassed via RPC.
        """
        if not tool:
            return
        if not tool.active:
            raise AccessError(_(
                "IPAI tool '%s' is inactive and cannot be invoked. "
                "Activate it in IPAI → Agents → Configuration → Tools."
            ) % tool.name)
        if not tool.allowed_group_ids:
            return
        user_group_ids = set(self.env.user.groups_id.ids)
        allowed_ids = set(tool.allowed_group_ids.ids)
        if not user_group_ids & allowed_ids:
            raise AccessError(_(
                "You are not authorized to use IPAI tool '%s'. "
                "Contact your IPAI Agent administrator to request access."
            ) % tool.name)

    # ── State machine actions ───────────────────────────────────────────────

    def action_approve(self):
        self.ensure_one()
        if self.state != "waiting_approval":
            raise UserError(_("Only runs in 'Waiting Approval' state can be approved."))
        self._close_approval_activities(feedback=_("Approved by %s") % self.env.user.name)
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
        self._close_approval_activities(feedback=_("Rejected by %s") % self.env.user.name)
        self.write({"state": "cancelled"})
        self.message_post(body=_("Run rejected by %s.") % self.env.user.name)

    def action_cancel(self):
        self.ensure_one()
        if self.state not in ("queued", "waiting_approval"):
            raise UserError(_("Only queued or pending-approval runs can be cancelled."))
        if self.state == "waiting_approval":
            self._close_approval_activities(feedback=_("Cancelled"))
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
        Notifications use mail.thread (chatter) — no bespoke SMTP logic.
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
                "completed_at": fields.Datetime.now(),
            })
            return

        payload = {
            "run_id": self.name,
            "idempotency_key": self.idempotency_key,
            "tool": tool.technical_name,
            "target_model": self.target_model,
            "target_res_id": self.target_res_id,
            "company_id": self.company_id.id,
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
                headers["Authorization"] = "Bearer %s" % secret

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
            _logger.info(
                "ipai.agent.run %s dispatched → external_run_id=%s",
                self.name, self.external_run_id,
            )
        except Exception as exc:
            _logger.exception("ipai.agent.run %s dispatch failed: %s", self.name, exc)
            self.write({
                "state": "failed",
                "error_message": str(exc),
                "completed_at": fields.Datetime.now(),
            })
            # Notify via chatter (Odoo mail subsystem — no bespoke SMTP)
            self.message_post(
                body=_("Dispatch failed: %s") % str(exc),
                subtype_xmlid="mail.mt_note",
            )

    # ── Cron entry point ────────────────────────────────────────────────────

    @api.model
    def cron_dispatch_queued(self):
        """
        Dispatches all queued runs respecting policy approval requirements.
        Called by ir.cron (every 2 minutes).

        When a run is gated by a policy, it moves to waiting_approval and
        a mail.activity is created on the run (and target record if supported).
        """
        runs = self.search([("state", "=", "queued")])
        policy_model = self.env["ipai.agent.policy"]
        for run in runs:
            policy = policy_model.get_policy_for(run.target_model, run.company_id.id)
            if policy and policy.require_approval and not run.approved_by:
                run.write({"state": "waiting_approval"})
                run.message_post(
                    body=_("Run moved to 'Waiting Approval' by policy '%s'.") % policy.name
                )
                run._schedule_approval_activity()
                continue
            run._dispatch_single()

    # ── Activities (Odoo Essentials alignment) ──────────────────────────────

    def _get_approver_user(self):
        """
        Return the first user in the IPAI Agent Approver group, or the
        requesting user as fallback. Used as the default assignee for
        approval activities.
        """
        group = self.env.ref(
            "ipai_agent.group_ipai_agent_approver", raise_if_not_found=False
        )
        if group and group.users:
            return group.users[0]
        return self.env.user

    def _schedule_approval_activity(self):
        """
        Schedule an 'IPAI: Approve Run' activity on:
          1. This ipai.agent.run record (visible in Odoo header clock list)
          2. The target record, if it supports mail.activity.mixin

        Called when a run transitions to waiting_approval.
        Uses Odoo's mail subsystem — no custom email transport.
        """
        approver = self._get_approver_user()
        note = (
            "<p>Run <strong>%s</strong> triggered by %s is awaiting approval "
            "on record: <em>%s</em>.</p>"
        ) % (self.name, self.requested_by.name, self.target_display or self.target_model)

        # Activity on the run record itself
        self.activity_schedule(
            act_type_xmlid=ACTIVITY_TYPE_APPROVE,
            summary=_("Approve agent run %s") % self.name,
            note=note,
            user_id=approver.id,
        )

        # Activity on the target record (if it has mail.activity.mixin)
        try:
            target = self.env[self.target_model].browse(self.target_res_id)
            if target.exists() and hasattr(target, "activity_schedule"):
                target.activity_schedule(
                    act_type_xmlid=ACTIVITY_TYPE_APPROVE,
                    summary=_("IPAI: Approve run %s") % self.name,
                    note=_(
                        "<p>Agent run <strong>%s</strong> is awaiting approval "
                        "for this record.</p>"
                    ) % self.name,
                    user_id=approver.id,
                )
        except Exception:
            # Target model may not support activities or record may not exist
            pass

    def _close_approval_activities(self, feedback=None):
        """
        Mark all pending IPAI approval activities on this run (and on the
        target record) as done. Called on action_approve and action_reject.

        Uses sudo() so approvers can close activities assigned to others
        (e.g., when a second approver takes over).
        """
        activity_type = self.env.ref(ACTIVITY_TYPE_APPROVE, raise_if_not_found=False)
        if not activity_type:
            return

        fb = feedback or ""

        # Close on the run itself
        activities = self.activity_ids.filtered(
            lambda a: a.activity_type_id.id == activity_type.id
        )
        if activities:
            activities.sudo().action_feedback(feedback=fb)

        # Close on the target record (if it has activity support)
        try:
            target = self.env[self.target_model].browse(self.target_res_id)
            if target.exists() and hasattr(target, "activity_ids"):
                t_activities = target.activity_ids.filtered(
                    lambda a: a.activity_type_id.id == activity_type.id
                )
                if t_activities:
                    t_activities.sudo().action_feedback(feedback=fb)
        except Exception:
            pass

    # ── Callback idempotency guard ────────────────────────────────────────────

    def _apply_external_event(self, payload):
        """
        Apply a callback payload to this run with idempotency protection.

        Event fingerprint (SHA-256):
            external_run_id | event_id | state | timestamp

        If the computed hash matches ``last_event_hash`` the call is a NOOP
        (duplicate delivery / retry storm) — returns False without any write.

        Otherwise: transitions state, persists the hash, and returns True.

        Called by the webhook controller. Also callable from tests and
        from n8n workflows via Supabase RPC.

        Args:
            payload (dict): Callback payload containing at minimum:
                - event_id   (str)  — unique event identifier from the caller
                - state      (str)  — "succeeded" or "failed"
                - timestamp  (str)  — Unix epoch of the event

        Returns:
            bool: True if event was applied; False if it was a NOOP.
        """
        self.ensure_one()

        # Build deterministic event fingerprint
        fingerprint = "|".join([
            str(payload.get("external_run_id") or self.external_run_id or ""),
            str(payload.get("event_id") or ""),
            str(payload.get("state") or ""),
            str(payload.get("timestamp") or ""),
        ])
        event_hash = hashlib.sha256(fingerprint.encode()).hexdigest()

        if self.last_event_hash == event_hash:
            _logger.info(
                "ipai.agent.run %s: duplicate callback event (hash=%s…) — NOOP",
                self.name, event_hash[:12],
            )
            return False

        state = payload.get("state", "succeeded")
        if state not in ("succeeded", "failed"):
            state = "succeeded"

        now = fields.Datetime.now()
        vals = {
            "state": state,
            "last_event_hash": event_hash,
            "last_event_at": now,
            "completed_at": now,
        }
        if payload.get("tool_calls"):
            vals["tool_calls_json"] = json.dumps(payload["tool_calls"])
        if payload.get("output"):
            vals["output_json"] = json.dumps(payload["output"])
        if payload.get("evidence_log"):
            vals["evidence_log"] = payload["evidence_log"]
        if payload.get("external_run_id"):
            vals["external_run_id"] = payload["external_run_id"]
        if state == "failed" and payload.get("error_message"):
            vals["error_message"] = payload["error_message"]

        self.write(vals)
        self.message_post(
            body=_("Agent run completed with state: %s") % state,
            subtype_xmlid="mail.mt_note",
        )
        _logger.info(
            "ipai.agent.run %s: event applied → state=%s (hash=%s…)",
            self.name, state, event_hash[:12],
        )
        return True
