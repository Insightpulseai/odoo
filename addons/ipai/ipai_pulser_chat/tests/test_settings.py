# -*- coding: utf-8 -*-
"""
test_settings.py — Verifies res.config.settings read/write behaviour and
validation constraints for ipai_pulser_chat config parameters.
"""

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("ipai", "ipai_pulser_chat", "-at_install", "post_install")
class TestSettings(TransactionCase):
    """Settings model read/write and constraint tests."""

    def _new_settings(self, **values):
        """Helper: create a transient res.config.settings record with given values."""
        return self.env["res.config.settings"].create(values)

    # ------------------------------------------------------------------
    # Valid save/load round-trips
    # ------------------------------------------------------------------

    def test_save_and_load_enabled(self):
        """Toggling enabled writes and reads back correctly via ir.config_parameter."""
        cfg = self._new_settings(ipai_pulser_chat_enabled=True)
        cfg.execute()
        ICP = self.env["ir.config_parameter"].sudo()
        self.assertEqual(ICP.get_param("ipai.pulser_chat.enabled"), "True")

        cfg2 = self._new_settings(ipai_pulser_chat_enabled=False)
        cfg2.execute()
        self.assertEqual(ICP.get_param("ipai.pulser_chat.enabled"), "False")

    def test_save_valid_https_url(self):
        """A well-formed https URL saves without raising."""
        cfg = self._new_settings(
            ipai_pulser_chat_backend_url="https://pulser.example.com/api/chat"
        )
        cfg.execute()  # Must not raise
        ICP = self.env["ir.config_parameter"].sudo()
        saved = ICP.get_param("ipai.pulser_chat.backend_url")
        self.assertEqual(saved, "https://pulser.example.com/api/chat")

    def test_save_valid_http_url(self):
        """http URLs are also accepted (e.g. internal dev endpoints)."""
        cfg = self._new_settings(
            ipai_pulser_chat_backend_url="http://internal-pulser:8080/chat"
        )
        cfg.execute()  # Must not raise

    def test_empty_url_is_allowed(self):
        """Empty URL is valid — feature simply won't be functional."""
        cfg = self._new_settings(ipai_pulser_chat_backend_url="")
        cfg.execute()  # Must not raise

    def test_save_valid_timeout(self):
        """Timeout in [5, 120] range saves correctly."""
        cfg = self._new_settings(ipai_pulser_chat_timeout_seconds=60)
        cfg.execute()  # Must not raise

    # ------------------------------------------------------------------
    # Constraint violations
    # ------------------------------------------------------------------

    def test_reject_relative_url(self):
        """Relative URL path must raise ValidationError."""
        with self.assertRaises(ValidationError):
            self._new_settings(
                ipai_pulser_chat_backend_url="/internal/api/chat"
            )

    def test_reject_ftp_url(self):
        """Non-http/https scheme must raise ValidationError."""
        with self.assertRaises(ValidationError):
            self._new_settings(
                ipai_pulser_chat_backend_url="ftp://pulser.example.com/chat"
            )

    def test_reject_plain_hostname(self):
        """Plain hostname without scheme must raise ValidationError."""
        with self.assertRaises(ValidationError):
            self._new_settings(
                ipai_pulser_chat_backend_url="pulser.example.com/chat"
            )

    def test_reject_timeout_too_low(self):
        """Timeout below 5 must raise ValidationError."""
        with self.assertRaises(ValidationError):
            self._new_settings(ipai_pulser_chat_timeout_seconds=4)

    def test_reject_timeout_too_high(self):
        """Timeout above 120 must raise ValidationError."""
        with self.assertRaises(ValidationError):
            self._new_settings(ipai_pulser_chat_timeout_seconds=121)

    def test_boundary_timeout_min(self):
        """Timeout exactly 5 must be accepted."""
        cfg = self._new_settings(ipai_pulser_chat_timeout_seconds=5)
        cfg.execute()  # Must not raise

    def test_boundary_timeout_max(self):
        """Timeout exactly 120 must be accepted."""
        cfg = self._new_settings(ipai_pulser_chat_timeout_seconds=120)
        cfg.execute()  # Must not raise
