# -*- coding: utf-8 -*-
"""Auth contract tests for FoundryService.

Tests credential resolution and header construction
WITHOUT requiring real Azure credentials.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from tests.copilot.conftest import load_foundry_service


class TestGetCredential(unittest.TestCase):
    """Verify _get_credential auth resolution."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_foundry_service()
        cls.cls = cls.mod.FoundryService

    def _make_service(self):
        inst = self.cls.__new__(self.cls)
        inst.env = MagicMock()
        return inst

    @patch.dict(os.environ, {"AZURE_FOUNDRY_API_KEY": "test-key-123"})
    def test_api_key_mode_when_env_set(self):
        """Returns ('api-key', ...) when AZURE_FOUNDRY_API_KEY is set."""
        inst = self._make_service()
        _, mode = inst._get_credential()
        self.assertEqual(mode, "api-key")

    @patch.dict(os.environ, {}, clear=True)
    def test_none_mode_without_credentials(self):
        """Returns ('none', ...) when no credentials and no azure-identity."""
        inst = self._make_service()
        original = self.mod._HAS_AZURE_IDENTITY
        try:
            self.mod._HAS_AZURE_IDENTITY = False
            _, mode = inst._get_credential()
            self.assertEqual(mode, "none")
        finally:
            self.mod._HAS_AZURE_IDENTITY = original


class TestGetAuthHeaders(unittest.TestCase):
    """Verify _get_auth_headers header construction."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_foundry_service()
        cls.cls = cls.mod.FoundryService

    def _make_service(self):
        inst = self.cls.__new__(self.cls)
        inst.env = MagicMock()
        return inst

    @patch.dict(os.environ, {"AZURE_FOUNDRY_API_KEY": "test-key-abc"})
    def test_api_key_header_format(self):
        """Returns api-key header when in api-key mode."""
        inst = self._make_service()
        headers, mode = inst._get_auth_headers()
        self.assertEqual(mode, "api-key")
        self.assertIn("api-key", headers)
        self.assertEqual(headers["api-key"], "test-key-abc")

    @patch.dict(os.environ, {}, clear=True)
    def test_empty_headers_when_none(self):
        """Returns empty dict when mode is 'none'."""
        inst = self._make_service()
        original = self.mod._HAS_AZURE_IDENTITY
        try:
            self.mod._HAS_AZURE_IDENTITY = False
            headers, mode = inst._get_auth_headers()
            self.assertEqual(mode, "none")
            self.assertEqual(headers, {})
        finally:
            self.mod._HAS_AZURE_IDENTITY = original


class TestGetSettings(unittest.TestCase):
    """Verify _get_settings returns expected keys."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_foundry_service()
        cls.cls = cls.mod.FoundryService

    def test_settings_includes_agent_api_mode(self):
        """_get_settings returns dict with 'agent_api_mode' key."""
        inst = self.cls.__new__(self.cls)
        mock_icp = MagicMock()
        mock_icp.sudo.return_value.get_param = MagicMock(
            side_effect=lambda key, default="": default
        )
        inst.env = MagicMock()
        inst.env.__getitem__ = MagicMock(return_value=mock_icp)

        settings = inst._get_settings()
        self.assertIn("agent_api_mode", settings)

    def test_agent_api_mode_default_is_agents(self):
        """Default agent_api_mode is 'agents'."""
        inst = self.cls.__new__(self.cls)
        mock_icp = MagicMock()
        mock_icp.sudo.return_value.get_param = MagicMock(
            side_effect=lambda key, default="": default
        )
        inst.env = MagicMock()
        inst.env.__getitem__ = MagicMock(return_value=mock_icp)

        settings = inst._get_settings()
        self.assertEqual(settings["agent_api_mode"], "agents")


if __name__ == "__main__":
    unittest.main()
