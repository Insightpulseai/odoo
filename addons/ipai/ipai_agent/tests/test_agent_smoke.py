# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAgentSmoke(TransactionCase):
    """Install smoke tests for ipai_agent module."""

    def test_module_installed(self):
        """ipai_agent must be in installed state."""
        module = self.env["ir.module.module"].search(
            [("name", "=", "ipai_agent")], limit=1,
        )
        self.assertTrue(module, "ipai_agent module record not found")
        self.assertEqual(
            module.state,
            "installed",
            "ipai_agent should be installed",
        )

    def test_no_broken_views(self):
        """No ir.ui.view records should reference missing fields from this module."""
        broken = self.env["ir.ui.view"].search([
            ("model", "like", "ipai.agent%"),
        ])
        for view in broken:
            # Attempt to read the arch — this triggers field validation
            try:
                view.arch
            except Exception as e:
                self.fail(
                    "View %s (id=%s) has broken arch: %s"
                    % (view.name, view.id, e)
                )
