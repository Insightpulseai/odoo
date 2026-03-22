import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class IpaiCopilotActionQueue(models.Model):
    _name = 'ipai.copilot.action.queue'
    _description = 'Copilot Action Queue'
    _order = 'create_date desc'
    _rec_name = 'display_name'

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------

    action_type = fields.Selection(
        [
            ('post_entry', 'Post Journal Entry'),
            ('approve_expense', 'Approve Expense'),
            ('update_status', 'Update Status'),
            ('escalate', 'Escalate'),
        ],
        string='Action Type',
        required=True,
    )
    payload = fields.Text(
        string='Payload (JSON)',
        help='JSON-serialised action parameters.',
    )
    status = fields.Selection(
        [
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('executed', 'Executed'),
            ('rejected', 'Rejected'),
            ('failed', 'Failed'),
        ],
        string='Status',
        default='pending',
        required=True,
        index=True,
    )
    requested_by = fields.Many2one(
        'res.users',
        string='Requested By',
        default=lambda self: self.env.uid,
        required=True,
        index=True,
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
    )
    executed_at = fields.Datetime(
        string='Executed At',
    )
    result = fields.Text(
        string='Result',
        help='Execution result or error details.',
    )
    display_name = fields.Char(
        compute='_compute_display_name',
        store=True,
    )

    # ------------------------------------------------------------------
    # SQL constraints
    # ------------------------------------------------------------------

    _sql_constraints = [
        (
            'status_approved_needs_approver',
            "CHECK(status != 'approved' OR approved_by IS NOT NULL)",
            'An approved action must have an approver.',
        ),
    ]

    # ------------------------------------------------------------------
    # Compute
    # ------------------------------------------------------------------

    @api.depends('action_type', 'status', 'create_date')
    def _compute_display_name(self):
        for rec in self:
            ts = rec.create_date.strftime('%Y-%m-%d %H:%M') if rec.create_date else '(new)'
            rec.display_name = '%s / %s / %s' % (
                rec.action_type or '?',
                rec.status or '?',
                ts,
            )

    # ------------------------------------------------------------------
    # Constrains
    # ------------------------------------------------------------------

    @api.constrains('payload')
    def _check_payload_json(self):
        for rec in self:
            if rec.payload:
                try:
                    json.loads(rec.payload)
                except (json.JSONDecodeError, TypeError):
                    raise ValidationError(
                        _('Payload must be valid JSON.')
                    )

    # ------------------------------------------------------------------
    # Action methods
    # ------------------------------------------------------------------

    def action_approve(self):
        """Mark the queued action as approved by the current user."""
        self.ensure_one()
        if self.status != 'pending':
            raise ValidationError(
                _('Only pending actions can be approved.')
            )
        self.write({
            'status': 'approved',
            'approved_by': self.env.uid,
        })
        _logger.info(
            'Copilot action %s approved by uid=%s', self.id, self.env.uid,
        )

    def action_reject(self):
        """Reject the queued action."""
        self.ensure_one()
        if self.status != 'pending':
            raise ValidationError(
                _('Only pending actions can be rejected.')
            )
        self.write({'status': 'rejected'})
        _logger.info(
            'Copilot action %s rejected by uid=%s', self.id, self.env.uid,
        )

    def action_execute(self):
        """Execute an approved action (stub).

        The real implementation will dispatch to the appropriate Odoo
        service based on ``action_type``.
        """
        self.ensure_one()
        if self.status != 'approved':
            raise ValidationError(
                _('Only approved actions can be executed.')
            )
        # Stub — real dispatch goes here
        self.write({
            'status': 'executed',
            'executed_at': fields.Datetime.now(),
            'result': 'Executed (stub — no-op)',
        })
        _logger.info('Copilot action %s executed (stub)', self.id)
