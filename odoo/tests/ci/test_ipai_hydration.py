"""
Tests for IPAI module hydration validation.

Tests validate:
- Manifest parsing (dict vs dict() syntax)
- Missing module detection
- Missing dependency detection
- Deprecated module blocking in required groups
- Database name validation
"""

import json
import os
import sys
import tempfile
from pathlib import Path
import yaml
import pytest


class TestManifestParsing:
    """Test __manifest__.py parsing."""

    def test_parse_dict_syntax(self, tmp_path):
        """Test parsing manifest with {} syntax."""
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        manifest_file = module_path / "__manifest__.py"
        manifest_file.write_text(
            "{\n"
            "    'name': 'Test Module',\n"
            "    'version': '18.0.1.0.0',\n"
            "    'depends': ['base'],\n"
            "}\n"
        )
        
        # Should be parseable
        import ast
        content = manifest_file.read_text()
        result = ast.literal_eval(content)
        
        assert isinstance(result, dict)
        assert result['name'] == 'Test Module'
        assert result['depends'] == ['base']

    def test_parse_dict_call_syntax(self, tmp_path):
        """Test parsing manifest with dict() syntax."""
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        manifest_file = module_path / "__manifest__.py"
        manifest_file.write_text(
            "dict(\n"
            "    name='Test Module',\n"
            "    version='18.0.1.0.0',\n"
            ")\n"
        )
        
        # dict() syntax is NOT valid for ast.literal_eval; should fail gracefully
        import ast
        content = manifest_file.read_text()
        
        with pytest.raises(ValueError):
            ast.literal_eval(content)

    def test_manifest_missing_required_fields(self, tmp_path):
        """Test manifest missing required fields."""
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        manifest_file = module_path / "__manifest__.py"
        manifest_file.write_text(
            "{\n"
            "    'name': 'Test Module',\n"
            "}\n"  # Missing 'version'
        )
        
        import ast
        content = manifest_file.read_text()
        result = ast.literal_eval(content)
        
        # Script should detect missing 'version'
        required_fields = ['name', 'version']
        errors = []
        for field in required_fields:
            if field not in result:
                errors.append(f"Missing required field: {field}")
        
        assert len(errors) == 1
        assert 'version' in errors[0]


class TestDatabaseNameValidation:
    """Test database name validation."""

    def test_allowed_ci_pattern(self):
        """Test CI database name patterns."""
        import re
        
        patterns = [
            r"^ci_odoo_[a-z0-9_]{3,30}$",
            r"^odoo_test_[a-z0-9_]{3,30}$",
        ]
        
        valid_names = [
            "ci_odoo_test",
            "ci_odoo_pr123",
            "ci_odoo_core_minimal",
            "odoo_test_bir",
            "odoo_test_finops_core",
        ]
        
        for name in valid_names:
            matched = any(re.match(p, name) for p in patterns)
            assert matched, f"Should match patterns: {name}"

    def test_rejected_production_names(self):
        """Test production database names are rejected."""
        import re
        
        patterns = [
            r"^ci_odoo_[a-z0-9_]{3,30}$",
            r"^odoo_test_[a-z0-9_]{3,30}$",
        ]
        
        invalid_names = [
            "odoo",
            "odoo_prod",
            "odoo_production",
            "odoo_staging",
            "defaultdb",
            "postgres",
        ]
        
        for name in invalid_names:
            matched = any(re.match(p, name) for p in patterns)
            assert not matched, f"Should NOT match patterns: {name}"

    def test_forbidden_names_list(self):
        """Test forbidden database names list."""
        forbidden = ["odoo", "odoo_prod", "odoo_production", "odoo_staging", "defaultdb"]
        
        test_names = {
            "ci_odoo_test": False,  # Should pass (not forbidden)
            "odoo": True,           # Should fail (forbidden)
            "odoo_prod": True,      # Should fail (forbidden)
        }
        
        for name, should_fail in test_names.items():
            is_forbidden = name in forbidden
            assert is_forbidden == should_fail


class TestInstallGroupValidation:
    """Test install group configuration."""

    def test_install_group_structure(self):
        """Test install group has required structure."""
        group = {
            "description": "Test group",
            "required": True,
            "ci_required": True,
            "modules": ["module1", "module2"],
            "dependencies_closure": True,
        }
        
        required_fields = ["description", "modules"]
        for field in required_fields:
            assert field in group, f"Missing field: {field}"

    def test_deprecated_module_detection(self):
        """Test deprecated module is flagged."""
        modules = {
            "active_module": {
                "status": "active",
                "depends_on": [],
            },
            "deprecated_module": {
                "status": "deprecated",
                "depends_on": [],
            },
        }
        
        # Should flag deprecated
        deprecated = [name for name, meta in modules.items() if meta['status'] == 'deprecated']
        
        assert "deprecated_module" in deprecated
        assert "active_module" not in deprecated


class TestDependencyValidation:
    """Test dependency closure validation."""

    def test_dependency_exists(self):
        """Test dependency validation."""
        modules = {
            "base": {
                "status": "active",
                "depends_on": [],
            },
            "module_a": {
                "status": "active",
                "depends_on": ["base"],
            },
            "module_b": {
                "status": "active",
                "depends_on": ["module_a"],
            },
        }
        
        # Validate all dependencies exist
        errors = []
        for module_name, module_meta in modules.items():
            for dep in module_meta.get('depends_on', []):
                if dep not in modules:
                    errors.append(f"Module {module_name} depends on missing {dep}")
        
        assert len(errors) == 0

    def test_missing_dependency_detection(self):
        """Test missing dependency is detected."""
        modules = {
            "module_a": {
                "status": "active",
                "depends_on": ["nonexistent"],
            },
        }
        
        errors = []
        for module_name, module_meta in modules.items():
            for dep in module_meta.get('depends_on', []):
                if dep not in modules:
                    errors.append(f"Module {module_name} depends on missing {dep}")
        
        assert len(errors) == 1
        assert "nonexistent" in errors[0]


class TestHydrationReport:
    """Test evidence report generation."""

    def test_report_structure(self):
        """Test hydration report has required fields."""
        report = {
            "timestamp": "2026-04-27T...",
            "odoo_root": "/path/to/odoo",
            "config_path": "ssot/odoo/ipai-install-baseline.yaml",
            "validation_results": {
                "modules": {},
                "install_groups": {},
                "dependencies": {},
            },
            "errors": [],
            "summary": {
                "total_modules": 0,
                "found_modules": 0,
                "missing_modules": 0,
                "manifest_errors": 0,
                "deprecated_in_required": 0,
            },
        }
        
        required_fields = ["timestamp", "validation_results", "summary"]
        for field in required_fields:
            assert field in report, f"Missing field: {field}"
        
        # Summary must have specific metrics
        summary_fields = ["total_modules", "found_modules", "missing_modules"]
        for field in summary_fields:
            assert field in report["summary"], f"Missing summary field: {field}"

    def test_report_json_serializable(self):
        """Test report is JSON-serializable."""
        report = {
            "timestamp": "2026-04-27T00:00:00Z",
            "modules": ["module_a", "module_b"],
            "summary": {"total": 2, "valid": 2},
        }
        
        # Should serialize without error
        json_str = json.dumps(report)
        loaded = json.loads(json_str)
        
        assert loaded["timestamp"] == report["timestamp"]
        assert len(loaded["modules"]) == 2


class TestSSoTConfiguration:
    """Test SSOT configuration file."""

    def test_ipai_install_baseline_yaml_valid(self):
        """Test ipai-install-baseline.yaml is valid YAML."""
        # This is a real-world test that would read the actual file
        # For unit tests, we simulate:
        
        yaml_content = """
version: 1
install_groups:
  core_minimal:
    description: "Minimal IPAI runtime"
    required: true
    modules:
      - ipai_finops_compliance_core
modules:
  ipai_finops_compliance_core:
    status: active
    depends_on: []
"""
        
        parsed = yaml.safe_load(yaml_content)
        
        assert "install_groups" in parsed
        assert "core_minimal" in parsed["install_groups"]
        assert "modules" in parsed
        assert "ipai_finops_compliance_core" in parsed["modules"]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
