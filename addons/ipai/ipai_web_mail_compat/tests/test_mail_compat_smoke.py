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
      5. Path canonicalization is stable for both leading-slash and slashless inputs.
    """

    BUNDLE = "web.assets_backend"

    # ── path canonicalization ─────────────────────────────────────────────────

    @staticmethod
    def _canon_asset_path(p: str) -> str:
        """Normalise an asset path to manifest-style (no leading slash).

        IrAsset._get_asset_paths() resolves paths from the filesystem as
        ``absolute_path[len(addons_path):]`` which yields a leading ``/``
        because addons_path has no trailing slash.  Manifest contract paths are
        written without a leading slash.  Applying this helper to both sides
        keeps comparisons format-agnostic and robust against future drift in
        the probe contract lists.
        """
        return (p or "").lstrip("/")

    # ── resolved path set ─────────────────────────────────────────────────────

    def _asset_path_set(self):
        """Return a frozenset of canonicalised paths for BUNDLE.

        Uses IrAsset._get_asset_paths() — the authoritative Odoo API for
        the final bundle contents after all directives are applied.
        """
        IrAsset = self.env["ir.asset"].sudo()
        resolved = IrAsset._get_asset_paths(self.BUNDLE, {})
        # Each entry is a 4-tuple (path, full_path, bundle, last_modified).
        # Canonicalise entry[0] so both leading-slash and slashless paths match.
        return frozenset(self._canon_asset_path(entry[0]) for entry in resolved)

    # ── regression: canonicalization helper ───────────────────────────────────

    def test_canon_asset_path_is_stable(self):
        """Canonicalization must produce identical output for both input forms."""
        cases = [
            # (input, expected_output)
            ("/mail_tracking/static/src/services/store_service_patch.esm.js",
             "mail_tracking/static/src/services/store_service_patch.esm.js"),
            ("mail_tracking/static/src/services/store_service_patch.esm.js",
             "mail_tracking/static/src/services/store_service_patch.esm.js"),
            ("/ipai_web_mail_compat/static/src/compat_probe.esm.js",
             "ipai_web_mail_compat/static/src/compat_probe.esm.js"),
            ("ipai_web_mail_compat/static/src/compat_probe.esm.js",
             "ipai_web_mail_compat/static/src/compat_probe.esm.js"),
            ("", ""),
        ]
        for inp, expected in cases:
            with self.subTest(inp=inp):
                self.assertEqual(self._canon_asset_path(inp), expected)

    # ── asset contract assertions ─────────────────────────────────────────────

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
                self._canon_asset_path(upstream_path),
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
                self._canon_asset_path(compat_path),
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
        removed = {self._canon_asset_path(p) for p in probe["removed_upstream_assets"]}
        added = {self._canon_asset_path(p) for p in probe["added_compat_assets"]}
        overlap = removed & added
        self.assertFalse(
            overlap,
            f"Probe removed_upstream_assets and added_compat_assets overlap: {overlap}",
        )
