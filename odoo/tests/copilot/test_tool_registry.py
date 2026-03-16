# -*- coding: utf-8 -*-
"""Tool registry shape tests for CopilotToolExecutor.

Validates the tool handler map, read-only tools set, blocked models,
and search limits WITHOUT requiring Odoo runtime.
"""

import unittest

from tests.copilot.conftest import load_tool_executor

# Expected tool names (derived from actual source)
EXPECTED_TOOLS = frozenset({
    "read_record",
    "search_records",
    "search_docs",
    "get_report",
    "read_finance_close",
    "view_campaign_perf",
    "view_dashboard",
    "search_strategy_docs",
    "search_odoo_docs",
    "search_azure_docs",
    "search_databricks_docs",
    "search_org_docs",
    "search_spec_bundles",
    "search_architecture_docs",
})

# Expected blocked models (security-sensitive)
EXPECTED_BLOCKED_MODELS = {
    "ir.config_parameter",
    "ir.cron",
    "ir.module.module",
    "ir.rule",
    "ir.model.access",
    "res.users",
    "base.module.upgrade",
    "base.module.uninstall",
    "ir.actions.server",
    "ir.actions.act_window",
}


class TestToolRegistry(unittest.TestCase):
    """Verify _TOOL_HANDLERS registry shape."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()
        cls.executor_cls = cls.mod.CopilotToolExecutor

    def test_tool_handlers_count(self):
        """_TOOL_HANDLERS has exactly 14 entries."""
        self.assertEqual(len(self.executor_cls._TOOL_HANDLERS), 14)

    def test_all_expected_tools_present(self):
        """All 14 expected tool names are registered."""
        registered = set(self.executor_cls._TOOL_HANDLERS.keys())
        self.assertEqual(registered, EXPECTED_TOOLS)

    def test_handler_names_start_with_execute(self):
        """Every handler method name starts with '_execute_'."""
        for tool_name, handler_name in self.executor_cls._TOOL_HANDLERS.items():
            self.assertTrue(
                handler_name.startswith("_execute_"),
                f"Handler for '{tool_name}' is '{handler_name}' — "
                f"must start with '_execute_'",
            )

    def test_read_only_tools_is_frozenset(self):
        """_READ_ONLY_TOOLS is a frozenset."""
        self.assertIsInstance(self.executor_cls._READ_ONLY_TOOLS, frozenset)

    def test_read_only_tools_contains_all_handlers(self):
        """All handler keys are in _READ_ONLY_TOOLS (Stage 1)."""
        handler_keys = set(self.executor_cls._TOOL_HANDLERS.keys())
        self.assertEqual(
            handler_keys,
            set(self.executor_cls._READ_ONLY_TOOLS),
        )


class TestBlockedModels(unittest.TestCase):
    """Verify _BLOCKED_MODELS security list."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()

    def test_blocked_models_is_frozenset(self):
        self.assertIsInstance(self.mod._BLOCKED_MODELS, frozenset)

    def test_blocked_models_contains_expected(self):
        """All expected security-sensitive models are blocked."""
        for model in EXPECTED_BLOCKED_MODELS:
            self.assertIn(
                model, self.mod._BLOCKED_MODELS,
                f"'{model}' missing from _BLOCKED_MODELS",
            )

    def test_blocked_models_exact_set(self):
        """_BLOCKED_MODELS matches expected set exactly."""
        self.assertEqual(set(self.mod._BLOCKED_MODELS), EXPECTED_BLOCKED_MODELS)


class TestSearchLimits(unittest.TestCase):
    """Verify search limit constants."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()

    def test_max_search_limit(self):
        self.assertEqual(self.mod._MAX_SEARCH_LIMIT, 100)

    def test_default_search_limit(self):
        self.assertEqual(self.mod._DEFAULT_SEARCH_LIMIT, 20)


if __name__ == "__main__":
    unittest.main()
