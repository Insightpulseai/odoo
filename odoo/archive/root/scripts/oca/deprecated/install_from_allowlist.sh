#!/usr/bin/env bash
# =============================================================================
# Install OCA Modules from Allowlist
# =============================================================================
# Reads config/oca/module_allowlist.yml and installs all modules in order.
# Respects install_order sequence for proper dependency resolution.
#
# Usage:
#   ./scripts/oca/install_from_allowlist.sh [--dry-run]
#
# Environment Variables:
#   ODOO_URL    - Odoo server URL (default: http://localhost:8069)
#   ODOO_DB     - Database name (default: odoo)
#   ODOO_USER   - Admin username (default: admin)
#   ODOO_PASS   - Admin password (default: admin)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/repo_root.sh"
ROOT="$(repo_root)"

# Allow passing an allowlist path; default to canonical SSOT location.
ALLOWLIST_PATH="${1:-config/oca/module_allowlist.yml}"
# Shift if first arg is not --dry-run
if [[ "${ALLOWLIST_PATH}" == "--dry-run" ]]; then
  ALLOWLIST_PATH="config/oca/module_allowlist.yml"
  DRY_RUN="--dry-run"
else
  DRY_RUN="${2:-}"
fi
ALLOWLIST="${ROOT}/${ALLOWLIST_PATH}"

if [[ ! -f "${ALLOWLIST}" ]]; then
  echo "ERROR: allowlist not found: ${ALLOWLIST}" >&2
  echo "Hint: run from monorepo root or pass a relative path from root." >&2
  exit 2
fi

# Odoo connection details
ODOO_URL="${ODOO_URL:-http://localhost:8069}"
ODOO_DB="${ODOO_DB:-odoo}"
ODOO_USER="${ODOO_USER:-admin}"
ODOO_PASS="${ODOO_PASS:-admin}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   OCA Module Installation from Allowlist${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "   Odoo URL: ${ODOO_URL}"
echo -e "   Database: ${ODOO_DB}"
echo -e "   Allowlist: ${ALLOWLIST}"
echo ""

# Check dependencies
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}ERROR: python3 is required${NC}"
    exit 1
fi

if ! command -v pip3 &>/dev/null && ! python3 -c "import yaml" &>/dev/null; then
    echo -e "${RED}ERROR: PyYAML is required. Install with: pip3 install pyyaml${NC}"
    exit 1
fi

# Check allowlist exists
if [[ ! -f "$ALLOWLIST" ]]; then
    echo -e "${RED}ERROR: Allowlist not found: $ALLOWLIST${NC}"
    exit 1
fi

# Validate allowlist first
echo -e "${GREEN}Validating allowlist...${NC}"
"$SCRIPT_DIR/clean_install_allowlist.sh" --dry-run || exit 1
echo ""

# Install modules using Python XML-RPC
python3 - "$ALLOWLIST" "$ODOO_URL" "$ODOO_DB" "$ODOO_USER" "$ODOO_PASS" "$DRY_RUN" <<'PYTHON'
import sys
import yaml
import xmlrpc.client
import time

allowlist_path = sys.argv[1]
url = sys.argv[2]
db = sys.argv[3]
username = sys.argv[4]
password = sys.argv[5]
dry_run = sys.argv[6] if len(sys.argv) > 6 else ""

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

# Load allowlist
with open(allowlist_path) as f:
    config = yaml.safe_load(f)

install_order = config.get("install_order", [])
packs = config.get("packs", {})

# Collect modules in install order
ordered_modules = []
pack_boundaries = {}

for pack_name in install_order:
    modules = packs.get(pack_name, [])
    pack_boundaries[pack_name] = (len(ordered_modules), len(ordered_modules) + len(modules))
    ordered_modules.extend(modules)

print(f"{GREEN}Found {len(ordered_modules)} modules in {len(install_order)} packs{NC}")
print("")

if dry_run == "--dry-run":
    print(f"{YELLOW}Dry run mode - showing install order only:{NC}")
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
        print(f"{RED}ERROR: Authentication failed for user: {username}{NC}", file=sys.stderr)
        sys.exit(1)

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    print(f"{GREEN}Connected as user ID: {uid}{NC}")
    print("")

except Exception as e:
    print(f"{RED}ERROR: Failed to connect to Odoo: {e}{NC}", file=sys.stderr)
    sys.exit(1)

# Check module availability
print(f"{BLUE}Checking module availability...{NC}")
installed_count = 0
to_install_count = 0
not_found = []

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

    except Exception as e:
        print(f"{YELLOW}Warning: Failed to check {module}: {e}{NC}")
        module_states[module] = 'error'

print(f"{GREEN}✓ Already installed: {installed_count}{NC}")
print(f"{YELLOW}○ To install: {to_install_count}{NC}")

if not_found:
    print(f"{RED}✗ Not found: {len(not_found)}{NC}")
    for m in not_found[:10]:
        print(f"  - {m}")
    if len(not_found) > 10:
        print(f"  ... and {len(not_found) - 10} more")
    print(f"\n{RED}ERROR: Some modules not found in addons path.{NC}")
    print(f"{YELLOW}Run: ./scripts/oca/fetch_and_pin.sh to fetch missing modules{NC}")
    sys.exit(1)

print("")

# Install modules pack by pack
total_installed = 0
total_failed = 0

for pack_name in install_order:
    start, end = pack_boundaries[pack_name]
    pack_modules = ordered_modules[start:end]

    # Filter modules that need installation
    to_install = [
        m for m in pack_modules
        if module_states.get(m) in ['uninstalled', 'to install', 'to upgrade']
    ]

    if not to_install:
        print(f"{GREEN}✓ Pack '{pack_name}': All {len(pack_modules)} modules already installed{NC}")
        continue

    print(f"{BLUE}Installing pack '{pack_name}': {len(to_install)}/{len(pack_modules)} modules{NC}")

    for module in to_install:
        print(f"  Installing {module}...", end=" ", flush=True)

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
                time.sleep(0.5)  # Brief pause between installs
            else:
                print(f"{RED}✗ Not found{NC}")
                total_failed += 1

        except Exception as e:
            print(f"{RED}✗ Error: {e}{NC}")
            total_failed += 1

    print("")

# Summary
print(f"{BLUE}═══════════════════════════════════════════════════════════${NC}")
print(f"{BLUE}   Installation Summary${NC}")
print(f"{BLUE}═══════════════════════════════════════════════════════════${NC}")
print(f"  Already installed: {installed_count}")
print(f"  Newly installed:   {total_installed}")
print(f"  Failed:            {total_failed}")
print(f"  Total modules:     {len(ordered_modules)}")
print("")

if total_failed > 0:
    print(f"{YELLOW}Installation completed with {total_failed} failures{NC}")
    sys.exit(1)
else:
    print(f"{GREEN}✓ All modules installed successfully!{NC}")
    sys.exit(0)

PYTHON

EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}✓ Installation complete!${NC}"
else
    echo -e "${RED}✗ Installation failed with exit code: $EXIT_CODE${NC}"
    exit $EXIT_CODE
fi
