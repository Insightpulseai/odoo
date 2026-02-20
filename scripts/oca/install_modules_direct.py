#!/usr/bin/env python3
"""
OCA Module Installation Script
Reads module allowlist from file and installs via XML-RPC
"""
import sys
import yaml
import xmlrpc.client
import time
import os
import subprocess
from pathlib import Path

# Parse arguments
allowlist_path = sys.argv[1]
url = sys.argv[2]
db = sys.argv[3]
username = sys.argv[4]
password = sys.argv[5]
dry_run = sys.argv[6] if len(sys.argv) > 6 else ""

# Resolve allowlist relative to git repo root if possible; else cwd.
# Handle submodules by looking for sentinel file (config/oca/module_allowlist.yml).
repo_root = None
try:
    current_root = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
        stderr=subprocess.DEVNULL
    ).strip()

    # Check if we're at monorepo root (has sentinel file)
    sentinel = os.path.join(current_root, "config/oca/module_allowlist.yml")
    if os.path.isfile(sentinel):
        repo_root = current_root
    else:
        # Walk up to find monorepo root
        check_dir = os.path.dirname(current_root)
        while os.path.isdir(check_dir):
            try:
                potential_root = subprocess.check_output(
                    ["git", "rev-parse", "--show-toplevel"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                    cwd=check_dir
                ).strip()

                # Check for sentinel file
                sentinel = os.path.join(potential_root, "config/oca/module_allowlist.yml")
                if os.path.isfile(sentinel):
                    repo_root = potential_root
                    break

                # Move up one level
                check_dir = os.path.dirname(potential_root)

                # Prevent infinite loop
                if potential_root == "/" or potential_root == check_dir:
                    break
            except subprocess.CalledProcessError:
                break

        # Fallback to original root if not found
        if repo_root is None:
            repo_root = current_root
except Exception:
    repo_root = os.getcwd()

# Make allowlist path absolute
if not os.path.isabs(allowlist_path):
    allowlist_path = str((Path(repo_root) / allowlist_path).resolve())

if not os.path.exists(allowlist_path):
    print(f"ERROR: allowlist not found: {allowlist_path}", file=sys.stderr)
    print("Hint: pass a path relative to monorepo root or an absolute path", file=sys.stderr)
    sys.exit(2)

# Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
RED = '\033[0;31m'
NC = '\033[0m'

# Load allowlist
with open(allowlist_path, 'r') as f:
    config = yaml.safe_load(f)

install_order = config.get("install_order", [])
packs = config.get("packs", {})

# Collect modules
ordered_modules = []
pack_boundaries = {}

for pack_name in install_order:
    modules = packs.get(pack_name, [])
    pack_boundaries[pack_name] = (len(ordered_modules), len(ordered_modules) + len(modules))
    ordered_modules.extend(modules)

print(f"{GREEN}Found {len(ordered_modules)} modules in {len(install_order)} packs{NC}")
print("")

if dry_run == "--dry-run":
    print(f"{YELLOW}Dry run - showing install order:{NC}")
    for pack_name in install_order:
        start, end = pack_boundaries[pack_name]
        print(f"\n{BLUE}Pack: {pack_name}{NC} ({end - start} modules)")
        for module in ordered_modules[start:end]:
            print(f"  - {module}")
    print(f"\n{GREEN}Dry run complete{NC}")
    sys.exit(0)

# Connect to Odoo
print(f"{BLUE}Connecting to Odoo...{NC}")
try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    if not uid:
        print(f"{RED}ERROR: Authentication failed{NC}", file=sys.stderr)
        sys.exit(1)

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    print(f"{GREEN}✓ Connected as user ID: {uid}{NC}")
    print("")

except Exception as e:
    print(f"{RED}ERROR: Connection failed: {e}{NC}", file=sys.stderr)
    sys.exit(1)

# Check modules
print(f"{BLUE}Checking modules...{NC}")
installed_count = 0
to_install_count = 0
not_found = []
uninstallable = []
module_states = {}

for module in ordered_modules:
    try:
        module_ids = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'search',
            [[['name', '=', module]]]
        )

        if not module_ids:
            not_found.append(module)
            module_states[module] = 'not_found'
            continue

        module_data = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'read',
            [module_ids],
            {'fields': ['name', 'state']}
        )

        state = module_data[0]['state']
        module_states[module] = state

        if state == 'installed':
            installed_count += 1
        elif state in ['uninstalled', 'to install', 'to upgrade']:
            to_install_count += 1
        elif state == 'uninstallable':
            uninstallable.append(module)

    except Exception as e:
        print(f"{YELLOW}Warning: {module}: {e}{NC}")
        module_states[module] = 'error'

print(f"{GREEN}✓ Already installed: {installed_count}{NC}")
print(f"{YELLOW}○ To install: {to_install_count}{NC}")

if not_found:
    print(f"{RED}✗ Not found: {len(not_found)}{NC}")
    for m in not_found[:10]:
        print(f"  - {m}")
    if len(not_found) > 10:
        print(f"  ... and {len(not_found) - 10} more")

if uninstallable:
    print(f"{YELLOW}⚠ Uninstallable: {len(uninstallable)}{NC}")
    for m in uninstallable[:10]:
        print(f"  - {m}")

print("")

# Install modules
total_installed = 0
total_failed = 0

for pack_name in install_order:
    start, end = pack_boundaries[pack_name]
    pack_modules = ordered_modules[start:end]

    to_install = [
        m for m in pack_modules
        if module_states.get(m) in ['uninstalled', 'to install', 'to upgrade']
    ]

    if not to_install:
        print(f"{GREEN}✓ Pack '{pack_name}': All {len(pack_modules)} modules installed{NC}")
        continue

    print(f"{BLUE}Installing pack '{pack_name}': {len(to_install)}/{len(pack_modules)} modules{NC}")

    for module in to_install:
        print(f"  {module}...", end=" ", flush=True)

        try:
            module_ids = models.execute_kw(
                db, uid, password,
                'ir.module.module', 'search',
                [[['name', '=', module]]]
            )

            if module_ids:
                models.execute_kw(
                    db, uid, password,
                    'ir.module.module', 'button_immediate_install',
                    [module_ids]
                )
                print(f"{GREEN}✓{NC}")
                total_installed += 1
                time.sleep(0.5)
            else:
                print(f"{RED}✗{NC}")
                total_failed += 1

        except Exception as e:
            print(f"{RED}✗ {str(e)[:50]}{NC}")
            total_failed += 1

    print("")

# Summary
print(f"{BLUE}═════════════════════════════════════════════════════════${NC}")
print(f"  Already installed: {installed_count}")
print(f"  Newly installed:   {total_installed}")
print(f"  Not found:         {len(not_found)}")
print(f"  Uninstallable:     {len(uninstallable)}")
print(f"  Failed:            {total_failed}")
print(f"  Total:             {len(ordered_modules)}")
print(f"{BLUE}═════════════════════════════════════════════════════════${NC}")

if total_failed > 0:
    print(f"\n{YELLOW}⚠ Completed with {total_failed} failures{NC}")
    sys.exit(1)
elif not_found:
    print(f"\n{YELLOW}⚠ Completed with {len(not_found)} missing modules{NC}")
    sys.exit(0)
else:
    print(f"\n{GREEN}✓ All modules installed successfully!{NC}")
    sys.exit(0)
