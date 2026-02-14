"""Validator tests for IPAI Control Plane."""

import pytest
from pathlib import Path
import tempfile
import os

from validators.manifest import ManifestValidator
from validators.xml import XMLValidator
from validators.security import SecurityValidator


class TestManifestValidator:
    """Manifest validator tests."""

    def setup_method(self):
        """Setup test fixtures."""
        self.validator = ManifestValidator()

    def test_valid_manifest(self):
        """Should validate correct manifest."""
        manifest_content = """
{
    'name': 'Test Module',
    'version': '1.0.0',
    'depends': ['base'],
    'installable': True,
    'author': 'Test Author',
    'license': 'AGPL-3',
    'category': 'Test',
    'summary': 'Test module'
}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='__manifest__.py', delete=False) as f:
            f.write(manifest_content)
            manifest_path = Path(f.name)

        try:
            result = self.validator.validate(manifest_path)

            assert result['valid'] is True
            assert len([i for i in result['issues'] if i['severity'] == 'error']) == 0
        finally:
            os.unlink(manifest_path)

    def test_missing_required_keys(self):
        """Should detect missing required keys."""
        manifest_content = """
{
    'name': 'Test Module',
    'version': '1.0.0'
    # Missing: depends, installable
}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='__manifest__.py', delete=False) as f:
            f.write(manifest_content)
            manifest_path = Path(f.name)

        try:
            result = self.validator.validate(manifest_path)

            assert result['valid'] is False
            errors = [i for i in result['issues'] if i['severity'] == 'error']
            assert len(errors) > 0

            # Should have errors for missing keys
            missing_keys = [e for e in errors if 'required key' in e['message'].lower()]
            assert len(missing_keys) > 0
        finally:
            os.unlink(manifest_path)

    def test_ee_module_dependency_detection(self):
        """Should detect Enterprise Edition module dependencies."""
        manifest_content = """
{
    'name': 'Test Module',
    'version': '1.0.0',
    'depends': ['base', 'web_studio', 'account_accountant'],
    'installable': True,
    'author': 'Test Author',
    'license': 'AGPL-3'
}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='__manifest__.py', delete=False) as f:
            f.write(manifest_content)
            manifest_path = Path(f.name)

        try:
            result = self.validator.validate(manifest_path)

            assert result['valid'] is False
            errors = [i for i in result['issues'] if i['severity'] == 'error']
            assert len(errors) > 0

            # Should have error for EE dependencies
            ee_errors = [e for e in errors if 'enterprise' in e['message'].lower()]
            assert len(ee_errors) > 0
        finally:
            os.unlink(manifest_path)

    def test_invalid_version_format(self):
        """Should detect invalid version format."""
        manifest_content = """
{
    'name': 'Test Module',
    'version': 'invalid-version',
    'depends': ['base'],
    'installable': True,
    'author': 'Test Author',
    'license': 'AGPL-3'
}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='__manifest__.py', delete=False) as f:
            f.write(manifest_content)
            manifest_path = Path(f.name)

        try:
            result = self.validator.validate(manifest_path)

            issues = result['issues']
            version_issues = [i for i in issues if 'version' in i['message'].lower()]
            assert len(version_issues) > 0
        finally:
            os.unlink(manifest_path)


class TestXMLValidator:
    """XML validator tests."""

    def setup_method(self):
        """Setup test fixtures."""
        self.validator = XMLValidator()

    def test_valid_xml(self):
        """Should validate correct Odoo XML."""
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_test_form" model="ir.ui.view">
        <field name="name">test.form</field>
        <field name="model">test.model</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <field name="name"/>
                </sheet>
            </form>
        </field>
    </record>
</odoo>
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            xml_path = Path(f.name)

        try:
            result = self.validator.validate(xml_path)

            assert result['valid'] is True
            errors = [i for i in result['issues'] if i['severity'] == 'error']
            assert len(errors) == 0
        finally:
            os.unlink(xml_path)

    def test_deprecated_tree_element(self):
        """Should detect deprecated <tree> element (should be <list> in Odoo 19+)."""
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_test_tree" model="ir.ui.view">
        <field name="name">test.tree</field>
        <field name="model">test.model</field>
        <field name="arch" type="xml">
            <tree>
                <field name="name"/>
            </tree>
        </field>
    </record>
</odoo>
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            xml_path = Path(f.name)

        try:
            result = self.validator.validate(xml_path)

            warnings = [i for i in result['issues'] if 'tree' in i['message'].lower() and 'list' in i['message'].lower()]
            assert len(warnings) > 0
        finally:
            os.unlink(xml_path)

    def test_missing_external_id(self):
        """Should detect missing external IDs on records."""
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record model="ir.ui.view">
        <field name="name">test.form</field>
        <field name="model">test.model</field>
        <field name="arch" type="xml">
            <form>
                <field name="name"/>
            </form>
        </field>
    </record>
</odoo>
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            xml_path = Path(f.name)

        try:
            result = self.validator.validate(xml_path)

            warnings = [i for i in result['issues'] if 'external id' in i['message'].lower()]
            assert len(warnings) > 0
        finally:
            os.unlink(xml_path)

    def test_malformed_xml(self):
        """Should detect malformed XML."""
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="test">
        <field name="name">Test</field>
    <!-- Missing closing </record> tag -->
</odoo>
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            xml_path = Path(f.name)

        try:
            result = self.validator.validate(xml_path)

            assert result['valid'] is False
            errors = [i for i in result['issues'] if i['severity'] == 'error']
            assert len(errors) > 0
        finally:
            os.unlink(xml_path)


class TestSecurityValidator:
    """Security validator tests."""

    def setup_method(self):
        """Setup test fixtures."""
        self.validator = SecurityValidator()

    def test_valid_security_configuration(self):
        """Should validate correct security setup."""
        # Create test directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)

            # Create models file
            models_dir = module_path / "models"
            models_dir.mkdir()
            (models_dir / "__init__.py").touch()

            models_file = models_dir / "test_model.py"
            models_file.write_text("""
from odoo import models, fields

class TestModel(models.Model):
    _name = 'test.model'
    _description = 'Test Model'

    name = fields.Char('Name')
""")

            # Create security directory with access rules
            security_dir = module_path / "security"
            security_dir.mkdir()

            access_file = security_dir / "ir.model.access.csv"
            access_file.write_text("""
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_test_model_user,test.model,model_test_model,base.group_user,1,1,1,1
""")

            result = self.validator.validate(module_path)

            # Should have minimal issues if any
            errors = [i for i in result['issues'] if i['severity'] == 'error']
            # Allow for some warnings but no critical errors
            assert len(errors) == 0 or result['valid'] is True

    def test_missing_access_rules(self):
        """Should detect missing access rules for models."""
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)

            # Create models file
            models_dir = module_path / "models"
            models_dir.mkdir()
            (models_dir / "__init__.py").touch()

            models_file = models_dir / "test_model.py"
            models_file.write_text("""
from odoo import models, fields

class TestModel(models.Model):
    _name = 'test.model'
    _description = 'Test Model'

    name = fields.Char('Name')
""")

            # No security directory - missing access rules

            result = self.validator.validate(module_path)

            warnings = [i for i in result['issues'] if 'access' in i['message'].lower()]
            assert len(warnings) > 0

    def test_detect_empty_record_rules(self):
        """Should detect potentially insecure empty domain record rules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)

            # Create security directory with record rule
            security_dir = module_path / "security"
            security_dir.mkdir()

            rules_file = security_dir / "test_security.xml"
            rules_file.write_text("""<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="test_rule" model="ir.rule">
        <field name="name">Test Rule</field>
        <field name="model_id" ref="model_test_model"/>
        <field name="domain_force">[]</field>
    </record>
</odoo>
""")

            result = self.validator.validate(module_path)

            warnings = [i for i in result['issues'] if 'domain' in i['message'].lower()]
            assert len(warnings) > 0
