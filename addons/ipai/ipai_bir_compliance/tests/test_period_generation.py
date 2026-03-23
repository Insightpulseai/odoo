# -*- coding: utf-8 -*-
"""Tests for obligation period generation and overdue detection."""
from datetime import date

from odoo.tests.common import TransactionCase


class TestPeriodGeneration(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.branch = cls.env.ref('ipai_branch_profile.branch_pasig_ho')
        cls.form_0619e = cls.env.ref('ipai_bir_compliance.bir_form_0619e')
        cls.form_1701q = cls.env.ref('ipai_bir_compliance.bir_form_1701q')

    def _create_obligation(self, form, branch=None):
        return self.env['l10n.ph.bir.obligation'].create({
            'company_id': self.env.company.id,
            'branch_id': (branch or self.branch).id,
            'form_id': form.id,
            'start_date': date(2026, 1, 1),
            'filing_channel': 'ebirforms',
        })

    def test_monthly_generates_12_periods(self):
        """Monthly obligation (0619E) generates 12 periods for the year."""
        obligation = self._create_obligation(self.form_0619e)
        obligation.action_generate_periods()
        periods = self.env['l10n.ph.bir.period'].search([
            ('obligation_id', '=', obligation.id),
        ])
        self.assertEqual(len(periods), 12)

    def test_quarterly_generates_3_periods_for_1701q(self):
        """1701Q generates 3 periods (Q1-Q3, Q4 covered by annual 1701)."""
        obligation = self._create_obligation(self.form_1701q)
        obligation.action_generate_periods()
        periods = self.env['l10n.ph.bir.period'].search([
            ('obligation_id', '=', obligation.id),
        ])
        self.assertEqual(len(periods), 3)

    def test_idempotent_generation(self):
        """Running generate_periods twice does not duplicate entries."""
        obligation = self._create_obligation(self.form_0619e)
        obligation.action_generate_periods()
        obligation.action_generate_periods()
        periods = self.env['l10n.ph.bir.period'].search([
            ('obligation_id', '=', obligation.id),
        ])
        self.assertEqual(len(periods), 12)

    def test_period_status_workflow(self):
        """Period can transition open -> prepared -> filed -> paid."""
        obligation = self._create_obligation(self.form_0619e)
        obligation.action_generate_periods()
        period = self.env['l10n.ph.bir.period'].search([
            ('obligation_id', '=', obligation.id),
        ], limit=1)
        self.assertEqual(period.status, 'open')
        period.action_mark_prepared()
        self.assertEqual(period.status, 'prepared')
        period.action_mark_filed()
        self.assertEqual(period.status, 'filed')
        period.action_mark_paid()
        self.assertEqual(period.status, 'paid')

    def test_filing_evidence_creation(self):
        """Filing record links to period and updates period status."""
        obligation = self._create_obligation(self.form_0619e)
        obligation.action_generate_periods()
        period = self.env['l10n.ph.bir.period'].search([
            ('obligation_id', '=', obligation.id),
        ], limit=1)
        filing = self.env['l10n.ph.bir.filing'].create({
            'period_id': period.id,
            'filing_reference': 'TEST-001',
            'amount_due': 5000.00,
            'amount_paid': 5000.00,
        })
        filing.action_mark_filed()
        self.assertEqual(filing.status, 'filed')
        self.assertEqual(period.status, 'filed')
        filing.action_mark_paid()
        self.assertEqual(filing.status, 'paid')
        self.assertEqual(period.status, 'paid')
