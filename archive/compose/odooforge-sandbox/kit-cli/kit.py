#!/usr/bin/env python3
"""
OdooForge Kit CLI - Module Development and Validation Toolkit

Commands:
    init <module_name>   - Create a new Odoo module
    validate             - Validate module structure and code
    build                - Build module package
    deploy               - Deploy module to Odoo
    version              - Show version information
"""

import os
import sys
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

import click
import yaml

__version__ = "1.0.0"

# Constants
ADDONS_DIR = Path("/workspace/addons")
TEMPLATES_DIR = Path("/workspace/templates")
SPECS_DIR = Path("/workspace/specs")
REPORTS_DIR = Path("/workspace/reports")

# IPAI Module naming pattern
MODULE_PATTERN = re.compile(r'^ipai_[a-z][a-z0-9_]*$')

# Required files for a valid module
REQUIRED_FILES = [
    "__init__.py",
    "__manifest__.py",
]

# Recommended files
RECOMMENDED_FILES = [
    "README.md",
    "models/__init__.py",
    "security/ir.model.access.csv",
]


def echo_success(msg):
    click.echo(click.style(f"✓ {msg}", fg="green"))


def echo_error(msg):
    click.echo(click.style(f"✗ {msg}", fg="red"))


def echo_warning(msg):
    click.echo(click.style(f"! {msg}", fg="yellow"))


def echo_info(msg):
    click.echo(click.style(f"→ {msg}", fg="blue"))


@click.group()
@click.version_option(__version__, prog_name="kit")
def cli():
    """OdooForge Kit CLI - Module development and validation toolkit."""
    pass


@cli.command()
def version():
    """Show version information."""
    click.echo(f"OdooForge Kit CLI v{__version__}")
    click.echo(f"Python {sys.version}")
    click.echo(f"Workspace: {ADDONS_DIR}")


@cli.command()
@click.argument("module_name")
@click.option("--template", "-t", default="basic", help="Module template to use")
@click.option("--author", "-a", default="IPAI Team", help="Module author")
@click.option("--description", "-d", default="", help="Module description")
def init(module_name, template, author, description):
    """Initialize a new Odoo module.

    MODULE_NAME must follow IPAI naming convention: ipai_<name>
    """
    # Validate module name
    if not MODULE_PATTERN.match(module_name):
        echo_error(f"Invalid module name: {module_name}")
        echo_info("Module name must match pattern: ipai_<name>")
        echo_info("Examples: ipai_hello, ipai_finance_core, ipai_ai_agents")
        sys.exit(1)

    module_path = ADDONS_DIR / module_name

    # Check if module already exists
    if module_path.exists():
        echo_error(f"Module already exists: {module_path}")
        sys.exit(1)

    # Create module structure
    echo_info(f"Creating module: {module_name}")

    try:
        # Create directories
        (module_path / "models").mkdir(parents=True)
        (module_path / "views").mkdir()
        (module_path / "security").mkdir()
        (module_path / "data").mkdir()
        (module_path / "static" / "description").mkdir(parents=True)
        (module_path / "tests").mkdir()

        # Generate description if not provided
        if not description:
            # Convert module name to title
            description = module_name.replace("ipai_", "IPAI ").replace("_", " ").title()

        # Create __manifest__.py
        manifest = {
            "name": description,
            "version": "18.0.1.0.0",
            "category": "IPAI",
            "summary": description,
            "description": f"IPAI Custom Module: {description}",
            "author": author,
            "website": "https://github.com/jgtolentino/odoo-ce",
            "license": "LGPL-3",
            "depends": ["base"],
            "data": [],
            "demo": [],
            "installable": True,
            "application": False,
            "auto_install": False,
        }

        manifest_content = f'''{json.dumps(manifest, indent=4)}
'''
        (module_path / "__manifest__.py").write_text(manifest_content)

        # Create __init__.py
        (module_path / "__init__.py").write_text("from . import models\n")

        # Create models/__init__.py
        (module_path / "models" / "__init__.py").write_text("# Models\n")

        # Create security/ir.model.access.csv
        security_content = "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n"
        (module_path / "security" / "ir.model.access.csv").write_text(security_content)

        # Create README.md
        readme_content = f"""# {description}

## Overview

{description} - Custom IPAI Odoo module.

## Installation

1. Copy module to addons directory
2. Update module list in Odoo
3. Install from Apps menu

## Configuration

No special configuration required.

## Usage

[Document module usage here]

## Technical Details

- **Technical Name**: `{module_name}`
- **Version**: 18.0.1.0.0
- **License**: LGPL-3
- **Dependencies**: base

## Changelog

### 1.0.0

- Initial release
"""
        (module_path / "README.md").write_text(readme_content)

        # Create test file
        test_content = f'''# -*- coding: utf-8 -*-
"""Tests for {module_name}."""

from odoo.tests.common import TransactionCase


class Test{module_name.title().replace("_", "")}(TransactionCase):
    """Test cases for {module_name}."""

    def setUp(self):
        super().setUp()
        # Setup test data

    def test_basic(self):
        """Test basic functionality."""
        self.assertTrue(True)
'''
        (module_path / "tests" / "__init__.py").write_text("from . import test_main\n")
        (module_path / "tests" / "test_main.py").write_text(test_content)

        # Create icon placeholder
        icon_readme = "Place module icon (icon.png, 128x128) here\n"
        (module_path / "static" / "description" / ".gitkeep").write_text(icon_readme)

        echo_success(f"Module created: {module_name}")
        echo_info(f"Location: {module_path}")
        echo_info("Files created:")
        for f in sorted(module_path.rglob("*")):
            if f.is_file():
                rel_path = f.relative_to(module_path)
                click.echo(f"  - {rel_path}")

    except Exception as e:
        echo_error(f"Failed to create module: {e}")
        # Cleanup on failure
        if module_path.exists():
            shutil.rmtree(module_path)
        sys.exit(1)


@cli.command()
@click.argument("module_name", required=False)
@click.option("--strict", is_flag=True, help="Enable strict validation")
def validate(module_name, strict):
    """Validate module structure and code.

    If MODULE_NAME is not provided, validates all modules in addons directory.
    """
    if module_name:
        modules = [ADDONS_DIR / module_name]
    else:
        modules = [d for d in ADDONS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]

    if not modules:
        echo_warning("No modules found in addons directory")
        return

    total_errors = 0
    total_warnings = 0

    for module_path in modules:
        click.echo(f"\nValidating: {module_path.name}")
        click.echo("-" * 40)

        errors, warnings = validate_module(module_path, strict)
        total_errors += errors
        total_warnings += warnings

    click.echo("\n" + "=" * 40)
    if total_errors == 0:
        echo_success(f"All rules pass! ({total_warnings} warnings)")
    else:
        echo_error(f"Validation failed: {total_errors} errors, {total_warnings} warnings")
        sys.exit(1)


def validate_module(module_path: Path, strict: bool = False) -> tuple:
    """Validate a single module. Returns (errors, warnings) count."""
    errors = 0
    warnings = 0

    # Check module exists
    if not module_path.exists():
        echo_error(f"Module not found: {module_path}")
        return 1, 0

    # Check naming convention
    if not MODULE_PATTERN.match(module_path.name):
        echo_error(f"Module name does not follow IPAI convention: {module_path.name}")
        errors += 1
    else:
        echo_success("Module name follows IPAI convention")

    # Check required files
    for req_file in REQUIRED_FILES:
        file_path = module_path / req_file
        if not file_path.exists():
            echo_error(f"Missing required file: {req_file}")
            errors += 1
        else:
            echo_success(f"Found: {req_file}")

    # Check recommended files
    for rec_file in RECOMMENDED_FILES:
        file_path = module_path / rec_file
        if not file_path.exists():
            echo_warning(f"Missing recommended file: {rec_file}")
            warnings += 1
        else:
            echo_success(f"Found: {rec_file}")

    # Validate manifest
    manifest_path = module_path / "__manifest__.py"
    if manifest_path.exists():
        manifest_errors, manifest_warnings = validate_manifest(manifest_path, strict)
        errors += manifest_errors
        warnings += manifest_warnings

    # Check for Python syntax errors
    py_errors = check_python_syntax(module_path)
    errors += py_errors

    return errors, warnings


def validate_manifest(manifest_path: Path, strict: bool = False) -> tuple:
    """Validate __manifest__.py content."""
    errors = 0
    warnings = 0

    try:
        content = manifest_path.read_text()
        # Simple eval for manifest dict (safe in this context)
        manifest = eval(content)

        # Required fields
        required_fields = ["name", "version", "depends", "license"]
        for field in required_fields:
            if field not in manifest:
                echo_error(f"Manifest missing required field: {field}")
                errors += 1

        # Check version format (OCA style)
        version = manifest.get("version", "")
        if not re.match(r"^\d+\.\d+\.\d+\.\d+\.\d+$", version):
            echo_warning(f"Version should follow OCA format: <odoo_version>.<major>.<minor>.<patch>")
            warnings += 1

        # Check license
        valid_licenses = ["LGPL-3", "AGPL-3", "GPL-3", "OPL-1"]
        if manifest.get("license") not in valid_licenses:
            echo_warning(f"License should be one of: {', '.join(valid_licenses)}")
            warnings += 1

        if strict:
            # Check for category
            if not manifest.get("category"):
                echo_warning("Manifest missing 'category' field")
                warnings += 1

            # Check for author
            if not manifest.get("author"):
                echo_warning("Manifest missing 'author' field")
                warnings += 1

        echo_success("Manifest structure is valid")

    except SyntaxError as e:
        echo_error(f"Manifest has syntax error: {e}")
        errors += 1
    except Exception as e:
        echo_error(f"Failed to parse manifest: {e}")
        errors += 1

    return errors, warnings


def check_python_syntax(module_path: Path) -> int:
    """Check Python files for syntax errors."""
    errors = 0

    for py_file in module_path.rglob("*.py"):
        try:
            with open(py_file, "r") as f:
                compile(f.read(), py_file, "exec")
        except SyntaxError as e:
            echo_error(f"Syntax error in {py_file.name}: {e}")
            errors += 1

    if errors == 0:
        echo_success("All Python files have valid syntax")

    return errors


@cli.command()
@click.argument("module_name")
@click.option("--output", "-o", default=None, help="Output directory for package")
def build(module_name, output):
    """Build module package for distribution."""
    module_path = ADDONS_DIR / module_name

    if not module_path.exists():
        echo_error(f"Module not found: {module_name}")
        sys.exit(1)

    # Validate first
    errors, _ = validate_module(module_path)
    if errors > 0:
        echo_error("Module validation failed. Fix errors before building.")
        sys.exit(1)

    # Determine output path
    if output:
        output_dir = Path(output)
    else:
        output_dir = REPORTS_DIR / "builds"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamp for build
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"{module_name}_{timestamp}"
    archive_path = output_dir / archive_name

    # Create zip archive
    echo_info(f"Building package: {archive_name}.zip")
    shutil.make_archive(str(archive_path), "zip", ADDONS_DIR, module_name)

    echo_success(f"Package created: {archive_path}.zip")

    # Generate build info
    build_info = {
        "module": module_name,
        "timestamp": timestamp,
        "archive": f"{archive_name}.zip",
        "created_at": datetime.now().isoformat(),
    }

    info_path = output_dir / f"{archive_name}_info.json"
    info_path.write_text(json.dumps(build_info, indent=2))
    echo_info(f"Build info: {info_path}")


@cli.command()
@click.argument("module_name")
@click.option("--upgrade", "-u", is_flag=True, help="Upgrade if already installed")
def deploy(module_name, upgrade):
    """Deploy module to Odoo instance.

    Note: This command requires Odoo to be running and accessible.
    """
    import requests

    module_path = ADDONS_DIR / module_name

    if not module_path.exists():
        echo_error(f"Module not found: {module_name}")
        sys.exit(1)

    odoo_host = os.environ.get("ODOO_HOST", "odoo")
    odoo_port = os.environ.get("ODOO_PORT", "8069")
    odoo_url = f"http://{odoo_host}:{odoo_port}"

    echo_info(f"Connecting to Odoo at {odoo_url}")

    # Check Odoo is accessible
    try:
        response = requests.get(f"{odoo_url}/web/health", timeout=10)
        if response.status_code != 200:
            echo_error("Odoo is not healthy")
            sys.exit(1)
        echo_success("Odoo is accessible")
    except requests.RequestException as e:
        echo_error(f"Cannot connect to Odoo: {e}")
        sys.exit(1)

    # For actual deployment, you would use XML-RPC or JSON-RPC
    # This is a placeholder that indicates successful connection
    action = "upgrade" if upgrade else "install"
    echo_info(f"Module {module_name} ready for {action}")
    echo_warning("Use Odoo Apps menu to complete installation")
    echo_info("Or run: odoo -d <database> -i {module_name}")


@cli.command()
def list():
    """List all modules in the addons directory."""
    modules = [d for d in ADDONS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]

    if not modules:
        echo_warning("No modules found")
        return

    click.echo(f"\nModules in {ADDONS_DIR}:")
    click.echo("-" * 40)

    for module in sorted(modules):
        manifest_path = module / "__manifest__.py"
        if manifest_path.exists():
            try:
                manifest = eval(manifest_path.read_text())
                name = manifest.get("name", module.name)
                version = manifest.get("version", "N/A")
                click.echo(f"  {module.name:<30} v{version}")
            except Exception:
                click.echo(f"  {module.name:<30} (invalid manifest)")
        else:
            click.echo(f"  {module.name:<30} (no manifest)")


@cli.command()
def status():
    """Show sandbox environment status."""
    click.echo("\nOdooForge Sandbox Status")
    click.echo("=" * 40)

    # Check directories
    click.echo("\nDirectories:")
    for name, path in [
        ("Addons", ADDONS_DIR),
        ("Templates", TEMPLATES_DIR),
        ("Specs", SPECS_DIR),
        ("Reports", REPORTS_DIR),
    ]:
        if path.exists():
            count = len(list(path.iterdir()))
            echo_success(f"{name}: {path} ({count} items)")
        else:
            echo_warning(f"{name}: {path} (not found)")

    # Check Odoo connection
    click.echo("\nOdoo Connection:")
    odoo_host = os.environ.get("ODOO_HOST", "odoo")
    odoo_port = os.environ.get("ODOO_PORT", "8069")

    try:
        import requests
        response = requests.get(f"http://{odoo_host}:{odoo_port}/web/health", timeout=5)
        if response.status_code == 200:
            echo_success(f"Odoo: http://{odoo_host}:{odoo_port} (healthy)")
        else:
            echo_warning(f"Odoo: http://{odoo_host}:{odoo_port} (status: {response.status_code})")
    except Exception as e:
        echo_warning(f"Odoo: http://{odoo_host}:{odoo_port} (not reachable)")

    # Check database
    click.echo("\nDatabase:")
    db_host = os.environ.get("DB_HOST", "db")
    db_port = os.environ.get("DB_PORT", "5432")

    try:
        import subprocess
        result = subprocess.run(
            ["pg_isready", "-h", db_host, "-p", db_port],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            echo_success(f"PostgreSQL: {db_host}:{db_port} (accepting connections)")
        else:
            echo_warning(f"PostgreSQL: {db_host}:{db_port} (not ready)")
    except Exception:
        echo_warning(f"PostgreSQL: {db_host}:{db_port} (status unknown)")


if __name__ == "__main__":
    cli()
