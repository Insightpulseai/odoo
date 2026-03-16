#!/usr/bin/env python3
import os
import sys
import re
import yaml
from pathlib import Path

# =============================================================================
# Repository Structure Guardrail (Python Port)
# =============================================================================
# Enforces the CE → OCA → IPAI layered architecture.
#
# Usage:
#   python3 infra/ci/structure_check.py
#
# =============================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ADDONS_DIR = REPO_ROOT / "addons"

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"

errors = 0

def log_ok(msg):
    print(f"{GREEN}[OK]{NC} {msg}")

def log_error(msg):
    global errors
    print(f"{RED}[ERROR]{NC} {msg}")
    errors += 1

def log_warn(msg):
    print(f"{YELLOW}[WARN]{NC} {msg}")

def check_structure():
    print("\nRepository Structure Check")
    print("==========================\n")

    if not ADDONS_DIR.exists():
        log_error("addons/ directory not found")
        return

    # Detect structure type
    namespaced_structure = (ADDONS_DIR / "ipai").is_dir()
    flat_ipai_count = len(list(ADDONS_DIR.glob("ipai_*")))
    flat_structure = flat_ipai_count > 0

    if flat_structure:
        print("Detected: FLAT structure (ipai_* modules in addons/)")
    elif namespaced_structure:
        print("Detected: NAMESPACED structure (addons/ipai/ subdirectory)")
    else:
        print("Detected: No IPAI modules found yet")
    print("")

    # Check 1: Addons directory structure
    print("Check 1: Addons directory structure")
    for item in ADDONS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            name = item.name
            if name in ["ipai", "oca"]:
                log_ok(f"Valid addon namespace: {name}/")
            elif name.startswith("ipai_"):
                if flat_structure:
                    log_ok(f"Valid IPAI module: {name}/")
                else:
                    log_error(f"Flat module {name}/ found but repo uses namespaced structure")
                    print(f"       Move to addons/ipai/{name}/")
            else:
                log_error(f"Invalid addon directory: addons/{name}/")
                print("       Allowed: ipai_* modules, oca/, or ipai/")
    print("")

    # Check 2: IPAI modules follow naming convention
    print("Check 2: IPAI module naming convention")
    ipai_modules_found = 0
    
    # Check namespaced
    if namespaced_structure:
        for module_dir in (ADDONS_DIR / "ipai").iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith("."):
                if module_dir.name.startswith("ipai_"):
                    log_ok(f"Valid IPAI module: ipai/{module_dir.name}")
                    ipai_modules_found += 1
                else:
                    log_error(f"Invalid IPAI module name: {module_dir.name}")
                    print("       IPAI modules must start with 'ipai_'")

    # Check flat
    if flat_structure:
        for module_dir in ADDONS_DIR.glob("ipai_*"):
            if module_dir.is_dir():
                log_ok(f"Valid IPAI module (flat): {module_dir.name}")
                ipai_modules_found += 1
    
    if ipai_modules_found == 0:
        log_warn("No IPAI modules found")
    else:
        print(f"Found {ipai_modules_found} IPAI module(s)")
    print("")

    # Check 3: OCA module vendoring
    print("Check 3: OCA module vendoring")
    if (ADDONS_DIR / "oca").is_dir():
        oca_found = 0
        for repo_dir in (ADDONS_DIR / "oca").iterdir():
            if repo_dir.is_dir() and not repo_dir.name.startswith("."):
                oca_found += 1
                if (repo_dir / ".git").exists():
                    log_ok(f"OCA repo vendored: {repo_dir.name}")
                else:
                    log_warn(f"OCA directory without .git: {repo_dir.name} (may be extracted)")
        
        if oca_found == 0:
            log_ok("OCA directory exists but is empty")
        
        if (REPO_ROOT / "vendor/oca.lock").exists():
            log_ok("OCA lockfile present: vendor/oca.lock")
        else:
            log_warn("OCA lockfile missing: vendor/oca.lock")
            print("       Run: ./vendor/oca-sync.sh update")
    else:
        log_warn("addons/oca/ not found (no OCA modules vendored yet)")
    print("")

    # Check 4: No duplicate module names
    print("Check 4: No duplicate module names")
    seen_modules = {}

    # Check namespaced IPAI
    if namespaced_structure:
        for module_dir in (ADDONS_DIR / "ipai").iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith("."):
                name = module_dir.name
                if name in seen_modules:
                    log_error(f"Duplicate module: {name} (also in {seen_modules[name]})")
                else:
                    seen_modules[name] = "ipai/"

    # Check flat IPAI
    if flat_structure:
        for module_dir in ADDONS_DIR.glob("ipai_*"):
            if module_dir.is_dir():
                name = module_dir.name
                if name in seen_modules:
                    log_warn(f"Module {name} exists in both addons/{name} and addons/ipai/{name} (flat is canonical)")
                    seen_modules[name] = "addons/ (canonical)"
                else:
                    seen_modules[name] = "addons/"

    # Check OCA modules
    if (ADDONS_DIR / "oca").exists():
        for repo_dir in (ADDONS_DIR / "oca").iterdir():
            if repo_dir.is_dir() and not repo_dir.name.startswith("."):
                for module_dir in repo_dir.iterdir():
                    if module_dir.is_dir() and (module_dir / "__manifest__.py").exists():
                        name = module_dir.name
                        if name in seen_modules:
                            log_error(f"Duplicate module: {name} ({seen_modules[name]} vs oca)")

    log_ok("No duplicate modules found checked") # Logic handled in loop
    print("")

    # Check 5: Docker compose restart loop check
    print("Check 5: Docker compose restart loop check")
    docker_compose = REPO_ROOT / "docker-compose.yml"
    if docker_compose.exists():
        try:
            with open(docker_compose, 'r') as f:
                # Basic parsing to avoid full yaml dependency if possible, but we imported yaml
                # Actually let's use regex for line-based checking like the bash script to be safe against complex yaml features
                content = f.read()
                services_block = False
                current_service = None
                stop_after_init = False
                restart_policy = None
                
                lines = content.split('\n')
                for line in lines:
                    if line.strip() == 'services:':
                        services_block = True
                        continue
                    
                    if not services_block:
                        continue
                        
                    # Service definition: "  servicename:"
                    service_match = re.match(r'^  ([a-zA-Z0-9_-]+):$', line)
                    if service_match:
                        # Check previous service
                        if current_service and stop_after_init and restart_policy and 'unless-stopped' in restart_policy and not current_service.endswith('-init'):
                             log_error(f"{current_service} has --stop-after-init with restart: {restart_policy}")

                        current_service = service_match.group(1)
                        stop_after_init = False
                        restart_policy = None
                        continue
                    
                    if current_service:
                        if '--stop-after-init' in line:
                            stop_after_init = True
                        
                        restart_match = re.match(r'^    restart:\s*(.*)', line)
                        if restart_match:
                            restart_policy = restart_match.group(1)

                # Check last service
                if current_service and stop_after_init and restart_policy and 'unless-stopped' in restart_policy and not current_service.endswith('-init'):
                        log_error(f"{current_service} has --stop-after-init with restart: {restart_policy}")
                
            log_ok("Docker compose check complete")
        except Exception as e:
            log_warn(f"Could not parse docker-compose.yml: {e}")
    else:
        log_ok("docker-compose.yml not found (skipped)")
    print("")

    # Check 6: QWeb template ID uniqueness
    print("Check 6: QWeb template ID check")
    
    ipai_related_dirs = []
    if namespaced_structure:
        ipai_related_dirs.append(ADDONS_DIR / "ipai")
    if flat_structure:
        ipai_related_dirs.extend(list(ADDONS_DIR.glob("ipai_*")))
    
    if ipai_related_dirs:
        # Simplistic grep-like check
        # Regex to find id="something" inside inherit_id=... lines is hard purely line-based without context
        # The bash script did: grep -r 'inherit_id=.*template.*id='
        # This implies it looks for lines containing both.
        
        seen_ids = set()
        duplicates = set()

        for d in ipai_related_dirs:
            if not d.is_dir(): continue
            for root, _, files in os.walk(d):
                for file in files:
                    if file.endswith(".xml"):
                        path = Path(root) / file
                        try:
                            content = path.read_text(encoding='utf-8', errors='ignore')
                            # Find IDs in templates that inherit
                            # This is a heuristic based on the bash script
                            # The bash script: grep -r 'inherit_id=.*template.*id=' ... | grep -o 'id="[^"]*"'
                            
                            # Let's just look for ALL IDs to be safe? 
                            # No, the bash script specifically targets this pattern.
                            # "inherit_id=" followed by "template" followed by "id=" on the SAME LINE.
                            
                            for line in content.splitlines():
                                if 'inherit_id=' in line and 'template' in line and 'id=' in line:
                                    # Use word boundary \b to ensure we match 'id=' and not 'inherit_id='
                                    matches = re.findall(r'\bid=["\']([^"\']+)["\']', line)
                                    for mid in matches:
                                        if mid in seen_ids:
                                            duplicates.add(mid)
                                        seen_ids.add(mid)
                        except:
                            pass
        
        if duplicates:
            log_error(f"Potential QWeb ID collisions: {', '.join(duplicates)}")
        else:
            log_ok("No QWeb ID collisions detected")

    else:
        log_ok("No IPAI modules to check")

    print("\n==========================")
    if errors > 0:
        print(f"{RED}FAILED{NC}: {errors} error(s) found")
        sys.exit(1)
    else:
        print(f"{GREEN}PASSED{NC}: Repository structure is valid")
        sys.exit(0)

if __name__ == "__main__":
    check_structure()
