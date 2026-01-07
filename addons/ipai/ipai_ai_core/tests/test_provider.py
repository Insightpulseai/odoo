# -*- coding: utf-8 -*-
"""
Tests for IPAI AI Provider Model
================================

Tests for the AI provider registry and configuration.
"""
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestAIProvider(TransactionCase):
    """Test cases for ipai.ai.provider model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Provider = cls.env['ipai.ai.provider']
        cls.company = cls.env.company

    def test_provider_create(self):
        """Test basic provider creation."""
        provider = self.Provider.create({
            'name': 'Test Kapa Provider',
            'provider_type': 'kapa',
            'company_id': self.company.id,
        })

        self.assertTrue(provider.id)
        self.assertEqual(provider.name, 'Test Kapa Provider')
        self.assertEqual(provider.provider_type, 'kapa')
        self.assertTrue(provider.active)

    def test_provider_default_single_per_company(self):
        """Test that only one provider can be default per company."""
        # Create first default provider
        provider1 = self.Provider.create({
            'name': 'Provider 1',
            'provider_type': 'kapa',
            'is_default': True,
            'company_id': self.company.id,
        })
        self.assertTrue(provider1.is_default)

        # Create second default provider
        provider2 = self.Provider.create({
            'name': 'Provider 2',
            'provider_type': 'openai',
            'is_default': True,
            'company_id': self.company.id,
        })

        # Refresh first provider
        provider1.invalidate_recordset()

        # First should no longer be default
        self.assertFalse(provider1.is_default)
        self.assertTrue(provider2.is_default)

    def test_get_default_provider(self):
        """Test get_default() method."""
        # Create default provider
        provider = self.Provider.create({
            'name': 'Default Provider',
            'provider_type': 'kapa',
            'is_default': True,
            'company_id': self.company.id,
        })

        # Get default
        default = self.Provider.get_default()
        self.assertEqual(default, provider)

    def test_get_default_falls_back_to_active(self):
        """Test get_default() falls back to any active provider."""
        # Create non-default provider
        provider = self.Provider.create({
            'name': 'Active Provider',
            'provider_type': 'kapa',
            'is_default': False,
            'company_id': self.company.id,
        })

        # Clear any existing defaults
        self.Provider.search([
            ('company_id', '=', self.company.id),
            ('is_default', '=', True),
        ]).write({'is_default': False})

        # Get default should return the active one
        default = self.Provider.get_default()
        self.assertEqual(default, provider)

    def test_update_stats(self):
        """Test statistics update method."""
        provider = self.Provider.create({
            'name': 'Stats Provider',
            'provider_type': 'kapa',
            'company_id': self.company.id,
        })

        # Initial state
        self.assertEqual(provider.total_requests, 0)
        self.assertEqual(provider.total_tokens, 0)
        self.assertEqual(provider.avg_latency_ms, 0.0)

        # First update
        provider.update_stats(latency_ms=100, tokens=50)

        self.assertEqual(provider.total_requests, 1)
        self.assertEqual(provider.total_tokens, 50)
        self.assertEqual(provider.avg_latency_ms, 100.0)

        # Second update
        provider.update_stats(latency_ms=200, tokens=100)

        self.assertEqual(provider.total_requests, 2)
        self.assertEqual(provider.total_tokens, 150)
        self.assertAlmostEqual(provider.avg_latency_ms, 150.0, places=1)

    def test_provider_types(self):
        """Test all provider types can be created."""
        provider_types = ['kapa', 'openai', 'anthropic', 'ollama']

        for ptype in provider_types:
            provider = self.Provider.create({
                'name': f'Test {ptype}',
                'provider_type': ptype,
                'company_id': self.company.id,
            })
            self.assertEqual(provider.provider_type, ptype)

    def test_provider_inactive(self):
        """Test inactive providers are excluded from get_default."""
        # Create inactive provider
        provider = self.Provider.create({
            'name': 'Inactive Provider',
            'provider_type': 'kapa',
            'is_default': True,
            'active': False,
            'company_id': self.company.id,
        })

        # Should not be returned by get_default
        default = self.Provider.get_default()
        self.assertNotEqual(default, provider)

    def test_provider_sequence(self):
        """Test provider ordering by sequence."""
        p1 = self.Provider.create({
            'name': 'Provider A',
            'provider_type': 'kapa',
            'sequence': 20,
            'company_id': self.company.id,
        })
        p2 = self.Provider.create({
            'name': 'Provider B',
            'provider_type': 'openai',
            'sequence': 10,
            'company_id': self.company.id,
        })

        providers = self.Provider.search([
            ('id', 'in', [p1.id, p2.id])
        ])

        # Should be ordered by sequence
        self.assertEqual(providers[0], p2)  # sequence 10
        self.assertEqual(providers[1], p1)  # sequence 20
