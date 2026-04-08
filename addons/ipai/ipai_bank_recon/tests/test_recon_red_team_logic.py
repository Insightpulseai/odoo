"""
Red Team Logic Test for Bank Reconciliation Agent.
Attacks the matching engine and state machine logic.
"""

import unittest
import json

class RedTeamBankLine:
    def __init__(self, amount, payment_ref=None):
        self.amount = amount
        self.payment_ref = payment_ref
        self.reconciliation_state = 'ingested'
        self.agent_evidence_pack = None
        self.confidence_score = 0.0

    def post(self):
        # RED TEAM GATE
        if self.reconciliation_state != 'approved_to_post':
            raise Exception("Fail-Closed: Blocked state")
        if not self.agent_evidence_pack:
            raise Exception("Fail-Closed: Blocked evidence")
        self.reconciliation_state = 'posted'

class RedTeamMatcher:
    def __init__(self, invoices):
        self.invoices = invoices

    def match(self, line):
        candidates = []
        for inv in self.invoices:
            if round(abs(line.amount), 2) == round(inv['amount'], 2):
                confidence = 0.95 if inv['ref'] == line.payment_ref else 0.85
                candidates.append({'id': inv['id'], 'confidence': confidence})
        
        if not candidates:
            line.reconciliation_state = 'ambiguous'
            return

        candidates.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Ambiguity Stress (Fixed 0.1 delta)
        if len(candidates) > 1 and (round(candidates[0]['confidence'] - candidates[1]['confidence'], 2) < 0.1):
            line.reconciliation_state = 'ambiguous'
            return

        line.reconciliation_state = 'matched'
        line.agent_evidence_pack = {'id': candidates[0]['id']}
        line.confidence_score = candidates[0]['confidence']

class TestRedTeamRuntime(unittest.TestCase):
    def setUp(self):
        self.invoices = [
            {'id': 'MATCH_01', 'ref': 'REF_OK', 'amount': 100.0},
            {'id': 'MATCH_02', 'ref': 'REF_ERR', 'amount': 100.0},
        ]
        self.matcher = RedTeamMatcher(self.invoices)

    def test_attack_01_direct_post_from_ingested(self):
        line = RedTeamBankLine(100.0)
        with self.assertRaisesRegex(Exception, "Fail-Closed: Blocked state"):
            line.post()

    def test_attack_02_post_missing_evidence(self):
        line = RedTeamBankLine(100.0)
        line.reconciliation_state = 'approved_to_post' # Forge state
        with self.assertRaisesRegex(Exception, "Fail-Closed: Blocked evidence"):
            line.post()

    def test_attack_03_ambiguity_collision(self):
        line = RedTeamBankLine(100.0, payment_ref='NO_MATCH')
        self.matcher.match(line)
        self.assertEqual(line.reconciliation_state, 'ambiguous')

    def test_fuzz_amount_precision(self):
        # 0.001 variance should still be blocked or handled deterministically
        # Here we use round(2) so 100.001 -> 100.00
        line = RedTeamBankLine(100.001)
        self.matcher.match(line)
        self.assertEqual(line.reconciliation_state, 'ambiguous') # Because it matches both and diff is 0

if __name__ == "__main__":
    unittest.main()
