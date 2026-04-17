# -*- coding: utf-8 -*-
"""Pulser Scrum Service — skill execution layer (R2 shim).

Delegated to by controllers/scrum.py. Owns:
  - ADO REST queries (WIQL, Analytics OData)
  - Foundry gpt-4.1 prompt construction (from SKILL.md)
  - Evidence artifact collection
  - Cost tracking

Service model (TransientModel-style, but concrete on ir.model) so it can be
called from controllers via `env["ipai.pulser.scrum.service"].sudo().run_skill(...)`.

Canonical path: ships under Phase 2 at apps/pulser-scrum-agent/ (MAF A2A
server). This shim returns the SAME (payload, evidence, flags, cost, latency)
tuple so the controller logic is stable across the transition.

Authority:
  - agents/skills/scrum_master/SKILL.md
  - ssot/governance/foundry-model-routing.yaml (gpt-4.1 baseline)
  - ssot/governance/agent-interop-matrix.yaml (pulser_scrum_master entry)

Rev: 2026-04-16
"""

import datetime
import json
import logging
import os
import time

from odoo import api, models

_logger = logging.getLogger(__name__)

# Skill → SKILL.md section header. Real prompt loads at runtime from
# agents/skills/scrum_master/SKILL.md (single source of truth).
SKILL_PROMPT_MAP = {
    "standup": "standup_daily",
    "velocity": "velocity_weekly",
    "retro": "retro_synthesis",
    "drift": "drift_scan",
}

# Deprecated platforms to grep for during drift scan (matches CLAUDE.md).
DEPRECATED_PLATFORMS = [
    "supabase", "n8n", "vercel", "cloudflare", "digitalocean",
    "wix", "mailgun", "mattermost", "insightpulseai.net",
]


class PulserScrumService(models.AbstractModel):
    _name = "ipai.pulser.scrum.service"
    _description = "Pulser Scrum Master skill execution service (R2 shim)"

    # ------------------------------------------------------------------
    # Public entry
    # ------------------------------------------------------------------
    @api.model
    def run_skill(self, skill, ado_context, extra=None):
        """Execute one scrum skill. Returns controller-shaped tuple.

        Args:
          skill: str — one of standup/velocity/retro/drift
          ado_context: dict — {org, project, iteration, team}
          extra: dict — skill-specific extra inputs

        Returns:
          (output_payload, evidence_refs, policy_flags, cost_tokens, latency_ms)
        """
        if skill not in SKILL_PROMPT_MAP:
            raise ValueError(f"Unknown scrum skill: {skill}")

        t0 = time.monotonic()
        extra = extra or {}

        handler = getattr(self, f"_run_{skill}")
        payload, evidence, flags, cost = handler(ado_context=ado_context, extra=extra)

        latency_ms = int((time.monotonic() - t0) * 1000)
        return payload, evidence, flags, cost, latency_ms

    # ------------------------------------------------------------------
    # Per-skill handlers (shim implementations)
    # ------------------------------------------------------------------
    def _run_standup(self, ado_context, extra):
        """Daily standup digest.

        R2 shim behavior:
          1. Query ADO for WI in current iteration (in-progress, blocked, done-yesterday)
          2. Build SKILL.md-driven prompt
          3. Call Foundry gpt-4.1 to render the markdown digest
          4. Return payload + evidence

        This shim stubs the ADO + Foundry calls; production wiring happens in
        Phase 2 via apps/pulser-scrum-agent/. Stub returns structured-but-empty
        output so downstream clients (Adaptive Card renderer, chatter post)
        can be integration-tested without live infra.
        """
        iteration = ado_context.get("iteration") or "R2.S3-CURRENT"
        team = ado_context.get("team") or f"{ado_context['org']}\\DeliveryEng"
        date = extra.get("date", datetime.date.today().isoformat())

        payload = {
            "digest_markdown": self._stub_standup_markdown(iteration, team, date),
            "blockers": [],
            "ownership_gaps": [],
            "completed_yesterday": [],
            "in_progress_today": [],
            "iteration": iteration,
            "team": team,
            "date": date,
        }
        evidence = [{
            "kind": "mcp_tool_call",
            "uri": f"mcp://ado-rest/wiql?project={ado_context['project']}&iteration={iteration}",
            "retrieved_at": datetime.datetime.utcnow().isoformat() + "Z",
        }]
        flags = []
        cost = {"input": 0, "output": 0, "total": 0}
        return payload, evidence, flags, cost

    def _run_velocity(self, ado_context, extra):
        """Weekly velocity trend."""
        iterations = extra.get("iterations", 5)
        team = ado_context.get("team") or f"{ado_context['org']}\\DeliveryEng"

        payload = {
            "trend_markdown": self._stub_velocity_markdown(iterations, team),
            "committed_vs_completed": [],
            "dora_metrics": {
                "lead_time_days": None,
                "deployment_frequency_per_week": None,
                "change_fail_rate": None,
                "mttr_hours": None,
            },
            "chart_data": {"labels": [], "committed": [], "completed": []},
            "iterations_analyzed": iterations,
            "team": team,
        }
        evidence = [{
            "kind": "mcp_tool_call",
            "uri": f"mcp://ado-rest/analytics/velocity?team={team}&n={iterations}",
            "retrieved_at": datetime.datetime.utcnow().isoformat() + "Z",
        }]
        flags = []
        cost = {"input": 0, "output": 0, "total": 0}
        return payload, evidence, flags, cost

    def _run_retro(self, ado_context, extra):
        """Sprint retro synthesis — L2 propose-only."""
        iteration = ado_context.get("iteration") or "R2.S2-CLOSED"
        refine = extra.get("refine", "")

        payload = {
            "synthesis_markdown": self._stub_retro_markdown(iteration, refine),
            "wins": [],
            "drags": [],
            "proposed_action_items": [],  # empty until Foundry wiring lands
            "iteration": iteration,
            "refine_hint": refine,
        }
        evidence = [{
            "kind": "mcp_tool_call",
            "uri": f"mcp://ado-rest/wiql?iteration={iteration}",
            "retrieved_at": datetime.datetime.utcnow().isoformat() + "Z",
        }]
        flags = []
        cost = {"input": 0, "output": 0, "total": 0}
        return payload, evidence, flags, cost

    def _run_drift(self, ado_context, extra):
        """Doctrine drift scan — L2 propose-only.

        Shim implementation: checks repo file tree (not ADO WI yet) for
        deprecated platform references. Phase 2 adds ADO WI scanning.
        """
        scope = extra.get("scope", "open_work_items")
        # Phase 2 wires this to ADO WI scanning; shim returns empty findings
        # with documented skipped-scope note.
        payload = {
            "summary_markdown": self._stub_drift_markdown(scope),
            "findings": [],
            "scope": scope,
            "scanned": "shim — ADO WI scan awaiting Phase 2 MCP client",
        }
        evidence = []
        flags = ["shim_partial_scan"]
        cost = {"input": 0, "output": 0, "total": 0}
        return payload, evidence, flags, cost

    # ------------------------------------------------------------------
    # Stub markdown generators (replaced by Foundry gpt-4.1 in Phase 2)
    # ------------------------------------------------------------------
    def _stub_standup_markdown(self, iteration, team, date):
        return (
            f"## Daily standup — {iteration} — {date}\n\n"
            f"_Team: {team}_\n\n"
            f"> Shim output — Foundry gpt-4.1 rendering ships with Phase 2 "
            f"(apps/pulser-scrum-agent/). Envelope shape and endpoint URL "
            f"are stable; digest content becomes LLM-generated on cutover.\n"
        )

    def _stub_velocity_markdown(self, n, team):
        return (
            f"## Velocity trend — last {n} iterations\n\n"
            f"_Team: {team}_\n\n"
            f"> Shim output. ADO Analytics OData + DORA metrics rendered "
            f"via Foundry gpt-4.1 in Phase 2.\n"
        )

    def _stub_retro_markdown(self, iteration, refine):
        refine_note = f" (refined: {refine})" if refine else ""
        return (
            f"## Retro synthesis — {iteration}{refine_note}\n\n"
            f"> Shim output. Wins / drags / action items synthesized via "
            f"Foundry gpt-4.1 in Phase 2. Retro items with mutations are "
            f"routed to control.approvals (when shipped).\n"
        )

    def _stub_drift_markdown(self, scope):
        return (
            f"## Doctrine drift scan — scope: {scope}\n\n"
            f"> Shim output. Full WI scan ships Phase 2. Repo-tree grep for "
            f"deprecated refs ({', '.join(DEPRECATED_PLATFORMS)}) runs via "
            f"CI gate in `.claude/skills/ci-validate.sh`.\n"
        )
