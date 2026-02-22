# Copyright 2026 InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestIpaiWebMailCompatSmoke(TransactionCase):
    """Smoke tests that block the two original OCA mail_tracking regressions.

    These tests run post-install so the asset records are already committed.
    They do not test JS runtime (not possible in Python), but they verify the
    *preconditions* that make the JS fixes effective:

      1. The upstream broken files are registered as REMOVED in ir.asset.
      2. The compat replacement files are registered as APPEND in ir.asset.
      3. The probe contract is internally consistent.

    If Odoo renames templates again or upstream paths change, test 2 catches it.
    """

    BUNDLE = "web.assets_backend"

    def _asset_paths(self):
        """Return a dict {path: directive} for all active assets in our bundle."""
        records = self.env["ir.asset"].sudo().search(
            [("bundle", "=", self.BUNDLE), ("active", "=", True)]
        )
        return {r.path: r.directive for r in records}

    def test_upstream_broken_files_are_removed(self):
        """ir.asset must have 'remove' directives for both OCA broken files."""
        assets = self._asset_paths()
        probe = self.env["ipai.compat.probe"].sudo().mail_tracking()
        for upstream_path in probe["removed_upstream_assets"]:
            self.assertEqual(
                assets.get(upstream_path),
                "remove",
                f"Expected ir.asset directive 'remove' for upstream path '{upstream_path}' "
                f"in bundle '{self.BUNDLE}'.  If missing, the ('remove', ...) stanza in "
                f"__manifest__.py did not register — reinstall the module.",
            )

    def test_compat_replacement_files_are_appended(self):
        """ir.asset must have 'append' directives for all compat replacement files."""
        assets = self._asset_paths()
        probe = self.env["ipai.compat.probe"].sudo().mail_tracking()
        for compat_path in probe["added_compat_assets"]:
            self.assertIn(
                assets.get(compat_path),
                ("append", None),  # None = default append
                f"Expected compat asset '{compat_path}' to be present as 'append' "
                f"in bundle '{self.BUNDLE}'.  Check __manifest__.py assets stanza.",
            )

    def test_probe_contract_shape(self):
        """Probe must return active=True and the expected required keys."""
        probe = self.env["ipai.compat.probe"].sudo().mail_tracking()
        self.assertTrue(
            probe.get("active"),
            "ipai.compat.probe.mail_tracking() must return active=True when installed.",
        )
        for required_key in ("module", "version", "fixes", "removed_upstream_assets", "added_compat_assets"):
            self.assertIn(required_key, probe, f"Probe missing required key '{required_key}'")

        self.assertEqual(probe["module"], "ipai_web_mail_compat")
        self.assertEqual(probe["bundle"], "web.assets_backend")
        self.assertEqual(len(probe["removed_upstream_assets"]), 2)
        self.assertEqual(len(probe["added_compat_assets"]), 3)

    def test_probe_removed_and_added_are_disjoint(self):
        """Removed and added asset paths must not overlap (would indicate manifest error)."""
        probe = self.env["ipai.compat.probe"].sudo().mail_tracking()
        removed = set(probe["removed_upstream_assets"])
        added = set(probe["added_compat_assets"])
        overlap = removed & added
        self.assertFalse(
            overlap,
            f"Probe removed_upstream_assets and added_compat_assets overlap: {overlap}",
        )
