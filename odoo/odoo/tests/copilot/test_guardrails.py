# -*- coding: utf-8 -*-
"""Read-only and safety guardrail tests.

Tests tool permission validation, blocked model enforcement,
and argument parsing safety WITHOUT requiring Odoo runtime.
"""

import unittest
from unittest.mock import MagicMock

from tests.copilot.conftest import load_tool_executor


class TestToolPermission(unittest.TestCase):
    """Verify _validate_tool_permission enforcement."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()
        cls.cls = cls.mod.CopilotToolExecutor

    def _make_executor(self):
        """Create executor instance with mocked env."""
        inst = self.cls.__new__(self.cls)
        inst.env = MagicMock()
        inst.env.__getitem__ = MagicMock(return_value=MagicMock())
        return inst

    def test_unpermitted_tool_returns_error(self):
        """Executing a tool not in permitted_tools returns error."""
        inst = self._make_executor()
        inst.env.__getitem__.return_value._get_settings.return_value = {
            "read_only_mode": True,
        }
        result = inst.execute_tool(
            "read_record",
            {"model": "res.partner", "record_id": 1},
            {"permitted_tools": ["search_docs"]},
        )
        self.assertFalse(result["success"])
        self.assertIn("not permitted", result["error"])

    def test_unknown_tool_returns_error(self):
        """Executing an unknown tool returns error."""
        inst = self._make_executor()
        # read_only_mode=False so the unknown-tool check is reached
        # (otherwise read_only_mode blocks it first since the tool
        # is not in _READ_ONLY_TOOLS).
        inst.env.__getitem__.return_value._get_settings.return_value = {
            "read_only_mode": False,
        }
        result = inst.execute_tool(
            "delete_everything",
            {},
            {"permitted_tools": ["delete_everything"]},
        )
        self.assertFalse(result["success"])
        self.assertIn("Unknown tool", result["error"])


class TestValidateScope(unittest.TestCase):
    """Verify _validate_scope enforcement."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()
        cls.cls = cls.mod.CopilotToolExecutor

    def _make_executor(self, model_exists=True):
        inst = self.cls.__new__(self.cls)
        inst.env = MagicMock()
        inst.env.__contains__ = MagicMock(return_value=model_exists)
        return inst

    def test_blocked_model_rejected(self):
        """_validate_scope rejects blocked models."""
        inst = self._make_executor()
        ok, msg = inst._validate_scope(
            "ir.config_parameter", [], {"company_id": 1}
        )
        self.assertFalse(ok)
        self.assertIn("not allowed", msg)

    def test_blocked_model_res_users_rejected(self):
        inst = self._make_executor()
        ok, msg = inst._validate_scope("res.users", [], {})
        self.assertFalse(ok)

    def test_nonexistent_model_rejected(self):
        """_validate_scope rejects non-existent models."""
        inst = self._make_executor(model_exists=False)
        ok, msg = inst._validate_scope(
            "fake.nonexistent.model", [], {"company_id": 1}
        )
        self.assertFalse(ok)
        self.assertIn("does not exist", msg)

    def test_valid_model_accepted(self):
        """_validate_scope accepts valid non-blocked models with no records."""
        inst = self._make_executor(model_exists=True)
        ok, msg = inst._validate_scope(
            "res.partner", [], {"company_id": 1}
        )
        self.assertTrue(ok)


class TestReadOnlyMode(unittest.TestCase):
    """Verify read_only_mode blocks non-READ_ONLY tools."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()
        cls.cls = cls.mod.CopilotToolExecutor

    def test_hypothetical_write_tool_blocked(self):
        """A tool not in _READ_ONLY_TOOLS is blocked in read_only_mode."""
        inst = self.cls.__new__(self.cls)
        inst.env = MagicMock()
        inst.env.__getitem__.return_value._get_settings.return_value = {
            "read_only_mode": True,
        }

        # Patch _READ_ONLY_TOOLS to exclude 'read_record'
        original = self.cls._READ_ONLY_TOOLS
        try:
            self.cls._READ_ONLY_TOOLS = frozenset(
                t for t in original if t != "read_record"
            )
            result = inst.execute_tool(
                "read_record",
                {},
                {"permitted_tools": ["read_record"]},
            )
            self.assertFalse(result["success"])
            self.assertIn("read-only mode", result["error"])
        finally:
            self.cls._READ_ONLY_TOOLS = original


class TestArgumentParsing(unittest.TestCase):
    """Verify argument parsing safety."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load_tool_executor()
        cls.cls = cls.mod.CopilotToolExecutor

    def _make_executor(self):
        inst = self.cls.__new__(self.cls)
        inst.env = MagicMock()
        inst.env.__getitem__.return_value._get_settings.return_value = {
            "read_only_mode": True,
        }
        return inst

    def test_empty_arguments_handled(self):
        """Empty string arguments are parsed as {}."""
        inst = self._make_executor()
        result = inst.execute_tool(
            "search_docs",
            "",
            {"permitted_tools": ["search_docs"]},
        )
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)

    def test_invalid_json_arguments_error(self):
        """Invalid JSON string arguments return error."""
        inst = self._make_executor()
        result = inst.execute_tool(
            "search_docs",
            "{invalid json!!!",
            {"permitted_tools": ["search_docs"]},
        )
        self.assertFalse(result["success"])
        self.assertIn("Invalid arguments", result["error"])


if __name__ == "__main__":
    unittest.main()
