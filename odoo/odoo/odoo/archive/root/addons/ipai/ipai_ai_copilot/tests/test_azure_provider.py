# © 2026 InsightPulse AI — License LGPL-3.0-or-later
"""
Tests for Azure OpenAI provider integration in ipai_ai_copilot.

Covers:
  - Config seeding from env vars
  - Deployment-name validation
  - Provider resolution
  - Azure API call with mocked HTTP responses
"""
import json
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase

from odoo.addons.ipai_ai_copilot.hooks import post_init_hook
from odoo.addons.ipai_ai_copilot.services.azure_openai import (
    AzureCallError,
    AzureConfigError,
    call_azure_openai,
    get_azure_config,
    has_azure_config,
    validate_config,
)
from odoo.addons.ipai_ai_copilot.services.provider_bridge import call_provider


class TestAzureConfigSeeding(TransactionCase):
    """Test post_init_hook seeds ir.config_parameter from env vars."""

    def setUp(self):
        super().setUp()
        self.icp = self.env["ir.config_parameter"].sudo()

    @patch.dict(
        "os.environ",
        {
            "AZURE_OPENAI_BASE_URL": "https://test.openai.azure.com",
            "AZURE_OPENAI_API_KEY": "test-key-123",
            "AZURE_OPENAI_DEPLOYMENT": "my-gpt4o-deploy",
            "AZURE_OPENAI_API_MODE": "responses",
        },
    )
    def test_seed_from_env_vars(self):
        """Config params should be seeded when DB values are empty."""
        # Clear any existing values
        for key in [
            "ipai_ask_ai_azure.base_url",
            "ipai_ask_ai_azure.api_key",
            "ipai_ask_ai_azure.model",
            "ipai_ask_ai_azure.api_mode",
        ]:
            self.icp.set_param(key, "")

        post_init_hook(self.env)

        self.assertEqual(
            self.icp.get_param("ipai_ask_ai_azure.base_url"),
            "https://test.openai.azure.com",
        )
        self.assertEqual(
            self.icp.get_param("ipai_ask_ai_azure.api_key"),
            "test-key-123",
        )
        self.assertEqual(
            self.icp.get_param("ipai_ask_ai_azure.model"),
            "my-gpt4o-deploy",
        )
        self.assertEqual(
            self.icp.get_param("ipai_ask_ai_azure.api_mode"),
            "responses",
        )

    @patch.dict(
        "os.environ",
        {
            "AZURE_OPENAI_BASE_URL": "https://new-endpoint.openai.azure.com",
            "AZURE_OPENAI_API_KEY": "new-key",
            "AZURE_OPENAI_DEPLOYMENT": "new-deploy",
        },
    )
    def test_seed_does_not_overwrite_existing(self):
        """Existing non-empty DB values must not be overwritten."""
        self.icp.set_param("ipai_ask_ai_azure.base_url", "https://existing.openai.azure.com")
        self.icp.set_param("ipai_ask_ai_azure.api_key", "existing-key")
        self.icp.set_param("ipai_ask_ai_azure.model", "existing-deploy")

        post_init_hook(self.env)

        self.assertEqual(
            self.icp.get_param("ipai_ask_ai_azure.base_url"),
            "https://existing.openai.azure.com",
        )
        self.assertEqual(
            self.icp.get_param("ipai_ask_ai_azure.api_key"),
            "existing-key",
        )
        self.assertEqual(
            self.icp.get_param("ipai_ask_ai_azure.model"),
            "existing-deploy",
        )

    @patch.dict("os.environ", {}, clear=True)
    def test_seed_no_env_vars(self):
        """When no env vars are set, no params should be seeded."""
        for key in [
            "ipai_ask_ai_azure.base_url",
            "ipai_ask_ai_azure.api_key",
            "ipai_ask_ai_azure.model",
            "ipai_ask_ai_azure.api_mode",
        ]:
            self.icp.set_param(key, "")

        post_init_hook(self.env)

        # api_mode gets default "responses" even without env var
        self.assertEqual(self.icp.get_param("ipai_ask_ai_azure.base_url", ""), "")
        self.assertEqual(self.icp.get_param("ipai_ask_ai_azure.api_key", ""), "")
        self.assertEqual(self.icp.get_param("ipai_ask_ai_azure.model", ""), "")


class TestAzureConfigValidation(TransactionCase):
    """Test deployment-name validation and config reading."""

    def test_validate_config_missing_deployment(self):
        """Deployment name must be set when base_url and api_key are present."""
        cfg = {
            "base_url": "https://test.openai.azure.com",
            "api_key": "test-key",
            "deployment": "",
            "api_mode": "responses",
        }
        with self.assertRaises(AzureConfigError) as ctx:
            validate_config(cfg)
        self.assertEqual(ctx.exception.code, "AZURE_DEPLOYMENT_MISSING")

    def test_validate_config_missing_base_url(self):
        """base_url must be set."""
        cfg = {"base_url": "", "api_key": "key", "deployment": "dep", "api_mode": "responses"}
        with self.assertRaises(AzureConfigError) as ctx:
            validate_config(cfg)
        self.assertEqual(ctx.exception.code, "AZURE_NOT_CONFIGURED")

    def test_validate_config_valid(self):
        """Valid config should not raise."""
        cfg = {
            "base_url": "https://test.openai.azure.com",
            "api_key": "test-key",
            "deployment": "my-deploy",
            "api_mode": "responses",
        }
        validate_config(cfg)  # Should not raise

    def test_has_azure_config(self):
        """has_azure_config checks all three required fields."""
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("ipai_ask_ai_azure.base_url", "https://test.openai.azure.com")
        icp.set_param("ipai_ask_ai_azure.api_key", "test-key")
        icp.set_param("ipai_ask_ai_azure.model", "my-deploy")

        self.assertTrue(has_azure_config(self.env))

    def test_has_azure_config_incomplete(self):
        """Incomplete config returns False."""
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("ipai_ask_ai_azure.base_url", "https://test.openai.azure.com")
        icp.set_param("ipai_ask_ai_azure.api_key", "")
        icp.set_param("ipai_ask_ai_azure.model", "")

        self.assertFalse(has_azure_config(self.env))


class TestAzureOpenAICall(TransactionCase):
    """Test Azure OpenAI API calls with mocked HTTP."""

    def setUp(self):
        super().setUp()
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("ipai_ask_ai_azure.base_url", "https://test.openai.azure.com")
        icp.set_param("ipai_ask_ai_azure.api_key", "test-key-abc")
        icp.set_param("ipai_ask_ai_azure.model", "gpt4o-deploy")
        icp.set_param("ipai_ask_ai_azure.api_mode", "responses")

    @patch("odoo.addons.ipai_ai_copilot.services.azure_openai.url_request.urlopen")
    def test_call_responses_api(self, mock_urlopen):
        """Test successful call using Responses API mode."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "id": "resp-123",
            "output": [
                {
                    "content": [
                        {"type": "output_text", "text": "Hello from Azure!"}
                    ]
                }
            ],
        }).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = call_azure_openai(self.env, "What is Odoo?")

        self.assertEqual(result["provider"], "azure_openai")
        self.assertEqual(result["text"], "Hello from Azure!")
        self.assertEqual(result["model"], "gpt4o-deploy")
        self.assertEqual(result["trace_id"], "resp-123")
        self.assertEqual(result["api_mode"], "responses")

    @patch("odoo.addons.ipai_ai_copilot.services.azure_openai.url_request.urlopen")
    def test_call_chat_completions_api(self, mock_urlopen):
        """Test successful call using Chat Completions API mode."""
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("ipai_ask_ai_azure.api_mode", "chat_completions")

        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "id": "chatcmpl-456",
            "choices": [
                {"message": {"content": "Hello from chat completions!"}}
            ],
        }).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = call_azure_openai(self.env, "What is Odoo?")

        self.assertEqual(result["text"], "Hello from chat completions!")
        self.assertEqual(result["api_mode"], "chat_completions")

    def test_call_missing_deployment(self):
        """Call with empty deployment should raise AzureConfigError."""
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("ipai_ask_ai_azure.model", "")

        with self.assertRaises(AzureConfigError) as ctx:
            call_azure_openai(self.env, "test")
        self.assertEqual(ctx.exception.code, "AZURE_DEPLOYMENT_MISSING")


class TestProviderResolution(TransactionCase):
    """Test the provider bridge resolution logic."""

    def test_no_provider_configured(self):
        """Returns error when no provider is configured."""
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("ipai_ask_ai_azure.base_url", "")
        icp.set_param("ipai_ask_ai_azure.api_key", "")
        icp.set_param("ipai_ask_ai_azure.model", "")

        data, error = call_provider(self.env, "Hello")
        self.assertIsNone(data)
        self.assertEqual(error, "NO_PROVIDER_CONFIGURED")

    @patch("odoo.addons.ipai_ai_copilot.services.provider_bridge.call_azure_openai")
    def test_azure_is_preferred(self, mock_azure):
        """Azure direct should be used when configured."""
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("ipai_ask_ai_azure.base_url", "https://test.openai.azure.com")
        icp.set_param("ipai_ask_ai_azure.api_key", "test-key")
        icp.set_param("ipai_ask_ai_azure.model", "my-deploy")

        mock_azure.return_value = {
            "provider": "azure_openai",
            "text": "mocked response",
            "model": "my-deploy",
            "trace_id": "t-1",
            "api_mode": "responses",
        }

        data, error = call_provider(self.env, "Hello")
        self.assertIsNone(error)
        self.assertEqual(data["provider"], "azure_openai")
        mock_azure.assert_called_once()
