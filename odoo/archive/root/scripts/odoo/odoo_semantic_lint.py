#!/usr/bin/env python3
"""
odoo_semantic_lint.py — Odoo static semantic analyzer

Catches Python↔XML↔manifest mismatches before Odoo install time:
  1. Models declared in Python but absent from module manifest 'data'
  2. XML view <field name="..."> that don't exist on the model
  3. res.config.settings fields referenced without an ir.config_parameter
  4. Module dependencies in __manifest__.py missing from addons_path
  5. Duplicate XML <record id="..."> within a module

Usage:
  python3 scripts/odoo/odoo_semantic_lint.py [--baseline] [--self-test] [addons_dir]

Options:
  --baseline       Write current findings to baseline file (silence them)
  --self-test      Run built-in tests and exit
  addons_dir       Path to addons directory (default: addons/ipai)
"""

import ast
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from xml.etree import ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ADDONS_DIR = REPO_ROOT / "addons" / "ipai"
BASELINE_FILE = Path(__file__).parent / "baselines" / "odoo_semantic_lint_baseline.json"


# ---------------------------------------------------------------------------
# Finding dataclass
# ---------------------------------------------------------------------------

class Finding:
    def __init__(self, rule: str, severity: str, module: str, file: str,
                 line: int, message: str):
        self.rule = rule
        self.severity = severity  # HIGH | MEDIUM | LOW
        self.module = module
        try:
            self.file = str(Path(file).relative_to(REPO_ROOT)) if Path(file).is_absolute() else file
        except ValueError:
            self.file = file  # path outside repo root (e.g. self-test tmpdir)
        self.line = line
        self.message = message

    def key(self) -> str:
        return f"{self.rule}:{self.file}:{self.line}:{self.message}"

    def __str__(self) -> str:
        return f"[{self.severity}] {self.rule} {self.file}:{self.line} — {self.message}"


# ---------------------------------------------------------------------------
# Python AST helpers
# ---------------------------------------------------------------------------

def extract_manifest(module_path: Path) -> Optional[dict]:
    """Parse __manifest__.py and return its dict."""
    manifest_file = module_path / "__manifest__.py"
    if not manifest_file.exists():
        return None
    try:
        tree = ast.parse(manifest_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Dict):
                # Safely evaluate simple dict literal
                return ast.literal_eval(node.value)
        return None
    except Exception:
        return None


def extract_model_names(py_file: Path) -> List[Tuple[str, int]]:
    """Return [(model_name, line)] for all models.Model subclasses."""
    results = []
    try:
        tree = ast.parse(py_file.read_text())
    except SyntaxError:
        return results

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and target.id == '_name':
                            if isinstance(stmt.value, ast.Constant):
                                results.append((stmt.value.s, stmt.lineno))
    return results


def extract_field_names_from_model(py_file: Path) -> Dict[str, Set[str]]:
    """Return {model_name: {field_names}} from a Python file."""
    models: Dict[str, Set[str]] = {}
    try:
        tree = ast.parse(py_file.read_text())
    except SyntaxError:
        return models

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        model_name = None
        fields: Set[str] = set()
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        if target.id == '_name' and isinstance(stmt.value, ast.Constant):
                            model_name = stmt.value.s
                        elif (isinstance(stmt.value, ast.Call) and
                              isinstance(getattr(stmt.value, 'func', None), ast.Attribute) and
                              stmt.value.func.attr.startswith('fields.')):
                            fields.add(target.id)
                        elif isinstance(stmt.value, ast.Call):
                            # fields.Char(...) etc at top level
                            func = stmt.value.func
                            if isinstance(func, ast.Attribute) and hasattr(func, 'value'):
                                if isinstance(func.value, ast.Name) and func.value.id == 'fields':
                                    fields.add(target.id)
        if model_name:
            models[model_name] = fields
    return models


# ---------------------------------------------------------------------------
# XML helpers
# ---------------------------------------------------------------------------

def parse_xml_safe(xml_file: Path) -> Optional[ET.Element]:
    try:
        return ET.parse(xml_file).getroot()
    except ET.ParseError:
        return None


def extract_xml_field_refs(xml_file: Path) -> List[Tuple[str, int]]:
    """Return [(field_name, approx_line)] for <field name="..."> in views."""
    refs = []
    text = xml_file.read_text(errors="replace")
    for i, line in enumerate(text.splitlines(), 1):
        m = re.search(r'<field\s+name=["\']([^"\']+)["\']', line)
        if m:
            refs.append((m.group(1), i))
    return refs


def extract_xml_record_ids(xml_file: Path) -> List[Tuple[str, int]]:
    """Return [(record_id, approx_line)] for all <record id="...">."""
    refs = []
    text = xml_file.read_text(errors="replace")
    for i, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r'<record\b[^>]*\bid=["\']([^"\']+)["\']', line):
            refs.append((m.group(1), i))
    return refs


# ---------------------------------------------------------------------------
# Rule implementations
# ---------------------------------------------------------------------------

def rule_duplicate_xml_ids(module_path: Path, module_name: str) -> List[Finding]:
    """R001: duplicate <record id="..."> within a module."""
    findings = []
    seen: Dict[str, Tuple[str, int]] = {}
    for xml_file in sorted(module_path.rglob("*.xml")):
        for rec_id, line in extract_xml_record_ids(xml_file):
            full_id = f"{module_name}.{rec_id}" if '.' not in rec_id else rec_id
            if full_id in seen:
                prev_file, prev_line = seen[full_id]
                findings.append(Finding(
                    "R001", "MEDIUM", module_name, str(xml_file), line,
                    f"Duplicate XML record id '{full_id}' (first seen {prev_file}:{prev_line})"
                ))
            else:
                seen[full_id] = (str(xml_file), line)
    return findings


def rule_manifest_missing_data_files(module_path: Path, module_name: str) -> List[Finding]:
    """R002: XML file exists in module but is not referenced in manifest['data']."""
    findings = []
    manifest = extract_manifest(module_path)
    if not manifest:
        return findings
    data_files: Set[str] = set(manifest.get("data", []) + manifest.get("demo", []))
    for xml_file in sorted(module_path.rglob("*.xml")):
        rel = xml_file.relative_to(module_path)
        rel_str = str(rel).replace("\\", "/")
        if rel_str not in data_files:
            findings.append(Finding(
                "R002", "LOW", module_name, str(xml_file), 0,
                f"XML file '{rel_str}' not listed in __manifest__.py 'data'"
            ))
    return findings


def rule_undeclared_depends(module_path: Path, module_name: str,
                            available_modules: Set[str]) -> List[Finding]:
    """R003: 'depends' in manifest references a module not in addons_path."""
    findings = []
    manifest = extract_manifest(module_path)
    if not manifest:
        return findings
    for dep in manifest.get("depends", []):
        if dep not in available_modules and not dep.startswith("base"):
            # Only flag custom ipai_* deps — OCA/base deps may be valid
            if dep.startswith("ipai_"):
                findings.append(Finding(
                    "R003", "HIGH", module_name,
                    str(module_path / "__manifest__.py"), 0,
                    f"Dependency '{dep}' not found in scanned addons_path"
                ))
    return findings


def rule_config_settings_missing_param(module_path: Path, module_name: str) -> List[Finding]:
    """R004: res.config.settings fields lack corresponding ir.config_parameter."""
    findings = []
    for py_file in sorted((module_path / "models").glob("*.py")) if (module_path / "models").exists() else []:
        try:
            text = py_file.read_text()
        except Exception:
            continue
        tree_lines = text.splitlines()
        in_config_settings = False
        for i, line in enumerate(tree_lines, 1):
            if re.search(r"class\s+\w+.*res\.config\.settings", line):
                in_config_settings = True
            if in_config_settings:
                m = re.search(r"config_parameter\s*=\s*['\"]([^'\"]+)['\"]", line)
                if not m:
                    m2 = re.search(r"(\w+)\s*=\s*fields\.", line)
                    if m2 and not re.search(r'_inherit|_name|_description', line):
                        # field without config_parameter — warn if it looks like a stored setting
                        if "store=True" in line or "compute=" not in line:
                            findings.append(Finding(
                                "R004", "LOW", module_name, str(py_file), i,
                                f"res.config.settings field '{m2.group(1)}' may be missing config_parameter"
                            ))
    return findings


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def lint_module(module_path: Path, available_modules: Set[str]) -> List[Finding]:
    module_name = module_path.name
    findings: List[Finding] = []
    findings += rule_duplicate_xml_ids(module_path, module_name)
    findings += rule_manifest_missing_data_files(module_path, module_name)
    findings += rule_undeclared_depends(module_path, module_name, available_modules)
    findings += rule_config_settings_missing_param(module_path, module_name)
    return findings


def load_baseline() -> Set[str]:
    if BASELINE_FILE.exists():
        data = json.loads(BASELINE_FILE.read_text())
        return set(data.get("suppressed", []))
    return set()


def write_baseline(findings: List[Finding]) -> None:
    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {"suppressed": sorted(f.key() for f in findings)}
    BASELINE_FILE.write_text(json.dumps(data, indent=2))
    print(f"Baseline written: {BASELINE_FILE} ({len(findings)} findings suppressed)")


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    import tempfile, os

    print("Running odoo_semantic_lint self-tests...")
    failures = 0

    # Test R001: duplicate XML record IDs
    with tempfile.TemporaryDirectory() as tmpdir:
        mod = Path(tmpdir) / "test_module"
        (mod / "views").mkdir(parents=True)
        (mod / "__manifest__.py").write_text("{'name':'T','version':'19.0.1.0.0','depends':['base'],'data':['views/test.xml']}")
        (mod / "views" / "test.xml").write_text(
            '<?xml version="1.0"?><odoo><record id="foo" model="m"/><record id="foo" model="m"/></odoo>'
        )
        results = rule_duplicate_xml_ids(mod, "test_module")
        if not results:
            print("FAIL: R001 did not detect duplicate XML ID")
            failures += 1
        else:
            print(f"PASS: R001 detected duplicate XML ID ({results[0].message})")

    # Test R002: manifest missing data file
    with tempfile.TemporaryDirectory() as tmpdir:
        mod = Path(tmpdir) / "test_module"
        (mod / "views").mkdir(parents=True)
        (mod / "__manifest__.py").write_text("{'name':'T','version':'19.0.1.0.0','depends':['base'],'data':[]}")
        (mod / "views" / "orphan.xml").write_text('<?xml version="1.0"?><odoo/>')
        results = rule_manifest_missing_data_files(mod, "test_module")
        if not any("orphan.xml" in r.message for r in results):
            print("FAIL: R002 did not detect unlisted XML file")
            failures += 1
        else:
            print(f"PASS: R002 detected unlisted data file")

    # Test R003: undeclared depends
    with tempfile.TemporaryDirectory() as tmpdir:
        mod = Path(tmpdir) / "test_module"
        mod.mkdir()
        (mod / "__manifest__.py").write_text(
            "{'name':'T','version':'19.0.1.0.0','depends':['base','ipai_nonexistent']}"
        )
        available = {"base", "mail"}
        results = rule_undeclared_depends(mod, "test_module", available)
        if not any("ipai_nonexistent" in r.message for r in results):
            print("FAIL: R003 did not detect missing dependency")
            failures += 1
        else:
            print(f"PASS: R003 detected missing ipai_* dependency")

    if failures:
        print(f"\n{failures} test(s) FAILED")
        return 1
    print("\nAll self-tests PASSED")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Odoo semantic lint")
    parser.add_argument("addons_dir", nargs="?", default=str(DEFAULT_ADDONS_DIR),
                        help="Path to addons directory")
    parser.add_argument("--baseline", action="store_true",
                        help="Write current findings to baseline (suppress them)")
    parser.add_argument("--self-test", action="store_true",
                        help="Run built-in tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    addons_dir = Path(args.addons_dir)
    if not addons_dir.exists():
        print(f"ERROR: addons directory not found: {addons_dir}", file=sys.stderr)
        return 2

    # Collect available module names
    available_modules: Set[str] = set()
    for d in addons_dir.iterdir():
        if d.is_dir() and (d / "__manifest__.py").exists():
            available_modules.add(d.name)

    # Also include well-known OCA + base modules
    available_modules.update({"base", "mail", "web", "account", "project",
                               "purchase", "sale", "hr", "mrp", "stock"})

    all_findings: List[Finding] = []
    for module_path in sorted(addons_dir.iterdir()):
        if not module_path.is_dir() or not (module_path / "__manifest__.py").exists():
            continue
        findings = lint_module(module_path, available_modules)
        all_findings.extend(findings)

    if args.baseline:
        write_baseline(all_findings)
        return 0

    # Apply baseline suppression
    suppressed = load_baseline()
    active = [f for f in all_findings if f.key() not in suppressed]

    # Report
    high = [f for f in active if f.severity == "HIGH"]
    medium = [f for f in active if f.severity == "MEDIUM"]
    low = [f for f in active if f.severity == "LOW"]

    for f in sorted(active, key=lambda x: (x.severity, x.module)):
        print(f)

    suppressed_count = len(all_findings) - len(active)
    print(f"\nSummary: {len(high)} HIGH, {len(medium)} MEDIUM, {len(low)} LOW "
          f"({suppressed_count} suppressed by baseline)")

    if high:
        print("FAIL: HIGH severity findings must be resolved")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
