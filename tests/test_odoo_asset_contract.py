#!/usr/bin/env python3
"""Odoo Asset Bundle Contract Test

Validates that all ipai_* module manifests have correct asset declarations:
- every referenced JS/CSS/XML/SCSS path actually exists on disk
- no duplicate asset entries across controlled bundles
- no asset path points outside the allowed addon roots
- bundle keys are valid Odoo bundle names
- assets dict structure is well-formed

Run:
    python3 tests/test_odoo_asset_contract.py
    # or via pytest:
    pytest tests/test_odoo_asset_contract.py -v
"""

import ast
import os
import sys
import unittest
from pathlib import Path

# Repo root = parent of tests/
REPO_ROOT = Path(__file__).resolve().parent.parent
ADDONS_IPAI = REPO_ROOT / "addons" / "ipai"

# Valid Odoo asset bundle keys (Odoo 19)
VALID_BUNDLE_KEYS = {
    "web.assets_backend",
    "web.assets_frontend",
    "web.assets_common",
    "web.assets_backend_lazy",
    "web.assets_backend_lazy_dark",
    "web.assets_web",
    "web.assets_web_dark",
    "web.assets_web_editor",
    "web.assets_tests",
    "web.assets_unit_tests",
    "web.qunit_suite_tests",
    "web.qunit_mobile_suite_tests",
    "web.report_assets_common",
    "web.report_assets_pdf",
    "website.assets_frontend",
    "website.assets_editor",
    "website.assets_wysiwyg",
    "point_of_sale.assets",
    "point_of_sale.assets_prod",
}

# Allowed file extensions for assets
VALID_ASSET_EXTENSIONS = {".js", ".css", ".scss", ".xml", ".less"}

# Allowed addon roots (relative to repo root)
ALLOWED_ROOTS = {"addons/ipai"}


def parse_manifest(manifest_path: Path) -> dict:
    """Parse __manifest__.py and return the dict."""
    with open(manifest_path) as f:
        content = f.read()
    try:
        return ast.literal_eval(content.lstrip("# -*- coding: utf-8 -*-\n"))
    except (ValueError, SyntaxError):
        return {}


def find_all_manifests() -> list[tuple[str, Path, dict]]:
    """Find all ipai module manifests and parse them."""
    results = []
    if not ADDONS_IPAI.is_dir():
        return results
    for module_dir in sorted(ADDONS_IPAI.iterdir()):
        manifest = module_dir / "__manifest__.py"
        if manifest.is_file():
            data = parse_manifest(manifest)
            if data:
                results.append((module_dir.name, manifest, data))
    return results


class TestAssetContract(unittest.TestCase):
    """Validate asset declarations in all ipai modules."""

    @classmethod
    def setUpClass(cls):
        cls.manifests = find_all_manifests()

    def test_manifests_found(self):
        """At least one module manifest should be found."""
        self.assertGreater(len(self.manifests), 0, "No ipai module manifests found")

    def test_asset_paths_exist(self):
        """Every asset path referenced in installable modules must exist on disk."""
        missing = []
        for module_name, manifest_path, data in self.manifests:
            if not data.get("installable", True):
                continue  # Skip deprecated/non-installable modules
            assets = data.get("assets", {})
            if not isinstance(assets, dict):
                continue
            for bundle_key, paths in assets.items():
                if not isinstance(paths, list):
                    continue
                for asset_path in paths:
                    if not isinstance(asset_path, str):
                        continue
                    # asset_path format: "module_name/static/src/..."
                    # Resolve relative to the module's parent directory
                    full_path = ADDONS_IPAI / asset_path
                    if not full_path.is_file():
                        missing.append(f"{module_name}: {asset_path}")
        if missing:
            self.fail(
                f"Missing asset files ({len(missing)}):\n"
                + "\n".join(f"  - {m}" for m in missing)
            )

    def test_bundle_keys_valid(self):
        """Bundle keys should be recognized Odoo bundles or module-scoped bundles."""
        invalid = []
        for module_name, _, data in self.manifests:
            assets = data.get("assets", {})
            if not isinstance(assets, dict):
                continue
            for bundle_key in assets:
                # Module-scoped bundles (e.g. "my_module.assets_backend") are valid
                if bundle_key in VALID_BUNDLE_KEYS:
                    continue
                # Accept module-scoped bundles (module.bundle_name pattern)
                parts = bundle_key.split(".")
                if len(parts) == 2 and parts[0] and parts[1]:
                    continue
                invalid.append(f"{module_name}: {bundle_key}")
        if invalid:
            self.fail(
                f"Invalid bundle keys:\n"
                + "\n".join(f"  - {i}" for i in invalid)
            )

    def test_no_duplicate_assets(self):
        """No duplicate asset entries within the same bundle across ipai modules."""
        bundle_entries: dict[str, list[str]] = {}
        for module_name, _, data in self.manifests:
            assets = data.get("assets", {})
            if not isinstance(assets, dict):
                continue
            for bundle_key, paths in assets.items():
                if not isinstance(paths, list):
                    continue
                for asset_path in paths:
                    if not isinstance(asset_path, str):
                        continue
                    key = f"{bundle_key}:{asset_path}"
                    bundle_entries.setdefault(key, []).append(module_name)

        dupes = {k: v for k, v in bundle_entries.items() if len(v) > 1}
        if dupes:
            lines = [f"  - {k}: declared by {', '.join(v)}" for k, v in dupes.items()]
            self.fail(
                f"Duplicate asset entries:\n" + "\n".join(lines)
            )

    def test_asset_paths_within_allowed_roots(self):
        """Asset paths must reference files within the module's own static/ directory."""
        violations = []
        for module_name, _, data in self.manifests:
            assets = data.get("assets", {})
            if not isinstance(assets, dict):
                continue
            for bundle_key, paths in assets.items():
                if not isinstance(paths, list):
                    continue
                for asset_path in paths:
                    if not isinstance(asset_path, str):
                        continue
                    # Must start with the module name
                    if not asset_path.startswith(f"{module_name}/"):
                        violations.append(
                            f"{module_name}: {asset_path} (doesn't start with {module_name}/)"
                        )
                    # Must contain /static/
                    elif "/static/" not in asset_path:
                        violations.append(
                            f"{module_name}: {asset_path} (not under static/)"
                        )
        if violations:
            self.fail(
                f"Asset path violations:\n"
                + "\n".join(f"  - {v}" for v in violations)
            )

    def test_asset_file_extensions(self):
        """Asset files should have recognized frontend extensions."""
        bad_ext = []
        for module_name, _, data in self.manifests:
            assets = data.get("assets", {})
            if not isinstance(assets, dict):
                continue
            for bundle_key, paths in assets.items():
                if not isinstance(paths, list):
                    continue
                for asset_path in paths:
                    if not isinstance(asset_path, str):
                        continue
                    ext = Path(asset_path).suffix.lower()
                    if ext not in VALID_ASSET_EXTENSIONS:
                        bad_ext.append(f"{module_name}: {asset_path} (ext={ext})")
        if bad_ext:
            self.fail(
                f"Unexpected asset extensions:\n"
                + "\n".join(f"  - {b}" for b in bad_ext)
            )

    def test_assets_dict_structure(self):
        """assets in manifest must be a dict of string -> list[string]."""
        malformed = []
        for module_name, _, data in self.manifests:
            assets = data.get("assets")
            if assets is None:
                continue
            if not isinstance(assets, dict):
                malformed.append(f"{module_name}: assets is {type(assets).__name__}, expected dict")
                continue
            for key, val in assets.items():
                if not isinstance(key, str):
                    malformed.append(f"{module_name}: bundle key {key!r} is not a string")
                if not isinstance(val, list):
                    malformed.append(f"{module_name}: bundle {key} value is {type(val).__name__}, expected list")
                elif not all(isinstance(v, str) for v in val):
                    malformed.append(f"{module_name}: bundle {key} contains non-string entries")
        if malformed:
            self.fail(
                f"Malformed assets declarations:\n"
                + "\n".join(f"  - {m}" for m in malformed)
            )

    def test_installable_modules_have_no_missing_data_files(self):
        """Installable modules' data file paths must exist on disk."""
        missing = []
        for module_name, manifest_path, data in self.manifests:
            if not data.get("installable", True):
                continue
            module_dir = manifest_path.parent
            for data_file in data.get("data", []):
                full_path = module_dir / data_file
                if not full_path.is_file():
                    missing.append(f"{module_name}: data/{data_file}")
        if missing:
            self.fail(
                f"Missing data files in installable modules:\n"
                + "\n".join(f"  - {m}" for m in missing)
            )


if __name__ == "__main__":
    unittest.main()
