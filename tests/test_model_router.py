#!/usr/bin/env python3
import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Add scripts to path to import model_router
sys.path.append(os.path.join(os.path.dirname(__file__), "../scripts"))
import model_router


class TestModelRouter(unittest.TestCase):
    def setUp(self):
        self.mock_caps = {
            "schema_version": "1.0.0",
            "policy": {
                "default_model": "ollama:test_model",
                "max_input_chars": 1000,
                "max_output_tokens": 100,
                "task_classes_local": ["local_task"],
                "task_classes_remote": ["remote_task"],
            },
        }

    @patch("model_router.load_capabilities")
    @patch("model_router.is_runtime_available")
    def test_local_routing_success(self, mock_available, mock_load):
        """Test simple local task routing."""
        mock_load.return_value = self.mock_caps
        mock_available.return_value = True

        result = model_router.get_route("local_task", 500)
        self.assertEqual(result["tier"], "local")
        self.assertEqual(result["model"], "ollama:test_model")
        self.assertIn("TASK_CLASS_LOCAL", result["reason_codes"])

    @patch("model_router.load_capabilities")
    def test_remote_task_class(self, mock_load):
        """Test explicit remote task class."""
        mock_load.return_value = self.mock_caps

        result = model_router.get_route("remote_task", 500)
        self.assertEqual(result["tier"], "remote")
        self.assertIn("TASK_CLASS_REMOTE", result["reason_codes"])

    @patch("model_router.load_capabilities")
    def test_unknown_task_class(self, mock_load):
        """Test unknown task class defaults to remote."""
        mock_load.return_value = self.mock_caps

        result = model_router.get_route("unknown_task", 500)
        self.assertIn("TASK_CLASS_UNKNOWN", result["reason_codes"])
        # Based on current implementation, unknown task returns early with reason code,
        # Default dict has tier=remote.
        self.assertEqual(result["tier"], "remote")

    @patch("model_router.load_capabilities")
    def test_input_size_exceeded(self, mock_load):
        """Test input size limit enforcement."""
        mock_load.return_value = self.mock_caps

        result = model_router.get_route("local_task", 1500)  # Limit is 1000
        self.assertEqual(result["tier"], "remote")
        self.assertIn("OVER_CHAR_LIMIT", result["reason_codes"])

    @patch("model_router.load_capabilities")
    @patch("model_router.is_runtime_available")
    def test_runtime_unavailable(self, mock_available, mock_load):
        """Test fallback when local runtime is down."""
        mock_load.return_value = self.mock_caps
        mock_available.return_value = False

        result = model_router.get_route("local_task", 500)
        self.assertEqual(result["tier"], "remote")
        self.assertIn("RUNTIME_UNAVAILABLE", result["reason_codes"])

    @patch("model_router.load_capabilities")
    def test_no_capabilities_file(self, mock_load):
        """Test missing capabilities file."""
        mock_load.return_value = None

        result = model_router.get_route("local_task", 500)
        self.assertEqual(result["tier"], "remote")
        self.assertIn("NO_CAPABILITIES_FOUND", result["reason_codes"])


if __name__ == "__main__":
    unittest.main()
