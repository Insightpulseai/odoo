# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
import json
import logging

class TestBankReconRedTeam(TransactionCase):
    def setUp(self):
        super(TestBankReconRedTeam, self).setUp()
        self.ReconAgent = self.env['ipai.reconciliation.agent']
        self.statement = self.env['account.bank.statement'].create({
            'name': 'Red Team Statement',
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
        })
        self.invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.env['res.partner'].create({'name': 'Adversary Partner'}).id,
            'ref': 'INV/RED/001',
            'invoice_line_ids': [(0, 0, {'name': 'Target', 'price_unit': 1000.0})],
        })
        self.invoice.action_post()

    def test_attack_01_direct_post_bypass(self):
        """ATTACK: Bypass the 'approved_to_post' state and call reconcile directly."""
        line = self.env['account.bank.statement.line'].create({
            'statement_id': self.statement.id,
            'amount': 1000.0,
            'reconciliation_state': 'ingested',
            'journal_id': self.statement.journal_id.id,
        })
        
        with self.assertRaisesRegex(UserError, "Fail-Closed: Posting is blocked"):
            line.action_bank_reconcile_bank_statement_line()
        self.assertEqual(line.reconciliation_state, 'ingested', "State should remain unchanged after failed bypass.")

    def test_attack_02_illegal_state_transition(self):
        """ATTACK: Force the state to 'approved_to_post' without match logic."""
        line = self.env['account.bank.statement.line'].create({
            'statement_id': self.statement.id,
            'amount': 1000.0,
            'reconciliation_state': 'ingested',
            'journal_id': self.statement.journal_id.id,
        })
        
        # Odoo's write will allow it, but our GATE must block the POST if the logical criteria aren't met
        # (Though in our module, we also check for agent_evidence_pack)
        line.write({'reconciliation_state': 'approved_to_post'})
        
        with self.assertRaisesRegex(UserError, "Fail-Closed: Posting is blocked"):
             # We need to refine the gate to also check for evidence pack even if state is forged
             line.action_bank_reconcile_bank_statement_line()

    def test_attack_03_duplicate_submit_replay(self):
        """ATTACK: Replay the post action on an already posted line."""
        line = self.env['account.bank.statement.line'].create({
            'statement_id': self.statement.id,
            'amount': 1000.0,
            'journal_id': self.statement.journal_id.id,
        })
        # Setup for success
        self.ReconAgent.match_statement_lines(line.ids)
        line.action_approve_reconciliation()
        line.action_bank_reconcile_bank_statement_line() # First post
        self.assertEqual(line.reconciliation_state, 'posted')
        
        # Second post attempt
        with self.assertRaisesRegex(UserError, "Fail-Closed: Posting is blocked"):
             line.action_bank_reconcile_bank_statement_line()

    def test_fuzz_01_ambiguity_collision(self):
        """FUZZ: Two candidates with identical amounts and no matching references."""
        self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.invoice.partner_id.id,
            'ref': 'INV/RED/002',
            'invoice_line_ids': [(0, 0, {'name': 'Other', 'price_unit': 1000.0})],
        }).action_post()
        
        line = self.env['account.bank.statement.line'].create({
            'statement_id': self.statement.id,
            'amount': 1000.0,
            'payment_ref': 'UNKNOWN',
            'journal_id': self.statement.journal_id.id,
        })
        
        self.ReconAgent.match_statement_lines(line.ids)
        self.assertEqual(line.reconciliation_state, 'ambiguous', "Collision must route to ambiguous state.")

    def test_fuzz_02_precision_near_equality(self):
        """FUZZ: Floating point near-equality (0.01 delta)."""
        line = self.env['account.bank.statement.line'].create({
            'statement_id': self.statement.id,
            'amount': 1000.01, # 0.01 over
            'journal_id': self.statement.journal_id.id,
        })
        self.ReconAgent.match_statement_lines(line.ids)
        self.assertEqual(line.reconciliation_state, 'ambiguous', "Amount drift of 0.01 must be blocked.")
