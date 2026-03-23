"""
Staging Smoke Logic Test for Bank Reconciliation Agent.
Verifies end-to-end scenarios in a simulated staging environment.
"""

import unittest
import json

class StagingBankLine:
    def __init__(self, id, amount, ref=None):
        self.id = id
        self.amount = amount
        self.payment_ref = ref
        self.reconciliation_state = 'ingested'
        self.agent_evidence_pack = None
        self.confidence_score = 0.0

    def approve(self):
        if self.reconciliation_state != 'matched':
            raise Exception("Invalid state for approval")
        self.reconciliation_state = 'approved_to_post'

    def post(self):
        if self.reconciliation_state != 'approved_to_post':
            raise Exception("Fail-Closed: Blocked")
        self.reconciliation_state = 'posted'

class StagingReconAgent:
    def __init__(self, db):
        self.db = db

    def match(self, line):
        candidates = [inv for inv in self.db if inv['amount'] == line.amount]
        if len(candidates) == 1:
            line.reconciliation_state = 'matched'
            line.agent_evidence_pack = {'id': candidates[0]['id']}
            line.confidence_score = 0.95
        elif len(candidates) > 1:
            line.reconciliation_state = 'ambiguous'
        else:
            line.reconciliation_state = 'ambiguous'

class TestStagingSmoke(unittest.TestCase):
    def setUp(self):
        self.db = [
            {'id': 'STAG_INV_01', 'amount': 1000.0, 'ref': 'REF_01'},
            {'id': 'STAG_INV_02', 'amount': 2000.0, 'ref': 'REF_02'},
        ]
        self.agent = StagingReconAgent(self.db)

    def test_happy_path(self):
        line = StagingBankLine(1, 1000.0, 'REF_01')
        self.agent.match(line)
        line.approve()
        line.post()
        self.assertEqual(line.reconciliation_state, 'posted')

    def test_ambiguous_block(self):
        self.db.append({'id': 'STAG_INV_03', 'amount': 1000.0, 'ref': 'REF_03'})
        line = StagingBankLine(2, 1000.0, 'REF_DIFF')
        self.agent.match(line)
        self.assertEqual(line.reconciliation_state, 'ambiguous')
        with self.assertRaises(Exception):
            line.post()

    def test_double_post_protection(self):
        line = StagingBankLine(3, 2000.0, 'REF_02')
        self.agent.match(line)
        line.approve()
        line.post()
        # Simulate replay
        with self.assertRaises(Exception):
            line.post()

if __name__ == "__main__":
    unittest.main()
