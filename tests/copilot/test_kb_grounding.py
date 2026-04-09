# -*- coding: utf-8 -*-
"""KB index name contract tests.

Validates that each KB search tool references the correct index name
and that _search_kb_index accepts the expected parameters.
"""

import inspect
import os
import unittest

from tests.copilot.conftest import COPILOT_ADDON_PATH, load_tool_executor


class TestKBIndexNames(unittest.TestCase):
    """Verify KB tools reference correct index names in source."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()

    def test_odoo_docs_index_name(self):
        """_execute_search_odoo_docs references 'odoo18-docs'."""
        method = getattr(self.mod.CopilotToolExecutor, "_execute_search_odoo_docs")
        src = inspect.getsource(method)
        self.assertIn('"odoo18-docs"', src)

    def test_azure_docs_index_name(self):
        """_execute_search_azure_docs references 'azure-platform-docs'."""
        method = getattr(self.mod.CopilotToolExecutor, "_execute_search_azure_docs")
        src = inspect.getsource(method)
        self.assertIn('"azure-platform-docs"', src)

    def test_databricks_docs_index_name(self):
        """_execute_search_databricks_docs references 'databricks-docs'."""
        method = getattr(self.mod.CopilotToolExecutor, "_execute_search_databricks_docs")
        src = inspect.getsource(method)
        self.assertIn('"databricks-docs"', src)


class TestSearchKBIndexSignature(unittest.TestCase):
    """Verify _search_kb_index method signature."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()

    def test_search_kb_index_params(self):
        """_search_kb_index accepts query, index_name, limit, filter_expr."""
        method = getattr(self.mod.CopilotToolExecutor, "_search_kb_index")
        sig = inspect.signature(method)
        param_names = list(sig.parameters.keys())
        self.assertIn("query", param_names)
        self.assertIn("index_name", param_names)
        self.assertIn("limit", param_names)
        self.assertIn("filter_expr", param_names)

    def test_filter_expr_default_none(self):
        """filter_expr defaults to None."""
        method = getattr(self.mod.CopilotToolExecutor, "_search_kb_index")
        sig = inspect.signature(method)
        param = sig.parameters["filter_expr"]
        self.assertIs(param.default, None)


class TestGetSearchClientGuard(unittest.TestCase):
    """Verify _get_search_client returns None when SDK is unavailable."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()

    def test_get_search_client_returns_none_without_sdk(self):
        """_get_search_client returns None when _HAS_SEARCH_SDK is False."""
        original = self.mod._HAS_SEARCH_SDK
        try:
            self.mod._HAS_SEARCH_SDK = False
            executor = self.mod.CopilotToolExecutor.__new__(
                self.mod.CopilotToolExecutor
            )
            result = executor._get_search_client("svc", "idx")
            self.assertIsNone(result)
        finally:
            self.mod._HAS_SEARCH_SDK = original


class TestKBResultSchema(unittest.TestCase):
    """Verify KB search result schema from source inspection."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(COPILOT_ADDON_PATH, "models", "tool_executor.py")
        with open(path, "r") as f:
            cls.source = f.read()

    def test_result_fields_in_search_kb_index(self):
        """_search_kb_index produces results with title, content, score, path, heading_chain."""
        for field in ("title", "content", "score", "path", "heading_chain"):
            self.assertIn(
                '"%s"' % field, self.source,
                f"Field '{field}' not found in _search_kb_index result construction",
            )

    def test_content_truncation(self):
        """Content is truncated to 500 chars."""
        self.assertIn("[:500]", self.source)


class TestKBEmptyQueryGuard(unittest.TestCase):
    """Verify that empty query raises UserError for each KB tool."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(COPILOT_ADDON_PATH, "models", "tool_executor.py")
        with open(path, "r") as f:
            cls.source = f.read()

    def test_odoo_docs_empty_query_guard(self):
        self.assertIn("search_odoo_docs requires 'query'", self.source)

    def test_azure_docs_empty_query_guard(self):
        self.assertIn("search_azure_docs requires 'query'", self.source)

    def test_databricks_docs_empty_query_guard(self):
        self.assertIn("search_databricks_docs requires 'query'", self.source)


if __name__ == "__main__":
    unittest.main()
