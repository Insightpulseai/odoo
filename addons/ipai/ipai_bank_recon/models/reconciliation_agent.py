# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import json
import logging

_logger = logging.getLogger(__name__)

class ReconciliationAgent(models.AbstractModel):
    _name = 'ipai.reconciliation.agent'
    _description = 'IPAI Bank Reconciliation Engine'

    @api.model
    def match_statement_lines(self, line_ids=False):
        """Logic to match statement lines to invoices/payments."""
        lines = self.env['account.bank.statement.line'].browse(line_ids) if line_ids else \
                self.env['account.bank.statement.line'].search([('reconciliation_state', '=', 'ingested')])
        
        for line in lines:
            try:
                candidates = self._find_candidates(line)
                
                if not candidates:
                    line.reconciliation_state = 'ambiguous'
                    line.message_post(body=_("No candidates found for matching."))
                    continue
                
                # Pick best candidate
                best_candidate = candidates[0] # Sorted by confidence
                
                # Ambiguity Check
                if len(candidates) > 1 and (round(candidates[0]['confidence'] - candidates[1]['confidence'], 2) < 0.1):
                    line.reconciliation_state = 'ambiguous'
                    line.message_post(body=_("Ambiguous: Multiple candidates with similar confidence found."))
                    continue
                
                # Tax Parity Check
                if not self._verify_tax_parity(line, best_candidate):
                    line.reconciliation_state = 'quarantined'
                    line.message_post(body=_("Quarantined: Tax parity failure (VAT/EWT mismatch)."))
                    continue

                # Success
                line.write({
                    'reconciliation_state': 'matched',
                    'confidence_score': best_candidate['confidence'],
                    'agent_evidence_pack': json.dumps({
                        'match_id': best_candidate['id'],
                        'confidence_score': best_candidate['confidence'],
                        'source_documents': [best_candidate['doc_ref']],
                        'rule_id': 'RECON_RULE_001'
                    })
                })
                line.message_post(body=_("Matched to %s (Confidence: %s)") % (best_candidate['doc_ref']['res_model'], best_candidate['confidence']))

            except Exception as e:
                _logger.error("Bank Recon Error: %s" % str(e))
                line.reconciliation_state = 'exception'
                line.message_post(body=_("Exception during reconciliation: %s") % str(e))

    def _find_candidates(self, line):
        """Search for invoices/payments matching the line."""
        # Simple amount-based exact match for now (MVP implementation)
        candidates = []
        
        # Search for unpaid invoices (Outbound / Customer)
        invoices = self.env['account.move'].search([
            ('amount_total', '=', abs(line.amount)),
            ('payment_state', '!=', 'paid'),
            ('state', '=', 'posted')
        ], limit=5)
        
        for inv in invoices:
            confidence = 0.95 if inv.ref == line.payment_ref else 0.85
            candidates.append({
                'id': inv.id,
                'confidence': confidence,
                'doc_ref': {
                    'res_model': 'account.move',
                    'res_id': inv.id,
                    'amount_parity': True,
                    'ref_match': (inv.ref == line.payment_ref)
                }
            })
            
        return sorted(candidates, key=lambda x: x['confidence'], reverse=True)

    def _verify_tax_parity(self, line, candidate):
        """Use ipai_bir_tax_compliance to verify tax logic parity."""
        # Placeholder for integration with the TaxPulse engine
        # In actual implementation, we would call RulesEvaluator here
        return True # Default to True for skeleton implementation
