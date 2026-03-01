# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

"""
Tests for Pulser intent handlers.

Layer 2: Odoo TransactionCase tests — validates handler dispatch,
data shapes, and args validation without requiring live Supabase.
"""

from unittest.mock import patch

from odoo.tests.common import TransactionCase

from ..models.pulser_handlers import ArgsValidationError


class TestPulserHandlers(TransactionCase):

    def setUp(self):
        super().setUp()
        self.handlers = self.env["ipai.pulser.handlers"]

    # ── Dispatch ────────────────────────────────────────────────────────

    def test_dispatch_unknown_type_raises(self):
        """Unknown intent types should raise ValueError."""
        with self.assertRaises(ValueError):
            self.handlers._dispatch("unknown.type", {})

    def test_dispatch_non_odoo_prefix_raises(self):
        """Non-odoo.* types should raise ValueError (not in handler map)."""
        with self.assertRaises(ValueError):
            self.handlers._dispatch("deploy", {})

    # ── odoo.healthcheck ────────────────────────────────────────────────

    @patch.dict("os.environ", {"SUPABASE_URL": "", "SUPABASE_SERVICE_ROLE_KEY": ""})
    def test_healthcheck_returns_required_keys(self):
        """Healthcheck must return all required top-level keys."""
        args = {"env": "prod", "include": {
            "addons_paths": True, "workers": True,
            "modules_count": True, "supabase_reachable": True,
        }}
        data = self.handlers._dispatch("odoo.healthcheck", args)

        self.assertIn("odoo", data)
        self.assertIn("runtime", data)
        self.assertIn("modules", data)
        self.assertIn("connectivity", data)

        self.assertIn("version", data["odoo"])
        self.assertIn("server_time_utc", data["odoo"])
        self.assertIn("db_name", data["odoo"])
        self.assertIn("addons_paths", data["odoo"])
        self.assertIsInstance(data["odoo"]["addons_paths"], list)

        self.assertIn("installed_count", data["modules"])
        self.assertIsInstance(data["modules"]["installed_count"], int)

    def test_healthcheck_invalid_env_raises(self):
        """Invalid env value should raise ArgsValidationError."""
        with self.assertRaises(ArgsValidationError) as ctx:
            self.handlers._dispatch("odoo.healthcheck", {"env": "invalid"})
        self.assertEqual(ctx.exception.code, "ARGS_INVALID")

    @patch.dict("os.environ", {"SUPABASE_URL": "", "SUPABASE_SERVICE_ROLE_KEY": ""})
    def test_healthcheck_defaults_without_args(self):
        """Healthcheck should work with empty args (defaults)."""
        data = self.handlers._dispatch("odoo.healthcheck", {})
        self.assertIn("odoo", data)

    @patch.dict("os.environ", {"SUPABASE_URL": "", "SUPABASE_SERVICE_ROLE_KEY": ""})
    def test_healthcheck_selective_include(self):
        """Healthcheck respects include flags."""
        args = {"env": "dev", "include": {
            "addons_paths": False, "workers": False,
            "modules_count": False, "supabase_reachable": False,
        }}
        data = self.handlers._dispatch("odoo.healthcheck", args)
        self.assertIsNone(data["odoo"]["addons_paths"])
        self.assertIsNone(data["runtime"]["workers"])
        self.assertIsNone(data["modules"]["installed_count"])
        self.assertIsNone(data["connectivity"]["supabase"])

    # ── odoo.modules.status ─────────────────────────────────────────────

    def test_modules_status_returns_required_keys(self):
        """Module status must return all required keys with correct types."""
        args = {
            "env": "prod",
            "limit": {"installed_sample": 50},
            "allowlist": {"profile": "oca_allowlist_v1", "include_diff": True},
            "risk": {"include": True},
        }
        data = self.handlers._dispatch("odoo.modules.status", args)

        self.assertIn("installed", data)
        self.assertIn("count", data["installed"])
        self.assertIn("sample", data["installed"])
        self.assertIsInstance(data["installed"]["sample"], list)
        self.assertLessEqual(len(data["installed"]["sample"]), 50)

        self.assertIn("allowlist", data)
        self.assertIn("passed", data["allowlist"])
        self.assertIn("missing_from_allowlist", data["allowlist"])
        self.assertIn("allowlisted_not_installed", data["allowlist"])

        self.assertIn("risk", data)

    def test_modules_status_sample_exceeds_max_raises(self):
        """installed_sample > 100 should raise ArgsValidationError."""
        args = {"env": "prod", "limit": {"installed_sample": 200}}
        with self.assertRaises(ArgsValidationError) as ctx:
            self.handlers._dispatch("odoo.modules.status", args)
        self.assertEqual(ctx.exception.code, "ARGS_INVALID")

    def test_modules_status_unknown_profile_raises(self):
        """Unknown allowlist profile should raise ALLOWLIST_PROFILE_UNKNOWN."""
        args = {
            "env": "prod",
            "allowlist": {"profile": "nonexistent_v99"},
        }
        with self.assertRaises(ArgsValidationError) as ctx:
            self.handlers._dispatch("odoo.modules.status", args)
        self.assertEqual(ctx.exception.code, "ALLOWLIST_PROFILE_UNKNOWN")

    def test_modules_status_invalid_sample_type_raises(self):
        """Non-integer installed_sample should raise ArgsValidationError."""
        args = {"env": "prod", "limit": {"installed_sample": "fifty"}}
        with self.assertRaises(ArgsValidationError) as ctx:
            self.handlers._dispatch("odoo.modules.status", args)
        self.assertEqual(ctx.exception.code, "ARGS_INVALID")

    # ── odoo.config.snapshot ────────────────────────────────────────────

    def test_config_snapshot_returns_required_keys(self):
        """Config snapshot must return all required keys (no secrets)."""
        args = {
            "env": "prod",
            "redaction": {
                "mode": "safe",
                "include_keys": ["db_host", "db_port", "workers"],
            },
            "fingerprint": {
                "algorithm": "sha256",
                "include_keys": ["db_host", "db_port", "workers"],
            },
        }
        data = self.handlers._dispatch("odoo.config.snapshot", args)

        self.assertIn("config", data)
        self.assertIn("odoo_conf_fingerprint", data["config"])
        self.assertTrue(
            data["config"]["odoo_conf_fingerprint"].startswith("sha256:")
        )

        self.assertIn("mail", data)
        self.assertIn("smtp_host", data["mail"])
        self.assertIn("smtp_port", data["mail"])
        self.assertIn("catcher_mode", data["mail"])
        self.assertIn("feature_flags", data)

    def test_config_snapshot_no_secrets(self):
        """Config snapshot must never include passwords or secret keys."""
        args = {"env": "prod", "redaction": {"mode": "safe"}}
        data = self.handlers._dispatch("odoo.config.snapshot", args)

        data_str = str(data).lower()
        self.assertNotIn("password", data_str)
        self.assertNotIn("secret", data_str)
        self.assertNotIn("smtp_pass", data_str)
        self.assertNotIn("service_role_key", data_str)

    def test_config_snapshot_unsupported_redaction_mode_raises(self):
        """Unsupported redaction mode should raise REDACTION_MODE_UNSUPPORTED."""
        args = {"env": "prod", "redaction": {"mode": "raw"}}
        with self.assertRaises(ArgsValidationError) as ctx:
            self.handlers._dispatch("odoo.config.snapshot", args)
        self.assertEqual(ctx.exception.code, "REDACTION_MODE_UNSUPPORTED")

    def test_config_snapshot_unsafe_keys_raises(self):
        """Requesting unsafe keys should raise ARGS_INVALID."""
        args = {
            "env": "prod",
            "redaction": {
                "mode": "safe",
                "include_keys": ["db_host", "admin_passwd"],
            },
        }
        with self.assertRaises(ArgsValidationError) as ctx:
            self.handlers._dispatch("odoo.config.snapshot", args)
        self.assertEqual(ctx.exception.code, "ARGS_INVALID")
        self.assertIn("admin_passwd", str(ctx.exception.details))

    def test_config_snapshot_invalid_env_raises(self):
        """Invalid env should raise ARGS_INVALID."""
        args = {"env": "staging"}
        with self.assertRaises(ArgsValidationError) as ctx:
            self.handlers._dispatch("odoo.config.snapshot", args)
        self.assertEqual(ctx.exception.code, "ARGS_INVALID")
