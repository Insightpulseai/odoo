# -*- coding: utf-8 -*-
"""Foundry compatibility seam tests.

Verifies agent resolution path selection and API mode configuration
WITHOUT requiring live Azure endpoints.
"""

import inspect
import os
import unittest

from tests.copilot.conftest import (
    BRIDGE_ADDON_PATH,
    load_foundry_provider_config,
    load_foundry_service,
)


class TestResolveAgentPathSelection(unittest.TestCase):
    """Verify _resolve_agent path selection by mode."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_foundry_service()
        cls.src = inspect.getsource(
            getattr(cls.mod.FoundryService, "_resolve_agent")
        )

    def test_agents_mode_uses_agents_path(self):
        """mode='agents' uses '/agents' path."""
        self.assertIn('"/agents"', self.src)

    def test_assistants_compat_uses_openai_path(self):
        """mode='assistants-compat' uses '/openai/assistants' path."""
        self.assertIn('"/openai/assistants"', self.src)

    def test_resolve_agent_signature_has_agent_api_mode(self):
        """_resolve_agent accepts agent_api_mode parameter."""
        sig = inspect.signature(
            getattr(self.mod.FoundryService, "_resolve_agent")
        )
        self.assertIn("agent_api_mode", sig.parameters)

    def test_agent_api_mode_default_is_agents(self):
        """agent_api_mode defaults to 'agents'."""
        sig = inspect.signature(
            getattr(self.mod.FoundryService, "_resolve_agent")
        )
        self.assertEqual(
            sig.parameters["agent_api_mode"].default, "agents"
        )


class TestEnsureAgentPassesMode(unittest.TestCase):
    """Verify ensure_agent passes agent_api_mode from settings."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_foundry_service()
        cls.src = inspect.getsource(
            getattr(cls.mod.FoundryService, "ensure_agent")
        )

    def test_ensure_agent_reads_agent_api_mode(self):
        """ensure_agent reads agent_api_mode from settings."""
        self.assertIn("agent_api_mode", self.src)

    def test_ensure_agent_passes_to_resolve_agent(self):
        """ensure_agent passes agent_api_mode to _resolve_agent."""
        self.assertIn("agent_api_mode=", self.src)


class TestFoundryProviderConfigDefaults(unittest.TestCase):
    """Verify FoundryProviderConfig field defaults."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_foundry_provider_config()
        cls.src_path = os.path.join(
            BRIDGE_ADDON_PATH, "models", "foundry_provider_config.py"
        )
        with open(cls.src_path, "r") as f:
            cls.src = f.read()

    def test_model_name(self):
        self.assertEqual(
            self.mod.FoundryProviderConfig._name,
            "ipai.foundry.provider.config",
        )

    def test_api_version_default(self):
        """api_version default is '2025-03-01-preview'."""
        self.assertIn('"2025-03-01-preview"', self.src)


class TestGetSettingsAgentApiMode(unittest.TestCase):
    """Verify _get_settings returns agent_api_mode with default."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_foundry_service()

    def test_settings_agent_api_mode_key(self):
        """_get_settings source contains 'agent_api_mode' key."""
        src = inspect.getsource(
            getattr(self.mod.FoundryService, "_get_settings")
        )
        self.assertIn('"agent_api_mode"', src)

    def test_settings_agent_api_mode_default_agents(self):
        """Default value for agent_api_mode in _get_settings is 'agents'."""
        src = inspect.getsource(
            getattr(self.mod.FoundryService, "_get_settings")
        )
        self.assertIn('"agents"', src)


if __name__ == "__main__":
    unittest.main()
