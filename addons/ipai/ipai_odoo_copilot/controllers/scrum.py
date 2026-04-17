# -*- coding: utf-8 -*-
"""Pulser Scrum Master — REST shim (R2).

Canonical path for "talk to Scrum Master" shipped TODAY via Odoo-native REST,
while the full MAF A2A server at apps/pulser-scrum-agent/ ships under the
Phase 2 build (currently blocked on B1-B5).

Design:
  - Thin Odoo controllers at /pulser/scrum/<skill>
  - Calls ADO REST for work-item state (PAT from Key Vault via existing
    config-parameter pattern used by copilot_gateway.py)
  - Calls Foundry gpt-4.1 via existing Foundry client wiring
  - Returns JSON matching the canonical agent_result envelope shape
    (agent-platform/contracts/envelopes/agent_result.yaml) so Phase 2
    migration is a swap, not a rewrite.

Scope (per SKILL.md + doctrine):
  - L1 auto: read-only digests (standup, velocity)
  - L2 propose-only: retro, drift suggestions returned as proposals
  - L3/L4 never via this shim (deferred until control.approvals ships)

Authority:
  - agents/skills/scrum_master/SKILL.md
  - agents/pulser-scrum-master/.well-known/agent-card.json
  - docs/research/ado-pulser-scrum-extension.md + addendum-a2a.md
  - docs/architecture/agent-orchestration-model.md (supervisor-mediated)

Rev: 2026-04-16
"""

import datetime
import json
import logging
import uuid

from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)

# ─── Constants ──────────────────────────────────────────────────────
A2A_PROTOCOL_VERSION = "0.2.0"
AGENT_ID = "pulser_scrum_master"
ALLOWED_SKILLS = {"standup", "velocity", "retro", "drift"}
DEFAULT_ADO_ORG = "insightpulseai"
DEFAULT_ADO_PROJECT = "ipai-platform"
KILL_SWITCH_PARAM = "ipai.pulser.scrum.disabled"


class PulserScrumController(http.Controller):
    """Pulser Scrum Master REST endpoints.

    Entry points (all type='json', auth='user'):
      POST /pulser/scrum/standup   — daily standup digest
      POST /pulser/scrum/velocity  — weekly velocity trend
      POST /pulser/scrum/retro     — sprint retro synthesis (L2 proposals)
      POST /pulser/scrum/drift     — doctrine drift scan (L2 proposals)
      GET  /pulser/scrum/health    — shim liveness + config status

    Response shape (matches agent-platform/contracts/envelopes/agent_result.yaml):
      {
        "request_id": "<uuid>",
        "workflow_id": "<uuid>",       # shim-generated until supervisor exists
        "step_id": "shim.scrum.<skill>",
        "agent_id": "pulser_scrum_master",
        "status": "success | hard_error | needs_review",
        "confidence": 0.0-1.0,
        "evidence_refs": [...],
        "output_payload": {...},
        "policy_flags": [...],
        "cost_tokens": {"input": 0, "output": 0, "total": 0},
        "cost_usd": 0.0,
        "latency_ms": 0,
        "model_used": {"provider": "foundry_cloud", "model": "gpt-4.1", ...},
        "suggested_followup": {...},
        "warning": "Shim path — canonical supervisor ships in Phase 2",
        "completed_at": "<iso8601>"
      }
    """

    # ------------------------------------------------------------------
    # Kill-switch gate (per SKILL.md observability contract)
    # ------------------------------------------------------------------
    def _check_kill_switch(self):
        """Respect the kill-switch config parameter. Matches SKILL.md spec."""
        disabled = request.env["ir.config_parameter"].sudo().get_param(
            KILL_SWITCH_PARAM, "False"
        )
        if str(disabled).lower() in ("1", "true", "yes"):
            raise AccessError(
                "Pulser Scrum Master is disabled via kill-switch "
                f"({KILL_SWITCH_PARAM}=True). Contact platform-engineering."
            )

    # ------------------------------------------------------------------
    # Envelope construction (matches agent_result.yaml shape)
    # ------------------------------------------------------------------
    def _build_envelope(self, skill, status, payload=None, confidence=1.0,
                        evidence=None, policy_flags=None, error=None,
                        suggested_followup=None, cost_tokens=None,
                        latency_ms=0, started_at=None):
        """Build canonical agent_result envelope.

        Once Phase 2 supervisor ships, this shim is removed and workers return
        the same envelope to the supervisor directly. Client contract preserved.
        """
        request_id = str(uuid.uuid4())
        workflow_id = f"shim-{started_at.strftime('%Y%m%d%H%M%S')}-{request_id[:8]}"
        now = datetime.datetime.utcnow().isoformat() + "Z"

        envelope = {
            "request_id": request_id,
            "workflow_id": workflow_id,
            "step_id": f"shim.scrum.{skill}",
            "agent_id": AGENT_ID,
            "status": status,
            "confidence": confidence,
            "evidence_refs": evidence or [],
            "output_payload": payload or {},
            "policy_flags": policy_flags or [],
            "cost_tokens": cost_tokens or {"input": 0, "output": 0, "total": 0},
            "latency_ms": latency_ms,
            "model_used": {
                "provider": "foundry_cloud",
                "model": "gpt-4.1",
                "version": "2025-04-14",
                "deployment": "gpt-4.1",
            },
            "completed_at": now,
            # Shim-specific metadata (removed once supervisor ships):
            "warning": (
                "Shim path via ipai_odoo_copilot. Canonical A2A supervisor "
                "ships in Phase 2. Output envelope shape preserved for "
                "seamless migration."
            ),
            "a2a_protocol_version": A2A_PROTOCOL_VERSION,
        }
        if error:
            envelope["error"] = error
        if suggested_followup:
            envelope["suggested_followup"] = suggested_followup
        return envelope

    # ------------------------------------------------------------------
    # Shared ADO + Foundry plumbing (delegated to existing copilot_gateway)
    # ------------------------------------------------------------------
    def _get_ado_context(self, org=None, project=None, iteration=None, team=None):
        """Normalize ADO query context. Defaults to insightpulseai/ipai-platform."""
        return {
            "org": org or DEFAULT_ADO_ORG,
            "project": project or DEFAULT_ADO_PROJECT,
            "iteration": iteration,  # None → supervisor/shim picks current
            "team": team,            # None → supervisor/shim picks default
        }

    def _call_scrum_worker(self, skill, ado_context, extra=None):
        """Delegate to the scrum worker service.

        Current impl: reads SKILL.md prompt, builds ADO queries, calls Foundry
        via the existing Foundry client used by copilot_gateway.
        Service layer: models/pulser_scrum_service.py (created alongside this controller).

        Returns: (output_payload, evidence_refs, policy_flags, cost_tokens, latency_ms)
        """
        service = request.env["ipai.pulser.scrum.service"].sudo()
        return service.run_skill(skill=skill, ado_context=ado_context, extra=extra or {})

    # ------------------------------------------------------------------
    # Skill endpoints
    # ------------------------------------------------------------------
    @http.route("/pulser/scrum/standup", type="json", auth="user",
                methods=["POST"], csrf=True)
    def standup(self, iteration=None, team=None, date=None, **kw):
        """Daily standup digest — L1 auto, read-only.

        Inputs (all optional):
          iteration: str — e.g. "R2.S3". Defaults to current iteration.
          team:      str — e.g. "insightpulseai\\DeliveryEng". Defaults to caller's team.
          date:      str ISO — defaults to today.

        Output payload:
          digest_markdown: str — ready-to-post Adaptive Card or chatter content
          blockers: list[dict]
          ownership_gaps: list[dict]
          completed_yesterday: list[dict]
          in_progress_today: list[dict]
        """
        self._check_kill_switch()
        started = datetime.datetime.utcnow()
        try:
            ctx = self._get_ado_context(iteration=iteration, team=team)
            extra = {"date": date or datetime.date.today().isoformat()}
            payload, evidence, flags, cost, latency = self._call_scrum_worker(
                "standup", ctx, extra=extra,
            )
            return self._build_envelope(
                skill="standup", status="success", payload=payload,
                evidence=evidence, policy_flags=flags, cost_tokens=cost,
                latency_ms=latency, started_at=started,
            )
        except AccessError:
            raise
        except Exception as exc:
            _logger.exception("Scrum standup failed: %s", exc)
            return self._build_envelope(
                skill="standup", status="hard_error",
                error={"code": "WORKER_ERROR", "message": str(exc),
                       "is_retryable": False},
                started_at=started,
            )

    @http.route("/pulser/scrum/velocity", type="json", auth="user",
                methods=["POST"], csrf=True)
    def velocity(self, iterations=5, team=None, **kw):
        """Weekly velocity trend — L1 auto, read-only.

        Inputs:
          iterations: int — how many iterations to trend (default 5)
          team:       str — ADO team path

        Output payload:
          trend_markdown: str
          committed_vs_completed: list[dict] per iteration
          dora_metrics: {lead_time, deployment_freq, change_fail_rate, mttr}
          chart_data: dict — for Adaptive Card Image or React chart
        """
        self._check_kill_switch()
        started = datetime.datetime.utcnow()
        try:
            if not isinstance(iterations, int) or iterations < 1 or iterations > 20:
                raise ValidationError(
                    "iterations must be int between 1 and 20; got %r" % iterations
                )
            ctx = self._get_ado_context(team=team)
            extra = {"iterations": iterations}
            payload, evidence, flags, cost, latency = self._call_scrum_worker(
                "velocity", ctx, extra=extra,
            )
            return self._build_envelope(
                skill="velocity", status="success", payload=payload,
                evidence=evidence, policy_flags=flags, cost_tokens=cost,
                latency_ms=latency, started_at=started,
            )
        except (AccessError, ValidationError):
            raise
        except Exception as exc:
            _logger.exception("Scrum velocity failed: %s", exc)
            return self._build_envelope(
                skill="velocity", status="hard_error",
                error={"code": "WORKER_ERROR", "message": str(exc),
                       "is_retryable": False},
                started_at=started,
            )

    @http.route("/pulser/scrum/retro", type="json", auth="user",
                methods=["POST"], csrf=True)
    def retro(self, iteration=None, team=None, refine=None, **kw):
        """Sprint retro — L2 propose-only.

        Returns synthesis + proposed action items. ANY action item that
        proposes WI creation/mutation is flagged as needs_review; the
        client is responsible for routing to control.approvals (when it
        exists) or to a human reviewer today.

        Inputs:
          iteration: str — which closed iteration to synthesize
          team:      str
          refine:    str — optional refinement hint ("make it shorter",
                     "focus on blockers", etc.). Shim is stateless per call;
                     workflow-scoped memory ships with the supervisor.

        Output payload:
          synthesis_markdown: str
          wins: list[str]
          drags: list[str]
          proposed_action_items: list[dict] — each has confidence + L-band
        """
        self._check_kill_switch()
        started = datetime.datetime.utcnow()
        try:
            ctx = self._get_ado_context(iteration=iteration, team=team)
            extra = {"refine": refine or ""}
            payload, evidence, flags, cost, latency = self._call_scrum_worker(
                "retro", ctx, extra=extra,
            )
            # Retro always surfaces as needs_review if any action item is L2+
            has_mutations = any(
                item.get("l_band", "L1_auto") != "L1_auto"
                for item in payload.get("proposed_action_items", [])
            )
            status = "needs_review" if has_mutations else "success"
            flags = flags or []
            if has_mutations:
                flags.append("requires_human_approval")
            return self._build_envelope(
                skill="retro", status=status, payload=payload,
                evidence=evidence, policy_flags=flags, cost_tokens=cost,
                latency_ms=latency, started_at=started,
                suggested_followup={
                    "reason": "Retro items proposed; route to approvals queue",
                    "suggested_agent_id": "pulser_supervisor",
                    "suggested_task_type": "approval_route",
                } if has_mutations else None,
            )
        except AccessError:
            raise
        except Exception as exc:
            _logger.exception("Scrum retro failed: %s", exc)
            return self._build_envelope(
                skill="retro", status="hard_error",
                error={"code": "WORKER_ERROR", "message": str(exc),
                       "is_retryable": False},
                started_at=started,
            )

    @http.route("/pulser/scrum/drift", type="json", auth="user",
                methods=["POST"], csrf=True)
    def drift(self, scope="open_work_items", **kw):
        """Doctrine drift scan — L2 propose-only.

        Scans open WI for: orphan WI (no area path), stale WI (>14d WIP
        with no update), wrong iteration, missing parent link, references
        to deprecated platforms (Supabase/n8n/Vercel/Cloudflare/DigitalOcean).

        Inputs:
          scope: str — "open_work_items" (default) | "last_closed_iteration"

        Output payload:
          findings: list[dict] with type, severity, wi_id, proposed_fix
          summary_markdown: str
        """
        self._check_kill_switch()
        started = datetime.datetime.utcnow()
        try:
            if scope not in ("open_work_items", "last_closed_iteration"):
                raise ValidationError(
                    "scope must be 'open_work_items' or 'last_closed_iteration'"
                )
            ctx = self._get_ado_context()
            extra = {"scope": scope}
            payload, evidence, flags, cost, latency = self._call_scrum_worker(
                "drift", ctx, extra=extra,
            )
            # Drift findings always surface as needs_review (L2 propose)
            has_findings = bool(payload.get("findings"))
            status = "needs_review" if has_findings else "success"
            return self._build_envelope(
                skill="drift", status=status, payload=payload,
                evidence=evidence, policy_flags=flags, cost_tokens=cost,
                latency_ms=latency, started_at=started,
                suggested_followup={
                    "reason": "Drift findings proposed; human review required",
                    "suggested_agent_id": "pulser_supervisor",
                    "suggested_task_type": "drift_remediation_route",
                } if has_findings else None,
            )
        except (AccessError, ValidationError):
            raise
        except Exception as exc:
            _logger.exception("Scrum drift failed: %s", exc)
            return self._build_envelope(
                skill="drift", status="hard_error",
                error={"code": "WORKER_ERROR", "message": str(exc),
                       "is_retryable": False},
                started_at=started,
            )

    # ------------------------------------------------------------------
    # Health / liveness
    # ------------------------------------------------------------------
    @http.route("/pulser/scrum/health", type="json", auth="user", methods=["POST"])
    def health(self, **kw):
        """Shim liveness + config status. Non-sensitive. Auth required."""
        disabled = request.env["ir.config_parameter"].sudo().get_param(
            KILL_SWITCH_PARAM, "False"
        )
        return {
            "status": "ok" if str(disabled).lower() not in ("1", "true", "yes") else "disabled",
            "agent_id": AGENT_ID,
            "a2a_protocol_version": A2A_PROTOCOL_VERSION,
            "supported_skills": sorted(ALLOWED_SKILLS),
            "kill_switch_param": KILL_SWITCH_PARAM,
            "kill_switch_value": disabled,
            "shim_mode": True,
            "canonical_path": (
                "Phase 2 ships apps/pulser-scrum-agent/ (MAF A2A server). "
                "Until then this shim provides the same envelope shape."
            ),
        }
