# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestOperatingBranch(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Branch = cls.env['operating.branch']
        cls.company = cls.env.company

    def test_seed_pasig_exists(self):
        """Pasig head office seed record exists with correct branch code."""
        branch = self.env.ref('ipai_branch_profile.branch_pasig_ho')
        self.assertEqual(branch.branch_code, '00000')
        self.assertTrue(branch.is_head_office)
        self.assertEqual(branch.tin, '215-308-716')

    def test_seed_makati_exists(self):
        """Makati W9 branch seed record exists with correct branch code."""
        branch = self.env.ref('ipai_branch_profile.branch_makati_w9')
        self.assertEqual(branch.branch_code, '00001')
        self.assertFalse(branch.is_head_office)
        self.assertEqual(branch.tin, '215-308-716')

    def test_full_tin_branch_computed(self):
        """full_tin_branch is TIN-branch_code."""
        branch = self.env.ref('ipai_branch_profile.branch_pasig_ho')
        self.assertEqual(branch.full_tin_branch, '215-308-716-00000')

    def test_full_tin_branch_makati(self):
        branch = self.env.ref('ipai_branch_profile.branch_makati_w9')
        self.assertEqual(branch.full_tin_branch, '215-308-716-00001')

    def test_unique_branch_code(self):
        """Duplicate BIR branch code in same company raises IntegrityError."""
        from psycopg2 import IntegrityError
        with self.assertRaises(IntegrityError):
            self.Branch.create({
                'name': 'Duplicate',
                'code': 'DUP-01',
                'tin': '215-308-716',
                'branch_code': '00000',  # same as Pasig HO
                'registered_address': 'Test',
                'company_id': self.company.id,
            })

    def test_create_new_branch(self):
        """Creating a new branch with distinct code succeeds."""
        branch = self.Branch.create({
            'name': 'Cebu Branch',
            'code': 'CEBU-01',
            'tin': '215-308-716',
            'branch_code': '00002',
            'registered_address': 'Cebu Business Park, Cebu City',
            'company_id': self.company.id,
            'vat_registered': True,
        })
        self.assertEqual(branch.full_tin_branch, '215-308-716-00002')
        self.assertTrue(branch.active)
