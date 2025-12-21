# -*- coding: utf-8 -*-
"""
Close Approval Gate

Control checkpoints that must pass before cycle completion.
"""
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CloseApprovalGateTemplate(models.Model):
    """
    Template for approval gates (maps from A1 Checks).
    """

    _name = "close.approval.gate.template"
    _description = "Close Approval Gate Template"
    _order = "sequence, code"

    code = fields.Char(string="Code", required=True, index=True)
    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)

    gate_type = fields.Selection([
        ("manual", "Manual Approval"),
        ("automated", "Automated Check"),
        ("threshold", "Threshold Check"),
    ], string="Type", default="manual", required=True)

    description = fields.Html(string="Description")
    pass_criteria = fields.Text(string="Pass Criteria")

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    # Bridge to A1
    a1_check_id = fields.Many2one(
        "a1.check",
        string="A1 Check",
        help="Source check from A1 Control Center",
    )


class CloseApprovalGate(models.Model):
    """
    Approval gate instance for a close cycle.
    """

    _name = "close.approval.gate"
    _description = "Close Approval Gate"
    _order = "sequence, id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Core fields
    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)

    # Relationships
    cycle_id = fields.Many2one(
        "close.cycle",
        string="Close Cycle",
        required=True,
        ondelete="cascade",
        index=True,
    )
    template_id = fields.Many2one(
        "close.approval.gate.template",
        string="Template",
    )

    # Gate configuration
    gate_type = fields.Selection([
        ("manual", "Manual Approval"),
        ("automated", "Automated Check"),
        ("threshold", "Threshold Check"),
    ], string="Type", default="manual", required=True)

    # Status
    state = fields.Selection([
        ("pending", "Pending"),
        ("ready", "Ready for Check"),
        ("blocked", "Blocked"),
        ("passed", "Passed"),
        ("failed", "Failed"),
    ], string="State", default="pending", tracking=True, required=True)

    # Approval
    approver_id = fields.Many2one(
        "res.users",
        string="Approver",
        tracking=True,
    )
    approved_date = fields.Datetime(string="Approved At")
    approved_by = fields.Many2one("res.users", string="Approved By")

    # Threshold (for threshold checks)
    threshold_value = fields.Float(string="Threshold Value")
    actual_value = fields.Float(string="Actual Value")

    # Blocking reason
    block_reason = fields.Text(string="Block Reason")

    # Multi-company
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="cycle_id.company_id",
        store=True,
    )

    notes = fields.Html(string="Notes")

    def action_mark_ready(self):
        """Mark gate as ready for checking."""
        self.ensure_one()
        if self.state != "pending":
            return
        self.state = "ready"
        self.message_post(body=f"Gate marked ready by {self.env.user.name}")

        # Notify approver
        if self.approver_id:
            self.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=self.approver_id.id,
                summary=f"Gate ready for approval: {self.name}",
            )

    def action_pass(self):
        """Mark gate as passed."""
        self.ensure_one()
        if self.state not in ("ready", "blocked"):
            return
        self.write({
            "state": "passed",
            "approved_date": fields.Datetime.now(),
            "approved_by": self.env.user.id,
            "block_reason": False,
        })
        self.message_post(body=f"Gate passed by {self.env.user.name}")
        self._trigger_webhook("close.gate.passed")

    def action_fail(self):
        """Mark gate as failed."""
        self.ensure_one()
        if self.state not in ("ready", "blocked"):
            return
        self.state = "failed"
        self.message_post(body=f"Gate failed by {self.env.user.name}")
        self._trigger_webhook("close.gate.failed")

    def action_block(self, reason=None):
        """Block the gate with a reason."""
        self.ensure_one()
        self.write({
            "state": "blocked",
            "block_reason": reason or "Blocked pending resolution",
        })
        self.message_post(body=f"Gate blocked: {self.block_reason}")
        self._trigger_webhook("close.gate.blocked")

    def action_unblock(self):
        """Unblock the gate."""
        self.ensure_one()
        if self.state != "blocked":
            return
        self.write({
            "state": "ready",
            "block_reason": False,
        })
        self.message_post(body=f"Gate unblocked by {self.env.user.name}")

    def _trigger_webhook(self, event_type):
        """Trigger webhook for gate events."""
        cycle = self.cycle_id
        if not cycle.webhook_url:
            return

        import json
        import requests

        data = {
            "source": "odoo",
            "module": "ipai_close_orchestration",
            "event": event_type,
            "company_id": self.company_id.id,
            "cycle": {"id": cycle.id, "name": cycle.name},
            "gate": {
                "id": self.id,
                "name": self.name,
                "state": self.state,
            },
            "ts": fields.Datetime.now().isoformat(),
        }

        try:
            requests.post(
                cycle.webhook_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
        except Exception as e:
            _logger.warning("Webhook failed for gate %s: %s", self.name, e)

    @api.model
    def _cron_check_gates(self):
        """Check automated gates and update status."""
        gates = self.search([
            ("state", "=", "pending"),
            ("gate_type", "=", "automated"),
        ])

        for gate in gates:
            # Check if all tasks in cycle are done
            cycle = gate.cycle_id
            all_done = all(
                t.state in ("done", "cancelled")
                for t in cycle.task_ids
            )
            if all_done:
                gate.action_mark_ready()

        # Check threshold gates
        threshold_gates = self.search([
            ("state", "=", "ready"),
            ("gate_type", "=", "threshold"),
        ])

        for gate in threshold_gates:
            if gate.actual_value is not None and gate.threshold_value is not None:
                if gate.actual_value >= gate.threshold_value:
                    gate.action_pass()
                else:
                    gate.action_fail()

        _logger.info("Gate check completed: %d automated, %d threshold", len(gates), len(threshold_gates))
