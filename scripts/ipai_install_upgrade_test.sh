#!/usr/bin/env bash
# IPAI Module Install/Upgrade Test Script
# Runs install and upgrade tests for all IPAI modules using Docker

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="${REPO_ROOT}/artifacts"
LOGS_DIR="${ARTIFACTS_DIR}/logs"
TEST_DB="ipai_test_db"
ODOO_IMAGE="odoo:18.0"
NETWORK="ipai-test-network"
POSTGRES_CONTAINER="ipai-test-postgres"
ODOO_CONTAINER="ipai-test-odoo"

# Modules to test (in dependency order)
MODULES=(
    # Foundation modules (no ipai dependencies)
    "ipai"
    "ipai_platform_theme"
    "ipai_platform_workflow"
    "ipai_platform_audit"
    "ipai_platform_permissions"
    "ipai_platform_approvals"

    # Finance modules
    "ipai_finance_closing"
    "ipai_month_end_closing"
    "ipai_bir_tax_compliance"
    "ipai_month_end"
    "ipai_tbwa_finance"
    "ipai_finance_monthly_closing"
    "ipai_finance_ppm"
    "ipai_close_orchestration"
    "ipai_ppm_a1"
    "ipai_ppm_monthly_close"
    "ipai_finance_ppm_golive"
    "ipai_finance_ppm_umbrella"

    # WorkOS modules
    "ipai_workos_core"
    "ipai_workos_blocks"
    "ipai_workos_db"
    "ipai_workos_canvas"
    "ipai_workos_collab"
    "ipai_workos_views"
    "ipai_workos_search"
    "ipai_workos_templates"
    "ipai_workos_affine"

    # Other modules
    "ipai_ask_ai"
    "ipai_crm_pipeline"
    "ipai_grid_view"
    "ipai_superset_connector"
    "ipai_theme_tbwa_backend"
)

# CSV file header
CSV_FILE="${ARTIFACTS_DIR}/ipai_install_upgrade_matrix.csv"
JSON_FILE="${ARTIFACTS_DIR}/ipai_install_upgrade_matrix.json"

# ANSI colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

cleanup() {
    log_info "Cleaning up test containers..."
    docker rm -f ${ODOO_CONTAINER} 2>/dev/null || true
    docker rm -f ${POSTGRES_CONTAINER} 2>/dev/null || true
    docker network rm ${NETWORK} 2>/dev/null || true
}

setup_test_env() {
    log_info "Setting up test environment..."

    # Cleanup any existing containers
    cleanup

    # Create network
    docker network create ${NETWORK} 2>/dev/null || true

    # Start PostgreSQL
    log_info "Starting PostgreSQL..."
    docker run -d --name ${POSTGRES_CONTAINER} \
        --network ${NETWORK} \
        -e POSTGRES_USER=odoo \
        -e POSTGRES_PASSWORD=odoo \
        -e POSTGRES_DB=postgres \
        postgres:15-alpine

    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL..."
    sleep 5
    for i in {1..30}; do
        if docker exec ${POSTGRES_CONTAINER} pg_isready -U odoo >/dev/null 2>&1; then
            log_info "PostgreSQL is ready"
            break
        fi
        sleep 1
    done

    # Create test database
    docker exec ${POSTGRES_CONTAINER} createdb -U odoo ${TEST_DB} 2>/dev/null || true
}

run_odoo_command() {
    local module=$1
    local action=$2  # install or upgrade
    local log_file="${LOGS_DIR}/${module}__${action}.log"
    local start_time=$(date +%s)

    local flag="-i"
    if [ "$action" = "upgrade" ]; then
        flag="-u"
    fi

    # Run Odoo in container
    docker run --rm \
        --name ${ODOO_CONTAINER} \
        --network ${NETWORK} \
        -v "${REPO_ROOT}/addons:/mnt/extra-addons:ro" \
        -e HOST=${POSTGRES_CONTAINER} \
        -e USER=odoo \
        -e PASSWORD=odoo \
        ${ODOO_IMAGE} \
        odoo -d ${TEST_DB} ${flag} ${module} \
        --stop-after-init \
        --addons-path=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons \
        --log-level=info \
        2>&1 | tee "${log_file}"

    local exit_code=${PIPESTATUS[0]}
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo "EXIT_CODE=${exit_code}" >> "${log_file}"
    echo "DURATION=${duration}" >> "${log_file}"

    return ${exit_code}
}

check_for_errors() {
    local log_file=$1

    # Check for common error patterns
    if grep -q "CRITICAL\|ERROR\|Traceback\|ParseError\|ValidationError" "${log_file}" 2>/dev/null; then
        return 1
    fi
    return 0
}

extract_error() {
    local log_file=$1

    # Extract first error message
    grep -m1 "ERROR\|CRITICAL\|Traceback" "${log_file}" 2>/dev/null | head -c 100 || echo ""
}

run_tests() {
    local results=()
    local commit_hash=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

    log_info "Starting IPAI module tests..."
    log_info "Modules to test: ${#MODULES[@]}"

    # Initialize CSV
    echo "module,install_ok,upgrade_ok,errors,warnings,duration_s,db_name,log_excerpt_path,tested_commit" > "${CSV_FILE}"

    # Initialize JSON structure
    echo '{"generated": "'$(date -Iseconds)'", "odoo_version": "18.0", "modules": [' > "${JSON_FILE}.tmp"

    local first=true
    for module in "${MODULES[@]}"; do
        log_info "Testing module: ${module}"

        local install_ok="pass"
        local upgrade_ok="pass"
        local errors=""
        local warnings=""
        local duration=0

        # Test install
        log_info "  [1/2] Install test..."
        if run_odoo_command "${module}" "install"; then
            if ! check_for_errors "${LOGS_DIR}/${module}__install.log"; then
                install_ok="warning"
                warnings=$(extract_error "${LOGS_DIR}/${module}__install.log")
            fi
            log_info "  Install: ${GREEN}PASS${NC}"
        else
            install_ok="fail"
            errors=$(extract_error "${LOGS_DIR}/${module}__install.log")
            log_error "  Install: FAIL - ${errors}"
        fi

        # Test upgrade (only if install passed)
        if [ "$install_ok" != "fail" ]; then
            log_info "  [2/2] Upgrade test..."
            if run_odoo_command "${module}" "upgrade"; then
                if ! check_for_errors "${LOGS_DIR}/${module}__upgrade.log"; then
                    upgrade_ok="warning"
                fi
                log_info "  Upgrade: ${GREEN}PASS${NC}"
            else
                upgrade_ok="fail"
                errors="${errors}; $(extract_error "${LOGS_DIR}/${module}__upgrade.log")"
                log_error "  Upgrade: FAIL"
            fi
        else
            upgrade_ok="skipped"
        fi

        # Get duration from log
        duration=$(grep -oP 'DURATION=\K\d+' "${LOGS_DIR}/${module}__install.log" 2>/dev/null || echo "0")

        # Write to CSV
        echo "${module},${install_ok},${upgrade_ok},\"${errors}\",\"${warnings}\",${duration},${TEST_DB},artifacts/logs/${module}__install.log,${commit_hash}" >> "${CSV_FILE}"

        # Write to JSON
        if [ "$first" = true ]; then
            first=false
        else
            echo "," >> "${JSON_FILE}.tmp"
        fi

        cat >> "${JSON_FILE}.tmp" << EOF
{
  "name": "${module}",
  "install_status": "${install_ok}",
  "upgrade_status": "${upgrade_ok}",
  "errors": "$(echo "${errors}" | sed 's/"/\\"/g')",
  "warnings": "$(echo "${warnings}" | sed 's/"/\\"/g')",
  "duration_s": ${duration},
  "tested_commit": "${commit_hash}"
}
EOF
    done

    echo "]}" >> "${JSON_FILE}.tmp"
    mv "${JSON_FILE}.tmp" "${JSON_FILE}"

    log_info "Tests completed!"
}

generate_summary() {
    log_info "Generating summary..."

    local total=$(wc -l < "${CSV_FILE}")
    total=$((total - 1))  # Exclude header

    local passed=$(grep -c ",pass,pass," "${CSV_FILE}" || echo "0")
    local failed=$(grep -c ",fail," "${CSV_FILE}" || echo "0")
    local warnings=$(grep -c ",warning," "${CSV_FILE}" || echo "0")

    echo ""
    echo "=========================================="
    echo "IPAI Install/Upgrade Test Summary"
    echo "=========================================="
    echo "Total modules: ${total}"
    echo "Passed: ${passed}"
    echo "Failed: ${failed}"
    echo "Warnings: ${warnings}"
    echo ""
    echo "Results saved to:"
    echo "  - ${CSV_FILE}"
    echo "  - ${JSON_FILE}"
    echo "  - ${LOGS_DIR}/*.log"
    echo "=========================================="
}

main() {
    log_info "IPAI Module Install/Upgrade Test Runner"
    echo ""

    # Ensure directories exist
    mkdir -p "${LOGS_DIR}"

    # Check Docker
    if ! command -v docker &>/dev/null; then
        log_error "Docker is required but not installed"
        exit 1
    fi

    # Trap for cleanup
    trap cleanup EXIT

    # Setup and run
    setup_test_env
    run_tests
    generate_summary

    # Cleanup is handled by trap
}

# Run main function
main "$@"
