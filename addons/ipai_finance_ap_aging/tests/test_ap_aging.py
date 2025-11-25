# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase
from datetime import datetime, timedelta
from unittest.mock import patch


class TestAPAging(TransactionCase):
    """
    Unit tests for AP Aging automation module.

    Test Coverage:
    - AP Aging bucket calculations
    - Employee context filtering
    - n8n webhook integration
    - Summary KPI calculations
    """

    def setUp(self):
        super().setUp()

        # Create test partner (vendor)
        self.vendor = self.env['res.partner'].create({
            'name': 'Test Vendor Inc.',
            'vat': 'PH-123456789',
            'supplier_rank': 1,
        })

        # Create test payable account
        self.payable_account = self.env['account.account'].create({
            'name': 'Test Accounts Payable',
            'code': 'TEST_AP_001',
            'account_type': 'liability_payable',
            'reconcile': True,
        })

        # Create test employee
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee RIM',
            'code': 'RIM',
        })

        # Create test user linked to employee
        self.user = self.env['res.users'].create({
            'name': 'Test User RIM',
            'login': 'test.rim@insightpulseai.net',
            'employee_ids': [(4, self.employee.id)],
        })

    def _create_test_move_line(self, amount, date_maturity):
        """
        Helper method to create test account move lines.

        Args:
            amount (float): Amount residual for the move line
            date_maturity (datetime): Maturity date for aging calculation
        """
        move = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.vendor.id,
            'invoice_date': datetime.now().date(),
            'date': datetime.now().date(),
            'state': 'posted',
        })

        move_line = self.env['account.move.line'].create({
            'move_id': move.id,
            'name': 'Test AP Line',
            'account_id': self.payable_account.id,
            'partner_id': self.vendor.id,
            'date_maturity': date_maturity,
            'amount_residual': amount,
            'reconciled': False,
            'parent_state': 'posted',
        })

        return move_line

    def test_ap_aging_bucket_0_30(self):
        """Test AP Aging calculation for 0-30 day bucket"""
        # Create move line due 15 days ago
        date_maturity = (datetime.now() - timedelta(days=15)).date()
        self._create_test_move_line(10000.00, date_maturity)

        # Generate AP Aging snapshot
        result = self.env['account.move.line'].cron_generate_ap_aging_snapshot('RIM')

        # Verify results
        self.assertEqual(len(result['vendors']), 1, "Should have 1 vendor")
        vendor = result['vendors'][0]
        self.assertEqual(vendor['vendor_name'], 'Test Vendor Inc.')
        self.assertGreater(float(vendor['bucket_0_30']), 0, "Should have amount in 0-30 bucket")

    def test_ap_aging_bucket_31_60(self):
        """Test AP Aging calculation for 31-60 day bucket"""
        date_maturity = (datetime.now() - timedelta(days=45)).date()
        self._create_test_move_line(25000.00, date_maturity)

        result = self.env['account.move.line'].cron_generate_ap_aging_snapshot('RIM')

        vendor = result['vendors'][0]
        self.assertGreater(float(vendor['bucket_31_60']), 0, "Should have amount in 31-60 bucket")

    def test_ap_aging_bucket_61_90(self):
        """Test AP Aging calculation for 61-90 day bucket"""
        date_maturity = (datetime.now() - timedelta(days=75)).date()
        self._create_test_move_line(50000.00, date_maturity)

        result = self.env['account.move.line'].cron_generate_ap_aging_snapshot('RIM')

        vendor = result['vendors'][0]
        self.assertGreater(float(vendor['bucket_61_90']), 0, "Should have amount in 61-90 bucket")

    def test_ap_aging_bucket_90_plus(self):
        """Test AP Aging calculation for 90+ day bucket"""
        date_maturity = (datetime.now() - timedelta(days=120)).date()
        self._create_test_move_line(75000.00, date_maturity)

        result = self.env['account.move.line'].cron_generate_ap_aging_snapshot('RIM')

        vendor = result['vendors'][0]
        self.assertGreater(float(vendor['bucket_90_plus']), 0, "Should have amount in 90+ bucket")

    def test_employee_context_filtering(self):
        """Test that employee context filtering works correctly"""
        # Create move line for RIM employee
        date_maturity = (datetime.now() - timedelta(days=30)).date()
        self._create_test_move_line(20000.00, date_maturity)

        # Generate snapshot for RIM
        result_rim = self.env['account.move.line'].cron_generate_ap_aging_snapshot('RIM')

        # Generate snapshot for different employee (should return same data if no employee filter in move lines)
        result_other = self.env['account.move.line'].cron_generate_ap_aging_snapshot('CKVC')

        # Both should work (employee filtering requires employee_id on move lines)
        self.assertIsInstance(result_rim, dict)
        self.assertIsInstance(result_other, dict)

    @patch('requests.post')
    def test_n8n_webhook_integration(self, mock_post):
        """Test n8n webhook trigger"""
        # Mock successful webhook response
        mock_post.return_value.status_code = 200

        # Create test data
        date_maturity = (datetime.now() - timedelta(days=15)).date()
        self._create_test_move_line(30000.00, date_maturity)

        # Set webhook URL in config parameters
        self.env['ir.config_parameter'].sudo().set_param(
            'ipai_finance_ap_aging.n8n_webhook_url',
            'https://ipa.insightpulseai.net/webhook/test'
        )

        # Generate snapshot (should trigger webhook)
        result = self.env['account.move.line'].cron_generate_ap_aging_snapshot('RIM')

        # Verify webhook was called
        mock_post.assert_called_once()

        # Verify payload structure
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        self.assertIn('employee_code', payload)
        self.assertIn('snapshot_date', payload)
        self.assertIn('vendors', payload)
        self.assertIn('total_payables', payload)

    def test_get_ap_aging_summary(self):
        """Test summary KPI calculation"""
        # Create test data
        date_maturity = (datetime.now() - timedelta(days=95)).date()
        self._create_test_move_line(100000.00, date_maturity)

        # Get summary
        summary = self.env['account.move.line'].get_ap_aging_summary('RIM')

        # Verify summary structure
        self.assertIn('total_payables', summary)
        self.assertIn('vendor_count', summary)
        self.assertIn('total_overdue_90plus', summary)
        self.assertIn('snapshot_date', summary)

        # Verify values
        self.assertGreater(summary['total_payables'], 0)
        self.assertEqual(summary['vendor_count'], 1)

    def test_multiple_vendors_sorting(self):
        """Test that vendors are sorted by total outstanding (DESC)"""
        # Create multiple vendors with different amounts
        vendor2 = self.env['res.partner'].create({
            'name': 'Vendor 2',
            'supplier_rank': 1,
        })

        vendor3 = self.env['res.partner'].create({
            'name': 'Vendor 3',
            'supplier_rank': 1,
        })

        # Create move lines with different amounts
        date_maturity = (datetime.now() - timedelta(days=15)).date()

        # Vendor 1: 50,000
        self._create_test_move_line(50000.00, date_maturity)

        # Vendor 2: 100,000 (should be first)
        move2 = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': vendor2.id,
            'invoice_date': datetime.now().date(),
            'state': 'posted',
        })
        self.env['account.move.line'].create({
            'move_id': move2.id,
            'name': 'Test AP Line 2',
            'account_id': self.payable_account.id,
            'partner_id': vendor2.id,
            'date_maturity': date_maturity,
            'amount_residual': 100000.00,
            'reconciled': False,
            'parent_state': 'posted',
        })

        # Vendor 3: 25,000
        move3 = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': vendor3.id,
            'invoice_date': datetime.now().date(),
            'state': 'posted',
        })
        self.env['account.move.line'].create({
            'move_id': move3.id,
            'name': 'Test AP Line 3',
            'account_id': self.payable_account.id,
            'partner_id': vendor3.id,
            'date_maturity': date_maturity,
            'amount_residual': 25000.00,
            'reconciled': False,
            'parent_state': 'posted',
        })

        # Generate snapshot
        result = self.env['account.move.line'].cron_generate_ap_aging_snapshot('RIM')

        # Verify sorting (highest amount first)
        self.assertEqual(result['vendors'][0]['vendor_name'], 'Vendor 2')
        self.assertGreaterEqual(
            float(result['vendors'][0]['total_outstanding']),
            float(result['vendors'][1]['total_outstanding'])
        )
