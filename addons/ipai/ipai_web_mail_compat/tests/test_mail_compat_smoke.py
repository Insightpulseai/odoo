# Copyright 2026 InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestIpaiWebMailCompatSmoke(TransactionCase):
    """Smoke tests that block the two original OCA mail_tracking regressions.

    These tests run post-install so all module manifests have been processed.
    They verify the *preconditions* that make the JS fixes effective by
    inspecting the FULLY RESOLVED asset bundle via IrAsset._get_asset_paths().

    _get_asset_paths() processes manifest-declared assets (including the
    '("remove", ...)' stanzas) AND dynamic ir.asset records, returning the
    final list after all directives are applied.

    Tuple structure: (path, full_path, bundle, last_modified) — 4 elements.

    Contract:
      1. Upstream broken files are NOT in the resolved bundle (removed).
      2. Compat replacement files ARE in the resolved bundle (added).
      3. The probe model returns a consistent and well-formed contract dict.
      4. Removed and added sets are disjoint.
    """

    BUNDLE = "web.assets_backend"

    def _asset_path_set(self):
        """Return a frozenset of resolved paths for BUNDLE.

        Uses IrAsset._get_asset_paths() — the authoritative Odoo API for
        final bundle contents.  Manifest-declared removes are already applied,
        so removed paths are absent and added paths are present.
        """
        IrAsset = self.env["ir.asset"].sudo()
        resolved = IrAsset._get_asset_paths(self.BUNDLE, {})
        # Each entry is a 4-tuple (path, full_path, bundle, last_modified).
        # Index 0 is the addon-relative path used in manifests / ir.asset.
        # _get_asset_paths() returns paths with a leading slash when resolved
        # from the filesystem (e.g. '/mail_tracking/static/...' not
        # 'mail_tracking/static/...').  Strip so comparisons against the probe
        # contract (which uses slashless paths matching __manifest__.py) work.
        return frozenset(entry[0].lstrip('/') for entry in resolved)

    def test_upstream_broken_files_are_removed(self):
        """Upstream broken OCA files must NOT be in the resolved bundle.

        The ('remove', ...) stanzas in __manifest__.py cause _get_asset_paths()
        to exclude these paths from the final list.  If this test fails, the
        removal stanza is broken or the module needs to be reinstalled.
        """
        path_set = self._asset_path_set()
        probe = self.env["ipai.compat.probe"].sudo().mail_tracking()
        for upstream_path in probe["removed_upstream_assets"]:
            self.assertNotIn(
                upstream_path,
                path_set,
                f"Upstream path '{upstream_path}' is STILL in bundle '{self.BUNDLE}'. "
                f"The ('remove', ...) stanza in __manifest__.py did not take effect — "
                f"reinstall the module or check manifest syntax.",
            )

    def test_compat_replacement_files_are_present(self):
        """Compat replacement files must be in the resolved bundle.

        Regular path entries in __manifest__.py assets cause _get_asset_paths()
        to include them.  If this test fails, a static file is missing or the
        manifest path is wrong.
        """
        path_set = self._asset_path_set()
        probe = self.env["ipai.compat.probe"].sudo().mail_tracking()
        for compat_path in probe["added_compat_assets"]:
            self.assertIn(
                compat_path,
                path_set,
                f"Compat asset '{compat_path}' NOT found in bundle '{self.BUNDLE}'. "
                f"Check __manifest__.py assets stanza and that the static file exists.",
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
