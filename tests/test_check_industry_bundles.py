"""
tests/test_check_industry_bundles.py
--------------------------------------
Unit tests for scripts/ci/check_industry_bundles.py.

Tests cover:
  - validate_schema: valid input, missing keys, bad oca_extensions, duplicate slugs
  - AuditResult: categorized output (ce_core / oca_replacements / extensions)
  - audit_bundle: optional=true → warning, optional=false → required failure
  - main() exit codes via subprocess (schema mode only — no live Odoo needed)
"""
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

# ── Import the module under test ──────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
CHECKER = REPO_ROOT / "scripts" / "ci" / "check_industry_bundles.py"

# Inline import to avoid sys.path gymnastics
import importlib.util

spec = importlib.util.spec_from_file_location("check_industry_bundles", CHECKER)
mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(mod)  # type: ignore[union-attr]

validate_schema = mod.validate_schema
AuditResult = mod.AuditResult
audit_bundle = mod.audit_bundle
SCHEMA_EXPECTED = mod.SCHEMA_EXPECTED


# ── Helpers ───────────────────────────────────────────────────────────────────

def minimal_bundle(**overrides):
    b = {
        "slug": "test-industry",
        "label": "Test Industry",
        "odoo_industry_url": "https://www.odoo.com/industries/test",
        "ce_core": [{"name": "crm", "reason": "Lead pipeline"}],
        "oca_replacements": [
            {"name": "dms", "replaces_ee": "documents", "oca_repo": "OCA/dms", "reason": "DMS"}
        ],
    }
    b.update(overrides)
    return b


def minimal_data(bundles=None):
    return {
        "schema": SCHEMA_EXPECTED,
        "version": "1.0",
        "bundles": bundles or [minimal_bundle()],
    }


# ── validate_schema: valid cases ──────────────────────────────────────────────

class TestValidateSchemaValid:
    def test_minimal_bundle_passes(self):
        assert validate_schema(minimal_data()) == []

    def test_bundle_with_all_optional_fields(self):
        bundle = minimal_bundle(
            ee_modules=["documents"],
            oca_extensions=[
                {"addon": "x", "repo": "OCA/y", "optional": True, "rationale": "nice"}
            ],
            notes=["A note."],
        )
        assert validate_schema(minimal_data([bundle])) == []

    def test_multiple_bundles_pass(self):
        b1 = minimal_bundle(slug="a", label="A")
        b2 = minimal_bundle(slug="b", label="B")
        assert validate_schema(minimal_data([b1, b2])) == []

    def test_real_ssot_file_parses_clean(self):
        """The actual SSOT file should always be schema-clean."""
        import yaml

        ssot = REPO_ROOT / "ssot" / "odoo" / "industry_bundles.yaml"
        if not ssot.exists():
            pytest.skip("SSOT file not present")
        data = yaml.safe_load(ssot.read_text()) or {}
        errors = validate_schema(data)
        assert errors == [], f"SSOT schema errors: {errors}"


# ── validate_schema: error cases ─────────────────────────────────────────────

class TestValidateSchemaErrors:
    def test_wrong_schema_key(self):
        data = minimal_data()
        data["schema"] = "ssot.wrong.v9"
        errors = validate_schema(data)
        assert any("schema:" in e for e in errors)

    def test_empty_bundles(self):
        errors = validate_schema({"schema": SCHEMA_EXPECTED, "bundles": []})
        assert any("bundles:" in e for e in errors)

    def test_missing_bundle_keys(self):
        bundle = {"slug": "x"}  # missing label, odoo_industry_url, ce_core, oca_replacements
        errors = validate_schema(minimal_data([bundle]))
        assert any("missing required keys" in e for e in errors)

    def test_duplicate_slug(self):
        b1 = minimal_bundle(slug="same")
        b2 = minimal_bundle(slug="same")
        errors = validate_schema(minimal_data([b1, b2]))
        assert any("duplicate slug" in e for e in errors)

    def test_empty_ce_core(self):
        bundle = minimal_bundle(ce_core=[])
        errors = validate_schema(minimal_data([bundle]))
        assert any("ce_core must be a non-empty list" in e for e in errors)

    def test_ce_core_missing_reason(self):
        bundle = minimal_bundle(ce_core=[{"name": "crm"}])  # missing reason
        errors = validate_schema(minimal_data([bundle]))
        assert any("ce_core" in e and "missing keys" in e for e in errors)

    def test_oca_replacement_missing_replaces_ee(self):
        bundle = minimal_bundle(
            oca_replacements=[{"name": "dms", "oca_repo": "OCA/dms", "reason": "r"}]
        )  # missing replaces_ee
        errors = validate_schema(minimal_data([bundle]))
        assert any("oca_replacements" in e and "missing keys" in e for e in errors)

    def test_oca_extension_missing_addon_field(self):
        """oca_extensions entry must have addon, repo, optional, rationale."""
        bundle = minimal_bundle(
            oca_extensions=[{"name": "x", "repo": "OCA/y"}]  # wrong keys
        )
        errors = validate_schema(minimal_data([bundle]))
        assert any("oca_extensions" in e and "missing keys" in e for e in errors)

    def test_oca_extension_optional_not_bool(self):
        bundle = minimal_bundle(
            oca_extensions=[
                {"addon": "x", "repo": "OCA/y", "optional": "yes", "rationale": "r"}
            ]
        )
        errors = validate_schema(minimal_data([bundle]))
        assert any("'optional' must be a bool" in e for e in errors)

    def test_ee_modules_not_list(self):
        bundle = minimal_bundle(ee_modules="documents")  # should be a list
        errors = validate_schema(minimal_data([bundle]))
        assert any("ee_modules must be a list" in e for e in errors)


# ── audit_bundle: categorized output ─────────────────────────────────────────

class TestAuditBundle:
    def _bundle(self, **overrides):
        b = {
            "slug": "test",
            "ce_core": [{"name": "crm", "reason": "r"}, {"name": "account", "reason": "r"}],
            "oca_replacements": [
                {"name": "dms", "replaces_ee": "documents", "oca_repo": "OCA/dms", "reason": "r"}
            ],
            "oca_extensions": [
                {"addon": "sale_product_set", "repo": "OCA/sale-workflow", "optional": False, "rationale": "r"},
                {"addon": "project_milestone", "repo": "OCA/project", "optional": True, "rationale": "r"},
            ],
        }
        b.update(overrides)
        return b

    def test_all_installed_no_failures(self):
        installed = {"crm", "account", "dms", "sale_product_set", "project_milestone"}
        result = audit_bundle(self._bundle(), installed)
        assert result.missing_ce_core == []
        assert result.missing_oca_replacements == []
        assert result.missing_required_extensions == []
        assert result.missing_optional_extensions == []
        assert not result.has_failures
        assert not result.has_strict_failures

    def test_missing_ce_core_module(self):
        installed = {"account", "dms", "sale_product_set", "project_milestone"}
        result = audit_bundle(self._bundle(), installed)
        assert "crm" in result.missing_ce_core
        assert result.has_failures

    def test_missing_oca_replacement(self):
        installed = {"crm", "account", "sale_product_set", "project_milestone"}
        result = audit_bundle(self._bundle(), installed)
        assert "dms" in result.missing_oca_replacements
        assert result.has_failures

    def test_optional_false_goes_to_required_extensions(self):
        installed = {"crm", "account", "dms", "project_milestone"}  # sale_product_set absent
        result = audit_bundle(self._bundle(), installed)
        assert "sale_product_set" in result.missing_required_extensions
        assert result.has_strict_failures
        assert not result.has_failures  # required fails only under strict-oca

    def test_optional_true_goes_to_optional_extensions(self):
        installed = {"crm", "account", "dms", "sale_product_set"}  # project_milestone absent
        result = audit_bundle(self._bundle(), installed)
        assert "project_milestone" in result.missing_optional_extensions
        assert result.has_warnings
        assert not result.has_failures
        assert not result.has_strict_failures

    def test_no_extensions_in_bundle(self):
        bundle = self._bundle(oca_extensions=[])
        installed = {"crm", "account", "dms"}
        result = audit_bundle(bundle, installed)
        assert not result.has_failures
        assert not result.has_strict_failures
        assert not result.has_warnings


# ── main() exit codes via subprocess (schema mode only) ──────────────────────

class TestMainExitCodes:
    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(CHECKER), *args],
            capture_output=True, text=True
        )

    def test_schema_mode_exits_0_on_valid_ssot(self):
        r = self._run()
        assert r.returncode == 0, r.stderr
        assert "OK: schema valid" in r.stdout

    def test_schema_mode_reports_bundle_slugs(self):
        r = self._run()
        assert "photography" in r.stdout
        assert "marketing-agency" in r.stdout
        assert "odoo-partner" in r.stdout

    def test_audit_mode_requires_bundle_flag(self):
        import os
        env = {**os.environ, "ODOO_URL": "http://localhost:8069", "ODOO_DB": "x",
               "ODOO_ADMIN_LOGIN": "admin", "ODOO_ADMIN_PASSWORD": "pw"}
        r = subprocess.run(
            [sys.executable, str(CHECKER), "--mode", "audit"],
            capture_output=True, text=True, env=env
        )
        # Should fail with clear error about missing --bundle
        assert r.returncode != 0
        assert "--bundle" in r.stderr or "--bundle" in r.stdout
