# -*- coding: utf-8 -*-
"""Citation and response schema tests.

Verifies the structure of search results returned by Azure AI Search
and KB index methods by inspecting source code contracts.
"""

import inspect
import os
import unittest
from unittest.mock import MagicMock

from tests.copilot.conftest import COPILOT_ADDON_PATH, load_tool_executor


class TestSearchViaAzureAIReturnShape(unittest.TestCase):
    """Verify _search_via_azure_ai return dict keys."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()
        cls.method = getattr(
            cls.mod.CopilotToolExecutor, "_search_via_azure_ai"
        )
        cls.src = inspect.getsource(cls.method)

    def test_returns_results_key(self):
        self.assertIn('"results"', self.src)

    def test_returns_source_key(self):
        self.assertIn('"source"', self.src)

    def test_returns_count_key(self):
        """Success path includes 'count' key."""
        self.assertIn('"count"', self.src)

    def test_error_path_includes_error_key(self):
        """Error path includes 'error' key."""
        self.assertIn('"error"', self.src)


class TestSearchKBIndexReturnShape(unittest.TestCase):
    """Verify _search_kb_index return dict keys."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()
        cls.method = getattr(
            cls.mod.CopilotToolExecutor, "_search_kb_index"
        )
        cls.src = inspect.getsource(cls.method)

    def test_returns_results_key(self):
        self.assertIn('"results"', self.src)

    def test_returns_source_key(self):
        self.assertIn('"source"', self.src)

    def test_returns_count_key(self):
        self.assertIn('"count"', self.src)

    def test_error_path_includes_error_key(self):
        self.assertIn('"error"', self.src)


class TestResultItemSchema(unittest.TestCase):
    """Verify individual result item has required fields."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()
        cls.kb_src = inspect.getsource(
            getattr(cls.mod.CopilotToolExecutor, "_search_kb_index")
        )
        cls.ai_src = inspect.getsource(
            getattr(cls.mod.CopilotToolExecutor, "_search_via_azure_ai")
        )

    def test_kb_result_has_title(self):
        self.assertIn('"title"', self.kb_src)

    def test_kb_result_has_content(self):
        self.assertIn('"content"', self.kb_src)

    def test_kb_result_has_score(self):
        self.assertIn('"score"', self.kb_src)

    def test_kb_result_has_path(self):
        self.assertIn('"path"', self.kb_src)

    def test_ai_result_has_title(self):
        self.assertIn('"title"', self.ai_src)

    def test_ai_result_has_content(self):
        self.assertIn('"content"', self.ai_src)

    def test_ai_result_has_score(self):
        self.assertIn('"score"', self.ai_src)

    def test_ai_result_has_path(self):
        self.assertIn('"path"', self.ai_src)


class TestContentTruncation(unittest.TestCase):
    """Verify content is truncated to 500 chars max."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()

    def test_truncation_in_kb_search(self):
        """[:500] truncation is applied in _search_kb_index."""
        method_src = inspect.getsource(
            getattr(self.mod.CopilotToolExecutor, "_search_kb_index")
        )
        self.assertIn("[:500]", method_src)

    def test_truncation_in_ai_search(self):
        """[:500] truncation is applied in _search_via_azure_ai."""
        method_src = inspect.getsource(
            getattr(self.mod.CopilotToolExecutor, "_search_via_azure_ai")
        )
        self.assertIn("[:500]", method_src)


class TestErrorResponseSchema(unittest.TestCase):
    """Verify error responses have required structure."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()

    def test_kb_error_has_empty_results(self):
        """Error responses set results=[]."""
        inst = self.mod.CopilotToolExecutor.__new__(
            self.mod.CopilotToolExecutor
        )
        inst.env = MagicMock()
        inst.env.__getitem__.return_value._get_settings.return_value = {
            "search_service": "",
        }

        result = inst._search_kb_index("test query", "test-index", 5)
        self.assertEqual(result["results"], [])
        self.assertEqual(result["source"], "test-index")
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
