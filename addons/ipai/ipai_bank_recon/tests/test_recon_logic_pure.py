"""
Pure Python Logic Test for Bank Reconciliation Agent.
Verifies the state machine and matching algorithm without Odoo dependencies.
"""

import json
import unittest

class MockBankStatementLine:
    def __init__(self, id, payment_ref, amount):
        self.id = id
        self.payment_ref = payment_ref
        self.amount = amount
        self.reconciliation_state = 'ingested'
        self.agent_evidence_pack = None
        self.confidence_score = 0.0
        self.messages = []

    def message_post(self, body):
        self.messages.append(body)

class BankReconLogic:
    def __init__(self, invoices):
        self.invoices = invoices

    def match_line(self, line):
        candidates = self._find_candidates(line)
        
        if not candidates:
            line.reconciliation_state = 'ambiguous'
            line.message_post("No candidates found.")
            return

        best = candidates[0]
        
        # Ambiguity Check
        if len(candidates) > 1 and (round(candidates[0]['confidence'] - candidates[1]['confidence'], 2) < 0.1):
            line.reconciliation_state = 'ambiguous'
            line.message_post("Ambiguous: Multiple close candidates.")
            return

        # Success match
        line.reconciliation_state = 'matched'
        line.confidence_score = best['confidence']
        line.agent_evidence_pack = {
            'match_id': best['id'],
            'confidence_score': best['confidence'],
            'source_documents': [best['doc_ref']]
        }
        line.message_post(f"Matched to {best['id']}")

    def _find_candidates(self, line):
        candidates = []
        for inv in self.invoices:
            if inv['amount'] == abs(line.amount):
                confidence = 0.95 if inv['ref'] == line.payment_ref else 0.85
                candidates.append({
                    'id': inv['id'],
                    'confidence': confidence,
                    'doc_ref': {'id': inv['id'], 'amount_parity': True}
                })
        return sorted(candidates, key=lambda x: x['confidence'], reverse=True)

class TestBankReconLogic(unittest.TestCase):
    def setUp(self):
        self.invoices = [
            {'id': 'INV001', 'ref': 'REF123', 'amount': 1000.0},
            {'id': 'INV002', 'ref': 'REF456', 'amount': 2000.0},
            {'id': 'INV003', 'ref': 'OTHER', 'amount': 1000.0},
        ]
        self.engine = BankReconLogic(self.invoices)

    def test_happy_path(self):
        line = MockBankStatementLine(1, 'REF123', 1000.0)
        self.engine.match_line(line)
        self.assertEqual(line.reconciliation_state, 'matched')
        self.assertEqual(line.agent_evidence_pack['match_id'], 'INV001')

    def test_ambiguous_amount(self):
        # Two invoices with 1000 but neither match the reference 'REF999'
        line = MockBankStatementLine(2, 'REF999', 1000.0)
        self.engine.match_line(line)
        self.assertEqual(line.reconciliation_state, 'ambiguous')

    def test_no_match(self):
        line = MockBankStatementLine(3, 'REFXXX', 555.55)
        self.engine.match_line(line)
        self.assertEqual(line.reconciliation_state, 'ambiguous')

if __name__ == "__main__":
    unittest.main()
