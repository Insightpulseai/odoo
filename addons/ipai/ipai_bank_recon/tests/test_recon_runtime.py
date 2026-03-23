# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
import json

class TestBankReconciliationRuntime(TransactionCase):
    def setUp(self):
        super(TestBankReconciliationRuntime, self).setUp()
        self.ReconAgent = self.env['ipai.reconciliation.agent']
        
        # Create a sample Bank Statement
        self.statement = self.env['account.bank.statement'].create({
            'name': 'Test Statement',
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
        })
        
        # Create a sample Invoice to match
        self.invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.env['res.partner'].create({'name': 'Test Partner'}).id,
            'ref': 'INV/2026/0001',
            'invoice_line_ids': [(0, 0, {
                'name': 'Test Product',
                'quantity': 1,
                'price_unit': 11200.0,
            })],
        })
        self.invoice.action_post()

    def test_case_01_happy_path(self):
        """Clean match -> Matched -> Approved to Post -> Posted."""
        line = self.env['account.bank.statement.line'].create({
            'statement_id': self.statement.id,
            'payment_ref': 'INV/2026/0001',
            'amount': 11200.0,
            'journal_id': self.statement.journal_id.id,
        })
        
        # 1. Run Matcher
        self.ReconAgent.match_statement_lines(line.ids)
        self.assertEqual(line.reconciliation_state, 'matched')
        self.assertAlmostEqual(line.confidence_score, 0.95)
        
        # 2. Approve
        line.action_approve_reconciliation()
        self.assertEqual(line.reconciliation_state, 'approved_to_post')
        
        # 3. Post (Simulate Odoo reconciliation)
        line.action_bank_reconcile_bank_statement_line()
        self.assertEqual(line.reconciliation_state, 'posted')

    def test_case_02_ambiguous_match(self):
        """Multiple candidates -> Ambiguous state."""
        # Create another invoice with same amount
        self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.invoice.partner_id.id,
            'ref': 'INV/2026/0002',
            'invoice_line_ids': [(0, 0, {'name': 'P2', 'price_unit': 11200.0})],
        }).action_post()
        
        line = self.env['account.bank.statement.line'].create({
            'statement_id': self.statement.id,
            'payment_ref': 'UNKNOWN_REF',
            'amount': 11200.0,
            'journal_id': self.statement.journal_id.id,
        })
        
        self.ReconAgent.match_statement_lines(line.ids)
        self.assertEqual(line.reconciliation_state, 'ambiguous')
        self.assertIn("Multiple candidates", line.message_ids[0].body)

    def test_case_03_fail_closed_gate(self):
        """Posting is blocked if state is not 'approved_to_post'."""
        line = self.env['account.bank.statement.line'].create({
            'statement_id': self.statement.id,
            'payment_ref': 'INV/2026/0001',
            'amount': 11200.0,
            'journal_id': self.statement.journal_id.id,
        })
        
        # Try to post directly from 'ingested'
        with self.assertRaises(UserError) as cm:
            line.action_bank_reconcile_bank_statement_line()
        self.assertIn("Fail-Closed: Posting is blocked", str(cm.exception))

    def test_case_04_quarantine_tax_parity(self):
        """(Future) Tax parity failure leads to Quarantine."""
        # This requires actual TaxPulse integration, currently mocked in _verify_tax_parity
        pass
