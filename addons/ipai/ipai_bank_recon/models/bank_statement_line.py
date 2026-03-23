# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json

class BankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    reconciliation_state = fields.Selection([
        ('ingested', 'Ingested'),
        ('matched', 'Matched'),
        ('ambiguous', 'Ambiguous'),
        ('exception', 'Exception'),
        ('approved_to_post', 'Approved to Post'),
        ('posted', 'Posted'),
        ('quarantined', 'Quarantined')
    ], string='Reconciliation State', default='ingested', tracking=True)

    agent_evidence_pack = fields.Text(string='Agent Evidence Pack (JSON)', help='Grounded matching logic and document links.')
    confidence_score = fields.Float(string='Match Confidence', digits=(1, 4))
    
    # State Transition Rules
    def action_approve_reconciliation(self):
        for line in self:
            if line.reconciliation_state != 'matched':
                raise UserError(_("Only matched lines can be approved for posting."))
            if not line.agent_evidence_pack:
                raise UserError(_("Cannot approve without a valid evidence pack."))
            line.reconciliation_state = 'approved_to_post'

    def action_quarantine_reconciliation(self, reason):
        for line in self:
            line.write({
                'reconciliation_state': 'quarantined',
                'message_post_reason': reason
            })
            line.message_post(body=_("Quarantined: %s") % reason)

    def action_reset_to_ingested(self):
        for line in self:
            if line.reconciliation_state == 'posted':
                raise UserError(_("Cannot reset a posted transaction."))
            line.reconciliation_state = 'ingested'
            line.agent_evidence_pack = False
            line.confidence_score = 0.0

    # Fail-Closed Override for Standard Post
    def action_bank_reconcile_bank_statement_line(self):
        """Override standard reconcile to enforce agentic gates."""
        for line in self:
            # RED TEAM FIX: Check both state and evidence pack presence
            if not self.env.context.get('manual_override'):
                if line.reconciliation_state != 'approved_to_post':
                    raise UserError(_("Fail-Closed: Posting is blocked. Transaction must be in 'Approved to Post' state."))
                if not line.agent_evidence_pack:
                    raise UserError(_("Fail-Closed: Posting is blocked. Missing required 'Agent Evidence Pack'."))
            
        res = super(BankStatementLine, self).action_bank_reconcile_bank_statement_line()
        
        # If successful, move to posted
        for line in self:
            line.reconciliation_state = 'posted'
        return res
