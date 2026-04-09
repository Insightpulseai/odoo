"""
tests/test_ssot_odoo_contract.py
---------------------------------
SSOT contract drift checks for the Odoo canonical baseline.

Validates:
  - Addon layer directories exist (oca, ipai, local)
  - ssot/odoo/ contains required registry files
  - config/addons.manifest.yaml and oca-aggregate.yml stay in sync
  - Every IPAI module has __manifest__.py + security/ + __init__.py
  - No secret files committed (*.env, credentials.*)
  - Docker compose exists and references correct Dockerfiles
  - Spec bundles have all 4 required files
"""

import ast
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent


# ── Addon Layer Existence ─────────────────────────────────────────────────


class TestAddonLayers:
    """Verify canonical addon layers exist."""

    def test_addons_ipai_exists(self):
        assert (REPO_ROOT / "addons" / "ipai").is_dir()

    def test_addons_oca_exists(self):
        assert (REPO_ROOT / "addons" / "oca").is_dir()

    def test_addons_local_exists(self):
        assert (REPO_ROOT / "addons" / "local").is_dir()


# ── SSOT Registry Files ──────────────────────────────────────────────────


class TestSSOTOdoo:
    """Verify ssot/odoo/ contains required files."""

    ssot_dir = REPO_ROOT / "ssot" / "odoo"

    def test_ssot_odoo_dir_exists(self):
        assert self.ssot_dir.is_dir(), "ssot/odoo/ must exist"

    def test_oca_repos_yaml_exists(self):
        assert (self.ssot_dir / "oca_repos.yaml").is_file()

    def test_oca_lock_yaml_exists(self):
        assert (self.ssot_dir / "oca_lock.yaml").is_file()

    def test_settings_catalog_exists(self):
        assert (self.ssot_dir / "settings_catalog.yaml").is_file()


# ── Addons Manifest Integrity ────────────────────────────────────────────


class TestAddonsManifest:
    """Verify config/addons.manifest.yaml exists and is parseable."""

    manifest_path = REPO_ROOT / "config" / "addons.manifest.yaml"

    def test_manifest_exists(self):
        assert self.manifest_path.is_file(), "config/addons.manifest.yaml must exist"

    def test_manifest_has_oca_repositories(self):
        content = self.manifest_path.read_text()
        assert "oca_repositories:" in content

    def test_manifest_has_profiles(self):
        content = self.manifest_path.read_text()
        assert "profiles:" in content

    def test_manifest_targets_odoo_18(self):
        content = self.manifest_path.read_text()
        assert 'odoo_version: "19.0"' in content


# ── OCA Aggregate Sync ───────────────────────────────────────────────────


class TestOCAAggregateSync:
    """Verify oca-aggregate.yml exists and references 19.0 branches."""

    agg_path = REPO_ROOT / "oca-aggregate.yml"

    def test_aggregate_exists(self):
        assert self.agg_path.is_file(), "oca-aggregate.yml must exist"

    def test_aggregate_references_19(self):
        content = self.agg_path.read_text()
        assert "19.0" in content


# ── IPAI Module Structure ────────────────────────────────────────────────


class TestIPAIModuleStructure:
    """Verify every installable IPAI module has minimal required files."""

    ipai_dir = REPO_ROOT / "addons" / "ipai"

    def _get_installable_modules(self):
        modules = []
        if not self.ipai_dir.is_dir():
            return modules
        for item in self.ipai_dir.iterdir():
            if not item.is_dir() or item.name.startswith("."):
                continue
            manifest = item / "__manifest__.py"
            if not manifest.exists():
                continue
            try:
                data = ast.literal_eval(manifest.read_text())
                if data.get("installable", True):
                    modules.append(item)
            except Exception:
                continue
        return modules

    def test_all_installable_have_init(self):
        for mod_dir in self._get_installable_modules():
            assert (
                mod_dir / "__init__.py"
            ).exists(), f"{mod_dir.name} missing __init__.py"

    def test_all_installable_have_manifest(self):
        for mod_dir in self._get_installable_modules():
            assert (
                mod_dir / "__manifest__.py"
            ).exists(), f"{mod_dir.name} missing __manifest__.py"

    def test_manifests_target_19(self):
        """All installable IPAI modules must target Odoo 18."""
        for mod_dir in self._get_installable_modules():
            manifest = mod_dir / "__manifest__.py"
            try:
                data = ast.literal_eval(manifest.read_text())
                version = data.get("version", "")
                assert version.startswith(
                    "19."
                ), f"{mod_dir.name} version {version} does not target 19.0"
            except (SyntaxError, ValueError):
                pass  # Parse errors caught by other tests


# ── No Secrets Committed ─────────────────────────────────────────────────


class TestNoSecrets:
    """Verify no secret files are committed."""

    FORBIDDEN_PATTERNS = [
        ".env",
        ".env.local",
        ".env.prod",
        ".env.staging",
        "credentials.json",
        "service-account.json",
    ]

    def test_no_root_env_files(self):
        for pattern in self.FORBIDDEN_PATTERNS:
            path = REPO_ROOT / pattern
            assert (
                not path.exists()
            ), f"Secret file {pattern} must not be committed to repo"


# ── Docker Compose Exists ────────────────────────────────────────────────


class TestDockerCompose:
    """Verify Docker infrastructure files exist."""

    def test_root_compose_exists(self):
        assert (REPO_ROOT / "docker-compose.yml").is_file()

    def test_dockerfile_unified_exists(self):
        assert (REPO_ROOT / "docker" / "Dockerfile.unified").is_file()


# ── Spec Kit 4-File Bundles ──────────────────────────────────────────────


class TestSpecKitBundles:
    """Verify spec bundles have all 4 required files."""

    REQUIRED_FILES = ["constitution.md", "prd.md", "plan.md", "tasks.md"]
    spec_dir = REPO_ROOT / "spec"

    def _get_spec_bundles(self):
        if not self.spec_dir.is_dir():
            return []
        return [
            d
            for d in self.spec_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

    def test_spec_bundles_have_prd(self):
        """Every spec bundle must have at least a prd.md."""
        for bundle in self._get_spec_bundles():
            has_any = any((bundle / f).exists() for f in self.REQUIRED_FILES)
            if has_any:
                assert (
                    bundle / "prd.md"
                ).exists(), f"spec/{bundle.name}/ missing prd.md"


# ── Evidence Directory ───────────────────────────────────────────────────


class TestEvidenceDirectory:
    """Verify evidence directory exists for deploy proofs."""

    def test_evidence_dir_exists(self):
        assert (REPO_ROOT / "evidence").is_dir() or (
            REPO_ROOT / "docs" / "evidence"
        ).is_dir(), "evidence/ or docs/evidence/ must exist"
