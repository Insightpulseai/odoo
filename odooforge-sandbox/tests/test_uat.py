#!/usr/bin/env python3
"""
OdooForge Sandbox - UAT Test Suite

Automated tests for validating the OdooForge Sandbox environment.
Run with: pytest test_uat.py -v
"""

import os
import json
import shutil
import subprocess
import time
from pathlib import Path

import pytest

# Test configuration
ADDONS_DIR = Path("/workspace/addons")
REPORTS_DIR = Path("/workspace/reports")
KIT_CLI = "kit"
TEST_MODULE = "ipai_uat_test"


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture(scope="session")
def ensure_directories():
    """Ensure test directories exist."""
    ADDONS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    yield


@pytest.fixture
def clean_test_module():
    """Remove test module before and after test."""
    module_path = ADDONS_DIR / TEST_MODULE
    if module_path.exists():
        shutil.rmtree(module_path)
    yield module_path
    if module_path.exists():
        shutil.rmtree(module_path)


@pytest.fixture
def created_module(clean_test_module):
    """Create a test module and return its path."""
    result = subprocess.run(
        [KIT_CLI, "init", TEST_MODULE],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Failed to create module: {result.stderr}"
    yield clean_test_module


# ==============================================================================
# Installation Tests (Category: installation)
# ==============================================================================

class TestInstallation:
    """Installation and environment tests."""

    def test_kit_cli_available(self):
        """I-01: Kit CLI is available."""
        result = subprocess.run([KIT_CLI, "--help"], capture_output=True, text=True)
        assert result.returncode == 0, "Kit CLI not available"

    def test_python_version(self):
        """Verify Python version is 3.11+."""
        import sys
        assert sys.version_info >= (3, 11), f"Python 3.11+ required, got {sys.version}"

    def test_addons_directory_exists(self, ensure_directories):
        """I-05: Addons directory exists."""
        assert ADDONS_DIR.exists(), "Addons directory not found"

    def test_reports_directory_exists(self, ensure_directories):
        """Reports directory exists."""
        assert REPORTS_DIR.exists(), "Reports directory not found"

    def test_required_packages(self):
        """Required Python packages are installed."""
        required = ["click", "yaml", "requests", "pytest"]
        for pkg in required:
            try:
                __import__(pkg)
            except ImportError:
                pytest.fail(f"Required package not installed: {pkg}")


# ==============================================================================
# CLI Version Tests
# ==============================================================================

class TestCLIVersion:
    """CLI version and help tests."""

    def test_version_command(self):
        """K-01: Version command works."""
        result = subprocess.run([KIT_CLI, "version"], capture_output=True, text=True)
        assert result.returncode == 0
        assert "OdooForge Kit CLI" in result.stdout

    def test_help_command(self):
        """Help command shows usage."""
        result = subprocess.run([KIT_CLI, "--help"], capture_output=True, text=True)
        assert result.returncode == 0
        assert "init" in result.stdout
        assert "validate" in result.stdout


# ==============================================================================
# CLI Init Tests (Category: init)
# ==============================================================================

class TestCLIInit:
    """Module initialization tests."""

    def test_init_creates_module(self, clean_test_module):
        """K-02: kit init creates module directory."""
        result = subprocess.run(
            [KIT_CLI, "init", TEST_MODULE],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, result.stderr
        assert clean_test_module.exists(), "Module directory not created"

    def test_init_invalid_name_rejected(self, ensure_directories):
        """K-03: Invalid module name is rejected."""
        result = subprocess.run(
            [KIT_CLI, "init", "invalid_name"],  # Missing ipai_ prefix
            capture_output=True,
            text=True
        )
        assert result.returncode != 0, "Invalid name should be rejected"

    def test_init_duplicate_rejected(self, created_module):
        """K-04: Duplicate module creation is rejected."""
        result = subprocess.run(
            [KIT_CLI, "init", TEST_MODULE],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0, "Duplicate should be rejected"
        assert "already exists" in result.stderr.lower() or "already exists" in result.stdout.lower()

    def test_init_creates_manifest(self, created_module):
        """K-05: __manifest__.py is created."""
        manifest = created_module / "__manifest__.py"
        assert manifest.exists(), "__manifest__.py not created"

    def test_init_creates_init(self, created_module):
        """K-06: __init__.py is created."""
        init_file = created_module / "__init__.py"
        assert init_file.exists(), "__init__.py not created"

    def test_init_creates_models(self, created_module):
        """K-07: models/ directory is created."""
        models = created_module / "models"
        assert models.exists() and models.is_dir(), "models/ not created"

    def test_init_creates_views(self, created_module):
        """K-08: views/ directory is created."""
        views = created_module / "views"
        assert views.exists() and views.is_dir(), "views/ not created"

    def test_init_creates_security(self, created_module):
        """K-09: security/ directory is created."""
        security = created_module / "security"
        assert security.exists() and security.is_dir(), "security/ not created"

    def test_init_creates_tests(self, created_module):
        """K-10: tests/ directory is created."""
        tests = created_module / "tests"
        assert tests.exists() and tests.is_dir(), "tests/ not created"

    def test_init_creates_readme(self, created_module):
        """K-11: README.md is created."""
        readme = created_module / "README.md"
        assert readme.exists(), "README.md not created"


# ==============================================================================
# CLI Validate Tests (Category: validate)
# ==============================================================================

class TestCLIValidate:
    """Module validation tests."""

    def test_validate_valid_module(self, created_module):
        """V-01: Valid module passes validation."""
        result = subprocess.run(
            [KIT_CLI, "validate", TEST_MODULE],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Validation failed: {result.stdout}\n{result.stderr}"
        assert "pass" in result.stdout.lower()

    def test_validate_missing_manifest(self, created_module):
        """V-02: Missing manifest fails validation."""
        manifest = created_module / "__manifest__.py"
        manifest.unlink()

        result = subprocess.run(
            [KIT_CLI, "validate", TEST_MODULE],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0, "Missing manifest should fail"

    def test_validate_nonexistent_module(self, ensure_directories):
        """E-01: Nonexistent module shows error."""
        result = subprocess.run(
            [KIT_CLI, "validate", "ipai_nonexistent"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0, "Nonexistent module should fail"

    def test_validate_strict_mode(self, created_module):
        """V-05: Strict mode shows additional warnings."""
        result = subprocess.run(
            [KIT_CLI, "validate", "--strict", TEST_MODULE],
            capture_output=True,
            text=True
        )
        # Should still pass but may show warnings
        assert result.returncode == 0, "Strict validation should pass for valid module"

    def test_validate_all_modules(self, created_module, ensure_directories):
        """Validate all modules in addons directory."""
        result = subprocess.run(
            [KIT_CLI, "validate"],
            capture_output=True,
            text=True
        )
        # May pass or fail depending on other modules
        assert "Validating" in result.stdout


# ==============================================================================
# Module Structure Tests (Category: structure)
# ==============================================================================

class TestModuleStructure:
    """Module structure and content tests."""

    def test_manifest_has_name(self, created_module):
        """M-01: Manifest has name field."""
        manifest = created_module / "__manifest__.py"
        content = manifest.read_text()
        data = eval(content)
        assert "name" in data, "Manifest missing 'name' field"

    def test_manifest_has_version(self, created_module):
        """M-02: Manifest has OCA-style version."""
        manifest = created_module / "__manifest__.py"
        content = manifest.read_text()
        data = eval(content)
        assert "version" in data, "Manifest missing 'version' field"
        # OCA format: <odoo_version>.<major>.<minor>.<patch>
        version = data["version"]
        assert version.startswith("18.0."), f"Version should start with '18.0.': {version}"

    def test_manifest_has_depends(self, created_module):
        """M-03: Manifest has depends with base."""
        manifest = created_module / "__manifest__.py"
        content = manifest.read_text()
        data = eval(content)
        assert "depends" in data, "Manifest missing 'depends' field"
        assert "base" in data["depends"], "Module should depend on 'base'"

    def test_manifest_has_license(self, created_module):
        """M-04: Manifest has license field."""
        manifest = created_module / "__manifest__.py"
        content = manifest.read_text()
        data = eval(content)
        assert "license" in data, "Manifest missing 'license' field"
        assert data["license"] in ["LGPL-3", "AGPL-3", "GPL-3", "OPL-1"]

    def test_security_csv_format(self, created_module):
        """M-05: Security CSV has valid header."""
        csv_path = created_module / "security" / "ir.model.access.csv"
        assert csv_path.exists(), "Security CSV not found"
        content = csv_path.read_text()
        assert "id,name,model_id" in content, "Invalid CSV header"

    def test_test_file_present(self, created_module):
        """M-06: Test file is present."""
        test_file = created_module / "tests" / "test_main.py"
        assert test_file.exists(), "test_main.py not found"


# ==============================================================================
# CLI Build/Deploy Tests (Category: build)
# ==============================================================================

class TestCLIBuild:
    """Build and deployment tests."""

    def test_build_creates_archive(self, created_module):
        """B-01: kit build creates zip archive."""
        result = subprocess.run(
            [KIT_CLI, "build", TEST_MODULE],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        assert "Package created" in result.stdout

    def test_build_custom_output(self, created_module):
        """B-02: Build with custom output directory."""
        output_dir = Path("/tmp/test_build")
        output_dir.mkdir(exist_ok=True)

        result = subprocess.run(
            [KIT_CLI, "build", TEST_MODULE, "-o", str(output_dir)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"

        # Clean up
        shutil.rmtree(output_dir)

    def test_list_modules(self, created_module):
        """B-04: kit list shows modules."""
        result = subprocess.run(
            [KIT_CLI, "list"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert TEST_MODULE in result.stdout

    def test_status_command(self, ensure_directories):
        """kit status shows environment info."""
        result = subprocess.run(
            [KIT_CLI, "status"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "OdooForge Sandbox Status" in result.stdout


# ==============================================================================
# Performance Tests (Category: performance)
# ==============================================================================

class TestPerformance:
    """Performance benchmarks."""

    def test_init_time(self, clean_test_module):
        """P-01: Module init completes in < 5 seconds."""
        start = time.time()
        result = subprocess.run(
            [KIT_CLI, "init", TEST_MODULE],
            capture_output=True,
            text=True
        )
        elapsed = time.time() - start

        assert result.returncode == 0, "Init failed"
        assert elapsed < 5.0, f"Init took too long: {elapsed:.2f}s"

    def test_validate_time(self, created_module):
        """P-02: Module validate completes in < 3 seconds."""
        start = time.time()
        result = subprocess.run(
            [KIT_CLI, "validate", TEST_MODULE],
            capture_output=True,
            text=True
        )
        elapsed = time.time() - start

        assert result.returncode == 0, "Validate failed"
        assert elapsed < 3.0, f"Validate took too long: {elapsed:.2f}s"


# ==============================================================================
# Error Handling Tests (Category: errors)
# ==============================================================================

class TestErrorHandling:
    """Error handling tests."""

    def test_invalid_command(self):
        """E-02: Invalid command shows help."""
        result = subprocess.run(
            [KIT_CLI, "invalidcmd"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        # Should show error or help

    def test_module_not_found_build(self, ensure_directories):
        """Build nonexistent module fails gracefully."""
        result = subprocess.run(
            [KIT_CLI, "build", "ipai_nonexistent"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        assert "not found" in result.stdout.lower() or "not found" in result.stderr.lower()


# ==============================================================================
# End-to-End Tests (Category: e2e)
# ==============================================================================

class TestEndToEnd:
    """End-to-end workflow tests."""

    def test_full_workflow(self, clean_test_module):
        """E2E-01: Full workflow init → validate → build."""
        # Init
        result = subprocess.run([KIT_CLI, "init", TEST_MODULE], capture_output=True, text=True)
        assert result.returncode == 0, f"Init failed: {result.stderr}"

        # Validate
        result = subprocess.run([KIT_CLI, "validate", TEST_MODULE], capture_output=True, text=True)
        assert result.returncode == 0, f"Validate failed: {result.stderr}"

        # Build
        result = subprocess.run([KIT_CLI, "build", TEST_MODULE], capture_output=True, text=True)
        assert result.returncode == 0, f"Build failed: {result.stderr}"

    def test_module_structure_complete(self, created_module):
        """Verify complete module structure after init."""
        expected_files = [
            "__init__.py",
            "__manifest__.py",
            "README.md",
            "models/__init__.py",
            "security/ir.model.access.csv",
            "tests/__init__.py",
            "tests/test_main.py",
        ]

        expected_dirs = [
            "models",
            "views",
            "security",
            "data",
            "static/description",
            "tests",
        ]

        for f in expected_files:
            assert (created_module / f).exists(), f"Missing file: {f}"

        for d in expected_dirs:
            assert (created_module / d).is_dir(), f"Missing directory: {d}"


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
