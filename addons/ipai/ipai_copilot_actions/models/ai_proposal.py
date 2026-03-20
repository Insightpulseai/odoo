# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AiProposal(models.Model):
    """AI-generated proposal requiring human review before commit.

    Implements proposal-first pattern: AI suggests, human approves.
    No financial or compliance write happens without explicit approval.
    """

    _name = 'ipai.ai.proposal'
    _description = 'AI Proposal (Human-in-the-Loop)'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    # --- Link to job ---
    job_id = fields.Many2one('ipai.ai.job', required=True, ondelete='cascade', index=True)
    correlation_id = fields.Char(related='job_id.correlation_id', store=True)

    # --- Target ---
    target_model = fields.Char(required=True)
    target_record_id = fields.Integer()
    target_record_name = fields.Char()
    proposal_type = fields.Selection(
        [
            ('create', 'Create Record'),
            ('update', 'Update Fields'),
            ('classify', 'Classify'),
            ('draft_entry', 'Draft Journal Entry'),
            ('suggest', 'Suggestion Only'),
        ],
        required=True,
    )

    # --- Proposed data ---
    proposed_values = fields.Json()
    proposed_summary = fields.Text()
    confidence = fields.Float(related='job_id.confidence', store=True)

    # --- Extracted fields (finance-specific) ---
    vendor_name = fields.Char()
    invoice_number = fields.Char()
    invoice_date = fields.Date()
    total_amount = fields.Float()
    currency_code = fields.Char()
    tax_amount = fields.Float()
    account_code = fields.Char()
    suggested_partner_id = fields.Many2one('res.partner')

    # --- Review state ---
    state = fields.Selection(
        [
            ('pending', 'Pending Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('edited', 'Edited & Approved'),
        ],
        default='pending',
        required=True,
        tracking=True,
        index=True,
    )
    reviewer_id = fields.Many2one('res.users', string='Reviewed By')
    reviewed_at = fields.Datetime()
    review_notes = fields.Text()

    # --- Result of approval ---
    created_record_model = fields.Char()
    created_record_id = fields.Integer()

    # --- Approval actions ---

    def action_approve(self):
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_('Only pending proposals can be approved.'))
        self.write({
            'state': 'approved',
            'reviewer_id': self.env.user.id,
            'reviewed_at': fields.Datetime.now(),
        })
        self._execute_proposal()

    def action_reject(self):
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_('Only pending proposals can be rejected.'))
        self.write({
            'state': 'rejected',
            'reviewer_id': self.env.user.id,
            'reviewed_at': fields.Datetime.now(),
        })

    def action_edit_and_approve(self):
        """Open wizard for editing proposed values before approval."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Edit Proposal'),
            'res_model': 'ipai.ai.proposal',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _execute_proposal(self):
        """Execute the approved proposal. Override per proposal_type."""
        self.ensure_one()
        if self.proposal_type == 'draft_entry':
            self._execute_draft_entry()
        elif self.proposal_type == 'create':
            self._execute_create()
        elif self.proposal_type == 'update':
            self._execute_update()

    def _execute_draft_entry(self):
        """Create draft journal entry from approved proposal."""
        if not self.proposed_values:
            return
        vals = self.proposed_values
        move_vals = {
            'move_type': vals.get('move_type', 'in_invoice'),
            'partner_id': self.suggested_partner_id.id if self.suggested_partner_id else False,
            'invoice_date': self.invoice_date,
            'ref': self.invoice_number,
            'state': 'draft',  # Always draft — never auto-post
        }
        if vals.get('line_ids'):
            from odoo.fields import Command
            move_vals['invoice_line_ids'] = [
                Command.create(line) for line in vals['line_ids']
            ]
        try:
            move = self.env['account.move'].create(move_vals)
            self.write({
                'created_record_model': 'account.move',
                'created_record_id': move.id,
            })
            self.job_id.message_post(
                body=_('Draft entry %s created from approved proposal.', move.name),
            )
        except Exception as e:
            _logger.exception('Failed to create draft entry from proposal %s', self.id)
            raise UserError(_('Failed to create draft entry: %s', str(e))) from e

    def _execute_create(self):
        """Create a record from approved proposal."""
        if not self.proposed_values or not self.target_model:
            return
        try:
            record = self.env[self.target_model].create(self.proposed_values)
            self.write({
                'created_record_model': self.target_model,
                'created_record_id': record.id,
            })
        except Exception as e:
            _logger.exception('Failed to create record from proposal %s', self.id)
            raise UserError(_('Failed to create record: %s', str(e))) from e

    def _execute_update(self):
        """Update fields on existing record from approved proposal."""
        if not self.proposed_values or not self.target_model or not self.target_record_id:
            return
        try:
            record = self.env[self.target_model].browse(self.target_record_id)
            record.write(self.proposed_values)
        except Exception as e:
            _logger.exception('Failed to update record from proposal %s', self.id)
            raise UserError(_('Failed to update record: %s', str(e))) from e
