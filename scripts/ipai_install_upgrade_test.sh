#!/usr/bin/env bash
# IPAI Module Install/Upgrade Test Script
# Runs install and upgrade tests for all IPAI modules
#
# Modes:
#   - Docker mode (default): Spins up PostgreSQL + Odoo containers
#   - CI mode (CI_MODE=true): Uses external PostgreSQL, runs Odoo in Docker
#
# Environment variables:
#   CI_MODE=true          - Use CI mode (external PostgreSQL)
#   POSTGRES_HOST         - PostgreSQL host (CI mode)
#   POSTGRES_USER         - PostgreSQL user (CI mode)
#   POSTGRES_PASSWORD     - PostgreSQL password (CI mode)
#   TEST_DB               - Test database name (default: ipai_test_db)
#   ODOO_IMAGE            - Odoo Docker image (default: odoo:18.0)
#   SKIP_CLEANUP          - Don't cleanup containers after run

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="${REPO_ROOT}/artifacts"
LOGS_DIR="${ARTIFACTS_DIR}/logs"

# Configurable via environment
TEST_DB="${TEST_DB:-ipai_test_db}"
ODOO_IMAGE="${ODOO_IMAGE:-odoo:18.0}"
CI_MODE="${CI_MODE:-false}"
SKIP_CLEANUP="${SKIP_CLEANUP:-false}"

# Docker networking
NETWORK="ipai-test-network"
POSTGRES_CONTAINER="ipai-test-postgres"
ODOO_CONTAINER="ipai-test-odoo"

# Modules to test (in dependency order - foundation first, then dependents)
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

# CSV file paths
CSV_FILE="${ARTIFACTS_DIR}/ipai_install_upgrade_matrix.csv"
JSON_FILE="${ARTIFACTS_DIR}/ipai_install_upgrade_matrix.json"

# ANSI colors (disabled in CI for cleaner logs)
if [ -t 1 ] && [ "${CI:-false}" != "true" ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    NC=''
fi

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
    if [ "${SKIP_CLEANUP}" = "true" ]; then
        log_info "Skipping cleanup (SKIP_CLEANUP=true)"
        return
    fi

    log_info "Cleaning up test containers..."
    docker rm -f ${ODOO_CONTAINER} 2>/dev/null || true

    if [ "${CI_MODE}" != "true" ]; then
        docker rm -f ${POSTGRES_CONTAINER} 2>/dev/null || true
        docker network rm ${NETWORK} 2>/dev/null || true
    fi
}

setup_docker_postgres() {
    log_info "Setting up Docker PostgreSQL..."

    # Create network
    docker network create ${NETWORK} 2>/dev/null || true

    # Start PostgreSQL
    log_info "Starting PostgreSQL container..."
    docker run -d --name ${POSTGRES_CONTAINER} \
        --network ${NETWORK} \
        -e POSTGRES_USER=odoo \
        -e POSTGRES_PASSWORD=odoo \
        -e POSTGRES_DB=postgres \
        postgres:15-alpine

    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL..."
    for i in {1..30}; do
        if docker exec ${POSTGRES_CONTAINER} pg_isready -U odoo >/dev/null 2>&1; then
            log_info "PostgreSQL is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "PostgreSQL failed to start"
            exit 1
        fi
        sleep 1
    done

    # Create test database
    docker exec ${POSTGRES_CONTAINER} createdb -U odoo ${TEST_DB} 2>/dev/null || true
}

setup_ci_postgres() {
    log_info "Using CI PostgreSQL at ${POSTGRES_HOST:-localhost}..."

    # Wait for PostgreSQL (external service)
    for i in {1..30}; do
        if PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST:-localhost}" -U "${POSTGRES_USER:-odoo}" -d postgres -c "SELECT 1" >/dev/null 2>&1; then
            log_info "PostgreSQL is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "PostgreSQL connection failed"
            exit 1
        fi
        sleep 1
    done

    # Create test database if not exists
    PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST:-localhost}" -U "${POSTGRES_USER:-odoo}" -d postgres \
        -c "CREATE DATABASE ${TEST_DB};" 2>/dev/null || true
}

run_odoo_command() {
    local module=$1
    local action=$2  # install or upgrade
    local log_file="${LOGS_DIR}/${module}__${action}.log"
    local start_time=$(date +%s)
    local exit_code=0

    local flag="-i"
    if [ "$action" = "upgrade" ]; then
        flag="-u"
    fi

    # Determine PostgreSQL connection
    local pg_host="${POSTGRES_HOST:-${POSTGRES_CONTAINER}}"
    local pg_user="${POSTGRES_USER:-odoo}"
    local pg_password="${POSTGRES_PASSWORD:-odoo}"
    local network_flag=""

    if [ "${CI_MODE}" = "true" ]; then
        network_flag="--network host"
    else
        network_flag="--network ${NETWORK}"
    fi

    # Build addons path - include both top-level and nested ipai modules
    local addons_path="/mnt/extra-addons:/mnt/extra-addons/ipai:/usr/lib/python3/dist-packages/odoo/addons"

    log_info "  Running: odoo ${flag} ${module} --stop-after-init"

    # Run Odoo in container with proper binary
    # Note: Official Odoo image uses 'odoo' as entrypoint, not 'odoo-bin'
    docker run --rm \
        --name ${ODOO_CONTAINER} \
        ${network_flag} \
        -v "${REPO_ROOT}/addons:/mnt/extra-addons:ro" \
        -e HOST=${pg_host} \
        -e USER=${pg_user} \
        -e PASSWORD=${pg_password} \
        ${ODOO_IMAGE} \
        odoo -d ${TEST_DB} ${flag} ${module} \
        --stop-after-init \
        --addons-path=${addons_path} \
        --log-level=warn \
        --no-http \
        2>&1 | tee "${log_file}" || exit_code=$?

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # Append metadata to log
    echo "" >> "${log_file}"
    echo "# === Test Metadata ===" >> "${log_file}"
    echo "EXIT_CODE=${exit_code}" >> "${log_file}"
    echo "DURATION=${duration}" >> "${log_file}"
    echo "TIMESTAMP=$(date -Iseconds)" >> "${log_file}"

    return ${exit_code}
}

check_for_errors() {
    local log_file=$1

    # Check for critical error patterns in log
    if grep -qE "CRITICAL|ERROR.*registry|Traceback|ParseError|ValidationError|KeyError|AttributeError" "${log_file}" 2>/dev/null; then
        # Exclude some false positives
        if grep -qE "ERROR.*Registry.*not.*found|Error.*test" "${log_file}" 2>/dev/null; then
            return 1
        fi
        return 1
    fi
    return 0
}

extract_error() {
    local log_file=$1

    # Extract first meaningful error message
    grep -m1 -E "ERROR|CRITICAL|Traceback|Exception" "${log_file}" 2>/dev/null | head -c 200 | tr '\n' ' ' || echo "Unknown error"
}

run_tests() {
    local commit_hash=$(git -C "${REPO_ROOT}" rev-parse --short HEAD 2>/dev/null || echo "unknown")

    log_info "Starting IPAI module tests..."
    log_info "Modules to test: ${#MODULES[@]}"
    log_info "Test database: ${TEST_DB}"
    log_info "Odoo image: ${ODOO_IMAGE}"
    log_info "CI mode: ${CI_MODE}"

    # Initialize CSV
    echo "module,install_ok,upgrade_ok,errors,warnings,duration_s,db_name,log_excerpt_path,tested_commit" > "${CSV_FILE}"

    # Initialize JSON structure
    cat > "${JSON_FILE}.tmp" << EOF
{
  "generated": "$(date -Iseconds)",
  "odoo_version": "18.0",
  "odoo_image": "${ODOO_IMAGE}",
  "test_db": "${TEST_DB}",
  "ci_mode": ${CI_MODE},
  "commit": "${commit_hash}",
  "modules": [
EOF

    local first=true
    local total_pass=0
    local total_fail=0
    local total_skip=0

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
                log_warn "  Install: PASS with warnings"
            else
                log_info "  Install: PASS"
            fi
        else
            install_ok="fail"
            errors=$(extract_error "${LOGS_DIR}/${module}__install.log")
            log_error "  Install: FAIL - ${errors:0:80}"
            ((total_fail++))
        fi

        # Test upgrade (only if install passed)
        if [ "$install_ok" != "fail" ]; then
            log_info "  [2/2] Upgrade test..."
            if run_odoo_command "${module}" "upgrade"; then
                if ! check_for_errors "${LOGS_DIR}/${module}__upgrade.log"; then
                    upgrade_ok="warning"
                    log_warn "  Upgrade: PASS with warnings"
                else
                    log_info "  Upgrade: PASS"
                fi
            else
                upgrade_ok="fail"
                local upgrade_error=$(extract_error "${LOGS_DIR}/${module}__upgrade.log")
                errors="${errors}; ${upgrade_error}"
                log_error "  Upgrade: FAIL"
                ((total_fail++))
            fi

            if [ "$install_ok" = "pass" ] && [ "$upgrade_ok" = "pass" ]; then
                ((total_pass++))
            fi
        else
            upgrade_ok="skipped"
            ((total_skip++))
        fi

        # Get duration from log
        duration=$(grep -oP 'DURATION=\K\d+' "${LOGS_DIR}/${module}__install.log" 2>/dev/null || echo "0")

        # Escape special characters for CSV/JSON
        local escaped_errors=$(echo "${errors}" | sed 's/"/\\"/g' | tr '\n' ' ')
        local escaped_warnings=$(echo "${warnings}" | sed 's/"/\\"/g' | tr '\n' ' ')

        # Write to CSV
        echo "${module},${install_ok},${upgrade_ok},\"${escaped_errors}\",\"${escaped_warnings}\",${duration},${TEST_DB},artifacts/logs/${module}__install.log,${commit_hash}" >> "${CSV_FILE}"

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
      "errors": "${escaped_errors}",
      "warnings": "${escaped_warnings}",
      "duration_s": ${duration},
      "log_install": "artifacts/logs/${module}__install.log",
      "log_upgrade": "artifacts/logs/${module}__upgrade.log"
    }
EOF
    done

    # Close JSON
    cat >> "${JSON_FILE}.tmp" << EOF

  ],
  "summary": {
    "total": ${#MODULES[@]},
    "passed": ${total_pass},
    "failed": ${total_fail},
    "skipped": ${total_skip}
  }
}
EOF
    mv "${JSON_FILE}.tmp" "${JSON_FILE}"

    log_info "Tests completed!"

    # Return non-zero if any failures
    if [ ${total_fail} -gt 0 ]; then
        return 1
    fi
    return 0
}

generate_summary() {
    log_info "Generating summary..."

    local total=$(($(wc -l < "${CSV_FILE}") - 1))  # Exclude header
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

    if [ ${failed} -gt 0 ]; then
        echo ""
        log_error "FAILED MODULES:"
        grep ",fail," "${CSV_FILE}" | cut -d',' -f1 | while read -r mod; do
            echo "  - ${mod}"
        done
    fi
}

main() {
    echo "=========================================="
    echo "IPAI Module Install/Upgrade Test Runner"
    echo "=========================================="
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

    # Setup PostgreSQL based on mode
    if [ "${CI_MODE}" = "true" ]; then
        setup_ci_postgres
    else
        setup_docker_postgres
    fi

    # Run tests
    local test_result=0
    run_tests || test_result=$?

    # Generate summary
    generate_summary

    exit ${test_result}
}

# Run main function
main "$@"
