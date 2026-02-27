# -*- coding: utf-8 -*-
"""
Tests for ipai_agent:
- ACL: user/approver/admin access rules
- State machine transitions
- Idempotency guard
- HMAC signature verification
- Policy enforcement (require_approval gate)
"""
import hashlib
import hmac
import json
import time

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestIpaiAgentSetup(TransactionCase):
    """Base setup shared by all test classes."""

    def setUp(self):
        super().setUp()
        # Create a minimal tool
        self.tool = self.env["ipai.agent.tool"].create({
            "name": "Test Tool",
            "technical_name": "test_tool",
            "auth_mode": "none",
        })
        # Create a run targeting a res.company record (always present)
        self.run = self.env["ipai.agent.run"].create({
            "tool_id": self.tool.id,
            "target_model": "res.company",
            "target_res_id": self.env.company.id,
            "input_json": "{}",
        })


class TestAgentRunStateMachine(TestIpaiAgentSetup):
    """State machine: queued → waiting_approval → approved → running → succeeded"""

    def test_initial_state_is_queued(self):
        self.assertEqual(self.run.state, "queued")

    def test_cannot_approve_queued_run(self):
        with self.assertRaises(UserError):
            self.run.action_approve()

    def test_approve_waiting_run(self):
        self.run.write({"state": "waiting_approval"})
        self.run.action_approve()
        self.assertEqual(self.run.state, "queued")
        self.assertEqual(self.run.approved_by, self.env.user)

    def test_reject_waiting_run(self):
        self.run.write({"state": "waiting_approval"})
        self.run.action_reject()
        self.assertEqual(self.run.state, "cancelled")

    def test_cancel_queued_run(self):
        self.run.action_cancel()
        self.assertEqual(self.run.state, "cancelled")

    def test_retry_failed_run(self):
        self.run.write({"state": "failed", "error_message": "oops"})
        self.run.action_retry()
        self.assertEqual(self.run.state, "queued")
        self.assertFalse(self.run.error_message)

    def test_cannot_retry_running_run(self):
        self.run.write({"state": "running"})
        with self.assertRaises(UserError):
            self.run.action_retry()

    def test_cannot_cancel_succeeded_run(self):
        self.run.write({"state": "succeeded"})
        with self.assertRaises(UserError):
            self.run.action_cancel()


class TestAgentIdempotency(TestIpaiAgentSetup):
    """find_or_create deduplication within window."""

    def test_same_key_returns_existing_run(self):
        key = self.run.idempotency_key
        run2 = self.env["ipai.agent.run"].find_or_create({
            "tool_id": self.tool.id,
            "target_model": "res.company",
            "target_res_id": self.env.company.id,
            "idempotency_key": key,
        })
        self.assertEqual(run2.id, self.run.id)

    def test_different_key_creates_new_run(self):
        run2 = self.env["ipai.agent.run"].find_or_create({
            "tool_id": self.tool.id,
            "target_model": "res.company",
            "target_res_id": self.env.company.id,
            "idempotency_key": "completely-different-key",
        })
        self.assertNotEqual(run2.id, self.run.id)

    def test_completed_run_not_deduplicated(self):
        """A succeeded run should not block a new run with the same key."""
        key = self.run.idempotency_key
        self.run.write({"state": "succeeded"})
        run2 = self.env["ipai.agent.run"].find_or_create({
            "tool_id": self.tool.id,
            "target_model": "res.company",
            "target_res_id": self.env.company.id,
            "idempotency_key": key,
        })
        self.assertNotEqual(run2.id, self.run.id)


class TestAgentPolicy(TestIpaiAgentSetup):
    """Policy: require_approval gate + uniqueness constraint."""

    def test_require_approval_moves_run_to_waiting(self):
        policy = self.env["ipai.agent.policy"].create({
            "name": "Test Policy",
            "target_model": "res.company",
            "require_approval": True,
        })
        run = self.env["ipai.agent.run"].create({
            "tool_id": self.tool.id,
            "target_model": "res.company",
            "target_res_id": self.env.company.id,
        })
        # Simulate cron call
        policy_model = self.env["ipai.agent.policy"]
        pol = policy_model.get_policy_for("res.company", self.env.company.id)
        self.assertEqual(pol, policy)
        if pol and pol.require_approval and not run.approved_by:
            run.write({"state": "waiting_approval"})
        self.assertEqual(run.state, "waiting_approval")

    def test_duplicate_active_policy_raises(self):
        self.env["ipai.agent.policy"].create({
            "name": "Policy A",
            "target_model": "hr.expense.liquidation",
            "require_approval": True,
        })
        from odoo.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.env["ipai.agent.policy"].create({
                "name": "Policy B",
                "target_model": "hr.expense.liquidation",
                "require_approval": False,
            })


class TestAgentToolRegistry(TestIpaiAgentSetup):
    """Tool registry: technical_name uniqueness."""

    def test_duplicate_technical_name_raises(self):
        from odoo.exceptions import ValidationError
        with self.assertRaises((ValidationError, Exception)):
            self.env["ipai.agent.tool"].create({
                "name": "Duplicate Tool",
                "technical_name": "test_tool",  # same as setUp tool
                "auth_mode": "none",
            })


class TestAgentActivities(TestIpaiAgentSetup):
    """
    Activities (Odoo Essentials alignment):
    - waiting_approval → creates mail.activity on the run
    - action_approve → closes approval activity (marks done)
    - action_reject  → closes approval activity (marks done)
    """

    def _get_approve_type(self):
        return self.env.ref(
            "ipai_agent.activity_type_ipai_approve", raise_if_not_found=False
        )

    def _create_run_with_waiting_approval(self):
        run = self.env["ipai.agent.run"].create({
            "tool_id": self.tool.id,
            "target_model": "res.company",
            "target_res_id": self.env.company.id,
            "state": "waiting_approval",
        })
        return run

    def test_schedule_approval_activity_creates_activity_on_run(self):
        """_schedule_approval_activity creates a mail.activity on the run."""
        run = self._create_run_with_waiting_approval()
        activity_type = self._get_approve_type()
        if not activity_type:
            self.skipTest("activity_type_ipai_approve not loaded in test env")

        # No activities yet
        self.assertFalse(
            run.activity_ids.filtered(lambda a: a.activity_type_id == activity_type)
        )

        run._schedule_approval_activity()

        activities = run.activity_ids.filtered(
            lambda a: a.activity_type_id == activity_type
        )
        self.assertTrue(activities, "Approval activity should be created on the run")

    def test_approve_closes_approval_activity(self):
        """action_approve marks the approval activity as done."""
        run = self._create_run_with_waiting_approval()
        activity_type = self._get_approve_type()
        if not activity_type:
            self.skipTest("activity_type_ipai_approve not loaded in test env")

        run.activity_schedule(
            act_type_xmlid="ipai_agent.activity_type_ipai_approve",
            summary="Approve run",
            user_id=self.env.user.id,
        )
        self.assertTrue(
            run.activity_ids.filtered(lambda a: a.activity_type_id == activity_type)
        )

        run.action_approve()

        self.assertEqual(run.state, "queued")
        remaining = run.activity_ids.filtered(
            lambda a: a.activity_type_id == activity_type
        )
        self.assertFalse(remaining, "Approval activity should be closed after approve")

    def test_reject_closes_approval_activity(self):
        """action_reject marks the approval activity as done."""
        run = self._create_run_with_waiting_approval()
        activity_type = self._get_approve_type()
        if not activity_type:
            self.skipTest("activity_type_ipai_approve not loaded in test env")

        run.activity_schedule(
            act_type_xmlid="ipai_agent.activity_type_ipai_approve",
            summary="Approve run",
            user_id=self.env.user.id,
        )

        run.action_reject()

        self.assertEqual(run.state, "cancelled")
        remaining = run.activity_ids.filtered(
            lambda a: a.activity_type_id == activity_type
        )
        self.assertFalse(remaining, "Approval activity should be closed after reject")

    def test_cron_creates_activity_when_policy_requires_approval(self):
        """cron_dispatch_queued creates an approval activity when policy gates the run."""
        self.env["ipai.agent.policy"].create({
            "name": "Activity Cron Policy",
            "target_model": "res.company",
            "require_approval": True,
        })
        run = self.env["ipai.agent.run"].create({
            "tool_id": self.tool.id,
            "target_model": "res.company",
            "target_res_id": self.env.company.id,
        })
        self.env["ipai.agent.run"].cron_dispatch_queued()

        self.assertEqual(run.state, "waiting_approval")

        activity_type = self._get_approve_type()
        if activity_type:
            activities = run.activity_ids.filtered(
                lambda a: a.activity_type_id == activity_type
            )
            self.assertTrue(activities, "Cron should schedule approval activity")

    def test_cancel_from_waiting_closes_activity(self):
        """action_cancel from waiting_approval also closes the approval activity."""
        run = self._create_run_with_waiting_approval()
        activity_type = self._get_approve_type()
        if not activity_type:
            self.skipTest("activity_type_ipai_approve not loaded in test env")

        run.activity_schedule(
            act_type_xmlid="ipai_agent.activity_type_ipai_approve",
            summary="Approve run",
            user_id=self.env.user.id,
        )
        run.action_cancel()

        self.assertEqual(run.state, "cancelled")
        remaining = run.activity_ids.filtered(
            lambda a: a.activity_type_id == activity_type
        )
        self.assertFalse(remaining, "Activity should be closed on cancel from waiting")


class TestToolAccessEnforcement(TestIpaiAgentSetup):
    """
    Server-side tool access enforcement (General settings alignment):
    - Tools with no allowed_group_ids are open to all agent users.
    - Tools with allowed_group_ids deny users not in those groups.
    - Bypass: env.su (superuser / cron context).
    """

    def test_tool_with_no_groups_allows_any_user(self):
        """A tool with no allowed_group_ids is accessible to any user."""
        tool = self.env["ipai.agent.tool"].create({
            "name": "Open Tool",
            "technical_name": "open_tool",
            "auth_mode": "none",
            # allowed_group_ids is empty
        })
        # Should not raise
        self.env["ipai.agent.run"]._check_tool_access(tool)

    def test_tool_with_admin_group_blocks_plain_user(self):
        """A tool restricted to admin group raises AccessError for a plain user."""
        admin_group = self.env.ref(
            "ipai_agent.group_ipai_agent_admin", raise_if_not_found=False
        )
        if not admin_group:
            self.skipTest("group_ipai_agent_admin not found")

        tool = self.env["ipai.agent.tool"].create({
            "name": "Admin-Only Tool",
            "technical_name": "admin_only_tool",
            "auth_mode": "none",
            "allowed_group_ids": [(4, admin_group.id)],
        })

        # Create a user without admin group
        plain_user = self.env["res.users"].create({
            "name": "Plain User",
            "login": "plain_user_test@ipai.test",
        })
        # Execute check as plain user
        with self.assertRaises(AccessError):
            self.env["ipai.agent.run"].with_user(plain_user)._check_tool_access(tool)

    def test_superuser_bypasses_tool_access_check(self):
        """Superuser context (cron) bypasses the tool allowlist check."""
        admin_group = self.env.ref(
            "ipai_agent.group_ipai_agent_admin", raise_if_not_found=False
        )
        if not admin_group:
            self.skipTest("group_ipai_agent_admin not found")

        tool = self.env["ipai.agent.tool"].create({
            "name": "Admin Cron Tool",
            "technical_name": "admin_cron_tool",
            "auth_mode": "none",
            "allowed_group_ids": [(4, admin_group.id)],
        })
        # sudo() sets env.su = True → bypassed
        # Should not raise even though the tool requires admin group
        self.env["ipai.agent.run"].sudo()._check_tool_access(tool)


class TestHmacVerification(TransactionCase):
    """HMAC-SHA256 signature verification in the webhook controller."""

    def _make_sig(self, body: bytes, timestamp: str, secret: str) -> str:
        return hmac.new(
            secret.encode(),
            body + timestamp.encode(),
            hashlib.sha256,
        ).hexdigest()

    def test_valid_signature_passes(self):
        from odoo.addons.ipai_agent.controllers.agent_webhook import IpaiAgentWebhook
        secret = "test-secret-key"
        body = b'{"run_id":"AGT/2026/0001","state":"succeeded"}'
        ts = str(int(time.time()))
        sig = self._make_sig(body, ts, secret)
        self.assertTrue(IpaiAgentWebhook._verify_signature(body, ts, sig, secret))

    def test_wrong_secret_fails(self):
        from odoo.addons.ipai_agent.controllers.agent_webhook import IpaiAgentWebhook
        secret = "test-secret-key"
        body = b'{"run_id":"AGT/2026/0001","state":"succeeded"}'
        ts = str(int(time.time()))
        sig = self._make_sig(body, ts, "different-secret")
        self.assertFalse(IpaiAgentWebhook._verify_signature(body, ts, sig, secret))

    def test_stale_timestamp_fails(self):
        from odoo.addons.ipai_agent.controllers.agent_webhook import IpaiAgentWebhook
        secret = "test-secret-key"
        body = b'{"run_id":"AGT/2026/0001","state":"succeeded"}'
        old_ts = str(int(time.time()) - 400)  # > 300s window
        sig = self._make_sig(body, old_ts, secret)
        self.assertFalse(IpaiAgentWebhook._verify_signature(body, old_ts, sig, secret))

    def test_missing_signature_fails(self):
        from odoo.addons.ipai_agent.controllers.agent_webhook import IpaiAgentWebhook
        body = b'{"run_id":"AGT/2026/0001"}'
        self.assertFalse(IpaiAgentWebhook._verify_signature(body, "", "", "secret"))
