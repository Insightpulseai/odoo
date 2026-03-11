#!/bin/bash
# List EE parity modules from environment variables
# Usage: ./scripts/dev/list-ee-parity-modules.sh [--json|--check]
#
# Environment variables:
#   ODOO_EE_PARITY_OCA_MODULES - Comma-separated list of OCA modules
#   ODOO_EE_PARITY_IPAI_MODULES - Comma-separated list of IPAI modules
#   ODOO_DB_NAME - Database name (default: odoo_core)
#   ODOO_CONTAINER - Container name (default: odoo-core)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Load environment if .env exists
if [[ -f "${REPO_ROOT}/.env" ]]; then
    set -a
    source "${REPO_ROOT}/.env"
    set +a
fi

# Defaults
ODOO_DB_NAME="${ODOO_DB_NAME:-odoo_core}"
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"
OUTPUT_FORMAT="${1:-text}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Parse env vars to arrays
parse_modules() {
    local var_name="$1"
    local value="${!var_name:-}"
    echo "$value" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$'
}

print_text() {
    echo "=========================================="
    echo "EE PARITY MODULE SET"
    echo "=========================================="
    echo ""

    echo -e "${CYAN}OCA Modules (${ODOO_EE_PARITY_OCA_MODULES:+defined}):${NC}"
    if [[ -n "${ODOO_EE_PARITY_OCA_MODULES:-}" ]]; then
        parse_modules "ODOO_EE_PARITY_OCA_MODULES" | while read -r m; do
            echo "  - $m"
        done
    else
        echo "  (none defined)"
    fi
    echo ""

    echo -e "${CYAN}IPAI Modules (${ODOO_EE_PARITY_IPAI_MODULES:+defined}):${NC}"
    if [[ -n "${ODOO_EE_PARITY_IPAI_MODULES:-}" ]]; then
        parse_modules "ODOO_EE_PARITY_IPAI_MODULES" | while read -r m; do
            echo "  - $m"
        done
    else
        echo "  (none defined)"
    fi
    echo ""

    local oca_count ipai_count
    oca_count=$(parse_modules "ODOO_EE_PARITY_OCA_MODULES" | wc -l)
    ipai_count=$(parse_modules "ODOO_EE_PARITY_IPAI_MODULES" | wc -l)
    echo "Total: $((oca_count + ipai_count)) modules ($oca_count OCA + $ipai_count IPAI)"
    echo "=========================================="
}

print_json() {
    local oca_json ipai_json
    oca_json=$(parse_modules "ODOO_EE_PARITY_OCA_MODULES" | jq -R -s -c 'split("\n") | map(select(length > 0))')
    ipai_json=$(parse_modules "ODOO_EE_PARITY_IPAI_MODULES" | jq -R -s -c 'split("\n") | map(select(length > 0))')

    jq -n \
        --argjson oca "$oca_json" \
        --argjson ipai "$ipai_json" \
        '{oca_modules: $oca, ipai_modules: $ipai, total: ($oca | length) + ($ipai | length)}'
}

check_modules() {
    echo "Checking module availability in Odoo..."
    echo ""

    # Collect all modules
    local all_modules
    all_modules=$(parse_modules "ODOO_EE_PARITY_OCA_MODULES"; parse_modules "ODOO_EE_PARITY_IPAI_MODULES")
    local modules_csv
    modules_csv=$(echo "$all_modules" | tr '\n' ',' | sed 's/,$//')

    if ! command -v docker &>/dev/null || ! docker ps -q --filter "name=${ODOO_CONTAINER}" 2>/dev/null | grep -q .; then
        echo -e "${YELLOW}[WARN]${NC} Container ${ODOO_CONTAINER} not running, cannot check module states"
        exit 1
    fi

    # Query module states
    docker exec -T "${ODOO_CONTAINER}" odoo shell -d "${ODOO_DB_NAME}" --no-http << PYEOF
from odoo import api, SUPERUSER_ID
env = api.Environment(cr, SUPERUSER_ID, {})
modules = "${modules_csv}".split(',')
found = env['ir.module.module'].search([('name', 'in', modules)])
found_names = {m.name: m.state for m in found}

print("Module Status:")
print("-" * 50)
for m in modules:
    if m in found_names:
        state = found_names[m]
        icon = "✅" if state == "installed" else "⬜"
        print(f"  {icon} {m}: {state}")
    else:
        print(f"  ❌ {m}: NOT FOUND")
print("-" * 50)
print(f"Found: {len(found_names)}/{len(modules)}")
PYEOF
}

main() {
    case "$OUTPUT_FORMAT" in
        --json)
            print_json
            ;;
        --check)
            check_modules
            ;;
        text|*)
            print_text
            ;;
    esac
}

main "$@"
