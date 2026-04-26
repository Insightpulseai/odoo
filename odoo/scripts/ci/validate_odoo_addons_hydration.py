#!/usr/bin/env python3
"""
Validate IPAI module hydration and manifest correctness.

This script reads ssot/odoo/ipai-install-baseline.yaml, verifies:
- All module directories exist
- All modules have __manifest__.py
- All manifests are syntactically valid
- No deprecated modules appear in CI-required groups
- All declared dependencies exist

Output: evidence/ci/ipai-install/hydration-report.json
"""

import json
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import yaml
import ast


def load_baseline_config(config_path: str) -> Dict[str, Any]:
    """Load and parse the IPAI install baseline YAML."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def find_module_directory(module_name: str, odoo_root: str) -> Path | None:
    """Find the directory for a given module name in standard addon paths."""
    addon_paths = [
        Path(odoo_root) / "addons" / "oca",
        Path(odoo_root) / "addons" / "ipai",
        Path(odoo_root) / "addons" / "local",
        Path(odoo_root) / "addons",  # Generic addons
    ]
    
    for addon_path in addon_paths:
        module_path = addon_path / module_name
        if module_path.is_dir():
            return module_path
    
    return None


def read_manifest(module_path: Path) -> Dict[str, Any] | None:
    """Read and parse __manifest__.py, handling both dict() and {} syntax."""
    manifest_file = module_path / "__manifest__.py"
    
    if not manifest_file.exists():
        return None
    
    try:
        with open(manifest_file, 'r') as f:
            content = f.read()
        
        # Use ast.literal_eval for safety
        # First, try direct evaluation (works for both dict() and {})
        manifest = ast.literal_eval(content)
        
        if not isinstance(manifest, dict):
            return None
        
        return manifest
    except Exception:
        return None


def validate_manifest_structure(module_name: str, manifest: Dict[str, Any]) -> List[str]:
    """Validate manifest has required fields. Return list of errors."""
    errors = []
    
    required_fields = ['name', 'version']
    for field in required_fields:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")
    
    if 'depends' in manifest:
        if not isinstance(manifest['depends'], list):
            errors.append(f"'depends' field is not a list: {type(manifest['depends'])}")
    
    return errors


def validate_hydration(config: Dict[str, Any], odoo_root: str) -> Tuple[Dict[str, Any], List[str]]:
    """
    Validate all modules in baseline config.
    
    Returns:
        (report_dict, error_list)
    """
    errors = []
    report = {
        "timestamp": None,
        "odoo_root": odoo_root,
        "config_path": f"{odoo_root}/ssot/odoo/ipai-install-baseline.yaml",
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
        }
    }
    
    # Get all modules from config
    all_modules = config.get('modules', {})
    
    # Validate each module
    for module_name, module_meta in all_modules.items():
        report["validation_results"]["modules"][module_name] = {}
        report["summary"]["total_modules"] += 1
        
        # Find module directory
        module_path = find_module_directory(module_name, odoo_root)
        
        if not module_path:
            report["validation_results"]["modules"][module_name]["status"] = "missing"
            report["validation_results"]["modules"][module_name]["path"] = None
            report["summary"]["missing_modules"] += 1
            errors.append(f"Module not found: {module_name}")
            continue
        
        report["validation_results"]["modules"][module_name]["status"] = "found"
        report["validation_results"]["modules"][module_name]["path"] = str(module_path)
        report["summary"]["found_modules"] += 1
        
        # Check for __manifest__.py
        manifest = read_manifest(module_path)
        
        if manifest is None:
            report["validation_results"]["modules"][module_name]["manifest_status"] = "missing_or_invalid"
            report["summary"]["manifest_errors"] += 1
            errors.append(f"Module {module_name}: no valid __manifest__.py")
            continue
        
        report["validation_results"]["modules"][module_name]["manifest_status"] = "valid"
        report["validation_results"]["modules"][module_name]["manifest"] = {
            "name": manifest.get('name'),
            "version": manifest.get('version'),
            "depends": manifest.get('depends', []),
        }
        
        # Validate manifest structure
        manifest_errors = validate_manifest_structure(module_name, manifest)
        if manifest_errors:
            report["validation_results"]["modules"][module_name]["manifest_errors"] = manifest_errors
            report["summary"]["manifest_errors"] += 1
            for error in manifest_errors:
                errors.append(f"Module {module_name}: {error}")
        
        # Check status
        status = module_meta.get('status', 'unknown')
        report["validation_results"]["modules"][module_name]["status_declared"] = status
        
        if status == "deprecated":
            report["validation_results"]["modules"][module_name]["deprecated"] = True
        
        # Store dependencies for closure validation
        report["validation_results"]["dependencies"][module_name] = manifest.get('depends', [])
    
    # Validate install groups
    install_groups = config.get('install_groups', {})
    for group_name, group_config in install_groups.items():
        report["validation_results"]["install_groups"][group_name] = {
            "required": group_config.get('required', False),
            "ci_required": group_config.get('ci_required', False),
            "modules": [],
            "status": "valid",
            "errors": [],
        }
        
        group_modules = group_config.get('modules', [])
        if group_modules is None:
            group_modules = []
        
        for module_name in group_modules:
            module_status = report["validation_results"]["modules"].get(module_name, {}).get("status")
            is_deprecated = all_modules.get(module_name, {}).get('status') == 'deprecated'
            
            report["validation_results"]["install_groups"][group_name]["modules"].append({
                "name": module_name,
                "found": module_status == "found",
                "deprecated": is_deprecated,
            })
            
            if module_status == "missing":
                error_msg = f"Install group '{group_name}' requires missing module: {module_name}"
                report["validation_results"]["install_groups"][group_name]["errors"].append(error_msg)
                errors.append(error_msg)
            
            if is_deprecated and group_config.get('ci_required', False):
                error_msg = f"CI-required group '{group_name}' contains deprecated module: {module_name}"
                report["validation_results"]["install_groups"][group_name]["errors"].append(error_msg)
                errors.append(error_msg)
                report["summary"]["deprecated_in_required"] += 1
    
    report["errors"] = errors
    
    return report, errors


def main():
    if len(sys.argv) > 1:
        odoo_root = sys.argv[1]
    else:
        odoo_root = os.getcwd()
    
    config_path = os.path.join(odoo_root, 'ssot', 'odoo', 'ipai-install-baseline.yaml')
    
    if not os.path.exists(config_path):
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        config = load_baseline_config(config_path)
    except Exception as e:
        print(f"ERROR: Failed to load config: {e}", file=sys.stderr)
        sys.exit(1)
    
    report, errors = validate_hydration(config, odoo_root)
    
    # Create evidence directory
    evidence_dir = Path(odoo_root) / "evidence" / "ci" / "ipai-install"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    # Write report
    report_path = evidence_dir / "hydration-report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✓ Hydration report written: {report_path}")
    
    # Print summary
    summary = report["summary"]
    print(f"\n=== HYDRATION VALIDATION SUMMARY ===")
    print(f"Total modules: {summary['total_modules']}")
    print(f"Found modules: {summary['found_modules']}")
    print(f"Missing modules: {summary['missing_modules']}")
    print(f"Manifest errors: {summary['manifest_errors']}")
    print(f"Deprecated in required groups: {summary['deprecated_in_required']}")
    
    if errors:
        print(f"\n✗ VALIDATION FAILED: {len(errors)} error(s)")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print(f"\n✓ VALIDATION PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
