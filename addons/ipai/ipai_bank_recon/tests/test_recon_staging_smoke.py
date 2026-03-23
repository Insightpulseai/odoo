# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
import json

class TestBankReconStagingSmoke(TransactionCase):
    def setUp(self):
        super(TestBankReconStagingSmoke, self).setUp()
        self.ReconAgent = self.env['ipai.reconciliation.agent']
        # Setup similar to production (Common Invoices)
        self.partner = self.env['res.partner'].create({'name': 'Staging Partner'})
        self.invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'ref': 'STAG/001',
            'invoice_line_ids': [(0, 0, {'name': 'Fees', 'price_unit': 5000.0})],
        })
        self.invoice.action_post()

    def test_smoke_happy_path(self):
        """End-to-End: Ingest -> Match -> Approve -> Post."""
        line = self.env['account.bank.statement.line'].create({
            'payment_ref': 'STAG/001',
            'amount': 5000.0,
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
        })
        self.ReconAgent.match_statement_lines(line.ids)
        self.assertEqual(line.reconciliation_state, 'matched')
        line.action_approve_reconciliation()
        line.action_bank_reconcile_bank_statement_line()
        self.assertEqual(line.reconciliation_state, 'posted')

    def test_smoke_ambiguous_quarantine(self):
        """End-to-End: Ambiguous collision -> Quarantine manually."""
        # Create second invoice with same amount
        self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'ref': 'STAG/002',
            'invoice_line_ids': [(0, 0, {'name': 'Fees', 'price_unit': 5000.0})],
        }).action_post()
        
        line = self.env['account.bank.statement.line'].create({
            'payment_ref': 'UNKNOWN',
            'amount': 5000.0,
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
        })
        self.ReconAgent.match_statement_lines(line.ids)
        self.assertEqual(line.reconciliation_state, 'ambiguous')
        
        # Manual audit -> Quarantine
        line.action_quarantine_reconciliation("Multiple candidates found in staging smoke test.")
        self.assertEqual(line.reconciliation_state, 'quarantined')

    def test_smoke_double_post_block(self):
        """End-to-End: Replay blocking."""
        line = self.env['account.bank.statement.line'].create({
            'payment_ref': 'STAG/001',
            'amount': 5000.0,
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
        })
        self.ReconAgent.match_statement_lines(line.ids)
        line.action_approve_reconciliation()
        line.action_bank_reconcile_bank_statement_line()
        
        # Replay attempt
        with self.assertRaises(UserError):
            line.action_bank_reconcile_bank_statement_line()
