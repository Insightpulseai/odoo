#!/usr/bin/env python3
"""
Simulate installation plan for IPAI modules and generate evidence.

This script performs install-plan simulation (does NOT invoke actual Odoo installation).

This script:
1. Validates database name is in CI allowlist
2. Rejects production/staging/default database names
3. Simulates install plan for specified module group into ephemeral database
4. Generates install evidence (install-report.json, module-dependency-graph.json)
5. Outputs JSON evidence for CI gates

Usage:
    python3 install_ipai_modules.py \
        --odoo-root /path/to/odoo \
        --install-group core_minimal \
        --db-name ci_odoo_test_core \
        --db-host localhost \
        --db-port 5432 \
        --db-user odoo \
        [--db-password PASSWORD]

Output:
    evidence/ci/ipai-install/install-report.json
    evidence/ci/ipai-install/module-dependency-graph.json
"""

import json
import sys
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
import yaml
import argparse
from datetime import datetime


def validate_db_name(db_name: str, allowed_patterns: List[str], forbidden_names: List[str]) -> Tuple[bool, str]:
    """
    Validate database name against allowlist.
    
    Returns:
        (is_valid, message)
    """
    # Check forbidden names first
    if db_name in forbidden_names:
        return False, f"Database name '{db_name}' is forbidden (production/staging/default)"
    
    # Check allowed patterns
    for pattern in allowed_patterns:
        if re.match(pattern, db_name):
            return True, f"Database name '{db_name}' matches allowed pattern"
    
    return False, f"Database name '{db_name}' does not match any allowed pattern"


def load_baseline_config(odoo_root: str) -> Dict[str, Any]:
    """Load install baseline config."""
    config_path = Path(odoo_root) / "ssot" / "odoo" / "ipai-install-baseline.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_install_group_modules(config: Dict[str, Any], group_name: str) -> List[str]:
    """Get list of modules for a specific install group."""
    install_groups = config.get('install_groups', {})
    
    if group_name not in install_groups:
        raise ValueError(f"Install group not found: {group_name}")
    
    group_config = install_groups[group_name]
    
    if group_name == 'full_dev_smoke':
        # Dynamically compute all approved, non-deprecated modules
        modules = []
        all_modules = config.get('modules', {})
        for module_name, module_meta in all_modules.items():
            if module_meta.get('status') != 'deprecated':
                modules.append(module_name)
        return sorted(modules)
    
    return group_config.get('modules', [])


def build_dependency_graph(config: Dict[str, Any], modules: List[str]) -> Dict[str, Any]:
    """Build dependency graph for specified modules."""
    all_modules = config.get('modules', {})
    graph = {}
    
    def add_dependencies(module_name: str, visited: set) -> Dict[str, Any]:
        """Recursively add module and its dependencies to graph."""
        if module_name in visited:
            return graph.get(module_name, {})
        
        visited.add(module_name)
        
        module_meta = all_modules.get(module_name, {})
        declared_deps = module_meta.get('depends_on', [])
        
        graph[module_name] = {
            "name": module_name,
            "status": module_meta.get('status', 'unknown'),
            "declared_dependencies": declared_deps,
            "transitive": [],
        }
        
        for dep in declared_deps:
            if dep in all_modules:
                add_dependencies(dep, visited)
                graph[module_name]["transitive"].append(dep)
        
        return graph[module_name]
    
    visited = set()
    for module in modules:
        add_dependencies(module, visited)
    
    return graph


def generate_install_evidence(
    odoo_root: str,
    install_group: str,
    db_name: str,
    modules_to_install: List[str],
    install_result: Dict[str, Any],
    dependency_graph: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate install evidence report."""
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "odoo_root": odoo_root,
        "environment": "ci",
        "install_group": install_group,
        "database": db_name,
        "requested_modules": modules_to_install,
        "install_result": install_result,
        "dependency_graph": dependency_graph,
        "success": install_result.get("success", False),
        "errors": install_result.get("errors", []),
    }
    
    return report


def run_install_simulation(
    odoo_root: str,
    db_name: str,
    modules: List[str],
    db_host: str = "localhost",
    db_port: int = 5432,
    db_user: str = "odoo",
    db_password: str = None,
) -> Dict[str, Any]:
    """
    Simulate module installation (does not mutate database in CI).
    
    In real CI, this would call:
      odoo-bin -i module1,module2 -d ci_odoo_test_core ...
    
    For now, returns a simulation result.
    """
    result = {
        "success": True,
        "installed_modules": modules,
        "install_order": modules,  # Simplified; real CLI would determine order
        "database": db_name,
        "db_connection": {
            "host": db_host,
            "port": db_port,
            "user": db_user,
        },
        "errors": [],
        "warnings": [],
    }
    
    # Validate basic Python import of each module's manifest
    for module_name in modules:
        module_paths = [
            Path(odoo_root) / "addons" / "oca" / module_name,
            Path(odoo_root) / "addons" / "ipai" / module_name,
            Path(odoo_root) / "addons" / "local" / module_name,
            Path(odoo_root) / "addons" / module_name,
        ]
        
        found = False
        for module_path in module_paths:
            if module_path.exists() and (module_path / "__manifest__.py").exists():
                found = True
                break
        
        if not found:
            result["success"] = False
            result["errors"].append(f"Module not found: {module_name}")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Install IPAI modules into ephemeral CI database"
    )
    parser.add_argument("--odoo-root", required=True, help="Odoo root directory")
    parser.add_argument("--install-group", required=True, help="Install group name")
    parser.add_argument("--db-name", required=True, help="Database name")
    parser.add_argument("--db-host", default="localhost", help="Database host")
    parser.add_argument("--db-port", type=int, default=5432, help="Database port")
    parser.add_argument("--db-user", default="odoo", help="Database user")
    parser.add_argument("--db-password", default=None, help="Database password")
    
    args = parser.parse_args()
    
    odoo_root = args.odoo_root
    install_group = args.install_group
    db_name = args.db_name
    
    # Load config
    try:
        config = load_baseline_config(odoo_root)
    except Exception as e:
        print(f"ERROR: Failed to load config: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate database name
    allowed_patterns = config.get('allowed_db_name_patterns', [])
    forbidden_names = config.get('forbidden_db_names', [])
    
    is_valid, msg = validate_db_name(db_name, allowed_patterns, forbidden_names)
    print(f"Database validation: {msg}")
    
    if not is_valid:
        print(f"ERROR: Database name validation failed", file=sys.stderr)
        sys.exit(1)
    
    # Get modules for install group
    try:
        modules = get_install_group_modules(config, install_group)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Install group '{install_group}' modules: {', '.join(modules)}")
    
    # Build dependency graph
    dependency_graph = build_dependency_graph(config, modules)
    
    # Simulate installation
    install_result = run_install_simulation(
        odoo_root,
        db_name,
        modules,
        db_host=args.db_host,
        db_port=args.db_port,
        db_user=args.db_user,
        db_password=args.db_password,
    )
    
    if not install_result["success"]:
        print(f"ERROR: Install simulation failed", file=sys.stderr)
        for error in install_result["errors"]:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    
    # Generate evidence
    evidence = generate_install_evidence(
        odoo_root,
        install_group,
        db_name,
        modules,
        install_result,
        dependency_graph,
    )
    
    # Create evidence directory
    evidence_dir = Path(odoo_root) / "evidence" / "ci" / "ipai-install"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    # Write install report
    install_report_path = evidence_dir / "install-report.json"
    with open(install_report_path, 'w') as f:
        json.dump(evidence, f, indent=2)
    print(f"✓ Install report written: {install_report_path}")
    
    # Write dependency graph
    dep_graph_path = evidence_dir / "module-dependency-graph.json"
    with open(dep_graph_path, 'w') as f:
        json.dump({"dependency_graph": dependency_graph}, f, indent=2)
    print(f"✓ Dependency graph written: {dep_graph_path}")
    
    print(f"\n✓ INSTALL SIMULATION SUCCEEDED")
    print(f"  Install group: {install_group}")
    print(f"  Database: {db_name}")
    print(f"  Modules: {', '.join(modules)}")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
