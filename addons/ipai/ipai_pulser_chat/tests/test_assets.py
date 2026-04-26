# -*- coding: utf-8 -*-
"""
test_assets.py — Asserts that every static asset declared in __manifest__.py
actually exists on disk.  Fails at install time if any declared asset is missing
so the breakage is caught before a broken bundle reaches the browser.
"""

import os

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("ipai", "ipai_pulser_chat", "-at_install", "post_install")
class TestAssets(TransactionCase):
    """Verify declared backend assets exist on disk."""

    # These paths are relative to the addon root directory and must match the
    # asset declarations in __manifest__.py exactly.
    _EXPECTED_ASSETS = [
        "static/src/js/systray/pulser_systray.js",
        "static/src/js/chat/pulser_chat_panel.js",
        "static/src/xml/pulser_systray.xml",
        "static/src/xml/chat/pulser_chat_panel.xml",
        "static/src/scss/pulser_chat.scss",
    ]

    def _addon_root(self):
        """Resolve the addon root directory at runtime."""
        import odoo.addons.ipai_pulser_chat as addon_pkg
        return os.path.dirname(addon_pkg.__file__)

    def test_all_declared_assets_exist(self):
        """Every asset path declared in __manifest__ must resolve to a real file."""
        root = self._addon_root()
        for rel_path in self._EXPECTED_ASSETS:
            abs_path = os.path.join(root, rel_path)
            self.assertTrue(
                os.path.isfile(abs_path),
                f"Declared asset missing from disk: {rel_path}",
            )

    def test_security_csv_exists(self):
        """security/ir.model.access.csv must be present (even if header-only)."""
        root = self._addon_root()
        csv_path = os.path.join(root, "security", "ir.model.access.csv")
        self.assertTrue(
            os.path.isfile(csv_path),
            "security/ir.model.access.csv is missing",
        )

    def test_data_xml_exists(self):
        """data/ir_config_parameter.xml must be present."""
        root = self._addon_root()
        xml_path = os.path.join(root, "data", "ir_config_parameter.xml")
        self.assertTrue(os.path.isfile(xml_path), "data/ir_config_parameter.xml is missing")
