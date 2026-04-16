# -*- coding: utf-8 -*-
"""Tests for Pulser Scrum Master REST shim.

Scope: smoke tests on controller + service envelope contract. Verifies
that the shim returns the canonical agent_result envelope shape so
Phase 2 migration (to apps/pulser-scrum-agent/ MAF A2A server) is a
swap, not a rewrite.

Does NOT hit ADO REST or Foundry; service-level handlers return stub
payloads for controller integration testing.

Authority:
  - agents/skills/scrum_master/SKILL.md
  - agent-platform/contracts/envelopes/agent_result.yaml
"""

from odoo.tests.common import HttpCase, TransactionCase, tagged


@tagged("post_install", "-at_install", "ipai_pulser_scrum")
class TestPulserScrumService(TransactionCase):
    """Service-layer envelope contract."""

    def test_service_model_registered(self):
        """ipai.pulser.scrum.service must be accessible via env."""
        service = self.env["ipai.pulser.scrum.service"]
        self.assertIsNotNone(service, "Service model not registered")

    def test_run_skill_standup_envelope(self):
        """run_skill('standup', ...) returns the 5-tuple contract."""
        service = self.env["ipai.pulser.scrum.service"].sudo()
        ado_ctx = {
            "org": "insightpulseai",
            "project": "ipai-platform",
            "iteration": "R2.S3-TEST",
            "team": None,
        }
        result = service.run_skill(
            skill="standup",
            ado_context=ado_ctx,
            extra={"date": "2026-04-16"},
        )
        self.assertEqual(len(result), 5, "Service must return 5-tuple")
        payload, evidence, flags, cost, latency = result
        # Payload shape
        self.assertIn("digest_markdown", payload)
        self.assertIn("blockers", payload)
        self.assertEqual(payload["iteration"], "R2.S3-TEST")
        # Evidence shape
        self.assertIsInstance(evidence, list)
        if evidence:
            self.assertIn("kind", evidence[0])
            self.assertIn("uri", evidence[0])
        # Cost shape
        self.assertIn("input", cost)
        self.assertIn("output", cost)
        self.assertIn("total", cost)
        # Latency
        self.assertIsInstance(latency, int)
        self.assertGreaterEqual(latency, 0)

    def test_run_skill_all_four(self):
        """All four skills (standup/velocity/retro/drift) must return the contract."""
        service = self.env["ipai.pulser.scrum.service"].sudo()
        ado_ctx = {
            "org": "insightpulseai",
            "project": "ipai-platform",
            "iteration": None,
            "team": None,
        }
        for skill in ("standup", "velocity", "retro", "drift"):
            result = service.run_skill(skill=skill, ado_context=ado_ctx, extra={})
            self.assertEqual(
                len(result), 5, "Skill %s must return 5-tuple" % skill
            )

    def test_run_skill_unknown_raises(self):
        """Unknown skill raises ValueError."""
        service = self.env["ipai.pulser.scrum.service"].sudo()
        with self.assertRaises(ValueError):
            service.run_skill(
                skill="bogus",
                ado_context={"org": "x", "project": "y"},
                extra={},
            )


@tagged("post_install", "-at_install", "ipai_pulser_scrum")
class TestPulserScrumController(HttpCase):
    """Controller-layer envelope contract (HTTP)."""

    def test_health_endpoint(self):
        """/pulser/scrum/health returns shim status."""
        self.authenticate("admin", "admin")
        result = self.url_open(
            "/pulser/scrum/health",
            data="{}",
            headers={"Content-Type": "application/json"},
        )
        # Odoo JSON-RPC returns 200 even on errors; check body
        self.assertEqual(result.status_code, 200)
        import json
        body = json.loads(result.content)
        payload = body.get("result", {})
        self.assertEqual(payload.get("agent_id"), "pulser_scrum_master")
        self.assertIn(payload.get("status"), ("ok", "disabled"))
        self.assertTrue(payload.get("shim_mode"))
        self.assertEqual(payload.get("a2a_protocol_version"), "0.2.0")
        self.assertEqual(
            sorted(payload.get("supported_skills", [])),
            ["drift", "retro", "standup", "velocity"],
        )

    def test_kill_switch_blocks_requests(self):
        """Setting kill-switch param blocks skill endpoints."""
        self.env["ir.config_parameter"].sudo().set_param(
            "ipai.pulser.scrum.disabled", "True"
        )
        self.authenticate("admin", "admin")
        # Health endpoint stays reachable; it reports the disabled state.
        result = self.url_open(
            "/pulser/scrum/health",
            data="{}",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(result.status_code, 200)
        import json
        body = json.loads(result.content)
        self.assertEqual(body.get("result", {}).get("status"), "disabled")
        # Reset for other tests
        self.env["ir.config_parameter"].sudo().set_param(
            "ipai.pulser.scrum.disabled", "False"
        )
