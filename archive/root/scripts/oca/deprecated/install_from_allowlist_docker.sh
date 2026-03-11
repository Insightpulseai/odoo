#!/usr/bin/env bash
# =============================================================================
# Install OCA Modules from Allowlist (Docker Edition)
# =============================================================================
# Wrapper script for Docker-based Odoo installations.
# Copies allowlist into container and runs installation via XML-RPC.
#
# Usage:
#   ./scripts/oca/install_from_allowlist_docker.sh [--dry-run]
#
# Environment Variables:
#   ODOO_CONTAINER - Container name (default: odoo-core)
#   ODOO_DB        - Database name (default: odoo)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ALLOWLIST="$ROOT_DIR/config/oca/module_allowlist.yml"
DRY_RUN="${1:-}"

# Docker settings
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"
ODOO_DB="${ODOO_DB:-odoo}"
ODOO_URL="http://localhost:8069"
ODOO_USER="admin"
ODOO_PASS="admin"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   OCA Module Installation (Docker)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "   Container: ${ODOO_CONTAINER}"
echo -e "   Database:  ${ODOO_DB}"
echo -e "   Allowlist: ${ALLOWLIST}"
echo ""

# Check Docker container is running
if ! docker ps --format "{{.Names}}" | grep -q "^${ODOO_CONTAINER}$"; then
    echo -e "${RED}ERROR: Container '${ODOO_CONTAINER}' is not running${NC}"
    echo -e "${YELLOW}Start it with: docker start ${ODOO_CONTAINER}${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Container '${ODOO_CONTAINER}' is running${NC}"
echo ""

# Validate allowlist
echo -e "${GREEN}Validating allowlist...${NC}"
"$SCRIPT_DIR/clean_install_allowlist.sh" --dry-run || exit 1
echo ""

# Install modules via Docker exec
docker exec -i "$ODOO_CONTAINER" python3 - "$ODOO_URL" "$ODOO_DB" "$ODOO_USER" "$ODOO_PASS" "$DRY_RUN" < <(cat "$ALLOWLIST" && cat <<'PYTHON'
import sys
import yaml
import xmlrpc.client
import time
import io

# Read allowlist from stdin (first part)
lines = []
for line in sys.stdin:
    if line.strip() == '# END_ALLOWLIST':
        break
    lines.append(line)

allowlist_yaml = ''.join(lines)

# Parse arguments
url = sys.argv[1]
db = sys.argv[2]
username = sys.argv[3]
password = sys.argv[4]
dry_run = sys.argv[5] if len(sys.argv) > 5 else ""

# Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
RED = '\033[0;31m'
NC = '\033[0m'

# Load allowlist
config = yaml.safe_load(allowlist_yaml)
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
    print(f"{GREEN}Connected as user ID: {uid}{NC}")
    print("")

except Exception as e:
    print(f"{RED}ERROR: Connection failed: {e}{NC}", file=sys.stderr)
    sys.exit(1)

# Check modules
print(f"{BLUE}Checking modules...{NC}")
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
    print(f"\n{RED}ERROR: Missing modules. Run: ./scripts/oca/fetch_and_pin.sh{NC}")
    sys.exit(1)

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
print(f"  Failed:            {total_failed}")
print(f"  Total:             {len(ordered_modules)}")
print(f"{BLUE}═════════════════════════════════════════════════════════${NC}")

if total_failed > 0:
    print(f"\n{YELLOW}Completed with {total_failed} failures{NC}")
    sys.exit(1)
else:
    print(f"\n{GREEN}✓ All modules installed successfully!{NC}")
    sys.exit(0)
PYTHON
)

EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}✓ Installation complete!${NC}"
else
    echo -e "${RED}✗ Installation failed${NC}"
    exit $EXIT_CODE
fi
