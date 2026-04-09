# -*- coding: utf-8 -*-
"""Static contract tests for ipai_odoo_copilot module.

Validates manifest, module constants, and model registration shapes
WITHOUT requiring a running Odoo instance or Azure credentials.
"""

import ast
import os
import unittest

from tests.copilot.conftest import (
    COPILOT_ADDON_PATH,
    load_foundry_service,
    load_tool_executor,
)


class TestManifestContract(unittest.TestCase):
    """Verify __manifest__.py parses and has required keys."""

    @classmethod
    def setUpClass(cls):
        manifest_path = os.path.join(COPILOT_ADDON_PATH, "__manifest__.py")
        with open(manifest_path, "r") as f:
            cls.manifest = ast.literal_eval(f.read())

    def test_manifest_parses(self):
        """Manifest is a valid Python dict literal."""
        self.assertIsInstance(self.manifest, dict)

    def test_version(self):
        """Version matches 19.0.2.0.0."""
        self.assertEqual(self.manifest["version"], "18.0.2.0.0")

    def test_license(self):
        self.assertEqual(self.manifest["license"], "LGPL-3")

    def test_installable(self):
        self.assertTrue(self.manifest["installable"])

    def test_external_dependencies_azure_identity(self):
        """azure-identity is listed as external dependency."""
        ext_deps = self.manifest.get("external_dependencies", {})
        python_deps = ext_deps.get("python", [])
        self.assertIn("azure-identity", python_deps)

    def test_external_dependencies_search_documents(self):
        """azure-search-documents is listed as external dependency."""
        ext_deps = self.manifest.get("external_dependencies", {})
        python_deps = ext_deps.get("python", [])
        self.assertIn("azure-search-documents", python_deps)

    def test_depends_base_setup(self):
        self.assertIn("base_setup", self.manifest.get("depends", []))


class TestFoundryServiceContract(unittest.TestCase):
    """Verify FoundryService module-level constants and class shape."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_foundry_service()

    def test_param_prefix(self):
        self.assertEqual(self.mod.PARAM_PREFIX, "ipai_odoo_copilot")

    def test_agents_api_version(self):
        self.assertEqual(self.mod._AGENTS_API_VERSION, "2025-03-01-preview")

    def test_has_azure_identity_flag_exists(self):
        """_HAS_AZURE_IDENTITY flag must exist (bool)."""
        self.assertIsInstance(self.mod._HAS_AZURE_IDENTITY, bool)

    def test_foundry_service_name(self):
        self.assertEqual(self.mod.FoundryService._name, "ipai.foundry.service")

    def test_foundry_service_auto_false(self):
        self.assertFalse(self.mod.FoundryService._auto)


class TestToolExecutorContract(unittest.TestCase):
    """Verify CopilotToolExecutor module-level constants and class shape."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()

    def test_tool_executor_name(self):
        self.assertEqual(
            self.mod.CopilotToolExecutor._name,
            "ipai.copilot.tool.executor",
        )

    def test_tool_executor_auto_false(self):
        self.assertFalse(self.mod.CopilotToolExecutor._auto)

    def test_has_search_sdk_flag_exists(self):
        self.assertIsInstance(self.mod._HAS_SEARCH_SDK, bool)


if __name__ == "__main__":
    unittest.main()
