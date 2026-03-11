#!/usr/bin/env python3
"""
IPAI Module Audit Agent

Auto-generates per-module documentation and install/upgrade evidence matrix.
Designed to run in CI as a "drift gate" to prevent regression.

Usage:
    python scripts/module_audit_agent.py --output artifacts/
    python scripts/module_audit_agent.py --module ipai_agent_core --verbose
    python scripts/module_audit_agent.py --ci  # CI mode with exit codes

Outputs:
    - artifacts/module_audit_matrix.json    # Full audit results
    - artifacts/module_audit_matrix.csv     # Summary for spreadsheets
    - docs/modules/                         # Per-module README files

Author: InsightPulse AI
License: LGPL-3
"""

import argparse
import ast
import csv
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Configuration
REPO_ROOT = Path(__file__).parent.parent
ADDONS_PATHS = [
    REPO_ROOT / "addons",
    REPO_ROOT / "addons" / "ipai",
]
OUTPUT_DIR = REPO_ROOT / "artifacts"
DOCS_DIR = REPO_ROOT / "docs" / "modules"


@dataclass
class ModuleAudit:
    """Audit result for a single module."""

    name: str
    path: str
    version: str = ""
    summary: str = ""
    author: str = ""
    depends: List[str] = field(default_factory=list)

    # Validation results
    manifest_valid: bool = False
    python_syntax_ok: bool = False
    xml_syntax_ok: bool = False
    security_csv_ok: bool = False
    init_imports_ok: bool = False

    # Counts
    model_count: int = 0
    view_count: int = 0
    menu_count: int = 0
    action_count: int = 0
    data_file_count: int = 0

    # Issues
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Install/upgrade evidence
    install_tested: bool = False
    install_success: bool = False
    install_log: str = ""
    upgrade_tested: bool = False
    upgrade_success: bool = False
    upgrade_log: str = ""

    # Timestamps
    audited_at: str = ""

    @property
    def status(self) -> str:
        """Overall status: PASS, WARN, FAIL."""
        if self.issues:
            return "FAIL"
        if self.warnings:
            return "WARN"
        if all(
            [
                self.manifest_valid,
                self.python_syntax_ok,
                self.xml_syntax_ok,
                self.init_imports_ok,
            ]
        ):
            return "PASS"
        return "UNKNOWN"


class ModuleAuditor:
    """Audits Odoo modules for quality gate compliance."""

    def __init__(self, addons_paths: List[Path] = None, verbose: bool = False):
        self.addons_paths = addons_paths or ADDONS_PATHS
        self.verbose = verbose
        self.audits: Dict[str, ModuleAudit] = {}

    def log(self, msg: str):
        if self.verbose:
            print(f"  {msg}")

    def find_modules(self, pattern: str = "ipai_*") -> List[Path]:
        """Find all modules matching pattern."""
        modules = []
        for addons_path in self.addons_paths:
            if not addons_path.exists():
                continue
            for item in addons_path.iterdir():
                if not item.is_dir():
                    continue
                if not item.name.startswith(pattern.replace("*", "")):
                    continue
                manifest = item / "__manifest__.py"
                if manifest.exists():
                    modules.append(item)
        return sorted(modules, key=lambda p: p.name)

    def audit_module(self, module_path: Path) -> ModuleAudit:
        """Run full audit on a module."""
        name = module_path.name
        audit = ModuleAudit(
            name=name, path=str(module_path), audited_at=datetime.now().isoformat()
        )

        self.log(f"Auditing {name}...")

        # 1. Parse manifest
        self._audit_manifest(module_path, audit)

        # 2. Check Python syntax
        self._audit_python(module_path, audit)

        # 3. Check XML syntax
        self._audit_xml(module_path, audit)

        # 4. Check security files
        self._audit_security(module_path, audit)

        # 5. Check __init__.py imports
        self._audit_init_imports(module_path, audit)

        # 6. Count objects
        self._count_objects(module_path, audit)

        self.audits[name] = audit
        return audit

    def _audit_manifest(self, module_path: Path, audit: ModuleAudit):
        """Parse and validate __manifest__.py."""
        manifest_path = module_path / "__manifest__.py"
        try:
            content = manifest_path.read_text(encoding="utf-8")
            manifest = ast.literal_eval(content)

            audit.manifest_valid = True
            audit.version = manifest.get("version", "")
            audit.summary = manifest.get("summary", manifest.get("name", ""))
            audit.author = manifest.get("author", "")
            audit.depends = manifest.get("depends", [])

            # Check for enterprise-only deps
            enterprise_only = {
                "accountant",
                "knowledge",
                "web_studio",
                "sign",
                "helpdesk",
                "planning",
                "sale_subscription",
                "quality_control",
                "hr_appraisal",
                "marketing_automation",
                "appointment",
                "web_mobile",
                "stock_barcode",
                "voip",
                "sale_amazon",
                "industry_fsm",
                "timesheet_grid",
            }
            for dep in audit.depends:
                if dep in enterprise_only:
                    audit.issues.append(f"Enterprise-only dependency: {dep}")

            # Check installable
            if not manifest.get("installable", True):
                audit.warnings.append("Module marked as not installable")

            # Count data files
            audit.data_file_count = len(manifest.get("data", []))

        except SyntaxError as e:
            audit.issues.append(f"Manifest syntax error: {e}")
        except Exception as e:
            audit.issues.append(f"Manifest parse error: {e}")

    def _audit_python(self, module_path: Path, audit: ModuleAudit):
        """Check Python syntax for all .py files."""
        py_files = list(module_path.rglob("*.py"))
        errors = []

        for py_file in py_files:
            try:
                with open(py_file, "rb") as f:
                    compile(f.read(), py_file, "exec")
            except SyntaxError as e:
                errors.append(f"{py_file.name}:{e.lineno}: {e.msg}")

        audit.python_syntax_ok = len(errors) == 0
        for error in errors:
            audit.issues.append(f"Python syntax: {error}")

    def _audit_xml(self, module_path: Path, audit: ModuleAudit):
        """Check XML syntax for all .xml files."""
        xml_files = list(module_path.rglob("*.xml"))
        errors = []

        for xml_file in xml_files:
            try:
                ET.parse(xml_file)
            except ET.ParseError as e:
                errors.append(f"{xml_file.name}: {e}")

        audit.xml_syntax_ok = len(errors) == 0
        for error in errors:
            audit.issues.append(f"XML parse: {error}")

    def _audit_security(self, module_path: Path, audit: ModuleAudit):
        """Check security/ir.model.access.csv."""
        csv_path = module_path / "security" / "ir.model.access.csv"

        if not csv_path.exists():
            # Not all modules need security CSV
            audit.security_csv_ok = True
            audit.warnings.append("No security/ir.model.access.csv")
            return

        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                # Validate columns
                required_cols = {"id", "name", "model_id:id"}
                if not required_cols.issubset(set(reader.fieldnames or [])):
                    audit.issues.append(
                        f"Security CSV missing columns: {required_cols}"
                    )
                    return

                audit.security_csv_ok = True

        except Exception as e:
            audit.issues.append(f"Security CSV error: {e}")

    def _audit_init_imports(self, module_path: Path, audit: ModuleAudit):
        """Check __init__.py imports subpackages correctly."""
        init_path = module_path / "__init__.py"

        if not init_path.exists():
            audit.issues.append("Missing __init__.py")
            return

        content = init_path.read_text(encoding="utf-8")

        # Check for expected subpackage imports
        subpackages = []
        for item in module_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                subpackages.append(item.name)

        missing = []
        for pkg in subpackages:
            if pkg not in content:
                missing.append(pkg)

        if missing:
            audit.warnings.append(f"Subpackages not imported in __init__.py: {missing}")

        audit.init_imports_ok = len(missing) == 0

    def _count_objects(self, module_path: Path, audit: ModuleAudit):
        """Count models, views, menus, actions."""
        # Count models
        models_dir = module_path / "models"
        if models_dir.exists():
            for py_file in models_dir.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                content = py_file.read_text(encoding="utf-8")
                audit.model_count += content.count("class ") - content.count(
                    "class Meta"
                )

        # Count views, menus, actions from XML
        for xml_file in module_path.rglob("*.xml"):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                for record in root.iter("record"):
                    model = record.get("model", "")
                    if model == "ir.ui.view":
                        audit.view_count += 1
                    elif model == "ir.ui.menu":
                        audit.menu_count += 1
                    elif model.startswith("ir.actions."):
                        audit.action_count += 1

                # Also count <menuitem> shortcuts
                audit.menu_count += len(list(root.iter("menuitem")))

            except ET.ParseError:
                pass  # Already reported in XML audit

    def generate_module_readme(self, audit: ModuleAudit) -> str:
        """Generate README.md content for a module."""
        status_emoji = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "UNKNOWN": "❓"}

        readme = f"""# {audit.name}

**Status**: {status_emoji.get(audit.status, "❓")} {audit.status}
**Version**: {audit.version}
**Author**: {audit.author}

## Summary

{audit.summary}

## Dependencies

{chr(10).join(f"- `{d}`" for d in audit.depends) if audit.depends else "_No dependencies_"}

## Module Contents

| Type | Count |
|------|-------|
| Models | {audit.model_count} |
| Views | {audit.view_count} |
| Menus | {audit.menu_count} |
| Actions | {audit.action_count} |
| Data Files | {audit.data_file_count} |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | {"✅" if audit.manifest_valid else "❌"} |
| Python Syntax | {"✅" if audit.python_syntax_ok else "❌"} |
| XML Syntax | {"✅" if audit.xml_syntax_ok else "❌"} |
| Security CSV | {"✅" if audit.security_csv_ok else "⚠️"} |
| Init Imports | {"✅" if audit.init_imports_ok else "⚠️"} |

"""
        if audit.issues:
            readme += "## Issues\n\n"
            for issue in audit.issues:
                readme += f"- ❌ {issue}\n"
            readme += "\n"

        if audit.warnings:
            readme += "## Warnings\n\n"
            for warning in audit.warnings:
                readme += f"- ⚠️ {warning}\n"
            readme += "\n"

        readme += f"""## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i {audit.name} --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u {audit.name} --stop-after-init
```

---
_Audited: {audit.audited_at}_
"""
        return readme

    def run_full_audit(self, pattern: str = "ipai_*") -> Dict[str, ModuleAudit]:
        """Run audit on all matching modules."""
        modules = self.find_modules(pattern)
        print(f"Found {len(modules)} modules matching '{pattern}'")

        for module_path in modules:
            self.audit_module(module_path)

        return self.audits

    def save_results(self, output_dir: Path = OUTPUT_DIR, docs_dir: Path = DOCS_DIR):
        """Save audit results to files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        docs_dir.mkdir(parents=True, exist_ok=True)

        # JSON output
        json_path = output_dir / "module_audit_matrix.json"
        json_data = {
            "generated_at": datetime.now().isoformat(),
            "module_count": len(self.audits),
            "summary": {
                "pass": sum(1 for a in self.audits.values() if a.status == "PASS"),
                "warn": sum(1 for a in self.audits.values() if a.status == "WARN"),
                "fail": sum(1 for a in self.audits.values() if a.status == "FAIL"),
            },
            "modules": {name: asdict(audit) for name, audit in self.audits.items()},
        }
        json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False))
        print(f"Saved: {json_path}")

        # CSV output
        csv_path = output_dir / "module_audit_matrix.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "module",
                    "status",
                    "version",
                    "depends_count",
                    "model_count",
                    "view_count",
                    "menu_count",
                    "manifest_ok",
                    "python_ok",
                    "xml_ok",
                    "security_ok",
                    "issue_count",
                    "warning_count",
                ]
            )
            for name, audit in sorted(self.audits.items()):
                writer.writerow(
                    [
                        name,
                        audit.status,
                        audit.version,
                        len(audit.depends),
                        audit.model_count,
                        audit.view_count,
                        audit.menu_count,
                        "Y" if audit.manifest_valid else "N",
                        "Y" if audit.python_syntax_ok else "N",
                        "Y" if audit.xml_syntax_ok else "N",
                        "Y" if audit.security_csv_ok else "N",
                        len(audit.issues),
                        len(audit.warnings),
                    ]
                )
        print(f"Saved: {csv_path}")

        # Per-module README files
        for name, audit in self.audits.items():
            readme_path = docs_dir / f"{name}.md"
            readme_path.write_text(self.generate_module_readme(audit))
        print(f"Saved: {len(self.audits)} module READMEs in {docs_dir}/")

        # Index file
        index_path = docs_dir / "INDEX.md"
        index_content = "# IPAI Module Index\n\n"
        index_content += f"_Generated: {datetime.now().isoformat()}_\n\n"
        index_content += "| Module | Status | Version | Models | Views |\n"
        index_content += "|--------|--------|---------|--------|-------|\n"
        for name, audit in sorted(self.audits.items()):
            status_emoji = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(
                audit.status, "❓"
            )
            index_content += f"| [{name}](./{name}.md) | {status_emoji} | {audit.version} | {audit.model_count} | {audit.view_count} |\n"
        index_path.write_text(index_content)
        print(f"Saved: {index_path}")

    def get_exit_code(self) -> int:
        """Return exit code for CI: 0=pass, 1=fail."""
        fail_count = sum(1 for a in self.audits.values() if a.status == "FAIL")
        return 1 if fail_count > 0 else 0


def main():
    parser = argparse.ArgumentParser(description="IPAI Module Audit Agent")
    parser.add_argument("--module", "-m", help="Audit specific module only")
    parser.add_argument("--pattern", "-p", default="ipai_*", help="Module name pattern")
    parser.add_argument(
        "--output", "-o", default=str(OUTPUT_DIR), help="Output directory"
    )
    parser.add_argument(
        "--docs", "-d", default=str(DOCS_DIR), help="Docs output directory"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--ci", action="store_true", help="CI mode (exit code on failure)"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    args = parser.parse_args()

    auditor = ModuleAuditor(verbose=args.verbose)

    if args.module:
        # Single module audit
        for addons_path in ADDONS_PATHS:
            module_path = addons_path / args.module
            if module_path.exists():
                audit = auditor.audit_module(module_path)
                print(f"\n{audit.name}: {audit.status}")
                if audit.issues:
                    for issue in audit.issues:
                        print(f"  ❌ {issue}")
                if audit.warnings:
                    for warning in audit.warnings:
                        print(f"  ⚠️ {warning}")
                break
        else:
            print(f"Module not found: {args.module}")
            sys.exit(1)
    else:
        # Full audit
        auditor.run_full_audit(args.pattern)

    # Save results
    auditor.save_results(Path(args.output), Path(args.docs))

    # Summary
    summary = auditor.audits
    pass_count = sum(1 for a in summary.values() if a.status == "PASS")
    warn_count = sum(1 for a in summary.values() if a.status == "WARN")
    fail_count = sum(1 for a in summary.values() if a.status == "FAIL")

    print(f"\n=== Audit Summary ===")
    print(f"  PASS: {pass_count}")
    print(f"  WARN: {warn_count}")
    print(f"  FAIL: {fail_count}")
    print(f"  Total: {len(summary)}")

    if args.json:
        print(
            json.dumps(
                {
                    "pass": pass_count,
                    "warn": warn_count,
                    "fail": fail_count,
                    "total": len(summary),
                }
            )
        )

    if args.ci:
        sys.exit(auditor.get_exit_code())


if __name__ == "__main__":
    main()
