#!/usr/bin/env python3
import pathlib
import sys

FORBIDDEN_NAMES = [
    "lakehouse",
    "ops-platform",
    "design-system",
    "addons/OCA",
    "odoo_prod",
    "odoo_core",
    "odoo_stage"
]

def check_naming_drift():
    repo_root = pathlib.Path(__file__).parent.parent.parent
    violations = []

    for path in repo_root.rglob("*"):
        if ".git" in path.parts:
            continue
        
        rel_path_str = str(path.relative_to(repo_root))
        
        for forbidden in FORBIDDEN_NAMES:
            if forbidden in rel_path_str:
                violations.append(f"Naming Drift Violation: Found forbidden term '{forbidden}' in path -> {rel_path_str}")
    
    if violations:
        print("Naming Drift Violations Found:")
        for v in violations:
            print(v)
        sys.exit(1)
    else:
        print("Naming Drift Check Passed.")
        sys.exit(0)

if __name__ == "__main__":
    check_naming_drift()
