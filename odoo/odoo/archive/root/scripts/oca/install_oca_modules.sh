#!/usr/bin/env bash
set -euo pipefail

# Install OCA modules for Odoo 19 CE
# This script reads the OCA module lists and installs them

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Odoo connection details
ODOO_URL="${ODOO_URL:-http://localhost:8069}"
ODOO_DB="${ODOO_DB:-odoo}"
ODOO_USER="${ODOO_USER:-admin}"
ODOO_PASS="${ODOO_PASS:-admin}"

echo "🔍 Checking OCA modules to install..."
echo "   Odoo URL: ${ODOO_URL}"
echo "   Database: ${ODOO_DB}"
echo ""

# Function to parse YAML and extract module names
extract_modules_from_yaml() {
    local yaml_file="$1"

    if [[ ! -f "$yaml_file" ]]; then
        echo "⚠️  File not found: $yaml_file" >&2
        return 1
    fi

    # Extract module names from YAML (simple grep-based parser)
    grep -E "^  - " "$yaml_file" | sed 's/^  - //' | grep -v "^#" || true
}

# Collect all OCA modules from config files
declare -a OCA_MODULES=()

echo "📋 Reading OCA module lists..."

# Base modules
if [[ -f "${REPO_ROOT}/config/oca/oca_must_have_base.yml" ]]; then
    echo "   - oca_must_have_base.yml"
    while IFS= read -r module; do
        [[ -n "$module" ]] && OCA_MODULES+=("$module")
    done < <(extract_modules_from_yaml "${REPO_ROOT}/config/oca/oca_must_have_base.yml")
fi

# Accounting modules
if [[ -f "${REPO_ROOT}/config/oca/oca_must_have_accounting.yml" ]]; then
    echo "   - oca_must_have_accounting.yml"
    while IFS= read -r module; do
        [[ -n "$module" ]] && OCA_MODULES+=("$module")
    done < <(extract_modules_from_yaml "${REPO_ROOT}/config/oca/oca_must_have_accounting.yml")
fi

# Sales modules
if [[ -f "${REPO_ROOT}/config/oca/oca_must_have_sales.yml" ]]; then
    echo "   - oca_must_have_sales.yml"
    while IFS= read -r module; do
        [[ -n "$module" ]] && OCA_MODULES+=("$module")
    done < <(extract_modules_from_yaml "${REPO_ROOT}/config/oca/oca_must_have_sales.yml")
fi

# Purchase modules
if [[ -f "${REPO_ROOT}/config/oca/oca_must_have_purchase.yml" ]]; then
    echo "   - oca_must_have_purchase.yml"
    while IFS= read -r module; do
        [[ -n "$module" ]] && OCA_MODULES+=("$module")
    done < <(extract_modules_from_yaml "${REPO_ROOT}/config/oca/oca_must_have_purchase.yml")
fi

echo ""
echo "📦 Found ${#OCA_MODULES[@]} OCA modules to check"
echo ""

# Check which modules are already installed
echo "🔍 Checking installation status..."

python3 - <<PYTHON
import xmlrpc.client
import os
import sys

url = os.environ['ODOO_URL']
db = os.environ['ODOO_DB']
username = os.environ['ODOO_USER']
password = os.environ['ODOO_PASS']

modules = """${OCA_MODULES[@]}""".split()

try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    if not uid:
        print(f"❌ Authentication failed for user: {username}", file=sys.stderr)
        sys.exit(1)

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    installed = []
    to_install = []
    not_found = []

    for module in modules:
        if not module.strip():
            continue

        # Search for module
        module_ids = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'search',
            [[['name', '=', module]]]
        )

        if not module_ids:
            not_found.append(module)
            continue

        # Get module state
        module_data = models.execute_kw(
            db, uid, password,
            'ir.module.module', 'read',
            [module_ids],
            {'fields': ['name', 'state']}
        )

        state = module_data[0]['state']

        if state == 'installed':
            installed.append(module)
        elif state in ['uninstalled', 'uninstallable']:
            to_install.append(module)
        else:
            print(f"   ⚠️  {module}: {state}")

    print(f"✅ Already installed: {len(installed)}")
    for m in installed[:10]:  # Show first 10
        print(f"   - {m}")
    if len(installed) > 10:
        print(f"   ... and {len(installed) - 10} more")

    print(f"")
    print(f"📦 To install: {len(to_install)}")
    for m in to_install:
        print(f"   - {m}")

    if not_found:
        print(f"")
        print(f"❌ Not found in addons path: {len(not_found)}")
        for m in not_found[:10]:
            print(f"   - {m}")
        if len(not_found) > 10:
            print(f"   ... and {len(not_found) - 10} more")

    # Install modules
    if to_install:
        print(f"")
        print(f"🚀 Installing {len(to_install)} modules...")

        for module in to_install:
            print(f"   Installing {module}...", end=" ", flush=True)
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
                    print("✅")
                else:
                    print("❌ Not found")
            except Exception as e:
                print(f"❌ Error: {e}")

        print(f"")
        print(f"✅ Installation complete!")
    else:
        print(f"")
        print(f"✅ All OCA modules already installed!")

except Exception as e:
    print(f"❌ Error: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON

echo ""
echo "✅ Done!"
