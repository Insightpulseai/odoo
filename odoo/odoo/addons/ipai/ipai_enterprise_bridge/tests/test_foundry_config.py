# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from unittest.mock import MagicMock, patch

from odoo.tests import TransactionCase


class TestFoundryProviderConfig(TransactionCase):
    """Test cases for Foundry Provider Configuration model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.FoundryConfig = cls.env["ipai.foundry.provider.config"]

    def test_create_default(self):
        """Test creating a Foundry config with defaults."""
        config = self.FoundryConfig.create(
            {"name": "Test Foundry", "endpoint": "https://test.azure.com"}
        )
        self.assertEqual(config.name, "Test Foundry")
        self.assertEqual(config.endpoint, "https://test.azure.com")
        self.assertEqual(config.auth_mode, "managed_identity")
        self.assertEqual(config.api_version, "2024-12-01-preview")

    def test_create_with_all_fields(self):
        """Test creating config with all fields populated."""
        config = self.FoundryConfig.create(
            {
                "name": "Full Config",
                "endpoint": "https://foundry.azure.com",
                "project_name": "ipai-project",
                "model_deployment": "gpt-4o",
                "auth_mode": "api_key",
                "api_version": "2025-01-01",
            }
        )
        self.assertEqual(config.project_name, "ipai-project")
        self.assertEqual(config.model_deployment, "gpt-4o")
        self.assertEqual(config.auth_mode, "api_key")

    def test_action_test_connection_success(self):
        """Test connection test with successful HTTP response."""
        config = self.FoundryConfig.create(
            {"name": "Test", "endpoint": "https://test.azure.com"}
        )
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "OK"

        with patch("requests.get", return_value=mock_resp) as mock_get:
            result = config.action_test_connection()
            mock_get.assert_called_once()
            call_url = mock_get.call_args[0][0]
            self.assertIn("/openai/models", call_url)

        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "display_notification")
        self.assertIn("OK", result["params"]["message"])
        self.assertIsNotNone(config.last_test_date)

    def test_action_test_connection_http_error(self):
        """Test connection test with HTTP error response."""
        config = self.FoundryConfig.create(
            {"name": "Test", "endpoint": "https://test.azure.com"}
        )
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"

        with patch("requests.get", return_value=mock_resp):
            result = config.action_test_connection()

        self.assertIn("Error", result["params"]["message"])
        self.assertEqual(result["params"]["type"], "warning")

    def test_action_test_connection_network_failure(self):
        """Test connection test with network failure."""
        import requests

        config = self.FoundryConfig.create(
            {"name": "Test", "endpoint": "https://unreachable.invalid"}
        )

        with patch(
            "requests.get",
            side_effect=requests.ConnectionError("Connection refused"),
        ):
            result = config.action_test_connection()

        self.assertIn("Connection failed", result["params"]["message"])

    def test_endpoint_trailing_slash_stripped(self):
        """Test that trailing slashes in endpoint are handled."""
        config = self.FoundryConfig.create(
            {"name": "Test", "endpoint": "https://test.azure.com/"}
        )
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "OK"

        with patch("requests.get", return_value=mock_resp) as mock_get:
            config.action_test_connection()
            call_url = mock_get.call_args[0][0]
            self.assertNotIn("//openai", call_url)
            self.assertIn("/openai/models", call_url)


class TestDocDigitizationConfig(TransactionCase):
    """Test cases for Document Digitization Configuration model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.DocConfig = cls.env["ipai.doc.digitization.config"]

    def test_create_default(self):
        """Test creating a Doc Digitization config with defaults."""
        config = self.DocConfig.create({"name": "Test OCR"})
        self.assertEqual(config.name, "Test OCR")
        self.assertEqual(config.provider, "azure_di")
        self.assertEqual(config.model, "prebuilt-invoice")
        self.assertEqual(config.storage_mode, "attachment")
        self.assertTrue(config.async_enabled)
        self.assertEqual(config.min_file_size, 0)

    def test_create_tesseract_provider(self):
        """Test creating config with Tesseract provider."""
        config = self.DocConfig.create(
            {
                "name": "Tesseract",
                "provider": "tesseract",
                "endpoint": "http://localhost:8080",
            }
        )
        self.assertEqual(config.provider, "tesseract")

    def test_action_test_connection_no_endpoint(self):
        """Test connection test with no endpoint configured."""
        config = self.DocConfig.create({"name": "No Endpoint"})
        result = config.action_test_connection()
        self.assertIn("No endpoint", result["params"]["message"])
        self.assertEqual(result["params"]["type"], "warning")

    def test_action_test_connection_success(self):
        """Test connection test with successful HTTP response."""
        config = self.DocConfig.create(
            {"name": "Test", "endpoint": "https://doc-ai.azure.com"}
        )
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "OK"

        with patch("requests.get", return_value=mock_resp) as mock_get:
            result = config.action_test_connection()
            call_url = mock_get.call_args[0][0]
            self.assertIn("/info", call_url)

        self.assertIn("OK", result["params"]["message"])
        self.assertEqual(result["params"]["type"], "info")

    def test_action_test_connection_http_error(self):
        """Test connection test with HTTP error."""
        config = self.DocConfig.create(
            {"name": "Test", "endpoint": "https://doc-ai.azure.com"}
        )
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"

        with patch("requests.get", return_value=mock_resp):
            result = config.action_test_connection()

        self.assertIn("Error", result["params"]["message"])

    def test_action_test_connection_network_failure(self):
        """Test connection test with network failure."""
        import requests

        config = self.DocConfig.create(
            {"name": "Test", "endpoint": "https://unreachable.invalid"}
        )
        with patch(
            "requests.get",
            side_effect=requests.ConnectionError("Connection refused"),
        ):
            result = config.action_test_connection()

        self.assertIn("Connection failed", result["params"]["message"])

    def test_all_providers_selectable(self):
        """Test that all provider options are valid."""
        for provider in ("azure_di", "tesseract", "custom"):
            config = self.DocConfig.create(
                {"name": f"Test {provider}", "provider": provider}
            )
            self.assertEqual(config.provider, provider)

    def test_storage_modes(self):
        """Test both storage mode options."""
        for mode in ("attachment", "azure_blob"):
            config = self.DocConfig.create(
                {"name": f"Test {mode}", "storage_mode": mode}
            )
            self.assertEqual(config.storage_mode, mode)


class TestSettingsActions(TransactionCase):
    """Test cases for settings action methods."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Settings = cls.env["res.config.settings"]

    def test_get_or_create_singleton_creates(self):
        """Test singleton helper creates record if none exists."""
        # Clear any existing records
        self.env["ipai.foundry.provider.config"].search([]).unlink()
        settings = self.Settings.create({})
        config = settings._get_or_create_singleton(
            "ipai.foundry.provider.config",
            {"name": "Auto-Created", "endpoint": ""},
        )
        self.assertTrue(config.exists())
        self.assertEqual(config.name, "Auto-Created")

    def test_get_or_create_singleton_returns_existing(self):
        """Test singleton helper returns existing record."""
        existing = self.env["ipai.foundry.provider.config"].create(
            {"name": "Existing", "endpoint": "https://existing.com"}
        )
        settings = self.Settings.create({})
        config = settings._get_or_create_singleton(
            "ipai.foundry.provider.config",
            {"name": "Should Not Create", "endpoint": ""},
        )
        self.assertEqual(config.id, existing.id)

    def test_action_open_api_keys(self):
        """Test API keys action returns URL action."""
        settings = self.Settings.create({})
        result = settings.action_open_api_keys()
        self.assertEqual(result["type"], "ir.actions.act_url")
        self.assertIn("api-keys", result["url"])

    def test_action_open_foundry_provider(self):
        """Test opening Foundry provider config."""
        settings = self.Settings.create({})
        result = settings.action_open_foundry_provider()
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "ipai.foundry.provider.config")
        self.assertEqual(result["target"], "new")

    def test_action_open_doc_digitization_provider(self):
        """Test opening Doc Digitization config."""
        settings = self.Settings.create({})
        result = settings.action_open_doc_digitization_provider()
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "ipai.doc.digitization.config")
        self.assertEqual(result["target"], "new")

    def test_action_test_foundry_no_config(self):
        """Test Foundry connection test with no config."""
        self.env["ipai.foundry.provider.config"].search([]).unlink()
        settings = self.Settings.create({})
        result = settings.action_test_foundry_connection()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("No Foundry", result["params"]["message"])

    def test_action_test_doc_digitization_no_config(self):
        """Test Doc Digitization connection test with no config."""
        self.env["ipai.doc.digitization.config"].search([]).unlink()
        settings = self.Settings.create({})
        result = settings.action_test_doc_digitization_connection()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertIn("No Document Digitization", result["params"]["message"])


class TestResConfigSettingsFields(TransactionCase):
    """Test that new config_parameter fields work correctly."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Settings = cls.env["res.config.settings"]
        cls.params = cls.env["ir.config_parameter"].sudo()

    def test_foundry_fields_exist(self):
        """Test all Foundry fields are accessible."""
        settings = self.Settings.create({})
        # These should not raise
        _ = settings.ipai_foundry_enabled
        _ = settings.ipai_foundry_endpoint
        _ = settings.ipai_foundry_project_name
        _ = settings.ipai_foundry_model_deployment
        _ = settings.ipai_foundry_auth_mode
        _ = settings.ipai_foundry_api_version

    def test_doc_ai_fields_exist(self):
        """Test all Doc AI fields are accessible."""
        settings = self.Settings.create({})
        _ = settings.ipai_doc_ai_enabled
        _ = settings.ipai_doc_ai_provider
        _ = settings.ipai_doc_ai_endpoint
        _ = settings.ipai_doc_ai_model
        _ = settings.ipai_doc_ai_storage_mode
        _ = settings.ipai_doc_ai_async_enabled
        _ = settings.ipai_doc_ai_min_file_size

    def test_foundry_defaults(self):
        """Test Foundry field default values."""
        settings = self.Settings.create({})
        self.assertFalse(settings.ipai_foundry_enabled)
        self.assertEqual(settings.ipai_foundry_auth_mode, "managed_identity")
        self.assertEqual(settings.ipai_foundry_api_version, "2024-12-01-preview")

    def test_doc_ai_defaults(self):
        """Test Doc AI field default values."""
        settings = self.Settings.create({})
        self.assertFalse(settings.ipai_doc_ai_enabled)
        self.assertEqual(settings.ipai_doc_ai_provider, "azure_di")
        self.assertEqual(settings.ipai_doc_ai_model, "prebuilt-invoice")
        self.assertEqual(settings.ipai_doc_ai_storage_mode, "attachment")
        self.assertTrue(settings.ipai_doc_ai_async_enabled)
        self.assertEqual(settings.ipai_doc_ai_min_file_size, 0)
